#!/usr/bin/env python3
"""Batch-convert PNG images to compressed JPG."""

import argparse
import os
import sys
from pathlib import Path


def convert_pngs(source_folder: str, quality: int) -> None:
    try:
        from PIL import Image
    except ImportError:
        print("ERROR: Pillow is not installed. Run: pip install Pillow", file=sys.stderr)
        sys.exit(1)

    source = Path(source_folder).resolve()
    if not source.is_dir():
        print(f"ERROR: '{source}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    output = source / "converted"
    output.mkdir(exist_ok=True)

    pngs = sorted(source.glob("*.png"), key=lambda p: p.name.lower())
    pngs += sorted(source.glob("*.PNG"), key=lambda p: p.name.lower())
    seen = set()
    unique_pngs = []
    for p in pngs:
        if p.name.lower() not in seen:
            seen.add(p.name.lower())
            unique_pngs.append(p)
    pngs = unique_pngs

    if not pngs:
        print("No PNG files found in the source folder.")
        sys.exit(0)

    total_src_size = 0
    total_dst_size = 0
    converted = 0
    skipped = 0
    failed = 0

    for png_path in pngs:
        jpg_name = png_path.stem + ".jpg"
        jpg_path = output / jpg_name

        if jpg_path.exists():
            print(f"  SKIP  {png_path.name} → already exists")
            skipped += 1
            continue

        try:
            img = Image.open(png_path)

            if img.mode in ("RGBA", "LA", "PA"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.getchannel("A"))
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            img.save(jpg_path, "JPEG", quality=quality, optimize=True)

            src_size = png_path.stat().st_size
            dst_size = jpg_path.stat().st_size
            total_src_size += src_size
            total_dst_size += dst_size
            reduction = (1 - dst_size / src_size) * 100 if src_size > 0 else 0

            print(f"  OK    {png_path.name} → {jpg_name}  "
                  f"({format_size(src_size)} → {format_size(dst_size)}, "
                  f"{reduction:.0f}% smaller)")
            converted += 1

        except Exception as e:
            print(f"  FAIL  {png_path.name} → {e}", file=sys.stderr)
            failed += 1

    print()
    print(f"Results: {converted} converted, {skipped} skipped, {failed} failed")
    if converted > 0:
        overall_reduction = (1 - total_dst_size / total_src_size) * 100 if total_src_size > 0 else 0
        print(f"Total size: {format_size(total_src_size)} → {format_size(total_dst_size)} "
              f"({overall_reduction:.0f}% reduction)")
    print(f"Output: {output}")


def format_size(num_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if abs(num_bytes) < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PNGs to compressed JPGs")
    parser.add_argument("source_folder", help="Folder containing PNG files")
    parser.add_argument("--quality", type=int, default=85,
                        help="JPG quality 1-100 (default: 85)")
    args = parser.parse_args()

    if not 1 <= args.quality <= 100:
        print("ERROR: Quality must be between 1 and 100.", file=sys.stderr)
        sys.exit(1)

    print(f"Converting PNGs in: {args.source_folder}")
    print(f"JPG quality: {args.quality}")
    print()
    convert_pngs(args.source_folder, args.quality)
