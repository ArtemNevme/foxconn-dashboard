"""
app.py — Foxconn BI Dashboard: Mexico vs Brazil.
Entry point for Streamlit Community Cloud.
"""

import streamlit as st
from datetime import datetime

from lib.api_client import get_macro, get_forecast
from lib.data_loader import load_all_curated
from lib.theme import ACCENT, COUNTRY_COLORS
from lib.assets import LOGO_PNG, FLAG_MX_PNG, FLAG_BR_PNG

from views import overview, governance, manufacturing, ev_semi, foxconn, forecast, geomap, recommendation, sources

st.set_page_config(
    page_title="Foxconn BI Dashboard — Mexico vs Brazil",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_custom_css():
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"] {
            font-family: 'Inter', 'Segoe UI', sans-serif !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #F4F6F8;
            padding: 8px 12px;
            border-radius: 12px;
            margin-bottom: 12px;
        }
        .stTabs [data-baseweb="tab"] {
            font-weight: 600 !important;
            font-size: 13px !important;
            color: #64748B !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
            letter-spacing: 0.2px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #FFFFFF !important;
            color: #0A2540 !important;
            box-shadow: 0 1px 3px rgba(10,37,64,0.08) !important;
        }
        .css-1d391kg, .css-1lcbmhc, section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
        }
        section[data-testid="stSidebar"] .block-container {
            padding-top: 2rem !important;
        }
        .stSlider > div > div > div {
            background-color: #006847 !important;
        }
        .stSlider > div > div > div > div {
            background-color: #006847 !important;
        }
        .stMultiSelect [data-baseweb="tag"] {
            background-color: #F0F7F4 !important;
            color: #006847 !important;
            font-weight: 600 !important;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', sans-serif !important;
            letter-spacing: -0.5px !important;
        }
        .stMetric {
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 1px 3px rgba(10,37,64,0.06);
        }
        .stMetric label {
            font-size: 11px !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #757575 !important;
            font-weight: 600 !important;
        }
        .stMetric > div {
            font-weight: 700 !important;
            color: #0A2540 !important;
        }
        div[data-testid="stDataFrameResizable"] {
            border-radius: 8px !important;
            overflow: hidden !important;
            border: 1px solid #E2E8F0 !important;
        }
    </style>
    """, unsafe_allow_html=True)


def hero_banner():
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0A2540 0%, #0d3b5c 50%, #006847 100%);
                border-radius: 16px;
                padding: 32px 40px;
                margin-bottom: 24px;
                box-shadow: 0 10px 40px rgba(10,37,64,0.15);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:20px;">
            <div style="flex:1; min-width:280px;">
                <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
                    <img src="data:image/png;base64,{LOGO_PNG}" style="height:40px; background:#FFFFFF; padding:6px 12px; border-radius:8px;">
                    <span style="background-color:rgba(255,255,255,0.15); color:#FFFFFF; padding:4px 10px; border-radius:20px; font-size:11px; font-weight:600; letter-spacing:1px;">BI PROJECT</span>
                </div>
                <h1 style="color:#FFFFFF; margin:0; font-size:32px; font-weight:800; letter-spacing:-0.5px; line-height:1.2;">
                    Mexico <span style="color:#FEDD00;">vs</span> Brazil
                </h1>
                <p style="color:rgba(255,255,255,0.75); margin:8px 0 0 0; font-size:15px; font-weight:400;">
                    Advanced Manufacturing and Assembly · Expansion Analysis · Group 3 · June 2026
                </p>
            </div>
            <div style="display:flex; gap:16px; align-items:center;">
                <div style="text-align:center;">
                    <img src="data:image/png;base64,{FLAG_MX_PNG}" style="width:64px; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.2); margin-bottom:4px;">
                    <div style="color:#FFFFFF; font-size:12px; font-weight:600; letter-spacing:1px;">MEXICO</div>
                </div>
                <div style="color:rgba(255,255,255,0.3); font-size:24px; font-weight:300;">vs</div>
                <div style="text-align:center;">
                    <img src="data:image/png;base64,{FLAG_BR_PNG}" style="width:64px; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.2); margin-bottom:4px;">
                    <div style="color:#FFFFFF; font-size:12px; font-weight:600; letter-spacing:1px;">BRAZIL</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def main():
    inject_custom_css()
    hero_banner()

    # Sidebar filters
    st.sidebar.markdown(f"""
    <div style="padding-bottom:16px; border-bottom:1px solid #E2E8F0; margin-bottom:16px;">
        <h3 style="color:{ACCENT}; margin:0; font-size:18px; font-weight:700;">⚙️ Filters</h3>
        <p style="color:#757575; font-size:12px; margin:4px 0 0 0;">Customize your analysis view</p>
    </div>
    """, unsafe_allow_html=True)

    countries = st.sidebar.multiselect(
        "Countries",
        options=["Mexico", "Brazil"],
        default=["Mexico", "Brazil"],
    )
    year_range = st.sidebar.slider(
        "Year Range",
        min_value=2015,
        max_value=2024,
        value=(2015, 2024),
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("<p style='font-size:11px; color:#64748B; text-transform:uppercase; letter-spacing:1px; font-weight:600; margin-bottom:8px;'>Legend</p>", unsafe_allow_html=True)
    st.sidebar.markdown(
        f"<div style='display:flex; align-items:center; gap:8px; margin-bottom:6px;'>"
        f"<img src='data:image/png;base64,{FLAG_MX_PNG}' style='width:18px; border-radius:2px;'>"
        f"<span style='font-size:13px; color:{ACCENT}; font-weight:500;'>Mexico</span></div>"
        f"<div style='display:flex; align-items:center; gap:8px;'>"
        f"<img src='data:image/png;base64,{FLAG_BR_PNG}' style='width:18px; border-radius:2px;'>"
        f"<span style='font-size:13px; color:{ACCENT}; font-weight:500;'>Brazil</span></div>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="background-color:#F0F7F4; border-radius:8px; padding:12px; margin-top:8px;">
        <p style="font-size:11px; color:#64748B; margin:0; line-height:1.4;">
            📡 Data refreshes daily from World Bank and IMF APIs.<br>
            Fallback to local snapshots if offline.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not countries:
        st.warning("Please select at least one country.")
        return

    filters = {"countries": countries, "year_range": year_range}

    # Load data
    with st.spinner("Loading data..."):
        macro_df, macro_source = get_macro()
        forecast_df, forecast_source = get_forecast()
        curated = load_all_curated()

    data = {
        "macro": (macro_df, macro_source),
        "forecast": (forecast_df, forecast_source),
        "cpi": curated["cpi"],
        "economic_freedom": curated["economic_freedom"],
        "wgi": curated["wgi"],
        "credit_ratings": curated["credit_ratings"],
        "manufacturing_ev": curated["manufacturing_ev"],
        "comparison": curated["comparison"],
        "sources": curated["sources"],
    }

    # Tabs
    tabs = st.tabs([
        "1. Macro Overview",
        "2. Corruption and Freedom",
        "3. Governance and Credit",
        "4. Manufacturing",
        "5. EV and Semiconductor",
        "6. Foxconn Investment",
        "7. Forecast",
        "8. Geo Map",
        "9. Recommendation",
        "10. Sources",
    ])

    with tabs[0]:
        overview.render(filters, data)
    with tabs[1]:
        governance.render_corruption(filters, data)
    with tabs[2]:
        governance.render_governance(filters, data)
    with tabs[3]:
        manufacturing.render(filters, data)
    with tabs[4]:
        ev_semi.render(filters, data)
    with tabs[5]:
        foxconn.render(filters, data)
    with tabs[6]:
        forecast.render(filters, data)
    with tabs[7]:
        geomap.render(filters, data)
    with tabs[8]:
        recommendation.render(filters, data)
    with tabs[9]:
        sources.render(filters, data)

    # Footer
    st.divider()
    st.caption(f"Foxconn BI Dashboard · Built with Streamlit · {datetime.now().year}")


if __name__ == "__main__":
    main()