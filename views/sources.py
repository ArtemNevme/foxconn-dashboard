"""views/sources.py — Section 10: Sources & Methodology."""
import streamlit as st
from lib.components import section_header, insight_box


def render(filters, data):
    sources = data["sources"]
    section_header("Sources & Methodology", "Data provenance and citations (APA)")

    st.markdown("**Live data:** World Bank (WDI) and IMF (DataMapper) APIs — fetched on load, "
                "cached daily, with automatic fallback to local snapshots if the APIs are unavailable.")
    st.markdown("**Curated data:** indices without a public API (CPI, Economic Freedom, credit "
                "ratings, automotive/EV/semiconductor figures) compiled manually from the sources below.")

    st.dataframe(
        sources,
        use_container_width=True,
        hide_index=True,
        column_config={"URL": st.column_config.LinkColumn("URL")},
    )

    insight_box("All quantitative claims trace to the cited sources. Composite index uses transparent "
                "weights and reference ranges (see the Recommendation tab).")
