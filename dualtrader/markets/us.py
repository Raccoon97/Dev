"""
Alpaca Markets API 래퍼
미국 시장 (NYSE/NASDAQ) 데이터 조회 및 주문 실행
"""

import logging
import requests
import pandas as pd
from datetime import datetime, timedelta

from config import AlpacaConfig

logger = logging.getLogger(__name__)


class USMarket:
    """Alpaca Markets 클라이언트"""

    def __init__(self):
        self.base_url = AlpacaConfig.BASE_URL
        self.data_url = AlpacaConfig.DATA_URL
        self.api_key = AlpacaConfig.API_KEY
        self.secret_key = AlpacaConfig.SECRET_KEY

    def _headers(self) -> dict:
        return {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.secret_key,
            "Content-Type": "application/json",
        }

    def _get(self, url: str, params: dict = None) -> dict:
        resp = requests.get(url, headers=self._headers(), params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _post(self, url: str, body: dict = None) -> dict:
        resp = requests.post(url, headers=self._headers(), json=body, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _delete(self, url: str) -> dict:
        resp = requests.delete(url, headers=self._headers(), timeout=10)
        if resp.status_code == 204:
            return {"success": True}
        resp.raise_for_status()
        return resp.json()

    # ──────────────────────────────────────────
    # 계좌 정보
    # ──────────────────────────────────────────
    def get_account(self) -> dict:
        """계좌 정보 조회"""
        data = self._get(f"{self.base_url}/v2/account")
        return {
            "cash": float(data.get("cash", 0)),
            "portfolio_value": float(data.get("portfolio_value", 0)),
            "equity": float(data.get("equity", 0)),
            "buying_power": float(data.get("buying_power", 0)),
        }

    def get_positions(self) -> list[dict]:
        """보유 포지션 조회"""
        data = self._get(f"{self.base_url}/v2/positions")
        positions = []
        for item in data:
            positions.append({
                "symbol": item["symbol"],
                "quantity": int(item["qty"]),
                "avg_price": float(item["avg_entry_price"]),
                "current_price": float(item["current_price"]),
                "market_value": float(item["market_value"]),
                "pnl": float(item["unrealized_pl"]),
                "pnl_pct": float(item["unrealized_plpc"]) * 100,
            })
        return positions

    def get_balance(self) -> dict:
        """잔고 요약"""
        account = self.get_account()
        positions = self.get_positions()
        stock_value = sum(p["market_value"] for p in positions)
        return {
            "holdings": positions,
            "total_value": account["portfolio_value"],
            "cash": account["cash"],
            "stock_value": stock_value,
        }

    # ──────────────────────────────────────────
    # 시세 데이터
    # ──────────────────────────────────────────
    def get_price(self, symbol: str) -> dict:
        """최신 시세 조회"""
        data = self._get(
            f"{self.data_url}/v2/stocks/{symbol}/quotes/latest"
        )
        quote = data.get("quote", {})
        # 스냅샷에서 trade 정보도 조회
        try:
            trade_data = self._get(
                f"{self.data_url}/v2/stocks/{symbol}/trades/latest"
            )
            last_price = float(trade_data.get("trade", {}).get("p", 0))
        except Exception:
            last_price = float(quote.get("ap", 0))

        return {
            "symbol": symbol,
            "price": last_price,
            "bid": float(quote.get("bp", 0)),
            "ask": float(quote.get("ap", 0)),
        }

    def get_ohlcv(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """일봉 OHLCV 데이터 조회 (최근 N거래일)"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days * 2)).strftime("%Y-%m-%d")
        params = {
            "start": start_date,
            "end": end_date,
            "timeframe": "1Day",
            "limit": days * 2,
            "adjustment": "split",
            "feed": "iex",
        }
        data = self._get(
            f"{self.data_url}/v2/stocks/{symbol}/bars",
            params=params,
        )
        bars = data.get("bars", [])
        if not bars:
            return pd.DataFrame()

        df = pd.DataFrame(bars)
        df = df.rename(columns={
            "t": "date", "o": "open", "h": "high",
            "l": "low", "c": "close", "v": "volume",
        })
        df["date"] = pd.to_datetime(df["date"])
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.sort_values("date").reset_index(drop=True)
        return df[["date", "open", "high", "low", "close", "volume"]].tail(days)

    def get_snapshot(self, symbol: str) -> dict:
        """종목 스냅샷 (일간 바 + 시세)"""
        data = self._get(
            f"{self.data_url}/v2/stocks/{symbol}/snapshot"
        )
        daily = data.get("dailyBar", {})
        return {
            "symbol": symbol,
            "price": float(daily.get("c", 0)),
            "open": float(daily.get("o", 0)),
            "high": float(daily.get("h", 0)),
            "low": float(daily.get("l", 0)),
            "volume": int(daily.get("v", 0)),
        }

    # ──────────────────────────────────────────
    # 주문 실행
    # ──────────────────────────────────────────
    def buy(self, symbol: str, quantity: int, price: float = None,
            order_type: str = "MARKET") -> dict:
        """매수 주문"""
        body = {
            "symbol": symbol,
            "qty": str(quantity),
            "side": "buy",
            "type": "market" if order_type == "MARKET" else "limit",
            "time_in_force": "day",
        }
        if order_type == "LIMIT" and price:
            body["limit_price"] = str(price)
        try:
            data = self._post(f"{self.base_url}/v2/orders", body=body)
            return {
                "success": True,
                "order_id": data.get("id", ""),
                "status": data.get("status", ""),
                "message": f"Order placed: {data.get('id', '')}",
            }
        except requests.HTTPError as e:
            logger.error("매수 주문 실패 [%s]: %s", symbol, e)
            return {"success": False, "order_id": "", "message": str(e)}

    def sell(self, symbol: str, quantity: int, price: float = None,
             order_type: str = "MARKET") -> dict:
        """매도 주문"""
        body = {
            "symbol": symbol,
            "qty": str(quantity),
            "side": "sell",
            "type": "market" if order_type == "MARKET" else "limit",
            "time_in_force": "day",
        }
        if order_type == "LIMIT" and price:
            body["limit_price"] = str(price)
        try:
            data = self._post(f"{self.base_url}/v2/orders", body=body)
            return {
                "success": True,
                "order_id": data.get("id", ""),
                "status": data.get("status", ""),
                "message": f"Order placed: {data.get('id', '')}",
            }
        except requests.HTTPError as e:
            logger.error("매도 주문 실패 [%s]: %s", symbol, e)
            return {"success": False, "order_id": "", "message": str(e)}

    def cancel_order(self, order_id: str) -> dict:
        """주문 취소"""
        try:
            self._delete(f"{self.base_url}/v2/orders/{order_id}")
            return {"success": True, "message": "Order cancelled"}
        except requests.HTTPError as e:
            return {"success": False, "message": str(e)}

    def get_order(self, order_id: str) -> dict:
        """주문 상태 조회"""
        data = self._get(f"{self.base_url}/v2/orders/{order_id}")
        return {
            "order_id": data.get("id", ""),
            "symbol": data.get("symbol", ""),
            "side": data.get("side", ""),
            "status": data.get("status", ""),
            "filled_qty": int(data.get("filled_qty", 0)),
            "filled_avg_price": float(data.get("filled_avg_price", 0) or 0),
        }

    def cancel_all_orders(self) -> dict:
        """모든 미체결 주문 취소"""
        try:
            self._delete(f"{self.base_url}/v2/orders")
            return {"success": True, "message": "All orders cancelled"}
        except requests.HTTPError as e:
            return {"success": False, "message": str(e)}

    def is_market_open(self) -> bool:
        """미국 장 운영 시간 확인"""
        try:
            data = self._get(f"{self.base_url}/v2/clock")
            return data.get("is_open", False)
        except Exception:
            from zoneinfo import ZoneInfo
            now = datetime.now(ZoneInfo("US/Eastern"))
            if now.weekday() >= 5:
                return False
            market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
            return market_open <= now <= market_close
