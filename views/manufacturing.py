"""
views/manufacturing.py — Section 4: Manufacturing and Automotive.
"""
import streamlit as st
import plotly.express as px
from lib.theme import COUNTRY_COLORS, apply_plotly_theme
from lib.components import section_header, insight_box, source_badge


def render(filters, data):
    mfg = data["manufacturing_ev"]
    countries = filters["countries"]
    section_header("Manufacturing and Automotive", "Auto production, OEM plants, supply chain depth")

    df = mfg[mfg["Country"].isin(countries)].copy()
    if df.empty:
        st.warning("No data available.")
        return

    metrics = [
        ("Auto_Production", "Auto Production (units)"),
        ("OEM_Plants", "OEM Plants (count)"),
        ("Tier1_Suppliers", "Tier-1 Suppliers"),
        ("Auto_Employment", "Auto Employment"),
        ("Auto_Exports_USD_Billions", "Auto Exports (USD Bn)"),
        ("Capacity_Utilization_Pct", "Capacity Utilization (%)"),
    ]

    cols = st.columns(2)
    for i, (col, title) in enumerate(metrics):
        with cols[i % 2]:
            fig = px.bar(df, x="Country", y=col, color="Country",
                         color_discrete_map=COUNTRY_COLORS,
                         title=title, text=col,
                         hover_data={col: ":.1f"})
            apply_plotly_theme(fig)
            fig.update_layout(showlegend=False)
            fig.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y:,.1f}<extra></extra>")
            st.plotly_chart(fig, use_container_width=True, key=f"mfg_{i}")

    insight_box("Mexico dominates auto production volume, export value, and supply-chain density (600 Tier-1 suppliers vs 200), with nearshoring driving 97% capacity utilization.")
    source_badge("Curated", "OICA, Trade.gov, ANFAVEA")
