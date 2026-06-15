"""Create a simple screenshot-like PNG for README."""
from __future__ import annotations

from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:
    raise SystemExit("Install Pillow to generate the demo screenshot: pip install pillow") from exc

ROOT = Path(__file__).resolve().parents[1]

demo_text = (ROOT / "demo" / "cli_demo.txt").read_text(encoding="utf-8")
lines = demo_text.splitlines()

width = 1200
line_height = 27
height = max(520, 60 + line_height * len(lines))
image = Image.new("RGB", (width, height), (248, 249, 251))
draw = ImageDraw.Draw(image)
try:
    font = ImageFont.truetype("DejaVuSansMono.ttf", 20)
    title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
except Exception:
    font = ImageFont.load_default()
    title_font = ImageFont.load_default()

# Header
draw.rectangle((0, 0, width, 48), fill=(32, 38, 52))
draw.text((24, 12), "ADAS ScenarioGuard MVP demo", font=title_font, fill=(255, 255, 255))

# Terminal area
draw.rounded_rectangle((24, 72, width - 24, height - 24), radius=12, fill=(20, 24, 31))
y = 92
for line in lines:
    fill = (180, 255, 190) if line.startswith("$") else (235, 238, 245)
    if "CRITICAL" in line:
        fill = (255, 190, 160)
    draw.text((48, y), line, font=font, fill=fill)
    y += line_height

out = ROOT / "demo" / "cli_demo.png"
out.parent.mkdir(exist_ok=True)
image.save(out)
print(out)
