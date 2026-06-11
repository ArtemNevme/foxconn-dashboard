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
    "margin": {"l": 45, "r": 25, "t": 50, "b": 65},
    "legend": {"orientation": "h", "yanchor": "bottom", "y": -0.18, "xanchor": "center", "x": 0.5, "bgcolor": "rgba(255,255,255,0.8)"},
    "hoverlabel": {
        "bgcolor": "#FFFFFF",
        "bordercolor": BORDER,
        "font": {"size": 13, "family": "Inter, sans-serif"},
    },
}


def apply_plotly_theme(fig):
    """Apply unified layout + styling defaults to any Plotly figure."""
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_xaxes(showgrid=True, gridcolor="#F0F0F0", linecolor="#E2E8F0", tickfont=dict(size=12, color=NEUTRAL))
    fig.update_yaxes(showgrid=True, gridcolor="#F0F0F0", linecolor="#E2E8F0", tickfont=dict(size=12, color=NEUTRAL))
    fig.update_traces(
        selector=dict(type="bar"),
        textposition="outside",
        textfont=dict(size=11, color=ACCENT),
    )
    fig.update_traces(
        selector=dict(type="scatter"),
        line=dict(width=3),
        marker=dict(size=8, line=dict(width=1, color="white")),
    )
    return fig


def get_country_color(country_name: str) -> str:
    return COUNTRY_COLORS.get(country_name, NEUTRAL)
