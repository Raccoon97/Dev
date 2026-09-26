"""명령줄 실행: python -m music2score 노래.wav"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .audio import record_audio
from .score import export, spell
from .transcriber import transcribe


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="music2score",
        description="음악(오디오)을 듣고 악보(MusicXML / MIDI / HTML)를 만듭니다.",
    )
    parser.add_argument("input", nargs="?", help="오디오 파일 (wav, mp3, flac, ogg ...)")
    parser.add_argument("--record", type=float, metavar="SEC", help="파일 대신 마이크로 SEC 초 동안 녹음")
    parser.add_argument(
        "--mode",
        choices=["mono", "poly"],
        default="mono",
        help="mono: 노래/허밍/단선율 악기 (기본), poly: 피아노처럼 화음이 있는 연주",
    )
    parser.add_argument("--bpm", type=float, help="템포를 알고 있으면 지정 (기본: 자동 추정)")
    parser.add_argument("--time", default="4/4", help="박자표 (기본: 4/4)")
    parser.add_argument("--grid", type=int, default=16, choices=[4, 8, 16, 32], help="가장 짧은 음표 (기본: 16분음표)")
    parser.add_argument("--min-note", type=float, metavar="SEC", help="이보다 짧은 음은 무시 (기본: mono 0.06초, poly 0.12초)")
    parser.add_argument("--title", help="악보 제목 (기본: 파일 이름)")
    parser.add_argument("-o", "--out", default="output", help="결과 폴더 (기본: output)")
    parser.add_argument("--pdf", action="store_true", help="MuseScore 로 PDF 도 만들기")
    args = parser.parse_args(argv)

    out_dir = Path(args.out)
    if args.record:
        src = record_audio(args.record, out_dir / "recording.wav")
    elif args.input:
        src = Path(args.input)
        if not src.exists():
            parser.error(f"파일이 없습니다: {src}")
    else:
        parser.error("오디오 파일을 주거나 --record 초 를 지정하세요.")

    print(f"♪ 분석 중: {src}")
    try:
        result = transcribe(
            src,
            mode=args.mode,
            bpm=args.bpm,
            time_signature=args.time,
            grid=args.grid,
            title=args.title,
            min_note=args.min_note,
        )
        files = export(result.score, out_dir, src.stem, pdf=args.pdf)
    except (RuntimeError, ValueError) as e:
        print(f"오류: {e}", file=sys.stderr)
        return 1

    names = " ".join(_pretty(spell(q.pitch, result.key).nameWithOctave) for q in result.qnotes[:16])
    more = " …" if len(result.qnotes) > 16 else ""
    print(f"  템포  : ♩ = {result.bpm:.0f}")
    print(f"  조성  : {_pretty(result.key.tonic.name)} {'장조' if result.key.mode == 'major' else '단조'}")
    print(f"  음 개수: {len(result.qnotes)}  ({names}{more})")
    print("  결과  :")
    for kind, path in files.items():
        print(f"    {kind:8} {path}")
    return 0


def _pretty(name: str) -> str:
    return name.replace("-", "♭").replace("#", "♯")


if __name__ == "__main__":
    sys.exit(main())
