"""템포 추정과 박자 격자 양자화 (초 → 4분음표 단위)."""

from __future__ import annotations

import math

import librosa
import numpy as np

from .notes import NoteEvent, QuantizedNote

MIN_BPM = 60.0
MAX_BPM = 180.0


def estimate_tempo(onsets: list[float] | np.ndarray) -> float:
    """검출한 음들의 시작 시각이 반복되는 주기로 BPM 을 추정한다 (60~180 으로 접어서 반환).

    오디오 전체의 어택 강도 대신 음 시작 시각만 쓰므로 잡음에 덜 흔들린다.
    """
    onsets = np.asarray(onsets, dtype=float)
    if onsets.size < 3:
        return 120.0
    sr, hop = 22050, 512  # 약 23ms 해상도의 가상 onset 곡선
    env = np.zeros(int(onsets.max() * sr / hop) + 50)
    np.add.at(env, np.round(onsets * sr / hop).astype(int), 1.0)
    env = np.convolve(env, np.hanning(5), mode="same")
    bpm = float(librosa.feature.tempo(onset_envelope=env, sr=sr, hop_length=hop)[0])
    if not np.isfinite(bpm) or bpm <= 0:
        return 120.0
    while bpm > MAX_BPM:
        bpm /= 2
    while bpm < MIN_BPM:
        bpm *= 2
    return bpm


def fit_grid(
    onsets: list[float] | np.ndarray,
    bpm: float,
    division: int,
    *,
    fixed_bpm: bool = False,
    search: float = 0.06,
) -> tuple[float, float]:
    """음 시작 시각들이 격자에 가장 잘 맞도록 (bpm, 첫 박 시각 t0) 를 미세 조정한다.

    추정 BPM 이 조금만 틀려도 곡 뒤쪽으로 갈수록 박이 밀리므로,
    ±search 범위에서 격자 오차가 가장 작은 BPM 을 찾는다. 범위가 좁아서
    두 배/절반 템포로 튀는 일은 없다.
    """
    onsets = np.sort(np.asarray(onsets, dtype=float))
    if onsets.size == 0:
        return bpm, 0.0
    first = float(onsets[0])
    if onsets.size < 4:
        return bpm, first

    candidates = [bpm] if fixed_bpm else np.linspace(bpm * (1 - search), bpm * (1 + search), 121)
    best = (np.inf, bpm, first)
    for cand in candidates:
        grid = 60.0 / cand / division
        for shift in np.linspace(-0.5, 0.5, 21) * grid:
            t0 = first + shift
            pos = (onsets - t0) / grid
            err = float(np.mean(np.abs(pos - np.round(pos))))
            err += 0.05 * abs(cand - bpm) / bpm  # 동점이면 원래 추정에 가까운 쪽
            if err < best[0]:
                best = (err, float(cand), t0)
    return best[1], best[2]


def quantize(
    notes: list[NoteEvent],
    bpm: float,
    t0: float,
    division: int = 4,
    *,
    monophonic: bool = True,
    bar_length: float = 4.0,
) -> list[QuantizedNote]:
    """음의 시작/끝을 1/division 박 격자에 맞춘다 (division=4 → 16분음표).

    monophonic 이면 음이 겹치지 않게 자르고, 음과 음 사이의 짧은 틈은 앞 음을
    늘려 메운다 — 사람이 부르거나 연주할 때 음 끝이 조금씩 일찍 끊기는 것이
    쉼표로 도배되는 것을 막기 위해서다. bar_length 는 마디 길이(4분음표 단위)로,
    마지막 음을 마디 끝까지 늘릴지 판단할 때 쓴다.
    """
    beat = 60.0 / bpm
    step = 1.0 / division
    slack = _articulation_slack(notes)

    def snap(t: float) -> float:
        return round((t - t0) / beat * division) / division

    snapped = []
    for n in sorted(notes, key=lambda n: (n.start, n.pitch)):
        s = max(0.0, snap(n.start))
        e = max(snap(n.end), s + step)
        snapped.append(QuantizedNote(s, e - s, n.pitch, n.velocity))

    if monophonic:
        return _monophonize(snapped, step, bar_length, slack)
    return _dedupe(_align_ends(snapped, step, bar_length, slack))


def _articulation_slack(notes: list[NoteEvent]) -> float:
    """연주자가 음을 얼마나 끊어 치는지 보고, 음 끝 뒤의 틈을 얼마나 봐줄지 정한다.

    음 하나만 봐서는 "온음표를 80% 만 끈 것"과 "점2분음표 + 4분쉼표"를 구분할 수
    없다. 그래서 곡 전체에서 (소리 난 길이 / 다음 음까지 간격) 의 중앙값 a 를 재고,
    소리 난 길이의 (1-a)/a 만큼(+여유 15%) 틈은 아티큘레이션으로 본다.
    끊어 부르는 사람이면 넉넉하게, 레가토로 이어 부르는 사람이면 빡빡하게 된다.
    """
    ordered = sorted(notes, key=lambda n: n.start)
    ratios = [
        cur.duration / (nxt.start - cur.start)
        for cur, nxt in zip(ordered, ordered[1:])
        if nxt.start > cur.start
    ]
    a = float(np.clip(np.median(ratios), 0.6, 1.0)) if ratios else 0.9
    return (1 - a) / a + 0.15


def _fill_gap(length: float, gap: float, step: float, slack: float) -> bool:
    """이 정도 틈이면 연주 습관(아티큘레이션)으로 보고 앞 음에 붙인다."""
    return gap <= max(step, slack * length)


def _monophonize(
    qnotes: list[QuantizedNote], step: float, bar_length: float, slack: float
) -> list[QuantizedNote]:
    # 같은 칸에서 시작하는 음이 여럿이면 가장 긴 것 하나만 남긴다.
    by_offset: dict[float, QuantizedNote] = {}
    for q in qnotes:
        if q.offset not in by_offset or q.length > by_offset[q.offset].length:
            by_offset[q.offset] = q
    ordered = [by_offset[k] for k in sorted(by_offset)]

    result = []
    for cur, nxt in zip(ordered, ordered[1:] + [None]):
        end = cur.end
        # 다음 음 시작(마지막 음이면 마디 끝)까지 붙일 수 있으면 붙이고,
        # 아니면 쉼표가 오므로 음 끝을 다음 박 → 반 박 경계 순으로 맞춰 본다.
        limit = nxt.offset if nxt is not None else math.ceil(end / bar_length) * bar_length
        if end >= limit:
            end = limit
        else:
            for boundary in (limit, math.ceil(end), math.ceil(end * 2) / 2):
                if boundary <= limit and _fill_gap(cur.length, boundary - end, step, slack):
                    end = float(boundary)
                    break
        result.append(QuantizedNote(cur.offset, end - cur.offset, cur.pitch, cur.velocity))
    return result


def ring_together(qnotes: list[QuantizedNote]) -> list[QuantizedNote]:
    """같이 시작한 음들은 같이 끝나게 한다 (기타 스트로크처럼 한 번에 친 화음).

    모델은 화음 구성음마다 길이를 제각각 잡아서(높은 줄은 빨리 사그라든다)
    악보가 붙임줄 조각투성이가 된다. 한 번에 긁은 줄들은 함께 울리므로 가장 긴 음에
    맞추고, 같은 음이 다시 나오면 거기서 끊는다.
    """
    longest: dict[float, float] = {}
    for q in qnotes:
        longest[q.offset] = max(longest.get(q.offset, 0.0), q.length)
    rung = [QuantizedNote(q.offset, longest[q.offset], q.pitch, q.velocity) for q in qnotes]
    return _dedupe(sorted(rung, key=lambda q: (q.offset, q.pitch)))


def _align_ends(
    qnotes: list[QuantizedNote], step: float, bar_length: float, slack: float
) -> list[QuantizedNote]:
    """다성: 음 끝을 가까운 다른 음의 시작이나 마디선에 맞춘다.

    화음 안의 음들이 조금씩 다른 때에 끝나면 악보가 붙임줄 조각으로 잘게
    쪼개지므로, 허용 범위 안에 있는 가장 가까운 경계로 끝을 모은다.
    """
    if not qnotes:
        return qnotes
    last = max(q.end for q in qnotes)
    bars = np.arange(0.0, last + bar_length, bar_length)
    boundaries = np.array(sorted({q.offset for q in qnotes} | set(bars.tolist())))

    result = []
    for q in qnotes:
        tol = max(step, slack * q.length)
        near = boundaries[(boundaries > q.offset) & (np.abs(boundaries - q.end) <= tol)]
        end = float(near[np.argmin(np.abs(near - q.end))]) if near.size else q.end
        result.append(QuantizedNote(q.offset, end - q.offset, q.pitch, q.velocity))
    return result


def _dedupe(qnotes: list[QuantizedNote]) -> list[QuantizedNote]:
    # 다성: 같은 음높이가 겹치면 앞 음을 뒤 음 시작에서 끊는다.
    result: list[QuantizedNote] = []
    last_by_pitch: dict[int, int] = {}
    for q in qnotes:
        i = last_by_pitch.get(q.pitch)
        if i is not None:
            prev = result[i]
            if prev.offset == q.offset:
                if q.length > prev.length:
                    result[i] = q
                continue
            if prev.end > q.offset:
                result[i] = QuantizedNote(prev.offset, q.offset - prev.offset, prev.pitch, prev.velocity)
        last_by_pitch[q.pitch] = len(result)
        result.append(q)
    return result
