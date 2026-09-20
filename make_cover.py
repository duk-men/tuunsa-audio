# -*- coding: utf-8 -*-
"""팟캐스트 커버 아트 생성 (3000x3000 JPG). Apple 권장 규격."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs" / "cover.jpg"
S = 3000

BG_TOP = (28, 26, 25)
BG_BOT = (58, 40, 26)
ACCENT = (217, 160, 102)
WHITE = (244, 241, 237)
MUTED = (150, 142, 132)

BOLD = "C:/Windows/Fonts/malgunbd.ttf"
REG = "C:/Windows/Fonts/malgun.ttf"


def main() -> None:
    img = Image.new("RGB", (S, S), BG_TOP)
    d = ImageDraw.Draw(img)

    # 세로 그라데이션
    for y in range(S):
        t = y / S
        d.line([(0, y), (S, y)], fill=tuple(
            int(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOT)))

    # 상단 강조선
    d.rounded_rectangle([340, 700, 340 + 300, 700 + 26], 13, fill=ACCENT)

    f_title = ImageFont.truetype(BOLD, 440)
    f_sub = ImageFont.truetype(REG, 150)
    f_tag = ImageFont.truetype(BOLD, 132)

    d.text((330, 820), "투자자산", font=f_title, fill=WHITE)
    d.text((330, 1300), "운용사", font=f_title, fill=WHITE)
    d.text((330, 1830), "핵심정리", font=f_title, fill=ACCENT)

    d.text((340, 2400), "출퇴근길에 듣는 12강", font=f_sub, fill=MUTED)

    # 하단 태그
    tag = "AUDIO COURSE"
    tw = d.textlength(tag, font=f_tag)
    d.rounded_rectangle([336, 2620, 336 + tw + 120, 2620 + 210], 40,
                        outline=ACCENT, width=8)
    d.text((396, 2658), tag, font=f_tag, fill=ACCENT)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "JPEG", quality=88, optimize=True)
    print(f"{OUT} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
