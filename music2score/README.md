# music2score 🎼

음악을 **듣고 악보를 만드는** 프로그램입니다.
오디오 파일(또는 마이크 녹음)을 넣으면 음높이·박자·템포·조성을 분석해서
**MusicXML**(MuseScore 등 악보 프로그램용), **MIDI**, 브라우저에서 바로 보는 **HTML 악보**를 만듭니다.

![학교종이 땡땡땡 인식 결과](docs/school_bell.png)

> 위 악보는 비브라토와 잡음을 섞어 합성한 "학교종이 땡땡땡" 오디오를 넣어서 나온 결과 그대로입니다.
> 템포(♩=100), 조성(다장조), 음 24개의 높이와 길이가 모두 원곡과 일치합니다.

<br>

## 설치

Python 3.10 이상이 필요합니다.

```bash
cd music2score
pip install -e .                 # 기본 (노래·멜로디 인식)
pip install -e ".[poly]"         # + 피아노처럼 화음이 있는 연주 인식 (TensorFlow 포함, 큼)
pip install -e ".[mic]"          # + 마이크 녹음
```

<br>

## 사용법

```bash
# 오디오 파일 → 악보
music2score 노래.wav
music2score 허밍.mp3 --title "내가 만든 노래"

# 마이크로 10초 녹음해서 바로 악보로
music2score --record 10

# 피아노 연주 (오른손/왼손 큰보표로)
music2score 피아노.mp3 --mode poly

# 템포·박자를 알고 있으면 알려 주면 더 정확합니다
music2score 왈츠.wav --bpm 90 --time 3/4
```

설치 없이 폴더 안에서 `python -m music2score 노래.wav` 로 실행해도 됩니다.
wav · mp3 · flac · ogg 는 바로 읽고, m4a · aac 같은 형식은 [ffmpeg](https://ffmpeg.org) 가 설치돼 있어야 읽힙니다.
리눅스에서 마이크 녹음을 쓰려면 PortAudio 도 필요합니다 (`sudo apt install libportaudio2`).

직접 녹음한 파일이 없다면 데모 오디오로 먼저 써 보세요.

```bash
python examples/make_demo.py                              # examples/ 에 wav 두 개 생성
music2score examples/school_bell.wav
music2score examples/school_bell_piano.wav --mode poly
```

실행하면 이렇게 나옵니다.

```
♪ 분석 중: examples/school_bell.wav
  템포  : ♩ = 100
  조성  : C 장조
  음 개수: 24  (G4 G4 A4 A4 G4 G4 E4 G4 G4 E4 E4 D4 G4 G4 A4 A4 …)
  결과  :
    musicxml output/school_bell.musicxml
    midi     output/school_bell.mid
    html     output/school_bell.html
```

### 옵션

| 옵션 | 설명 | 기본값 |
|---|---|---|
| `--mode mono` | 노래, 허밍, 휘파람, 리코더·바이올린 같은 **멜로디 한 줄** | ✔ |
| `--mode poly` | 피아노·기타처럼 **여러 음이 동시에** 울리는 연주 (basic-pitch 필요) | |
| `--record SEC` | 파일 대신 마이크로 SEC 초 녹음 (sounddevice 필요) | |
| `--bpm` | 템포 직접 지정 | 자동 추정 |
| `--time` | 박자표 (`4/4`, `3/4`, `6/8` …) | `4/4` |
| `--grid` | 가장 짧은 음표 (`8` = 8분음표, `16` = 16분음표) | `16` |
| `--min-note` | 이보다 짧은 음(초)은 잡음으로 보고 버림 | mono 0.06 / poly 0.12 |
| `--title` | 악보 제목 | 파일 이름 |
| `-o`, `--out` | 결과 폴더 | `output` |
| `--pdf` | PDF 도 생성 (MuseScore 설치 필요) | |

### 결과 파일

| 파일 | 쓰는 곳 |
|---|---|
| `*.musicxml` | [MuseScore](https://musescore.org)(무료), Finale, Sibelius, Dorico 에서 열어 **수정·인쇄** |
| `*.mid` | DAW, GarageBand, 피아노 앱 등에서 재생 |
| `*.html` | 더블클릭해서 브라우저로 바로 보기 ([OpenSheetMusicDisplay](https://opensheetmusicdisplay.org)) |

자동 인식 결과는 초안입니다. MusicXML 을 MuseScore 에서 열어 틀린 음만 고치면 완성본을 빠르게 만들 수 있습니다.

<br>

## 동작 원리

```
오디오 ─▶ ① 음 검출 ─▶ ② 템포 추정 ─▶ ③ 박자 양자화 ─▶ ④ 조성 추정 ─▶ ⑤ 악보 만들기
          (초 단위)                     (4분음표 단위)
```

**① 음 검출** — 소리에서 "몇 초부터 몇 초까지 어떤 음"인지 찾습니다.
- `mono` ([mono.py](music2score/mono.py)): **pYIN** 알고리즘으로 11.6ms 마다 기본 주파수(f0)를 구하고,
  - 음높이가 0.75 반음 이상 바뀐 상태가 이어지면 → 새 음
  - 같은 음높이라도 음량이 다시 치솟는 어택(onset)이 있으면 → 같은 음을 다시 부른 것 (솔-솔-라-라 구분)
  - 한두 프레임 인식이 끊긴 것은 다시 이어 붙이고, 잡음 바닥보다 작은 소리는 무시합니다.
- `poly` ([poly.py](music2score/poly.py)): Spotify 의 신경망 모델 **basic-pitch** 로 여러 음을 동시에 찾고,
  배음(옥타브 위에 약하게 따라 울리는 소리)이 따로 잡힌 가짜 음을 걸러 냅니다.

**② 템포 추정** ([rhythm.py](music2score/rhythm.py)) — 음이 시작되는 시각들이 반복되는 주기로 BPM 을 구한 뒤,
±6% 범위에서 음 시작점들이 박자 격자에 가장 잘 맞는 BPM 과 첫 박 위치를 다시 찾습니다.
(템포가 1%만 틀려도 곡 뒤쪽에서 박이 밀리기 때문입니다.)

**③ 박자 양자화** — 초 단위 시간을 16분음표 격자에 맞춥니다.
사람은 음을 악보 길이보다 조금 일찍 끊는 경우가 많아서, 그대로 옮기면 악보가 쉼표투성이가 됩니다.
그래서 곡 전체에서 **연주자가 음을 얼마나 끊어 부르는지**를 재고, 그 습관만큼의 틈은 앞 음에 붙이고
그보다 긴 틈만 쉼표로 적습니다. (끊어 부르는 사람의 "온음표"와 레가토로 부른 "점2분음표+4분쉼표"를 구분할 수 있습니다.)

**④ 조성 추정** ([score.py](music2score/score.py)) — 음 길이로 가중한 음 분포를 조성별 프로필과 비교(Krumhansl-Schmuckler)해서
조표를 정하고, 조성에 맞게 음 이름을 적습니다. (바장조면 A♯ 대신 B♭, 라단조면 D♭ 대신 C♯)

**⑤ 악보 만들기** — [music21](https://web.mit.edu/music21/) 로 마디·붙임줄·쉼표를 정리하고 MusicXML/MIDI 로 저장합니다.
`poly` 는 가온 도(C4)를 기준으로 오른손/왼손 큰보표로 나눕니다.

<br>

## 잘 되는 것과 한계

| 입력 | 결과 |
|---|---|
| 노래·허밍·휘파람·단선율 악기 독주 | 👍 잘 됩니다. 비브라토·약한 잡음·레가토/스타카토 모두 테스트로 확인 |
| 피아노 독주 | 🙂 멜로디와 화음 구성음은 잘 잡지만, 음 길이가 들쭉날쭉한 **초안** 수준 (아래 그림) |
| 반주·드럼이 섞인 일반 음원 (가요, 팝) | 😢 여러 악기가 섞여 있어 그대로는 어렵습니다. [Demucs](https://github.com/facebookresearch/demucs) 같은 음원 분리 도구로 **보컬만 뽑은 뒤** `mono` 로 넣으면 멜로디 악보를 얻을 수 있습니다. |

![피아노 인식 결과](docs/school_bell_piano.png)

> 피아노 모드 결과. 오른손 멜로디는 정확하고 왼손 화음(도-미-솔, 솔-시-레)도 맞지만,
> 피아노 소리는 치고 나면 점점 작아지기 때문에 모델이 음 길이를 짧게/여러 번 잡아서 붙임줄이 지저분합니다.

그 밖의 한계
- 셋잇단음표는 지원하지 않습니다 (가장 가까운 16분음표 격자로 맞춤).
- 첫 음을 항상 첫 마디 첫 박으로 둡니다. 못갖춘마디(여린내기)로 시작하는 곡은 마디선이 밀릴 수 있습니다.
- 템포가 크게 변하는 곡(리타르단도, 루바토)은 뒤쪽 박자가 어긋날 수 있습니다. `--bpm` 을 지정하면 도움이 됩니다.
- 템포는 60~180 사이로 추정합니다. 실제로는 200 인 곡이 100 으로 잡히면 음표 길이가 절반이 될 뿐 악보는 맞습니다.

<br>

## 테스트

```bash
pip install -e ".[dev,poly]"
pytest
```

정답을 아는 멜로디를 [synth.py](music2score/synth.py) 로 직접 합성해서 넣고, **음높이·시작 박·길이가 정답과 완전히 같은지** 확인합니다.
(학교종 / 바장조 8분·16분·점음표 멜로디 × 잡음·비브라토·빠른 템포·레가토·스타카토, 3/4 박자, 피아노 화음 등 21개)

<br>

## 폴더 구조

```
music2score/
├── music2score/
│   ├── __main__.py     # 명령줄 (music2score 명령)
│   ├── transcriber.py  # 전체 파이프라인 transcribe()
│   ├── audio.py        # 오디오 읽기, 마이크 녹음
│   ├── mono.py         # ① 단선율 음 검출 (pYIN)
│   ├── poly.py         # ① 다성 음 검출 (basic-pitch)
│   ├── rhythm.py       # ② 템포 추정, ③ 박자 양자화
│   ├── score.py        # ④ 조성, ⑤ 악보 생성·내보내기
│   ├── synth.py        # 테스트/데모용 신시사이저
│   └── notes.py        # 자료형
├── examples/make_demo.py
└── tests/
```

파이썬 코드에서 직접 쓸 수도 있습니다.

```python
from pathlib import Path
from music2score import transcribe
from music2score.score import export

result = transcribe("노래.wav", mode="mono")
print(result.bpm, result.key)          # 예: 100.0 C major
export(result.score, Path("output"), "노래")
```
