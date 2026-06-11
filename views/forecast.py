"""
views/forecast.py — Section 7: IMF Forecast 2025-2026.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from lib.theme import COUNTRY_COLORS, apply_plotly_theme
from lib.components import section_header, insight_box, source_badge, freshness_caption


def render(filters, data):
    fdf, source = data["forecast"]
    countries = filters["countries"]
    section_header("Macro Forecast", "IMF WEO — actuals through 2024 and forecast 2025-2026")

    if fdf.empty:
        st.warning("No forecast data available.")
        return

    df = fdf[fdf["Country"].isin(countries)].copy()
    metric = st.selectbox("Select metric", ["GDP_Growth_Pct", "Inflation_CPI_Pct", "Unemployment_Pct"],
                          format_func=lambda x: {"GDP_Growth_Pct": "GDP Growth (%)",
                                                  "Inflation_CPI_Pct": "Inflation CPI (%)",
                                                  "Unemployment_Pct": "Unemployment (%)"}[x],
                          key="forecast_metric")

    fig = go.Figure()
    for country in df["Country"].unique():
        cdf = df[df["Country"] == country].sort_values("Year")
        actual = cdf[cdf["Note"] == "Actual"]
        forecast = cdf[cdf["Note"] == "Forecast"]
        color = COUNTRY_COLORS.get(country, "#999999")
        fig.add_trace(go.Scatter(
            x=actual["Year"], y=actual[metric],
            mode="lines+markers", name=f"{country} Actual",
            line=dict(color=color, width=3), marker=dict(size=8)
        ))
        if not forecast.empty:
            # Connect last actual to first forecast for visual continuity
            conn = pd.concat([actual.tail(1), forecast.head(1)])
            fig.add_trace(go.Scatter(
                x=conn["Year"], y=conn[metric],
                mode="lines", line=dict(color=color, width=2, dash="dash"),
                showlegend=False, hoverinfo="skip"
            ))
            fig.add_trace(go.Scatter(
                x=forecast["Year"], y=forecast[metric],
                mode="lines+markers", name=f"{country} Forecast",
                line=dict(color=color, width=2, dash="dash"),
                marker=dict(size=8, symbol="diamond")
            ))

    title_map = {"GDP_Growth_Pct": "GDP Growth (%)", "Inflation_CPI_Pct": "Inflation CPI (%)", "Unemployment_Pct": "Unemployment (%)"}
    fig.update_layout(
        title=title_map.get(metric),
        xaxis_title="Year",
        yaxis_title=title_map.get(metric),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=50, r=30, t=60, b=80),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, sans-serif", color="#0A2540"),
    )
    st.plotly_chart(fig, use_container_width=True, key="forecast_chart")

    insight_box("Mexico is forecast to recover from 0.6% to 1.6% GDP growth by 2026, while Brazil is expected to slow from 2.3% to 1.9%. Inflation moderation and stable unemployment favor a medium-term manufacturing capex cycle in Mexico.")
    source_badge(source, "IMF WEO April 2025")
    freshness_caption(source, "2025")
