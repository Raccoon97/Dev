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
from dataclasses import dataclass, replace

import numpy as np
from music21 import articulations, clef, instrument, pitch, stream

from .notes import NoteEvent, QuantizedNote

MAX_SPAN = 4  # 한 화음에서 누르는 프렛 사이 최대 폭 (검지~새끼, 한 칸 벌리기 포함)
MAX_BEND = 3  # 기타에서 벤딩으로 볼 최대 폭 (반음). 온음 반(3반음)까지
HAND_WINDOW = 3  # 검지가 h 프렛에 있을 때 손 이동 없이 닿는 범위: h ~ h+3
SHIFT_COST = 2.0  # 포지션을 옮길 때마다 드는 고정 비용
LEGATO_STRING_COST = 8.0  # 해머링·풀링·슬라이드인데 줄이 바뀌는 운지 (사실상 금지)


@dataclass(frozen=True)
class Tuning:
    name: str
    label: str  # 사람이 읽는 이름
    strings: tuple[int, ...]  # 각 줄 개방현의 MIDI 번호. 가장 아래 줄(번호가 큰 줄)부터
    names: tuple[str, ...]  # 타브 왼쪽에 적는 줄 이름
    frets: int
    bends: bool = False  # 벤딩을 쓰는 악기인가 (미끄러짐을 벤딩으로 읽을지)

    def clef(self) -> clef.Clef:
        if self.name.startswith("bass"):
            return clef.Bass8vbClef()
        if self.name == "ukulele":
            return clef.TrebleClef()
        return clef.Treble8vbClef()  # 기타는 실제 소리보다 한 옥타브 높게 적는다

    def instrument(self) -> instrument.Instrument:
        if self.name.startswith("bass"):
            return instrument.ElectricBass()
        if self.name == "ukulele":
            return instrument.Ukulele()
        if self.name == "electric":
            return instrument.ElectricGuitar()
        return instrument.AcousticGuitar()

    def string_number(self, index: int) -> int:
        """strings 의 인덱스 → 줄 번호 (1번 줄 = 가장 높은 줄)."""
        return len(self.strings) - index


TUNINGS = {
    "guitar": Tuning("guitar", "기타 표준 (E A D G B E)", (40, 45, 50, 55, 59, 64), ("E", "A", "D", "G", "B", "e"), 22, True),
    "electric": Tuning("electric", "일렉기타 표준 (E A D G B E)", (40, 45, 50, 55, 59, 64), ("E", "A", "D", "G", "B", "e"), 22, True),
    "drop-d": Tuning("drop-d", "기타 드롭 D (D A D G B E)", (38, 45, 50, 55, 59, 64), ("D", "A", "D", "G", "B", "e"), 22, True),
    "bass": Tuning("bass", "베이스 4현 (E A D G)", (28, 33, 38, 43), ("E", "A", "D", "G"), 20),
    "bass5": Tuning("bass5", "베이스 5현 (B E A D G)", (23, 28, 33, 38, 43), ("B", "E", "A", "D", "G"), 20),
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
        fitted.append(replace(q, pitch=p))
    return fitted, moved


@dataclass
class _Fingering:
    notes: tuple[QuantizedNote, ...]
    places: tuple[tuple[int, int], ...]  # (strings 인덱스, 프렛)
    cost: float
    hands: tuple[int, ...]  # 이 운지를 잡을 수 있는 검지 위치들


def resolve_glides(notes: list[NoteEvent], *, allow_bends: bool) -> list[NoteEvent]:
    """미끄러지듯 이어진 음(glide)을 벤딩 또는 슬라이드로 정한다.

    소리만으로는 "7번 프렛을 치고 9번까지 밀어 올림(벤딩)"과 "7→9 슬라이드"가 비슷하다.
    기타에서 피킹 없이 위로 3반음 이내로 부드럽게 올라가는 건 대개 벤딩이므로 그렇게 보고,
    그 뒤 다시 원래 음으로 내려오면 릴리즈로 본다. 베이스처럼 벤딩을 잘 쓰지 않는
    악기이거나 그보다 크게/아래로 움직이면 슬라이드다.
    """
    out: list[NoteEvent] = []
    i = 0
    while i < len(notes):
        n = notes[i]
        nxt = notes[i + 1] if i + 1 < len(notes) else None
        if allow_bends and nxt and nxt.tech.link == "glide" and 0 < nxt.pitch - n.pitch <= MAX_BEND:
            j, release, last = i + 2, False, nxt
            after = notes[j] if j < len(notes) else None
            if after and after.tech.link == "glide" and after.pitch == n.pitch:
                release, last, j = True, after, j + 1
            tech = replace(n.tech, bend=nxt.pitch - n.pitch, release=release, slide_out=last.tech.slide_out)
            out.append(replace(n, end=last.end, tech=tech))
            i = j
            continue
        if n.tech.link == "glide":
            n = replace(n, tech=replace(n.tech, link="slide"))
        out.append(n)
        i += 1
    return out


@dataclass
class _Layer:
    notes: list[QuantizedNote]  # 이 시점에 동시에 치는 음들
    states: list[tuple[_Fingering, int]]  # (운지, 검지 위치)
    static: np.ndarray  # 상태마다 운지 자체의 비용
    hands: np.ndarray  # 상태마다 검지 위치
    strings: np.ndarray  # 단음이면 그 음의 줄 인덱스, 화음이면 -1


def assign_frets(qnotes: list[QuantizedNote], tuning: Tuning, capo: int = 0) -> list[TabNote]:
    """모든 음에 (줄, 프렛)을 정한다. 한 손으로 잡을 수 없는 화음의 음은 빠진다.

    상태 = (운지, 검지 위치). 음 하나하나는 가까워도 손이 계속 미끄러져 올라가면
    안 되므로, 손 위치가 바뀔 때마다 비용을 물린다. 개방현만 치는 순간에는 손이
    어디에 있어도 되므로 이전 위치를 그대로 이어 간다.
    해머링·풀링·슬라이드로 이어진 두 음은 같은 줄에서만 낼 수 있으므로 줄이 바뀌면
    큰 비용을 물리고, 슬라이드는 손을 옮기는 것 자체가 연주이므로 이동 비용을 거의 받지 않는다.
    """
    events = defaultdict(list)
    for q in qnotes:
        events[q.offset].append(q)
    ordered = sorted(events)
    # 다음 음과 슬라이드로 이어지는 음(출발 음)도 줄을 눌러야 하므로 개방현을 쓸 수 없다.
    leaves_by_slide = {
        id(events[a][0]) for a, b in zip(ordered, ordered[1:]) if len(events[b]) == 1 and events[b][0].tech.link == "slide"
    }

    all_hands = tuple(range(1, max(2, tuning.frets - capo - HAND_WINDOW + 1)))
    layers: list[_Layer] = []
    for t in ordered:
        notes = sorted(events[t], key=lambda q: q.pitch)
        cands = _candidates(notes, tuning, capo, all_hands, fretted=_needs_fret(notes, leaves_by_slide))
        if cands:
            states = [(f, h) for f in cands for h in f.hands]
            layers.append(
                _Layer(
                    notes,
                    states,
                    np.array([f.cost for f, _ in states]),
                    np.array([h for _, h in states], dtype=float),
                    np.array([f.places[0][0] if len(f.places) == 1 else -1 for f, _ in states]),
                )
            )
    if not layers:
        return []

    # 비터비: 각 상태까지 오는 가장 싼 길만 기억한다.
    cost = layers[0].static.copy()
    back = []
    for prev, cur in zip(layers, layers[1:]):
        shift = np.abs(prev.hands[:, None] - cur.hands[None, :])
        link = cur.notes[0].tech.link if len(cur.notes) == 1 and len(prev.notes) == 1 else ""
        if link == "slide":
            trans = 0.1 * shift
        else:
            trans = np.where(shift > 0, SHIFT_COST + 0.2 * shift, 0.0)
        if link in ("hammer", "pull", "slide"):
            trans = trans + np.where(prev.strings[:, None] != cur.strings[None, :], LEGATO_STRING_COST, 0.0)
        total = cost[:, None] + trans
        back.append(total.argmin(axis=0))
        cost = total.min(axis=0) + cur.static

    path = [int(cost.argmin())]
    for b in reversed(back):
        path.append(int(b[path[-1]]))
    path.reverse()

    result: list[TabNote] = []
    for layer, i in zip(layers, path):
        f, _ = layer.states[i]
        for q, (s, fret) in zip(f.notes, f.places):
            result.append(TabNote(q, tuning.string_number(s), fret))
    return _drop_impossible(result)


def _needs_fret(notes: list[QuantizedNote], leaves_by_slide: set[int]) -> bool:
    """벤딩·슬라이드는 줄을 눌러야 할 수 있는 주법이다."""
    if len(notes) != 1:
        return False
    tech = notes[0].tech
    return bool(tech.bend or tech.slide_in or tech.slide_out or tech.link == "slide" or id(notes[0]) in leaves_by_slide)


def _drop_impossible(tab: list[TabNote]) -> list[TabNote]:
    """그래도 다른 줄로 갈라졌거나 개방현에 붙은 주법 표시는 지운다 (칠 수 없는 표기 방지)."""
    out: list[TabNote] = []
    for i, t in enumerate(tab):
        tech = t.note.tech
        prev = out[-1] if out else None
        if tech.link in ("hammer", "pull", "slide") and (prev is None or prev.string != t.string or tab[i - 1].note.offset == t.note.offset):
            tech = replace(tech, link="")
        if t.fret == 0:
            tech = replace(tech, bend=0, release=False, slide_in="", slide_out="", link="" if tech.link == "slide" else tech.link)
        out.append(replace(t, note=replace(t.note, tech=tech)) if tech != t.note.tech else t)
    return out


def _candidates(
    notes: list[QuantizedNote], tuning: Tuning, capo: int, all_hands: tuple[int, ...], *, fretted: bool = False
) -> list[_Fingering]:
    """동시에 치는 음들을 잡는 모든 운지 후보. 안 되면 음을 하나씩 뺀다 (셋 이상은 가운데부터, 둘이면 아래 음)."""
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
        if fretted and all(any(f > 0 for _, f in o) for o in options):
            options = [[place for place in o if place[1] > 0] for o in options]
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
        # 셋 이상이면 가운데 음부터, 둘이면(편곡의 선율+베이스) 선율을 살리고 아래 음을 뺀다.
        drop = len(notes) // 2 if len(notes) > 2 else 0
        notes = notes[:drop] + notes[drop + 1 :]
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
    prev: TabNote | None = None
    for t in sorted(tab_notes, key=lambda t: (t.note.offset, t.string)):
        by_offset[round(t.note.offset / step)][t.string] = cell_text(t, prev)
        prev = t

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
    if any(t.note.tech.any for t in tab_notes):
        lines.append(LEGEND)
    return "\n".join(lines).rstrip() + "\n"


LEGEND = "h 해머링 · p 풀링 · / \\ 슬라이드 (앞뒤에 붙으면 미끄러져 들어옴/빠짐) · 7b9 벤딩 · r 릴리즈"


def cell_text(t: TabNote, prev: TabNote | None) -> str:
    """글자 타브 한 칸: 프렛 번호에 주법 기호를 붙인다. 예) h7, p5, /9, 7b9r7, 5\\"""
    tech = t.note.tech
    text = str(t.fret)
    if tech.link == "hammer":
        text = "h" + text
    elif tech.link == "pull":
        text = "p" + text
    elif tech.link == "slide":
        text = ("/" if prev is None or t.note.pitch > prev.note.pitch else "\\") + text
    if tech.slide_in:
        text = ("/" if tech.slide_in == "up" else "\\") + text
    if tech.bend:
        text += f"b{t.fret + tech.bend}" + (f"r{t.fret}" if tech.release else "")
    if tech.slide_out:
        text += "/" if tech.slide_out == "up" else "\\"
    return text


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

    # 다음 음이 해머링·풀링·슬라이드로 이어지는지 (시작 표시를 앞 음에 달아야 한다)
    ordered = sorted(tab_notes, key=lambda t: (t.note.offset, t.string))
    outgoing = {id(a): b.note.tech.link for a, b in zip(ordered, ordered[1:]) if b.note.tech.link}

    flat = tab_staff.flatten()  # 붙임줄로 나뉜 조각의 절대 위치는 평평하게 펼친 보표에서 재야 정확하다
    for el in flat.notes:
        offset = float(flat.elementOffset(el))
        end = offset + float(el.quarterLength)
        for n in el.notes if el.isChord else [el]:
            t = find(n.pitch.midi, offset)
            if t is None:
                el.articulations.append(articulations.Fingering("?"))
                continue
            first, last = abs(offset - t.note.offset) < 1e-6, abs(end - t.note.end) < 1e-6
            el.articulations.append(articulations.Fingering(f"{t.string}/{t.fret}" + _tokens(t, first, last, outgoing.get(id(t)))))


def _tokens(t: TabNote, first: bool, last: bool, outgoing: str | None) -> str:
    """주법을 임시 표기로: ;he(해머링 끝) ;hs(해머링 시작) ;b2(벤딩 2반음) ;r(릴리즈) ;si+(슬라이드 인 위로) …

    붙임줄로 나뉜 음은 첫 조각에 들어오는 주법을, 마지막 조각에 나가는 주법을 단다.
    """
    tech, tokens = t.note.tech, []
    code = {"hammer": "h", "pull": "p", "slide": "s"}
    if first:
        if tech.link in code:
            tokens.append(code[tech.link] + "e")
        if tech.slide_in:
            tokens.append("si" + ("+" if tech.slide_in == "up" else "-"))
        if tech.bend:
            tokens.append(f"b{tech.bend}")
            if tech.release:
                tokens.append("r")
    if last:
        if outgoing in code:
            tokens.append(code[outgoing] + "s")
        if tech.slide_out:
            tokens.append("so" + ("+" if tech.slide_out == "up" else "-"))
    return "".join(";" + x for x in tokens)


def add_tab_details(xml: str, tuning: Tuning, capo: int = 0) -> str:
    """music21 이 쓴 MusicXML 에 줄/프렛·주법 표기와 조율 정보(staff-tuning)를 넣는다."""
    xml = re.sub(r"<technical>\s*<fingering[^>]*>(\d+)/(\d+)([^<]*)</fingering>\s*</technical>", _technical, xml)
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


def osmd_bends(xml: str) -> str:
    """HTML 뷰어(OpenSheetMusicDisplay)용: bend-alter 를 반음 수 대신 "도착 프렛"으로 바꾼다.

    MusicXML 표준에서 bend-alter 는 반음 수지만 OSMD 는 이를 도착 프렛 번호로 읽고
    (bend-alter - 프렛) 으로 "1/2", "Full" 을 붙인다. 저장하는 .musicxml 은 표준 그대로 두고
    뷰어에 넣는 사본만 고친다.
    """

    def fix(m: re.Match) -> str:
        block = m.group(0)
        fret = re.search(r"<fret>(\d+)</fret>", block)
        if not fret:
            return block
        f = int(fret.group(1))
        return re.sub(r"<bend-alter>(-?\d+)</bend-alter>", lambda b: f"<bend-alter>{f + abs(int(b.group(1)))}</bend-alter>", block)

    return re.sub(r"<technical>.*?</technical>", fix, xml, flags=re.S)


def _technical(match: re.Match) -> str:
    """임시 표기 → MusicXML 표준 요소.

    <technical> 안: 줄·프렛, 해머링/풀링(hammer-on/pull-off), 벤딩(bend)
    <notations> 안: 슬라이드(slide), 해머링·풀링의 이음줄(slur),
                    슬라이드 인/아웃(scoop·plop / doit·falloff)
    """
    string, fret, raw = match.group(1), match.group(2), match.group(3)
    tokens = [x for x in raw.split(";") if x]
    technical = [f"<string>{string}</string>", f"<fret>{fret}</fret>"]
    notations, marks = [], []
    names = {"h": ("hammer-on", "H"), "p": ("pull-off", "P")}
    for x in tokens:  # 끝(e)을 시작(s)보다 먼저 적어야 한 음에서 끝나고 다시 시작하는 5h7p5 가 맞다
        if x in ("he", "pe"):
            technical.append(f'<{names[x[0]][0]} number="1" type="stop"/>')
            notations.append('<slur number="1" type="stop"/>')
        elif x == "se":
            notations.append('<slide line-type="solid" number="1" type="stop"/>')
    for x in tokens:
        if x in ("hs", "ps"):
            tag, letter = names[x[0]]
            technical.append(f'<{tag} number="1" type="start">{letter}</{tag}>')
            notations.append('<slur number="1" type="start"/>')
        elif x == "ss":
            notations.append('<slide line-type="solid" number="1" type="start"/>')
        elif x.startswith("b"):
            amount = int(x[1:])
            technical.append(f"<bend><bend-alter>{amount}</bend-alter></bend>")
            if "r" in tokens:
                technical.append(f"<bend><bend-alter>{-amount}</bend-alter><release/></bend>")
        elif x.startswith("si"):
            marks.append("<scoop/>" if x.endswith("+") else "<plop/>")
        elif x.startswith("so"):
            marks.append("<doit/>" if x.endswith("+") else "<falloff/>")
    out = "<technical>" + "".join(technical) + "</technical>" + "".join(notations)
    if marks:
        out += "<articulations>" + "".join(marks) + "</articulations>"
    return out
