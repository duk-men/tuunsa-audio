# 투자자산운용사 핵심정리 (오디오)

투운사 요약 노트 12개를 강의형 팟캐스트 대본으로 재구성하고, TTS로 mp3를 만들어
GitHub Pages에 비공개 RSS 피드로 올려 **Apple 팟캐스트 앱에서 듣는** 개인 학습용 프로젝트.

팟캐스트 앱으로 들으면 백그라운드 재생 · 잠금화면 컨트롤 · **이어듣기** · 배속 ·
에어팟 조작 · 오프라인 다운로드가 전부 앱 기본 기능으로 동작한다.

## 구성

```
scripts/            대본 12편 (사람이 읽고 고치는 원본)
docs/               GitHub Pages로 서빙되는 폴더
  audio/ep01..12.mp3  생성된 오디오
  feed.xml            팟캐스트 RSS
  index.html          웹 플레이어 + 구독 안내
  cover.jpg           커버 아트 3000x3000
tts.py              대본 -> mp3
build_feed.py       mp3 -> feed.xml + index.html
make_cover.py       커버 아트 생성
```

## 사용법

필요한 패키지:

```bash
pip install edge-tts mutagen pillow
```

### 1. 대본 수정

`scripts/*.txt`를 직접 고친다. TTS가 그대로 읽으므로 기호(`★`, `→`, 표)는 쓰지 말고
숫자도 읽는 대로 쓴다 (`14%` 대신 `14퍼센트`).

### 2. 오디오 생성

```bash
python tts.py              # mp3가 없는 편만 생성
python tts.py 05 08        # 5편, 8편만 다시 생성
python tts.py --force      # 전부 다시 생성
python tts.py --voice ko-KR-SunHiNeural   # 여성 목소리로
```

목소리와 속도는 `tts.py` 상단 `VOICE` / `RATE`에서 바꾼다.
현재 설정: `ko-KR-InJoonNeural` (남성), `+20%`.

사용 가능한 한국어 목소리:

| 음성 | 성별 |
|---|---|
| `ko-KR-InJoonNeural` | 남 |
| `ko-KR-SunHiNeural` | 여 |
| `ko-KR-HyunsuMultilingualNeural` | 남 |

### 3. 피드 재생성 후 배포

```bash
python build_feed.py --base-url https://<사용자명>.github.io/<저장소명>
git add -A && git commit -m "update" && git push
```

푸시하면 1~2분 뒤 GitHub Pages에 반영된다.

### 4. 아이폰에서 구독

팟캐스트 앱 → 보관함 → 오른쪽 위 `…` → **URL로 팟캐스트 추가** →
`https://<사용자명>.github.io/<저장소명>/feed.xml`

## 주의

- 저장소가 public이면 주소를 아는 사람은 접근할 수 있다. 주소를 공유하지 않는 방식의
  비공개(unlisted)다. 완전한 비공개가 필요하면 별도 인증이 있는 호스팅이 필요하다.
- 대본은 개인 요약 노트를 옮긴 것이므로 법령·세율 등은 시험 시점 기준으로 반드시 재확인할 것.
