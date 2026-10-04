# -*- coding: utf-8 -*-
"""
scripts/*.txt -> docs/audio/epNN.mp3 (edge-tts)

대본에 [[PAUSE:3]] 을 단독 줄로 넣으면 그 자리에 3초 무음이 들어간다.
(퀴즈에서 스스로 답을 떠올릴 시간을 주기 위한 것)

usage:
  python tts.py            # 아직 mp3가 없는 것만 생성
  python tts.py --force    # 전부 다시 생성
  python tts.py 01 03      # 지정한 번호만 생성
  python tts.py --voice ko-KR-SunHiNeural
"""
import argparse
import asyncio
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "scripts"
OUT = ROOT / "docs" / "audio"

VOICE = "ko-KR-InJoonNeural"  # 남성. 여성은 ko-KR-SunHiNeural
RATE = "+20%"                 # 낭독 속도
VOLUME = "+0%"
PITCH = "+0Hz"

PAUSE_RE = re.compile(r"\[\[PAUSE:(\d+(?:\.\d+)?)\]\]")

# edge-tts 출력 포맷과 맞춰야 무손실로 이어붙일 수 있다.
SR, BR = 24000, "48k"

FFMPEG = ""


def find_ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    base = Path.home() / "AppData/Local/Microsoft/WinGet/Packages"
    for p in base.glob("Gyan.FFmpeg*/**/bin/ffmpeg.exe"):
        return str(p)
    raise SystemExit("ffmpeg을 찾을 수 없습니다. winget install Gyan.FFmpeg")


def clean(text: str) -> str:
    """TTS가 어색하게 읽는 기호를 제거/치환한다. PAUSE 마커는 보존한다."""
    text = text.replace("★", "").replace("→", " ").replace("※", "")
    text = text.replace("%", "퍼센트")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def silence(seconds: float, path: Path) -> None:
    subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error",
         "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono",
         "-t", str(seconds), "-c:a", "libmp3lame", "-b:a", BR, str(path)],
        check=True)


def concat(parts: list, dst: Path, work: Path) -> None:
    listing = work / "list.txt"
    listing.write_text(
        "".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(listing), "-c", "copy", "-f", "mp3", str(dst)], check=True)


async def say(text: str, dst: Path, voice: str) -> None:
    comm = edge_tts.Communicate(text, voice, rate=RATE, volume=VOLUME, pitch=PITCH)
    await comm.save(str(dst))


async def synth(src: Path, dst: Path, voice: str) -> None:
    text = clean(src.read_text(encoding="utf-8"))
    chunks = PAUSE_RE.split(text)   # [본문, 초, 본문, 초, ...]
    tmp = dst.with_suffix(".part")

    if len(chunks) == 1:
        await say(text, tmp, voice)
        pauses = 0
    else:
        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            parts, pauses = [], 0
            for i, chunk in enumerate(chunks):
                part = work / f"{i:04d}.mp3"
                if i % 2 == 0:                      # 본문
                    body = chunk.strip()
                    if not body:
                        continue
                    await say(body, part, voice)
                else:                               # 무음
                    silence(float(chunk), part)
                    pauses += 1
                parts.append(part)
            concat(parts, tmp, work)

    tmp.replace(dst)
    kb = dst.stat().st_size / 1024
    print(f"  OK  {dst.name}  ({kb:,.0f} KB, 원고 {len(text):,}자, 무음 {pauses}곳)")


async def main() -> int:
    global FFMPEG
    ap = argparse.ArgumentParser()
    ap.add_argument("only", nargs="*", help="생성할 편 번호 (예: 01 03)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--voice", default=VOICE)
    args = ap.parse_args()

    FFMPEG = find_ffmpeg()
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
