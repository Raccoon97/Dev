"""오디오 파일 읽기와 마이크 녹음."""

from __future__ import annotations

import time
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

SAMPLE_RATE = 22050


def load_audio(path: str | Path, sr: int = SAMPLE_RATE) -> tuple[np.ndarray, int]:
    """오디오를 모노로 읽고 최대 진폭이 1 이 되도록 정규화한다."""
    y, sr = librosa.load(str(path), sr=sr, mono=True)
    peak = float(np.max(np.abs(y))) if y.size else 0.0
    if peak == 0.0:
        raise ValueError(f"소리가 없는 오디오입니다: {path}")
    return y / peak, sr


def record_audio(seconds: float, path: str | Path, sr: int = SAMPLE_RATE) -> Path:
    """마이크로 seconds 초 동안 녹음해서 WAV 로 저장한다."""
    try:
        import sounddevice as sd
    except ImportError as e:  # 선택 의존성
        raise RuntimeError(
            "마이크 녹음에는 sounddevice 패키지가 필요합니다: pip install sounddevice"
        ) from e

    for n in (3, 2, 1):
        print(f"  {n}...", flush=True)
        time.sleep(1)
    print(f"● 녹음 중 ({seconds:g}초)", flush=True)
    data = sd.rec(int(seconds * sr), samplerate=sr, channels=1, dtype="float32")
    sd.wait()
    print("■ 녹음 완료", flush=True)

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, data, sr)
    return path
