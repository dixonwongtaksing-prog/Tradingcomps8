"""
Information & Data Services comp table.
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.sidebar import render_sidebar
from components.comp_table import render_comp_table
from config.settings import DB_PATH
from fetcher.db_manager import DBManager

render_sidebar()

st.title("Information & Data Services")

db = DBManager(DB_PATH)
try:
    data = db.get_latest_snapshots(sector="info_data")
    render_comp_table(data, "Information & Data Services", show_sub_sectors=True)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Run the data fetcher to populate the database.")
