#!/usr/bin/env python3
"""
OndaMia — Generatore Icone PWA
Genera tutte le icone necessarie per la PWA e il Play Store.

Uso:
  pip install Pillow
  python3 generate_icons.py

Oppure con il tuo logo:
  python3 generate_icons.py --source logo.png
"""

import sys
import os
import argparse
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Installa Pillow: pip install Pillow")
    sys.exit(1)

SIZES = [72, 96, 128, 144, 152, 192, 384, 512]
OUTPUT_DIR = Path("icons")

def create_default_icon(size: int, maskable: bool = False) -> Image.Image:
    """Crea un'icona OndaMia con gradiente viola e emoji onda."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Padding per icone maskable (Google richiede safe zone del 10%)
    padding = int(size * 0.1) if maskable else 0

    # Sfondo con gradiente simulato (angolare viola → indaco)
    for y in range(size):
        ratio = y / size
        r = int(26 + ratio * (14 - 26))     # #1a -> #0e
        g = int(16 + ratio * (11 - 16))     # #10 -> #0b
        b = int(53 + ratio * (32 - 53))     # #35 -> #20
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))

    # Cerchio di sfondo con glow viola
    cx, cy = size // 2, size // 2
    radius = (size // 2) - padding - int(size * 0.04)

    # Cerchio esterno (glow)
    glow = int(size * 0.06)
    draw.ellipse(
        [cx - radius - glow, cy - radius - glow,
         cx + radius + glow, cy + radius + glow],
        fill=(192, 132, 252, 40)
    )
    # Cerchio principale
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=(30, 26, 56, 255)
    )
    # Bordo viola
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        outline=(192, 132, 252, 180), width=max(1, size // 40)
    )

    # Emoji 🌊 come testo (fallback: testo "OM")
    emoji_size = int(radius * 1.1)
    try:
        # Prova a caricare un font emoji di sistema
        font_paths = [
            "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
            "/System/Library/Fonts/Apple Color Emoji.ttc",
            "C:/Windows/Fonts/seguiemj.ttf",
        ]
        font = None
        for fp in font_paths:
            if os.path.exists(fp):
                font = ImageFont.truetype(fp, emoji_size)
                break

        if font:
            draw.text((cx, cy), "🌊", font=font, anchor="mm", embedded_color=True)
        else:
            raise Exception("No emoji font")
    except Exception:
        # Fallback: testo "OM" stilizzato
        text_size = int(radius * 0.7)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", text_size)
        except Exception:
            font = ImageFont.load_default()
        draw.text((cx, cy), "OM", font=font, fill=(192, 132, 252, 255), anchor="mm")

    return img

def generate_from_source(source_path: str, size: int, maskable: bool = False) -> Image.Image:
    """Ridimensiona e centra un'immagine sorgente."""
    src = Image.open(source_path).convert("RGBA")
    img = Image.new("RGBA", (size, size), (14, 11, 32, 255))
    padding = int(size * 0.12) if maskable else int(size * 0.08)
    inner = size - padding * 2
    src = src.resize((inner, inner), Image.LANCZOS)
    img.paste(src, (padding, padding), src)
    return img

def main():
    parser = argparse.ArgumentParser(description="Genera icone PWA per OndaMia")
    parser.add_argument("--source", type=str, help="Percorso logo sorgente (opzionale)")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"\n🌊 OndaMia — Generatore Icone")
    print(f"{'─' * 40}")

    for size in SIZES:
        maskable = size in [192, 512]
        fname = OUTPUT_DIR / f"icon-{size}.png"

        if args.source and os.path.exists(args.source):
            img = generate_from_source(args.source, size, maskable)
            print(f"  ✅ icon-{size}.png {'(maskable)' if maskable else ''} [da {args.source}]")
        else:
            img = create_default_icon(size, maskable)
            print(f"  ✅ icon-{size}.png {'(maskable)' if maskable else ''} [default]")

        img.save(fname, "PNG", optimize=True)

    print(f"\n{'─' * 40}")
    print(f"  📦 {len(SIZES)} icone generate in ./icons/")
    print(f"\n  💡 Per usare il tuo logo:")
    print(f"     python3 generate_icons.py --source il_tuo_logo.png\n")

if __name__ == "__main__":
    main()
