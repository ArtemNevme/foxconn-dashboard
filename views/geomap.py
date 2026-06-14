"""
views/geomap.py — Section 8: Regional LATAM Heat Map.
"""
import streamlit as st
import plotly.express as px
from lib.theme import apply_plotly_theme, COUNTRY_COLORS, ACCENT
from lib.components import section_header, insight_box, source_badge


_METRIC_LABELS = {
    "GDP_Growth_Pct": "GDP Growth (%)",
    "Manufacturing_Pct_GDP": "Manufacturing % of GDP",
}


def render(filters, data):
    latam_df, latam_source = data["latam"]
    section_header("Regional LATAM Heat Map", "18 economies · World Bank WDI · latest available year")

    if latam_df.empty:
        st.warning("No regional data available for map.")
        return

    df = latam_df.copy()

    # Highlight Mexico and Brazil with accent colors; others neutral.
    df["Color"] = df["Country"].apply(
        lambda c: COUNTRY_COLORS.get(c, "#CBD5E1")
    )
    df["Outline"] = df["Country"].apply(
        lambda c: ACCENT if c in ("Mexico", "Brazil") else "#FFFFFF"
    )

    metric = st.selectbox(
        "Color metric",
        options=["GDP_Growth_Pct", "Manufacturing_Pct_GDP"],
        format_func=lambda x: _METRIC_LABELS[x],
        key="latam_map_metric",
    )

    # Heat map: color = metric, opacity differentiates selected vs rest
    fig = px.choropleth(
        df,
        locations="ISO",
        color=metric,
        hover_name="Country",
        hover_data={
            "ISO": False,
            metric: ":.2f",
        },
        color_continuous_scale=["#FEF3C7", "#F59E0B", "#B45309"],
        range_color=(df[metric].min() * 0.95, df[metric].max() * 1.05),
        labels={metric: _METRIC_LABELS[metric]},
        title=f"{_METRIC_LABELS[metric]} · Latin America & Caribbean",
        scope="world",
    )

    fig.update_geos(
        center=dict(lat=5, lon=-70),
        projection_scale=3.2,
        showframe=False,
        showcoastlines=True,
        coastlinecolor="#CBD5E1",
        landcolor="#F4F6F8",
        oceancolor="#FFFFFF",
        lakecolor="#FFFFFF",
        showocean=True,
        visible=False,
        lonaxis_range=[-120, -30],
        lataxis_range=[-35, 35],
    )

    fig.update_traces(
        marker_line_color=df["Outline"],
        marker_line_width=df["Country"].apply(lambda c: 2 if c in ("Mexico", "Brazil") else 0.5),
        selector=dict(type="choropleth"),
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=60, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", color=ACCENT),
        coloraxis_colorbar=dict(title="", thickness=15, len=0.6),
    )

    fig = apply_plotly_theme(fig)
    # Reset geo-specific defaults that apply_plotly_theme may override
    fig.update_geos(
        center=dict(lat=5, lon=-70),
        projection_scale=3.2,
        lonaxis_range=[-120, -30],
        lataxis_range=[-35, 35],
    )

    st.plotly_chart(fig, use_container_width=True, key="latam_heatmap")

    # Highlight cards for Mexico / Brazil
    mx = df[df["Country"] == "Mexico"]
    br = df[df["Country"] == "Brazil"]
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"""
            <div style="border-left:4px solid {COUNTRY_COLORS['Mexico']}; padding:12px 16px; background:#FFFFFF; border-radius:8px; box-shadow:0 1px 2px rgba(10,37,64,0.06);">
                <div style="font-size:12px; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.8px;">🇲🇽 Mexico</div>
                <div style="font-size:20px; font-weight:800; color:{ACCENT};">{metric.replace('_', ' ')}</div>
                <div style="font-size:24px; font-weight:800; color:{COUNTRY_COLORS['Mexico']};">{mx[metric].values[0]:.2f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div style="border-left:4px solid {COUNTRY_COLORS['Brazil']}; padding:12px 16px; background:#FFFFFF; border-radius:8px; box-shadow:0 1px 2px rgba(10,37,64,0.06);">
                <div style="font-size:12px; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.8px;">🇧🇷 Brazil</div>
                <div style="font-size:20px; font-weight:800; color:{ACCENT};">{metric.replace('_', ' ')}</div>
                <div style="font-size:24px; font-weight:800; color:{COUNTRY_COLORS['Brazil']};">{br[metric].values[0]:.2f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    insight_box(
        "Mexico and Brazil stand out in very different ways: Mexico leads the region in manufacturing intensity "
        "(% of GDP), confirming its role as an export-oriented advanced-manufacturing hub, while Brazil offers "
        "a larger domestic economy but lower manufacturing concentration. For Foxconn, Mexico's density is the "
        "stronger strategic fit."
    )
    source_badge(latam_source, "World Bank WDI")
