"""
Field Services, Engineering & TIC comp table.
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

st.title("Field Services, Engineering & TIC")

db = DBManager(DB_PATH)
try:
    data = db.get_latest_snapshots(sector="field_eng_tic")
    render_comp_table(data, "Field Services, Engineering & TIC", show_sub_sectors=True)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Run the data fetcher to populate the database.")
