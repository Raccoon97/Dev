"""양자화된 음 → music21 악보, 그리고 MusicXML / MIDI / HTML / PDF 내보내기."""

from __future__ import annotations

import html
import math
import shutil
import subprocess
from pathlib import Path

from music21 import chord, clef, instrument, key, layout, metadata, meter, note, pitch, stream, tempo

from .notes import QuantizedNote

SPLIT_POINT = 60  # 피아노 모드에서 C4 이상은 오른손(높은음자리표), 미만은 왼손


def estimate_key(qnotes: list[QuantizedNote]) -> key.Key:
    """음 길이로 가중한 음 분포로 조성을 추정한다 (Krumhansl-Schmuckler)."""
    if not qnotes:
        return key.Key("C")
    s = stream.Stream()
    for q in qnotes:
        s.insert(q.offset, note.Note(q.pitch, quarterLength=q.length))
    return s.analyze("key")


def spell(midi: int, k: key.Key) -> pitch.Pitch:
    """MIDI 번호를 조성에 맞는 음이름으로 바꾼다 (예: F 장조에서 70 → B♭4, A♯4 아님)."""
    p = pitch.Pitch(midi=midi)
    scale = list(k.pitches)
    if k.mode == "minor":
        # 화성/가락 단음계의 올린 6·7음 (예: 가단조의 F♯·G♯)
        scale += [k.pitchFromDegree(d).transpose("A1") for d in (6, 7)]
    scale_names = {sp.pitchClass: sp.name for sp in scale}
    if p.pitchClass in scale_names:
        if p.name != scale_names[p.pitchClass]:
            p = pitch.Pitch(scale_names[p.pitchClass] + str(p.octave))
            while p.midi > midi:
                p.octave -= 1
            while p.midi < midi:
                p.octave += 1
    elif p.accidental is not None:
        if (k.sharps > 0 and p.accidental.alter < 0) or (k.sharps < 0 and p.accidental.alter > 0):
            p = p.getEnharmonic()
    return p


def build_score(
    qnotes: list[QuantizedNote],
    *,
    bpm: float,
    k: key.Key,
    time_signature: str = "4/4",
    title: str = "Transcription",
    piano: bool = False,
) -> stream.Score:
    score = stream.Score()
    # title 로 넣으면 work-title/movement-title 두 곳에 들어가 뷰어에 제목이 두 번 찍힌다.
    score.insert(0, metadata.Metadata(movementName=title, composer="music2score"))

    if piano:
        right = _make_part([q for q in qnotes if q.pitch >= SPLIT_POINT], k, chords=True)
        left = _make_part([q for q in qnotes if q.pitch < SPLIT_POINT], k, chords=True)
        parts = [(right, clef.TrebleClef()), (left, clef.BassClef())]
    else:
        part = _make_part(qnotes, k, chords=False)
        parts = [(part, clef.bestClef(part, recurse=True))]

    # 마지막 마디가 모자라면 쉼표로 채워서 온전한 마디로 끝낸다.
    bar = meter.TimeSignature(time_signature).barDuration.quarterLength
    total = math.ceil(max((q.end for q in qnotes), default=0.0) / bar) * bar
    for i, (part, part_clef) in enumerate(parts):
        _pad_to(part, total)
        part.insert(0, part_clef)
        part.insert(0, key.KeySignature(k.sharps))
        part.insert(0, meter.TimeSignature(time_signature))
        if i == 0:
            part.insert(0, tempo.MetronomeMark(number=round(bpm)))
        part.insert(0, instrument.Piano())  # MIDI 재생용 음색
        score.insert(0, part)

    if piano:
        score.insert(0, layout.StaffGroup([p for p, _ in parts], symbol="brace", barTogether=True))
    return score.makeNotation()


def _make_part(qnotes: list[QuantizedNote], k: key.Key, *, chords: bool) -> stream.Part:
    part: stream.Part = stream.PartStaff() if chords else stream.Part()
    for q in qnotes:
        n = note.Note(spell(q.pitch, k), quarterLength=q.length)
        n.volume.velocity = q.velocity
        part.insert(q.offset, n)
    if chords and qnotes:
        # 길이가 서로 다른 음이 겹쳐도 붙임줄로 이어진 화음 열로 정리된다.
        flat = part.chordify()
        part = stream.PartStaff()
        for el in flat.recurse().notesAndRests:
            part.insert(el.getOffsetInHierarchy(flat), _unwrap(el))
    part.makeRests(fillGaps=True, inPlace=True)
    return part


def _unwrap(el: note.GeneralNote) -> note.GeneralNote:
    """chordify 가 만든 '음 하나짜리 화음'을 보통 음표로 되돌린다."""
    if not isinstance(el, chord.Chord) or len(el.notes) != 1:
        return el
    single = el.notes[0]
    n = note.Note(single.pitch, quarterLength=el.quarterLength)
    n.tie = el.tie or single.tie
    n.volume.velocity = single.volume.velocity
    return n


def _pad_to(part: stream.Part, total: float) -> None:
    """모든 성부가 같은 길이(마디 끝)로 끝나도록 마지막을 쉼표로 채운다."""
    end = part.highestTime
    if end < total:
        part.insert(end, note.Rest(quarterLength=total - end))


def export(score: stream.Score, out_dir: Path, name: str = "score", *, pdf: bool = False) -> dict[str, Path]:
    """악보를 여러 형식으로 저장하고 {형식: 경로} 를 돌려준다."""
    out_dir.mkdir(parents=True, exist_ok=True)
    files: dict[str, Path] = {}

    xml_path = Path(score.write("musicxml", fp=out_dir / f"{name}.musicxml"))
    files["musicxml"] = xml_path
    files["midi"] = Path(score.write("midi", fp=out_dir / f"{name}.mid"))

    html_path = out_dir / f"{name}.html"
    html_path.write_text(_viewer_html(xml_path.read_text(encoding="utf-8"), score), encoding="utf-8")
    files["html"] = html_path

    if pdf:
        files["pdf"] = _musescore_pdf(xml_path, out_dir / f"{name}.pdf")
    return files


def _musescore_pdf(xml_path: Path, pdf_path: Path) -> Path:
    names = ("mscore", "musescore", "mscore4", "MuseScore4", "mscore3", "musescore3")
    exe = next(filter(None, map(shutil.which, names)), None)
    if exe is None:
        raise RuntimeError("PDF 를 만들려면 MuseScore 를 설치하고 PATH 에 mscore 를 등록하세요.")
    subprocess.run([exe, "-o", str(pdf_path), str(xml_path)], check=True, capture_output=True)
    return pdf_path


OSMD_URL = "https://cdn.jsdelivr.net/npm/opensheetmusicdisplay@2.1.3/build/opensheetmusicdisplay.min.js"


def _viewer_html(musicxml: str, score: stream.Score) -> str:
    """브라우저에서 바로 열어 보는 악보 뷰어 (OpenSheetMusicDisplay)."""
    title = html.escape(score.metadata.bestTitle or "Score")
    # JS 템플릿 문자열 안에 넣으므로 \, `, ${ 를 이스케이프하고 </script> 조기 종료도 막는다.
    xml_js = (
        musicxml.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${").replace("</", "<\\/")
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body {{ margin: 0; background: #fff; color: #222; font-family: system-ui, sans-serif; }}
  #osmd {{ max-width: 1100px; margin: 0 auto; padding: 16px; }}
  #error {{ color: #b00020; padding: 16px; }}
</style>
</head>
<body>
<div id="osmd"></div>
<div id="error"></div>
<script src="{OSMD_URL}"></script>
<script>
  const xml = `{xml_js}`;
  const osmd = new opensheetmusicdisplay.OpenSheetMusicDisplay("osmd", {{ autoResize: true, drawTitle: true }});
  osmd.load(xml).then(() => osmd.render()).catch(e => {{
    document.getElementById("error").textContent = "악보를 그리지 못했습니다: " + e;
  }});
</script>
</body>
</html>
"""
