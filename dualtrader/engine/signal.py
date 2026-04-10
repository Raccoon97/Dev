"""
Signal Engine — 기술적 지표 계산 + 복합 신호 생성
RSI, MACD, 볼린저밴드, 이동평균, 거래량, ATR을 종합 분석
"""

import logging
import pandas as pd
import pandas_ta as ta
from dataclasses import dataclass

from config import SignalConfig

logger = logging.getLogger(__name__)


@dataclass
class Signal:
    """매매 신호 데이터"""
    symbol: str
    signal_type: str   # BUY, SELL, HOLD
    score: float       # 0 ~ 100
    rsi: float
    macd_signal: str   # GOLDEN_CROSS, DEAD_CROSS, NEUTRAL
    bb_signal: str     # LOWER_TOUCH, UPPER_TOUCH, NEUTRAL
    ma_signal: str     # ALIGNED_UP, ALIGNED_DOWN, NEUTRAL
    volume_signal: str # SURGE, NORMAL
    atr: float
    stop_loss: float
    take_profit: float
    detail: str


class SignalEngine:
    """기술적 지표 기반 신호 생성 엔진"""

    def __init__(self):
        self.cfg = SignalConfig

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """OHLCV DataFrame에 모든 기술적 지표를 추가"""
        if df.empty or len(df) < self.cfg.MA_LONG:
            logger.warning("데이터 부족 (필요: %d행, 현재: %d행)", self.cfg.MA_LONG, len(df))
            return df

        # RSI
        df["rsi"] = ta.rsi(df["close"], length=self.cfg.RSI_PERIOD)

        # MACD
        macd = ta.macd(
            df["close"],
            fast=self.cfg.MACD_FAST,
            slow=self.cfg.MACD_SLOW,
            signal=self.cfg.MACD_SIGNAL,
        )
        if macd is not None:
            df["macd"] = macd.iloc[:, 0]
            df["macd_hist"] = macd.iloc[:, 1]
            df["macd_signal_line"] = macd.iloc[:, 2]

        # 볼린저밴드
        bbands = ta.bbands(df["close"], length=self.cfg.BB_PERIOD, std=self.cfg.BB_STD)
        if bbands is not None:
            df["bb_lower"] = bbands.iloc[:, 0]
            df["bb_mid"] = bbands.iloc[:, 1]
            df["bb_upper"] = bbands.iloc[:, 2]

        # 이동평균
        df["ma_short"] = ta.sma(df["close"], length=self.cfg.MA_SHORT)
        df["ma_mid"] = ta.sma(df["close"], length=self.cfg.MA_MID)
        df["ma_long"] = ta.sma(df["close"], length=self.cfg.MA_LONG)

        # ATR
        df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=self.cfg.ATR_PERIOD)

        # 거래량 이동평균
        df["vol_ma20"] = ta.sma(df["volume"], length=20)

        return df

    def _evaluate_rsi(self, row: pd.Series) -> tuple[str, float]:
        """RSI 신호 평가"""
        rsi = row.get("rsi")
        if pd.isna(rsi):
            return "NEUTRAL", 0

        if rsi < self.cfg.RSI_OVERSOLD:
            return "BUY", min(30, (self.cfg.RSI_OVERSOLD - rsi) * 2)
        elif rsi > self.cfg.RSI_OVERBOUGHT:
            return "SELL", min(30, (rsi - self.cfg.RSI_OVERBOUGHT) * 2)
        return "NEUTRAL", 0

    def _evaluate_macd(self, df: pd.DataFrame, idx: int) -> tuple[str, float]:
        """MACD 골든크로스/데드크로스 판단"""
        if idx < 1:
            return "NEUTRAL", 0
        curr_hist = df.iloc[idx].get("macd_hist")
        prev_hist = df.iloc[idx - 1].get("macd_hist")
        if pd.isna(curr_hist) or pd.isna(prev_hist):
            return "NEUTRAL", 0

        if prev_hist < 0 and curr_hist > 0:
            return "BUY", 20
        elif prev_hist > 0 and curr_hist < 0:
            return "SELL", 20
        return "NEUTRAL", 0

    def _evaluate_bollinger(self, row: pd.Series) -> tuple[str, float]:
        """볼린저밴드 신호 평가"""
        close = row.get("close")
        bb_lower = row.get("bb_lower")
        bb_upper = row.get("bb_upper")
        if pd.isna(close) or pd.isna(bb_lower) or pd.isna(bb_upper):
            return "NEUTRAL", 0

        if close <= bb_lower:
            return "BUY", 15
        elif close >= bb_upper:
            return "SELL", 15
        return "NEUTRAL", 0

    def _evaluate_ma(self, row: pd.Series) -> tuple[str, float]:
        """이동평균 정배열/역배열 판단"""
        ma_short = row.get("ma_short")
        ma_mid = row.get("ma_mid")
        ma_long = row.get("ma_long")
        if pd.isna(ma_short) or pd.isna(ma_mid) or pd.isna(ma_long):
            return "NEUTRAL", 0

        if ma_short > ma_mid > ma_long:
            return "BUY", 15
        elif ma_short < ma_mid < ma_long:
            return "SELL", 15
        return "NEUTRAL", 0

    def _evaluate_volume(self, row: pd.Series) -> tuple[str, float]:
        """거래량 급증 판단"""
        volume = row.get("volume")
        vol_ma = row.get("vol_ma20")
        if pd.isna(volume) or pd.isna(vol_ma) or vol_ma == 0:
            return "NORMAL", 0

        ratio = volume / vol_ma
        if ratio > 2.0:
            return "SURGE", 20
        elif ratio > 1.5:
            return "SURGE", 10
        return "NORMAL", 0

    def generate_signal(self, df: pd.DataFrame, symbol: str) -> Signal:
        """전체 지표를 종합하여 매매 신호 생성"""
        df = self.calculate_indicators(df.copy())
        if df.empty or len(df) < 2:
            return Signal(
                symbol=symbol, signal_type="HOLD", score=0,
                rsi=0, macd_signal="NEUTRAL", bb_signal="NEUTRAL",
                ma_signal="NEUTRAL", volume_signal="NORMAL",
                atr=0, stop_loss=0, take_profit=0,
                detail="데이터 부족",
            )

        idx = len(df) - 1
        row = df.iloc[idx]
        close = float(row["close"])

        # 각 지표 평가
        rsi_dir, rsi_score = self._evaluate_rsi(row)
        macd_dir, macd_score = self._evaluate_macd(df, idx)
        bb_dir, bb_score = self._evaluate_bollinger(row)
        ma_dir, ma_score = self._evaluate_ma(row)
        vol_dir, vol_score = self._evaluate_volume(row)

        # 매수/매도 신호 카운트
        buy_signals = sum(1 for d in [rsi_dir, macd_dir, bb_dir, ma_dir] if d == "BUY")
        sell_signals = sum(1 for d in [rsi_dir, macd_dir, bb_dir, ma_dir] if d == "SELL")

        # 신호 방향 결정
        if buy_signals >= self.cfg.BUY_MIN_SIGNALS:
            signal_type = "BUY"
            base_score = rsi_score + macd_score + bb_score + ma_score
            # 거래량 급증 시 가중치
            if vol_dir == "SURGE":
                base_score += vol_score
            score = min(100, base_score)
        elif sell_signals >= self.cfg.SELL_MIN_SIGNALS:
            signal_type = "SELL"
            base_score = rsi_score + macd_score + bb_score + ma_score
            if vol_dir == "SURGE":
                base_score += vol_score
            score = min(100, base_score)
        else:
            signal_type = "HOLD"
            score = 0

        # ATR 기반 손절/익절
        atr_val = float(row.get("atr", 0)) if not pd.isna(row.get("atr")) else 0
        if signal_type == "BUY":
            stop_loss = close - self.cfg.ATR_STOP_MULTIPLIER * atr_val
            take_profit = close + self.cfg.ATR_STOP_MULTIPLIER * 2 * atr_val
        elif signal_type == "SELL":
            stop_loss = close + self.cfg.ATR_STOP_MULTIPLIER * atr_val
            take_profit = close - self.cfg.ATR_STOP_MULTIPLIER * 2 * atr_val
        else:
            stop_loss = 0
            take_profit = 0

        detail_parts = [
            f"RSI({row.get('rsi', 0):.1f})={rsi_dir}",
            f"MACD={macd_dir}",
            f"BB={bb_dir}",
            f"MA={ma_dir}",
            f"VOL={vol_dir}",
        ]

        rsi_val = float(row.get("rsi", 0)) if not pd.isna(row.get("rsi")) else 0

        return Signal(
            symbol=symbol,
            signal_type=signal_type,
            score=score,
            rsi=rsi_val,
            macd_signal=macd_dir,
            bb_signal=bb_dir,
            ma_signal=ma_dir,
            volume_signal=vol_dir,
            atr=atr_val,
            stop_loss=round(stop_loss, 2),
            take_profit=round(take_profit, 2),
            detail=" | ".join(detail_parts),
        )

    def batch_signals(self, market_client, symbols: list[str]) -> list[Signal]:
        """여러 종목의 신호를 일괄 생성"""
        signals = []
        for symbol in symbols:
            try:
                df = market_client.get_ohlcv(symbol, days=self.cfg.LOOKBACK_DAYS + self.cfg.MA_LONG)
                signal = self.generate_signal(df, symbol)
                signals.append(signal)
                logger.info("[%s] %s (score: %.0f)", symbol, signal.signal_type, signal.score)
            except Exception as e:
                logger.error("신호 생성 실패 [%s]: %s", symbol, e)
        return signals
