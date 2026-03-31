"""
Yahoo Finance data fetcher.
Pulls raw market data for a single company.
Designed for easy swap to FactSet: just replace this file and change one import.
"""

import logging
import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)


def fetch_company_data(yahoo_ticker: str) -> dict | None:
    """
    Fetch all raw data for one company from Yahoo Finance.

    Returns a flat dict of raw fields, or None on failure.
    Keys returned:
        current_price, market_cap, enterprise_value,
        total_debt, total_cash, shares_outstanding,
        fifty_two_week_high, currency,
        ltm_revenue, ltm_gross_profit, ltm_ebitda, ltm_ebit,
        current_fy_rev_est, next_fy_rev_est,
        current_fy_eps_est, next_fy_eps_est,
        trailing_pe, forward_pe, dividend_yield,
        free_cash_flow,
        price_history (DataFrame)
    """
    try:
        stock = yf.Ticker(yahoo_ticker)
        info = stock.info or {}

        if not info.get("regularMarketPrice") and not info.get("currentPrice"):
            logger.warning(f"{yahoo_ticker}: no price data returned")
            return None

        result = {}

        result["current_price"] = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
        )
        result["market_cap"] = info.get("marketCap")
        result["enterprise_value"] = info.get("enterpriseValue")
        result["total_debt"] = info.get("totalDebt")
        result["total_cash"] = info.get("totalCash")
        result["shares_outstanding"] = info.get("sharesOutstanding")
        result["fifty_two_week_high"] = info.get("fiftyTwoWeekHigh")
        result["currency"] = info.get("currency", "USD")

        result["ltm_revenue"] = info.get("totalRevenue")
        result["ltm_gross_profit"] = info.get("grossProfits")
        result["ltm_ebitda"] = info.get("ebitda")
        result["ltm_ebit"] = info.get("operatingIncome")

        result["trailing_pe"] = info.get("trailingPE")
        result["forward_pe"] = info.get("forwardPE")
        result["dividend_yield"] = info.get("dividendYield")
        result["free_cash_flow"] = info.get("freeCashflow")

        result["current_fy_rev_est"] = _safe_get(info, "revenueEstimate", "currentYear")
        result["next_fy_rev_est"] = _safe_get(info, "revenueEstimate", "nextYear")
        result["current_fy_eps_est"] = _safe_get(info, "earningsEstimate", "currentYear")
        result["next_fy_eps_est"] = _safe_get(info, "earningsEstimate", "nextYear")

        # Revenue estimates from analyst data if not in info
        if result["current_fy_rev_est"] is None:
            result["current_fy_rev_est"] = _get_analyst_rev_est(stock, 0)
        if result["next_fy_rev_est"] is None:
            result["next_fy_rev_est"] = _get_analyst_rev_est(stock, 1)

        # EPS estimates from analyst data if not in info
        if result["current_fy_eps_est"] is None:
            result["current_fy_eps_est"] = _get_analyst_eps_est(stock, 0)
        if result["next_fy_eps_est"] is None:
            result["next_fy_eps_est"] = _get_analyst_eps_est(stock, 1)

        # Price history for 2w/2m change calculation
        try:
            result["price_history"] = stock.history(period="3mo")
        except Exception:
            result["price_history"] = None

        return result

    except Exception as e:
        logger.error(f"{yahoo_ticker}: fetch failed: {e}")
        return None


def _safe_get(info: dict, *keys):
    """Safely navigate nested dicts."""
    val = info
    for k in keys:
        if isinstance(val, dict):
            val = val.get(k)
        else:
            return None
    return val


def _get_analyst_rev_est(stock, year_offset: int):
    """Try to get revenue estimate from analyst data."""
    try:
        re_df = stock.revenue_estimate
        if re_df is not None and len(re_df.columns) > year_offset:
            avg_row = re_df.loc["avg"] if "avg" in re_df.index else None
            if avg_row is not None:
                return avg_row.iloc[year_offset]
    except Exception:
        pass
    return None


def _get_analyst_eps_est(stock, year_offset: int):
    """Try to get EPS estimate from analyst data."""
    try:
        ee_df = stock.earnings_estimate
        if ee_df is not None and len(ee_df.columns) > year_offset:
            avg_row = ee_df.loc["avg"] if "avg" in ee_df.index else None
            if avg_row is not None:
                return avg_row.iloc[year_offset]
    except Exception:
        pass
    return None
