"""
views/foxconn.py — Section 6: Foxconn Investment.
"""
import streamlit as st
import plotly.express as px
from lib.theme import COUNTRY_COLORS, apply_plotly_theme
from lib.components import section_header, kpi_card, insight_box, source_badge


def render(filters, data):
    mfg = data["manufacturing_ev"]
    countries = filters["countries"]
    section_header("Foxconn Investment", "Labor cost, STEM pipeline, and existing footprint")

    df = mfg[mfg["Country"].isin(countries)].copy()
    if df.empty:
        st.warning("No data available.")
        return
    df["BubbleSize"] = df["Foxconn_Plants"] + 1

    mx = df[df["Country"] == "Mexico"]
    br = df[df["Country"] == "Brazil"]

    mx_labor = mx["Labor_Cost_Hourly_USD"].values[0] if not mx.empty else None
    br_labor = br["Labor_Cost_Hourly_USD"].values[0] if not br.empty else None
    mx_stem = mx["STEM_Graduates_Annual"].values[0] if not mx.empty else None
    br_stem = br["STEM_Graduates_Annual"].values[0] if not br.empty else None
    mx_plants = mx["Foxconn_Plants"].values[0] if not mx.empty else None
    br_plants = br["Foxconn_Plants"].values[0] if not br.empty else None

    kpi_card("Foxconn Plants", mx_plants, br_plants, "{:.0f}", higher_is_better=True)
    kpi_card("Labor Cost (USD/hr)", mx_labor, br_labor, "{:.2f}", higher_is_better=False)
    kpi_card("STEM Graduates / Year", mx_stem, br_stem, "{:,.0f}", higher_is_better=True)

    fig = px.scatter(df, x="Labor_Cost_Hourly_USD", y="STEM_Graduates_Annual",
                     size="BubbleSize", color="Country",
                     color_discrete_map=COUNTRY_COLORS,
                     hover_name="Country",
                     hover_data={"BubbleSize": False, "Foxconn_Plants": True},
                     size_max=60,
                     title="Foxconn Context: Labor Cost vs STEM Pipeline",
                     labels={"Labor_Cost_Hourly_USD": "Labor Cost (USD/hr)",
                             "STEM_Graduates_Annual": "STEM Graduates / Year"})
    apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True, key="foxconn_bubble")

    insight_box("Mexico offers 27% lower labor costs and 88% more STEM graduates annually, with 3 existing Foxconn facilities versus 0 in Brazil. This existing footprint accelerates time-to-production and de-risks supply-chain ramp-up.")
    source_badge("Curated", "Reuters, Dallas Fed, OEM data")
