"""
텔레그램 알림 모듈
매매 신호, 오류, 리포트를 텔레그램으로 전송
"""

import logging
import asyncio
import aiohttp
from pathlib import Path

from config import TelegramConfig

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """텔레그램 봇 알림 전송"""

    def __init__(self):
        self.bot_token = TelegramConfig.BOT_TOKEN
        self.chat_id = TelegramConfig.CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.enabled = bool(self.bot_token and self.chat_id)

    async def send_message(self, text: str, parse_mode: str = "HTML"):
        """텍스트 메시지 전송"""
        if not self.enabled:
            logger.debug("텔레그램 비활성 — 메시지 스킵: %s", text[:50])
            return

        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        logger.debug("텔레그램 메시지 전송 완료")
                    else:
                        body = await resp.text()
                        logger.error("텔레그램 전송 실패 [%d]: %s", resp.status, body)
        except Exception as e:
            logger.error("텔레그램 전송 오류: %s", e)

    async def send_photo(self, photo_path: str, caption: str = ""):
        """이미지 전송 (차트 등)"""
        if not self.enabled:
            return

        url = f"{self.base_url}/sendPhoto"
        try:
            async with aiohttp.ClientSession() as session:
                data = aiohttp.FormData()
                data.add_field("chat_id", self.chat_id)
                if caption:
                    data.add_field("caption", caption)
                    data.add_field("parse_mode", "HTML")
                data.add_field(
                    "photo",
                    open(photo_path, "rb"),
                    filename=Path(photo_path).name,
                )
                async with session.post(url, data=data, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        logger.debug("텔레그램 이미지 전송 완료")
                    else:
                        body = await resp.text()
                        logger.error("텔레그램 이미지 전송 실패 [%d]: %s", resp.status, body)
        except Exception as e:
            logger.error("텔레그램 이미지 전송 오류: %s", e)

    async def send_document(self, doc_path: str, caption: str = ""):
        """문서 전송 (리포트 PDF/HTML 등)"""
        if not self.enabled:
            return

        url = f"{self.base_url}/sendDocument"
        try:
            async with aiohttp.ClientSession() as session:
                data = aiohttp.FormData()
                data.add_field("chat_id", self.chat_id)
                if caption:
                    data.add_field("caption", caption)
                data.add_field(
                    "document",
                    open(doc_path, "rb"),
                    filename=Path(doc_path).name,
                )
                async with session.post(url, data=data, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        logger.debug("텔레그램 문서 전송 완료")
                    else:
                        body = await resp.text()
                        logger.error("텔레그램 문서 전송 실패 [%d]: %s", resp.status, body)
        except Exception as e:
            logger.error("텔레그램 문서 전송 오류: %s", e)

    def send_sync(self, text: str):
        """동기 방식 메시지 전송 (이벤트 루프 밖에서 호출 가능)"""
        if not self.enabled:
            logger.debug("텔레그램 비활성 — 메시지 스킵")
            return
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(self.send_message(text))
            else:
                loop.run_until_complete(self.send_message(text))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.send_message(text))
            loop.close()

    # ──────────────────────────────────────────
    # 포맷된 메시지 헬퍼
    # ──────────────────────────────────────────

    async def notify_buy(self, market: str, symbol: str, name: str,
                         quantity: int, price: float, score: float):
        msg = (
            f"<b>[매수 체결]</b> {market}\n"
            f"종목: {symbol} {name}\n"
            f"수량: {quantity}주 / 가격: {price:,.2f}\n"
            f"신호 점수: {score:.0f}"
        )
        await self.send_message(msg)

    async def notify_sell(self, market: str, symbol: str,
                          quantity: int, price: float, pnl: float):
        emoji = "+" if pnl >= 0 else ""
        msg = (
            f"<b>[매도 체결]</b> {market}\n"
            f"종목: {symbol}\n"
            f"수량: {quantity}주 / 가격: {price:,.2f}\n"
            f"실현 손익: {emoji}{pnl:,.2f}"
        )
        await self.send_message(msg)

    async def notify_stop_loss(self, market: str, symbol: str,
                               price: float, stop_price: float):
        msg = (
            f"<b>[손절 실행]</b> {market}\n"
            f"종목: {symbol}\n"
            f"현재가: {price:,.2f} / 손절가: {stop_price:,.2f}"
        )
        await self.send_message(msg)

    async def notify_error(self, error_msg: str):
        msg = f"<b>[오류]</b>\n{error_msg}"
        await self.send_message(msg)

    async def notify_risk_halt(self, reason: str):
        msg = f"<b>[거래 중단]</b>\n{reason}\n\n수동 확인이 필요합니다."
        await self.send_message(msg)
