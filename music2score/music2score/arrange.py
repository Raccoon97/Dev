"""기타 한 대로 칠 수 있는 편곡 (핑거스타일): 1·2번 줄에 선율, 6~4번 줄에 베이스.

원곡을 악기별로 떼어 낸 소리 두 개를 받는다.
  - 선율: 건반·기타 등 나머지 악기(other)에서 가장 두드러진 선율 한 줄 (--mode melody 와 같은 방법)
  - 베이스: 베이스 소리(bass)에서 읽은 베이스 라인
선율은 옥타브 단위로 옮겨 기타 1·2번 줄 낮은 포지션에 오게 하고, 베이스는 한 손으로 선율과
함께 누를 수 있도록 강박(4/4 에서 1·3박)마다 한 음만 남겨 6~4번 줄 음역에 놓는다.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import replace
from pathlib import Path

from music21 import meter

from . import mono, poly
from .audio import load_audio
from .notes import NoteEvent, QuantizedNote
from .rhythm import estimate_tempo, fit_grid, quantize
from .score import build_score, estimate_key
from .tab import TUNINGS, assign_frets, fit_range

MELODY_CENTER = 69  # A4: 선율의 중앙값을 여기 가까이 → 1·2번 줄 0~10프렛
BASS_LOW, BASS_HIGH = 40, 52  # E2~E3: 6·5·4번 줄 개방현 ~ 7프렛
MIN_GAP = 5  # 같은 순간 베이스는 선율보다 이만큼(반음) 이상 낮아야 한다


def melody_octave_shift(notes: list[NoteEvent], center: int = MELODY_CENTER) -> int:
    """선율 전체를 몇 옥타브 옮겨야 중앙값이 center 근처에 오는지 (반음 수).

    두 옥타브 사이 딱 가운데면 내리는 쪽을 고른다 (기타는 낮을수록 치기 편하다).
    """
    if not notes:
        return 0
    median = statistics.median(n.pitch for n in notes)
    return 12 * math.floor((center - median + 6) / 12 - 1e-9)


def fold_bass(pitch: int) -> int:
    """베이스 음을 옥타브 단위로 옮겨 E2~E3 안에 넣는다."""
    while pitch < BASS_LOW:
        pitch += 12
    while pitch > BASS_HIGH:
        pitch -= 12
    return pitch


def bass_on_strong_beats(bass: list[QuantizedNote], total: float, step: float) -> list[QuantizedNote]:
    """step(4분음표 단위)마다 그 순간 울리고 있거나 곧 시작하는 베이스 음 하나만 남긴다."""
    out: list[QuantizedNote] = []
    t = 0.0
    while t < total:
        sounding = [q for q in bass if q.offset <= t < q.end]
        soon = [q for q in bass if t < q.offset < t + step / 2]
        pick = sounding[-1] if sounding else (soon[0] if soon else None)
        if pick is not None:
            out.append(QuantizedNote(t, step, fold_bass(pick.pitch), pick.velocity))
        t += step
    return out


def combine(melody: list[QuantizedNote], bass: list[QuantizedNote]) -> list[QuantizedNote]:
    """선율과 베이스를 합친다. 베이스가 그 순간 선율에 너무 붙으면 한 옥타브 내리고, 그래도 안 되면 뺀다."""
    out = list(melody)
    for b in bass:
        above = [m.pitch for m in melody if m.offset <= b.offset < m.end or b.offset <= m.offset < b.end]
        pitch = b.pitch
        if above and pitch > min(above) - MIN_GAP:
            pitch -= 12
        if pitch < BASS_LOW or (above and pitch > min(above) - MIN_GAP):
            continue  # 기타 가장 낮은 음(E2)보다 내려가면 칠 수 없다
        out.append(replace(b, pitch=pitch))
    return sorted(out, key=lambda q: (q.offset, q.pitch))


def arrange(
    melody_path: str | Path,
    bass_path: str | Path,
    *,
    tab: str = "guitar",
    bpm: float | None = None,
    time_signature: str = "4/4",
    grid: int = 8,
    title: str = "Arrangement",
    capo: int = 0,
    transpose: int | None = None,
):
    """선율 소리와 베이스 소리에서 기타 독주 편곡을 만든다. transpose 를 안 주면 선율 옥타브를 자동으로 맞춘다."""
    from .transcriber import Transcription  # 순환 import 방지

    tuning = TUNINGS[tab]
    division = grid // 4

    melody_notes = poly.extract_melody(melody_path, low=52, high=96)
    y, sr = load_audio(bass_path)
    bass_notes = mono.detect_notes(y, sr, fmin="B0", fmax="G3")
    if not melody_notes:
        raise ValueError("선율을 찾지 못했습니다.")

    shift = melody_octave_shift(melody_notes) if transpose is None else transpose
    melody_notes = [replace(n, pitch=n.pitch + shift) for n in melody_notes]

    onsets = sorted(n.start for n in melody_notes + bass_notes)
    guess = bpm if bpm else estimate_tempo(onsets)
    fitted_bpm, t0 = fit_grid(onsets, guess, division, fixed_bpm=bool(bpm))
    bar = meter.TimeSignature(time_signature).barDuration.quarterLength

    melody_q = quantize(melody_notes, fitted_bpm, t0, division, monophonic=True, bar_length=bar)
    melody_q, _ = fit_range(melody_q, tuning, capo)
    bass_q = quantize(bass_notes, fitted_bpm, t0, division, monophonic=True, bar_length=bar) if bass_notes else []
    total = max(q.end for q in melody_q)
    strong = bar / 2 if bar % 2 == 0 else bar  # 4/4 → 2박마다, 3/4 → 마디마다
    qnotes = combine(melody_q, bass_on_strong_beats(bass_q, total, strong))

    tab_notes = assign_frets(qnotes, tuning, capo)
    dropped = len(qnotes) - len(tab_notes)
    qnotes = sorted((t.note for t in tab_notes), key=lambda q: (q.offset, q.pitch))
    k = estimate_key(melody_q)
    score = build_score(
        qnotes, bpm=fitted_bpm, k=k, time_signature=time_signature, title=title, tab=(tuning, tab_notes)
    )
    return Transcription(
        melody_notes + bass_notes, qnotes, fitted_bpm, k, score, title, time_signature, tuning, capo, tab_notes, 0, dropped, shift
    )
