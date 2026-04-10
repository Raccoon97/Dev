"""
주문 실행 모듈
신호 기반 매수/매도 주문 실행, 체결 관리
"""

import logging
from datetime import datetime

from config import SignalConfig, FundConfig
from engine.signal import Signal
from engine.risk import RiskManager
from order.position import PositionTracker
from db.models import insert_order, update_order_status, insert_signal_log

logger = logging.getLogger(__name__)


class OrderManager:
    """주문 실행 관리자"""

    def __init__(self, kr_market, us_market, risk_manager: RiskManager,
                 position_tracker: PositionTracker, notifier=None):
        self.kr_market = kr_market
        self.us_market = us_market
        self.risk = risk_manager
        self.positions = position_tracker
        self.notifier = notifier

    def _get_market_client(self, market: str):
        if market == "KR":
            return self.kr_market
        return self.us_market

    def _get_market_fund(self, market: str, balance: dict) -> float:
        """시장별 가용 자금 계산"""
        return balance.get("cash", 0)

    async def _notify(self, message: str):
        """텔레그램 알림 전송"""
        if self.notifier:
            try:
                await self.notifier.send_message(message)
            except Exception as e:
                logger.error("알림 전송 실패: %s", e)

    def execute_buy(self, market: str, signal: Signal,
                    balance: dict, name: str = "") -> dict:
        """매수 주문 실행"""
        client = self._get_market_client(market)
        market_fund = self._get_market_fund(market, balance)

        # 리스크 체크
        risk_check = self.risk.full_check(
            market=market,
            total_asset=balance.get("total_value", 0),
            realized_pnl_today=0,
        )
        if not risk_check.can_trade:
            logger.warning("매수 거부 [%s]: %s", signal.symbol, risk_check.reason)
            return {"success": False, "reason": risk_check.reason}

        # 현재가 조회
        try:
            price_data = client.get_price(signal.symbol)
            current_price = price_data.get("price", 0)
        except Exception as e:
            logger.error("시세 조회 실패 [%s]: %s", signal.symbol, e)
            return {"success": False, "reason": f"시세 조회 실패: {e}"}

        if current_price <= 0:
            return {"success": False, "reason": "유효하지 않은 가격"}

        # 포지션 크기 계산
        quantity = self.risk.calculate_position_size(
            market_fund=market_fund,
            price=current_price,
            signal_score=signal.score,
            atr=signal.atr,
        )
        if quantity <= 0:
            return {"success": False, "reason": "수량 0 (자금 부족 또는 비중 초과)"}

        # 포지션 비중 체크
        order_amount = current_price * quantity
        if not self.risk.check_position_size(market_fund, order_amount):
            return {"success": False, "reason": "단일 종목 비중 초과"}

        # 주문 유형 결정
        order_type = "MARKET" if signal.score >= SignalConfig.STRONG_SIGNAL_THRESHOLD else "LIMIT"
        price_arg = 0 if order_type == "MARKET" else int(current_price)

        # DB에 주문 기록
        order_id = insert_order(
            market=market,
            symbol=signal.symbol,
            side="BUY",
            order_type=order_type,
            quantity=quantity,
            price=current_price,
            signal_score=signal.score,
        )

        # 신호 로그 기록
        insert_signal_log(
            market=market,
            symbol=signal.symbol,
            signal_type="BUY",
            score=signal.score,
            rsi=signal.rsi,
            macd_signal=signal.macd_signal,
            bb_signal=signal.bb_signal,
            ma_signal=signal.ma_signal,
            volume_signal=signal.volume_signal,
            atr=signal.atr,
            detail=signal.detail,
        )

        # 실제 주문 제출
        try:
            if market == "KR":
                result = client.buy(signal.symbol, quantity, price_arg, order_type)
            else:
                limit_price = current_price if order_type == "LIMIT" else None
                result = client.buy(signal.symbol, quantity, limit_price, order_type)
        except Exception as e:
            update_order_status(order_id, "REJECTED")
            logger.error("주문 제출 실패 [%s]: %s", signal.symbol, e)
            return {"success": False, "reason": f"주문 실패: {e}"}

        if result.get("success"):
            update_order_status(
                order_id, "FILLED",
                filled_price=current_price,
                filled_quantity=quantity,
                broker_order_id=result.get("order_id", ""),
            )
            # 포지션 개설
            position_id = self.positions.open_position(
                market=market,
                symbol=signal.symbol,
                name=name,
                quantity=quantity,
                entry_price=current_price,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                signal_score=signal.score,
            )
            msg = (
                f"[매수] {market} {signal.symbol} {name}\n"
                f"  수량: {quantity} / 가격: {current_price:,.2f}\n"
                f"  신호 점수: {signal.score:.0f} / 손절: {signal.stop_loss:,.2f}\n"
                f"  주문금액: {order_amount:,.0f}"
            )
            logger.info(msg)
            return {
                "success": True,
                "position_id": position_id,
                "quantity": quantity,
                "price": current_price,
                "message": msg,
            }
        else:
            update_order_status(order_id, "REJECTED")
            return {"success": False, "reason": result.get("message", "주문 거부")}

    def execute_sell(self, market: str, position: dict) -> dict:
        """매도 주문 실행 (포지션 청산)"""
        client = self._get_market_client(market)
        symbol = position["symbol"]
        quantity = position["quantity"]

        try:
            price_data = client.get_price(symbol)
            current_price = price_data.get("price", 0)
        except Exception as e:
            logger.error("시세 조회 실패 [%s]: %s", symbol, e)
            return {"success": False, "reason": f"시세 조회 실패: {e}"}

        # DB에 주문 기록
        order_id = insert_order(
            market=market,
            symbol=symbol,
            side="SELL",
            order_type="MARKET",
            quantity=quantity,
            price=current_price,
            position_id=position["id"],
        )

        # 실제 주문 제출
        try:
            result = client.sell(symbol, quantity, order_type="MARKET")
        except Exception as e:
            update_order_status(order_id, "REJECTED")
            return {"success": False, "reason": f"매도 실패: {e}"}

        if result.get("success"):
            entry_price = position["entry_price"]
            realized_pnl = (current_price - entry_price) * quantity
            if market == "US":
                # USD 기준 손익
                realized_pnl_display = realized_pnl
            else:
                realized_pnl_display = realized_pnl

            update_order_status(
                order_id, "FILLED",
                filled_price=current_price,
                filled_quantity=quantity,
                broker_order_id=result.get("order_id", ""),
            )
            self.positions.close_position_by_id(
                position["id"], current_price, realized_pnl,
            )
            msg = (
                f"[매도] {market} {symbol}\n"
                f"  수량: {quantity} / 가격: {current_price:,.2f}\n"
                f"  진입가: {entry_price:,.2f} / 실현손익: {realized_pnl_display:,.2f}"
            )
            logger.info(msg)
            return {
                "success": True,
                "realized_pnl": realized_pnl,
                "message": msg,
            }
        else:
            update_order_status(order_id, "REJECTED")
            return {"success": False, "reason": result.get("message", "매도 거부")}

    def process_signals(self, market: str, signals: list[Signal],
                        balance: dict) -> list[dict]:
        """신호 목록을 처리하여 매수 실행"""
        results = []
        for signal in signals:
            if signal.signal_type != "BUY":
                continue
            result = self.execute_buy(market, signal, balance, name=signal.symbol)
            results.append(result)
            if result.get("success"):
                # 잔고 업데이트 (재계산이 필요하나 간략화)
                balance["cash"] -= result["price"] * result["quantity"]
        return results

    def process_sell_signals(self, market: str, signals: list[Signal]) -> list[dict]:
        """매도 신호에 따라 보유 포지션 청산"""
        results = []
        sell_symbols = {s.symbol for s in signals if s.signal_type == "SELL"}
        positions = self.positions.get_all_open(market)

        for pos in positions:
            if pos["symbol"] in sell_symbols:
                result = self.execute_sell(market, pos)
                results.append(result)

        return results

    def check_and_execute_stop_losses(self) -> list[dict]:
        """손절가 도달 포지션 자동 청산"""
        market_clients = {"KR": self.kr_market, "US": self.us_market}
        triggered = self.positions.check_stop_loss(market_clients)
        results = []

        for item in triggered:
            pos = item["position"]
            logger.warning("손절 실행: %s %s — %s", pos["market"], pos["symbol"], item["reason"])
            result = self.execute_sell(pos["market"], pos)
            result["stop_loss_reason"] = item["reason"]
            results.append(result)

        return results

    def cancel_unfilled_kr_orders(self):
        """한국 장 마감 전 미체결 주문 취소"""
        from db.models import get_connection
        conn = get_connection()
        pending = conn.execute(
            "SELECT * FROM orders WHERE market='KR' AND status='PENDING'"
        ).fetchall()
        conn.close()

        for order in pending:
            order_dict = dict(order)
            broker_id = order_dict.get("broker_order_id", "")
            if broker_id:
                try:
                    result = self.kr_market.cancel_order(
                        broker_id, order_dict["quantity"]
                    )
                    if result.get("success"):
                        update_order_status(order_dict["id"], "CANCELLED")
                        logger.info("미체결 주문 취소: %s", broker_id)
                except Exception as e:
                    logger.error("주문 취소 실패: %s", e)
