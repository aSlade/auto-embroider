"""Generate a simple cat image for testing the embroidery converter."""

from PIL import Image, ImageDraw


def generate_cat_image(path="cat.png", size=400):
    """Draw a simple cartoon cat face and save it."""
    img = Image.new("RGB", (size, size), (255, 255, 255))
    d = ImageDraw.Draw(img)
    s = size

    # Body / head (dark gray circle)
    head_color = (80, 80, 80)
    d.ellipse([s*0.15, s*0.25, s*0.85, s*0.9], fill=head_color)

    # Left ear (triangle)
    ear_color = (60, 60, 60)
    d.polygon([(s*0.18, s*0.32), (s*0.28, s*0.05), (s*0.42, s*0.28)], fill=ear_color)
    # Inner left ear (pink)
    d.polygon([(s*0.22, s*0.30), (s*0.30, s*0.12), (s*0.38, s*0.28)], fill=(220, 140, 140))

    # Right ear
    d.polygon([(s*0.58, s*0.28), (s*0.72, s*0.05), (s*0.82, s*0.32)], fill=ear_color)
    # Inner right ear
    d.polygon([(s*0.62, s*0.28), (s*0.70, s*0.12), (s*0.78, s*0.30)], fill=(220, 140, 140))

    # Eyes (green with black pupils)
    eye_color = (100, 200, 80)
    # Left eye
    d.ellipse([s*0.25, s*0.40, s*0.42, s*0.55], fill=eye_color)
    d.ellipse([s*0.30, s*0.44, s*0.37, s*0.52], fill=(20, 20, 20))
    # Right eye
    d.ellipse([s*0.58, s*0.40, s*0.75, s*0.55], fill=eye_color)
    d.ellipse([s*0.63, s*0.44, s*0.70, s*0.52], fill=(20, 20, 20))

    # Nose (pink triangle)
    d.polygon([(s*0.46, s*0.58), (s*0.54, s*0.58), (s*0.50, s*0.64)], fill=(220, 120, 120))

    # Mouth
    d.arc([s*0.38, s*0.60, s*0.50, s*0.72], 0, 180, fill=(40, 40, 40), width=2)
    d.arc([s*0.50, s*0.60, s*0.62, s*0.72], 0, 180, fill=(40, 40, 40), width=2)

    # Whiskers
    whisker_color = (180, 180, 180)
    ww = 2
    # Left whiskers
    d.line([(s*0.10, s*0.55), (s*0.38, s*0.60)], fill=whisker_color, width=ww)
    d.line([(s*0.08, s*0.62), (s*0.38, s*0.64)], fill=whisker_color, width=ww)
    d.line([(s*0.10, s*0.70), (s*0.38, s*0.68)], fill=whisker_color, width=ww)
    # Right whiskers
    d.line([(s*0.62, s*0.60), (s*0.90, s*0.55)], fill=whisker_color, width=ww)
    d.line([(s*0.62, s*0.64), (s*0.92, s*0.62)], fill=whisker_color, width=ww)
    d.line([(s*0.62, s*0.68), (s*0.90, s*0.70)], fill=whisker_color, width=ww)

    img.save(path)
    print(f"Generated cat image: {path} ({size}x{size})")
    return path


if __name__ == "__main__":
    generate_cat_image()
