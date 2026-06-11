"""
views/ev_semi.py — Section 5: EV and Semiconductor.
"""
import streamlit as st
import plotly.express as px
from lib.theme import COUNTRY_COLORS, apply_plotly_theme
from lib.components import section_header, insight_box, source_badge


def render(filters, data):
    mfg = data["manufacturing_ev"]
    countries = filters["countries"]
    section_header("EV Production and Export Base", "EV metrics and semiconductor electronics ecosystem")

    df = mfg[mfg["Country"].isin(countries)].copy()
    if df.empty:
        st.warning("No data available.")
        return

    c1, c2 = st.columns(2)
    ev_metrics = [
        ("EV_Production", "EV Production (units)"),
        ("EV_Growth_Rate_Pct", "EV Growth Rate (%)"),
        ("EV_Sales", "EV Sales (units)"),
        ("Charging_Stations", "Charging Stations"),
    ]
    for i, (col, title) in enumerate(ev_metrics):
        with (c1 if i % 2 == 0 else c2):
            fig = px.bar(df, x="Country", y=col, color="Country",
                         color_discrete_map=COUNTRY_COLORS,
                         title=title, text=col)
            apply_plotly_theme(fig)
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True, key=f"ev_{i}")

    # 100% stacked for EV market share
    fig = px.bar(df, x="Country", y="EV_Market_Share_Pct", color="Country",
                 color_discrete_map=COUNTRY_COLORS,
                 title="EV Market Share (% of total auto sales)", text="EV_Market_Share_Pct")
    apply_plotly_theme(fig)
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True, key="ev_share")

    st.markdown("---")
    c3, c4 = st.columns(2)
    with c3:
        fig = px.bar(df, x="Country", y="Semiconductor_Exports_Billions", color="Country",
                     color_discrete_map=COUNTRY_COLORS,
                     title="Semiconductor Exports (USD Bn)", text="Semiconductor_Exports_Billions")
        apply_plotly_theme(fig)
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True, key="semi_exp")

    with c4:
        fig = px.bar(df, x="Country", y="Electronics_Mfg_Billions", color="Country",
                     color_discrete_map=COUNTRY_COLORS,
                     title="Electronics Manufacturing (USD Bn)", text="Electronics_Mfg_Billions")
        apply_plotly_theme(fig)
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True, key="elec_mfg")

    insight_box("Brazil leads in absolute EV sales and charging infrastructure, but Mexico is building a larger EV production and export base (220k vs 50k units) with a far deeper semiconductor and electronics manufacturing ecosystem (USD 107 Bn vs 15 Bn).")
    source_badge("Curated", "IEA, OECD, Dallas Fed")
