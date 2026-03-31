"""
Shared sidebar component: dark rail, institutional style.
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import DB_PATH
from fetcher.db_manager import DBManager


def render_sidebar():
    """Render the shared sidebar across all pages."""

    st.markdown("""
<style>
html { zoom: 0.9; }
.block-container {
    padding-top: 1.25rem !important;
    padding-bottom: 0.5rem !important;
}
.block-container h1 {
    margin-bottom: 0.4rem !important;
    padding-bottom: 0 !important;
}
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="collapsedControl"]        { display: none !important; }
section[data-testid="stSidebar"] {
    transform: none !important;
    min-width: 244px !important;
    max-width: 244px !important;
    visibility: visible !important;
    display: flex !important;
    opacity: 1 !important;
    background-color: #111827 !important;
    border-right: 1px solid #1F2937 !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] li {
    color: #9CA3AF !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #F1F5F9 !important;
}
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] .stCaption p {
    color: #4B5563 !important;
}
section[data-testid="stSidebar"] hr {
    border-color: #1F2937 !important;
    opacity: 1 !important;
    margin: 14px 0 !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"],
section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] span {
    color: #374151 !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.10em !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] span {
    color: #6B7280 !important;
    font-size: 13px !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] a {
    border-radius: 6px !important;
    transition: background 0.12s ease;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] a:hover {
    background-color: #1E293B !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] [aria-selected="true"] {
    background-color: #1E293B !important;
    border-left: 2px solid #3B82F6 !important;
    border-radius: 0 6px 6px 0 !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] [aria-selected="true"] span {
    color: #E2E8F0 !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

    # Wordmark
    st.sidebar.markdown(
        "<div style='padding:4px 0 14px 0;'>"
        "<div style='font-size:10px;font-weight:700;text-transform:uppercase;"
        "letter-spacing:0.12em;color:#3B82F6;margin-bottom:6px;'>Services Comps</div>"
        "<div style='font-size:15px;font-weight:600;color:#F1F5F9;line-height:1.4;'>"
        "Trading Comparable<br>"
        "<span style='color:#4B5563;font-weight:400;font-size:13px;'>Analysis</span>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.divider()

    # Last updated
    db = DBManager(DB_PATH)
    try:
        last_fetch = db.get_last_fetch_time()
        if last_fetch:
            date_str = last_fetch[:10]
            time_str = last_fetch[11:16]
            st.sidebar.markdown(
                "<p style='font-size:10px;font-weight:700;color:#374151;"
                "text-transform:uppercase;letter-spacing:0.10em;margin:0 0 5px 0;'>"
                "Last Updated</p>"
                f"<p style='font-size:13px;font-weight:600;color:#CBD5E1;margin:0 0 1px 0;'>"
                f"{date_str}</p>"
                f"<p style='font-size:11px;color:#4B5563;margin:0;'>{time_str} UTC</p>",
                unsafe_allow_html=True,
            )
        else:
            st.sidebar.markdown(
                "<p style='font-size:12px;color:#4B5563;margin:0;'>No data yet.</p>",
                unsafe_allow_html=True,
            )
    except Exception:
        st.sidebar.markdown(
            "<p style='font-size:12px;color:#4B5563;margin:0;'>DB not initialized.</p>",
            unsafe_allow_html=True,
        )

    st.sidebar.divider()

    # Data source
    st.sidebar.markdown(
        "<p style='font-size:10px;font-weight:700;color:#374151;"
        "text-transform:uppercase;letter-spacing:0.10em;margin:0 0 5px 0;'>"
        "Data Source</p>"
        "<p style='font-size:13px;font-weight:600;color:#CBD5E1;margin:0;'>Yahoo Finance</p>",
        unsafe_allow_html=True,
    )
