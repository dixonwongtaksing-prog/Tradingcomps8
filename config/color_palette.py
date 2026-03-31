"""
Colour definitions for all 10 sectors.
Badge styles, Plotly chart tokens.
"""

SECTOR_COLORS: dict[str, str] = {
    "consulting":     "#4A6FA5",
    "insurance":      "#2A9D8F",
    "info_data":      "#6366F1",
    "it_services":    "#0EA5E9",
    "wealth_mgmt":    "#D4A017",
    "supply_chain":   "#E07A3A",
    "field_eng_tic":  "#3D8B37",
    "property":       "#D4526E",
    "education":      "#9333EA",
    "alt_asset_mgmt": "#475569",
}

BADGE_STYLES: dict[str, tuple[str, str]] = {
    "consulting":     ("#EBF0F7", "#3A5A88"),
    "insurance":      ("#E6F5F3", "#1F7A6F"),
    "info_data":      ("#EEEDFE", "#4F46E5"),
    "it_services":    ("#E6F6FE", "#0284C7"),
    "wealth_mgmt":    ("#FBF5E0", "#A37D12"),
    "supply_chain":   ("#FDF0E6", "#C4622B"),
    "field_eng_tic":  ("#E8F3E7", "#2D6B29"),
    "property":       ("#FBEAEE", "#B33D5A"),
    "education":      ("#F3E8FD", "#7E22CE"),
    "alt_asset_mgmt": ("#ECEEF1", "#334155"),
}

PLOTLY_BG:   str = "#FFFFFF"
PLOTLY_GRID: str = "#F3F4F6"
PLOTLY_TEXT:  str = "#64748B"
