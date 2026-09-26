"""파이프라인 단계 사이에서 주고받는 음(note) 자료형."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NoteEvent:
    """오디오에서 검출한 음 하나. 시간 단위는 초."""

    start: float
    end: float
    pitch: int  # MIDI 번호 (60 = C4, 가온 도)
    velocity: int = 80

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

    @property
    def end(self) -> float:
        return self.offset + self.length
