"""
Cell rendering functions for comp table HTML.
Each function takes a raw value and returns an HTML string for one table cell.
"""

import math


def _is_valid(val) -> bool:
    if val is None:
        return False
    try:
        return not math.isnan(val) and not math.isinf(val)
    except (TypeError, ValueError):
        return False


DASH = '<span style="color:#CBD5E1;">—</span>'


def fmt_dollar_m(val) -> str:
    """Format as $mm: '$1,234' or dash."""
    if not _is_valid(val):
        return DASH
    v = val / 1e6
    if abs(v) >= 1000:
        return f"${v:,.0f}"
    return f"${v:,.1f}"


def fmt_price(val) -> str:
    """Format price: '$45.67' or dash."""
    if not _is_valid(val):
        return DASH
    return f"${val:,.2f}"


def fmt_multiple(val) -> str:
    """Format valuation multiple: '12.3x' or dash."""
    if not _is_valid(val):
        return DASH
    return f"{val:.1f}x"


def fmt_pct(val) -> str:
    """Format as percentage: '67.2%' or dash. Expects decimal input (0.67)."""
    if not _is_valid(val):
        return DASH
    return f"{val * 100:.1f}%"


def fmt_growth(val) -> str:
    """Growth as coloured pill: green positive, red negative."""
    if not _is_valid(val):
        return DASH
    pct = val * 100
    if pct >= 0:
        bg, color = "#ECFDF5", "#059669"
        sign = "+"
    else:
        bg, color = "#FEF2F2", "#DC2626"
        sign = ""
    return (
        f'<span style="background:{bg};color:{color};padding:2px 7px;'
        f'border-radius:4px;font-size:11px;font-weight:500;">'
        f'{sign}{pct:.1f}%</span>'
    )


def fmt_margin(val) -> str:
    """Margin as percentage with subtle colour intensity."""
    if not _is_valid(val):
        return DASH
    pct = val * 100
    if pct >= 25:
        color = "#059669"
    elif pct >= 15:
        color = "#D97706"
    elif pct >= 0:
        color = "#374151"
    else:
        color = "#DC2626"
    return f'<span style="color:{color};">{pct:.1f}%</span>'


def fmt_leverage(val) -> str:
    """Net Debt/EBITDA with red flag if > 3x."""
    if not _is_valid(val):
        return DASH
    if val > 3.0:
        color = "#DC2626"
    elif val > 2.0:
        color = "#D97706"
    elif val < 0:
        color = "#059669"  # net cash
    else:
        color = "#374151"
    return f'<span style="color:{color};">{val:.1f}x</span>'


def fmt_change(val) -> str:
    """Price change as coloured percentage."""
    if not _is_valid(val):
        return DASH
    pct = val * 100
    if pct >= 0:
        color = "#059669"
        sign = "+"
    else:
        color = "#DC2626"
        sign = ""
    return f'<span style="color:{color};font-size:11px;">{sign}{pct:.1f}%</span>'


def fmt_fcf_yield(val) -> str:
    """FCF yield with colour."""
    if not _is_valid(val):
        return DASH
    pct = val * 100
    if pct >= 5:
        color = "#059669"
    elif pct >= 0:
        color = "#374151"
    else:
        color = "#DC2626"
    return f'<span style="color:{color};">{pct:.1f}%</span>'


def fmt_div_yield(val) -> str:
    """Dividend yield."""
    if not _is_valid(val):
        return DASH
    pct = val * 100
    return f"{pct:.1f}%"
