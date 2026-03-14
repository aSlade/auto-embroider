"""Test script: convert a cat image to embroidery files."""

from generate_cat import generate_cat_image
from image_to_embroidery import image_to_embroidery, image_to_embroidery_outline

# Generate the test cat image
cat_path = generate_cat_image("cat.png", size=400)

# Full color embroidery (filled regions + outlines)
print("\nGenerating filled embroidery...")
image_to_embroidery(
    cat_path,
    "cat_filled.dst",
    width_mm=120,
    max_colors=6,
    fill_spacing=0.8,
    fill_angle=45,
    min_area=30,
)
print("Created cat_filled.dst")

# Outline-only embroidery (sketch style)
print("\nGenerating outline embroidery...")
image_to_embroidery_outline(
    cat_path,
    "cat_outline.dst",
    width_mm=120,
    edge_threshold1=40,
    edge_threshold2=120,
    min_length=10,
)
print("Created cat_outline.dst")

# Also save as .pes format (common for home embroidery machines)
print("\nGenerating PES format...")
image_to_embroidery(
    cat_path,
    "cat_filled.pes",
    width_mm=120,
    max_colors=6,
    fill_spacing=0.8,
)
print("Created cat_filled.pes")

print("\nDone! Files created:")
print("  cat.png          - source image")
print("  cat_filled.dst   - filled embroidery (DST)")
print("  cat_filled.pes   - filled embroidery (PES)")
print("  cat_outline.dst  - outline-only embroidery (DST)")
