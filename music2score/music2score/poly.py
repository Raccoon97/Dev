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


# ── 화음 속에서 선율 한 줄 뽑기 ────────────────────────────────

FPS = 86  # basic-pitch 출력 프레임 (22050Hz / 256)
LOWEST_KEY = 21  # basic-pitch 88건반 출력의 첫 칸 = A0


def extract_melody(
    path: str | Path,
    *,
    low: int = 52,
    high: int = 93,
    min_note: float = 0.08,
) -> list[NoteEvent]:
    """반주·건반처럼 여러 음이 겹친 소리에서 가장 두드러진 선율 한 줄을 뽑는다.

    low~high(MIDI, 기본 E3~A6)는 선율을 찾을 음역이다. 기타로 치기 좋은 높이를 기본으로 둔다.
    """
    try:
        from basic_pitch import ICASSP_2022_MODEL_PATH
        from basic_pitch.inference import predict
    except ImportError as e:
        raise RuntimeError("선율 뽑기(--melody)에는 basic-pitch 가 필요합니다: pip install basic-pitch") from e
    output, _, _ = predict(str(path), ICASSP_2022_MODEL_PATH)
    return melody_from_posteriors(output["note"], output["onset"], low=low, high=high, min_note=min_note)


def melody_from_posteriors(
    note: np.ndarray,
    onset: np.ndarray,
    *,
    low: int = 52,
    high: int = 93,
    min_note: float = 0.08,
    fps: float = FPS,
    rest_level: float = 0.3,
    height_bonus: float = 1.5,
    switch_cost: float = 1.5,
    jump_cost: float = 0.3,
    min_strength: float = 0.4,
) -> list[NoteEvent]:
    """프레임별 음 확률(note: 프레임 × 88건반)에서 선율 한 줄을 비터비로 고른다.

    프레임마다 '어느 음이 선율인가(또는 쉼)'를 정하는데, 곡 전체에서
      - 그 음이 울릴 확률이 높을수록 (-log 확률),
      - 높은 음일수록 (선율은 보통 반주 위에 있다),
      - 음을 덜 바꿀수록, 바꾸더라도 가까운 음으로 갈수록
    싼 길을 고른다. 확률이 rest_level 보다 낮으면 쉼이 더 싸다.
    평균 확률이 min_strength 에 못 미치면서 짧은 음(0.2초 미만)은 모델이 잘못 잡은 잔음으로 보고 버린다.
    """
    lo, hi = low - LOWEST_KEY, high - LOWEST_KEY + 1
    probs = note[:, lo:hi]
    n_frames, k = probs.shape
    if n_frames == 0:
        return []
    emit = np.empty((n_frames, k + 1))
    emit[:, :k] = -np.log(probs + 1e-4) - height_bonus * np.linspace(0.0, 1.0, k)
    # 높은 음 가산점 때문에 거의 안 울리는 높은 잔음이 쉼을 이기지 않도록, 약한 음은 아예 못 고르게 한다.
    emit[:, :k][probs < 0.7 * rest_level] = 20.0
    emit[:, k] = -np.log(rest_level)  # 마지막 상태 = 쉼

    keys = np.arange(k)
    trans = np.zeros((k + 1, k + 1))
    trans[:k, :k] = np.where(keys[:, None] != keys[None, :], switch_cost + jump_cost * np.abs(keys[:, None] - keys[None, :]), 0.0)
    trans[:k, k] = trans[k, :k] = switch_cost / 2  # 쉼으로 들어가고 나오기

    cost = emit[0].copy()
    back = np.empty((n_frames, k + 1), dtype=np.int32)
    for t in range(1, n_frames):
        total = cost[:, None] + trans
        back[t] = total.argmin(axis=0)
        cost = total.min(axis=0) + emit[t]
    path = np.empty(n_frames, dtype=np.int32)
    path[-1] = int(cost.argmin())
    for t in range(n_frames - 1, 0, -1):
        path[t - 1] = back[t, path[t]]

    # 같은 음이 이어진 구간 = 음 하나. 같은 음을 다시 친 곳(onset 봉우리)에서는 나눈다.
    min_frames = max(1, int(round(min_note * fps)))
    notes: list[NoteEvent] = []
    t = 0
    while t < n_frames:
        state = path[t]
        u = t + 1
        while u < n_frames and path[u] == state:
            u += 1
        if state < k:
            key = lo + state
            cuts = [t]
            for f in range(t + min_frames, u - min_frames):
                o = onset[f, key]
                if o > 0.5 and o >= onset[f - 1, key] and o >= onset[f + 1, key] and f - cuts[-1] >= min_frames:
                    cuts.append(f)
            for a, b in zip(cuts, [*cuts[1:], u]):
                strength = float(probs[a:b, state].mean())
                if b - a < min_frames or (strength < min_strength and b - a < 0.2 * fps):
                    continue
                notes.append(NoteEvent(a / fps, b / fps, key + LOWEST_KEY, int(np.clip(strength * 127, 1, 127))))
        t = u
    return notes
