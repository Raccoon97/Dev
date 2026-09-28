"""다성(화음) 음 검출 — Spotify 의 basic-pitch 신경망 모델 사용.

피아노, 기타처럼 여러 음이 동시에 울리는 연주에 쓴다.
basic-pitch 는 TensorFlow 를 끌어오는 무거운 패키지라 선택 의존성으로 둔다.
"""

from __future__ import annotations

import bisect
from pathlib import Path

import numpy as np

from .notes import NoteEvent

# 배음이 따로 음으로 잡히기 쉬운 음정 (옥타브, 옥타브+5도, 두 옥타브)
OVERTONE_INTERVALS = (12, 19, 24)
# 기타 스트로크·펼침화음: 앞 음과 STRUM_GAP 초 안에 이어서 시작하고, 첫 음부터
# STRUM_SPAN 초 안에 있는 음들은 한 화음으로 본다.
STRUM_GAP = 0.09  # 16분음표(150 BPM 에서 0.1초)보다는 짧게
STRUM_SPAN = 0.15


def detect_notes(
    path: str | Path,
    *,
    min_note: float = 0.12,
    onset_threshold: float = 0.5,
    frame_threshold: float = 0.3,
    drop_overtones: bool = True,
) -> list[NoteEvent]:
    """drop_overtones: 배음 유령 제거. 기타 화음은 옥타브 겹침이 기본이라 타브 모드에선 끈다."""
    try:
        from basic_pitch import ICASSP_2022_MODEL_PATH
        from basic_pitch.inference import predict
    except ImportError as e:
        raise RuntimeError(
            "다성 모드(--mode poly)에는 basic-pitch 가 필요합니다: pip install basic-pitch"
        ) from e

    _, _, events = predict(
        str(path),
        ICASSP_2022_MODEL_PATH,
        onset_threshold=onset_threshold,
        frame_threshold=frame_threshold,
        minimum_note_length=min_note * 1000,  # ms
    )
    notes = [
        NoteEvent(float(start), float(end), int(pitch), int(max(1, min(127, amp * 127))))
        for start, end, pitch, amp, _bends in events
    ]
    return remove_ghosts(merge_strums(notes), drop_overtones=drop_overtones)


def merge_strums(notes: list[NoteEvent]) -> list[NoteEvent]:
    """조금씩 어긋나게 시작한 화음 구성음들의 시작을 한 시각(중앙값)으로 모은다.

    같은 무리 안에 같은 음이 두 번 잡혔으면(스트로크 도중 끊겨 다시 잡힌 경우) 하나로 합친다.
    """
    notes = sorted(notes, key=lambda n: n.start)
    merged: list[NoteEvent] = []
    i = 0
    while i < len(notes):
        j = i
        while (
            j + 1 < len(notes)
            and notes[j + 1].start - notes[j].start <= STRUM_GAP
            and notes[j + 1].start - notes[i].start <= STRUM_SPAN
        ):
            j += 1
        group = notes[i : j + 1]
        start = float(np.median([n.start for n in group]))
        by_pitch: dict[int, NoteEvent] = {}
        for n in group:
            prev = by_pitch.get(n.pitch)
            end = max(n.end, prev.end) if prev else n.end
            velocity = max(n.velocity, prev.velocity) if prev else n.velocity
            by_pitch[n.pitch] = NoteEvent(start, max(end, start + 0.01), n.pitch, velocity)
        merged += sorted(by_pitch.values(), key=lambda n: n.pitch)
        i = j + 1
    return merged


def remove_ghosts(notes: list[NoteEvent], *, drop_overtones: bool = True) -> list[NoteEvent]:
    """모델이 잘못 잡은 음을 걸러낸다.

    - 배음 유령: 옥타브/12도/두 옥타브 아래 음과 거의 동시에 시작했고, 그보다
      확실히 작은 음. (진짜 옥타브 연주는 두 음 세기가 비슷해서 남는다.)
    - 잡음: 전체 중앙값보다 훨씬 작으면서 짧은 음.
    """
    if not notes:
        return notes
    notes = sorted(notes, key=lambda n: n.start)
    starts = [n.start for n in notes]
    median_velocity = float(np.median([n.velocity for n in notes]))

    kept = []
    for n in notes:
        if n.velocity < 0.6 * median_velocity and n.duration < 0.3:
            continue
        if not drop_overtones:
            kept.append(n)
            continue
        lo = bisect.bisect_left(starts, n.start - 0.08)
        hi = bisect.bisect_right(starts, n.start + 0.08)
        ghost = any(
            n.pitch - m.pitch in OVERTONE_INTERVALS and n.velocity < 0.75 * m.velocity
            for m in notes[lo:hi]
        )
        if not ghost:
            kept.append(n)
    return kept
