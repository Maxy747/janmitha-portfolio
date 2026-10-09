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
| `assets/hero.webp` | arched hero portrait |
| `assets/about.webp` | "Say hi" photo |
| `assets/avatar.webp` | buddy, contact card, favicon |

```bash
pip install pillow
python tools/build_photos.py
```

Crop boxes are at the top of the script if a new photo needs reframing.

## Adding a head turn (optional)

Right now the hero photo just leans toward the cursor. To get Shiza-style head turning, generate an ordered set of illustrated portraits (15–30 frames, left → right) and run:

```bash
pip install "rembg[cpu]" pillow
python tools/build_frames.py "C:\path\to\frames"
```

That writes `assets/turn/000.webp …` and `assets/turn/frames.json`, which the page picks up automatically. Point the `<img id="portrait">` `src` at `assets/turn/front.webp` and set its `width`/`height` to the frame size.

## Contact form

Uses [FormSubmit](https://formsubmit.co) posting to janmithav3@gmail.com. The very first message makes FormSubmit send her a one-time "Activate form" email; until she clicks it, messages won't be delivered.

## Credits

Site by [Max](https://github.com/Maxy747). Layout and motion reused from Shiza's portfolio, which was inspired by Maheen Dossal's portfolio.
