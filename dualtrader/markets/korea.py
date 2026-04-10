"""
한국투자증권 OpenAPI 래퍼
KRX(코스피/코스닥) 시장 데이터 조회 및 주문 실행
"""

import time
import logging
import requests
import pandas as pd
from datetime import datetime, timedelta

from config import KISConfig

logger = logging.getLogger(__name__)


class KoreaMarket:
    """한국투자증권 OpenAPI 클라이언트"""

    def __init__(self):
        self.base_url = KISConfig.BASE_URL
        self.app_key = KISConfig.APP_KEY
        self.app_secret = KISConfig.APP_SECRET
        self.account_no = KISConfig.ACCOUNT_NO
        self.account_product = KISConfig.ACCOUNT_PRODUCT
        self.access_token = None
        self.token_expires_at = None
        self._request_timestamps: list[float] = []
        self._rate_limit_per_sec = 10  # 초당 최대 요청 수

    # ──────────────────────────────────────────
    # 인증
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
        logger.info("KIS 인증 토큰 발급 완료 (만료: %s)", self.token_expires_at)

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
    # 속도 제한 처리
    # ──────────────────────────────────────────
    def _throttle(self):
        """초당 요청 제한 준수"""
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
        """현재가 조회"""
        tr_id = "FHKST01010100"
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": symbol,
        }
        data = self._get(
            "/uapi/domestic-stock/v1/quotations/inquire-price",
            params=params,
            tr_id=tr_id,
        )
        output = data.get("output", {})
        return {
            "symbol": symbol,
            "price": float(output.get("stck_prpr", 0)),
            "change": float(output.get("prdy_vrss", 0)),
            "change_pct": float(output.get("prdy_ctrt", 0)),
            "volume": int(output.get("acml_vol", 0)),
            "high": float(output.get("stck_hgpr", 0)),
            "low": float(output.get("stck_lwpr", 0)),
            "open": float(output.get("stck_oprc", 0)),
        }

    def get_ohlcv(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """일봉 OHLCV 데이터 조회 (최근 N거래일)"""
        tr_id = "FHKST01010400"
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days * 2)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": symbol,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date,
            "FID_PERIOD_DIV_CODE": "D",
            "FID_ORG_ADJ_PRC": "0",
        }
        data = self._get(
            "/uapi/domestic-stock/v1/quotations/inquire-daily-price",
            params=params,
            tr_id=tr_id,
        )
        records = data.get("output", [])
        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)
        df = df.rename(columns={
            "stck_bsop_date": "date",
            "stck_oprc": "open",
            "stck_hgpr": "high",
            "stck_lwpr": "low",
            "stck_clpr": "close",
            "acml_vol": "volume",
        })
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        return df[["date", "open", "high", "low", "close", "volume"]].tail(days)

    # ──────────────────────────────────────────
    # 계좌 정보
    # ──────────────────────────────────────────
    def get_balance(self) -> dict:
        """계좌 잔고 조회"""
        tr_id = "VTTC8434R" if KISConfig.IS_PAPER else "TTTC8434R"
        params = {
            "CANO": self.account_no[:8],
            "ACNT_PRDT_CD": self.account_product,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "02",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "00",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
        }
        data = self._get(
            "/uapi/domestic-stock/v1/trading/inquire-balance",
            params=params,
            tr_id=tr_id,
        )
        holdings = []
        for item in data.get("output1", []):
            if int(item.get("hldg_qty", 0)) > 0:
                holdings.append({
                    "symbol": item["pdno"],
                    "name": item["prdt_name"],
                    "quantity": int(item["hldg_qty"]),
                    "avg_price": float(item["pchs_avg_pric"]),
                    "current_price": float(item["prpr"]),
                    "pnl": float(item["evlu_pfls_amt"]),
                    "pnl_pct": float(item["evlu_pfls_rt"]),
                })
        summary = data.get("output2", [{}])[0] if data.get("output2") else {}
        return {
            "holdings": holdings,
            "total_value": float(summary.get("tot_evlu_amt", 0)),
            "cash": float(summary.get("dnca_tot_amt", 0)),
            "stock_value": float(summary.get("scts_evlu_amt", 0)),
        }

    # ──────────────────────────────────────────
    # 주문 실행
    # ──────────────────────────────────────────
    def buy(self, symbol: str, quantity: int, price: int = 0,
            order_type: str = "MARKET") -> dict:
        """매수 주문"""
        tr_id = "VTTC0802U" if KISConfig.IS_PAPER else "TTTC0802U"
        # 시장가: 01, 지정가: 00
        ord_dvsn = "01" if order_type == "MARKET" else "00"
        body = {
            "CANO": self.account_no[:8],
            "ACNT_PRDT_CD": self.account_product,
            "PDNO": symbol,
            "ORD_DVSN": ord_dvsn,
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price) if order_type == "LIMIT" else "0",
        }
        data = self._post(
            "/uapi/domestic-stock/v1/trading/order-cash",
            body=body,
            tr_id=tr_id,
        )
        output = data.get("output", {})
        return {
            "success": data.get("rt_cd") == "0",
            "order_id": output.get("ODNO", ""),
            "message": data.get("msg1", ""),
        }

    def sell(self, symbol: str, quantity: int, price: int = 0,
             order_type: str = "MARKET") -> dict:
        """매도 주문"""
        tr_id = "VTTC0801U" if KISConfig.IS_PAPER else "TTTC0801U"
        ord_dvsn = "01" if order_type == "MARKET" else "00"
        body = {
            "CANO": self.account_no[:8],
            "ACNT_PRDT_CD": self.account_product,
            "PDNO": symbol,
            "ORD_DVSN": ord_dvsn,
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price) if order_type == "LIMIT" else "0",
        }
        data = self._post(
            "/uapi/domestic-stock/v1/trading/order-cash",
            body=body,
            tr_id=tr_id,
        )
        output = data.get("output", {})
        return {
            "success": data.get("rt_cd") == "0",
            "order_id": output.get("ODNO", ""),
            "message": data.get("msg1", ""),
        }

    def cancel_order(self, order_id: str, quantity: int) -> dict:
        """주문 취소"""
        tr_id = "VTTC0803U" if KISConfig.IS_PAPER else "TTTC0803U"
        body = {
            "CANO": self.account_no[:8],
            "ACNT_PRDT_CD": self.account_product,
            "KRX_FWDG_ORD_ORGNO": "",
            "ORGN_ODNO": order_id,
            "ORD_DVSN": "00",
            "RVSE_CNCL_DVSN_CD": "02",  # 취소
            "ORD_QTY": str(quantity),
            "ORD_UNPR": "0",
            "QTY_ALL_ORD_YN": "Y",
        }
        data = self._post(
            "/uapi/domestic-stock/v1/trading/order-rvsecncl",
            body=body,
            tr_id=tr_id,
        )
        return {
            "success": data.get("rt_cd") == "0",
            "message": data.get("msg1", ""),
        }

    # ──────────────────────────────────────────
    # 종목 정보
    # ──────────────────────────────────────────
    def get_stock_info(self, symbol: str) -> dict:
        """종목 기본 정보 조회"""
        tr_id = "CTPF1002R"
        params = {
            "PRDT_TYPE_CD": "300",
            "PDNO": symbol,
        }
        try:
            data = self._get(
                "/uapi/domestic-stock/v1/quotations/search-stock-info",
                params=params,
                tr_id=tr_id,
            )
            output = data.get("output", {})
            return {
                "symbol": symbol,
                "name": output.get("prdt_abrv_name", ""),
                "market_cap": float(output.get("lstg_stqt", 0)) * float(output.get("stck_prpr", 0)),
            }
        except Exception as e:
            logger.warning("종목 정보 조회 실패 [%s]: %s", symbol, e)
            return {"symbol": symbol, "name": "", "market_cap": 0}

    def is_market_open(self) -> bool:
        """한국 장 운영 시간 확인"""
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("Asia/Seoul"))
        # 평일 09:00 ~ 15:30
        if now.weekday() >= 5:  # 토,일
            return False
        market_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        return market_open <= now <= market_close
