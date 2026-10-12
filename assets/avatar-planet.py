"""Render a 32×32 retro planet avatar using only Python's standard library."""

from math import cos, sin, sqrt
from pathlib import Path
from struct import pack
from zlib import compress, crc32

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
pixels = {(x, y): colors["background"] for y in range(32) for x in range(32)}
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

assert len(set(pixels.values())) == len(COLORS)
assert all((x - 15.5) ** 2 + (y - 15.5) ** 2 <= 15.5 ** 2
           for y in range(32) for x in range(32)
           if pixels[x, y] != colors["background"]), "Artwork must fit the circular crop."

scanlines = []
for y in range(32):
    row = b"\0" + b"".join(bytes(pixels[x, y]) * 32 for x in range(32))
    scanlines.append(row * 32)
raw = b"".join(scanlines)
assert len(raw) == (1024 * 3 + 1) * 1024


def chunk(kind, data):
    payload = kind + data
    return pack(">I", len(data)) + payload + pack(">I", crc32(payload))


# PNG uses 8-bit RGB pixels, filter 0 on every row, and no interlace.
header = pack(">IIBBBBB", 1024, 1024, 8, 2, 0, 0, 0)
png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
       + chunk(b"IDAT", compress(raw)) + chunk(b"IEND", b""))
assert len(png) < 1_000_000
(OUT / "avatar-planet.png").write_bytes(png)
print("Rendered avatar-planet.png; all artwork fits the circular crop.")
