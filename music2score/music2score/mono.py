"""단선율(멜로디 한 줄) 음 검출.

pYIN 으로 프레임마다 기본 주파수(f0)를 추정한 뒤, 음높이가 바뀌는 지점과
어택(onset)을 기준으로 프레임들을 음 단위로 묶는다.
노래, 허밍, 휘파람, 리코더/바이올린 같은 단선율 악기에 적합하다.
"""

from __future__ import annotations

import librosa
import numpy as np

from .notes import NoteEvent

HOP_LENGTH = 256
FRAME_LENGTH = 2048

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
    f0, voiced_flag, _ = librosa.pyin(
        y,
        fmin=librosa.note_to_hz(fmin),
        fmax=librosa.note_to_hz(fmax),
        sr=sr,
        frame_length=FRAME_LENGTH,
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
    attack_guard = max(min_frames, FRAME_LENGTH // HOP_LENGTH)
    segments = _segment(midi, voiced, attack_mask, attack_guard)
    segments = [(s, e) for s, e in segments if e - s >= min_frames]
    segments = _merge_dropouts(segments, midi, attack_mask, loud)

    notes = []
    for s, e in segments:
        pitch = int(round(float(np.nanmedian(midi[s:e]))))
        loudness = float(np.max(rms_db[s:e]))  # -40 ~ 0 dB
        velocity = int(np.clip(110 + loudness * 2, 30, 110))
        start, end = librosa.frames_to_time([s, e], sr=sr, hop_length=HOP_LENGTH)
        notes.append(NoteEvent(float(start), float(end), pitch, velocity))
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


def _merge_dropouts(
    segments: list[tuple[int, int]],
    midi: np.ndarray,
    attack_mask: np.ndarray,
    loud: np.ndarray,
    max_gap: int = 3,
) -> list[tuple[int, int]]:
    """pYIN 이 한두 프레임 놓쳐서 끊긴 같은 음을 다시 잇는다.

    소리가 계속 나고 있었고(무음 틈이 아님) 새 어택도 없을 때만 잇는다.
    """
    merged: list[tuple[int, int]] = []
    for s, e in segments:
        if merged:
            ps, pe = merged[-1]
            same_pitch = round(float(np.nanmedian(midi[ps:pe]))) == round(
                float(np.nanmedian(midi[s:e]))
            )
            attack = attack_mask[max(0, s - 2) : s + 5].any()
            if same_pitch and s - pe <= max_gap and loud[pe:s].all() and not attack:
                merged[-1] = (ps, e)
                continue
        merged.append((s, e))
    return merged
