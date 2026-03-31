"""
Central configuration: paths and display name mappings.
"""

from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = str(BASE_DIR / "data" / "services_comps.db")


SECTOR_DISPLAY: dict[str, str] = {
    "consulting":     "Consulting & Professional Services",
    "insurance":      "Insurance Services",
    "info_data":      "Information & Data Services",
    "it_services":    "IT Services",
    "wealth_mgmt":    "Wealth Management & Advisory",
    "supply_chain":   "Supply Chain Services",
    "field_eng_tic":  "Field Services, Engineering & TIC",
    "property":       "Property Services",
    "education":      "Education",
    "alt_asset_mgmt": "Alternative Asset Management",
}


SECTOR_ORDER: list[str] = [
    "consulting",
    "insurance",
    "info_data",
    "it_services",
    "wealth_mgmt",
    "supply_chain",
    "field_eng_tic",
    "property",
    "education",
    "alt_asset_mgmt",
]
