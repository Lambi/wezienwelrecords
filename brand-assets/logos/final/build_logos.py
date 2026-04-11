#!/usr/bin/env python3
"""
WeZienWel Records — Final logo asset builder.
Generates:
  1. square-in-circle: square canvas with a circular badge containing the logo,
     in multiple brand color combos.
  2. transparent: no-background square canvas with the logo tinted in brand colors.
  3. favicon: sized PNGs + multi-size .ico for the web.
"""
from PIL import Image, ImageDraw
import os

BASE = os.path.dirname(os.path.abspath(__file__))
SRC_INK = os.path.join(os.path.dirname(BASE), "..", "..", "assets", "wzw-logo-ink.png")

# Brand palette (from WZW Brand Guide v1.0)
PAPER = (242, 238, 229, 255)   # #F2EEE5
INK   = (14,  14,  12,  255)   # #0E0E0C
RED   = (226, 61,  40,  255)   # #E23D28
DUST  = (184, 179, 168, 255)   # #B8B3A8
GHOST = (26,  26,  23,  255)   # #1A1A17
BLUE  = (31,  59,  255, 255)   # #1F3BFF

def load_logo_mask():
    """Return a grayscale alpha mask for the logo, with transparent margins trimmed."""
    img = Image.open(SRC_INK).convert("RGBA")
    alpha = img.split()[-1]
    bbox = alpha.getbbox()
    cropped = img.crop(bbox)
    return cropped  # RGBA, black pixels on transparent

def recolor(logo, rgba):
    """Return a new RGBA image where visible pixels are replaced with `rgba`,
    preserving the logo's original alpha."""
    base = logo.copy()
    alpha = base.split()[-1]
    solid = Image.new("RGBA", base.size, rgba)
    solid.putalpha(alpha)
    return solid

def paste_centered(canvas, layer, scale_to_w):
    """Fit `layer` to width `scale_to_w` and paste centered on `canvas`."""
    w, h = layer.size
    new_w = int(scale_to_w)
    new_h = int(h * (new_w / w))
    resized = layer.resize((new_w, new_h), Image.LANCZOS)
    cw, ch = canvas.size
    x = (cw - new_w) // 2
    y = (ch - new_h) // 2
    canvas.alpha_composite(resized, (x, y))
    return canvas

def make_square_in_circle(size, bg, circle_bg, logo_color, out_path, logo):
    """Square canvas, circular badge centered, logo on the badge."""
    canvas = Image.new("RGBA", (size, size), bg)
    draw = ImageDraw.Draw(canvas)
    # circle
    margin = int(size * 0.08)
    draw.ellipse([margin, margin, size - margin, size - margin], fill=circle_bg, outline=INK, width=max(2, size // 180))
    # inner subtle ring
    inner = int(size * 0.11)
    draw.ellipse([inner, inner, size - inner, size - inner], outline=logo_color, width=max(1, size // 400))
    # logo
    tinted = recolor(logo, logo_color)
    paste_centered(canvas, tinted, size * 0.48)
    canvas.save(out_path, "PNG")
    print(f"  → {os.path.basename(out_path)}")

def make_transparent(size, logo_color, out_path, logo):
    """Square transparent canvas with logo only, tinted."""
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    tinted = recolor(logo, logo_color)
    paste_centered(canvas, tinted, size * 0.78)
    canvas.save(out_path, "PNG")
    print(f"  → {os.path.basename(out_path)}")

def make_favicon_set(logo):
    """Paper square with circle + ink logo, sized for web favicon use."""
    out_dir = os.path.join(BASE, "favicon")
    sizes = [16, 32, 48, 64, 128, 180, 192, 256, 512]
    print("[favicon]")
    master = Image.new("RGBA", (512, 512), PAPER)
    d = ImageDraw.Draw(master)
    m = int(512 * 0.06)
    d.ellipse([m, m, 512 - m, 512 - m], fill=PAPER, outline=INK, width=6)
    d.ellipse([m + 10, m + 10, 512 - m - 10, 512 - m - 10], outline=RED, width=2)
    tinted = recolor(logo, INK)
    paste_centered(master, tinted, 512 * 0.52)
    for s in sizes:
        out = master.resize((s, s), Image.LANCZOS)
        out.save(os.path.join(out_dir, f"favicon-{s}.png"), "PNG")
        print(f"  → favicon-{s}.png")
    # multi-size ICO
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    master.save(os.path.join(out_dir, "favicon.ico"), format="ICO", sizes=ico_sizes)
    print("  → favicon.ico")
    # Dark-mode favicon (ink square, paper logo)
    dark = Image.new("RGBA", (512, 512), INK)
    d2 = ImageDraw.Draw(dark)
    d2.ellipse([m, m, 512 - m, 512 - m], fill=INK, outline=PAPER, width=6)
    d2.ellipse([m + 10, m + 10, 512 - m - 10, 512 - m - 10], outline=RED, width=2)
    tinted2 = recolor(logo, PAPER)
    paste_centered(dark, tinted2, 512 * 0.52)
    for s in sizes:
        out = dark.resize((s, s), Image.LANCZOS)
        out.save(os.path.join(out_dir, f"favicon-dark-{s}.png"), "PNG")
    print("  → favicon-dark-{sizes}.png")

def main():
    logo = load_logo_mask()
    print(f"Source logo: {logo.size}")

    # 1. SQUARE-IN-CIRCLE (background color combos)
    print("\n[square-in-circle]")
    sic_dir = os.path.join(BASE, "square-in-circle")
    combos = [
        ("paper-on-ink",   INK,   PAPER, INK),    # ink frame, paper circle, ink logo
        ("ink-on-paper",   PAPER, INK,   PAPER),  # paper frame, ink circle, paper logo
        ("red-on-paper",   PAPER, RED,   PAPER),  # paper frame, red circle, paper logo
        ("red-on-ink",     INK,   RED,   PAPER),  # ink frame, red circle, paper logo
        ("paper-on-red",   RED,   PAPER, INK),    # red frame, paper circle, ink logo
        ("ink-on-red",     RED,   INK,   PAPER),  # red frame, ink circle, paper logo
        ("dust-on-ink",    INK,   DUST,  INK),    # ink frame, dust circle, ink logo
        ("paper-on-blue",  BLUE,  PAPER, INK),    # blue frame (reserved), paper circle
    ]
    for name, bg, circle_bg, logo_color in combos:
        make_square_in_circle(2000, bg, circle_bg, logo_color,
                              os.path.join(sic_dir, f"wzw-sic-{name}-2000.png"), logo)
        make_square_in_circle(800, bg, circle_bg, logo_color,
                              os.path.join(sic_dir, f"wzw-sic-{name}-800.png"), logo)

    # 2. TRANSPARENT (logo-only, color variants)
    print("\n[transparent]")
    tr_dir = os.path.join(BASE, "transparent")
    colors = [
        ("ink",   INK),
        ("paper", PAPER),
        ("red",   RED),
        ("dust",  DUST),
        ("ghost", GHOST),
        ("blue",  BLUE),
    ]
    for name, c in colors:
        make_transparent(2000, c, os.path.join(tr_dir, f"wzw-logo-{name}-2000.png"), logo)
        make_transparent(800,  c, os.path.join(tr_dir, f"wzw-logo-{name}-800.png"),  logo)

    # 3. FAVICON
    make_favicon_set(logo)

    print("\nDone.")

if __name__ == "__main__":
    main()
