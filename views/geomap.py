"""
views/geomap.py — Section 8: Geo Map (choropleth).
"""
import streamlit as st
import plotly.express as px
from lib.theme import apply_plotly_theme
from lib.components import section_header, insight_box, source_badge
from lib.composite import compute_composite


def render(filters, data):
    macro_df, macro_source = data["macro"]
    countries = filters["countries"]
    section_header("Geographic Context", "Latin America — Mexico and Brazil highlighted")

    if macro_df.empty:
        st.warning("No macro data available for map.")
        return

    # Build latest-year country-level dataset for map
    latest_year = macro_df["Year"].max()
    latest = macro_df[macro_df["Year"] == latest_year].copy()
    latest["ISO"] = latest["Country"].map({"Mexico": "MEX", "Brazil": "BRA"})

    # Inject composite score
    comp = compute_composite()
    score_map = {"Mexico": comp["mexico_score"], "Brazil": comp["brazil_score"]}
    latest["Composite_Score"] = latest["Country"].map(score_map)

    metric = st.selectbox("Color metric", ["Composite_Score", "GDP_Growth_Pct", "Manufacturing_Pct_GDP", "GDP_Current_USD"],
                          format_func=lambda x: {"Composite_Score": "Composite Investment Score",
                                                  "GDP_Growth_Pct": "GDP Growth (%)",
                                                  "Manufacturing_Pct_GDP": "Manufacturing % GDP",
                                                  "GDP_Current_USD": "GDP Current USD (Bn)"}[x],
                          key="map_metric")

    # Full world choropleth with focus on Americas
    hover_map = {
        "Composite_Score": ["Country", "Composite_Score"],
        "GDP_Growth_Pct": ["Country", "GDP_Growth_Pct"],
        "Manufacturing_Pct_GDP": ["Country", "Manufacturing_Pct_GDP"],
        "GDP_Current_USD": ["Country", "GDP_Current_USD"],
    }
    fig = px.choropleth(
        latest,
        locations="ISO",
        color=metric,
        hover_name="Country",
        hover_data=hover_map.get(metric, ["Country"]),
        color_continuous_scale="RdYlGn",
        range_color=(latest[metric].min() * 0.9, latest[metric].max() * 1.05),
        labels={metric: metric.replace("_", " ")},
        title=f"{metric.replace('_', ' ').replace('Composite Score', 'Composite Investment Score')} ({latest_year})",
    )
    fig.update_geos(
        scope="world",
        center=dict(lat=10, lon=-60),
        projection_scale=2.5,
        showframe=False,
        showcoastlines=True,
        coastlinecolor="#CCCCCC",
        landcolor="#F4F6F8",
        oceancolor="#FFFFFF",
        lakecolor="#FFFFFF",
        showocean=True,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=60, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, sans-serif", color="#0A2540"),
        coloraxis_colorbar=dict(title="", thickness=15, len=0.6),
    )
    st.plotly_chart(fig, use_container_width=True, key="geo_map")

    insight_box("The map visualizes structural divergence: Mexico punches above its weight on manufacturing share, while Brazil dominates absolute GDP scale. For Foxconn Advanced Manufacturing, manufacturing intensity matters more than total market size.")
    source_badge(macro_source, "World Bank WDI")
