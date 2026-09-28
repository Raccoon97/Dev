"""파이프라인 단계 사이에서 주고받는 음(note) 자료형."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Technique:
    """현악기 주법. 피킹 없이 왼손만으로 음을 바꾸는 소리를 오디오에서 읽어 낸 것."""

    # 앞 음에서 이 음으로 어떻게 넘어왔나.
    #   ""       : 새로 친 음 (피킹)
    #   "hammer" : 해머링 — 치지 않고 더 높은 음으로 순간 이동
    #   "pull"   : 풀링   — 치지 않고 더 낮은 음으로 순간 이동
    #   "slide"  : 슬라이드 — 음높이가 미끄러지듯 이어서 이동
    #   "glide"  : 미끄러지듯 이동했지만 슬라이드인지 벤딩인지 아직 모름 (악기를 알면 정한다)
    link: str = ""
    slide_in: str = ""  # "up": 아래에서 미끄러져 들어옴, "down": 위에서
    slide_out: str = ""  # "up" / "down": 끝에서 미끄러져 빠져나감
    bend: int = 0  # 벤딩 폭 (반음). 2 = 온음 벤딩
    release: bool = False  # 벤딩 후 원래 음으로 되돌림

    @property
    def any(self) -> bool:
        return bool(self.link or self.slide_in or self.slide_out or self.bend)


@dataclass(frozen=True)
class NoteEvent:
    """오디오에서 검출한 음 하나. 시간 단위는 초."""

    start: float
    end: float
    pitch: int  # MIDI 번호 (60 = C4, 가온 도)
    velocity: int = 80
    tech: Technique = field(default_factory=Technique)

    @property
    def duration(self) -> float:
        return self.end - self.start


@dataclass(frozen=True)
class QuantizedNote:
    """박자 격자에 맞춘 음. 단위는 4분음표 = 1.0 (music21 의 quarterLength)."""

    offset: float
    length: float
    pitch: int
    velocity: int = 80
    tech: Technique = field(default_factory=Technique)

    @property
    def end(self) -> float:
        return self.offset + self.length
