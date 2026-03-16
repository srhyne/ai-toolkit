---
name: png-to-jpg
description: Batch-convert PNG images to compressed JPG files. Use when the user asks to convert PNGs to JPGs, compress images, optimize image file sizes, or batch-convert images.
---

# PNG to JPG Converter

Batch-convert PNG images in a folder to compressed JPG files, preserving filenames.

## Workflow

### Step 1: Ask for the Source Folder

Use the AskQuestion tool or ask conversationally:

> "Which folder contains the PNG images you'd like to convert?"

Resolve the path relative to the workspace root. Verify the folder exists before proceeding.

### Step 2: Scan for PNGs

```bash
find <folder> -maxdepth 1 -iname '*.png' | head -50
```

Report how many PNGs were found. If none, stop and tell the user.

### Step 3: Ask for JPG Quality

Present quality options using AskQuestion (or ask conversationally):

| Option | Quality | Typical Size Reduction | Best For |
|--------|---------|----------------------|----------|
| High | 92 | ~60-70% smaller | Photography, detailed graphics |
| **Recommended** | **85** | **~75-85% smaller** | **General use — best balance of quality and size** |
| Medium | 75 | ~85-90% smaller | Web thumbnails, previews |
| Low | 60 | ~90-95% smaller | Placeholders, low-bandwidth |

Default recommendation: **85** — virtually indistinguishable from the original for most images while achieving significant compression.

### Step 4: Run the Conversion

Ensure Pillow is available, then run the conversion script:

```bash
pip install Pillow 2>/dev/null
python3 <skill_dir>/scripts/convert.py "<source_folder>" --quality <quality>
```

Where `<skill_dir>` is the absolute path to this skill's directory (the folder containing this SKILL.md).

The script will:
- Create a `converted/` subfolder inside the source folder
- Convert each PNG to JPG at the specified quality
- Handle transparency by compositing onto a white background
- Preserve the original filename (only the extension changes)
- Skip files that already exist in `converted/` (re-run safe)

### Step 5: Report Results

After conversion, report:
1. Number of images converted
2. Total size before and after (with % reduction)
3. Location of the converted files

## Edge Cases

- **Transparent PNGs**: Automatically composited onto a white background before saving as JPG (JPG does not support transparency).
- **Already exists**: Existing files in `converted/` are skipped. Inform the user if any were skipped.
- **Pillow not installed**: The script installs it automatically via pip.
- **Empty folder**: Stop early with a clear message.
- **Permission errors**: Report which files failed and continue with the rest.
