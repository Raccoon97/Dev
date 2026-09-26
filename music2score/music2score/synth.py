"""간단한 신시사이저 — 테스트와 데모용 오디오를 만든다."""

from __future__ import annotations

import numpy as np
from music21 import pitch

Melody = list[tuple[str | None, float]]  # (음이름 또는 None=쉼표, 박 수)

# 학교종이 땡땡땡 (다장조, 4/4)
SCHOOL_BELL: Melody = [
    ("G4", 1), ("G4", 1), ("A4", 1), ("A4", 1),
    ("G4", 1), ("G4", 1), ("E4", 2),
    ("G4", 1), ("G4", 1), ("E4", 1), ("E4", 1),
    ("D4", 4),
    ("G4", 1), ("G4", 1), ("A4", 1), ("A4", 1),
    ("G4", 1), ("G4", 1), ("E4", 2),
    ("G4", 1), ("E4", 1), ("D4", 1), ("E4", 1),
    ("C4", 4),
]

# 학교종 왼손 반주 (마디마다 온음표 화음)
SCHOOL_BELL_CHORDS: list[list[str]] = [
    ["C3", "E3", "G3"], ["C3", "E3", "G3"], ["C3", "E3", "G3"], ["G2", "B2", "D3"],
    ["C3", "E3", "G3"], ["C3", "E3", "G3"], ["G2", "B2", "D3"], ["C3", "E3", "G3"],
]


def synthesize(
    melody: Melody,
    bpm: float,
    sr: int = 22050,
    *,
    legato: float = 0.9,
    vibrato: float = 0.0,
    noise: float = 0.0,
    lead_in: float = 0.5,
    seed: int = 0,
    timbre: str = "organ",
) -> np.ndarray:
    """배음이 섞인 음색으로 멜로디를 합성한다.

    legato  : 음 길이 중 실제로 소리 나는 비율 (1.0 이면 음 사이 틈이 없다)
    vibrato : 비브라토 폭 (반음 단위)
    noise   : 백색 잡음 크기
    lead_in : 첫 음 앞 무음 (초)
    timbre  : "organ" (소리가 일정하게 유지) 또는 "piano" (치고 나서 점점 작아짐)
    """
    tone_fn = _piano_tone if timbre == "piano" else _tone
    beat = 60.0 / bpm
    total = lead_in + sum(b for _, b in melody) * beat + 0.5
    out = np.zeros(int(total * sr))
    t = lead_in
    for name, beats in melody:
        dur = beats * beat
        if name is not None:
            tone = tone_fn(pitch.Pitch(name).frequency, dur * legato, sr, vibrato)
            i = int(t * sr)
            out[i : i + len(tone)] += tone
        t += dur
    if noise:
        out += np.random.default_rng(seed).normal(0, noise, len(out))
    return (out / np.max(np.abs(out)) * 0.8).astype(np.float32)


def synthesize_piano(melody: Melody, chords: list[list[str]], bpm: float, sr: int = 22050) -> np.ndarray:
    """오른손 멜로디 + 왼손 화음(마디마다 온음표)을 피아노 음색으로 합성한다."""
    out = synthesize(melody, bpm, sr, legato=0.95, timbre="piano").astype(float)
    for voice in range(max(len(c) for c in chords)):
        line: Melody = [(c[voice] if voice < len(c) else None, 4) for c in chords]
        v = synthesize(line, bpm, sr, legato=0.95, timbre="piano")
        n = min(len(out), len(v))
        out[:n] += 0.45 * v[:n]
    return (out / np.max(np.abs(out)) * 0.8).astype(np.float32)


def _tone(freq: float, dur: float, sr: int, vibrato: float) -> np.ndarray:
    n = int(dur * sr)
    t = np.arange(n) / sr
    f = freq * 2 ** (vibrato * np.sin(2 * np.pi * 5.5 * t) / 12)
    phase = 2 * np.pi * np.cumsum(f) / sr
    wave = sum(amp * np.sin(h * phase) for h, amp in ((1, 1.0), (2, 0.5), (3, 0.3), (4, 0.15)))

    attack, release = int(0.015 * sr), int(0.04 * sr)
    env = np.ones(n) * 0.8
    env[:attack] = np.linspace(0, 1, attack)
    decay = min(int(0.08 * sr), n - attack)
    env[attack : attack + decay] = np.linspace(1, 0.8, decay)
    env[-release:] *= np.linspace(1, 0, release)
    return wave * env


def _piano_tone(freq: float, dur: float, sr: int, vibrato: float) -> np.ndarray:
    n = int(dur * sr)
    t = np.arange(n) / sr
    # 높은 배음일수록 약하고 빨리 사라지며, 현의 강성 때문에 배음이 살짝 높아진다.
    wave = sum(
        0.6 ** (h - 1) * np.sin(2 * np.pi * freq * h * np.sqrt(1 + 0.0004 * h * h) * t) * np.exp(-t * (1.5 + 0.8 * h))
        for h in range(1, 8)
    )
    attack, release = int(0.005 * sr), int(0.03 * sr)
    wave[:attack] *= np.linspace(0, 1, attack)
    wave[-release:] *= np.linspace(1, 0, release)
    return wave
