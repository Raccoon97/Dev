"""
포지션 추적 모듈
보유 포지션의 상태를 추적하고 관리합니다.
"""

import logging
from datetime import datetime

from db.models import (
    get_open_positions, insert_position, close_position,
    insert_daily_balance, get_daily_balances,
)
from config import FundConfig, ExchangeRateConfig

logger = logging.getLogger(__name__)


class PositionTracker:
    """포지션 추적 및 관리"""

    def __init__(self):
        self.exchange_rate = ExchangeRateConfig.DEFAULT_USD_KRW

    def update_exchange_rate(self, rate: float):
        """환율 업데이트"""
        if rate > 0:
            self.exchange_rate = rate

    def fetch_exchange_rate(self) -> float:
        """실시간 환율 조회"""
        import requests
        try:
            resp = requests.get(ExchangeRateConfig.API_URL, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            rate = data.get("rates", {}).get("KRW", ExchangeRateConfig.DEFAULT_USD_KRW)
            self.exchange_rate = rate
            logger.info("환율 업데이트: 1 USD = %.2f KRW", rate)
            return rate
        except Exception as e:
            logger.warning("환율 조회 실패, 기본값 사용: %s", e)
            return self.exchange_rate

    def get_all_open(self, market: str = None) -> list[dict]:
        """열린 포지션 조회"""
        return get_open_positions(market)

    def open_position(self, market: str, symbol: str, name: str,
                      quantity: int, entry_price: float,
                      stop_loss: float = None, take_profit: float = None,
                      signal_score: float = None) -> int:
        """새 포지션 개설"""
        position_id = insert_position(
            market=market,
            symbol=symbol,
            name=name,
            side="BUY",
            quantity=quantity,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            signal_score=signal_score,
        )
        logger.info(
            "포지션 개설: [%s] %s %s %d주 @ %.2f (SL: %.2f, TP: %.2f)",
            market, symbol, name, quantity, entry_price,
            stop_loss or 0, take_profit or 0,
        )
        return position_id

    def close_position_by_id(self, position_id: int, close_price: float,
                             realized_pnl: float):
        """포지션 청산"""
        close_position(position_id, close_price, realized_pnl)
        logger.info(
            "포지션 청산: ID=%d 가격=%.2f 실현손익=%.2f",
            position_id, close_price, realized_pnl,
        )

    def check_stop_loss(self, market_clients: dict) -> list[dict]:
        """모든 오픈 포지션의 손절가 도달 여부 체크"""
        triggered = []
        positions = get_open_positions()

        for pos in positions:
            if not pos.get("stop_loss"):
                continue
            try:
                market = pos["market"]
                client = market_clients.get(market)
                if not client:
                    continue
                price_data = client.get_price(pos["symbol"])
                current_price = price_data.get("price", 0)

                # 매수 포지션의 손절
                if pos["side"] == "BUY" and current_price <= pos["stop_loss"]:
                    triggered.append({
                        "position": pos,
                        "current_price": current_price,
                        "reason": f"손절가 도달 ({current_price:.2f} <= {pos['stop_loss']:.2f})",
                    })
                # 매도 포지션의 손절
                elif pos["side"] == "SELL" and current_price >= pos["stop_loss"]:
                    triggered.append({
                        "position": pos,
                        "current_price": current_price,
                        "reason": f"손절가 도달 ({current_price:.2f} >= {pos['stop_loss']:.2f})",
                    })
            except Exception as e:
                logger.error("손절 체크 실패 [%s]: %s", pos["symbol"], e)

        return triggered

    def calculate_portfolio_summary(self, kr_balance: dict, us_balance: dict) -> dict:
        """전체 포트폴리오 요약 계산"""
        krw_cash = kr_balance.get("cash", 0)
        krw_stock = kr_balance.get("stock_value", 0)
        usd_cash = us_balance.get("cash", 0)
        usd_stock = us_balance.get("stock_value", 0)

        total_krw = (
            krw_cash + krw_stock +
            (usd_cash + usd_stock) * self.exchange_rate
        )

        # 미실현 손익 계산
        kr_unrealized = sum(
            h.get("pnl", 0) for h in kr_balance.get("holdings", [])
        )
        us_unrealized = sum(
            h.get("pnl", 0) for h in us_balance.get("holdings", [])
        )
        total_unrealized = kr_unrealized + us_unrealized * self.exchange_rate

        return {
            "total_asset_krw": total_krw,
            "krw_cash": krw_cash,
            "krw_stock_value": krw_stock,
            "usd_cash": usd_cash,
            "usd_stock_value": usd_stock,
            "exchange_rate": self.exchange_rate,
            "unrealized_pnl": total_unrealized,
            "kr_holdings": kr_balance.get("holdings", []),
            "us_holdings": us_balance.get("holdings", []),
        }

    def save_daily_snapshot(self, summary: dict, realized_pnl: float = 0,
                            drawdown: float = 0):
        """일간 잔고 스냅샷 저장"""
        today = datetime.now().strftime("%Y-%m-%d")
        insert_daily_balance(
            date=today,
            total_asset_krw=summary["total_asset_krw"],
            krw_cash=summary["krw_cash"],
            krw_stock_value=summary["krw_stock_value"],
            usd_cash=summary["usd_cash"],
            usd_stock_value=summary["usd_stock_value"],
            exchange_rate=summary["exchange_rate"],
            realized_pnl=realized_pnl,
            unrealized_pnl=summary.get("unrealized_pnl", 0),
            drawdown=drawdown,
        )
        logger.info("일간 스냅샷 저장: %s / 총자산: %,.0f KRW", today, summary["total_asset_krw"])
