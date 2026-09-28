"""타브 악보: 운지 선택, 글자 타브, MusicXML TAB 보표, 기타 소리 → 타브."""

from __future__ import annotations

import pytest
import soundfile as sf
from music21 import converter, pitch

from music2score import transcribe
from music2score.notes import NoteEvent, QuantizedNote
from music2score.poly import merge_strums
from music2score.score import export
from music2score.synth import synthesize, synthesize_chords
from music2score.tab import TUNINGS, assign_frets, fit_range, render_ascii

SR = 22050

# E 단조 펜타토닉 기타 리프
RIFF = [
    ("E3", 0.5), ("G3", 0.5), ("A3", 1), ("B3", 0.5), ("D4", 0.5), ("E4", 1),
    ("D4", 0.5), ("B3", 0.5), ("A3", 1), ("G3", 1), ("E3", 2),
]


def midi(name: str) -> int:
    return pitch.Pitch(name).midi


def shape(tab_notes, tuning) -> str:
    """운지를 기타 코드표 표기로: 가장 낮은 줄부터, 안 치는 줄은 x (예: C = x32010)."""
    frets = {t.string: t.fret for t in tab_notes}
    return "".join(str(frets.get(s, "x")) for s in range(len(tuning.strings), 0, -1))


def arrange(names, tuning="guitar", capo=0):
    notes = [QuantizedNote(0.0, 4.0, midi(n)) for n in names]
    return shape(assign_frets(notes, TUNINGS[tuning], capo), TUNINGS[tuning])


# ── 운지 선택 ────────────────────────────────────────────────


@pytest.mark.parametrize(
    "chord, notes, expected",
    [
        ("C", ["C3", "E3", "G3", "C4", "E4"], "x32010"),
        ("G", ["G2", "B2", "D3", "G3", "B3", "G4"], "320003"),
        ("D", ["D3", "A3", "D4", "F#4"], "xx0232"),
        ("Am", ["A2", "E3", "A3", "C4", "E4"], "x02210"),
        ("E", ["E2", "B2", "E3", "G#3", "B3", "E4"], "022100"),
        ("F", ["F2", "C3", "F3", "A3", "C4", "F4"], "133211"),  # 바레 코드
    ],
)
def test_guitar_chords_get_standard_shapes(chord, notes, expected):
    assert arrange(notes) == expected


def test_capo_frets_are_relative_to_capo():
    # 카포 2 에서 D 코드는 C 모양으로 잡는다.
    assert arrange(["D3", "F#3", "A3", "D4", "F#4"], capo=2) == "x32010"


def test_ukulele_and_bass():
    assert arrange(["G4", "C4", "E4", "C5"], "ukulele") == "0003"  # 우쿨렐레 C
    assert arrange(["E1", "B1", "E2"], "bass") == "022x"


def test_melody_stays_in_one_position():
    scale = ["G3", "A3", "B3", "C4", "D4", "E4", "F#4", "G4", "F#4", "E4", "D4", "C4", "B3", "A3", "G3"]
    notes = [QuantizedNote(i * 0.5, 0.5, midi(n)) for i, n in enumerate(scale)]
    tuning = TUNINGS["guitar"]

    tab = assign_frets(notes, tuning)

    assert all(tuning.strings[len(tuning.strings) - t.string] + t.fret == t.note.pitch for t in tab)
    assert max(t.fret for t in tab) <= 4  # 1포지션에서 해결


def test_high_melody_shifts_position_rarely():
    scale = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5", "D5", "E5", "F5", "G5"]
    tab = assign_frets([QuantizedNote(i * 0.5, 0.5, midi(n)) for i, n in enumerate(scale)], TUNINGS["guitar"])
    pressed = [t.fret for t in tab if t.fret]

    # 한 줄로 한 칸씩 미끄러지지 않고, 몇 개의 포지션 안에서 친다.
    jumps = sum(abs(a - b) > 3 for a, b in zip(pressed, pressed[1:]))
    assert jumps <= 2


def test_fit_range_moves_or_drops_out_of_range_notes():
    notes = [QuantizedNote(0.0, 1.0, midi("C5")), QuantizedNote(1.0, 1.0, midi("C2"))]
    bass = TUNINGS["bass"]

    moved, n_moved = fit_range(notes, bass)
    dropped, n_dropped = fit_range(notes, bass, drop=True)

    assert [q.pitch for q in moved] == [midi("C4"), midi("C2")] and n_moved == 1
    assert [q.pitch for q in dropped] == [midi("C2")] and n_dropped == 1


def test_merge_strums_aligns_chord_onsets():
    strum = [NoteEvent(0.50 + i * 0.02, 2.0, p) for i, p in enumerate((48, 52, 55, 60, 64))]
    strum.append(NoteEvent(0.48, 0.55, 48))  # 스트로크 도중 끊겨 두 번 잡힌 C3
    later = NoteEvent(1.0, 2.0, 67)

    merged = merge_strums(strum + [later])

    starts = {round(n.start, 3) for n in merged if n.pitch != 67}
    assert len(starts) == 1 and [n.pitch for n in merged].count(48) == 1
    assert later in merged


# ── 글자 타브 ────────────────────────────────────────────────


def test_render_ascii():
    notes = [QuantizedNote(0.0, 1.0, midi("G4")), QuantizedNote(1.0, 1.0, midi("A4")), QuantizedNote(2.0, 2.0, midi("D4"))]
    tuning = TUNINGS["guitar"]

    text = render_ascii(assign_frets(notes, tuning), tuning, title="t", bpm=100)

    assert text == (
        "t\n"
        "기타 표준 (E A D G B E) | ♩ = 100 | 4/4\n"
        "\n"
        "  1\n"
        "e|-3---5-----------|\n"
        "B|---------3-------|\n"
        "G|-----------------|\n"
        "D|-----------------|\n"
        "A|-----------------|\n"
        "E|-----------------|\n"
    )


# ── 오디오 → 타브 ────────────────────────────────────────────


def test_guitar_riff_to_tab(tmp_path):
    path = tmp_path / "riff.wav"
    sf.write(path, synthesize(RIFF, 96, SR, legato=1.0, timbre="guitar"), SR)

    result = transcribe(path, tab="guitar")

    offsets, expected = 0.0, []
    for name, beats in RIFF:
        expected.append((offsets, float(beats), midi(name)))
        offsets += beats
    assert [(q.offset, q.length, q.pitch) for q in result.qnotes] == expected
    assert [(t.string, t.fret) for t in result.tab_notes][:6] == [(4, 2), (3, 0), (3, 2), (2, 0), (2, 3), (1, 0)]
    assert "e|" in result.tab_text() and result.dropped == 0


def test_tab_musicxml_has_strings_frets_and_tuning(tmp_path):
    path = tmp_path / "riff.wav"
    sf.write(path, synthesize(RIFF, 96, SR, legato=1.0, timbre="guitar"), SR)
    result = transcribe(path, tab="guitar", capo=0)

    files = export(result.score, tmp_path / "out", "riff", tuning=result.tuning)

    xml = files["musicxml"].read_text(encoding="utf-8")
    assert xml.count("<fret>") == xml.count("<string>") >= len(result.qnotes)
    assert xml.count("<staff-tuning") == 6 and "<sign>TAB</sign>" in xml
    assert "<fingering" not in xml  # 임시로 쓴 운지 번호가 남으면 안 된다
    parsed = converter.parse(files["musicxml"])
    assert len(parsed.parts) == 2


def test_strummed_chords_to_guitar_tab(tmp_path):
    pytest.importorskip("basic_pitch")
    chords = [
        (["C3", "E3", "G3", "C4", "E4"], "x32010"),
        (["G2", "B2", "D3", "G3", "B3", "G4"], "320003"),
        (["A2", "E3", "A3", "C4", "E4"], "x02210"),
        (["F2", "C3", "F3", "A3", "C4", "F4"], "133211"),
    ]
    path = tmp_path / "strum.wav"
    sf.write(path, synthesize_chords([(c, 4) for c, _ in chords], 90, SR), SR)

    # 화음이 마디마다 하나뿐이면 템포를 정할 근거가 없어 bpm 을 알려 준다.
    result = transcribe(path, mode="poly", tab="guitar", bpm=90)

    tuning = TUNINGS["guitar"]
    for bar, (_, expected) in enumerate(chords):
        on_beat = [t for t in result.tab_notes if t.note.offset == bar * 4]
        got = shape(on_beat, tuning)
        assert len(on_beat) >= 4, got
        assert all(g in ("x", e) for g, e in zip(got, expected)), f"{got} != {expected}"
