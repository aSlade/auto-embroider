"""
Convert raster images to simplified embroidery patterns.

Uses Pillow and OpenCV to process images, then the drawing library
to generate stitch patterns.
"""

import math
import cv2
import numpy as np
from PIL import Image

from drawing import Canvas


def _rgb_to_hex(r, g, b):
    return f"#{r:02X}{g:02X}{b:02X}"


def _simplify_contour(contour, epsilon_factor=0.02):
    """Reduce points in a contour using Douglas-Peucker algorithm."""
    epsilon = epsilon_factor * cv2.arcLength(contour, True)
    return cv2.approxPolyDP(contour, epsilon, True)


def _contour_to_points(contour, scale_x, scale_y, offset_x=0, offset_y=0):
    """Convert an OpenCV contour to a list of (x, y) tuples in mm."""
    pts = []
    for point in contour:
        px, py = point[0]
        pts.append((px * scale_x + offset_x, py * scale_y + offset_y))
    return pts


def _contour_centroid(contour):
    """Return (cx, cy) centroid of an OpenCV contour in pixel coords."""
    m = cv2.moments(contour)
    if m["m00"] == 0:
        # Degenerate contour — use first point
        return (float(contour[0][0][0]), float(contour[0][0][1]))
    return (m["m10"] / m["m00"], m["m01"] / m["m00"])


def _nearest_neighbor_order(contours, start=(0, 0)):
    """Reorder contours by greedy nearest-neighbor on centroids.

    Starting from *start*, repeatedly pick the closest unvisited contour.
    This minimises total travel / jump distance between regions.
    """
    if len(contours) <= 1:
        return list(contours)

    centroids = [_contour_centroid(c) for c in contours]
    remaining = set(range(len(contours)))
    ordered = []

    cx, cy = start
    while remaining:
        best_idx = min(
            remaining,
            key=lambda i: math.hypot(centroids[i][0] - cx, centroids[i][1] - cy),
        )
        ordered.append(contours[best_idx])
        cx, cy = centroids[best_idx]
        remaining.discard(best_idx)

    return ordered


def image_to_embroidery(
    image_path,
    output_path,
    width_mm=100,
    height_mm=None,
    max_colors=8,
    min_area=20,
    fill_spacing=0.8,
    fill_angle=45,
    stitch_length=2.5,
    outline=True,
    do_fill=True,
    simplify=0.015,
):
    """Convert an image to an embroidery file.

    Args:
        image_path: Path to the input image.
        output_path: Path for the output embroidery file (.dst, .pes, etc.).
        width_mm: Target width in mm.
        height_mm: Target height in mm (auto-calculated from aspect ratio if None).
        max_colors: Number of thread colors to quantize to.
        min_area: Minimum contour area in pixels to include (filters noise).
        fill_spacing: Distance between fill lines in mm.
        fill_angle: Angle of fill hatching in degrees.
        stitch_length: Maximum stitch length in mm.
        outline: Whether to stitch outlines around color regions.
        do_fill: Whether to fill color regions.
        simplify: Contour simplification factor (0 = no simplification).

    Returns:
        The Canvas object with the generated pattern.
    """
    # Load and prepare image
    img = Image.open(image_path).convert("RGB")
    orig_w, orig_h = img.size

    if height_mm is None:
        height_mm = width_mm * (orig_h / orig_w)

    # Resize for processing — work at a reasonable resolution
    process_w = 300
    process_h = int(process_w * (orig_h / orig_w))
    img_resized = img.resize((process_w, process_h), Image.LANCZOS)

    # Quantize colors
    img_quantized = img_resized.quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT)
    palette_data = img_quantized.getpalette()
    img_indexed = np.array(img_quantized)

    # Extract palette colors (RGB tuples)
    palette = []
    for i in range(max_colors):
        r, g, b = palette_data[i * 3], palette_data[i * 3 + 1], palette_data[i * 3 + 2]
        palette.append((r, g, b))

    # Sort colors by luminance (stitch dark colors last so they sit on top)
    color_order = sorted(
        range(max_colors),
        key=lambda i: -(0.299 * palette[i][0] + 0.587 * palette[i][1] + 0.114 * palette[i][2]),
    )

    # Scale factors: pixels -> mm
    scale_x = width_mm / process_w
    scale_y = height_mm / process_h

    canvas = Canvas(stitch_length=stitch_length)
    first_color = True

    for color_idx in color_order:
        r, g, b = palette[color_idx]

        # Skip near-white colors (likely background)
        if r > 240 and g > 240 and b > 240:
            continue

        # Create binary mask for this color
        mask = (img_indexed == color_idx).astype(np.uint8) * 255

        # Clean up mask with morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Find contours
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            continue

        # Filter small contours
        contours = [c for c in contours if cv2.contourArea(c) >= min_area]
        if not contours:
            continue

        # Switch thread color
        hex_color = _rgb_to_hex(r, g, b)
        if first_color:
            canvas._add_thread(hex_color)
            first_color = False
        else:
            canvas.color(hex_color)

        # Order contours by spatial proximity to reduce travel stitches
        last_pos = (canvas._x / scale_x, canvas._y / scale_y) if not first_color else (0, 0)
        contours = _nearest_neighbor_order(contours, start=last_pos)

        for contour in contours:
            # Simplify contour
            if simplify > 0:
                contour = _simplify_contour(contour, simplify)

            if len(contour) < 3:
                continue

            points = _contour_to_points(contour, scale_x, scale_y)

            # Fill the region
            if do_fill:
                canvas.fill(points, angle=fill_angle, spacing=fill_spacing)

            # Outline the region
            if outline:
                canvas.polygon(points)

    canvas.save(output_path)
    return canvas


def image_to_embroidery_outline(
    image_path,
    output_path,
    width_mm=100,
    height_mm=None,
    stitch_length=2.0,
    edge_threshold1=50,
    edge_threshold2=150,
    simplify=0.02,
    min_length=15,
):
    """Convert an image to an outline-only embroidery (like a sketch).

    Uses Canny edge detection to find edges, then traces them as stitches.

    Args:
        image_path: Path to the input image.
        output_path: Path for the output embroidery file.
        width_mm: Target width in mm.
        height_mm: Target height in mm (auto from aspect ratio if None).
        stitch_length: Maximum stitch length in mm.
        edge_threshold1: Canny lower threshold.
        edge_threshold2: Canny upper threshold.
        simplify: Contour simplification factor.
        min_length: Minimum contour arc length in pixels to include.

    Returns:
        The Canvas object with the generated pattern.
    """
    img = Image.open(image_path).convert("RGB")
    orig_w, orig_h = img.size

    if height_mm is None:
        height_mm = width_mm * (orig_h / orig_w)

    # Process at reasonable resolution
    process_w = 400
    process_h = int(process_w * (orig_h / orig_w))
    img_resized = img.resize((process_w, process_h), Image.LANCZOS)

    # Convert to grayscale and detect edges
    gray = cv2.cvtColor(np.array(img_resized), cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(gray, edge_threshold1, edge_threshold2)

    # Dilate slightly to connect nearby edges
    kernel = np.ones((2, 2), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)

    # Find contours of edges
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    scale_x = width_mm / process_w
    scale_y = height_mm / process_h

    canvas = Canvas(stitch_length=stitch_length, color="black")

    # Filter and sort contours by position (top-to-bottom, left-to-right)
    # to minimize jumps
    valid = []
    for c in contours:
        if cv2.arcLength(c, False) >= min_length:
            if simplify > 0:
                c = _simplify_contour(c, simplify)
            if len(c) >= 2:
                valid.append(c)

    # Order contours by spatial proximity (nearest-neighbor) to
    # minimise jump stitches between regions.
    valid = _nearest_neighbor_order(valid, start=(0, 0))

    for contour in valid:
        points = _contour_to_points(contour, scale_x, scale_y)
        if len(points) >= 3:
            canvas.polygon(points)
        elif len(points) == 2:
            canvas.line(*points[0], *points[1])

    canvas.save(output_path)
    return canvas
