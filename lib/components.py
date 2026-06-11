"""
lib/components.py — Reusable Streamlit components.
"""

from datetime import date
import streamlit as st
from lib.theme import COUNTRY_COLORS, ACCENT, GOOD, BAD, NEUTRAL, CARD_BG, BORDER


def section_header(title: str, subtitle: str = ""):
    """Render a consistent section header with optional subtitle."""
    st.markdown(f"""
    <div style="margin-top: 20px; margin-bottom: 12px;">
        <h3 style="color:{ACCENT}; margin-bottom:4px; font-weight:700; letter-spacing:-0.5px; font-size:20px;">{title}</h3>
        <div style="width:50px; height:4px; background: linear-gradient(90deg, {COUNTRY_COLORS['Mexico']}, {COUNTRY_COLORS['Brazil']}); border-radius:2px; margin-bottom:6px;"></div>
        {f"<p style='color:{NEUTRAL}; margin-top:0px; font-size:13px; font-weight:400;'>{subtitle}</p>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)


def kpi_card(label: str, mexico_val, brazil_val, fmt: str = "{:.2f}", higher_is_better: bool = True):
    """
    Render a compact row of styled cards for Mexico vs Brazil.
    """
    try:
        mv = float(mexico_val) if mexico_val is not None else None
        bv = float(brazil_val) if brazil_val is not None else None
    except (TypeError, ValueError):
        mv, bv = mexico_val, brazil_val

    col1, col2, col3 = st.columns([1.1, 1, 1])

    mx_wins = None
    if mv is not None and bv is not None:
        delta = mv - bv
        mx_wins = (delta > 0 and higher_is_better) or (delta < 0 and not higher_is_better)

    def _card(value, country, accent_color, is_winner=None):
        val_str = fmt.format(value) if value is not None else "N/A"
        flag = "🇲🇽" if country == "Mexico" else "🇧🇷"
        win_color = GOOD if is_winner else (BAD if is_winner is False else NEUTRAL)
        win_icon = "▲" if is_winner else ("▼" if is_winner is False else "—")
        return f"""
        <div style="background: {CARD_BG}; border-radius: 10px; padding: 14px 16px;
                    box-shadow: 0 1px 2px rgba(10,37,64,0.06), 0 2px 8px rgba(10,37,64,0.04);
                    border-top: 3px solid {accent_color};">
            <div style="display:flex; align-items:center; gap:6px; margin-bottom:6px;">
                <span style="font-size:14px;">{flag}</span>
                <span style="font-size:10px; color:{NEUTRAL}; text-transform:uppercase; letter-spacing:0.8px; font-weight:700;">{country}</span>
            </div>
            <div style="font-size:24px; font-weight:800; color:{ACCENT}; line-height:1;">{val_str}</div>
            <div style="font-size:11px; color:{win_color}; margin-top:4px; font-weight:600;">{win_icon} {"Winner" if is_winner else ("Behind" if is_winner is False else "—")}</div>
        </div>
        """

    with col1:
        st.markdown(f"""
        <div style="background: {CARD_BG}; border-radius: 10px; padding: 14px 16px;
                    box-shadow: 0 1px 2px rgba(10,37,64,0.06);">
            <div style="font-size:10px; color:{NEUTRAL}; text-transform:uppercase; letter-spacing:0.8px; font-weight:700; margin-bottom:6px;">{label}</div>
            <div style="font-size:12px; color:{NEUTRAL}; line-height:1.4;">Comparison metric</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(_card(mv, "Mexico", COUNTRY_COLORS["Mexico"], mx_wins), unsafe_allow_html=True)

    with col3:
        st.markdown(_card(bv, "Brazil", COUNTRY_COLORS["Brazil"], not mx_wins if mx_wins is not None else None), unsafe_allow_html=True)


def insight_box(markdown_text: str):
    """Render a colored analyst insight callout."""
    st.markdown(
        f"""
        <div style="background: linear-gradient(90deg, #F0F7F4 0%, #FFFFFF 100%); border-left:4px solid {GOOD}; padding:14px 18px; margin:16px 0; border-radius:8px; box-shadow: 0 1px 2px rgba(10,37,64,0.04);">
            <span style="font-weight:700; color:{ACCENT}; font-size:13px;">💡 Insight</span>
            <p style="color:{ACCENT}; margin:4px 0 0 0; font-size:13px; line-height:1.5;">{markdown_text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def source_badge(kind: str, label: str):
    """Render a source badge: LIVE / Curated / SNAPSHOT."""
    if kind == "LIVE":
        badge = f"<span style='color:{GOOD}; font-weight:700;'>● LIVE</span> · {label}"
    elif kind == "SNAPSHOT":
        badge = f"<span style='color:#E6A23C; font-weight:700;'>● SNAPSHOT</span> · {label}"
    else:
        badge = f"<span style='color:{NEUTRAL}; font-weight:700;'>● Curated</span> · {label}"
    st.markdown(f"""
    <div style="display:inline-block; background-color:#F8FAFC; padding:4px 12px; border-radius:16px; font-size:11px; margin-top:8px; border:1px solid {BORDER};">
        {badge}
    </div>
    """, unsafe_allow_html=True)


def freshness_caption(source_flag: str, date_str: str | None = None):
    """Render a freshness caption below a chart/section."""
    today = date_str or date.today().isoformat()
    if source_flag == "LIVE":
        st.caption(f"Updated live from World Bank / IMF API · {today}")
    elif source_flag == "SNAPSHOT":
        st.caption(f"Local snapshot (API unavailable) · {today}")
    else:
        st.caption(f"Curated data · {today}")


def country_filter_apply(df, countries):
    """Filter DataFrame by selected countries."""
    if "Country" not in df.columns:
        return df
    return df[df["Country"].isin(countries)].copy()


def card_container():
    """Return a styled container wrapper for chart sections."""
    return st.container()
