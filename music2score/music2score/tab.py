"""타브(TAB) 악보 — 음마다 어느 줄의 몇 번 프렛을 누를지 정하고 그린다.

기타에서는 같은 음을 여러 자리에서 낼 수 있다 (E4 = 1번 줄 개방현, 2번 줄 5프렛,
3번 줄 9프렛 …). 음 하나씩 따로 고르면 손이 지판 위를 널뛰므로, 곡 전체에서
"손 이동 + 높은 포지션 + 벌리기 어려운 운지" 비용이 가장 작은 경로를
동적 계획법(비터비)으로 찾는다.
"""

from __future__ import annotations

import itertools
import math
import re
from collections import defaultdict
from dataclasses import dataclass

import numpy as np
from music21 import articulations, clef, instrument, pitch, stream

from .notes import QuantizedNote

MAX_SPAN = 4  # 한 화음에서 누르는 프렛 사이 최대 폭 (검지~새끼, 한 칸 벌리기 포함)
HAND_WINDOW = 3  # 검지가 h 프렛에 있을 때 손 이동 없이 닿는 범위: h ~ h+3
SHIFT_COST = 2.0  # 포지션을 옮길 때마다 드는 고정 비용


@dataclass(frozen=True)
class Tuning:
    name: str
    label: str  # 사람이 읽는 이름
    strings: tuple[int, ...]  # 각 줄 개방현의 MIDI 번호. 가장 아래 줄(번호가 큰 줄)부터
    names: tuple[str, ...]  # 타브 왼쪽에 적는 줄 이름
    frets: int

    def clef(self) -> clef.Clef:
        if self.name == "bass":
            return clef.Bass8vbClef()
        if self.name == "ukulele":
            return clef.TrebleClef()
        return clef.Treble8vbClef()  # 기타는 실제 소리보다 한 옥타브 높게 적는다

    def instrument(self) -> instrument.Instrument:
        if self.name == "bass":
            return instrument.ElectricBass()
        if self.name == "ukulele":
            return instrument.Ukulele()
        return instrument.AcousticGuitar()

    def string_number(self, index: int) -> int:
        """strings 의 인덱스 → 줄 번호 (1번 줄 = 가장 높은 줄)."""
        return len(self.strings) - index


TUNINGS = {
    "guitar": Tuning("guitar", "기타 표준 (E A D G B E)", (40, 45, 50, 55, 59, 64), ("E", "A", "D", "G", "B", "e"), 22),
    "drop-d": Tuning("drop-d", "기타 드롭 D (D A D G B E)", (38, 45, 50, 55, 59, 64), ("D", "A", "D", "G", "B", "e"), 22),
    "bass": Tuning("bass", "베이스 4현 (E A D G)", (28, 33, 38, 43), ("E", "A", "D", "G"), 20),
    "ukulele": Tuning("ukulele", "우쿨렐레 (G C E A)", (67, 60, 64, 69), ("G", "C", "E", "A"), 15),
}


@dataclass(frozen=True)
class TabNote:
    note: QuantizedNote
    string: int  # 줄 번호 (1 = 가장 높은 줄)
    fret: int  # 카포 기준 프렛 번호


def fit_range(
    qnotes: list[QuantizedNote], tuning: Tuning, capo: int = 0, *, drop: bool = False
) -> tuple[list[QuantizedNote], int]:
    """악기로 낼 수 없는 높이의 음을 옥타브 단위로 옮긴다 (drop 이면 버린다). 처리한 음 개수도 돌려준다.

    노래 멜로디를 기타로 옮길 땐 옥타브 이동이 맞지만, 그 악기를 녹음한 화음에서
    음역 밖 음이 나왔다면 잘못 인식한 음이므로 버리는 게 맞다.
    """
    low = min(tuning.strings) + capo
    high = max(tuning.strings) + tuning.frets
    fitted, moved = [], 0
    for q in qnotes:
        if drop and not low <= q.pitch <= high:
            moved += 1
            continue
        p = q.pitch
        while p < low:
            p += 12
        while p > high:
            p -= 12
        moved += p != q.pitch
        fitted.append(QuantizedNote(q.offset, q.length, p, q.velocity))
    return fitted, moved


@dataclass
class _Fingering:
    notes: tuple[QuantizedNote, ...]
    places: tuple[tuple[int, int], ...]  # (strings 인덱스, 프렛)
    cost: float
    hands: tuple[int, ...]  # 이 운지를 잡을 수 있는 검지 위치들


def assign_frets(qnotes: list[QuantizedNote], tuning: Tuning, capo: int = 0) -> list[TabNote]:
    """모든 음에 (줄, 프렛)을 정한다. 한 손으로 잡을 수 없는 화음의 음은 빠진다.

    상태 = (운지, 검지 위치). 음 하나하나는 가까워도 손이 계속 미끄러져 올라가면
    안 되므로, 손 위치가 바뀔 때마다 비용을 물린다. 개방현만 치는 순간에는 손이
    어디에 있어도 되므로 이전 위치를 그대로 이어 간다.
    """
    events = defaultdict(list)
    for q in qnotes:
        events[q.offset].append(q)

    all_hands = tuple(range(1, max(2, tuning.frets - capo - HAND_WINDOW + 1)))
    layers = []
    for t in sorted(events):
        cands = _candidates(sorted(events[t], key=lambda q: q.pitch), tuning, capo, all_hands)
        if cands:
            states = [(f, h) for f in cands for h in f.hands]
            layers.append(
                (states, np.array([f.cost for f, _ in states]), np.array([h for _, h in states], dtype=float))
            )
    if not layers:
        return []

    # 비터비: 각 상태까지 오는 가장 싼 길만 기억한다.
    cost = layers[0][1].copy()
    back = []
    for (_, _, ha), (_, static, hb) in zip(layers, layers[1:]):
        shift = np.abs(ha[:, None] - hb[None, :])
        total = cost[:, None] + np.where(shift > 0, SHIFT_COST + 0.2 * shift, 0.0)
        back.append(total.argmin(axis=0))
        cost = total.min(axis=0) + static

    path = [int(cost.argmin())]
    for b in reversed(back):
        path.append(int(b[path[-1]]))
    path.reverse()

    result = []
    for (states, _, _), i in zip(layers, path):
        f, _ = states[i]
        for q, (s, fret) in zip(f.notes, f.places):
            result.append(TabNote(q, tuning.string_number(s), fret))
    return result


def _candidates(
    notes: list[QuantizedNote], tuning: Tuning, capo: int, all_hands: tuple[int, ...]
) -> list[_Fingering]:
    """동시에 치는 음들을 잡는 모든 운지 후보. 안 되면 가운데 음부터 하나씩 뺀다."""
    opens = [s + capo for s in tuning.strings]
    max_fret = tuning.frets - capo
    while notes:
        options = [
            sorted(
                ((i, q.pitch - o) for i, o in enumerate(opens) if 0 <= q.pitch - o <= max_fret),
                key=lambda place: place[1],
            )[:5]  # 음마다 낮은 자리 5곳까지만 (조합 폭발 방지)
            for q in notes
        ]
        found = []
        for places in itertools.product(*options):
            if len({s for s, _ in places}) < len(places):
                continue  # 한 줄에서 두 음을 동시에 낼 수 없다
            pressed = [f for _, f in places if f > 0]
            span = max(pressed) - min(pressed) if pressed else 0
            if span > MAX_SPAN:
                continue
            if pressed:
                hands = tuple(range(max(1, max(pressed) - HAND_WINDOW), min(pressed) + 1)) or (min(pressed),)
            else:
                hands = all_hands  # 개방현만: 손은 어디 있어도 된다
            cost = 0.3 * span + 0.1 * sum(pressed)  # 벌리기 어려울수록, 높은 포지션일수록 비싸다
            found.append(_Fingering(tuple(notes), places, cost, hands))
        if found:
            return found
        notes = notes[: len(notes) // 2] + notes[len(notes) // 2 + 1 :]
    return []


# ── 글자 타브 (.txt) ─────────────────────────────────────────


def render_ascii(
    tab_notes: list[TabNote],
    tuning: Tuning,
    *,
    bar_length: float = 4.0,
    capo: int = 0,
    title: str = "",
    bpm: float | None = None,
    time_signature: str = "4/4",
    width: int = 78,
) -> str:
    """인터넷에서 흔히 쓰는 글자 타브를 만든다. 가로 간격이 박자에 비례한다.

        e|-----0---|
        B|-1-3-----|
    """
    info = [tuning.label, time_signature]
    if bpm:
        info.insert(1, f"♩ = {bpm:.0f}")
    if capo:
        info.append(f"카포 {capo}프렛")
    lines = [title, " | ".join(info), ""] if title else [" | ".join(info), ""]
    if not tab_notes:
        return "\n".join(lines)

    # 모든 음 시작이 떨어지는 가장 굵은 격자 (4분음표만 있으면 8분 간격으로 그린다)
    step = next(
        (r for r in (0.5, 0.25, 0.125) if all(abs(t.note.offset / r - round(t.note.offset / r)) < 1e-6 for t in tab_notes)),
        0.125,
    )
    by_offset = defaultdict(dict)
    for t in tab_notes:
        by_offset[round(t.note.offset / step)][t.string] = str(t.fret)

    n_strings = len(tuning.strings)
    label_w = max(len(n) for n in tuning.names)
    cols = int(round(bar_length / step))
    last = max(t.note.end for t in tab_notes)
    n_bars = max(1, math.ceil(last / bar_length - 1e-9))

    bars = []  # 마디마다 줄별 문자열
    for b in range(n_bars):
        rows = ["-"] * n_strings
        for c in range(cols):
            cells = by_offset.get(b * cols + c, {})
            w = max((len(v) for v in cells.values()), default=1)
            for s in range(1, n_strings + 1):
                rows[s - 1] += cells.get(s, "").ljust(w, "-") + "-"
        bars.append(rows)

    system: list[list[str]] = []
    first_bar = 1
    for b, rows in enumerate(bars, start=1):
        used = label_w + 1 + sum(len(r[0]) + 1 for r in system)
        if system and used + len(rows[0]) + 1 > width:
            lines += _system(system, tuning, label_w, first_bar)
            system, first_bar = [], b
        system.append(rows)
    lines += _system(system, tuning, label_w, first_bar)
    return "\n".join(lines).rstrip() + "\n"


def _system(bars: list[list[str]], tuning: Tuning, label_w: int, first_bar: int) -> list[str]:
    out = [" " * (label_w + 1) + str(first_bar)]
    for s in range(1, len(tuning.strings) + 1):  # 1번 줄(가장 높은 줄)이 맨 위
        name = tuning.names[len(tuning.strings) - s]
        out.append(name.ljust(label_w) + "|" + "|".join(bar[s - 1] for bar in bars) + "|")
    return out + [""]


# ── MusicXML 타브 보표 ────────────────────────────────────────


def attach_frets(tab_staff: stream.Stream, tab_notes: list[TabNote]) -> None:
    """TAB 보표의 음표마다 줄/프렛을 단다.

    music21 은 화음 안 음마다 줄/프렛을 따로 내보내지 못해서, 음마다 따로 내보내는
    운지 번호(fingering) 자리에 "줄/프렛" 을 적어 두고 add_tab_details() 에서 바꾼다.
    """
    by_pitch = defaultdict(list)
    for t in tab_notes:
        by_pitch[t.note.pitch].append(t)

    def find(midi: int, offset: float) -> TabNote | None:
        for t in by_pitch[midi]:
            if t.note.offset - 1e-6 <= offset < t.note.end - 1e-6:
                return t
        return None

    for el in tab_staff.recurse().notes:
        offset = float(el.getOffsetInHierarchy(tab_staff))
        for n in el.notes if el.isChord else [el]:
            t = find(n.pitch.midi, offset)
            el.articulations.append(articulations.Fingering(f"{t.string}/{t.fret}" if t else "?"))


def add_tab_details(xml: str, tuning: Tuning, capo: int = 0) -> str:
    """music21 이 쓴 MusicXML 에 줄/프렛 표기와 조율 정보(staff-tuning)를 넣는다."""
    xml = re.sub(
        r"<fingering[^>]*>(\d+)/(\d+)</fingering>",
        r"<string>\1</string>\n            <fret>\2</fret>",
        xml,
    )
    xml = re.sub(r"<technical>\s*<fingering[^>]*>\?</fingering>\s*</technical>", "", xml)

    tunings = []
    for line, midi in enumerate(tuning.strings, start=1):  # line 1 = 맨 아래 줄
        p = pitch.Pitch(midi=midi)
        alter = f"<tuning-alter>{int(p.alter)}</tuning-alter>" if p.alter else ""
        tunings.append(
            f'<staff-tuning line="{line}"><tuning-step>{p.step}</tuning-step>{alter}'
            f"<tuning-octave>{p.octave}</tuning-octave></staff-tuning>"
        )
    details = (
        f'<staff-details number="2"><staff-lines>{len(tuning.strings)}</staff-lines>'
        + "".join(tunings)
        + (f"<capo>{capo}</capo>" if capo else "")
        + "</staff-details>"
    )
    return re.sub(r'(<clef number="2">.*?</clef>)', r"\1" + details, xml, count=1, flags=re.S)
