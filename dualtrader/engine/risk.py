"""
리스크 관리 모듈
일일 손실 한도, 드로우다운 관리, 포지션 크기 계산
"""

import logging
from dataclasses import dataclass
from datetime import datetime

from config import RiskConfig, FundConfig
from db.models import get_open_positions, get_daily_balances

logger = logging.getLogger(__name__)


@dataclass
class RiskCheck:
    """리스크 체크 결과"""
    can_trade: bool
    reason: str
    daily_pnl: float
    drawdown: float
    open_positions_count: int


class RiskManager:
    """리스크 관리자"""

    def __init__(self, initial_capital: float = None):
        self.initial_capital = initial_capital or FundConfig.INITIAL_CAPITAL_KRW
        self.cfg = RiskConfig
        self.peak_value = self.initial_capital
        self.daily_pnl = 0.0
        self.is_halted = False

    def update_peak(self, current_total: float):
        """최고 자산 갱신"""
        if current_total > self.peak_value:
            self.peak_value = current_total

    def calculate_drawdown(self, current_total: float) -> float:
        """현재 드로우다운 계산"""
        if self.peak_value == 0:
            return 0
        return (self.peak_value - current_total) / self.peak_value

    def check_daily_loss(self, realized_pnl_today: float, total_asset: float) -> bool:
        """일일 손실 한도 체크"""
        if total_asset == 0:
            return False
        loss_ratio = abs(min(0, realized_pnl_today)) / total_asset
        return loss_ratio < self.cfg.MAX_DAILY_LOSS_RATIO

    def check_drawdown(self, current_total: float) -> bool:
        """드로우다운 한도 체크"""
        dd = self.calculate_drawdown(current_total)
        return dd < self.cfg.MAX_DRAWDOWN_RATIO

    def check_position_count(self, market: str) -> bool:
        """시장별 보유 종목 수 체크"""
        positions = get_open_positions(market)
        return len(positions) < self.cfg.MAX_POSITIONS_PER_MARKET

    def check_position_size(self, market_fund: float, order_amount: float) -> bool:
        """단일 종목 비중 체크"""
        if market_fund == 0:
            return False
        ratio = order_amount / market_fund
        return ratio <= self.cfg.MAX_SINGLE_POSITION_RATIO

    def full_check(self, market: str, total_asset: float,
                   realized_pnl_today: float) -> RiskCheck:
        """전체 리스크 체크"""
        self.update_peak(total_asset)

        positions = get_open_positions(market)
        open_count = len(positions)
        drawdown = self.calculate_drawdown(total_asset)

        # 드로우다운 초과
        if not self.check_drawdown(total_asset):
            self.is_halted = True
            return RiskCheck(
                can_trade=False,
                reason=f"드로우다운 한도 초과 ({drawdown:.1%} >= {self.cfg.MAX_DRAWDOWN_RATIO:.0%}). 전체 포지션 청산 필요.",
                daily_pnl=realized_pnl_today,
                drawdown=drawdown,
                open_positions_count=open_count,
            )

        # 일일 손실 한도 초과
        if not self.check_daily_loss(realized_pnl_today, total_asset):
            return RiskCheck(
                can_trade=False,
                reason=f"일일 최대 손실 한도 초과 (손실: {realized_pnl_today:,.0f}원)",
                daily_pnl=realized_pnl_today,
                drawdown=drawdown,
                open_positions_count=open_count,
            )

        # 포지션 수 초과
        if not self.check_position_count(market):
            return RiskCheck(
                can_trade=False,
                reason=f"최대 보유 종목 수 초과 ({open_count}/{self.cfg.MAX_POSITIONS_PER_MARKET})",
                daily_pnl=realized_pnl_today,
                drawdown=drawdown,
                open_positions_count=open_count,
            )

        return RiskCheck(
            can_trade=True,
            reason="정상",
            daily_pnl=realized_pnl_today,
            drawdown=drawdown,
            open_positions_count=open_count,
        )

    def calculate_position_size(self, market_fund: float, price: float,
                                signal_score: float, atr: float = 0) -> int:
        """포지션 크기 계산 (고정 비율 + 신호 강도 조절)"""
        if price <= 0 or market_fund <= 0:
            return 0

        # 기본: 시장 자금의 최대 15% 이내
        max_amount = market_fund * self.cfg.MAX_SINGLE_POSITION_RATIO

        # 신호 강도에 비례하여 투자 비율 조절 (50% ~ 100%)
        score_ratio = 0.5 + (signal_score / 100) * 0.5
        target_amount = max_amount * score_ratio

        # 1회 주문 한도 적용
        single_limit = market_fund * FundConfig.MAX_SINGLE_ORDER_RATIO
        target_amount = min(target_amount, single_limit)

        quantity = int(target_amount / price)
        return max(0, quantity)

    def calculate_stop_loss(self, entry_price: float, atr: float,
                            side: str = "BUY") -> float:
        """ATR 기반 손절가 계산"""
        if atr <= 0:
            # ATR 없으면 진입가의 3% 손절
            if side == "BUY":
                return entry_price * 0.97
            return entry_price * 1.03

        multiplier = 1.5
        if side == "BUY":
            return entry_price - multiplier * atr
        return entry_price + multiplier * atr

    def reset_daily(self):
        """일일 리스크 카운터 리셋"""
        self.daily_pnl = 0.0
        if not self.is_halted:
            logger.info("일일 리스크 카운터 리셋")
        else:
            logger.warning("시스템이 중단 상태입니다. 수동 확인이 필요합니다.")
