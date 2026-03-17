"""Run an image-to-embroidery conversion and save results in a timestamped folder.

Usage:
    python run_sample.py <image_path> [--width 150] [--colors 10] [--spacing 0.6]
"""

import argparse
import math
import os
import shutil
from datetime import datetime

import pyembroidery

from image_to_embroidery import image_to_embroidery, image_to_embroidery_outline


def embroidery_summary(filepath):
    """Read an embroidery file and return a summary dict with stats."""
    pattern = pyembroidery.read(filepath)
    stitches = pattern.stitches

    stitch_count = 0
    color_changes = 0
    total_length_mm = 0.0
    prev_x, prev_y = None, None

    for x, y, cmd in stitches:
        if cmd == pyembroidery.STITCH:
            stitch_count += 1
            if prev_x is not None:
                dx = (x - prev_x) / 10.0  # pyembroidery units are 0.1mm
                dy = (y - prev_y) / 10.0
                total_length_mm += math.hypot(dx, dy)
        elif cmd == pyembroidery.COLOR_CHANGE:
            color_changes += 1

        if cmd in (pyembroidery.STITCH, pyembroidery.TRIM, pyembroidery.JUMP):
            prev_x, prev_y = x, y

    num_colors = color_changes + 1 if stitch_count > 0 else 0

    # Estimate time: ~400 stitches/min for home machines, plus ~30s per color change
    minutes = stitch_count / 400.0 + color_changes * 0.5
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    time_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"

    return {
        "stitches": stitch_count,
        "colors": num_colors,
        "thread_length_m": total_length_mm / 1000.0,
        "estimated_time": time_str,
    }


def write_summary(embroidery_path):
    """Generate a .summary.txt file next to the embroidery file."""
    stats = embroidery_summary(embroidery_path)
    base = os.path.splitext(embroidery_path)[0]
    ext = os.path.splitext(embroidery_path)[1]
    summary_path = f"{base}{ext}.summary.txt"
    with open(summary_path, "w") as f:
        f.write(f"File: {os.path.basename(embroidery_path)}\n")
        f.write(f"Stitches: {stats['stitches']:,}\n")
        f.write(f"Thread colors: {stats['colors']}\n")
        f.write(f"Thread length: {stats['thread_length_m']:.1f} m\n")
        f.write(f"Estimated time: {stats['estimated_time']}\n")
    return summary_path


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

    write_summary(dst_path)

    # Filled embroidery — PES
    pes_path = os.path.join(run_dir, f"{base_name}_filled.pes")
    print(f"Generating filled PES -> {pes_path}")
    image_to_embroidery(
        image_path, pes_path,
        width_mm=width_mm, max_colors=max_colors,
        fill_spacing=fill_spacing, fill_angle=45,
        min_area=15, stitch_length=2.5, simplify=0.012,
    )

    write_summary(pes_path)

    # Outline-only embroidery
    outline_path = os.path.join(run_dir, f"{base_name}_outline.dst")
    print(f"Generating outline DST -> {outline_path}")
    image_to_embroidery_outline(
        image_path, outline_path,
        width_mm=width_mm,
        edge_threshold1=30, edge_threshold2=100,
        min_length=8, simplify=0.015,
    )

    write_summary(outline_path)

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
