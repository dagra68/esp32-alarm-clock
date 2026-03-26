#!/usr/bin/env python3
"""
Generates needle images for ESP32 analog clock.
Needle points to the RIGHT (East = 3 o'clock), pivot at left edge center.
LVGL rotates the image so that at value=0 it points UP (12 o'clock).

Scale radius = 240px (half of 480px meter widget).
  Minute: scale_radius + r_mod(-4)  = 236px from center
  Hour:   scale_radius + r_mod(-50) = 190px from center
"""
from PIL import Image, ImageDraw

OUT = "needles"

# Minute hand: 236px long
M_LEN = 236
# Hour hand: 190px long
H_LEN = 190

def save(img, name):
    path = f"{OUT}/{name}.png"
    img.save(path)
    print(f"  {path}  ({img.width}x{img.height})")

# ── Pfeil (Arrow) ──────────────────────────────────────────────────
# Classic watch hand: thin rectangular shaft + wide triangular arrowhead
def make_pfeil(length, shaft_w, head_h, color):
    height = head_h + 2
    cy = height // 2
    head_start = int(length * 0.70)
    img = Image.new("RGBA", (length, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # shaft
    draw.rectangle([0, cy - shaft_w // 2, head_start, cy + shaft_w // 2], fill=color)
    # arrowhead triangle
    draw.polygon([
        (head_start, cy - head_h // 2),
        (head_start, cy + head_h // 2),
        (length - 1, cy),
    ], fill=color)
    return img, cy

img, cy = make_pfeil(M_LEN, shaft_w=6,  head_h=18, color=(30, 30, 30, 255))
save(img, "minute_pfeil")
print(f"    pivot: (0, {cy})")

img, cy = make_pfeil(H_LEN, shaft_w=10, head_h=26, color=(30, 30, 30, 255))
save(img, "hour_pfeil")
print(f"    pivot: (0, {cy})")

# ── Raute (Diamond) ────────────────────────────────────────────────
# Elongated rhombus: thin at both ends, widest at center
def make_raute(length, max_h, color):
    height = max_h + 2
    cy = height // 2
    mid = length // 2
    img = Image.new("RGBA", (length, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.polygon([
        (1,          cy),           # left tip  (pivot end)
        (mid,        1),            # top
        (length - 1, cy),           # right tip
        (mid,        height - 1),   # bottom
    ], fill=color)
    return img, cy

img, cy = make_raute(M_LEN, max_h=18, color=(15, 15, 80, 255))
save(img, "minute_raute")
print(f"    pivot: (0, {cy})")

img, cy = make_raute(H_LEN, max_h=26, color=(15, 15, 80, 255))
save(img, "hour_raute")
print(f"    pivot: (0, {cy})")

# ── Dreieck (Triangle) ─────────────────────────────────────────────
# Isoceles triangle: full width at pivot base, tapers to sharp point
def make_dreieck(length, base_h, color):
    height = base_h + 2
    cy = height // 2
    img = Image.new("RGBA", (length, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.polygon([
        (1,          1),
        (1,          height - 2),
        (length - 1, cy),
    ], fill=color)
    return img, cy

img, cy = make_dreieck(M_LEN, base_h=20, color=(160, 30, 30, 255))
save(img, "minute_dreieck")
print(f"    pivot: (0, {cy})")

img, cy = make_dreieck(H_LEN, base_h=28, color=(160, 30, 30, 255))
save(img, "hour_dreieck")
print(f"    pivot: (0, {cy})")

print("\nDone.")
