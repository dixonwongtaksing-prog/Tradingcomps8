"""
Financial metric calculations for services trading comps.
All pure functions, no I/O, no state.
"""

from datetime import date


def calc_ntm_revenue(current_fy_rev_est, next_fy_rev_est, fy_end_month=12):
    """
    NTM Revenue = weighted interpolation between current FY and next FY estimates.
    Weight for current FY = months remaining in current FY / 12.
    """
    if not current_fy_rev_est and not next_fy_rev_est:
        return None
    if not current_fy_rev_est:
        return next_fy_rev_est
    if not next_fy_rev_est:
        return current_fy_rev_est

    today = date.today()
    fy_end_year = today.year if today.month <= fy_end_month else today.year + 1
    months_remaining = max(0, (fy_end_year - today.year) * 12 + fy_end_month - today.month)
    months_remaining = min(12, months_remaining)

    w_curr = months_remaining / 12.0
    w_next = 1.0 - w_curr
    return (w_curr * current_fy_rev_est) + (w_next * next_fy_rev_est)


def calc_ntm_revenue_growth(ntm_revenue, ltm_revenue):
    """NTM Revenue Growth = (NTM Rev / LTM Rev) - 1."""
    if ntm_revenue and ltm_revenue and ltm_revenue > 0:
        return (ntm_revenue / ltm_revenue) - 1.0
    return None


def calc_tev(market_cap, total_debt, total_cash):
    """TEV = Market Cap + Total Debt - Total Cash."""
    if not market_cap:
        return None
    debt = total_debt or 0
    cash = total_cash or 0
    return market_cap + debt - cash


def calc_pct_52wk_high(current_price, fifty_two_week_high):
    """Current price as % of 52 week high."""
    if current_price and fifty_two_week_high and fifty_two_week_high > 0:
        return current_price / fifty_two_week_high
    return None


def calc_margins(ltm_revenue, ltm_gross_profit, ltm_ebitda, ltm_ebit):
    """
    Compute gross, EBITDA, and EBIT margins.
    Returns (gross_margin, ebitda_margin, ebit_margin) as decimals.
    """
    gm = em = ebm = None
    if ltm_revenue and ltm_revenue > 0:
        if ltm_gross_profit is not None:
            gm = ltm_gross_profit / ltm_revenue
        if ltm_ebitda is not None:
            em = ltm_ebitda / ltm_revenue
        if ltm_ebit is not None:
            ebm = ltm_ebit / ltm_revenue
    return gm, em, ebm


def calc_ntm_ev_revenue(tev, ntm_revenue):
    """NTM EV/Revenue multiple."""
    if tev and ntm_revenue and ntm_revenue > 0:
        val = tev / ntm_revenue
        return val if val < 100 else None  # sanity cap
    return None


def calc_ltm_ev_revenue(tev, ltm_revenue):
    """LTM EV/Revenue multiple."""
    if tev and ltm_revenue and ltm_revenue > 0:
        val = tev / ltm_revenue
        return val if val < 100 else None
    return None


def calc_ntm_ev_ebitda(tev, ntm_ebitda=None, ntm_revenue=None, ebitda_margin=None):
    """
    NTM EV/EBITDA.
    Falls back to NTM Revenue * EBITDA Margin if no consensus EBITDA available.
    """
    ebitda = ntm_ebitda
    if not ebitda and ntm_revenue and ebitda_margin and ebitda_margin > 0:
        ebitda = ntm_revenue * ebitda_margin
    if tev and ebitda and ebitda > 0:
        val = tev / ebitda
        return val if 0 < val < 200 else None  # sanity cap
    return None


def calc_ltm_ev_ebitda(tev, ltm_ebitda):
    """LTM EV/EBITDA."""
    if tev and ltm_ebitda and ltm_ebitda > 0:
        val = tev / ltm_ebitda
        return val if 0 < val < 200 else None
    return None


def calc_ntm_pe(current_price, next_fy_eps_est):
    """NTM P/E = Price / Next FY EPS estimate."""
    if current_price and next_fy_eps_est and next_fy_eps_est > 0:
        val = current_price / next_fy_eps_est
        return val if 0 < val < 500 else None
    return None


def calc_fcf_yield(free_cash_flow, enterprise_value):
    """FCF Yield = Free Cash Flow / Enterprise Value."""
    if free_cash_flow and enterprise_value and enterprise_value > 0:
        return free_cash_flow / enterprise_value
    return None


def calc_net_debt_ebitda(total_debt, total_cash, ltm_ebitda):
    """Net Debt / EBITDA = (Debt - Cash) / EBITDA."""
    if ltm_ebitda and ltm_ebitda > 0:
        debt = total_debt or 0
        cash = total_cash or 0
        return (debt - cash) / ltm_ebitda
    return None


def calc_price_changes(price_history):
    """
    Compute 2 week and 2 month price changes from a price history DataFrame.
    Returns (change_2w, change_2m) as decimals.
    """
    if price_history is None or len(price_history) < 2:
        return None, None

    closes = price_history["Close"]
    if not hasattr(closes, "iloc"):
        return None, None

    latest = closes.iloc[-1]

    # 2 week ~ 10 trading days
    idx_2w = min(10, len(closes) - 1)
    price_2w_ago = closes.iloc[-(idx_2w + 1)]
    change_2w = (latest / price_2w_ago) - 1.0 if price_2w_ago > 0 else None

    # 2 month ~ 42 trading days
    idx_2m = min(42, len(closes) - 1)
    price_2m_ago = closes.iloc[-(idx_2m + 1)]
    change_2m = (latest / price_2m_ago) - 1.0 if price_2m_ago > 0 else None

    return change_2w, change_2m
