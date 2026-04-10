"""
한국투자증권 OpenAPI 래퍼 — 미국 시장 (NYSE/NASDAQ)
KIS 해외주식 API를 통해 미국 주식 데이터 조회 및 주문 실행
"""

import time
import logging
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

from config import KISConfig

logger = logging.getLogger(__name__)


class USMarket:
    """한국투자증권 해외주식 API 클라이언트"""

    def __init__(self):
        self.base_url = KISConfig.BASE_URL
        self.app_key = KISConfig.APP_KEY
        self.app_secret = KISConfig.APP_SECRET
        self.account_no = KISConfig.ACCOUNT_NO
        self.account_product = KISConfig.ACCOUNT_PRODUCT
        self.access_token = None
        self.token_expires_at = None
        self._request_timestamps: list[float] = []
        self._rate_limit_per_sec = 10

    # ──────────────────────────────────────────
    # 인증 (한국 시장과 동일한 토큰 사용)
    # ──────────────────────────────────────────
    def authenticate(self):
        """OAuth 토큰 발급"""
        url = f"{self.base_url}/oauth2/tokenP"
        body = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
        }
        resp = requests.post(url, json=body, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        self.access_token = data["access_token"]
        self.token_expires_at = datetime.now() + timedelta(hours=23)
        logger.info("KIS 해외주식 인증 토큰 발급 완료")

    def _ensure_token(self):
        if not self.access_token or datetime.now() >= self.token_expires_at:
            self.authenticate()

    def _headers(self) -> dict:
        self._ensure_token()
        return {
            "Content-Type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
        }

    # ──────────────────────────────────────────
    # 속도 제한
    # ──────────────────────────────────────────
    def _throttle(self):
        now = time.time()
        self._request_timestamps = [
            t for t in self._request_timestamps if now - t < 1.0
        ]
        if len(self._request_timestamps) >= self._rate_limit_per_sec:
            sleep_time = 1.0 - (now - self._request_timestamps[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        self._request_timestamps.append(time.time())

    def _get(self, path: str, params: dict = None, tr_id: str = "") -> dict:
        self._throttle()
        headers = self._headers()
        if tr_id:
            headers["tr_id"] = tr_id
        resp = requests.get(
            f"{self.base_url}{path}",
            headers=headers,
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, body: dict = None, tr_id: str = "") -> dict:
        self._throttle()
        headers = self._headers()
        if tr_id:
            headers["tr_id"] = tr_id
        resp = requests.post(
            f"{self.base_url}{path}",
            headers=headers,
            json=body,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    # ──────────────────────────────────────────
    # 시세 데이터
    # ──────────────────────────────────────────
    def get_price(self, symbol: str) -> dict:
        """미국 주식 현재가 조회"""
        tr_id = "HHDFS00000300"
        params = {
            "AUTH": "",
            "EXCD": "NAS",  # NAS: 나스닥, NYS: 뉴욕, AMS: 아멕스
            "SYMB": symbol,
        }
        # 거래소 자동 판별
        exchange = self._detect_exchange(symbol)
        params["EXCD"] = exchange

        data = self._get(
            "/uapi/overseas-price/v1/quotations/price",
            params=params,
            tr_id=tr_id,
        )
        output = data.get("output", {})
        return {
            "symbol": symbol,
            "price": float(output.get("last", 0) or 0),
            "change": float(output.get("diff", 0) or 0),
            "change_pct": float(output.get("rate", 0) or 0),
            "volume": int(output.get("tvol", 0) or 0),
            "high": float(output.get("high", 0) or 0),
            "low": float(output.get("low", 0) or 0),
            "open": float(output.get("open", 0) or 0),
        }

    def get_ohlcv(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """미국 주식 일봉 데이터 조회 — yfinance 사용 (KIS 일봉 API 제한 보완)"""
        try:
            ticker = yf.Ticker(symbol)
            # 충분한 기간 확보
            df = ticker.history(period=f"{days * 2}d")
            if df.empty:
                return pd.DataFrame()

            df = df.reset_index()
            df = df.rename(columns={
                "Date": "date", "Open": "open", "High": "high",
                "Low": "low", "Close": "close", "Volume": "volume",
            })
            df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
            for col in ["open", "high", "low", "close", "volume"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            df = df.sort_values("date").reset_index(drop=True)
            return df[["date", "open", "high", "low", "close", "volume"]].tail(days)
        except Exception as e:
            logger.error("yfinance OHLCV 조회 실패 [%s]: %s", symbol, e)
            return pd.DataFrame()

    # ──────────────────────────────────────────
    # 계좌 정보
    # ──────────────────────────────────────────
    def get_balance(self) -> dict:
        """해외주식 잔고 조회"""
        tr_id = "VTTS3012R" if KISConfig.IS_PAPER else "TTTS3012R"
        params = {
            "CANO": self.account_no[:8],
            "ACNT_PRDT_CD": self.account_product,
            "OVRS_EXCG_CD": "NASD",
            "TR_CRCY_CD": "USD",
            "CTX_AREA_FK200": "",
            "CTX_AREA_NK200": "",
        }
        data = self._get(
            "/uapi/overseas-stock/v1/trading/inquire-balance",
            params=params,
            tr_id=tr_id,
        )
        holdings = []
        for item in data.get("output1", []):
            qty = int(item.get("ovrs_cblc_qty", 0) or 0)
            if qty > 0:
                avg_price = float(item.get("pchs_avg_pric", 0) or 0)
                current_price = float(item.get("now_pric2", 0) or item.get("ovrs_now_pric", 0) or 0)
                eval_amt = float(item.get("frcr_evlu_pfls_amt", 0) or 0)
                holdings.append({
                    "symbol": item.get("ovrs_pdno", ""),
                    "name": item.get("ovrs_item_name", ""),
                    "quantity": qty,
                    "avg_price": avg_price,
                    "current_price": current_price,
                    "pnl": eval_amt,
                    "pnl_pct": ((current_price - avg_price) / avg_price * 100) if avg_price else 0,
                })

        summary = data.get("output2", [{}])[0] if data.get("output2") else {}
        total_value = float(summary.get("tot_evlu_pfls_amt", 0) or 0)
        cash = float(summary.get("frcr_use_psbl_amt", 0) or summary.get("ovrs_ord_psbl_amt", 0) or 0)
        stock_value = sum(
            h["current_price"] * h["quantity"] for h in holdings
        )

        return {
            "holdings": holdings,
            "total_value": cash + stock_value,
            "cash": cash,
            "stock_value": stock_value,
        }

    # ──────────────────────────────────────────
    # 주문 실행
    # ──────────────────────────────────────────
    def buy(self, symbol: str, quantity: int, price: float = 0,
            order_type: str = "MARKET") -> dict:
        """해외주식 매수 주문"""
        tr_id = "VTTT1002U" if KISConfig.IS_PAPER else "JTTT1002U"
        exchange = self._detect_exchange(symbol)
        excd_map = {"NAS": "NASD", "NYS": "NYSE", "AMS": "AMEX"}
        ovrs_excg_cd = excd_map.get(exchange, "NASD")

        # KIS 해외주식: 지정가만 지원, 시장가 주문은 현재가로 지정가 제출
        if order_type == "MARKET" and price <= 0:
            try:
                price_data = self.get_price(symbol)
                price = price_data.get("price", 0)
            except Exception:
                pass

        body = {
            "CANO": self.account_no[:8],
            "ACNT_PRDT_CD": self.account_product,
            "OVRS_EXCG_CD": ovrs_excg_cd,
            "PDNO": symbol,
            "ORD_QTY": str(quantity),
            "OVRS_ORD_UNPR": f"{price:.2f}",
            "ORD_SVR_DVSN_CD": "0",
            "ORD_DVSN": "00",  # 지정가
        }
        try:
            data = self._post(
                "/uapi/overseas-stock/v1/trading/order",
                body=body,
                tr_id=tr_id,
            )
            output = data.get("output", {})
            success = data.get("rt_cd") == "0"
            return {
                "success": success,
                "order_id": output.get("ODNO", "") or output.get("ORD_TMD", ""),
                "message": data.get("msg1", ""),
            }
        except Exception as e:
            logger.error("해외주식 매수 실패 [%s]: %s", symbol, e)
            return {"success": False, "order_id": "", "message": str(e)}

    def sell(self, symbol: str, quantity: int, price: float = 0,
             order_type: str = "MARKET") -> dict:
        """해외주식 매도 주문"""
        tr_id = "VTTT1001U" if KISConfig.IS_PAPER else "JTTT1006U"
        exchange = self._detect_exchange(symbol)
        excd_map = {"NAS": "NASD", "NYS": "NYSE", "AMS": "AMEX"}
        ovrs_excg_cd = excd_map.get(exchange, "NASD")

        if order_type == "MARKET" and price <= 0:
            try:
                price_data = self.get_price(symbol)
                price = price_data.get("price", 0)
            except Exception:
                pass

        body = {
            "CANO": self.account_no[:8],
            "ACNT_PRDT_CD": self.account_product,
            "OVRS_EXCG_CD": ovrs_excg_cd,
            "PDNO": symbol,
            "ORD_QTY": str(quantity),
            "OVRS_ORD_UNPR": f"{price:.2f}",
            "ORD_SVR_DVSN_CD": "0",
            "ORD_DVSN": "00",
        }
        try:
            data = self._post(
                "/uapi/overseas-stock/v1/trading/order",
                body=body,
                tr_id=tr_id,
            )
            output = data.get("output", {})
            success = data.get("rt_cd") == "0"
            return {
                "success": success,
                "order_id": output.get("ODNO", "") or output.get("ORD_TMD", ""),
                "message": data.get("msg1", ""),
            }
        except Exception as e:
            logger.error("해외주식 매도 실패 [%s]: %s", symbol, e)
            return {"success": False, "order_id": "", "message": str(e)}

    def cancel_order(self, order_id: str, quantity: int = 0) -> dict:
        """해외주식 주문 취소"""
        tr_id = "VTTT1004U" if KISConfig.IS_PAPER else "JTTT1004U"
        body = {
            "CANO": self.account_no[:8],
            "ACNT_PRDT_CD": self.account_product,
            "OVRS_EXCG_CD": "NASD",
            "ORGN_ODNO": order_id,
            "RVSE_CNCL_DVSN_CD": "02",  # 취소
            "ORD_QTY": str(quantity),
            "OVRS_ORD_UNPR": "0",
        }
        try:
            data = self._post(
                "/uapi/overseas-stock/v1/trading/order-rvsecncl",
                body=body,
                tr_id=tr_id,
            )
            return {
                "success": data.get("rt_cd") == "0",
                "message": data.get("msg1", ""),
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def cancel_all_orders(self) -> dict:
        """미체결 해외주식 주문 전체 취소"""
        from db.models import get_connection
        conn = get_connection()
        pending = conn.execute(
            "SELECT * FROM orders WHERE market='US' AND status='PENDING'"
        ).fetchall()
        conn.close()

        cancelled = 0
        for order in pending:
            order_dict = dict(order)
            broker_id = order_dict.get("broker_order_id", "")
            if broker_id:
                result = self.cancel_order(broker_id, order_dict.get("quantity", 0))
                if result.get("success"):
                    from db.models import update_order_status
                    update_order_status(order_dict["id"], "CANCELLED")
                    cancelled += 1

        return {"success": True, "message": f"{cancelled}건 취소 완료"}

    # ──────────────────────────────────────────
    # 유틸리티
    # ──────────────────────────────────────────
    def _detect_exchange(self, symbol: str) -> str:
        """종목 심볼로 거래소 추정 (NAS/NYS/AMS)"""
        # 주요 NYSE 종목
        nyse_symbols = {
            "BRK-B", "JPM", "JNJ", "V", "PG", "UNH", "HD", "MA", "DIS",
            "XOM", "CVX", "MRK", "ABBV", "KO", "PEP", "WMT", "TMO",
            "BA", "GS", "MS", "NKE", "COST",
        }
        if symbol.upper() in nyse_symbols:
            return "NYS"
        # 대부분 나스닥으로 기본 처리
        return "NAS"

    def is_market_open(self) -> bool:
        """미국 장 운영 시간 확인 (KST 기준)"""
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("US/Eastern"))
        if now.weekday() >= 5:
            return False
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        return market_open <= now <= market_close

    def share_token(self, token: str, expires_at):
        """한국 시장 클라이언트에서 토큰 공유 (같은 KIS 계정)"""
        self.access_token = token
        self.token_expires_at = expires_at
        logger.info("KIS 토큰 공유 완료 (해외주식)")
