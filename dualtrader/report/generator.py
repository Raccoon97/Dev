"""
리포트 생성기
일간 보고서를 HTML로 생성하고 차트를 포함합니다.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # GUI 백엔드 없이 렌더링
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from jinja2 import Environment, FileSystemLoader

from config import FundConfig
from db.models import (
    get_open_positions, get_orders_by_date,
    get_daily_balances,
)

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent / "templates"
OUTPUT_DIR = Path(__file__).parent / "output"


class ReportGenerator:
    """일간 리포트 생성기"""

    def __init__(self):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

    def generate_asset_chart(self, output_path: str = None) -> str:
        """자산 추이 차트 생성"""
        balances = get_daily_balances(30)
        if not balances:
            logger.warning("차트 생성 불가: 잔고 데이터 없음")
            return ""

        balances.reverse()  # 날짜 오름차순
        dates = [b["date"] for b in balances]
        totals = [b["total_asset_krw"] / 10000 for b in balances]  # 만원 단위

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(dates, totals, color="#1a1a2e", linewidth=2, marker="o", markersize=3)
        ax.fill_between(dates, totals, alpha=0.1, color="#1a1a2e")

        # 초기 자본 기준선
        initial = FundConfig.INITIAL_CAPITAL_KRW / 10000
        ax.axhline(y=initial, color="#e74c3c", linestyle="--", alpha=0.5, label="초기 자본")

        ax.set_title("자산 추이 (만원)", fontsize=14, fontweight="bold")
        ax.set_xlabel("")
        ax.set_ylabel("총 자산 (만원)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()

        if not output_path:
            output_path = str(OUTPUT_DIR / "asset_chart.png")
        fig.savefig(output_path, dpi=150)
        plt.close(fig)
        logger.info("자산 추이 차트 생성: %s", output_path)
        return output_path

    def generate_daily_report(self, summary: dict,
                              watchlist_kr: list[str] = None,
                              watchlist_us: list[str] = None) -> str:
        """일간 HTML 리포트 생성"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")

        # 전일 주문 내역
        orders = get_orders_by_date(yesterday)

        buy_count = sum(1 for o in orders if o["side"] == "BUY")
        sell_count = sum(1 for o in orders if o["side"] == "SELL")

        # 실현 손익 계산
        realized_pnl = sum(
            (o.get("filled_price", 0) - o.get("price", 0)) * o.get("filled_quantity", 0)
            for o in orders if o["side"] == "SELL" and o["status"] == "FILLED"
        )

        # 보유 포지션
        positions = get_open_positions()
        position_list = []
        for p in positions:
            entry = p["entry_price"]
            current = p.get("current_price", entry)
            pnl_pct = ((current - entry) / entry * 100) if entry else 0
            position_list.append({
                "market": p["market"],
                "symbol": p["symbol"],
                "name": p.get("name", ""),
                "quantity": p["quantity"],
                "entry_price": f"{entry:,.2f}",
                "current_price": f"{current:,.2f}",
                "pnl_pct": pnl_pct,
                "pnl_pct_str": f"{pnl_pct:+.1f}%",
            })

        # 총 자산
        total_asset = summary.get("total_asset_krw", 0)
        initial = FundConfig.INITIAL_CAPITAL_KRW
        initial_pct = ((total_asset - initial) / initial * 100) if initial else 0

        # 주문 리스트 포맷팅
        order_list = []
        for o in orders:
            order_list.append({
                "market": o["market"],
                "symbol": o["symbol"],
                "side": o["side"],
                "quantity": o.get("filled_quantity", o["quantity"]),
                "price": f"{o.get('filled_price', o.get('price', 0)):,.2f}",
                "status": o["status"],
            })

        # 템플릿 렌더링
        template = self.env.get_template("daily_report.html")
        html = template.render(
            date=date_str,
            time=time_str,
            total_asset=f"{total_asset:,.0f} KRW",
            initial_pct=initial_pct,
            initial_pct_str=f"{initial_pct:+.1f}%",
            krw_total=f"{summary.get('krw_cash', 0) + summary.get('krw_stock_value', 0):,.0f} KRW",
            usd_total=f"${summary.get('usd_cash', 0) + summary.get('usd_stock_value', 0):,.2f}",
            unrealized_pnl=summary.get("unrealized_pnl", 0),
            unrealized_pnl_str=f"{summary.get('unrealized_pnl', 0):+,.0f} KRW",
            exchange_rate=f"{summary.get('exchange_rate', 0):,.2f}",
            buy_count=buy_count,
            sell_count=sell_count,
            realized_pnl=realized_pnl,
            realized_pnl_str=f"{realized_pnl:+,.0f} KRW",
            orders=order_list,
            positions=position_list,
            watchlist_kr=watchlist_kr or [],
            watchlist_us=watchlist_us or [],
        )

        # HTML 저장
        report_path = str(OUTPUT_DIR / f"report_{date_str}.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info("일간 리포트 생성: %s", report_path)
        return report_path

    def generate_text_report(self, summary: dict) -> str:
        """텔레그램용 텍스트 리포트"""
        now = datetime.now()
        total_asset = summary.get("total_asset_krw", 0)
        initial = FundConfig.INITIAL_CAPITAL_KRW
        initial_pct = ((total_asset - initial) / initial * 100) if initial else 0

        positions = get_open_positions()
        pos_lines = []
        for p in positions:
            entry = p["entry_price"]
            current = p.get("current_price", entry)
            pnl_pct = ((current - entry) / entry * 100) if entry else 0
            pos_lines.append(
                f"  [{p['market']}] {p['symbol']} {p.get('name', '')} "
                f"{p['quantity']}주 @ {entry:,.0f} → {current:,.0f} ({pnl_pct:+.1f}%)"
            )

        text = (
            f"<b>[DualTrader 일간 보고서]</b> {now.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"<b>■ 자산 현황</b>\n"
            f"  총 자산: {total_asset:,.0f} KRW (초기 대비 {initial_pct:+.1f}%)\n"
            f"  KRW 파트: {summary.get('krw_cash', 0) + summary.get('krw_stock_value', 0):,.0f} KRW\n"
            f"  USD 파트: ${summary.get('usd_cash', 0) + summary.get('usd_stock_value', 0):,.2f}\n"
            f"  미실현 손익: {summary.get('unrealized_pnl', 0):+,.0f} KRW\n\n"
            f"<b>■ 보유 포지션</b>\n"
        )
        if pos_lines:
            text += "\n".join(pos_lines)
        else:
            text += "  보유 포지션 없음"

        return text
