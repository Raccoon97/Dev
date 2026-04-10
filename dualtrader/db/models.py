"""
DualTrader DB 모델
SQLite를 사용한 매매일지, 포지션, 잔고 저장
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from config import DBConfig


def get_connection() -> sqlite3.Connection:
    """SQLite 연결 반환 (없으면 DB 파일 자동 생성)"""
    DBConfig.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DBConfig.DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """데이터베이스 초기화 — 테이블 생성"""
    conn = get_connection()
    cursor = conn.cursor()

    # 포지션 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market TEXT NOT NULL CHECK(market IN ('KR', 'US')),
            symbol TEXT NOT NULL,
            name TEXT,
            side TEXT NOT NULL CHECK(side IN ('BUY', 'SELL')),
            quantity INTEGER NOT NULL,
            entry_price REAL NOT NULL,
            current_price REAL DEFAULT 0,
            stop_loss REAL,
            take_profit REAL,
            signal_score REAL,
            status TEXT NOT NULL DEFAULT 'OPEN' CHECK(status IN ('OPEN', 'CLOSED', 'PARTIAL')),
            opened_at TEXT NOT NULL,
            closed_at TEXT,
            realized_pnl REAL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # 주문 이력 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            position_id INTEGER,
            market TEXT NOT NULL CHECK(market IN ('KR', 'US')),
            symbol TEXT NOT NULL,
            side TEXT NOT NULL CHECK(side IN ('BUY', 'SELL')),
            order_type TEXT NOT NULL CHECK(order_type IN ('MARKET', 'LIMIT')),
            quantity INTEGER NOT NULL,
            price REAL,
            filled_price REAL,
            filled_quantity INTEGER DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'PENDING'
                CHECK(status IN ('PENDING', 'FILLED', 'PARTIAL', 'CANCELLED', 'REJECTED')),
            broker_order_id TEXT,
            signal_score REAL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (position_id) REFERENCES positions(id)
        )
    """)

    # 일간 잔고 스냅샷
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_balance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            total_asset_krw REAL NOT NULL,
            krw_cash REAL NOT NULL,
            krw_stock_value REAL NOT NULL,
            usd_cash REAL NOT NULL,
            usd_stock_value REAL NOT NULL,
            exchange_rate REAL NOT NULL,
            realized_pnl REAL DEFAULT 0,
            unrealized_pnl REAL DEFAULT 0,
            drawdown REAL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # 매매 신호 로그
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signal_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market TEXT NOT NULL CHECK(market IN ('KR', 'US')),
            symbol TEXT NOT NULL,
            signal_type TEXT NOT NULL CHECK(signal_type IN ('BUY', 'SELL', 'HOLD')),
            score REAL NOT NULL,
            rsi REAL,
            macd_signal TEXT,
            bb_signal TEXT,
            ma_signal TEXT,
            volume_signal TEXT,
            atr REAL,
            detail TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # 인덱스 생성
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_positions_market ON positions(market)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_symbol ON orders(symbol)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_signal_log_symbol ON signal_log(symbol)")

    conn.commit()
    conn.close()


# ──────────────────────────────────────────────
# CRUD 헬퍼 함수
# ──────────────────────────────────────────────

def insert_position(market: str, symbol: str, name: str, side: str,
                    quantity: int, entry_price: float,
                    stop_loss: float = None, take_profit: float = None,
                    signal_score: float = None) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO positions
            (market, symbol, name, side, quantity, entry_price,
             stop_loss, take_profit, signal_score, status, opened_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', ?)
    """, (market, symbol, name, side, quantity, entry_price,
          stop_loss, take_profit, signal_score,
          datetime.now().isoformat()))
    position_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return position_id


def close_position(position_id: int, close_price: float, realized_pnl: float):
    conn = get_connection()
    conn.execute("""
        UPDATE positions
        SET status='CLOSED', current_price=?, realized_pnl=?,
            closed_at=?, updated_at=?
        WHERE id=?
    """, (close_price, realized_pnl,
          datetime.now().isoformat(), datetime.now().isoformat(),
          position_id))
    conn.commit()
    conn.close()


def get_open_positions(market: str = None) -> list[dict]:
    conn = get_connection()
    if market:
        rows = conn.execute(
            "SELECT * FROM positions WHERE status='OPEN' AND market=?",
            (market,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM positions WHERE status='OPEN'"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def insert_order(market: str, symbol: str, side: str, order_type: str,
                 quantity: int, price: float = None,
                 position_id: int = None, signal_score: float = None) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO orders
            (position_id, market, symbol, side, order_type, quantity, price, signal_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (position_id, market, symbol, side, order_type, quantity, price, signal_score))
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return order_id


def update_order_status(order_id: int, status: str,
                        filled_price: float = None, filled_quantity: int = None,
                        broker_order_id: str = None):
    conn = get_connection()
    conn.execute("""
        UPDATE orders
        SET status=?, filled_price=?, filled_quantity=?,
            broker_order_id=?, updated_at=?
        WHERE id=?
    """, (status, filled_price, filled_quantity,
          broker_order_id, datetime.now().isoformat(), order_id))
    conn.commit()
    conn.close()


def insert_daily_balance(date: str, total_asset_krw: float,
                         krw_cash: float, krw_stock_value: float,
                         usd_cash: float, usd_stock_value: float,
                         exchange_rate: float,
                         realized_pnl: float = 0, unrealized_pnl: float = 0,
                         drawdown: float = 0):
    conn = get_connection()
    conn.execute("""
        INSERT OR REPLACE INTO daily_balance
            (date, total_asset_krw, krw_cash, krw_stock_value,
             usd_cash, usd_stock_value, exchange_rate,
             realized_pnl, unrealized_pnl, drawdown)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (date, total_asset_krw, krw_cash, krw_stock_value,
          usd_cash, usd_stock_value, exchange_rate,
          realized_pnl, unrealized_pnl, drawdown))
    conn.commit()
    conn.close()


def insert_signal_log(market: str, symbol: str, signal_type: str,
                      score: float, **indicators):
    conn = get_connection()
    conn.execute("""
        INSERT INTO signal_log
            (market, symbol, signal_type, score,
             rsi, macd_signal, bb_signal, ma_signal,
             volume_signal, atr, detail)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (market, symbol, signal_type, score,
          indicators.get("rsi"), indicators.get("macd_signal"),
          indicators.get("bb_signal"), indicators.get("ma_signal"),
          indicators.get("volume_signal"), indicators.get("atr"),
          indicators.get("detail")))
    conn.commit()
    conn.close()


def get_daily_balances(limit: int = 30) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM daily_balance ORDER BY date DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_orders_by_date(date: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM orders WHERE DATE(created_at)=? ORDER BY created_at",
        (date,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


if __name__ == "__main__":
    init_db()
    print("DB 초기화 완료:", DBConfig.DB_PATH)
