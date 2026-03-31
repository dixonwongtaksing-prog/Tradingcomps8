"""
Data fetch orchestrator.
Loops through the company registry, pulls data from Yahoo Finance,
derives all metrics, and stores snapshots in SQLite.

Usage:
    python -m fetcher.run_fetch              # fetch all
    python -m fetcher.run_fetch --limit 10   # fetch first 10 only
    python -m fetcher.run_fetch --sector consulting  # one sector
"""

import argparse
import logging
import sys
import time
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.company_registry import COMPANY_REGISTRY
from config.settings import DB_PATH
from fetcher.yf_fetcher import fetch_company_data
from fetcher.db_manager import DBManager
from fetcher.calculators import (
    calc_ntm_revenue,
    calc_ntm_revenue_growth,
    calc_tev,
    calc_pct_52wk_high,
    calc_margins,
    calc_ntm_ev_revenue,
    calc_ltm_ev_revenue,
    calc_ntm_ev_ebitda,
    calc_ltm_ev_ebitda,
    calc_ntm_pe,
    calc_fcf_yield,
    calc_net_debt_ebitda,
    calc_price_changes,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def process_one_company(ticker: str, info: dict, raw: dict) -> dict:
    """
    Take raw Yahoo Finance data and derive all metrics.
    Returns a flat dict ready for DB upsert.
    """
    today_str = date.today().isoformat()
    now_str = datetime.utcnow().isoformat()

    # TEV
    tev = calc_tev(raw.get("market_cap"), raw.get("total_debt"), raw.get("total_cash"))

    # Use TEV from yfinance if our calc returns None
    if tev is None:
        tev = raw.get("enterprise_value")

    # NTM revenue
    ntm_rev = calc_ntm_revenue(
        raw.get("current_fy_rev_est"),
        raw.get("next_fy_rev_est"),
        fy_end_month=12,
    )

    # Revenue growth
    ntm_rev_growth = calc_ntm_revenue_growth(ntm_rev, raw.get("ltm_revenue"))

    # Margins
    gm, em, ebm = calc_margins(
        raw.get("ltm_revenue"),
        raw.get("ltm_gross_profit"),
        raw.get("ltm_ebitda"),
        raw.get("ltm_ebit"),
    )

    # Valuation multiples
    ntm_ev_rev = calc_ntm_ev_revenue(tev, ntm_rev)
    ltm_ev_rev = calc_ltm_ev_revenue(tev, raw.get("ltm_revenue"))
    ntm_ev_ebitda = calc_ntm_ev_ebitda(tev, ntm_ebitda=None, ntm_revenue=ntm_rev, ebitda_margin=em)
    ltm_ev_ebitda = calc_ltm_ev_ebitda(tev, raw.get("ltm_ebitda"))

    # P/E
    ntm_pe = calc_ntm_pe(raw.get("current_price"), raw.get("next_fy_eps_est"))
    if ntm_pe is None:
        ntm_pe = raw.get("forward_pe")

    # FCF yield and leverage
    fcf_y = calc_fcf_yield(raw.get("free_cash_flow"), tev)
    nd_ebitda = calc_net_debt_ebitda(raw.get("total_debt"), raw.get("total_cash"), raw.get("ltm_ebitda"))

    # Price performance
    pct_52 = calc_pct_52wk_high(raw.get("current_price"), raw.get("fifty_two_week_high"))
    chg_2w, chg_2m = calc_price_changes(raw.get("price_history"))

    return {
        "ticker": ticker,
        "snapshot_date": today_str,
        "name": info.get("name"),
        "sector": info.get("sector"),
        "sub_sector": info.get("sub_sector"),
        "exchange": info.get("exchange"),
        "listing_country": info.get("listing_country"),
        "current_price": raw.get("current_price"),
        "market_cap": raw.get("market_cap"),
        "enterprise_value": tev,
        "total_debt": raw.get("total_debt"),
        "total_cash": raw.get("total_cash"),
        "shares_outstanding": raw.get("shares_outstanding"),
        "fifty_two_week_high": raw.get("fifty_two_week_high"),
        "currency": raw.get("currency"),
        "ltm_revenue": raw.get("ltm_revenue"),
        "ltm_gross_profit": raw.get("ltm_gross_profit"),
        "ltm_ebitda": raw.get("ltm_ebitda"),
        "ltm_ebit": raw.get("ltm_ebit"),
        "gross_margin": gm,
        "ebitda_margin": em,
        "ebit_margin": ebm,
        "current_fy_rev_est": raw.get("current_fy_rev_est"),
        "next_fy_rev_est": raw.get("next_fy_rev_est"),
        "ntm_revenue": ntm_rev,
        "ntm_revenue_growth": ntm_rev_growth,
        "ntm_ev_revenue": ntm_ev_rev,
        "ltm_ev_revenue": ltm_ev_rev,
        "ntm_ev_ebitda": ntm_ev_ebitda,
        "ltm_ev_ebitda": ltm_ev_ebitda,
        "ntm_pe": ntm_pe,
        "fcf_yield": fcf_y,
        "dividend_yield": raw.get("dividend_yield"),
        "net_debt_ebitda": nd_ebitda,
        "pct_52wk_high": pct_52,
        "price_change_2w": chg_2w,
        "price_change_2m": chg_2m,
        "free_cash_flow": raw.get("free_cash_flow"),
        "fetch_timestamp": now_str,
    }


def run_full_fetch(limit: int = None, sector_filter: str = None):
    """Main fetch loop."""
    db = DBManager(DB_PATH)
    db.init_schema()

    tickers = list(COMPANY_REGISTRY.items())

    if sector_filter:
        tickers = [(t, i) for t, i in tickers if i["sector"] == sector_filter]

    if limit:
        tickers = tickers[:limit]

    total = len(tickers)
    fetched = 0
    failed = 0

    logger.info(f"Starting fetch for {total} companies")

    for idx, (ticker, info) in enumerate(tickers, 1):
        try:
            logger.info(f"[{idx}/{total}] {ticker} ({info['name'][:40]})")
            raw = fetch_company_data(ticker)

            if raw is None:
                logger.warning(f"  SKIP: no data returned")
                failed += 1
                continue

            snapshot = process_one_company(ticker, info, raw)
            db.upsert_snapshot(snapshot)
            fetched += 1

            # Polite delay to avoid rate limiting
            if idx < total:
                time.sleep(0.3)

        except Exception as e:
            logger.error(f"  FAIL: {e}")
            failed += 1

    logger.info(f"Done: {fetched} fetched, {failed} failed, {total} total")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch services comps data")
    parser.add_argument("--limit", type=int, default=None, help="Max companies to fetch")
    parser.add_argument("--sector", type=str, default=None, help="Fetch one sector only")
    args = parser.parse_args()
    run_full_fetch(limit=args.limit, sector_filter=args.sector)
