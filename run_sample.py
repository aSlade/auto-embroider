"""Run an image-to-embroidery conversion and save results in a timestamped folder.

Usage:
    python run_sample.py <image_path> [--width 150] [--colors 10] [--spacing 0.6]
"""

import argparse
import os
import shutil
from datetime import datetime

from image_to_embroidery import image_to_embroidery, image_to_embroidery_outline


def run(image_path, width_mm=150, max_colors=10, fill_spacing=0.6):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    run_dir = os.path.join("samples", f"{timestamp}_{base_name}")
    os.makedirs(run_dir, exist_ok=True)

    # Copy source image into run folder
    src_copy = os.path.join(run_dir, os.path.basename(image_path))
    shutil.copy2(image_path, src_copy)

    # Filled embroidery — DST
    dst_path = os.path.join(run_dir, f"{base_name}_filled.dst")
    print(f"Generating filled DST -> {dst_path}")
    image_to_embroidery(
        image_path, dst_path,
        width_mm=width_mm, max_colors=max_colors,
        fill_spacing=fill_spacing, fill_angle=45,
        min_area=15, stitch_length=2.5, simplify=0.012,
    )

    # Filled embroidery — PES
    pes_path = os.path.join(run_dir, f"{base_name}_filled.pes")
    print(f"Generating filled PES -> {pes_path}")
    image_to_embroidery(
        image_path, pes_path,
        width_mm=width_mm, max_colors=max_colors,
        fill_spacing=fill_spacing, fill_angle=45,
        min_area=15, stitch_length=2.5, simplify=0.012,
    )

    # Outline-only embroidery
    outline_path = os.path.join(run_dir, f"{base_name}_outline.dst")
    print(f"Generating outline DST -> {outline_path}")
    image_to_embroidery_outline(
        image_path, outline_path,
        width_mm=width_mm,
        edge_threshold1=30, edge_threshold2=100,
        min_length=8, simplify=0.015,
    )

    # Write a run info file
    info_path = os.path.join(run_dir, "run_info.txt")
    with open(info_path, "w") as f:
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Source: {image_path}\n")
        f.write(f"Width: {width_mm}mm\n")
        f.write(f"Colors: {max_colors}\n")
        f.write(f"Fill spacing: {fill_spacing}mm\n")
        f.write(f"Fill angle: 45deg\n")
        f.write(f"Outputs:\n")
        for p in [dst_path, pes_path, outline_path]:
            size_kb = os.path.getsize(p) / 1024
            f.write(f"  {os.path.basename(p)} ({size_kb:.1f} KB)\n")

    print(f"\nRun complete: {run_dir}/")
    for fname in sorted(os.listdir(run_dir)):
        fpath = os.path.join(run_dir, fname)
        size_kb = os.path.getsize(fpath) / 1024
        print(f"  {fname} ({size_kb:.1f} KB)")

    return run_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert image to embroidery")
    parser.add_argument("image", help="Path to source image")
    parser.add_argument("--width", type=float, default=150, help="Width in mm")
    parser.add_argument("--colors", type=int, default=10, help="Max thread colors")
    parser.add_argument("--spacing", type=float, default=0.6, help="Fill line spacing in mm")
    args = parser.parse_args()
    run(args.image, width_mm=args.width, max_colors=args.colors, fill_spacing=args.spacing)
