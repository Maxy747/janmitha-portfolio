"""Cut the plain studio background out of the head-turn frames, so the giant name shows behind her.

The Codex frames sit on a smooth pale-blue background, which is far from her hair, skin and the navy
saree in colour. So no ML model is needed:

  1. Model the background as a smooth colour gradient, fitted to the frame's top and side edges.
  2. Measure how much darker each pixel is than that gradient and turn it into a soft alpha
     (soft so hair wisps fade instead of getting a hard edge; lighter-than-background glow is dropped).
  3. Only remove background that is connected to the frame edge, so light details inside her
     (eye whites, silver stripes, earrings) are never punched out.
  4. Pull the leftover blue tint out of semi-transparent edge pixels (decontamination).

Reads the frames listed in assets/turn/frames.json ("source_frames": a number is a frame from the
Codex folder, a file name is an extra frame in assets/src/turn-extra/) and writes
assets/turn/000.webp ... plus front.webp, with transparency.

Usage (from the repo root):
    python tools/cutout_frames.py "C:\\path\\to\\navy-turn"
    python tools/cutout_frames.py "C:\\path\\to\\navy-turn" --preview out.png   # checkerboard sheet

Needs numpy and Pillow.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TURN = ROOT / "assets" / "turn"
EXTRA = ROOT / "assets" / "src" / "turn-extra"
WIDTH = 760

# colour distance (0-255 RGB space) below LO is pure background, above HI is pure subject
LO, HI = 18.0, 46.0


def fit_background(rgb: np.ndarray) -> np.ndarray:
    """Least-squares quadratic colour surface fitted to a band along the top and side edges."""
    h, w, _ = rgb.shape
    band = max(8, w // 40)
    mask = np.zeros((h, w), bool)
    mask[:band, :] = True
    mask[: int(h * .55), :band] = True
    mask[: int(h * .55), -band:] = True
    ys, xs = np.nonzero(mask)
    # drop edge pixels that are clearly not background (hair touching the edge)
    vals = rgb[ys, xs]
    keep = vals.mean(1) > 170
    ys, xs, vals = ys[keep], xs[keep], vals[keep]
    def basis(y, x):
        y = y / h; x = x / w
        return np.stack([np.ones_like(x), x, y, x * x, y * y, x * y], 1)
    coef, *_ = np.linalg.lstsq(basis(ys, xs), vals, rcond=None)
    gy, gx = np.mgrid[0:h, 0:w]
    return (basis(gy.ravel().astype(float), gx.ravel().astype(float)) @ coef).reshape(h, w, 3)


def box_mean(a: np.ndarray, r: int) -> np.ndarray:
    """Mean of `a` over a (2r+1)x(2r+1) window, via an integral image (edges clamped)."""
    p = np.pad(a, r + 1, mode="edge")
    s = p.cumsum(0).cumsum(1)
    k = 2 * r + 1
    h, w = a.shape
    tot = s[k:k + h, k:k + w] - s[:h, k:k + w] - s[k:k + h, :w] + s[:h, :w]
    return tot / (k * k)


def edge_connected(candidate: np.ndarray) -> np.ndarray:
    """Pixels of `candidate` reachable from the top/left/right border (iterative geodesic dilation)."""
    seed = np.zeros_like(candidate)
    seed[0, :] = candidate[0, :]
    seed[:, 0] = candidate[:, 0]
    seed[:, -1] = candidate[:, -1]
    reach = seed
    while True:
        grown = reach.copy()
        grown[1:, :] |= reach[:-1, :]
        grown[:-1, :] |= reach[1:, :]
        grown[:, 1:] |= reach[:, :-1]
        grown[:, :-1] |= reach[:, 1:]
        grown &= candidate
        if (grown == reach).all():
            return reach
        reach = grown


def cutout(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    img = img.resize((WIDTH, round(img.height * WIDTH / img.width)), Image.LANCZOS)
    rgb = np.asarray(img, dtype=float)
    bg = fit_background(rgb)
    # Only count how much DARKER a pixel is than the background, per channel. Hair, skin and the
    # saree are all darker than the pale studio backdrop in at least one channel, while the light
    # glow the generator left around her hair is brighter, so it is treated as background
    # (otherwise it shows as a white halo over the dark name behind her).
    dist = np.sqrt((np.minimum(rgb - bg, 0) ** 2).sum(2))
    alpha = np.clip((dist - LO) / (HI - LO), 0, 1)
    # anything not connected to the edge through background-ish pixels stays fully opaque...
    outside = edge_connected(alpha < 1)
    alpha[~outside] = 1
    # Hair edges: the generator drew a band of light grey/bluish strands around her hair outline,
    # plus backdrop showing through gaps between strands. Real hair here is dark (~45 brightness), so
    # treat any light, non-warm pixel as dark hair blended with the backdrop and take its alpha from
    # how far it sits between the two. Skip anything near skin (eye whites, earrings, face highlights)
    # or near the navy saree (its silver stripes).
    r, b = rgb[..., 0], rgb[..., 2]
    lum = rgb.mean(2)
    skin = (r - b > 25) & (lum > 110)
    navy = (b - r > 30) & (lum < 130)
    away = (box_mean(skin.astype(float), 12) < 0.1) & (box_mean(navy.astype(float), 12) < 0.15)
    light_cool = (b - r > -10) & (lum > 95)
    HAIR_LUM = 45.0
    mix = np.clip((bg.mean(2) - lum) / (bg.mean(2) - HAIR_LUM), 0, 1)
    edge = away & light_cool
    alpha[edge] = np.minimum(alpha[edge], mix[edge])
    # decontaminate: remove the background's share from partly transparent pixels
    a = alpha[..., None]
    fg = np.where(a > 0.02, (rgb - (1 - a) * bg) / np.maximum(a, 0.02), rgb)
    out = np.dstack([np.clip(fg, 0, 255), alpha * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", type=Path, help="folder with the original 000.png ... frames")
    ap.add_argument("--preview", type=Path, help="also write a checkerboard contact sheet here")
    args = ap.parse_args()

    meta = json.loads((TURN / "frames.json").read_text(encoding="utf-8"))
    frames = []
    for n, i in enumerate(meta["source_frames"]):
        # a number is a frame of the original Codex set; a name is an extra frame kept in assets/src/turn-extra/
        path = args.source / f"{i:03d}.png" if isinstance(i, int) else EXTRA / i
        im = cutout(Image.open(path))
        im.save(TURN / f"{n:03d}.webp", "WEBP", quality=84, alpha_quality=90, method=6)
        if n == meta["front"]:
            im.save(TURN / "front.webp", "WEBP", quality=84, alpha_quality=90, method=6)
        frames.append(im)
        print(f"{n:03d}.webp  <- {path.name}  {(TURN / f'{n:03d}.webp').stat().st_size // 1024} KB")

    if args.preview:
        tw = 260; th = round(frames[0].height * tw / frames[0].width)
        sheet = Image.new("RGB", (tw * len(frames), th), "white")
        yy, xx = np.mgrid[0:th, 0:tw]
        checker = Image.fromarray(np.where(((yy // 12 + xx // 12) % 2)[..., None], 200, 255).repeat(3, 2).astype(np.uint8))
        for k, f in enumerate(frames):
            tile = checker.copy(); tile.paste(f.resize((tw, th)), (0, 0), f.resize((tw, th)))
            sheet.paste(tile, (k * tw, 0))
        sheet.save(args.preview)


if __name__ == "__main__":
    main()
