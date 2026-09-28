"""화음·반주 속에서 선율 한 줄 뽑기 (--mode melody)."""

from __future__ import annotations

import numpy as np
import pytest
import soundfile as sf
from music21 import pitch

from music2score import transcribe
from music2score.poly import LOWEST_KEY, melody_from_posteriors
from music2score.synth import SCHOOL_BELL, SCHOOL_BELL_CHORDS, synthesize_piano
from music2score.tab import TUNINGS

SR = 22050


def test_viterbi_picks_the_melody_over_chords_and_ghosts():
    fps, beat = 86, 43  # 프레임, 한 박 = 0.5초
    melody = [72, 74, 76, 74, 72, 67]  # C5 D5 E5 D5 C5 G4
    note = np.zeros((beat * len(melody), 88))
    onset = np.zeros_like(note)
    for key in (48, 52, 55):  # 계속 울리는 반주 화음 C3 E3 G3
        note[:, key - LOWEST_KEY] = 0.7
    for i, key in enumerate(melody):
        note[i * beat : (i + 1) * beat - 2, key - LOWEST_KEY] = 0.8
        onset[i * beat, key - LOWEST_KEY] = 0.9
    note[10:20, 93 - LOWEST_KEY] = 0.1  # 아주 약한 높은 잔음 (A6)

    notes = melody_from_posteriors(note, onset, low=40, high=96, fps=fps)

    assert [n.pitch for n in notes] == melody


def test_melody_from_piano_to_electric_guitar_tab(tmp_path):
    pytest.importorskip("basic_pitch")
    path = tmp_path / "piano.wav"
    sf.write(path, synthesize_piano(SCHOOL_BELL, SCHOOL_BELL_CHORDS, 100, SR), SR)

    result = transcribe(path, mode="melody", tab="electric")

    expected, offset = [], 0.0
    for name, beats in SCHOOL_BELL:
        expected.append((offset, float(beats), pitch.Pitch(name).midi))
        offset += beats
    assert [(q.offset, q.length, q.pitch) for q in result.qnotes] == expected  # 반주 화음은 하나도 섞이지 않는다
    assert result.tuning.name == "electric" and "e|-3---3---5---5---|" in result.tab_text()


def test_electric_guitar_allows_bends_bass_does_not():
    assert TUNINGS["electric"].bends and TUNINGS["guitar"].bends
    assert not TUNINGS["bass"].bends and not TUNINGS["ukulele"].bends


def test_transpose_moves_notes_and_keeps_rhythm(tmp_path):
    from music2score.synth import synthesize

    path = tmp_path / "bell.wav"
    sf.write(path, synthesize(SCHOOL_BELL, 100, SR), SR)

    result = transcribe(path, tab="electric", transpose=-12)

    assert [q.pitch for q in result.qnotes] == [pitch.Pitch(name).midi - 12 for name, _ in SCHOOL_BELL]
    assert result.qnotes[-1].offset == 28.0 and result.moved == 0
