"""단선율(멜로디 한 줄) 음 검출과 주법(해머링·풀링·슬라이드·벤딩) 읽기.

pYIN 으로 프레임마다 기본 주파수(f0)를 추정한 뒤,
  1. 어택(피킹)과 무음을 경계로 "한 번 친 소리"(프레이즈)로 나누고,
  2. 프레이즈 안에서 음높이가 머무는 구간을 음으로, 그 사이를 전이로 본다.
     - 한 프레임 만에 뛰는 전이 → 해머링(위로) / 풀링(아래로)
     - 여러 프레임에 걸쳐 미끄러지는 전이 → 글라이드 (슬라이드 또는 벤딩)
     - 첫 음 앞 / 끝 음 뒤의 글라이드 → 슬라이드 인 / 슬라이드 아웃
노래, 허밍, 휘파람, 기타·베이스 한 줄 연주 같은 단선율에 적합하다.
"""

from __future__ import annotations

import librosa
import numpy as np

from .notes import NoteEvent, Technique

HOP_LENGTH = 256
FRAME_LENGTH = 2048  # 약 93ms. 저음(베이스 E1=41Hz)까지 잡으려면 이만큼 길어야 한다
SHORT_FRAME_LENGTH = 1024  # 약 46ms. 가장 낮은 음이 75Hz 이상이면(기타 등) 짧은 창으로 전이를 또렷하게

# 기준 음높이에서 이만큼(반음 단위) 벗어난 상태가 CHANGE_FRAMES 동안 이어지면 다른 음으로 본다.
# 1 반음보다 작게 잡되, 비브라토에 쪼개지지 않도록 여유를 둔다.
PITCH_CHANGE_SEMITONES = 0.75
CHANGE_FRAMES = 4

# 음량은 짧은 창(약 23ms)으로 재야 음과 음 사이의 짧은 틈이 보인다.
RMS_FRAME_LENGTH = 512
# onset 검출기는 음이 끝날 때(릴리스)도 반응하므로, 음량이 실제로 이만큼(dB) 올라간
# onset 만 새 어택으로 인정한다.
ATTACK_RISE_DB = 3.0
NOISE_MARGIN_DB = 6.0

# 프레이즈 안 음높이 곡선 읽기
RAMP_STEP = 0.15  # 한 프레임에 이만큼(반음) 이상 움직이면 '이동 중'
SMOOTH_FRAMES = 9  # 비브라토(약 5~6Hz)를 누그러뜨리는 이동 평균 길이 (약 100ms)
STEADY_DRIFT = 0.35  # 평활 곡선이 ±3프레임 사이에 이보다 적게 변하면 '머무는' 음높이
GLIDE_MIN = 2.0  # 슬라이드 인/아웃으로 볼 최소 음높이 변화 (반음)
ARRIVAL_MIN = 8  # 글라이드로 도착한 음이 이보다(약 90ms) 짧고 곧바로 새로 친 음이 오면 "미끄러져 빠짐"
HAMMER_MAX = 4  # 해머링·풀링으로 볼 최대 음정 (반음). 손을 옮기지 않고 닿는 네 프렛


def detect_notes(
    y: np.ndarray,
    sr: int,
    *,
    fmin: str = "C2",
    fmax: str = "C7",
    min_note: float = 0.06,
    silence_db: float = -40.0,
) -> list[NoteEvent]:
    """단선율 오디오에서 음 목록을 뽑는다.

    min_note   : 이보다 짧은(초) 음은 잡음/글리산도로 보고 버린다.
    silence_db : 가장 큰 소리 대비 이보다 작은 프레임은 무음으로 본다.
    """
    frame_length = SHORT_FRAME_LENGTH if librosa.note_to_hz(fmin) >= 75 else FRAME_LENGTH
    f0, voiced_flag, _ = librosa.pyin(
        y,
        fmin=librosa.note_to_hz(fmin),
        fmax=librosa.note_to_hz(fmax),
        sr=sr,
        frame_length=frame_length,
        hop_length=HOP_LENGTH,
    )
    n = len(f0)
    rms = librosa.feature.rms(y=y, frame_length=RMS_FRAME_LENGTH, hop_length=HOP_LENGTH)[0]
    rms_db = librosa.amplitude_to_db(rms, ref=np.max)[:n]
    if len(rms_db) < n:
        rms_db = np.pad(rms_db, (0, n - len(rms_db)), constant_values=-80.0)

    # 잡음이 깔린 녹음이면 잡음 바닥보다 확실히 큰 소리만 음으로 본다.
    noise_floor = float(np.percentile(rms_db, 5))
    loud = rms_db > min(max(silence_db, noise_floor + NOISE_MARGIN_DB), -20.0)
    voiced = voiced_flag & ~np.isnan(f0) & loud
    midi = np.full(n, np.nan)
    midi[voiced] = librosa.hz_to_midi(f0[voiced])

    onset_frames = librosa.onset.onset_detect(
        y=y, sr=sr, hop_length=HOP_LENGTH, units="frames"
    )
    attack_mask = np.zeros(n, dtype=bool)
    for f in onset_frames[onset_frames < n]:
        before = rms_db[max(0, f - 4) : f + 1].min()
        after = rms_db[f : f + 5].max()
        attack_mask[f] = after - before >= ATTACK_RISE_DB

    min_frames = max(1, int(round(min_note * sr / HOP_LENGTH)))
    # pYIN 창은 앞쪽 음을 반 창만큼 미리 보고, onset 은 조금 늦게 잡힌다.
    # 그래서 음이 막 시작된 직후의 onset 은 같은 음의 어택으로 본다.
    attack_guard = max(min_frames, frame_length // HOP_LENGTH)
    # 순간 이동(해머링·풀링)도 pYIN 창 절반 남짓 동안은 중간 음높이로 번져 보인다.
    jump_max = frame_length // HOP_LENGTH // 2 + 2
    segments = _segment(midi, voiced, attack_mask, attack_guard)
    phrases = _phrases(segments, attack_mask, loud, rms_db, attack_guard)

    notes = []
    for k, (ps, pe) in enumerate(phrases):
        if pe - ps < min_frames:
            continue
        followed = k + 1 < len(phrases) and phrases[k + 1][0] - pe <= 3
        for s, e, pitch, tech in _read_phrase(midi[ps:pe], min_frames, jump_max, followed=followed):
            loudness = float(np.max(rms_db[ps + s : ps + e]))  # -40 ~ 0 dB
            velocity = int(np.clip(110 + loudness * 2, 30, 110))
            start, end = librosa.frames_to_time([ps + s, ps + e], sr=sr, hop_length=HOP_LENGTH)
            notes.append(NoteEvent(float(start), float(end), pitch, velocity, tech))
    return notes


def _segment(
    midi: np.ndarray, voiced: np.ndarray, attack_mask: np.ndarray, attack_guard: int
) -> list[tuple[int, int]]:
    """유성음 프레임을 [start, end) 구간들로 나눈다.

    새 음은 (1) 무음 뒤 소리가 시작될 때, (2) 음높이가 확실히 바뀔 때,
    (3) 같은 음높이라도 새 어택이 들어올 때(같은 음 반복) 시작된다.
    """
    segments: list[tuple[int, int]] = []
    start: int | None = None
    values: list[float] = []

    for i in range(len(midi)):
        if not voiced[i]:
            if start is not None:
                segments.append((start, i))
                start = None
            continue
        if start is None:
            start, values = i, [midi[i]]
            continue

        ref = float(np.median(values))
        ahead = midi[i : i + CHANGE_FRAMES]
        ahead = ahead[~np.isnan(ahead)]
        pitch_changed = (
            abs(midi[i] - ref) > PITCH_CHANGE_SEMITONES
            and ahead.size > 0
            and abs(float(np.median(ahead)) - ref) > PITCH_CHANGE_SEMITONES
        )
        re_attack = attack_mask[i] and i - start >= attack_guard
        if pitch_changed or re_attack:
            segments.append((start, i))
            start, values = i, [midi[i]]
        else:
            values.append(midi[i])

    if start is not None:
        segments.append((start, len(midi)))
    return segments


def _phrases(
    segments: list[tuple[int, int]],
    attack_mask: np.ndarray,
    loud: np.ndarray,
    rms_db: np.ndarray,
    attack_guard: int,
    max_gap: int = 3,
) -> list[tuple[int, int]]:
    """한 번 친 소리 단위로 구간을 묶는다.

    음높이가 바뀌어 나뉜 구간이라도 새 어택이 없고 소리가 이어져 있으면(pYIN 이 한두
    프레임 놓친 틈 포함) 왼손만으로 음을 바꾼 것이므로 같은 프레이즈다.
    onset 검출기가 놓치더라도 음량이 뚜렷이 다시 올라가면 새로 친 음으로 본다
    (앞 음이 울리는 중에 다시 뜯으면 onset 이 약하게 잡힌다).
    """
    phrases: list[tuple[int, int]] = []
    for s, e in segments:
        if phrases:
            ps, pe = phrases[-1]
            rise = rms_db[s : s + attack_guard].max() - rms_db[max(0, s - 4) : s + 2].min()
            attack = attack_mask[max(0, s - 2) : s + attack_guard].any() or rise >= ATTACK_RISE_DB
            if 0 <= s - pe <= max_gap and loud[pe:s].all() and not attack:
                phrases[-1] = (ps, e)
                continue
        phrases.append((s, e))
    return phrases


def _read_phrase(
    contour: np.ndarray, min_frames: int, jump_max: int, *, followed: bool = False
) -> list[tuple[int, int, int, Technique]]:
    """프레이즈 하나의 음높이 곡선 → [(시작, 끝, 음높이, 주법)] (프레임은 프레이즈 기준).

    jump_max: 두 음 사이 중간 음높이에 머문 프레임이 이 이하면 순간 이동(해머링·풀링),
              넘으면 미끄러짐(슬라이드·벤딩).
    followed: 이 프레이즈 바로 뒤에 새로 친 음이 붙어 있는지.
    """
    n = len(contour)
    frames = np.arange(n)
    known = ~np.isnan(contour)
    if not known.any():
        return []
    m = np.interp(frames, frames[known], contour[known])  # 끊긴 프레임은 앞뒤로 메운다

    # 1) 음높이가 움직이는 프레임을 경계로 조각낸다 (평활이 전이를 건너 번지지 않게).
    moving = np.abs(np.diff(m, prepend=m[0])) >= RAMP_STEP
    pieces, a = [], 0
    for i in range(n + 1):
        if i == n or moving[i]:
            if i > a:
                pieces.append((a, i))
            a = i + 1

    # 2) 조각마다 비브라토를 누그러뜨린 곡선에서 음높이가 머무는 구간을 찾는다.
    plateaus: list[list[int]] = []  # [시작, 끝]
    for a, b in pieces:
        piece = m[a:b]
        w = min(SMOOTH_FRAMES, len(piece))
        smooth = np.convolve(np.pad(piece, (w // 2, w - 1 - w // 2), mode="edge"), np.ones(w) / w, mode="valid")

        def steady(k: int) -> bool:
            return abs(smooth[min(len(piece) - 1, k + 3)] - smooth[max(0, k - 3)]) <= STEADY_DRIFT

        i = 0
        while i < len(piece):
            if not steady(i):
                i += 1
                continue
            j = i
            while j < len(piece) and steady(j) and abs(piece[j] - np.median(piece[i : j + 1])) <= 0.6:
                j += 1
            if j - i >= min(min_frames, 4):
                plateaus.append([a + i, a + j])
            i = max(j, i + 1)

    # 3) 같은 음높이로 이어진 머무는 구간은 하나로 (비브라토·인식 흔들림)
    def pitch_of(p: list[int]) -> int:
        return int(round(float(np.median(m[p[0] : p[1]]))))

    merged: list[list[int]] = []
    for p in plateaus:
        if merged and pitch_of(merged[-1]) == pitch_of(p):
            merged[-1][1] = p[1]
        else:
            merged.append(p)
    if not merged:
        return [(0, n, int(round(float(np.median(m)))), Technique())] if n >= min_frames else []

    def between(lo: float, hi: float, a: int, b: int) -> int:
        """a~b 프레임 중 두 음높이 사이(양끝 0.25반음 제외)에 있던 프레임 수 = 옮겨 가는 데 걸린 시간."""
        lo, hi = min(lo, hi), max(lo, hi)
        seg = m[a:b]
        return int(np.sum((seg > lo + 0.25) & (seg < hi - 0.25)))

    # 4) 음과 주법. 두 음의 경계는 옮겨 가는 구간의 한가운데로 잡는다.
    cuts = [0, *((merged[i - 1][1] + merged[i][0]) // 2 for i in range(1, len(merged))), n]
    notes = []
    for idx, (s, e) in enumerate(merged):
        pitch = pitch_of([s, e])
        link, slide_in, slide_out = "", "", ""
        start, end = cuts[idx], cuts[idx + 1]
        if idx:
            ps, pe = merged[idx - 1]
            prev = pitch_of([ps, pe])
            if between(prev, pitch, pe, s) > jump_max:
                link = "glide"
            elif abs(pitch - prev) <= HAMMER_MAX:
                link = "hammer" if pitch > prev else "pull"
            # 그보다 넓게 순간 이동했으면 어택이 약하게 잡혔을 뿐 새로 친 음으로 본다
        elif abs(m[s] - m[0]) >= GLIDE_MIN and between(m[0], m[s], 0, s) > jump_max:
            slide_in = "up" if m[s] > m[0] else "down"
        if idx == len(merged) - 1 and abs(m[-1] - m[e - 1]) >= GLIDE_MIN and between(m[e - 1], m[-1], e, n) > jump_max // 2:
            slide_out = "up" if m[-1] > m[e - 1] else "down"
        notes.append((start, end, pitch, Technique(link=link, slide_in=slide_in, slide_out=slide_out)))

    # 미끄러져 내려가다 잠깐 닿고 바로 다음 음을 새로 쳤다면, 도착 음은 따로 적지 않고
    # 앞 음의 "슬라이드 아웃"으로 본다 (다음 음으로 미끄러져 들어가는 연주).
    if followed and len(notes) >= 2:
        s, e, pitch, tech = notes[-1]
        ps, _, prev, prev_tech = notes[-2]
        if tech.link == "glide" and e - s < ARRIVAL_MIN:
            direction = "up" if pitch > prev else "down"
            notes[-2:] = [(ps, e, prev, Technique(link=prev_tech.link, slide_in=prev_tech.slide_in, slide_out=direction))]
    return notes
