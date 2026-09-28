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
    timbre  : "organ" (소리가 일정하게 유지), "piano" (치고 나서 점점 작아짐), "guitar" (뜯는 줄)
    """
    tone_fn = {"piano": _piano_tone, "guitar": _guitar_tone}.get(timbre, _tone)
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


def synthesize_chords(
    chords: list[tuple[list[str], float]], bpm: float, sr: int = 22050, *, strum: float = 0.025, lead_in: float = 0.5
) -> np.ndarray:
    """기타 스트로크처럼 화음을 낮은 줄부터 strum 초 간격으로 긁어서 합성한다."""
    beat = 60.0 / bpm
    total = lead_in + sum(b for _, b in chords) * beat + 1.0
    out = np.zeros(int(total * sr))
    t = lead_in
    for names, beats in chords:
        for i, name in enumerate(names):
            tone = _guitar_tone(pitch.Pitch(name).frequency, beats * beat * 0.95 - i * strum, sr, 0.0)
            start = int((t + i * strum) * sr)
            out[start : start + len(tone)] += tone
        t += beats * beat
    return (out / np.max(np.abs(out)) * 0.8).astype(np.float32)


def _guitar_tone(freq: float, dur: float, sr: int, vibrato: float) -> np.ndarray:
    """Karplus-Strong 뜯는 줄 소리: 잡음 한 주기를 되먹이며 거르면 줄 소리처럼 감쇠한다."""
    period = int(np.ceil(sr / freq))
    inner_sr = freq * period  # 주기가 정확히 정수 샘플이 되는 내부 샘플링 주파수 → 음정 오차 없음
    n_inner = int(dur * inner_sr)
    rng = np.random.default_rng(int(freq * 100))
    cycle = np.convolve(rng.uniform(-1, 1, period), [0.5, 0.5], mode="same")  # 살짝 부드러운 픽 소리
    cycles = []
    for _ in range(n_inner // period + 1):
        cycles.append(cycle)
        cycle = 0.996 * 0.5 * (cycle + np.roll(cycle, -1))
    wave = np.concatenate(cycles)[:n_inner]
    n = int(dur * sr)
    wave = np.interp(np.arange(n) * inner_sr / sr, np.arange(n_inner), wave)
    release = min(int(0.02 * sr), n)
    wave[n - release :] *= np.linspace(1, 0, release)
    return wave


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


Lick = list[tuple[str, float, str]]  # (음이름, 박 수, 주법)


def synthesize_lick(lick: Lick, bpm: float, sr: int = 22050, *, lead_in: float = 0.5) -> np.ndarray:
    """주법이 들어간 기타 한 줄 연주를 합성한다 (주법 인식 테스트용).

    주법: ""(피킹) | "h"(해머링) | "p"(풀링) | "/"(앞 음에서 슬라이드) |
          "b2"(2반음 벤딩) | "b2r"(벤딩 후 릴리즈) | "<"(아래에서 슬라이드 인) | ">"(끝에서 슬라이드 아웃)
    해머링·풀링·슬라이드는 줄을 다시 치지 않으므로 소리를 새로 내지 않고 음높이만 바꾼다.
    """
    beat = 60.0 / bpm
    total = lead_in + sum(b for _, b, _ in lick) * beat + 0.5
    n = int(total * sr)
    t = np.arange(n) / sr
    semis = np.full(n, np.nan)  # 시각마다 음높이 (MIDI, 소리 없으면 nan)
    phrase = np.full(n, -1)  # 시각마다 몇 번째로 친 소리인가
    starts = []

    pos, k = lead_in, -1
    prev, prev_end = None, 0
    for name, beats, how in lick:
        p = pitch.Pitch(name).midi
        s, e = int(pos * sr), int((pos + beats * beat * 0.97) * sr)
        if how not in ("h", "p", "/") or prev is None:
            k += 1
            starts.append(s)
        else:  # 이어지는 음: 앞 음이 틈 없이 여기까지 울린다
            semis[prev_end:s] = prev
            phrase[prev_end:s] = k
        seg = np.full(e - s, float(p))
        tt = t[s:e] - pos
        if how == "/" and prev is not None:  # 앞 음에서 80ms 동안 미끄러져 옴
            glide = int(0.04 * sr)
            semis[s - glide : s] = np.linspace(prev, prev + (p - prev) / 2, glide)
            seg[:glide] = np.linspace(prev + (p - prev) / 2, p, glide)
        if how.startswith("b"):  # 치고 80ms 뒤부터 150ms 동안 밀어 올림
            amount = int(how[1])
            seg += amount * _smoothstep((tt - 0.08) / 0.15)
            if how.endswith("r"):  # 음 길이의 60% 지점에서 되돌림
                seg -= amount * _smoothstep((tt - beats * beat * 0.6) / 0.15)
        if how == "<":
            seg -= 4 * (1 - _smoothstep(tt / 0.08))
        if how == ">":
            seg -= 5 * _smoothstep((tt - (tt[-1] - 0.15)) / 0.15)
        semis[s:e] = seg
        phrase[s:e] = k
        pos += beats * beat
        prev, prev_end = p, e

    freq = 440.0 * 2 ** ((np.nan_to_num(semis, nan=69.0) - 69) / 12)
    phase = 2 * np.pi * np.cumsum(freq) / sr
    out = np.zeros(n)
    for k, s in enumerate(starts):
        mask = phrase == k
        idx = np.where(mask)[0]
        age = (np.arange(n) - s) / sr
        env = np.where(mask, np.exp(-np.clip(age, 0, None) * 1.2), 0.0)
        env[s : s + int(0.003 * sr)] *= np.linspace(0, 1, int(0.003 * sr))
        tail = int(0.015 * sr)
        env[idx[-1] - tail + 1 : idx[-1] + 1] *= np.linspace(1, 0, tail)
        tone = sum(a * np.sin(h * phase) * np.exp(-np.clip(age, 0, None) * 0.8 * h) for h, a in ((1, 1.0), (2, 0.5), (3, 0.33), (4, 0.25)))
        out += env * tone
    return (out / np.max(np.abs(out)) * 0.8).astype(np.float32)


def _smoothstep(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)
