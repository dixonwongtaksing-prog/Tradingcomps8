"""
Services Trading Comparable Analysis
Main Streamlit entrypoint.
"""

import streamlit as st

st.set_page_config(
    page_title="Services Trading Comps",
    page_icon=":material/bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}
.stApp { background-color: #FAFBFC !important; }
.main .block-container {
    background-color: #FAFBFC !important;
    max-width: 100% !important;
    padding-top: 1rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    padding-bottom: 1rem !important;
    color: #111827 !important;
}
h1 { margin-top: 0 !important; padding-top: 0 !important; }
h1, h2, h3, h4, h5, h6 { color: #111827 !important; }
h4 {
    font-size: 15px !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    border-left: 3px solid #3B82F6 !important;
    padding-left: 10px !important;
    margin-top: 1.5rem !important;
    color: #374151 !important;
}

#MainMenu { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }
footer { visibility: hidden; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="collapsedControl"]        { display: none !important; }
section[data-testid="stSidebar"] {
    transform: none !important;
    min-width: 244px !important;
    max-width: 344px !important;
    visibility: visible !important;
    display: flex !important;
    opacity: 1 !important;
}
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

div[data-testid="stDataFrame"] table {
    font-size: 13px !important;
    font-family: 'DM Sans', sans-serif !important;
}
div[data-testid="stDataFrame"] th {
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    color: #6B7280 !important;
    background-color: #F9FAFB !important;
    border-bottom: 2px solid #E5E7EB !important;
    padding: 8px 10px !important;
    white-space: nowrap !important;
}
div[data-testid="stDataFrame"] td {
    padding: 6px 10px !important;
    border-bottom: 1px solid #F3F4F6 !important;
    white-space: nowrap !important;
    color: #111827 !important;
}

div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border-radius: 10px;
    padding: 12px 16px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
div[data-testid="stMetric"] label {
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #6B7280 !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #111827 !important;
}

hr { border-color: #E5E7EB !important; margin: 1.5rem 0 !important; }

div[data-testid="stCaptionContainer"] p,
.stCaption p {
    font-size: 12px !important;
    color: #9CA3AF !important;
}

.stTabs [data-baseweb="tab-list"] {
    border-bottom: 1px solid #E5E7EB !important;
    gap: 4px !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"], button[role="tab"] {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #9CA3AF !important;
    background: transparent !important;
    border-bottom: 2px solid transparent !important;
    padding: 10px 20px !important;
}
.stTabs [aria-selected="true"], button[role="tab"][aria-selected="true"] {
    color: #111827 !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #3B82F6 !important;
}

div[data-testid="stSelectbox"] label,
div[data-testid="stMultiSelect"] label,
div[data-testid="stRadio"] label {
    color: #374151 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
}

.stButton button {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    color: #374151 !important;
    border-radius: 6px !important;
}
.stButton button:hover {
    border-color: #D1D5DB !important;
    background: #F9FAFB !important;
}
</style>
""", unsafe_allow_html=True)


pg = st.navigation({
    "Overview": [
        st.Page("views/01_Overview.py",      title="Overview",                    icon=":material/dashboard:"),
    ],
    "Sector Comps": [
        st.Page("views/02_Consulting.py",    title="Consulting & Prof. Svc",      icon=":material/groups:"),
        st.Page("views/03_Insurance.py",     title="Insurance",                   icon=":material/shield:"),
        st.Page("views/04_Info_Data.py",     title="Information & Data",          icon=":material/database:"),
        st.Page("views/05_IT_Services.py",   title="IT Services",                icon=":material/computer:"),
        st.Page("views/06_Wealth_Mgmt.py",   title="Wealth & Advisory",          icon=":material/account_balance:"),
        st.Page("views/07_Supply_Chain.py",  title="Supply Chain",               icon=":material/local_shipping:"),
        st.Page("views/08_Field_Eng_TIC.py", title="Field / Eng / TIC",          icon=":material/engineering:"),
        st.Page("views/09_Property.py",      title="Property",                   icon=":material/home_work:"),
        st.Page("views/10_Education.py",     title="Education",                  icon=":material/school:"),
        st.Page("views/11_Alt_Asset.py",     title="Alt Asset Mgmt",             icon=":material/trending_up:"),
    ],
    "Explore": [
        st.Page("views/20_Screener.py",      title="Screener",                   icon=":material/filter_alt:"),
    ],
})

pg.run()
