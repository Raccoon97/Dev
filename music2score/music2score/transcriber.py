"""오디오 → 악보 전체 파이프라인.

  오디오 ─▶ 음 검출(초 단위) ─▶ 템포 추정 ─▶ 박자 양자화 ─▶ 조성 추정 ─▶ 악보
          mono: pYIN            librosa     16분음표 격자    Krumhansl    music21
          poly: basic-pitch
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from music21 import key, meter, stream

from . import mono, poly
from .audio import load_audio
from .notes import NoteEvent, QuantizedNote
from .rhythm import estimate_tempo, fit_grid, quantize
from .score import build_score, estimate_key


@dataclass
class Transcription:
    notes: list[NoteEvent]
    qnotes: list[QuantizedNote]
    bpm: float
    key: key.Key
    score: stream.Score


def transcribe(
    path: str | Path,
    *,
    mode: str = "mono",
    bpm: float | None = None,
    time_signature: str = "4/4",
    grid: int = 16,
    title: str | None = None,
    min_note: float | None = None,
) -> Transcription:
    """오디오 파일을 받아 악보(music21 Score)와 중간 결과를 돌려준다.

    mode : "mono" (멜로디 한 줄) 또는 "poly" (피아노처럼 화음이 있는 연주)
    bpm  : 알고 있으면 지정. 없으면 오디오에서 추정한다.
    grid : 가장 짧은 음표 단위 (16 → 16분음표).
    min_note : 이보다 짧은(초) 음은 버린다. 없으면 mono 0.06초, poly 0.12초.
    """
    path = Path(path)
    if grid not in (4, 8, 16, 32):
        raise ValueError("grid 는 4, 8, 16, 32 중 하나여야 합니다.")
    division = grid // 4  # 4분음표 한 박을 몇 칸으로 나눌지

    if mode == "mono":
        y, sr = load_audio(path)
        notes = mono.detect_notes(y, sr, min_note=min_note or 0.06)
    elif mode == "poly":  # basic-pitch 가 오디오를 직접 읽는다
        notes = poly.detect_notes(path, min_note=min_note or 0.12)
    else:
        raise ValueError(f"알 수 없는 mode: {mode}")
    if not notes:
        raise ValueError("음을 하나도 찾지 못했습니다. 소리가 너무 작거나 잡음이 많은지 확인하세요.")

    onsets = sorted(n.start for n in notes)
    guess = bpm if bpm else estimate_tempo(onsets)
    fitted_bpm, t0 = fit_grid(onsets, guess, division, fixed_bpm=bool(bpm))
    bar_length = meter.TimeSignature(time_signature).barDuration.quarterLength
    qnotes = quantize(
        notes, fitted_bpm, t0, division, monophonic=(mode == "mono"), bar_length=bar_length
    )

    k = estimate_key(qnotes)
    score = build_score(
        qnotes,
        bpm=fitted_bpm,
        k=k,
        time_signature=time_signature,
        title=title or path.stem,
        piano=(mode == "poly"),
    )
    return Transcription(notes, qnotes, fitted_bpm, k, score)
