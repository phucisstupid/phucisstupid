"""Render a 32×32 retro planet avatar with Python and Pillow."""

from math import cos, sin, sqrt
from pathlib import Path
from PIL import Image

OUT = Path(__file__).resolve().parent
COLORS = {
    "background": "#222937",
    "back_ring": "#666f86",
    "ring_shadow": "#87949b",
    "cream": "#ead8b0",
    "light": "#e5b57e",
    "planet": "#c78365",
    "shadow": "#955449",
}
colors = {name: tuple(bytes.fromhex(value[1:])) for name, value in COLORS.items()}
image = Image.new("RGB", (32, 32), colors["background"])
pixels = image.load()
angle = -0.42

# Draw the back ring, the sphere, then the front ring on the same pixel grid.
for y in range(32):
    for x in range(32):
        dx, dy = x - 15.5, y - 15.5
        u = cos(angle) * dx + sin(angle) * dy
        v = -sin(angle) * dx + cos(angle) * dy
        ring = (u / 12.7) ** 2 + (v / 4.1) ** 2 <= 1 and (u / 10.2) ** 2 + (v / 2.0) ** 2 >= 1
        if ring:
            pixels[x, y] = colors["back_ring"]
        distance = (dx * dx + dy * dy) / 64
        if distance <= 1:
            light = -0.6 * dx / 8 - 0.7 * dy / 8 + 0.4 * sqrt(1 - distance)
            pixels[x, y] = colors["light" if light > 0.45 else "planet" if light > -0.2 else "shadow"]
        if ring and v > 0:
            pixels[x, y] = colors["cream" if v < 3.4 else "ring_shadow"]

for x, y in [(7, 5), (6, 6), (7, 6), (8, 6), (7, 7), (25, 24)]:
    pixels[x, y] = colors["cream"]

assert len(image.getcolors()) == len(COLORS)
assert all((x - 15.5) ** 2 + (y - 15.5) ** 2 <= 15.5 ** 2
           for y in range(32) for x in range(32)
           if pixels[x, y] != colors["background"]), "Artwork must fit the circular crop."

target = OUT / "avatar-planet.png"
image.resize((1024, 1024), Image.Resampling.NEAREST).save(target)
with Image.open(target) as rendered:
    assert rendered.size == (1024, 1024) and rendered.format == "PNG"
assert target.stat().st_size < 1_000_000
print("Rendered avatar-planet.png; all artwork fits the circular crop.")
