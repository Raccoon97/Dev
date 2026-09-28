"""오디오 → 악보 전체 파이프라인.

  오디오 ─▶ 음 검출(초 단위) ─▶ 템포 추정 ─▶ 박자 양자화 ─▶ (타브 운지) ─▶ 조성 추정 ─▶ 악보
          mono: pYIN            librosa     16분음표 격자    비터비          Krumhansl    music21
          poly: basic-pitch
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import librosa
from music21 import key, meter, stream

from . import mono, poly
from .audio import load_audio
from .notes import NoteEvent, QuantizedNote
from .rhythm import estimate_tempo, fit_grid, quantize, ring_together
from .score import build_score, estimate_key
from .tab import TUNINGS, TabNote, Tuning, assign_frets, fit_range, render_ascii, resolve_glides


@dataclass
class Transcription:
    notes: list[NoteEvent]
    qnotes: list[QuantizedNote]
    bpm: float
    key: key.Key
    score: stream.Score
    title: str = ""
    time_signature: str = "4/4"
    tuning: Tuning | None = None
    capo: int = 0
    tab_notes: list[TabNote] = field(default_factory=list)
    moved: int = 0  # 악기 음역 밖이라 옥타브를 옮긴(mono) / 버린(poly) 음 개수
    dropped: int = 0  # 한 손으로 잡을 수 없어 뺀 화음 구성음 개수

    def tab_text(self) -> str:
        """글자 타브 (tab 을 지정했을 때만)."""
        if self.tuning is None:
            return ""
        return render_ascii(
            self.tab_notes,
            self.tuning,
            bar_length=meter.TimeSignature(self.time_signature).barDuration.quarterLength,
            capo=self.capo,
            title=self.title,
            bpm=self.bpm,
            time_signature=self.time_signature,
        )


def transcribe(
    path: str | Path,
    *,
    mode: str = "mono",
    bpm: float | None = None,
    time_signature: str = "4/4",
    grid: int = 16,
    title: str | None = None,
    min_note: float | None = None,
    tab: str | None = None,
    capo: int = 0,
) -> Transcription:
    """오디오 파일을 받아 악보(music21 Score)와 중간 결과를 돌려준다.

    mode : "mono" (멜로디 한 줄), "poly" (피아노처럼 화음이 있는 연주),
           "melody" (화음·반주가 섞인 소리에서 가장 두드러진 선율 한 줄만)
    bpm  : 알고 있으면 지정. 없으면 오디오에서 추정한다.
    grid : 가장 짧은 음표 단위 (16 → 16분음표).
    min_note : 이보다 짧은(초) 음은 버린다. 없으면 mono 0.06초, poly 0.12초.
    tab  : "guitar", "drop-d", "bass", "bass5", "ukulele" 중 하나면 그 악기 타브 보표를 붙이고
           해머링·풀링·슬라이드·벤딩(기타만) 을 읽어 표기한다.
    capo : 카포 위치 (타브의 프렛 번호는 카포 기준).
    """
    path = Path(path)
    if tab is not None and tab not in TUNINGS:
        raise ValueError(f"알 수 없는 악기: {tab} (가능: {', '.join(TUNINGS)})")
    if grid not in (4, 8, 16, 32):
        raise ValueError("grid 는 4, 8, 16, 32 중 하나여야 합니다.")
    division = grid // 4  # 4분음표 한 박을 몇 칸으로 나눌지

    tuning = TUNINGS[tab] if tab is not None else None
    if mode == "mono":
        y, sr = load_audio(path)
        fmin, fmax = "C2", "C7"
        if tuning is not None:  # 악기 음역만 찾으면 베이스 저음(E1=41Hz)도 잡고 엉뚱한 배음도 덜 잡는다
            fmin = librosa.midi_to_note(min(tuning.strings) + capo - 1)
            fmax = librosa.midi_to_note(min(max(tuning.strings) + tuning.frets + 1, 96))
        notes = mono.detect_notes(y, sr, fmin=fmin, fmax=fmax, min_note=min_note or 0.06)
    elif mode == "poly":  # basic-pitch 가 오디오를 직접 읽는다
        notes = poly.detect_notes(path, min_note=min_note or 0.12, drop_overtones=tab is None)
    elif mode == "melody":
        low, high = 52, 93  # E3~A6
        if tuning is not None:  # 그 악기로 낼 수 있는 음역에서만 찾는다
            low, high = min(tuning.strings) + capo, min(max(tuning.strings) + tuning.frets, 96)
        notes = poly.extract_melody(path, low=low, high=high, min_note=min_note or 0.08)
    else:
        raise ValueError(f"알 수 없는 mode: {mode}")
    if not notes:
        raise ValueError("음을 하나도 찾지 못했습니다. 소리가 너무 작거나 잡음이 많은지 확인하세요.")
    if tuning is not None:
        # 미끄러지듯 이어진 음 → 기타면 벤딩/슬라이드, 베이스·우쿨렐레면 슬라이드
        notes = resolve_glides(notes, allow_bends=tuning.bends)

    onsets = sorted(n.start for n in notes)
    guess = bpm if bpm else estimate_tempo(onsets)
    fitted_bpm, t0 = fit_grid(onsets, guess, division, fixed_bpm=bool(bpm))
    bar_length = meter.TimeSignature(time_signature).barDuration.quarterLength
    qnotes = quantize(
        notes, fitted_bpm, t0, division, monophonic=(mode != "poly"), bar_length=bar_length
    )

    tab_notes, moved, dropped = [], 0, 0
    if tuning is not None:
        if mode == "poly":
            qnotes = ring_together(qnotes)
        qnotes, moved = fit_range(qnotes, tuning, capo, drop=(mode == "poly"))
        qnotes = list({(q.offset, q.pitch): q for q in qnotes}.values())  # 옥타브 이동으로 겹친 음 정리
        tab_notes = assign_frets(qnotes, tuning, capo)
        dropped = len(qnotes) - len(tab_notes)
        qnotes = sorted((t.note for t in tab_notes), key=lambda q: (q.offset, q.pitch))

    k = estimate_key(qnotes)
    title = title or path.stem
    score = build_score(
        qnotes,
        bpm=fitted_bpm,
        k=k,
        time_signature=time_signature,
        title=title,
        piano=(mode == "poly" and tuning is None),
        tab=(tuning, tab_notes) if tuning else None,
    )
    return Transcription(
        notes, qnotes, fitted_bpm, k, score, title, time_signature, tuning, capo, tab_notes, moved, dropped
    )
