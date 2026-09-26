"""직접 녹음한 파일이 없을 때 써 볼 수 있는 데모 오디오를 만든다.

    python examples/make_demo.py
    python -m music2score examples/school_bell.wav
    python -m music2score examples/school_bell_piano.wav --mode poly
"""

from pathlib import Path

import soundfile as sf

from music2score.synth import SCHOOL_BELL, SCHOOL_BELL_CHORDS, synthesize, synthesize_piano

SR = 22050
HERE = Path(__file__).parent

files = {
    # 사람 목소리처럼 비브라토와 약간의 잡음이 섞인 멜로디
    "school_bell.wav": synthesize(SCHOOL_BELL, 100, SR, vibrato=0.25, noise=0.01),
    # 오른손 멜로디 + 왼손 화음 피아노
    "school_bell_piano.wav": synthesize_piano(SCHOOL_BELL, SCHOOL_BELL_CHORDS, 100, SR),
}
for name, audio in files.items():
    sf.write(HERE / name, audio, SR)
    print(f"만들었습니다: {HERE / name}")
