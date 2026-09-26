"""합성한 오디오로 파이프라인 전체를 검증한다.

정답 악보를 알고 있는 멜로디를 직접 합성해서 넣고, 같은 악보가 나오는지 본다.
"""

from __future__ import annotations

import pytest
import soundfile as sf
from music21 import converter, key, pitch

from music2score import transcribe
from music2score.notes import NoteEvent, QuantizedNote
from music2score.poly import remove_ghosts
from music2score.rhythm import estimate_tempo, fit_grid, quantize
from music2score.score import export, spell
from music2score.synth import SCHOOL_BELL, SCHOOL_BELL_CHORDS, synthesize, synthesize_piano

SR = 22050

# 바장조, 8분음표·점음표·16분음표·B♭ 이 섞인 멜로디
F_MAJOR = [
    ("F4", 1), ("A4", 0.5), ("C5", 0.5), ("B-4", 1.5), ("A4", 0.5),
    ("G4", 0.5), ("A4", 0.5), ("B-4", 0.5), ("G4", 0.5), ("F4", 2),
    ("C5", 0.75), ("B-4", 0.25), ("A4", 1), ("G4", 1), ("E4", 1),
    ("F4", 3), (None, 1),
]

# 3/4 박자 (나비야 앞부분 비슷한 왈츠)
WALTZ = [
    ("G4", 1), ("E4", 1), ("E4", 1),
    ("F4", 1), ("D4", 1), ("D4", 1),
    ("C4", 1), ("D4", 1), ("E4", 1),
    ("F4", 1), ("G4", 1), ("G4", 1),
    ("G4", 3),
]


def expected(melody):
    notes, offset = [], 0.0
    for name, beats in melody:
        if name is not None:
            notes.append((offset, float(beats), pitch.Pitch(name).midi))
        offset += beats
    return notes


def got(result):
    return [(q.offset, q.length, q.pitch) for q in result.qnotes]


def write_wav(tmp_path, name, audio):
    path = tmp_path / f"{name}.wav"
    sf.write(path, audio, SR)
    return path


# ── 단선율 (mono) ─────────────────────────────────────────────


@pytest.mark.parametrize(
    "name, melody, bpm, options",
    [
        ("school_bell", SCHOOL_BELL, 100, {}),
        ("f_major", F_MAJOR, 90, {}),
        ("noise_vibrato", F_MAJOR, 90, dict(vibrato=0.3, noise=0.02)),
        ("fast", F_MAJOR, 132, dict(legato=0.95)),
        ("slow_legato", F_MAJOR, 72, dict(legato=1.0, vibrato=0.2)),
        ("detached", SCHOOL_BELL, 66, dict(legato=0.8)),
    ],
)
def test_mono_transcribes_exact_score(tmp_path, name, melody, bpm, options):
    path = write_wav(tmp_path, name, synthesize(melody, bpm, SR, **options))

    result = transcribe(path)

    assert got(result) == expected(melody)
    assert result.bpm == pytest.approx(bpm, rel=0.02)


def test_mono_detects_key(tmp_path):
    bell = transcribe(write_wav(tmp_path, "bell", synthesize(SCHOOL_BELL, 100, SR)))
    f_major = transcribe(write_wav(tmp_path, "f", synthesize(F_MAJOR, 90, SR)))

    assert (bell.key.tonic.name, bell.key.mode) == ("C", "major")
    assert (f_major.key.tonic.name, f_major.key.mode) == ("F", "major")
    # 바장조이므로 A♯ 이 아니라 B♭ 으로 적혀야 한다.
    names = [n.name for n in f_major.score.parts[0].recurse().notes]
    assert "B-" in names and "A#" not in names


def test_given_bpm_is_kept(tmp_path):
    path = write_wav(tmp_path, "bell", synthesize(SCHOOL_BELL, 100, SR))

    result = transcribe(path, bpm=100)

    assert result.bpm == 100
    assert got(result) == expected(SCHOOL_BELL)


def test_three_four_time(tmp_path):
    path = write_wav(tmp_path, "waltz", synthesize(WALTZ, 120, SR))

    result = transcribe(path, time_signature="3/4")

    assert got(result) == expected(WALTZ)
    measures = result.score.parts[0].getElementsByClass("Measure")
    assert len(measures) == 5
    assert measures[0].timeSignature.ratioString == "3/4"


def test_silent_audio_is_rejected(tmp_path):
    path = write_wav(tmp_path, "silence", [0.0] * SR)

    with pytest.raises(ValueError):
        transcribe(path)


# ── 내보내기 ─────────────────────────────────────────────────


def test_export_writes_readable_files(tmp_path):
    result = transcribe(write_wav(tmp_path, "bell", synthesize(SCHOOL_BELL, 100, SR)), title="학교종")

    files = export(result.score, tmp_path / "out", "bell")

    parsed = converter.parse(files["musicxml"])
    assert [n.pitch.midi for n in parsed.recurse().notes] == [p for _, _, p in expected(SCHOOL_BELL)]
    assert files["midi"].stat().st_size > 0
    page = files["html"].read_text(encoding="utf-8")
    assert "opensheetmusicdisplay" in page and "<title>학교종</title>" in page
    assert page.count("</script>") == 2  # 악보 XML 이 script 태그를 일찍 닫지 않는다


# ── 다성 (poly, basic-pitch 필요) ─────────────────────────────


def test_poly_piano_melody_and_chords(tmp_path):
    pytest.importorskip("basic_pitch")
    path = write_wav(tmp_path, "piano", synthesize_piano(SCHOOL_BELL, SCHOOL_BELL_CHORDS, 100, SR))

    result = transcribe(path, mode="poly")

    assert result.bpm == pytest.approx(100, rel=0.02)
    right, left = result.score.parts
    melody = [(n.offset, n.pitch.midi) for n in right.flatten().notes if n.isNote and not _tied_from_before(n)]
    assert [p for _, p in melody] == [p for _, _, p in expected(SCHOOL_BELL)]
    # 왼손 첫 화음은 도-미-솔
    first_chord = next(n for n in left.flatten().notes)
    assert {p.name for p in first_chord.pitches} == {"C", "E", "G"}


def _tied_from_before(n):
    return n.tie is not None and n.tie.type in ("continue", "stop")


# ── 단위 테스트 ──────────────────────────────────────────────


def test_quantize_fills_articulation_gaps_but_keeps_real_rests():
    beat = 0.5  # 120 BPM
    notes = [
        NoteEvent(0.00, 0.45, 60),  # 4분음표를 조금 짧게 → 틈 메움
        NoteEvent(0.50, 0.95, 62),  # 4분음표 뒤에 4분쉼표 → 쉼표 유지
        NoteEvent(1.50, 1.95, 64),
        NoteEvent(2.00, 3.80, 65),  # 마지막 온음표를 조금 짧게 → 마디 끝까지
    ]

    q = quantize(notes, bpm=60 / beat, t0=0.0, division=4)

    assert [(n.offset, n.length) for n in q] == [(0.0, 1.0), (1.0, 1.0), (3.0, 1.0), (4.0, 4.0)]


def test_tempo_from_onsets_and_grid_fit():
    onsets = [0.3 + i * 0.6 for i in range(16)]  # 100 BPM 4분음표

    bpm = estimate_tempo(onsets)
    fitted, t0 = fit_grid(onsets, bpm, division=4)

    assert fitted == pytest.approx(100, rel=0.01)
    assert t0 == pytest.approx(0.3, abs=0.02)


@pytest.mark.parametrize(
    "tonic, midi, name",
    [("F", 70, "B-"), ("E", 63, "D#"), ("d", 61, "C#"), ("g", 66, "F#"), ("C", 70, "B-")],
)
def test_spelling_follows_key(tonic, midi, name):
    assert spell(midi, key.Key(tonic)).name == name


def test_remove_ghosts_drops_quiet_overtones_but_keeps_real_octaves():
    notes = [
        NoteEvent(0.0, 1.0, 60, 100),
        NoteEvent(0.0, 1.0, 72, 50),  # 옥타브 위 약한 유령 → 제거
        NoteEvent(1.0, 2.0, 48, 90),
        NoteEvent(1.0, 2.0, 60, 85),  # 실제 옥타브 연주 → 유지
        NoteEvent(2.0, 2.1, 67, 30),  # 짧고 약한 잡음 → 제거
        NoteEvent(2.0, 3.0, 64, 95),
    ]

    kept = remove_ghosts(notes)

    assert [(n.start, n.pitch) for n in kept] == [(0.0, 60), (1.0, 48), (1.0, 60), (2.0, 64)]


def test_quantized_note_end():
    assert QuantizedNote(1.0, 0.5, 60).end == 1.5
