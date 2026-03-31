"""
Scenario screener: filter the full universe by valuation, growth, margin, leverage.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.sidebar import render_sidebar
from components.comp_table import render_comp_table
from config.settings import DB_PATH, SECTOR_DISPLAY, SECTOR_ORDER
from fetcher.db_manager import DBManager

render_sidebar()

st.title("Screener")
st.markdown(
    '<p style="color:#94A3B8;font-size:13px;margin:-8px 0 16px 0;">'
    'Filter the universe by valuation, growth, profitability, and leverage.</p>',
    unsafe_allow_html=True,
)

db = DBManager(DB_PATH)
data = db.get_all_latest_snapshots()

if not data:
    st.info("No data available. Run the data fetcher to populate the database.")
    st.stop()

df = pd.DataFrame(data)

# Numeric conversion
num_cols = [
    "enterprise_value", "market_cap", "ntm_ev_ebitda", "ntm_ev_revenue",
    "ntm_pe", "ntm_revenue_growth", "ebitda_margin", "ebit_margin",
    "gross_margin", "fcf_yield", "net_debt_ebitda", "dividend_yield",
]
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# Filters
st.markdown(
    '<h4 style="font-size:14px;font-weight:600;border-left:3px solid #3B82F6;'
    'padding-left:10px;color:#374151;margin:0 0 10px 0;">Filters</h4>',
    unsafe_allow_html=True,
)

fc1, fc2, fc3 = st.columns(3)

with fc1:
    sector_options = ["All Sectors"] + [SECTOR_DISPLAY.get(s, s) for s in SECTOR_ORDER]
    sector_pick = st.selectbox("Sector", sector_options)

    tev_bands = {
        "Any": (None, None),
        "< $500mm": (None, 500e6),
        "$500mm to $2B": (500e6, 2e9),
        "$2B to $10B": (2e9, 10e9),
        "$10B to $50B": (10e9, 50e9),
        "> $50B": (50e9, None),
    }
    tev_pick = st.selectbox("TEV Range", list(tev_bands.keys()))

with fc2:
    ev_ebitda_max = st.slider("Max NTM EV/EBITDA", 5.0, 50.0, 30.0, step=1.0)
    growth_min = st.slider("Min NTM Rev Growth (%)", -20.0, 50.0, 0.0, step=1.0)

with fc3:
    ebitda_min = st.slider("Min EBITDA Margin (%)", -10.0, 50.0, 0.0, step=1.0)
    nd_max = st.slider("Max Net Debt/EBITDA", 0.0, 10.0, 5.0, step=0.5)

# Apply filters
filtered = df.copy()

if sector_pick != "All Sectors":
    sector_key = [k for k, v in SECTOR_DISPLAY.items() if v == sector_pick]
    if sector_key:
        filtered = filtered[filtered["sector"] == sector_key[0]]

tev_lo, tev_hi = tev_bands[tev_pick]
if tev_lo is not None:
    filtered = filtered[filtered["enterprise_value"] >= tev_lo]
if tev_hi is not None:
    filtered = filtered[filtered["enterprise_value"] <= tev_hi]

filtered = filtered[
    (filtered["ntm_ev_ebitda"].isna()) | (filtered["ntm_ev_ebitda"] <= ev_ebitda_max)
]
filtered = filtered[
    (filtered["ntm_revenue_growth"].isna()) | (filtered["ntm_revenue_growth"] >= growth_min / 100)
]
filtered = filtered[
    (filtered["ebitda_margin"].isna()) | (filtered["ebitda_margin"] >= ebitda_min / 100)
]
filtered = filtered[
    (filtered["net_debt_ebitda"].isna()) | (filtered["net_debt_ebitda"] <= nd_max)
]

st.markdown(
    f'<p style="color:#6B7280;font-size:13px;margin:12px 0 4px 0;">'
    f'{len(filtered)} of {len(df)} companies match filters</p>',
    unsafe_allow_html=True,
)

# Render
render_comp_table(
    filtered.to_dict("records"),
    "Screener Results",
    show_sub_sectors=True,
)
