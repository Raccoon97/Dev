"""
스케줄러 모듈
APScheduler를 사용하여 장 시작/종료, 리포트 생성 등을 스케줄링합니다.
"""

import logging
import asyncio
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import SchedulerConfig

logger = logging.getLogger(__name__)


class TradingScheduler:
    """매매 스케줄러"""

    def __init__(self, trader):
        """
        Args:
            trader: DualTrader 메인 객체 (콜백 메서드를 가진 인스턴스)
        """
        self.trader = trader
        self.scheduler = AsyncIOScheduler(
            timezone=SchedulerConfig.TIMEZONE_KST,
        )
        self._setup_jobs()

    def _setup_jobs(self):
        """스케줄 잡 등록"""
        cfg = SchedulerConfig

        # ──────────────────────────────────────
        # 한국 시장
        # ──────────────────────────────────────

        # 한국 장 시작 전 스크리닝 (08:50 KST)
        self.scheduler.add_job(
            self.trader.on_kr_pre_market,
            CronTrigger(hour=8, minute=50, timezone=cfg.TIMEZONE_KST),
            id="kr_pre_market",
            name="KR Pre-Market Screening",
            day_of_week="mon-fri",
        )

        # 한국 장 시작 (09:05 KST) — 약간의 지연으로 안정적 시작
        self.scheduler.add_job(
            self.trader.on_kr_market_open,
            CronTrigger(hour=9, minute=5, timezone=cfg.TIMEZONE_KST),
            id="kr_market_open",
            name="KR Market Open",
            day_of_week="mon-fri",
        )

        # 한국 장중 신호 체크 (매 30분마다, 09:30~15:00)
        self.scheduler.add_job(
            self.trader.on_kr_signal_check,
            CronTrigger(
                minute="0,30", hour="9-14",
                timezone=cfg.TIMEZONE_KST,
            ),
            id="kr_signal_check",
            name="KR Signal Check",
            day_of_week="mon-fri",
        )

        # 한국 장 마감 전 미체결 정리 (15:15 KST)
        self.scheduler.add_job(
            self.trader.on_kr_pre_close,
            CronTrigger(hour=15, minute=15, timezone=cfg.TIMEZONE_KST),
            id="kr_pre_close",
            name="KR Pre-Close Cleanup",
            day_of_week="mon-fri",
        )

        # ──────────────────────────────────────
        # 미국 시장 (KST 기준으로 스케줄링)
        # ──────────────────────────────────────

        # 미국 장 시작 (23:30 KST = 09:30 ET, 서머타임 시 22:30)
        self.scheduler.add_job(
            self.trader.on_us_market_open,
            CronTrigger(hour=23, minute=35, timezone=cfg.TIMEZONE_KST),
            id="us_market_open",
            name="US Market Open",
            day_of_week="mon-fri",
        )

        # 미국 장중 신호 체크 (매 30분, KST 0:00~5:30)
        self.scheduler.add_job(
            self.trader.on_us_signal_check,
            CronTrigger(
                minute="0,30", hour="0-5",
                timezone=cfg.TIMEZONE_KST,
            ),
            id="us_signal_check",
            name="US Signal Check",
            day_of_week="tue-sat",  # 미국 장은 한국 기준 화~토 새벽
        )

        # 미국 장 마감 (06:00 KST = 16:00 ET)
        self.scheduler.add_job(
            self.trader.on_us_market_close,
            CronTrigger(hour=6, minute=0, timezone=cfg.TIMEZONE_KST),
            id="us_market_close",
            name="US Market Close",
            day_of_week="tue-sat",
        )

        # ──────────────────────────────────────
        # 공통
        # ──────────────────────────────────────

        # 손절 체크 (매 5분마다, 장 운영 시간)
        self.scheduler.add_job(
            self.trader.on_stop_loss_check,
            CronTrigger(minute="*/5", timezone=cfg.TIMEZONE_KST),
            id="stop_loss_check",
            name="Stop Loss Check",
        )

        # 일간 리포트 (11:00 KST)
        self.scheduler.add_job(
            self.trader.on_daily_report,
            CronTrigger(
                hour=cfg.REPORT_HOUR,
                minute=cfg.REPORT_MINUTE,
                timezone=cfg.TIMEZONE_KST,
            ),
            id="daily_report",
            name="Daily Report",
            day_of_week="mon-fri",
        )

        # 일일 리스크 카운터 리셋 (00:00 KST)
        self.scheduler.add_job(
            self.trader.on_daily_reset,
            CronTrigger(hour=0, minute=0, timezone=cfg.TIMEZONE_KST),
            id="daily_reset",
            name="Daily Risk Reset",
        )

        logger.info("스케줄 잡 등록 완료 (%d개)", len(self.scheduler.get_jobs()))

    def start(self):
        """스케줄러 시작"""
        self.scheduler.start()
        logger.info("스케줄러 시작")

    def stop(self):
        """스케줄러 중지"""
        self.scheduler.shutdown(wait=False)
        logger.info("스케줄러 중지")

    def get_jobs_info(self) -> list[dict]:
        """등록된 잡 정보 조회"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else "N/A",
            })
        return jobs
