"""
SQLite database manager for services trading comps.
Handles schema creation, upserts, and queries.
"""

import sqlite3
from datetime import date, datetime
from pathlib import Path


class DBManager:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _connect(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def init_schema(self):
        conn = self._connect()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS company_snapshots (
                    ticker TEXT NOT NULL,
                    snapshot_date TEXT NOT NULL,
                    name TEXT,
                    sector TEXT,
                    sub_sector TEXT,
                    exchange TEXT,
                    listing_country TEXT,
                    current_price REAL,
                    market_cap REAL,
                    enterprise_value REAL,
                    total_debt REAL,
                    total_cash REAL,
                    shares_outstanding REAL,
                    fifty_two_week_high REAL,
                    currency TEXT,
                    ltm_revenue REAL,
                    ltm_gross_profit REAL,
                    ltm_ebitda REAL,
                    ltm_ebit REAL,
                    gross_margin REAL,
                    ebitda_margin REAL,
                    ebit_margin REAL,
                    current_fy_rev_est REAL,
                    next_fy_rev_est REAL,
                    ntm_revenue REAL,
                    ntm_revenue_growth REAL,
                    ntm_ev_revenue REAL,
                    ltm_ev_revenue REAL,
                    ntm_ev_ebitda REAL,
                    ltm_ev_ebitda REAL,
                    ntm_pe REAL,
                    fcf_yield REAL,
                    dividend_yield REAL,
                    net_debt_ebitda REAL,
                    pct_52wk_high REAL,
                    price_change_2w REAL,
                    price_change_2m REAL,
                    free_cash_flow REAL,
                    fetch_timestamp TEXT,
                    PRIMARY KEY (ticker, snapshot_date)
                );

                CREATE INDEX IF NOT EXISTS idx_snapshots_sector
                    ON company_snapshots(sector);
                CREATE INDEX IF NOT EXISTS idx_snapshots_date
                    ON company_snapshots(snapshot_date);
            """)
            conn.commit()
        finally:
            conn.close()

    def upsert_snapshot(self, data: dict):
        conn = self._connect()
        try:
            cols = list(data.keys())
            placeholders = ", ".join(["?"] * len(cols))
            col_names = ", ".join(cols)
            sql = f"INSERT OR REPLACE INTO company_snapshots ({col_names}) VALUES ({placeholders})"
            conn.execute(sql, [data.get(c) for c in cols])
            conn.commit()
        finally:
            conn.close()

    def get_latest_snapshots(self, sector: str = None) -> list[dict]:
        conn = self._connect()
        try:
            base = """
                SELECT * FROM company_snapshots
                WHERE (ticker, snapshot_date) IN (
                    SELECT ticker, MAX(snapshot_date) FROM company_snapshots GROUP BY ticker
                )
            """
            if sector:
                base += " AND sector = ?"
                rows = conn.execute(base + " ORDER BY name", (sector,)).fetchall()
            else:
                rows = conn.execute(base + " ORDER BY name").fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_all_latest_snapshots(self) -> list[dict]:
        return self.get_latest_snapshots(sector=None)

    def get_last_fetch_time(self) -> str | None:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT MAX(fetch_timestamp) as ts FROM company_snapshots"
            ).fetchone()
            return row["ts"] if row else None
        finally:
            conn.close()

    def get_sector_summary(self) -> list[dict]:
        conn = self._connect()
        try:
            rows = conn.execute("""
                SELECT
                    sector,
                    COUNT(*) as count,
                    AVG(ntm_ev_ebitda) as avg_ev_ebitda,
                    AVG(ntm_ev_revenue) as avg_ev_rev,
                    AVG(ntm_revenue_growth) as avg_growth,
                    AVG(ebitda_margin) as avg_ebitda_margin
                FROM company_snapshots
                WHERE (ticker, snapshot_date) IN (
                    SELECT ticker, MAX(snapshot_date) FROM company_snapshots GROUP BY ticker
                )
                GROUP BY sector
                ORDER BY sector
            """).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
