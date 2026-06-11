"""
lib/theme.py — Design system for Foxconn BI Dashboard.
"""

COUNTRY_COLORS = {
    "Mexico": "#006847",
    "Brazil": "#FEDD00",
}

ACCENT = "#0A2540"
GOOD = "#1B9E77"
BAD = "#D62728"
NEUTRAL = "#757575"
LIGHT_BG = "#F4F6F8"
CARD_BG = "#FFFFFF"
BORDER = "#E2E8F0"

PLOTLY_LAYOUT = {
    "font": {"family": "Inter, Segoe UI, Roboto, Helvetica, Arial, sans-serif", "color": ACCENT, "size": 13},
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "margin": {"l": 50, "r": 30, "t": 60, "b": 50},
    "legend": {"orientation": "h", "yanchor": "bottom", "y": -0.22, "xanchor": "center", "x": 0.5},
    "hoverlabel": {"bgcolor": "#FFFFFF", "bordercolor": ACCENT, "font_size": 12, "font_family": "sans-serif"},
    "xaxis": {"showgrid": True, "gridcolor": "#EAEAEA", "linecolor": "#CCCCCC", "tickfont": {"size": 12}},
    "yaxis": {"showgrid": True, "gridcolor": "#EAEAEA", "linecolor": "#CCCCCC", "tickfont": {"size": 12}},
}


def apply_plotly_theme(fig):
    """Apply unified layout to any Plotly figure."""
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def get_country_color(country_name: str) -> str:
    return COUNTRY_COLORS.get(country_name, NEUTRAL)
