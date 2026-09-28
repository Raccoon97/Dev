"""기타 한 대 편곡 (--mode arrange): 선율 + 베이스."""

from __future__ import annotations

import pytest
import soundfile as sf
from music21 import pitch

from music2score.arrange import combine, fold_bass, melody_octave_shift
from music2score.notes import NoteEvent, QuantizedNote
from music2score.synth import SCHOOL_BELL, SCHOOL_BELL_CHORDS, synthesize, synthesize_piano

SR = 22050


def test_melody_octave_shift_prefers_lower_on_ties():
    shift = [melody_octave_shift([NoteEvent(0, 1, p)]) for p in (57, 69, 75, 81)]
    assert shift == [12, 0, -12, -12]  # 75(D♯5)는 두 옥타브 한가운데 → 내린다


def test_fold_bass_and_keep_it_under_the_melody():
    assert [fold_bass(p) for p in (28, 36, 60)] == [40, 48, 48]
    melody = [QuantizedNote(0.0, 2.0, 50)]  # 선율이 낮게 내려온 순간
    out = combine(melody, [QuantizedNote(0.0, 2.0, 48)])  # C3 는 D3 와 붙고, 내린 C2 는 기타 음역 밖 → 뺀다
    assert [q.pitch for q in out] == [50]
    out = combine([QuantizedNote(0.0, 2.0, 67)], [QuantizedNote(0.0, 2.0, 48)])
    assert sorted(q.pitch for q in out) == [48, 67]


def test_arrange_school_bell(tmp_path):
    pytest.importorskip("basic_pitch")
    from music2score.arrange import arrange

    # 선율을 한 옥타브 높게 친 피아노 + 마디마다 근음을 2분음표로 두 번 치는 베이스
    high = [(pitch.Pitch(n).transpose(12).nameWithOctave, b) for n, b in SCHOOL_BELL]
    chords = [[p.replace("3", "4").replace("2", "3") for p in c] for c in SCHOOL_BELL_CHORDS]
    roots = ["C2" if c[0] == "C3" else "G1" for c in SCHOOL_BELL_CHORDS]
    sf.write(tmp_path / "melody.wav", synthesize_piano(high, chords, 100, SR), SR)
    sf.write(tmp_path / "bass.wav", synthesize([(r, 2) for r in roots for _ in range(2)], 100, SR, legato=0.95, timbre="guitar"), SR)

    result = arrange(tmp_path / "melody.wav", tmp_path / "bass.wav", tab="guitar")

    assert result.shift == -12 and result.dropped == 0
    melody = [q.pitch for q in result.qnotes if q.pitch >= 55]
    bass = [(q.offset, q.pitch) for q in result.qnotes if q.pitch < 55]
    assert melody == [pitch.Pitch(n).midi for n, _ in SCHOOL_BELL]  # 선율은 원래 높이로 그대로
    assert bass[:3] == [(0.0, 48), (2.0, 48), (4.0, 48)] and (12.0, 43) in bass  # 1·3박마다 근음 (C3, G2)
    assert "A|-3-------3-------|" in result.tab_text()
