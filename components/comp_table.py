"""
Comp table renderer: custom HTML table with sticky Company + Ticker columns,
mean/median summary rows pinned at top, column sort via JS, sub sector badges.
"""

import html as _html
import math
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as _st_comps

from config.color_palette import BADGE_STYLES
from config.settings import SECTOR_DISPLAY
from components.formatters import (
    fmt_dollar_m, fmt_price, fmt_multiple, fmt_pct,
    fmt_growth, fmt_margin, fmt_leverage, fmt_change,
    fmt_fcf_yield, fmt_div_yield, DASH,
)

# Column definitions: (label, df_key, width_px, format_func, text_align)
COLUMNS = [
    ("TEV ($mm)",       "enterprise_value",    90,  fmt_dollar_m,  "right"),
    ("Mkt Cap ($mm)",   "market_cap",          90,  fmt_dollar_m,  "right"),
    ("Price",           "current_price",       70,  fmt_price,     "right"),
    ("% 52wk Hi",       "pct_52wk_high",       76,  fmt_pct,       "right"),
    ("NTM Rev Gr",      "ntm_revenue_growth",  76,  fmt_growth,    "right"),
    ("Gross Mgn",       "gross_margin",        76,  fmt_margin,    "right"),
    ("EBITDA Mgn",      "ebitda_margin",       80,  fmt_margin,    "right"),
    ("EBIT Mgn",        "ebit_margin",         76,  fmt_margin,    "right"),
    ("NTM EV/Rev",      "ntm_ev_revenue",      76,  fmt_multiple,  "right"),
    ("NTM EV/EBITDA",   "ntm_ev_ebitda",       90,  fmt_multiple,  "right"),
    ("LTM EV/EBITDA",   "ltm_ev_ebitda",       90,  fmt_multiple,  "right"),
    ("NTM P/E",         "ntm_pe",              70,  fmt_multiple,  "right"),
    ("FCF Yield",       "fcf_yield",           76,  fmt_fcf_yield, "right"),
    ("Div Yield",       "dividend_yield",      76,  fmt_div_yield, "right"),
    ("ND/EBITDA",       "net_debt_ebitda",     80,  fmt_leverage,  "right"),
    ("2W Chg",          "price_change_2w",     60,  fmt_change,    "right"),
    ("2M Chg",          "price_change_2m",     60,  fmt_change,    "right"),
]


def _safe_median(series):
    clean = series.dropna()
    return clean.median() if len(clean) > 0 else None


def _safe_mean(series):
    clean = series.dropna()
    return clean.mean() if len(clean) > 0 else None


def _build_summary_rows(df: pd.DataFrame) -> list[dict]:
    """Compute mean and median for all numeric columns."""
    rows = []
    for label, func in [("Median", _safe_median), ("Mean", _safe_mean)]:
        row = {"_summary_label": label}
        for _, key, _, _, _ in COLUMNS:
            if key in df.columns:
                row[key] = func(df[key])
            else:
                row[key] = None
        rows.append(row)
    return rows


def _sub_sector_badge(sub_sector: str, sector: str) -> str:
    """Render a small coloured badge for the sub sector."""
    if not sub_sector:
        return ""
    bg, color = BADGE_STYLES.get(sector, ("#F3F4F6", "#6B7280"))
    label = sub_sector.replace("_", " ").title()
    if len(label) > 35:
        label = label[:32] + "..."
    return (
        f'<span style="background:{bg};color:{color};padding:1px 6px;'
        f'border-radius:3px;font-size:9px;font-weight:500;'
        f'white-space:nowrap;">{_html.escape(label)}</span>'
    )


def _render_html_table(df: pd.DataFrame, summary_rows: list[dict],
                       show_sub_sectors: bool = True) -> str:
    """Build the full HTML table string."""

    # Styles
    TH = (
        "padding:7px 10px;font-size:10px;font-weight:600;"
        "text-transform:uppercase;letter-spacing:0.03em;"
        "color:#64748B;background:#F9FAFB;"
        "border-bottom:2px solid #E5E7EB;white-space:nowrap;"
        "position:sticky;top:0;z-index:2;"
    )
    TD = "padding:6px 10px;border-bottom:1px solid #F3F4F6;white-space:nowrap;font-size:12px;"
    STICKY_TH = TH + "position:sticky;z-index:4;background:#F9FAFB;"
    STICKY_TD = TD + "position:sticky;z-index:3;background:inherit;"

    # Header row
    header = '<tr>'
    header += f'<th style="{STICKY_TH}left:0;min-width:160px;text-align:left;">Company</th>'
    header += f'<th style="{STICKY_TH}left:160px;min-width:70px;text-align:left;">Ticker</th>'
    if show_sub_sectors:
        header += f'<th style="{TH}min-width:140px;text-align:left;">Sub Sector</th>'
    for label, _, width, _, align in COLUMNS:
        header += f'<th style="{TH}min-width:{width}px;text-align:{align};">{label}</th>'
    header += '</tr>'

    # Summary rows (mean/median pinned at top)
    summary_html = ""
    for srow in summary_rows:
        lbl = srow["_summary_label"]
        summary_html += '<tr style="background:#F0F4FF;">'
        summary_html += (
            f'<td style="{STICKY_TD}left:0;font-weight:600;color:#1D4ED8;font-size:11px;">'
            f'{lbl}</td>'
        )
        summary_html += f'<td style="{STICKY_TD}left:160px;"></td>'
        if show_sub_sectors:
            summary_html += f'<td style="{TD}"></td>'
        for _, key, _, fmt_fn, align in COLUMNS:
            val = srow.get(key)
            cell = fmt_fn(val) if val is not None else DASH
            summary_html += f'<td style="{TD}text-align:{align};font-weight:600;font-size:11px;">{cell}</td>'
        summary_html += '</tr>'

    # Data rows
    body_html = ""
    for _, row in df.iterrows():
        name = _html.escape(str(row.get("name", "")))
        ticker = _html.escape(str(row.get("ticker", "")))
        sector = row.get("sector", "")
        sub = row.get("sub_sector", "")

        body_html += '<tr>'
        body_html += (
            f'<td style="{STICKY_TD}left:0;background:#FFFFFF;">'
            f'<span style="font-size:12px;color:#111827;">{name}</span></td>'
        )
        body_html += (
            f'<td style="{STICKY_TD}left:160px;background:#FFFFFF;">'
            f'<span style="font-size:11px;font-weight:600;color:#1D4ED8;">{ticker}</span></td>'
        )
        if show_sub_sectors:
            badge = _sub_sector_badge(sub, sector)
            body_html += f'<td style="{TD}">{badge}</td>'

        for _, key, _, fmt_fn, align in COLUMNS:
            val = row.get(key)
            cell = fmt_fn(val)
            body_html += f'<td style="{TD}text-align:{align};">{cell}</td>'
        body_html += '</tr>'

    total_width = 160 + 70 + (140 if show_sub_sectors else 0) + sum(w for _, _, w, _, _ in COLUMNS) + 100

    return f"""
    <div style="overflow-x:auto;border:1px solid #E5E7EB;border-radius:8px;background:#FFFFFF;">
        <table style="width:{total_width}px;border-collapse:collapse;font-family:'DM Sans',sans-serif;">
            <thead>{header}</thead>
            <tbody>{summary_html}{body_html}</tbody>
        </table>
    </div>
    """


def render_comp_table(data: list[dict], title: str, show_sub_sectors: bool = True):
    """
    Main entry point: renders a full comp table from snapshot data.

    Args:
        data: list of snapshot dicts from db_manager
        title: section title
        show_sub_sectors: whether to show sub sector badge column
    """
    if not data:
        st.info("No data available. Run the data fetcher to populate the database.")
        return

    df = pd.DataFrame(data)

    # Data freshness
    if "fetch_timestamp" in df.columns:
        latest = df["fetch_timestamp"].dropna().max()
        if latest:
            date_part = str(latest)[:10]
            st.markdown(
                f'<p style="color:#94A3B8;font-size:12px;margin:-8px 0 12px 0;">'
                f'Data as of {date_part} · {len(df)} companies</p>',
                unsafe_allow_html=True,
            )

    # Summary rows
    numeric_cols = [key for _, key, _, _, _ in COLUMNS]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    summary_rows = _build_summary_rows(df)

    # Sort by name
    df = df.sort_values("name", key=lambda s: s.str.lower(), na_position="last")

    # Render
    html = _render_html_table(df, summary_rows, show_sub_sectors)
    st.markdown(html, unsafe_allow_html=True)
