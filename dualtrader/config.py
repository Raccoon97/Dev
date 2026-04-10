"""
DualTrader 설정 모듈
API 키, 파라미터, 시스템 설정을 관리합니다.
환경변수(.env)로 민감 정보를 관리합니다.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv(Path(__file__).parent.parent / ".env")


# ──────────────────────────────────────────────
# API 키 설정
# ──────────────────────────────────────────────
class KISConfig:
    """한국투자증권 OpenAPI 설정"""
    APP_KEY = os.getenv("KIS_APP_KEY", "")
    APP_SECRET = os.getenv("KIS_APP_SECRET", "")
    ACCOUNT_NO = os.getenv("KIS_ACCOUNT_NO", "")          # 계좌번호 (8자리-2자리)
    ACCOUNT_PRODUCT = os.getenv("KIS_ACCOUNT_PRODUCT", "01")
    BASE_URL = os.getenv("KIS_BASE_URL", "https://openapivts.koreainvestment.com:29443")  # 모의투자
    # 실거래: https://openapi.koreainvestment.com:9443
    IS_PAPER = os.getenv("KIS_IS_PAPER", "true").lower() == "true"


class AlpacaConfig:
    """Alpaca Markets API 설정"""
    API_KEY = os.getenv("ALPACA_API_KEY", "")
    SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
    BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")  # 페이퍼
    # 실거래: https://api.alpaca.markets
    DATA_URL = "https://data.alpaca.markets"
    IS_PAPER = os.getenv("ALPACA_IS_PAPER", "true").lower() == "true"


class TelegramConfig:
    """텔레그램 봇 설정"""
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


# ──────────────────────────────────────────────
# 자금 관리 설정
# ──────────────────────────────────────────────
class FundConfig:
    INITIAL_CAPITAL_KRW = int(os.getenv("INITIAL_CAPITAL_KRW", "10000000"))  # 초기 예수금 (원)
    KRW_RATIO = 0.5   # 한국 시장 배분 비율
    USD_RATIO = 0.5   # 미국 시장 배분 비율
    MAX_SINGLE_ORDER_RATIO = 0.10   # 1회 주문 한도 (총 자산의 10%)
    MAX_SINGLE_POSITION_RATIO = 0.15  # 단일 종목 최대 비중 (각 시장 자금의 15%)


# ──────────────────────────────────────────────
# 신호 엔진 설정
# ──────────────────────────────────────────────
class SignalConfig:
    LOOKBACK_DAYS = 30           # 참조 기간 (거래일)
    RSI_PERIOD = 14
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    BB_PERIOD = 20
    BB_STD = 2
    MA_SHORT = 5
    MA_MID = 20
    MA_LONG = 60
    ATR_PERIOD = 14
    ATR_STOP_MULTIPLIER = 1.5
    BUY_MIN_SIGNALS = 3          # 매수 최소 일치 신호 수
    SELL_MIN_SIGNALS = 2         # 매도 최소 일치 신호 수
    STRONG_SIGNAL_THRESHOLD = 80  # 강한 신호 기준 (시장가 주문)


# ──────────────────────────────────────────────
# 리스크 관리 설정
# ──────────────────────────────────────────────
class RiskConfig:
    MAX_DAILY_LOSS_RATIO = 0.03      # 일일 최대 손실 한도 (총 자산의 3%)
    MAX_DRAWDOWN_RATIO = 0.10        # 최대 드로우다운 (총 자산의 10%)
    MAX_POSITIONS_PER_MARKET = 5     # 각 시장 최대 동시 보유 종목 수
    MAX_SINGLE_POSITION_RATIO = 0.15 # 단일 종목 최대 비중


# ──────────────────────────────────────────────
# 스크리너 설정
# ──────────────────────────────────────────────
class ScreenerConfig:
    KR_UNIVERSE = "KOSPI200"    # 코스피200 / KOSDAQ150
    US_UNIVERSE = "SP500"       # S&P500 / NASDAQ100
    TOP_N_CANDIDATES = 30       # 당일 관심 종목 수
    MIN_MARKET_CAP_KRW = 1_000_000_000_000   # 최소 시가총액 1조원
    MIN_MARKET_CAP_USD = 10_000_000_000      # 최소 시가총액 100억달러


# ──────────────────────────────────────────────
# 스케줄러 / 리포트 설정
# ──────────────────────────────────────────────
class SchedulerConfig:
    REPORT_HOUR = 11   # KST 오전 11시
    REPORT_MINUTE = 0
    KR_MARKET_OPEN = "09:00"   # KST
    KR_MARKET_CLOSE = "15:30"  # KST
    US_MARKET_OPEN = "09:30"   # ET
    US_MARKET_CLOSE = "16:00"  # ET
    TIMEZONE_KST = "Asia/Seoul"
    TIMEZONE_ET = "US/Eastern"


# ──────────────────────────────────────────────
# DB 설정
# ──────────────────────────────────────────────
class DBConfig:
    DB_PATH = Path(__file__).parent / "db" / "dualtrader.db"


# ──────────────────────────────────────────────
# 환율 API
# ──────────────────────────────────────────────
class ExchangeRateConfig:
    API_URL = "https://api.exchangerate-api.com/v4/latest/USD"
    DEFAULT_USD_KRW = 1350.0  # API 불가 시 기본 환율
