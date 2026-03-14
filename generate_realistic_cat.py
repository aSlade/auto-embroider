"""Generate a realistic pencil-sketch style cat head image.

Replicates the style of the DragoArt 'how to draw a cat head' tutorial:
front-facing cat portrait with detailed shading, fur texture, and whiskers.
"""

import math
from PIL import Image, ImageDraw, ImageFilter


def _ellipse(d, cx, cy, rx, ry, fill=None, outline=None, width=1):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill, outline=outline, width=width)


def _fur_strokes(d, cx, cy, radius, count, length_range, angle_range, color_range, width=1):
    """Draw short fur-like strokes radiating from a center area."""
    import random
    random.seed(42)
    for _ in range(count):
        angle = random.uniform(*angle_range)
        r = random.uniform(0, radius)
        sx = cx + r * math.cos(angle)
        sy = cy + r * math.sin(angle)
        ln = random.uniform(*length_range)
        ex = sx + ln * math.cos(angle)
        ey = sy + ln * math.sin(angle)
        gray = random.randint(*color_range)
        d.line([(sx, sy), (ex, ey)], fill=(gray, gray, gray), width=width)


def generate_realistic_cat(path="cat_realistic.png", size=600):
    """Create a pencil-sketch style cat head portrait."""
    s = size
    img = Image.new("RGB", (s, s), (245, 240, 235))  # off-white paper
    d = ImageDraw.Draw(img)

    cx, cy = s * 0.50, s * 0.48  # head center

    # ── Head shape (slightly wider than tall) ──
    head_rx, head_ry = s * 0.30, s * 0.28
    # Base head fill - medium gray
    _ellipse(d, cx, cy, head_rx, head_ry, fill=(160, 155, 150))
    # Lighter center face area
    _ellipse(d, cx, cy + s*0.03, head_rx * 0.65, head_ry * 0.70, fill=(185, 180, 175))

    # ── Ears ──
    ear_color = (130, 125, 120)
    inner_ear = (195, 165, 160)
    # Left ear
    d.polygon([
        (cx - s*0.22, cy - s*0.18),
        (cx - s*0.15, cy - s*0.38),
        (cx - s*0.04, cy - s*0.20),
    ], fill=ear_color)
    d.polygon([
        (cx - s*0.19, cy - s*0.19),
        (cx - s*0.15, cy - s*0.33),
        (cx - s*0.07, cy - s*0.20),
    ], fill=inner_ear)
    # Right ear
    d.polygon([
        (cx + s*0.04, cy - s*0.20),
        (cx + s*0.15, cy - s*0.38),
        (cx + s*0.22, cy - s*0.18),
    ], fill=ear_color)
    d.polygon([
        (cx + s*0.07, cy - s*0.20),
        (cx + s*0.15, cy - s*0.33),
        (cx + s*0.19, cy - s*0.19),
    ], fill=inner_ear)

    # ── Forehead darker stripes (tabby markings) ──
    stripe_color = (110, 105, 100)
    for i, offset in enumerate([-0.08, 0.0, 0.08]):
        x = cx + s * offset
        top = cy - s * 0.20
        bot = cy - s * 0.08
        d.line([(x, top), (x - s*0.01, bot)], fill=stripe_color, width=max(2, s // 80))

    # ── Eyes ──
    eye_y = cy - s * 0.02
    eye_sep = s * 0.10
    eye_rx, eye_ry = s * 0.065, s * 0.045

    for side in [-1, 1]:
        ex = cx + side * eye_sep
        # Eye white / light area
        _ellipse(d, ex, eye_y, eye_rx, eye_ry, fill=(200, 195, 140))
        # Iris - yellow-green
        _ellipse(d, ex, eye_y, eye_rx * 0.85, eye_ry * 0.85, fill=(160, 170, 80))
        # Darker iris ring
        _ellipse(d, ex, eye_y, eye_rx * 0.85, eye_ry * 0.85, outline=(90, 100, 50), width=2)
        # Pupil - vertical slit
        pw = max(2, int(s * 0.012))
        d.ellipse([ex - pw, eye_y - eye_ry * 0.7, ex + pw, eye_y + eye_ry * 0.7],
                  fill=(20, 20, 20))
        # Eye highlight
        hl = max(2, int(s * 0.015))
        d.ellipse([ex - eye_rx*0.3 - hl, eye_y - eye_ry*0.3 - hl,
                   ex - eye_rx*0.3 + hl, eye_y - eye_ry*0.3 + hl],
                  fill=(240, 240, 240))
        # Eye outline
        _ellipse(d, ex, eye_y, eye_rx, eye_ry, outline=(40, 35, 30), width=2)
        # Dark eyeliner above
        d.arc([ex - eye_rx, eye_y - eye_ry, ex + eye_rx, eye_y + eye_ry],
              200, 340, fill=(30, 25, 20), width=3)

    # ── Nose ──
    nose_y = cy + s * 0.08
    nose_w, nose_h = s * 0.035, s * 0.025
    # Nose shape (rounded triangle)
    d.polygon([
        (cx, nose_y - nose_h),
        (cx - nose_w, nose_y + nose_h),
        (cx + nose_w, nose_y + nose_h),
    ], fill=(180, 130, 130))
    d.polygon([
        (cx, nose_y - nose_h),
        (cx - nose_w, nose_y + nose_h),
        (cx + nose_w, nose_y + nose_h),
    ], outline=(100, 70, 70), width=2)

    # ── Mouth ──
    mouth_y = nose_y + nose_h
    d.line([(cx, mouth_y), (cx, mouth_y + s*0.03)], fill=(80, 70, 65), width=2)
    d.arc([cx - s*0.06, mouth_y + s*0.005, cx, mouth_y + s*0.05],
          0, 180, fill=(80, 70, 65), width=2)
    d.arc([cx, mouth_y + s*0.005, cx + s*0.06, mouth_y + s*0.05],
          0, 180, fill=(80, 70, 65), width=2)

    # ── Muzzle area (lighter) ──
    _ellipse(d, cx, nose_y + s*0.01, s*0.08, s*0.045, fill=(195, 190, 185))
    # Redraw nose and mouth on top
    d.polygon([
        (cx, nose_y - nose_h),
        (cx - nose_w, nose_y + nose_h),
        (cx + nose_w, nose_y + nose_h),
    ], fill=(180, 130, 130), outline=(100, 70, 70), width=2)
    d.line([(cx, mouth_y), (cx, mouth_y + s*0.03)], fill=(80, 70, 65), width=2)
    d.arc([cx - s*0.06, mouth_y + s*0.005, cx, mouth_y + s*0.05],
          0, 180, fill=(80, 70, 65), width=2)
    d.arc([cx, mouth_y + s*0.005, cx + s*0.06, mouth_y + s*0.05],
          0, 180, fill=(80, 70, 65), width=2)

    # ── Whisker dots ──
    dot_r = max(1, s // 200)
    for side in [-1, 1]:
        for row in range(3):
            for col in range(2):
                dx = cx + side * (s * 0.04 + col * s * 0.015)
                dy = nose_y + s * 0.02 + row * s * 0.012
                d.ellipse([dx - dot_r, dy - dot_r, dx + dot_r, dy + dot_r], fill=(80, 75, 70))

    # ── Whiskers ──
    whisker_color = (210, 205, 200)
    ww = max(1, s // 300)
    for side in [-1, 1]:
        base_x = cx + side * s * 0.06
        for i, (angle_off, y_off) in enumerate([(-0.05, -0.01), (0, 0.01), (0.05, 0.03)]):
            sx = base_x
            sy = nose_y + s * 0.03 + s * y_off
            length = s * 0.22
            angle = (0 if side == 1 else math.pi) + angle_off
            ex = sx + length * math.cos(angle)
            ey = sy + length * math.sin(angle)
            d.line([(sx, sy), (ex, ey)], fill=whisker_color, width=ww)

    # ── Fur texture all over the head ──
    # Dark fur strokes around edges
    _fur_strokes(d, cx, cy, head_rx * 1.0, 800,
                 length_range=(s*0.01, s*0.04),
                 angle_range=(0, 2 * math.pi),
                 color_range=(90, 150), width=1)
    # Lighter fur in center
    _fur_strokes(d, cx, cy + s*0.02, head_rx * 0.5, 400,
                 length_range=(s*0.008, s*0.025),
                 angle_range=(0, 2 * math.pi),
                 color_range=(150, 200), width=1)

    # ── Chin / lower face darker ──
    _fur_strokes(d, cx, cy + s*0.18, s*0.12, 300,
                 length_range=(s*0.01, s*0.03),
                 angle_range=(math.pi*0.3, math.pi*0.7),
                 color_range=(110, 150), width=1)

    # ── Chest / neck area ──
    chest_y = cy + s * 0.30
    _ellipse(d, cx, chest_y, s * 0.22, s * 0.15, fill=(170, 165, 160))
    _fur_strokes(d, cx, chest_y, s * 0.18, 500,
                 length_range=(s*0.015, s*0.04),
                 angle_range=(math.pi*0.2, math.pi*0.8),
                 color_range=(120, 170), width=1)

    # ── Soften everything slightly ──
    img = img.filter(ImageFilter.GaussianBlur(radius=0.8))

    # ── Re-draw crisp eye outlines and whiskers on top ──
    d = ImageDraw.Draw(img)
    for side in [-1, 1]:
        ex = cx + side * eye_sep
        _ellipse(d, ex, eye_y, eye_rx, eye_ry, outline=(40, 35, 30), width=2)

    img.save(path)
    print(f"Generated realistic cat: {path} ({size}x{size})")
    return path


if __name__ == "__main__":
    generate_realistic_cat()
