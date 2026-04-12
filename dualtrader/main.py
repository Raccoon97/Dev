"""
DualTrader — 한미 자동매매 시스템 진입점
모든 모듈을 통합하여 24시간 자동매매를 실행합니다.

사용법:
    python main.py              # 전체 자동매매 실행
    python main.py --paper      # 페이퍼 트레이딩 모드
    python main.py --report     # 리포트만 생성
    python main.py --screen     # 종목 스크리닝만 실행
"""

import sys
import signal
import asyncio
import logging
import argparse
from pathlib import Path
from datetime import datetime

# 프로젝트 루트를 PYTHONPATH에 추가
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    FundConfig, KISConfig,
    SchedulerConfig, SignalConfig,
)
from db.models import init_db
from markets.korea import KoreaMarket
from markets.us import USMarket
from engine.signal import SignalEngine
from engine.screener import Screener
from engine.risk import RiskManager
from order.manager import OrderManager
from order.position import PositionTracker
from report.generator import ReportGenerator
from notify.telegram import TelegramNotifier
from scheduler import TradingScheduler


# ──────────────────────────────────────────────
# 로깅 설정
# ──────────────────────────────────────────────
def setup_logging():
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"dualtrader_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(str(log_file), encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# DualTrader 메인 클래스
# ──────────────────────────────────────────────
class DualTrader:
    """한미 자동매매 시스템 메인 컨트롤러"""

    def __init__(self):
        logger.info("=" * 60)
        logger.info("DualTrader 초기화 시작")
        logger.info("=" * 60)

        # DB 초기화
        init_db()

        # 시장 클라이언트
        self.kr_market = KoreaMarket()
        self.us_market = USMarket()

        # 엔진 모듈
        self.signal_engine = SignalEngine()
        self.screener = Screener()
        self.risk_manager = RiskManager()
        self.position_tracker = PositionTracker()

        # 주문 관리
        self.notifier = TelegramNotifier()
        self.order_manager = OrderManager(
            kr_market=self.kr_market,
            us_market=self.us_market,
            risk_manager=self.risk_manager,
            position_tracker=self.position_tracker,
            notifier=self.notifier,
        )

        # 리포트
        self.report_gen = ReportGenerator()

        # 당일 관심 종목
        self.kr_watchlist: list[str] = []
        self.us_watchlist: list[str] = []

        # 자금 배분 계산
        self._log_fund_allocation()

        logger.info("DualTrader 초기화 완료")

    def _log_fund_allocation(self):
        initial = FundConfig.INITIAL_CAPITAL_KRW
        rate = self.position_tracker.fetch_exchange_rate()
        krw_alloc = initial * FundConfig.KRW_RATIO
        usd_alloc = initial * FundConfig.USD_RATIO / rate

        logger.info("초기 예수금: %s KRW", f"{initial:,.0f}")
        logger.info("KRW 시장 배분: %s KRW", f"{krw_alloc:,.0f}")
        logger.info("USD 시장 배분: $%s (환율: %.2f)", f"{usd_alloc:,.2f}", rate)

    # ──────────────────────────────────────────
    # 스케줄러 콜백 메서드
    # ──────────────────────────────────────────

    async def on_kr_pre_market(self):
        """한국 장 시작 전 스크리닝"""
        logger.info("[KR] 장 시작 전 스크리닝 시작")
        try:
            self.kr_market.authenticate()
            # KIS 토큰을 미국 시장 클라이언트에도 공유
            self.us_market.share_token(
                self.kr_market.access_token,
                self.kr_market.token_expires_at,
            )
            self.kr_watchlist = self.screener.screen_kr_stocks(self.kr_market)
            logger.info("[KR] 관심 종목 %d개 선정: %s",
                        len(self.kr_watchlist), self.kr_watchlist[:5])
            await self.notifier.send_message(
                f"<b>[KR 프리마켓]</b> 관심 종목 {len(self.kr_watchlist)}개 선정\n"
                f"TOP 5: {', '.join(self.kr_watchlist[:5])}"
            )
        except Exception as e:
            logger.error("[KR] 프리마켓 스크리닝 실패: %s", e)
            await self.notifier.notify_error(f"KR 프리마켓 스크리닝 실패: {e}")

    async def on_kr_market_open(self):
        """한국 장 시작 — 초기 신호 분석 및 매매"""
        logger.info("[KR] 장 시작")
        try:
            if not self.kr_watchlist:
                self.kr_watchlist = self.screener.get_kr_universe()[:10]

            signals = self.signal_engine.batch_signals(
                self.kr_market, self.kr_watchlist[:15]
            )
            buy_signals = [s for s in signals if s.signal_type == "BUY"]
            logger.info("[KR] 매수 신호 %d개 감지", len(buy_signals))

            if buy_signals:
                balance = self.kr_market.get_balance()
                results = self.order_manager.process_signals("KR", buy_signals, balance)
                for r in results:
                    if r.get("success"):
                        await self.notifier.send_message(r["message"])
        except Exception as e:
            logger.error("[KR] 장 시작 처리 실패: %s", e)
            await self.notifier.notify_error(f"KR 장 시작 처리 실패: {e}")

    async def on_kr_signal_check(self):
        """한국 장중 정기 신호 체크"""
        if not self.kr_market.is_market_open():
            return
        logger.info("[KR] 장중 신호 체크")
        try:
            # 매수 신호 체크
            signals = self.signal_engine.batch_signals(
                self.kr_market, self.kr_watchlist[:10]
            )
            buy_signals = [s for s in signals if s.signal_type == "BUY"]
            sell_signals = [s for s in signals if s.signal_type == "SELL"]

            if buy_signals:
                balance = self.kr_market.get_balance()
                self.order_manager.process_signals("KR", buy_signals, balance)

            # 매도 신호 체크
            if sell_signals:
                self.order_manager.process_sell_signals("KR", sell_signals)
        except Exception as e:
            logger.error("[KR] 신호 체크 실패: %s", e)

    async def on_kr_pre_close(self):
        """한국 장 마감 전 정리"""
        logger.info("[KR] 장 마감 전 미체결 주문 취소")
        try:
            self.order_manager.cancel_unfilled_kr_orders()
            await self.notifier.send_message("<b>[KR]</b> 장 마감 전 미체결 주문 정리 완료")
        except Exception as e:
            logger.error("[KR] 마감 전 정리 실패: %s", e)

    async def on_us_market_open(self):
        """미국 장 시작"""
        logger.info("[US] 장 시작")
        try:
            if not self.us_watchlist:
                self.us_watchlist = self.screener.screen_us_stocks()

            signals = self.signal_engine.batch_signals(
                self.us_market, self.us_watchlist[:15]
            )
            buy_signals = [s for s in signals if s.signal_type == "BUY"]
            logger.info("[US] 매수 신호 %d개 감지", len(buy_signals))

            if buy_signals:
                balance = self.us_market.get_balance()
                results = self.order_manager.process_signals("US", buy_signals, balance)
                for r in results:
                    if r.get("success"):
                        await self.notifier.send_message(r["message"])
        except Exception as e:
            logger.error("[US] 장 시작 처리 실패: %s", e)
            await self.notifier.notify_error(f"US 장 시작 처리 실패: {e}")

    async def on_us_signal_check(self):
        """미국 장중 정기 신호 체크"""
        if not self.us_market.is_market_open():
            return
        logger.info("[US] 장중 신호 체크")
        try:
            signals = self.signal_engine.batch_signals(
                self.us_market, self.us_watchlist[:10]
            )
            buy_signals = [s for s in signals if s.signal_type == "BUY"]
            sell_signals = [s for s in signals if s.signal_type == "SELL"]

            if buy_signals:
                balance = self.us_market.get_balance()
                self.order_manager.process_signals("US", buy_signals, balance)

            if sell_signals:
                self.order_manager.process_sell_signals("US", sell_signals)
        except Exception as e:
            logger.error("[US] 신호 체크 실패: %s", e)

    async def on_us_market_close(self):
        """미국 장 마감"""
        logger.info("[US] 장 마감")
        try:
            self.us_market.cancel_all_orders()
            await self.notifier.send_message("<b>[US]</b> 장 마감 — 미체결 주문 정리 완료")
        except Exception as e:
            logger.error("[US] 장 마감 처리 실패: %s", e)

    async def on_stop_loss_check(self):
        """손절가 도달 체크 (양 시장)"""
        try:
            results = self.order_manager.check_and_execute_stop_losses()
            for r in results:
                if r.get("success"):
                    reason = r.get("stop_loss_reason", "손절 실행")
                    await self.notifier.send_message(
                        f"<b>[손절 실행]</b>\n{reason}\n{r.get('message', '')}"
                    )
        except Exception as e:
            logger.error("손절 체크 실패: %s", e)

    async def on_daily_report(self):
        """일간 리포트 생성 및 전송"""
        logger.info("일간 리포트 생성 시작")
        try:
            kr_balance = self.kr_market.get_balance()
            us_balance = self.us_market.get_balance()
            summary = self.position_tracker.calculate_portfolio_summary(
                kr_balance, us_balance
            )
            drawdown = self.risk_manager.calculate_drawdown(summary["total_asset_krw"])
            self.position_tracker.save_daily_snapshot(summary, drawdown=drawdown)

            # HTML 리포트
            report_path = self.report_gen.generate_daily_report(
                summary,
                watchlist_kr=self.kr_watchlist[:5],
                watchlist_us=self.us_watchlist[:5],
            )

            # 차트
            chart_path = self.report_gen.generate_asset_chart()

            # 텔레그램 텍스트 리포트
            text_report = self.report_gen.generate_text_report(summary)
            await self.notifier.send_message(text_report)

            # 차트 이미지 전송
            if chart_path:
                await self.notifier.send_photo(chart_path, caption="자산 추이 차트")

            logger.info("일간 리포트 전송 완료")
        except Exception as e:
            logger.error("리포트 생성 실패: %s", e)
            await self.notifier.notify_error(f"리포트 생성 실패: {e}")

    async def on_daily_reset(self):
        """일일 리스크 카운터 리셋"""
        self.risk_manager.reset_daily()
        logger.info("일일 리셋 완료")

    # ──────────────────────────────────────────
    # 메인 실행
    # ──────────────────────────────────────────

    async def run(self):
        """메인 실행 루프"""
        logger.info("DualTrader 시작 — 24시간 자동매매 모드")

        # 스케줄러 시작
        trading_scheduler = TradingScheduler(self)
        trading_scheduler.start()

        # 잡 정보 출력
        for job in trading_scheduler.get_jobs_info():
            logger.info("  [JOB] %s → next: %s", job["name"], job["next_run"])

        await self.notifier.send_message(
            "<b>[DualTrader 시작]</b>\n"
            f"모드: {'페이퍼' if KISConfig.IS_PAPER else '실거래'}\n"
            f"초기 자본: {FundConfig.INITIAL_CAPITAL_KRW:,.0f} KRW\n"
            f"등록 스케줄: {len(trading_scheduler.get_jobs_info())}개"
        )

        # 무한 루프 (Ctrl+C로 종료)
        try:
            while True:
                await asyncio.sleep(60)
        except (KeyboardInterrupt, SystemExit):
            logger.info("종료 신호 수신")
            trading_scheduler.stop()
            await self.notifier.send_message("<b>[DualTrader 종료]</b>")

    async def run_report_only(self):
        """리포트만 생성"""
        logger.info("리포트 전용 모드")
        try:
            kr_balance = self.kr_market.get_balance()
        except Exception:
            kr_balance = {"cash": 0, "stock_value": 0, "holdings": []}
        try:
            us_balance = self.us_market.get_balance()
        except Exception:
            us_balance = {"cash": 0, "stock_value": 0, "holdings": []}

        summary = self.position_tracker.calculate_portfolio_summary(
            kr_balance, us_balance
        )
        report_path = self.report_gen.generate_daily_report(summary)
        self.report_gen.generate_asset_chart()
        text = self.report_gen.generate_text_report(summary)
        print(text)
        logger.info("리포트 생성 완료: %s", report_path)

    async def run_screen_only(self):
        """종목 스크리닝만 실행"""
        logger.info("스크리닝 전용 모드")
        print("\n[미국 시장 스크리닝]")
        us_list = self.screener.screen_us_stocks()
        for i, sym in enumerate(us_list[:10], 1):
            print(f"  {i}. {sym}")

        print("\n[한국 시장 유니버스]")
        kr_list = self.screener.get_kr_universe()
        for i, sym in enumerate(kr_list[:10], 1):
            print(f"  {i}. {sym}")


# ──────────────────────────────────────────────
# 진입점
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="DualTrader — 한미 자동매매 시스템")
    parser.add_argument("--paper", action="store_true", help="페이퍼 트레이딩 모드")
    parser.add_argument("--report", action="store_true", help="리포트만 생성")
    parser.add_argument("--screen", action="store_true", help="종목 스크리닝만 실행")
    args = parser.parse_args()

    setup_logging()

    logger.info("=" * 60)
    logger.info("DualTrader v0.1.0")
    logger.info("=" * 60)

    trader = DualTrader()

    if args.report:
        asyncio.run(trader.run_report_only())
    elif args.screen:
        asyncio.run(trader.run_screen_only())
    else:
        asyncio.run(trader.run())


if __name__ == "__main__":
    main()
