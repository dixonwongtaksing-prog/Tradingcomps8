"""
Overview page: cross sector valuation summary.
Shows median multiples and key metrics per sector in a summary table.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.sidebar import render_sidebar
from config.settings import DB_PATH, SECTOR_DISPLAY, SECTOR_ORDER
from config.color_palette import SECTOR_COLORS, BADGE_STYLES
from fetcher.db_manager import DBManager

render_sidebar()

st.title("Services Comps Overview")

db = DBManager(DB_PATH)
data = db.get_all_latest_snapshots()

if not data:
    st.info("No data available. Run the data fetcher to populate the database.")
    st.stop()

df = pd.DataFrame(data)

# Data freshness
if "fetch_timestamp" in df.columns:
    latest = df["fetch_timestamp"].dropna().max()
    if latest:
        st.markdown(
            f'<p style="color:#94A3B8;font-size:12px;margin:-8px 0 16px 0;">'
            f'Data as of {str(latest)[:10]} · {len(df)} companies across {df["sector"].nunique()} sectors</p>',
            unsafe_allow_html=True,
        )

# Top level metrics
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Companies", len(df))
with c2:
    med_ev_ebitda = df["ntm_ev_ebitda"].dropna().median()
    st.metric("Median NTM EV/EBITDA", f"{med_ev_ebitda:.1f}x" if med_ev_ebitda else "N/A")
with c3:
    med_ev_rev = df["ntm_ev_revenue"].dropna().median()
    st.metric("Median NTM EV/Rev", f"{med_ev_rev:.1f}x" if med_ev_rev else "N/A")
with c4:
    med_growth = df["ntm_revenue_growth"].dropna().median()
    st.metric("Median NTM Rev Growth", f"{med_growth*100:.1f}%" if med_growth else "N/A")

st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

# Sector summary table
st.markdown(
    '<h4 style="font-size:15px;font-weight:600;border-left:3px solid #3B82F6;'
    'padding-left:10px;color:#374151;margin:0 0 12px 0;">Sector Summary</h4>',
    unsafe_allow_html=True,
)

TH = (
    "padding:8px 10px;font-size:10px;font-weight:600;"
    "text-transform:uppercase;letter-spacing:0.03em;"
    "color:#64748B;background:#F9FAFB;"
    "border-bottom:2px solid #E5E7EB;white-space:nowrap;text-align:right;"
)
TD = "padding:7px 10px;border-bottom:1px solid #F3F4F6;white-space:nowrap;font-size:12px;text-align:right;"

header = '<tr>'
header += f'<th style="{TH}text-align:left;min-width:200px;">Sector</th>'
header += f'<th style="{TH}">#</th>'
header += f'<th style="{TH}">Med EV/EBITDA</th>'
header += f'<th style="{TH}">Med EV/Rev</th>'
header += f'<th style="{TH}">Med P/E</th>'
header += f'<th style="{TH}">Med Rev Gr</th>'
header += f'<th style="{TH}">Med EBITDA Mgn</th>'
header += f'<th style="{TH}">Med FCF Yield</th>'
header += f'<th style="{TH}">Med ND/EBITDA</th>'
header += '</tr>'

body = ""
for sector_key in SECTOR_ORDER:
    sdf = df[df["sector"] == sector_key]
    if len(sdf) == 0:
        continue

    display_name = SECTOR_DISPLAY.get(sector_key, sector_key)
    bg, color = BADGE_STYLES.get(sector_key, ("#F3F4F6", "#6B7280"))

    def _med(col):
        v = sdf[col].dropna().median() if col in sdf.columns else None
        return v

    ev_ebitda = _med("ntm_ev_ebitda")
    ev_rev = _med("ntm_ev_revenue")
    pe = _med("ntm_pe")
    growth = _med("ntm_revenue_growth")
    ebitda_m = _med("ebitda_margin")
    fcf_y = _med("fcf_yield")
    nd_eb = _med("net_debt_ebitda")

    def _f_mult(v):
        return f"{v:.1f}x" if v is not None and not np.isnan(v) else '<span style="color:#CBD5E1;">—</span>'

    def _f_pct(v):
        if v is None or np.isnan(v):
            return '<span style="color:#CBD5E1;">—</span>'
        return f"{v*100:.1f}%"

    body += '<tr>'
    body += (
        f'<td style="{TD}text-align:left;">'
        f'<span style="background:{bg};color:{color};padding:2px 8px;'
        f'border-radius:4px;font-size:11px;font-weight:500;">{display_name}</span></td>'
    )
    body += f'<td style="{TD}color:#6B7280;">{len(sdf)}</td>'
    body += f'<td style="{TD}font-weight:600;">{_f_mult(ev_ebitda)}</td>'
    body += f'<td style="{TD}">{_f_mult(ev_rev)}</td>'
    body += f'<td style="{TD}">{_f_mult(pe)}</td>'
    body += f'<td style="{TD}">{_f_pct(growth)}</td>'
    body += f'<td style="{TD}">{_f_pct(ebitda_m)}</td>'
    body += f'<td style="{TD}">{_f_pct(fcf_y)}</td>'
    body += f'<td style="{TD}">{_f_mult(nd_eb)}</td>'
    body += '</tr>'

html = f"""
<div style="overflow-x:auto;border:1px solid #E5E7EB;border-radius:8px;background:#FFFFFF;">
    <table style="width:100%;border-collapse:collapse;font-family:'DM Sans',sans-serif;">
        <thead>{header}</thead>
        <tbody>{body}</tbody>
    </table>
</div>
"""
st.markdown(html, unsafe_allow_html=True)
