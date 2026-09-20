# -*- coding: utf-8 -*-
"""
scripts/*.txt -> docs/audio/*.mp3 (edge-tts)

usage:
  python tts.py            # 아직 mp3가 없는 것만 생성
  python tts.py --force    # 전부 다시 생성
  python tts.py 01 03      # 지정한 번호만 생성
  python tts.py --voice ko-KR-InJoonNeural
"""
import argparse
import asyncio
import re
import sys
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "scripts"
OUT = ROOT / "docs" / "audio"

VOICE = "ko-KR-InJoonNeural"  # 남성. 여성은 ko-KR-SunHiNeural
RATE = "+20%"                 # 낭독 속도
VOLUME = "+0%"
PITCH = "+0Hz"


def clean(text: str) -> str:
    """TTS가 어색하게 읽는 기호를 제거/치환한다."""
    text = text.replace("★", "").replace("→", " ").replace("※", "")
    text = text.replace("%", "퍼센트")
    text = re.sub(r"[ \t]+", " ", text)
    # 빈 줄은 문장 사이 호흡으로 남기되 3줄 이상은 2줄로 축소
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


async def synth(src: Path, dst: Path, voice: str) -> None:
    text = clean(src.read_text(encoding="utf-8"))
    comm = edge_tts.Communicate(text, voice, rate=RATE, volume=VOLUME, pitch=PITCH)
    tmp = dst.with_suffix(".part")
    await comm.save(str(tmp))
    tmp.replace(dst)
    kb = dst.stat().st_size / 1024
    print(f"  OK  {dst.name}  ({kb:,.0f} KB, 원고 {len(text):,}자)")


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("only", nargs="*", help="생성할 편 번호 (예: 01 03)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--voice", default=VOICE)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    targets = sorted(SRC.glob("*.txt"))
    if args.only:
        targets = [p for p in targets if p.name[:2] in args.only]
    if not targets:
        print("생성할 대본이 없습니다.")
        return 1

    for src in targets:
        dst = OUT / ("ep" + src.name[:2] + ".mp3")
        if dst.exists() and not args.force:
            print(f"  skip {dst.name} (이미 있음)")
            continue
        print(f"[TTS] {src.name}")
        for attempt in range(1, 4):
            try:
                await synth(src, dst, args.voice)
                break
            except Exception as e:  # 네트워크 일시 오류 재시도
                print(f"  실패 {attempt}/3: {e}")
                if attempt == 3:
                    return 1
                await asyncio.sleep(3)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
