"""
views/footprint.py — Section 9: Foxconn Footprint in Mexico.
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from lib.theme import apply_plotly_theme, COUNTRY_COLORS, ACCENT, GOOD
from lib.components import section_header, insight_box, source_badge


_SITES = [
    # Existing sites
    {
        "Site": "Tijuana",
        "State": "Baja California",
        "Lat": 32.5149,
        "Lon": -117.0382,
        "Status": "Existing",
        "Focus": "Electronics, PCs, components",
        "Employees": "5,000+",
        "Notes": "Long-standing border manufacturing campus near San Diego.",
    },
    {
        "Site": "Ciudad Juárez (San Jerónimo)",
        "State": "Chihuahua",
        "Lat": 31.6904,
        "Lon": -106.4245,
        "Status": "Existing",
        "Focus": "PCs, servers, AI servers, EV components",
        "Employees": "10,000+",
        "Notes": "Largest Foxconn campus in Mexico; $500M+ invested in Chihuahua.",
    },
    {
        "Site": "Guadalajara",
        "State": "Jalisco",
        "Lat": 20.6597,
        "Lon": -103.3496,
        "Status": "Existing",
        "Focus": "GB200 AI superchips (Nvidia)",
        "Employees": "2,000+",
        "Notes": "New high-value AI/semiconductor facility announced 2024.",
    },
    # Proposed sites
    {
        "Site": "Monterrey / Nuevo León",
        "State": "Nuevo León",
        "Lat": 25.6866,
        "Lon": -100.3161,
        "Status": "Proposed",
        "Focus": "Advanced manufacturing, EV supply chain",
        "Employees": "TBD",
        "Notes": "Proximity to Tesla Gigafactory Texas and USMCA logistics corridors.",
    },
    {
        "Site": "Querétaro",
        "State": "Querétaro",
        "Lat": 20.5888,
        "Lon": -100.3899,
        "Status": "Proposed",
        "Focus": "Aerospace & automotive electronics",
        "Employees": "TBD",
        "Notes": "Central Mexico talent hub with strong aerospace cluster.",
    },
]


def render(filters, data):
    section_header("Foxconn Footprint in Mexico", "3 existing sites + 2 proposed expansion locations")

    df = pd.DataFrame(_SITES)
    df["Color"] = df["Status"].map({
        "Existing": COUNTRY_COLORS["Mexico"],
        "Proposed": GOOD,
    })
    df["Symbol"] = df["Status"].map({
        "Existing": "factory",
        "Proposed": "diamond",
    })
    df["Size"] = df["Status"].map({
        "Existing": 18,
        "Proposed": 14,
    })

    fig = px.scatter_geo(
        df,
        lat="Lat",
        lon="Lon",
        text="Site",
        color="Status",
        color_discrete_map={"Existing": COUNTRY_COLORS["Mexico"], "Proposed": GOOD},
        symbol="Status",
        symbol_sequence=["circle", "diamond"],
        size="Size",
        size_max=18,
        hover_name="Site",
        hover_data={
            "State": True,
            "Focus": True,
            "Employees": True,
            "Notes": True,
            "Lat": False,
            "Lon": False,
            "Size": False,
        },
        title="Foxconn Sites & Expansion Targets in Mexico",
        scope="world",
    )

    fig.update_geos(
        center=dict(lat=24, lon=-102),
        projection_scale=6.5,
        showframe=False,
        showcoastlines=True,
        coastlinecolor="#CBD5E1",
        landcolor="#F4F6F8",
        oceancolor="#FFFFFF",
        lakecolor="#FFFFFF",
        showocean=True,
        visible=False,
        lonaxis_range=[-118, -86],
        lataxis_range=[14, 33],
    )

    fig.update_traces(
        textposition="top center",
        textfont=dict(size=11, color=ACCENT, family="Inter, sans-serif"),
        marker=dict(line=dict(width=1.5, color="white")),
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=60, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", color=ACCENT),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.12,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.9)",
        ),
    )

    fig = apply_plotly_theme(fig)
    fig.update_geos(
        center=dict(lat=24, lon=-102),
        projection_scale=6.5,
        lonaxis_range=[-118, -86],
        lataxis_range=[14, 33],
    )

    st.plotly_chart(fig, use_container_width=True, key="mexico_footprint_map")

    # Site details table
    st.markdown("#### Site Details")
    display_df = df[["Site", "State", "Status", "Focus", "Employees", "Notes"]].copy()
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    insight_box(
        "Foxconn's Mexico footprint is already concentrated along the US border and in Jalisco's high-tech corridor. "
        "The proposed Nuevo León and Querétaro sites would close gaps in EV/semiconductor supply chains and tap "
        "central Mexico's engineering talent — reinforcing Mexico as the priority expansion market."
    )
    source_badge("Curated", "Foxconn press releases, Milenio / El Economista 2024–2025")
