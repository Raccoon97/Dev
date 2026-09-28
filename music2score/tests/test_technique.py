"""주법(해머링·풀링·슬라이드·벤딩) 인식과 표기, 악기 분리."""

from __future__ import annotations

import numpy as np
import pytest
import soundfile as sf
from music21 import pitch

from music2score import transcribe
from music2score.notes import NoteEvent, Technique
from music2score.score import export
from music2score.separate import MdxModel, _demix
from music2score.synth import synthesize, synthesize_lick
from music2score.tab import TUNINGS, osmd_bends, resolve_glides

SR = 22050

# 5포지션 A 단조 펜타토닉 릭: 해머링, 풀링, 슬라이드, 벤딩, 벤딩+릴리즈, 슬라이드 아웃
GUITAR_LICK = [
    ("A3", 1, ""), ("C4", 0.5, ""), ("D4", 0.5, "h"), ("E4", 0.5, ""), ("D4", 0.5, "p"),
    ("C4", 1, ""), ("E4", 1, "/"), ("A4", 2, "b2"), ("G4", 2, "b2r"), ("E4", 2, ">"),
]
BASS_LICK = [
    ("E2", 1, ""), ("G2", 0.5, ""), ("A2", 0.5, "h"), ("B2", 1, ""), ("A2", 0.5, ""),
    ("G2", 0.5, "p"), ("E2", 1, ""), ("A2", 1, "/"), ("E2", 2, ">"),
]


def midi(name: str) -> int:
    return pitch.Pitch(name).midi


@pytest.fixture(scope="module")
def guitar(tmp_path_factory):
    path = tmp_path_factory.mktemp("lick") / "lick.wav"
    sf.write(path, synthesize_lick(GUITAR_LICK, 90, SR), SR)
    return transcribe(path, tab="guitar")


def test_guitar_lick_notes_and_rhythm(guitar):
    expected, offset = [], 0.0
    for name, beats, _ in GUITAR_LICK:
        expected.append((offset, float(beats), midi(name)))
        offset += beats
    assert [(q.offset, q.length, q.pitch) for q in guitar.qnotes] == expected


def test_guitar_lick_techniques(guitar):
    techs = [t.note.tech for t in guitar.tab_notes]
    assert [t.link for t in techs] == ["", "", "hammer", "", "pull", "", "slide", "", "", ""]
    assert [(t.bend, t.release) for t in techs][7:9] == [(2, False), (2, True)]
    assert techs[9].slide_out == "down"


def test_legato_notes_stay_on_one_string(guitar):
    tab = guitar.tab_notes
    for prev, cur in zip(tab, tab[1:]):
        if cur.note.tech.link:
            assert prev.string == cur.string
    assert all(t.fret > 0 for t in tab if t.note.tech.bend)  # 개방현은 밀어 올릴 수 없다


def test_guitar_lick_ascii(guitar):
    text = guitar.tab_text()
    for mark in ("h7", "p3", "/5", "5b7", "3b5r3", "5\\", "h 해머링"):
        assert mark in text, mark


def test_guitar_lick_musicxml(guitar, tmp_path):
    files = export(guitar.score, tmp_path, "lick", tuning=guitar.tuning)
    xml = files["musicxml"].read_text(encoding="utf-8")

    assert xml.count('<hammer-on number="1" type="start">H</hammer-on>') == 1
    assert xml.count('<pull-off number="1" type="stop"/>') == 1
    assert xml.count('<slide line-type="solid" number="1" type="start"/>') == 1
    assert xml.count("<bend-alter>2</bend-alter>") == 2 and xml.count("<release/>") == 1  # 표준: 반음 수
    assert "<falloff/>" in xml and "<fingering" not in xml
    # 뷰어(OSMD)에 넣는 사본만 bend-alter 가 도착 프렛이다: 5b7 → 7, 3b5 → 5
    page = files["html"].read_text(encoding="utf-8")
    assert "<bend-alter>7<\\/bend-alter>" in page and "<bend-alter>5<\\/bend-alter>" in page


def test_bass_lick(tmp_path):
    path = tmp_path / "bass.wav"
    sf.write(path, synthesize_lick(BASS_LICK, 100, SR), SR)

    result = transcribe(path, tab="bass")

    assert [q.pitch for q in result.qnotes] == [midi(n) for n, _, _ in BASS_LICK]
    assert [t.note.tech.link for t in result.tab_notes] == ["", "", "hammer", "", "", "pull", "", "slide", ""]
    assert result.tab_notes[-1].note.tech.slide_out == "down"
    assert "0-h2" in result.tab_text() and "2-p0" in result.tab_text()  # 개방현에서 해머링 / 개방현으로 풀링


def test_picked_notes_get_no_techniques(tmp_path):
    riff = [("E3", 0.5), ("G3", 0.5), ("A3", 1), ("B3", 0.5), ("D4", 0.5), ("E4", 1), ("D4", 0.5), ("B3", 0.5)]
    for name, audio in {
        "guitar": synthesize(riff, 96, SR, legato=1.0, timbre="guitar"),
        "voice": synthesize(riff, 96, SR, legato=1.0, vibrato=0.3, noise=0.01),
    }.items():
        path = tmp_path / f"{name}.wav"
        sf.write(path, audio, SR)
        result = transcribe(path, tab="guitar")
        assert not any(t.note.tech.any for t in result.tab_notes), name


def test_resolve_glides_depends_on_instrument():
    glide = Technique(link="glide")
    up = [NoteEvent(0.0, 0.3, 69), NoteEvent(0.3, 1.0, 71, tech=glide)]
    up_and_back = up + [NoteEvent(1.0, 1.5, 69, tech=glide)]
    wide = [NoteEvent(0.0, 0.3, 60), NoteEvent(0.3, 1.0, 65, tech=glide)]

    bent = resolve_glides(up, allow_bends=True)
    assert len(bent) == 1 and (bent[0].pitch, bent[0].tech.bend, bent[0].end) == (69, 2, 1.0)
    released = resolve_glides(up_and_back, allow_bends=True)
    assert len(released) == 1 and released[0].tech.release
    assert [n.tech.link for n in resolve_glides(up, allow_bends=False)] == ["", "slide"]  # 베이스
    assert [n.tech.link for n in resolve_glides(wide, allow_bends=True)] == ["", "slide"]  # 5반음은 벤딩이 아니다


def test_osmd_bends_only_rewrites_bend_alter():
    xml = "<technical><string>1</string><fret>5</fret><bend><bend-alter>2</bend-alter></bend></technical>"
    assert "<bend-alter>7</bend-alter>" in osmd_bends(xml)


def test_bass5_reaches_low_b():
    assert min(TUNINGS["bass5"].strings) == midi("B0")


class _Identity:
    """악기 분리 모델 대신: 받은 스펙트로그램을 그대로 돌려준다."""

    def run(self, _outputs, feeds):
        return [feeds["input"]]


def test_separation_chunks_reassemble_exactly():
    # 모델이 아무것도 안 바꾸면 조각내기 → STFT → iSTFT → 이어 붙이기가 원래 소리를 돌려줘야 한다.
    sr = 44100
    t = np.arange(int(sr * 7.3)) / sr
    mix = np.stack([np.sin(2 * np.pi * 220 * t), 0.5 * np.sin(2 * np.pi * 330 * t)]).astype(np.float32)

    out = _demix(mix, _Identity(), MdxModel("-", n_fft=4096, dim_t=64))

    assert out.shape == mix.shape
    assert np.max(np.abs(out - mix)) < 1e-3
