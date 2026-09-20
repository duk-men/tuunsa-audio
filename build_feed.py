# -*- coding: utf-8 -*-
"""
docs/audio/ep*.mp3 -> docs/feed.xml (Apple 팟캐스트용 RSS) + docs/index.html

usage:
  python build_feed.py --base-url https://<사용자>.github.io/<저장소>
"""
import argparse
import datetime as dt
import html
from pathlib import Path
from xml.sax.saxutils import escape

from mutagen.mp3 import MP3

ROOT = Path(__file__).resolve().parent
AUDIO = ROOT / "docs" / "audio"

SHOW = {
    "title": "투자자산운용사 핵심정리",
    "subtitle": "출퇴근길에 듣는 투운사 12강",
    "author": "본인 학습용",
    "summary": (
        "투자자산운용사 시험 대비 요약 노트를 강의형 팟캐스트로 재구성한 개인 학습용 오디오입니다. "
        "금융투자세제부터 분산투자기법까지 12편으로 구성되어 있습니다."
    ),
    "lang": "ko",
    "category": "Education",
}

# (번호, 제목, 한 줄 설명)
EPISODES = [
    ("01", "금융투자세제와 절세전략",
     "조세의 분류, 납세의무의 성립·확정·소멸, 이자·배당소득, 그로스업, 양도소득세, 증권거래세, 증여·상속 절세전략."),
    ("02", "금융상품",
     "금융회사와 금융상품 구분, ISA, 예금과 신탁, ELS·ELD·ELF, 예금자보호, 보험 구조, 펀드와 MMF, 랩어카운트, ABS."),
    ("03", "부동산 관련 상품",
     "부동산의 특성과 권리관계, 현금흐름 분석, 타당성 분석, 용도지역·지구·구역, 가치평가 3방식, 부동산펀드와 리츠."),
    ("04", "직무윤리",
     "고객우선·신의성실 2대 원칙, 과당매매, 금융소비자보호 6대 판매원칙, 청약철회권, 내부통제와 과태료."),
    ("05", "자본시장법",
     "금융투자업 인가와 등록, 건전성 규제, 집합투자재산 운용 제한, 증권신고서와 공시, 불공정거래 규제."),
    ("06", "협회 규정",
     "핵심설명서, 조사분석자료, 투자광고 위험표시 기준, 재산상 이익, 배타적 사용권, 약관 보고 기한."),
    ("07", "주식투자운용과 투자전략",
     "효율적 시장가설, 자산집단, 전략적·전술적·보험 자산배분, CPPI와 OBPI, 인덱스 운용, 이상현상."),
    ("08", "채권",
     "채권의 분류, 전환사채 가격지표, 말킬의 정리, 듀레이션과 볼록성, 수익률 곡선과 기간구조, 투자전략."),
    ("09", "파생상품 투자운용",
     "증거금과 일일정산, 헤지비율 산정, 스프레드와 콤비네이션, 풋콜 패리티, 이항모형, 옵션 민감도."),
    ("10", "투자운용 결과분석",
     "금액가중·시간가중 수익률, 절대적·상대적 위험, 기준지표, 샤프·트레이너·정보·소티노 비율, 성과요인분석."),
    ("11", "거시경제",
     "IS-LM 모형, 구축효과, 유동성 함정, 통화정책 중간목표, 이자율 결정이론, 경기종합지수와 물가지수."),
    ("12", "분산투자기법",
     "포트폴리오 기대수익과 위험, 최소분산 포트폴리오, CAPM, 자본시장선과 증권시장선, 단일지표 모형, APT."),
]

# 1편을 이 날짜로 두고 하루씩 뒤로 배치한다 (팟캐스트 앱에서 1편부터 정렬되도록).
START = dt.datetime(2026, 9, 1, 7, 0, 0)


def rfc2822(d: dt.datetime) -> str:
    return d.strftime("%a, %d %b %Y %H:%M:%S +0900")


def hhmmss(seconds: float) -> str:
    s = int(round(seconds))
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def build(base_url: str) -> None:
    base = base_url.rstrip("/")
    items, rows, total = [], [], 0.0

    for i, (num, title, desc) in enumerate(EPISODES):
        mp3 = AUDIO / f"ep{num}.mp3"
        if not mp3.exists():
            print(f"  ! ep{num}.mp3 없음 - 건너뜀")
            continue
        size = mp3.stat().st_size
        dur = MP3(mp3).info.length
        total += dur
        pub = START + dt.timedelta(days=i)
        full = f"{num}. {title}"

        items.append(f"""    <item>
      <title>{escape(full)}</title>
      <itunes:title>{escape(title)}</itunes:title>
      <itunes:episode>{int(num)}</itunes:episode>
      <itunes:episodeType>full</itunes:episodeType>
      <description>{escape(desc)}</description>
      <itunes:summary>{escape(desc)}</itunes:summary>
      <enclosure url="{base}/audio/ep{num}.mp3" length="{size}" type="audio/mpeg"/>
      <guid isPermaLink="false">tuunsa-ep{num}</guid>
      <pubDate>{rfc2822(pub)}</pubDate>
      <itunes:duration>{hhmmss(dur)}</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
    </item>""")

        rows.append(f"""      <li>
        <div class="ep"><span class="num">{num}</span>
          <div><strong>{html.escape(title)}</strong>
            <p>{html.escape(desc)}</p>
            <audio controls preload="none" src="audio/ep{num}.mp3"></audio>
            <span class="dur">{hhmmss(dur)}</span>
          </div>
        </div>
      </li>""")

    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
     xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>{escape(SHOW['title'])}</title>
    <link>{base}/</link>
    <language>{SHOW['lang']}</language>
    <description>{escape(SHOW['summary'])}</description>
    <itunes:author>{escape(SHOW['author'])}</itunes:author>
    <itunes:subtitle>{escape(SHOW['subtitle'])}</itunes:subtitle>
    <itunes:summary>{escape(SHOW['summary'])}</itunes:summary>
    <itunes:type>serial</itunes:type>
    <itunes:explicit>false</itunes:explicit>
    <itunes:image href="{base}/cover.jpg"/>
    <itunes:category text="{SHOW['category']}"/>
    <itunes:owner>
      <itunes:name>{escape(SHOW['author'])}</itunes:name>
    </itunes:owner>
    <lastBuildDate>{rfc2822(dt.datetime.now())}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
"""
    (ROOT / "docs" / "feed.xml").write_text(feed, encoding="utf-8")

    page = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{html.escape(SHOW['title'])}</title>
<style>
  :root {{ color-scheme: light dark; --bg:#fbfaf8; --fg:#1b1a19; --mut:#6b6764; --card:#fff; --line:#e7e3de; --acc:#8a5a2b; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#191817; --fg:#ececea; --mut:#a39f9b; --card:#232120; --line:#35322f; --acc:#d9a066; }}
  }}
  * {{ box-sizing:border-box }}
  body {{ margin:0; background:var(--bg); color:var(--fg); font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans KR",sans-serif; }}
  .wrap {{ max-width:720px; margin:0 auto; padding:32px 20px 64px; }}
  h1 {{ font-size:1.6rem; margin:0 0 4px; letter-spacing:-.02em }}
  .sub {{ color:var(--mut); margin:0 0 28px }}
  .box {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:18px 20px; margin-bottom:28px }}
  .box h2 {{ font-size:.95rem; margin:0 0 10px; text-transform:uppercase; letter-spacing:.08em; color:var(--mut) }}
  ol.steps {{ margin:0; padding-left:1.2em }} ol.steps li {{ margin:6px 0 }}
  code {{ background:rgba(138,90,43,.12); color:var(--acc); padding:2px 6px; border-radius:5px;
          font:13px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace; word-break:break-all }}
  ul.list {{ list-style:none; margin:0; padding:0 }}
  ul.list li {{ border-top:1px solid var(--line); padding:16px 0 }}
  ul.list li:first-child {{ border-top:0 }}
  .ep {{ display:flex; gap:14px; align-items:flex-start }}
  .num {{ flex:0 0 34px; height:34px; border-radius:9px; background:var(--acc); color:#fff;
          display:grid; place-items:center; font-weight:700; font-size:.85rem }}
  .ep p {{ margin:3px 0 10px; color:var(--mut); font-size:.9rem }}
  audio {{ width:100%; max-width:100%; height:36px }}
  .dur {{ display:inline-block; margin-top:6px; font-size:.8rem; color:var(--mut); font-variant-numeric:tabular-nums }}
  footer {{ margin-top:36px; color:var(--mut); font-size:.85rem }}
</style></head><body><div class="wrap">
  <h1>{html.escape(SHOW['title'])}</h1>
  <p class="sub">{html.escape(SHOW['subtitle'])} · 총 {len(items)}편 · {hhmmss(total)}</p>

  <div class="box">
    <h2>아이폰에서 듣기</h2>
    <ol class="steps">
      <li>아이폰 <strong>팟캐스트</strong> 앱 → <strong>보관함</strong> 탭</li>
      <li>오른쪽 위 <strong>…</strong> → <strong>URL로 팟캐스트 추가</strong></li>
      <li>아래 주소를 붙여넣기<br><code>{base}/feed.xml</code></li>
    </ol>
    <p style="margin:10px 0 0;color:var(--mut);font-size:.88rem">
      백그라운드 재생 · 잠금화면 컨트롤 · 이어듣기 · 배속 · 오프라인 다운로드가 모두 앱 기본 기능으로 동작합니다.</p>
  </div>

  <ul class="list">
{chr(10).join(rows)}
  </ul>
  <footer>개인 학습용으로 제작된 오디오입니다.</footer>
</div></body></html>
"""
    (ROOT / "docs" / "index.html").write_text(page, encoding="utf-8")
    print(f"feed.xml / index.html 생성 완료 · {len(items)}편 · 총 {hhmmss(total)}")
    print(f"피드 주소: {base}/feed.xml")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    build(ap.parse_args().base_url)
