"""
종목 스크리너
한국/미국 시장에서 관심 종목을 선정합니다.
코스피200, S&P500 등 유니버스에서 거래량, 시가총액 기준 필터링
"""

import logging
import yfinance as yf
import pandas as pd

from config import ScreenerConfig

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# 유니버스 정의
# ──────────────────────────────────────────────

# 코스피200 대표 종목 (심볼 코드)
KOSPI200_MAJOR = [
    "005930",  # 삼성전자
    "000660",  # SK하이닉스
    "373220",  # LG에너지솔루션
    "207940",  # 삼성바이오로직스
    "005380",  # 현대차
    "006400",  # 삼성SDI
    "051910",  # LG화학
    "035420",  # NAVER
    "000270",  # 기아
    "068270",  # 셀트리온
    "035720",  # 카카오
    "105560",  # KB금융
    "055550",  # 신한지주
    "034730",  # SK
    "012330",  # 현대모비스
    "003670",  # 포스코퓨처엠
    "028260",  # 삼성물산
    "066570",  # LG전자
    "032830",  # 삼성생명
    "096770",  # SK이노베이션
    "003550",  # LG
    "015760",  # 한국전력
    "034020",  # 두산에너빌리티
    "086790",  # 하나금융지주
    "011200",  # HMM
    "010130",  # 고려아연
    "033780",  # KT&G
    "018260",  # 삼성에스디에스
    "009150",  # 삼성전기
    "030200",  # KT
]

# S&P500 / NASDAQ100 대표 종목
SP500_MAJOR = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL",
    "META", "TSLA", "BRK-B", "UNH", "XOM",
    "JNJ", "JPM", "V", "PG", "AVGO",
    "HD", "MA", "CVX", "MRK", "ABBV",
    "COST", "PEP", "KO", "WMT", "LLY",
    "TMO", "ADBE", "CRM", "NFLX", "AMD",
    "INTC", "QCOM", "DIS", "ORCL", "NKE",
    "BA", "GS", "MS", "PYPL", "SQ",
    "UBER", "ABNB", "COIN", "SNOW", "PLTR",
    "SOFI", "RIVN", "LCID", "NET", "CRWD",
]


class Screener:
    """종목 스크리닝 엔진"""

    def __init__(self):
        self.cfg = ScreenerConfig

    def get_kr_universe(self) -> list[str]:
        """한국 유니버스 종목 반환"""
        return KOSPI200_MAJOR.copy()

    def get_us_universe(self) -> list[str]:
        """미국 유니버스 종목 반환"""
        return SP500_MAJOR.copy()

    def screen_kr_stocks(self, kr_market) -> list[str]:
        """한국 시장 종목 스크리닝 — 거래량 기준 상위 종목 선정"""
        universe = self.get_kr_universe()
        candidates = []

        for symbol in universe:
            try:
                price_data = kr_market.get_price(symbol)
                volume = price_data.get("volume", 0)
                price = price_data.get("price", 0)
                if volume > 0 and price > 0:
                    candidates.append({
                        "symbol": symbol,
                        "price": price,
                        "volume": volume,
                        "score": volume,  # 거래량 기준 정렬
                    })
            except Exception as e:
                logger.warning("KR 스크리닝 실패 [%s]: %s", symbol, e)
                continue

        # 거래량 상위 정렬
        candidates.sort(key=lambda x: x["score"], reverse=True)
        top = [c["symbol"] for c in candidates[:self.cfg.TOP_N_CANDIDATES]]
        logger.info("KR 스크리닝 완료: %d종목 선정", len(top))
        return top

    def screen_us_stocks(self, us_market=None) -> list[str]:
        """미국 시장 종목 스크리닝 — yfinance로 거래량/시총 기준 필터링"""
        universe = self.get_us_universe()
        candidates = []

        for symbol in universe:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.fast_info
                market_cap = getattr(info, "market_cap", 0) or 0
                volume = getattr(info, "last_volume", 0) or 0
                price = getattr(info, "last_price", 0) or 0

                if price > 0 and volume > 0:
                    candidates.append({
                        "symbol": symbol,
                        "price": price,
                        "volume": volume,
                        "market_cap": market_cap,
                        "score": volume,
                    })
            except Exception as e:
                logger.warning("US 스크리닝 실패 [%s]: %s", symbol, e)
                continue

        # 거래량 기준 정렬
        candidates.sort(key=lambda x: x["score"], reverse=True)
        top = [c["symbol"] for c in candidates[:self.cfg.TOP_N_CANDIDATES]]
        logger.info("US 스크리닝 완료: %d종목 선정", len(top))
        return top

    def screen_us_stocks_via_yfinance(self) -> list[str]:
        """yfinance만 사용한 미국 종목 스크리닝 (API 키 없이 가능)"""
        return self.screen_us_stocks(us_market=None)
