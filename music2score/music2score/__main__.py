"""명령줄 실행: python -m music2score 노래.wav"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .audio import record_audio
from .score import export, spell
from .tab import TUNINGS
from .transcriber import transcribe


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="music2score",
        description="음악(오디오)을 듣고 악보(MusicXML / MIDI / HTML / 타브)를 만듭니다.",
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
    parser.add_argument(
        "--tab",
        choices=list(TUNINGS),
        help="타브 악보도 만들기: guitar(기타), drop-d(드롭 D 기타), bass(베이스), ukulele(우쿨렐레)",
    )
    parser.add_argument("--capo", type=int, default=0, metavar="N", help="카포 위치 (--tab 과 함께, 기본: 0)")
    parser.add_argument("--title", help="악보 제목 (기본: 파일 이름)")
    parser.add_argument("-o", "--out", default="output", help="결과 폴더 (기본: output)")
    parser.add_argument("--pdf", action="store_true", help="MuseScore 로 PDF 도 만들기")
    args = parser.parse_args(argv)
    if args.capo and not args.tab:
        parser.error("--capo 는 --tab 과 함께 쓰세요.")
    if not 0 <= args.capo <= 12:
        parser.error("--capo 는 0~12 사이여야 합니다.")

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
            tab=args.tab,
            capo=args.capo,
        )
        files = export(result.score, out_dir, src.stem, pdf=args.pdf, tuning=result.tuning, capo=args.capo)
    except (RuntimeError, ValueError) as e:
        print(f"오류: {e}", file=sys.stderr)
        return 1

    names = " ".join(_pretty(spell(q.pitch, result.key).nameWithOctave) for q in result.qnotes[:16])
    more = " …" if len(result.qnotes) > 16 else ""
    print(f"  템포  : ♩ = {result.bpm:.0f}")
    print(f"  조성  : {_pretty(result.key.tonic.name)} {'장조' if result.key.mode == 'major' else '단조'}")
    print(f"  음 개수: {len(result.qnotes)}  ({names}{more})")
    if result.tuning is not None:
        tab_path = out_dir / f"{src.stem}.tab.txt"
        tab_text = result.tab_text()
        tab_path.write_text(tab_text, encoding="utf-8")
        files["tab"] = tab_path
        print(f"  타브  : {result.tuning.label}" + (f", 카포 {args.capo}프렛" if args.capo else ""))
        if result.moved:
            done = "뺀" if args.mode == "poly" else "옥타브를 옮긴"
            print(f"          악기 음역 밖이라 {done} 음 {result.moved}개")
        if result.dropped:
            print(f"          한 손으로 잡을 수 없어 뺀 화음 구성음 {result.dropped}개")
    print("  결과  :")
    for kind, path in files.items():
        print(f"    {kind:8} {path}")
    if result.tuning is not None:
        print()
        print(_first_system(tab_text))
    return 0


def _first_system(tab_text: str) -> str:
    """글자 타브에서 제목·정보 줄을 빼고 첫 줄(보표 한 단)만."""
    systems = tab_text.strip("\n").split("\n\n")
    return systems[1] if len(systems) > 1 else systems[0]


def _pretty(name: str) -> str:
    return name.replace("-", "♭").replace("#", "♯")


if __name__ == "__main__":
    sys.exit(main())
