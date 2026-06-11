"""
lib/components.py — Reusable Streamlit components.
"""

import streamlit as st
from lib.theme import COUNTRY_COLORS, ACCENT, GOOD, BAD, NEUTRAL


def section_header(title: str, subtitle: str = ""):
    """Render a consistent section header with optional subtitle."""
    st.markdown(f"<h3 style='color:{ACCENT}; margin-bottom:4px;'>{title}</h3>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<p style='color:{NEUTRAL}; margin-top:0px; font-size:14px;'>{subtitle}</p>", unsafe_allow_html=True)
    st.divider()


def kpi_card(label: str, mexico_val, brazil_val, fmt: str = "{:.2f}", higher_is_better: bool = True):
    """
    Render a row of st.metric for Mexico vs Brazil.
    Highlights winner based on whether higher is better.
    """
    try:
        mv = float(mexico_val) if mexico_val is not None else None
        bv = float(brazil_val) if brazil_val is not None else None
    except (TypeError, ValueError):
        mv, bv = mexico_val, brazil_val

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.markdown(f"<p style='font-weight:600; color:{ACCENT};'>{label}</p>", unsafe_allow_html=True)
    with col2:
        st.metric(label="Mexico", value=fmt.format(mv) if mv is not None else "N/A")
    with col3:
        delta = None
        if mv is not None and bv is not None:
            delta = mv - bv
            # Determine if Mexico wins
            mx_wins = (delta > 0 and higher_is_better) or (delta < 0 and not higher_is_better)
            color = GOOD if mx_wins else BAD
            st.markdown(
                f"""
                <div style='padding:8px 0px;'>
                    <span style='font-size:12px; color:{NEUTRAL};'>Brazil</span><br>
                    <span style='font-size:20px; font-weight:500; color:{ACCENT};'>{fmt.format(bv) if bv is not None else "N/A"}</span><br>
                    <span style='font-size:12px; color:{color};'>Δ {fmt.format(delta)}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.metric(label="Brazil", value=fmt.format(bv) if bv is not None else "N/A")


def insight_box(markdown_text: str):
    """Render a colored analyst insight callout."""
    st.markdown(
        f"""
        <div style="background-color:#F0F7F4; border-left:4px solid {GOOD}; padding:12px 16px; margin:12px 0; border-radius:4px;">
            <span style="font-weight:600; color:{ACCENT};">💡 Insight:</span> {markdown_text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def source_badge(kind: str, label: str):
    """Render a source badge: LIVE / Curated / SNAPSHOT."""
    if kind == "LIVE":
        badge = f"<span style='color:{GOOD}; font-weight:600;'>🟢 LIVE</span> · {label}"
    elif kind == "SNAPSHOT":
        badge = f"<span style='color:#E6A23C; font-weight:600;'>🟡 SNAPSHOT</span> · {label}"
    else:
        badge = f"<span style='color:{NEUTRAL}; font-weight:600;'>📄 Curated</span> · {label}"
    st.markdown(f"<p style='font-size:12px; margin-top:8px;'>{badge}</p>", unsafe_allow_html=True)


def freshness_caption(source_flag: str, date_str: str):
    """Render a freshness caption below a chart/section."""
    if source_flag == "LIVE":
        st.caption(f"🟢 Обновлено из World Bank API · {date_str}")
    elif source_flag == "SNAPSHOT":
        st.caption(f"🟡 Резервный snapshot · {date_str}")
    else:
        st.caption(f"📄 Curated данные · {date_str}")


def country_filter_apply(df, countries):
    """Filter DataFrame by selected countries."""
    if "Country" not in df.columns:
        return df
    return df[df["Country"].isin(countries)].copy()
