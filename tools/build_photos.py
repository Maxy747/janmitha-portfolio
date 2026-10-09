"""Crop and compress Janmitha's photos from assets/src/ into the web assets the page uses.

    assets/about.webp    "Say hi" photo (photo 2)
    assets/avatar.webp   small circle: buddy, contact card, favicon (photo 3)

Usage (from the repo root):  python tools/build_photos.py
Needs Pillow:  pip install pillow
"""
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "assets" / "src", ROOT / "assets"

# (source, output, crop box (left, top, right, bottom) or None, output size)
JOBS = [
    ("about.jpg", "about.webp", None, (900, 1200)),
    ("avatar.jpg", "avatar.webp", (347, 355, 687, 695), (256, 256)),
]


def main() -> None:
    for src, out, box, size in JOBS:
        im = ImageOps.exif_transpose(Image.open(SRC / src)).convert("RGB")
        if box:
            im = im.crop(box)
        if size:
            im = im.resize(size, Image.LANCZOS)
        im.save(OUT / out, "WEBP", quality=84, method=6)
        print(f"{out}: {im.width}x{im.height}, {(OUT / out).stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
