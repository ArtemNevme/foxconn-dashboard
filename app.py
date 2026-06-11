"""
app.py — Foxconn BI Dashboard: Mexico vs Brazil.
Entry point for Streamlit Community Cloud.
"""

import streamlit as st
from datetime import datetime

from lib.api_client import get_macro, get_forecast
from lib.data_loader import load_all_curated
from lib.theme import ACCENT, COUNTRY_COLORS

from views import overview, governance, manufacturing, ev_semi, foxconn, forecast, geomap, recommendation

st.set_page_config(
    page_title="Foxconn BI Dashboard — Mexico vs Brazil",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    # Header
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:12px;">
        <h1 style="color:{ACCENT}; margin-bottom:4px;">🏭 Foxconn BI Dashboard</h1>
        <p style="color:#757575; font-size:15px; margin-top:0px;">
            Advanced Manufacturing and Assembly · Mexico vs Brazil · Group 3 · June 2026
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar filters
    st.sidebar.header("Filters")
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
    st.sidebar.markdown("**Colors**")
    st.sidebar.markdown(
        f"<span style='color:{COUNTRY_COLORS['Mexico']}'>■ Mexico</span> &nbsp; "
        f"<span style='color:{COUNTRY_COLORS['Brazil']}'>■ Brazil</span>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")
    st.sidebar.caption("Data refreshes daily from World Bank and IMF APIs. Falls back to local snapshots if offline.")

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

    # Footer
    st.divider()
    st.caption(f"Foxconn BI Dashboard · Built with Streamlit · {datetime.now().year}")


if __name__ == "__main__":
    main()
