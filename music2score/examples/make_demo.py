"""직접 녹음한 파일이 없을 때 써 볼 수 있는 데모 오디오를 만든다.

    python examples/make_demo.py
    python -m music2score examples/school_bell.wav
    python -m music2score examples/school_bell_piano.wav --mode poly
    python -m music2score examples/guitar_riff.wav --tab guitar
    python -m music2score examples/guitar_chords.wav --mode poly --tab guitar --bpm 90
    python -m music2score examples/guitar_lick.wav --tab guitar      # 해머링·풀링·슬라이드·벤딩
    python -m music2score examples/bass_lick.wav --tab bass
"""

from pathlib import Path

import soundfile as sf

from music2score.synth import (
    SCHOOL_BELL,
    SCHOOL_BELL_CHORDS,
    synthesize,
    synthesize_chords,
    synthesize_lick,
    synthesize_piano,
)

SR = 22050
HERE = Path(__file__).parent

files = {
    # 사람 목소리처럼 비브라토와 약간의 잡음이 섞인 멜로디
    "school_bell.wav": synthesize(SCHOOL_BELL, 100, SR, vibrato=0.25, noise=0.01),
    # 오른손 멜로디 + 왼손 화음 피아노
    "school_bell_piano.wav": synthesize_piano(SCHOOL_BELL, SCHOOL_BELL_CHORDS, 100, SR),
    # 기타 한 줄 리프 (E 단조 펜타토닉)
    "guitar_riff.wav": synthesize(
        [("E3", 0.5), ("G3", 0.5), ("A3", 1), ("B3", 0.5), ("D4", 0.5), ("E4", 1),
         ("D4", 0.5), ("B3", 0.5), ("A3", 1), ("G3", 1), ("E3", 2)],
        96, SR, legato=1.0, timbre="guitar",
    ),
    # 기타 스트로크 C - G - Am - F
    "guitar_chords.wav": synthesize_chords(
        [(["C3", "E3", "G3", "C4", "E4"], 4), (["G2", "B2", "D3", "G3", "B3", "G4"], 4),
         (["A2", "E3", "A3", "C4", "E4"], 4), (["F2", "C3", "F3", "A3", "C4", "F4"], 4)],
        90, SR,
    ),
    # 주법이 들어간 기타 릭: 해머링, 풀링, 슬라이드, 벤딩, 벤딩+릴리즈, 슬라이드 아웃
    "guitar_lick.wav": synthesize_lick(
        [("A3", 1, ""), ("C4", 0.5, ""), ("D4", 0.5, "h"), ("E4", 0.5, ""), ("D4", 0.5, "p"),
         ("C4", 1, ""), ("E4", 1, "/"), ("A4", 2, "b2"), ("G4", 2, "b2r"), ("E4", 2, ">")],
        90, SR,
    ),
    # 베이스 라인: 개방현 해머링·풀링, 슬라이드, 슬라이드 아웃
    "bass_lick.wav": synthesize_lick(
        [("E2", 1, ""), ("G2", 0.5, ""), ("A2", 0.5, "h"), ("B2", 1, ""), ("A2", 0.5, ""),
         ("G2", 0.5, "p"), ("E2", 1, ""), ("A2", 1, "/"), ("E2", 2, ">")],
        100, SR,
    ),
}
for name, audio in files.items():
    sf.write(HERE / name, audio, SR)
    print(f"만들었습니다: {HERE / name}")
