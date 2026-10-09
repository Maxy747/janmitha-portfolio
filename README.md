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

The hero scrubs through 10 illustrated frames in `assets/turn/` (`000.webp … 009.webp`) as the cursor moves, or as you swipe on a phone. `frames.json` holds the count, the straight-on frame (`front`: 5) and each frame's head angle (`positions`, -1 left … +1 right). `front.webp` is shown before the script loads.

The frames come from a 33-frame Codex set (2026-10-09, navy saree), converted from 1033×1523 PNG to 760 px WebP. Only 10 were kept (`source_frames` in `frames.json` lists the original numbers). The rest were dropped because 14 of them repeated the same strong left turn with slightly different faces, several front and right views were near-duplicates (24–28 are all about the same angle), and the last frame (32) has a different, longer face. The `positions` come from measuring how far each frame's face has moved from the front frame toward the far-left/far-right one, not from even spacing.

The frames are transparent cutouts, so the giant name shows behind her. `tools/cutout_frames.py` keys out the plain studio backdrop by colour; there's no ML model, just numpy and Pillow. It also clears the light glow the generator drew around her hair, which otherwise shows as a white halo over the dark name. It reads the frames listed in `frames.json` (`source_frames`) from the Codex folder:

```bash
python tools/cutout_frames.py "C:\Users\MoeLustHer\Documents\Codex\2026-10-09\use-this-existing-interactive-portrait-c-2\outputs\janmitha-portfolio\assets\navy-turn" --preview check.png
```

To swap in a completely new set:

```bash
pip install "rembg[cpu]" pillow
python tools/build_frames.py "C:\path\to\frames"
```

If the new frames have a different aspect ratio, update the `<img id="portrait">` `width`/`height` and the `/ 1.475` ratio in `.portrait-stage`.

## Contact form

Uses [FormSubmit](https://formsubmit.co) posting to janmithav3@gmail.com. The very first message makes FormSubmit send her a one-time "Activate form" email; until she clicks it, messages won't be delivered.

## Credits

Site by [Max](https://github.com/Maxy747). Layout and motion reused from Shiza's portfolio, which was inspired by Maheen Dossal's portfolio.
