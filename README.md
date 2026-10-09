# Janmitha V Bangera — portfolio

Single-page portfolio for Janmitha: software, cybersecurity and data.
Plain HTML/CSS/JS in `index.html`, no build step and no libraries. Scrolling is native; the scroll-linked motion is hand-written.
Same layout and motion as [Shiza's portfolio](https://maxy747.github.io/shiza-portfolio/), rethemed navy and silver.

## Run locally

```bash
python -m http.server 5391
```

Then open http://localhost:5391.

## Photos

Originals live in `assets/src/` (git-ignored). `tools/build_photos.py` crops and compresses them into the files the page uses:

| File | Used for |
|---|---|
| `assets/about.webp` | "Say hi" photo |
| `assets/avatar.webp` | buddy, contact card, favicon |

```bash
pip install pillow
python tools/build_photos.py
```

Crop boxes are at the top of the script if a new photo needs reframing.

## Head turn

The hero scrubs through 33 illustrated frames in `assets/turn/` (`000.webp … 032.webp`) as the cursor moves, or as you swipe on a phone. `frames.json` holds the count, the straight-on frame (`front`: 20) and each frame's head angle (`positions`, -1 left … +1 right). `front.webp` is shown before the script loads.

The frames were generated in Codex (2026-10-09, navy saree set) as 1033×1523 PNGs and converted to 760 px WebP at quality 82, 2.1 MB for all 33. To swap in a new set:

```bash
pip install "rembg[cpu]" pillow
python tools/build_frames.py "C:\path\to\frames"
```

If the new frames have a different aspect ratio, update the `<img id="portrait">` `width`/`height` and the `/ 1.475` ratio in `.portrait-stage`.

## Contact form

Uses [FormSubmit](https://formsubmit.co) posting to janmithav3@gmail.com. The very first message makes FormSubmit send her a one-time "Activate form" email; until she clicks it, messages won't be delivered.

## Credits

Site by [Max](https://github.com/Maxy747). Layout and motion reused from Shiza's portfolio, which was inspired by Maheen Dossal's portfolio.
