"""Convert the realistic cat head drawing into embroidery files."""

from generate_realistic_cat import generate_realistic_cat
from image_to_embroidery import image_to_embroidery, image_to_embroidery_outline

# Generate source image
cat_path = generate_realistic_cat("cat_realistic.png", size=600)

# Filled embroidery — captures the shading and color regions
print("\nGenerating filled embroidery (DST)...")
image_to_embroidery(
    cat_path,
    "cat_realistic_filled.dst",
    width_mm=150,
    max_colors=10,
    fill_spacing=0.6,
    fill_angle=45,
    min_area=15,
    stitch_length=2.5,
    simplify=0.012,
)
print("Created cat_realistic_filled.dst")

# PES format for home machines
print("\nGenerating filled embroidery (PES)...")
image_to_embroidery(
    cat_path,
    "cat_realistic_filled.pes",
    width_mm=150,
    max_colors=10,
    fill_spacing=0.6,
    fill_angle=45,
    min_area=15,
    stitch_length=2.5,
    simplify=0.012,
)
print("Created cat_realistic_filled.pes")

# Outline / sketch version
print("\nGenerating outline embroidery...")
image_to_embroidery_outline(
    cat_path,
    "cat_realistic_outline.dst",
    width_mm=150,
    edge_threshold1=30,
    edge_threshold2=100,
    min_length=8,
    simplify=0.015,
)
print("Created cat_realistic_outline.dst")

print("\nDone! Files created:")
print("  cat_realistic.png              - source image")
print("  cat_realistic_filled.dst       - filled embroidery (DST)")
print("  cat_realistic_filled.pes       - filled embroidery (PES)")
print("  cat_realistic_outline.dst      - outline-only (DST)")
