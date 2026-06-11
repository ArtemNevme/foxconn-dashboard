"""
views/recommendation.py — Section 9: Recommendation and Composite Score.
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from lib.theme import COUNTRY_COLORS, apply_plotly_theme, GOOD, BAD, ACCENT
from lib.components import section_header, insight_box, source_badge
from lib.composite import compute_composite


def render(filters, data):
    comp = data["comparison"]
    mfg = data["manufacturing_ev"]
    countries = filters["countries"]
    section_header("Recommendation", "Composite score and decision matrix")

    # Composite
    result = compute_composite()
    mx_score = result["mexico_score"]
    br_score = result["brazil_score"]
    breakdown = result["breakdown_df"]
    weights = result["weights_df"]

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Mexico Composite", f"{mx_score:.1f}")
        st.progress(min(mx_score / 100, 1.0))
    with c2:
        st.metric("Brazil Composite", f"{br_score:.1f}")
        st.progress(min(br_score / 100, 1.0))

    score_df = pd.DataFrame({
        "Country": ["Mexico", "Brazil"],
        "Score": [mx_score, br_score]
    })
    fig = px.bar(score_df, x="Country", y="Score", color="Country",
                 color_discrete_map=COUNTRY_COLORS,
                 title="Composite Index Score (0-100)", text="Score",
                 hover_data={"Score": ":.1f"})
    apply_plotly_theme(fig)
    fig.update_layout(showlegend=False)
    fig.update_traces(hovertemplate="<b>%{x}</b><br>Composite Score: %{y:.1f}/100<extra></extra>")
    st.plotly_chart(fig, use_container_width=True, key="composite_bar")

    with st.expander("Show methodology and weights"):
        st.markdown("**Weights (Advanced Manufacturing focus)**")
        st.dataframe(weights, use_container_width=True, hide_index=True)
        st.markdown("**Breakdown**")
        st.dataframe(breakdown, use_container_width=True, hide_index=True)

    # Decision matrix from Comparison.csv
    st.markdown("### Decision Matrix")
    df = comp.copy()
    # Highlight winner per row
    def highlight_winner(row):
        styles = [""] * len(row)
        try:
            mx = float(row["Mexico"])
            br = float(row["Brazil"])
            # For most metrics in Comparison, higher is better except a few
            lower_better = ["Inflation (2024)", "Unemployment (2024)", "Labor Cost/hr"]
            metric_name = row["Metric"]
            mx_wins = (mx > br) if metric_name not in lower_better else (mx < br)
            styles[1] = f"background-color: {GOOD}; color: white;" if mx_wins else ""
            styles[2] = f"background-color: {GOOD}; color: white;" if not mx_wins else ""
        except Exception:
            pass
        return styles

    styled = df.style.apply(highlight_winner, axis=1)
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #F0F7F4 0%, #FFFFFF 100%); border-left:4px solid {GOOD}; padding:20px; border-radius:12px; box-shadow: 0 2px 8px rgba(27,158,119,0.08);">
        <h4 style="color:{ACCENT}; margin-top:0;">RECOMMENDED: Mexico</h4>
        <ul style="margin-bottom:8px;">
            <li><strong>Manufacturing intensity:</strong> ~20% of GDP vs ~12% in Brazil</li>
            <li><strong>Labor economics:</strong> 27% lower hourly cost with larger STEM pipeline</li>
            <li><strong>Existing footprint:</strong> 3 Foxconn plants operational vs 0</li>
            <li><strong>Credit quality:</strong> Investment Grade across all four agencies</li>
            <li><strong>Trade integration:</strong> USMCA and deep Tier-1 supplier ecosystem (600 vs 200)</li>
        </ul>
        <p style="margin-bottom:4px;"><strong>Primary Risk:</strong> US trade-policy volatility and potential USMCA rule-of-origin changes.</p>
        <p style="margin-bottom:0;"><strong>Mitigation:</strong> Geographic diversification across Chihuahua, Guadalajara and Guanajuato; active USMCA working-group engagement; tariff-scenario supply buffers.</p>
    </div>
    """, unsafe_allow_html=True)

    insight_box("The composite index normalizes mixed scales (CPI, GDP growth, EV growth, credit ratings) into a single comparable score. Transparency on weights and reference ranges is essential for academic and client Q and A defense.")
    source_badge("Curated", "Composite methodology + Comparison dataset")
