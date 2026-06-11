"""
views/governance.py
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from lib.theme import COUNTRY_COLORS, apply_plotly_theme, GOOD, BAD
from lib.components import section_header, kpi_card, insight_box, source_badge, freshness_caption, country_filter_apply


def render_corruption(filters, data):
    cpi = data["cpi"]
    ef = data["economic_freedom"]
    countries = filters["countries"]
    year_range = filters["year_range"]

    section_header("Corruption and Economic Freedom", "CPI 2015-2024 and Heritage Index 2021-2024")

    cpi_f = country_filter_apply(cpi, countries)
    cpi_f = cpi_f[(cpi_f["Year"] >= year_range[0]) & (cpi_f["Year"] <= year_range[1])]

    col1, col2 = st.columns(2)
    with col1:
        fig = px.line(cpi_f, x="Year", y="CPI_Score", color="Country",
                      color_discrete_map=COUNTRY_COLORS, markers=True,
                      title="CPI Score (higher = less corrupt)")
        apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True, key="cpi_ts")

    with col2:
        fig = px.bar(cpi_f, x="Year", y="CPI_Rank", color="Country",
                     color_discrete_map=COUNTRY_COLORS, barmode="group",
                     title="CPI Rank (lower is better)")
        apply_plotly_theme(fig)
        fig.update_layout(yaxis_autorange="reversed")
        st.plotly_chart(fig, use_container_width=True, key="cpi_rank")

    ef_f = country_filter_apply(ef, countries)
    fig = px.bar(ef_f, x="Year", y="Economic_Freedom_Score", color="Country",
                 color_discrete_map=COUNTRY_COLORS, barmode="group",
                 title="Economic Freedom Score (Heritage)",
                 text="Economic_Freedom_Score")
    apply_plotly_theme(fig)
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True, key="ef_bar")

    insight_box("Brazil scores slightly higher on CPI (less perceived corruption), while Mexico leads on Economic Freedom, reflecting more open trade and investment regimes critical for manufacturing FDI.")
    source_badge("Curated", "Transparency International and Heritage Foundation")


def render_governance(filters, data):
    wgi = data["wgi"]
    cr = data["credit_ratings"]
    countries = filters["countries"]

    section_header("Governance and Credit", "WGI 2023 radar and sovereign credit ratings")

    wgi_f = country_filter_apply(wgi, countries)
    if not wgi_f.empty:
        WGI_LABELS = {
            "Voice_Accountability": "Voice & Accountability",
            "Political_Stability": "Political Stability",
            "Gov_Effectiveness": "Government Effectiveness",
            "Regulatory_Quality": "Regulatory Quality",
            "Rule_of_Law": "Rule of Law",
            "Control_of_Corruption": "Control of Corruption",
        }
        wgi_cols = [c for c in wgi_f.columns if c not in ["Country", "Year"]]
        fig = go.Figure()
        for country in wgi_f["Country"].unique():
            row = wgi_f[wgi_f["Country"] == country].iloc[0]
            fig.add_trace(go.Scatterpolar(
                r=[row[c] for c in wgi_cols],
                theta=[WGI_LABELS.get(c, c) for c in wgi_cols],
                fill="toself",
                name=country,
                line_color=COUNTRY_COLORS.get(country),
            ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 60])),
            title="World Governance Indicators 2023 (percentile)",
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(l=60, r=60, t=80, b=60),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Segoe UI, sans-serif", color="#0A2540"),
        )
        st.plotly_chart(fig, use_container_width=True, key="wgi_radar")

    cr_f = country_filter_apply(cr, countries)
    if not cr_f.empty:
        st.markdown("#### Sovereign Credit Ratings")
        def color_grade(val):
            color = GOOD if "Investment" in str(val) else BAD
            return f"background-color: {color}; color: white;"
        styled = cr_f.style.map(color_grade, subset=["Grade_Category"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

    insight_box("Mexico holds Investment Grade from all four agencies, while Brazil remains in speculative territory. This directly affects cost of capital and sovereign risk premiums for Foxconn capex.")
    source_badge("Curated", "World Bank WGI and S and P / Moodys / Fitch / DBRS")


def render(filters, data):
    render_corruption(filters, data)
    st.divider()
    render_governance(filters, data)
