"""
Embroidery drawing library built on pyembroidery.

Provides a Canvas class with methods for lines, curves, shapes, and fills
that generate stitch patterns for embroidery files.

All coordinates are in millimeters. Internally converted to pyembroidery's
0.1mm unit system.
"""

import math
import pyembroidery


def _mm(v):
    """Convert mm to pyembroidery units (0.1mm)."""
    return v * 10


class Canvas:
    """Drawing surface that builds an embroidery pattern."""

    def __init__(self, stitch_length=2.0, color="black"):
        """
        Args:
            stitch_length: Default max stitch length in mm.
            color: Initial thread color (name or hex).
        """
        self.pattern = pyembroidery.EmbPattern()
        self.stitch_length = stitch_length
        self._color = color
        self._add_thread(color)
        self._x = 0.0
        self._y = 0.0

    # ── Thread / color management ──────────────────────────────

    _COLOR_MAP = {
        "black": "#000000", "white": "#FFFFFF", "red": "#FF0000",
        "green": "#00FF00", "blue": "#0000FF", "yellow": "#FFFF00",
        "orange": "#FFA500", "purple": "#800080", "pink": "#FFC0CB",
        "brown": "#8B4513", "gray": "#808080", "grey": "#808080",
    }

    def _add_thread(self, color):
        hex_color = self._COLOR_MAP.get(color.lower(), color)
        thread = pyembroidery.EmbThread()
        thread.set_hex_color(hex_color)
        self.pattern.add_thread(thread)

    def color(self, color):
        """Switch to a new thread color."""
        self._color = color
        self._add_thread(color)
        self.pattern.add_command(pyembroidery.COLOR_CHANGE)
        return self

    # ── Movement ───────────────────────────────────────────────

    def move_to(self, x, y):
        """Move needle without stitching."""
        self.pattern.add_command(pyembroidery.TRIM)
        self.pattern.add_command(pyembroidery.STITCH, _mm(x), _mm(y))
        self._x, self._y = x, y
        return self

    # ── Primitives ─────────────────────────────────────────────

    def _stitch_to(self, x, y):
        """Add a single stitch to (x, y) in mm."""
        self.pattern.add_command(pyembroidery.STITCH, _mm(x), _mm(y))
        self._x, self._y = x, y

    def _walk(self, x0, y0, x1, y1):
        """Stitch from (x0,y0) to (x1,y1), splitting long segments."""
        dx, dy = x1 - x0, y1 - y0
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        steps = max(1, math.ceil(dist / self.stitch_length))
        for i in range(1, steps + 1):
            t = i / steps
            self._stitch_to(x0 + dx * t, y0 + dy * t)

    def line(self, x0, y0, x1, y1):
        """Draw a straight line between two points."""
        self.move_to(x0, y0)
        self._walk(x0, y0, x1, y1)
        return self

    def polyline(self, points):
        """Draw connected line segments through a list of (x, y) points."""
        if len(points) < 2:
            return self
        self.move_to(*points[0])
        for i in range(1, len(points)):
            self._walk(*points[i - 1], *points[i])
        return self

    def polygon(self, points):
        """Draw a closed polygon outline."""
        if len(points) < 3:
            return self
        self.polyline(points + [points[0]])
        return self

    # ── Curves ─────────────────────────────────────────────────

    def _bezier_point(self, t, p0, p1, p2, p3):
        """Evaluate cubic bezier at parameter t."""
        u = 1 - t
        return (u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0],
                u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1])

    def _bezier_length_estimate(self, p0, p1, p2, p3, samples=20):
        """Rough arc length of a cubic bezier."""
        length = 0
        prev = p0
        for i in range(1, samples + 1):
            pt = self._bezier_point(i / samples, p0, p1, p2, p3)
            length += math.hypot(pt[0] - prev[0], pt[1] - prev[1])
            prev = pt
        return length

    def curve(self, p0, p1, p2, p3):
        """Draw a cubic bezier curve. p0-p3 are (x,y) tuples in mm."""
        self.move_to(*p0)
        arc_len = self._bezier_length_estimate(p0, p1, p2, p3)
        steps = max(2, math.ceil(arc_len / self.stitch_length))
        for i in range(1, steps + 1):
            pt = self._bezier_point(i / steps, p0, p1, p2, p3)
            self._stitch_to(*pt)
        return self

    def quadratic_curve(self, p0, p1, p2):
        """Draw a quadratic bezier by promoting to cubic."""
        # Quadratic (p0, p1, p2) -> Cubic (p0, c1, c2, p2)
        c1 = (p0[0] + 2/3 * (p1[0] - p0[0]), p0[1] + 2/3 * (p1[1] - p0[1]))
        c2 = (p2[0] + 2/3 * (p1[0] - p2[0]), p2[1] + 2/3 * (p1[1] - p2[1]))
        return self.curve(p0, c1, c2, p2)

    # ── Shapes ─────────────────────────────────────────────────

    def rectangle(self, x, y, width, height):
        """Draw a rectangle outline."""
        pts = [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]
        return self.polygon(pts)

    def circle(self, cx, cy, radius, segments=64):
        """Draw a circle outline."""
        pts = []
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            pts.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
        return self.polygon(pts)

    def ellipse(self, cx, cy, rx, ry, segments=64):
        """Draw an ellipse outline."""
        pts = []
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            pts.append((cx + rx * math.cos(angle), cy + ry * math.sin(angle)))
        return self.polygon(pts)

    def arc(self, cx, cy, radius, start_angle, end_angle, segments=32):
        """Draw a circular arc. Angles in degrees."""
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)
        pts = []
        for i in range(segments + 1):
            t = i / segments
            angle = start_rad + t * (end_rad - start_rad)
            pts.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
        return self.polyline(pts)

    def star(self, cx, cy, outer_r, inner_r, points=5):
        """Draw a star outline."""
        pts = []
        for i in range(points * 2):
            angle = math.pi * i / points - math.pi / 2
            r = outer_r if i % 2 == 0 else inner_r
            pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        return self.polygon(pts)

    def rounded_rectangle(self, x, y, width, height, radius, corner_segments=8):
        """Draw a rectangle with rounded corners."""
        r = min(radius, width / 2, height / 2)
        pts = []
        corners = [
            (x + width - r, y + r, -math.pi / 2, 0),
            (x + width - r, y + height - r, 0, math.pi / 2),
            (x + r, y + height - r, math.pi / 2, math.pi),
            (x + r, y + r, math.pi, 3 * math.pi / 2),
        ]
        for cx, cy, a_start, a_end in corners:
            for i in range(corner_segments + 1):
                t = i / corner_segments
                a = a_start + t * (a_end - a_start)
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        return self.polygon(pts)

    # ── Fill algorithms ────────────────────────────────────────

    def _scanline_intersections(self, points, y):
        """Find x-coordinates where horizontal line y intersects polygon edges."""
        intersections = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if y0 == y1:
                continue
            if min(y0, y1) <= y < max(y0, y1):
                x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                intersections.append(x)
        intersections.sort()
        return intersections

    def fill(self, points, angle=0, spacing=0.8):
        """Fill a polygon with parallel stitch lines (hatching).

        Args:
            points: List of (x, y) polygon vertices in mm.
            angle: Hatch angle in degrees.
            spacing: Distance between fill lines in mm.
        """
        if len(points) < 3:
            return self

        # Rotate points so we can scan horizontally, then rotate back
        rad = math.radians(-angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        def rotate(px, py):
            return (px * cos_a - py * sin_a, px * sin_a + py * cos_a)

        def unrotate(px, py):
            return (px * cos_a + py * sin_a, -px * sin_a + py * cos_a)

        rotated = [rotate(p[0], p[1]) for p in points]

        y_min = min(p[1] for p in rotated)
        y_max = max(p[1] for p in rotated)

        y = y_min + spacing / 2
        forward = True
        first = True
        while y < y_max:
            xs = self._scanline_intersections(rotated, y)
            for i in range(0, len(xs) - 1, 2):
                x_start, x_end = xs[i], xs[i + 1]
                if not forward:
                    x_start, x_end = x_end, x_start

                p0 = unrotate(x_start, y)
                p1 = unrotate(x_end, y)

                if first:
                    self.move_to(*p0)
                    first = False
                else:
                    self._walk(self._x, self._y, *p0)

                self._walk(*p0, *p1)

            forward = not forward
            y += spacing
        return self

    # ── Filled shape helpers ───────────────────────────────────

    def filled_rectangle(self, x, y, width, height, angle=0, spacing=0.8):
        """Draw and fill a rectangle."""
        pts = [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]
        self.rectangle(x, y, width, height)
        self.fill(pts, angle=angle, spacing=spacing)
        return self

    def filled_circle(self, cx, cy, radius, angle=0, spacing=0.8, segments=64):
        """Draw and fill a circle."""
        pts = []
        for i in range(segments):
            a = 2 * math.pi * i / segments
            pts.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
        self.circle(cx, cy, radius, segments=segments)
        self.fill(pts, angle=angle, spacing=spacing)
        return self

    def filled_ellipse(self, cx, cy, rx, ry, angle=0, spacing=0.8, segments=64):
        """Draw and fill an ellipse."""
        pts = []
        for i in range(segments):
            a = 2 * math.pi * i / segments
            pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
        self.ellipse(cx, cy, rx, ry, segments=segments)
        self.fill(pts, angle=angle, spacing=spacing)
        return self

    def filled_polygon(self, points, angle=0, spacing=0.8):
        """Draw and fill a polygon."""
        self.polygon(points)
        self.fill(points, angle=angle, spacing=spacing)
        return self

    def filled_star(self, cx, cy, outer_r, inner_r, num_points=5, angle=0, spacing=0.8):
        """Draw and fill a star."""
        pts = []
        for i in range(num_points * 2):
            a = math.pi * i / num_points - math.pi / 2
            r = outer_r if i % 2 == 0 else inner_r
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        self.star(cx, cy, outer_r, inner_r, num_points)
        self.fill(pts, angle=angle, spacing=spacing)
        return self

    # ── Satin stitch ───────────────────────────────────────────

    def satin(self, points_a, points_b):
        """Satin stitch between two parallel paths of equal length.

        Zig-zags between corresponding points on path A and path B.
        """
        if len(points_a) != len(points_b) or len(points_a) < 2:
            raise ValueError("Satin paths must have equal length >= 2")
        self.move_to(*points_a[0])
        for i in range(len(points_a)):
            self._walk(self._x, self._y, *points_a[i])
            self._walk(*points_a[i], *points_b[i])
        return self

    def satin_line(self, x0, y0, x1, y1, width=2.0):
        """Draw a satin-stitched line with given width."""
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        if length == 0:
            return self
        nx, ny = -dy / length * width / 2, dx / length * width / 2

        steps = max(2, math.ceil(length / self.stitch_length))
        path_a, path_b = [], []
        for i in range(steps + 1):
            t = i / steps
            mx, my = x0 + dx * t, y0 + dy * t
            path_a.append((mx + nx, my + ny))
            path_b.append((mx - nx, my - ny))
        return self.satin(path_a, path_b)

    # ── Text (basic block letters) ─────────────────────────────

    _FONT = {
        'A': [[(0,1),(0.5,0),(1,1)],[(0.25,0.5),(0.75,0.5)]],
        'B': [[(0,0),(0,1),(0.75,1),(0.75,0.5),(0,0.5),(0.75,0.5),(0.75,0),(0,0)]],
        'C': [[(1,0),(0,0),(0,1),(1,1)]],
        'D': [[(0,0),(0,1),(0.75,1),(1,0.75),(1,0.25),(0.75,0),(0,0)]],
        'E': [[(1,0),(0,0),(0,0.5),(0.75,0.5),(0,0.5),(0,1),(1,1)]],
        'F': [[(0,1),(0,0),(1,0),(0,0),(0,0.5),(0.75,0.5)]],
        'G': [[(1,0),(0,0),(0,1),(1,1),(1,0.5),(0.5,0.5)]],
        'H': [[(0,0),(0,1)],[(0,0.5),(1,0.5)],[(1,0),(1,1)]],
        'I': [[(0.25,0),(0.75,0)],[(0.5,0),(0.5,1)],[(0.25,1),(0.75,1)]],
        'J': [[(0.25,0),(0.75,0),(0.75,1),(0.25,1),(0,0.75)]],
        'K': [[(0,0),(0,1)],[(1,0),(0,0.5),(1,1)]],
        'L': [[(0,0),(0,1),(1,1)]],
        'M': [[(0,1),(0,0),(0.5,0.5),(1,0),(1,1)]],
        'N': [[(0,1),(0,0),(1,1),(1,0)]],
        'O': [[(0,0),(1,0),(1,1),(0,1),(0,0)]],
        'P': [[(0,1),(0,0),(1,0),(1,0.5),(0,0.5)]],
        'Q': [[(0,0),(1,0),(1,1),(0,1),(0,0)],[(0.6,0.8),(1,1.1)]],
        'R': [[(0,1),(0,0),(1,0),(1,0.5),(0,0.5),(1,1)]],
        'S': [[(1,0),(0,0),(0,0.5),(1,0.5),(1,1),(0,1)]],
        'T': [[(0,0),(1,0)],[(0.5,0),(0.5,1)]],
        'U': [[(0,0),(0,1),(1,1),(1,0)]],
        'V': [[(0,0),(0.5,1),(1,0)]],
        'W': [[(0,0),(0.25,1),(0.5,0.5),(0.75,1),(1,0)]],
        'X': [[(0,0),(1,1)],[(1,0),(0,1)]],
        'Y': [[(0,0),(0.5,0.5),(1,0)],[(0.5,0.5),(0.5,1)]],
        'Z': [[(0,0),(1,0),(0,1),(1,1)]],
        '0': [[(0,0),(1,0),(1,1),(0,1),(0,0)],[(0,1),(1,0)]],
        '1': [[(0.25,0.25),(0.5,0)],[(0.5,0),(0.5,1)],[(0.25,1),(0.75,1)]],
        '2': [[(0,0.25),(0.25,0),(0.75,0),(1,0.25),(1,0.5),(0,1),(1,1)]],
        '3': [[(0,0),(1,0),(1,0.5),(0.25,0.5),(1,0.5),(1,1),(0,1)]],
        '4': [[(0,0),(0,0.5),(1,0.5)],[(0.75,0),(0.75,1)]],
        '5': [[(1,0),(0,0),(0,0.5),(0.75,0.5),(1,0.75),(0.75,1),(0,1)]],
        '6': [[(1,0),(0,0),(0,1),(1,1),(1,0.5),(0,0.5)]],
        '7': [[(0,0),(1,0),(0.5,1)]],
        '8': [[(0.5,0.5),(0,0.25),(0,0),(1,0),(1,0.25),(0.5,0.5),(0,0.75),(0,1),(1,1),(1,0.75),(0.5,0.5)]],
        '9': [[(0,1),(1,1),(1,0),(0,0),(0,0.5),(1,0.5)]],
        ' ': [],
        '.': [[(0.4,0.9),(0.6,0.9),(0.6,1),(0.4,1),(0.4,0.9)]],
        ',': [[(0.5,0.9),(0.5,1.1)]],
        '!': [[(0.5,0),(0.5,0.7)],[(0.5,0.9),(0.5,1)]],
        '-': [[(0.2,0.5),(0.8,0.5)]],
    }

    def text(self, x, y, string, size=10):
        """Draw text as simple block letters.

        Args:
            x, y: Top-left position in mm.
            string: The string to draw.
            size: Character height in mm.
        """
        cursor_x = x
        char_width = size * 0.8
        spacing = size * 0.3

        for ch in string.upper():
            strokes = self._FONT.get(ch, [])
            for stroke in strokes:
                scaled = [(cursor_x + p[0] * char_width, y + p[1] * size) for p in stroke]
                self.polyline(scaled)
            cursor_x += char_width + spacing
        return self

    # ── Output ─────────────────────────────────────────────────

    def save(self, filename):
        """Finalize and save the pattern to a file.

        The format is determined by the file extension (e.g., .dst, .pes, .jef).
        """
        self.pattern.add_command(pyembroidery.END)
        pyembroidery.write(self.pattern, filename)
        return self
