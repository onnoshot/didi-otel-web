#!/usr/bin/env python3
"""Web-image pipeline for DİDİ Otel.
Generates multi-width AVIF + WebP + a JPEG fallback into assets/web/.
Idempotent: skips outputs that already exist and are newer than source.
Usage: python3 optimize-images.py [group ...]   (groups: editorial rooms gallery photos all)
"""
import os, sys, glob
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "assets")
OUT = os.path.join(ROOT, "assets", "web")
WIDTHS = [480, 800, 1280, 1920]          # responsive steps
AVIF_Q, WEBP_Q, JPG_Q = 52, 78, 82

def newer(src, dst):
    return os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src)

def process(src_path, slug):
    """slug = output basename (no ext). Emits slug-<w>.avif/.webp + slug.jpg (1920 fallback)."""
    try:
        im = Image.open(src_path)
        im = ImageOps.exif_transpose(im).convert("RGB")
    except Exception as e:
        print("  SKIP (open fail)", src_path, e); return 0
    w0 = im.width
    made = 0
    os.makedirs(os.path.dirname(os.path.join(OUT, slug)), exist_ok=True)
    for w in WIDTHS:
        if w > w0 and w != WIDTHS[0]:
            continue
        ww = min(w, w0); hh = round(im.height * ww / im.width)
        rim = im.resize((ww, hh), Image.LANCZOS)
        for ext, q, fmt in (("avif", AVIF_Q, "AVIF"), ("webp", WEBP_Q, "WEBP")):
            dst = os.path.join(OUT, f"{slug}-{w}.{ext}")
            if newer(src_path, dst): continue
            rim.save(dst, fmt, quality=q)
            made += 1
    # jpeg fallback at largest width
    jdst = os.path.join(OUT, f"{slug}.jpg")
    if not newer(src_path, jdst):
        wj = min(WIDTHS[-1], w0); hj = round(im.height * wj / im.width)
        im.resize((wj, hj), Image.LANCZOS).save(jdst, "JPEG", quality=JPG_Q, optimize=True, progressive=True)
        made += 1
    return made

def run_group(g):
    total = 0; n = 0
    if g == "editorial":
        for f in sorted(glob.glob(f"{SRC}/editorial/ONN*_editorial.png")):
            slug = "editorial/" + os.path.basename(f).replace("_editorial.png", "")
            total += process(f, slug); n += 1
    elif g == "rooms":
        for f in sorted(glob.glob(f"{SRC}/rooms/*/*.jpg")):
            rel = os.path.relpath(f, f"{SRC}/rooms")[:-4]
            total += process(f, "rooms/" + rel); n += 1
    elif g == "gallery":
        for f in sorted(glob.glob(f"{SRC}/gallery/*")):
            slug = "gallery/" + os.path.splitext(os.path.basename(f))[0]
            total += process(f, slug); n += 1
    elif g == "photos":
        for f in sorted(glob.glob(f"{SRC}/photos/d*.jpg") + glob.glob(f"{SRC}/photos/d0.png")):
            slug = "photos/" + os.path.splitext(os.path.basename(f))[0]
            total += process(f, slug); n += 1
    print(f"[{g}] {n} sources -> {total} files written")
    return total

if __name__ == "__main__":
    groups = sys.argv[1:] or ["editorial"]
    if "all" in groups:
        groups = ["editorial", "rooms", "gallery", "photos"]
    for g in groups:
        run_group(g)
    print("done ->", OUT)
