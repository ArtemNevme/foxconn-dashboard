"""
views/overview.py — Section 1: Macro Overview.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from lib.theme import COUNTRY_COLORS, apply_plotly_theme, GOOD, BAD, ACCENT
from lib.components import section_header, kpi_card, insight_box, source_badge, freshness_caption, country_filter_apply


def render(filters, data):
    macro_df, macro_source = data["macro"]
    countries = filters["countries"]
    year_range = filters["year_range"]

    section_header("Macro Overview", "GDP, inflation, unemployment, trade & manufacturing — 2015-2024")

    if macro_df.empty:
        st.warning("No macro data available.")
        return

    df = country_filter_apply(macro_df, countries)
    df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]

    # Latest year for KPIs
    latest_year = int(df["Year"].max())
    latest_per_country = df.sort_values("Year").groupby("Country").last().reset_index()
    mx_latest = latest_per_country[latest_per_country["Country"] == "Mexico"]
    br_latest = latest_per_country[latest_per_country["Country"] == "Brazil"]

    mx_gdp = mx_latest["GDP_Growth_Pct"].values[0] if not mx_latest.empty else None
    br_gdp = br_latest["GDP_Growth_Pct"].values[0] if not br_latest.empty else None
    mx_inf = mx_latest["Inflation_CPI_Pct"].values[0] if not mx_latest.empty else None
    br_inf = br_latest["Inflation_CPI_Pct"].values[0] if not br_latest.empty else None
    mx_unemp = mx_latest["Unemployment_Pct"].values[0] if not mx_latest.empty else None
    br_unemp = br_latest["Unemployment_Pct"].values[0] if not br_latest.empty else None
    mx_mfg = mx_latest["Manufacturing_Pct_GDP"].values[0] if not mx_latest.empty else None
    br_mfg = br_latest["Manufacturing_Pct_GDP"].values[0] if not br_latest.empty else None

    kpi_card(f"GDP Growth {latest_year} (%)", mx_gdp, br_gdp, "{:.2f}", higher_is_better=True)
    kpi_card(f"Inflation CPI {latest_year} (%)", mx_inf, br_inf, "{:.2f}", higher_is_better=False)
    kpi_card(f"Unemployment {latest_year} (%)", mx_unemp, br_unemp, "{:.2f}", higher_is_better=False)
    kpi_card("Manufacturing % GDP", mx_mfg, br_mfg, "{:.2f}", higher_is_better=True)

    st.markdown("---")

    # Time series
    col1, col2 = st.columns(2)
    metrics_ts = [
        ("GDP_Growth_Pct", "GDP Growth (%)", col1),
        ("Inflation_CPI_Pct", "Inflation CPI (%)", col2),
        ("Unemployment_Pct", "Unemployment (%)", col1),
    ]
    for i, (col, title, container) in enumerate(metrics_ts):
        with container:
            fig = px.line(df, x="Year", y=col, color="Country", color_discrete_map=COUNTRY_COLORS,
                          markers=True, title=title,
                          hover_data={col: ":.2f"})
            apply_plotly_theme(fig)
            fig.update_layout(legend_title_text="", hovermode="x unified")
            fig.update_traces(hovertemplate="<b>%{fullData.name}</b><br>Year: %{x}<br>Value: %{y:.2f}<extra></extra>")
            st.plotly_chart(fig, use_container_width=True, key=f"macro_ts_{i}")

    # Risk vs Return scatter
    with col2:
        agg = df.groupby("Country").agg({
            "Inflation_CPI_Pct": "mean",
            "GDP_Growth_Pct": "mean",
        }).reset_index()
        fig = px.scatter(agg, x="Inflation_CPI_Pct", y="GDP_Growth_Pct", color="Country",
                         color_discrete_map=COUNTRY_COLORS,
                         title="Risk vs Return (avg 2015–2024)",
                         labels={"Inflation_CPI_Pct": "Avg Inflation (risk)", "GDP_Growth_Pct": "Avg GDP Growth (return)"},
                         size=[40] * len(agg),
                         hover_data={"Inflation_CPI_Pct": ":.2f", "GDP_Growth_Pct": ":.2f"})
        apply_plotly_theme(fig)
        fig.update_traces(marker=dict(opacity=0.9, line=dict(width=2, color="white")),
                          hovertemplate="<b>%{fullData.name}</b><br>Avg Inflation: %{x:.2f}%<br>Avg GDP Growth: %{y:.2f}%<extra></extra>")
        st.plotly_chart(fig, use_container_width=True, key="macro_scatter")

    st.markdown("---")

    # GDP Current USD & Manufacturing % side by side
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(df, x="Year", y="GDP_Current_USD", color="Country",
                     color_discrete_map=COUNTRY_COLORS, barmode="group",
                     title="GDP Current USD (Billions)", labels={"GDP_Current_USD": "USD Bn"},
                     hover_data={"GDP_Current_USD": ":.1f"})
        apply_plotly_theme(fig)
        fig.update_traces(hovertemplate="<b>%{fullData.name}</b><br>Year: %{x}<br>GDP: $%{y:.1f} Bn<extra></extra>")
        st.plotly_chart(fig, use_container_width=True, key="macro_gdp_usd")

    with c2:
        fig = px.bar(df, x="Year", y="Manufacturing_Pct_GDP", color="Country",
                     color_discrete_map=COUNTRY_COLORS, barmode="group",
                     title="Manufacturing % of GDP",
                     labels={"Manufacturing_Pct_GDP": "% of GDP"},
                     hover_data={"Manufacturing_Pct_GDP": ":.1f"})
        apply_plotly_theme(fig)
        fig.update_traces(hovertemplate="<b>%{fullData.name}</b><br>Year: %{x}<br>Manufacturing: %{y:.1f}%<extra></extra>")
        st.plotly_chart(fig, use_container_width=True, key="macro_mfg_pct")

    insight_box(
        "Mexico shows lower unemployment and a larger manufacturing share of GDP (~20% vs ~12%), "
        "while Brazil has a bigger absolute economy but higher volatility and inflation. "
        "For Advanced Manufacturing & Assembly, Mexico's industrial base offers stronger nearshoring fundamentals."
    )
    source_badge(macro_source, "World Bank WDI")
    freshness_caption(macro_source)
