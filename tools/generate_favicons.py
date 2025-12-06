"""
Generate favicon and app icon assets from a source logo image.

Usage (PowerShell):
  & \
  "C:/Users/JefferyAlexander/Dropbox/chatbot/FullSiteNewPages/backporch-chair-app/bp-chairperson-app/.venv/Scripts/python.exe" \
  tools/generate_favicons.py \
  --src "C:\\Users\\JefferyAlexander\\Dropbox\\chatbot\\FullSiteNewPages\\assets\\pdfs\\backporch-logo.png" \
  --out "static/img"

If you don't have the logo saved locally yet, place a high-resolution square PNG (preferably 512x512 or larger)
and pass its path as --src.
"""

import argparse
from pathlib import Path
from PIL import Image

PNG_SIZES = [16, 32, 180]  # 180x180 used by iOS apple-touch-icon
ICO_SIZES = [16, 32, 48, 64]

def make_square(img: Image.Image, fill=(255, 255, 255, 0)) -> Image.Image:
    """Pad image to square with transparent or specified fill background."""
    w, h = img.size
    if w == h:
        return img
    side = max(w, h)
    square = Image.new("RGBA", (side, side), fill)
    offset = ((side - w) // 2, (side - h) // 2)
    square.paste(img, offset)
    return square

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True, help="Path to source logo image (PNG/JPG).")
    parser.add_argument("--out", default="static/img", help="Output directory for generated icons.")
    args = parser.parse_args()

    src_path = Path(args.src)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    img = Image.open(src_path).convert("RGBA")
    img_sq = make_square(img)

    # Generate PNG sizes
    for size in PNG_SIZES:
        png_out = out_dir / f"favicon-{size}x{size}.png"
        img_sq.resize((size, size), Image.LANCZOS).save(png_out, format="PNG")
        print(f"Wrote {png_out}")

    # Apple touch icon 180x180
    apple_out = out_dir / "apple-touch-icon.png"
    img_sq.resize((180, 180), Image.LANCZOS).save(apple_out, format="PNG")
    print(f"Wrote {apple_out}")

    # Generate ICO with multiple sizes
    ico_out = out_dir / "favicon.ico"
    # For ICO, provide a list of resized images
    imgs = [img_sq.resize((s, s), Image.LANCZOS) for s in ICO_SIZES]
    imgs[0].save(ico_out, format="ICO", sizes=[(s, s) for s in ICO_SIZES])
    print(f"Wrote {ico_out}")

    # Save a standard brand logo used in navbar (28x28 recommended in template)
    logo_out = out_dir / "backporch-logo.png"
    img_sq.resize((256, 256), Image.LANCZOS).save(logo_out, format="PNG")
    print(f"Wrote {logo_out}")

if __name__ == "__main__":
    main()
