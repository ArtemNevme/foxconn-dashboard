"""
lib/components.py — Reusable Streamlit components.
"""

from datetime import date
import streamlit as st
from lib.theme import COUNTRY_COLORS, ACCENT, GOOD, BAD, NEUTRAL, CARD_BG, BORDER


def section_header(title: str, subtitle: str = ""):
    """Render a consistent section header with optional subtitle."""
    st.markdown(f"""
    <div style="margin-top: 24px; margin-bottom: 16px;">
        <h3 style="color:{ACCENT}; margin-bottom:4px; font-weight:700; letter-spacing:-0.5px;">{title}</h3>
        <div style="width:60px; height:4px; background: linear-gradient(90deg, {COUNTRY_COLORS['Mexico']}, {COUNTRY_COLORS['Brazil']}); border-radius:2px; margin-bottom:8px;"></div>
        {f"<p style='color:{NEUTRAL}; margin-top:0px; font-size:14px; font-weight:400;'>{subtitle}</p>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)


def kpi_card(label: str, mexico_val, brazil_val, fmt: str = "{:.2f}", higher_is_better: bool = True):
    """
    Render a row of styled cards for Mexico vs Brazil.
    Highlights winner based on whether higher is better.
    """
    try:
        mv = float(mexico_val) if mexico_val is not None else None
        bv = float(brazil_val) if brazil_val is not None else None
    except (TypeError, ValueError):
        mv, bv = mexico_val, brazil_val

    col1, col2, col3 = st.columns([1, 1, 1])

    def card_html(value, country, accent_color, is_winner=None):
        val_str = fmt.format(value) if value is not None else "N/A"
        flag = "🇲🇽" if country == "Mexico" else "🇧🇷"
        winner_badge = ""
        if is_winner is True:
            winner_badge = f"<p style='font-size:13px; color:{GOOD}; margin-top:6px; font-weight:600;'>✓ Winner</p>"
        elif is_winner is False:
            winner_badge = f"<p style='font-size:13px; color:{BAD}; margin-top:6px; font-weight:600;'>—</p>"
        return f"""
        <div style="background-color: {CARD_BG}; border-radius: 12px; padding: 16px 20px;
                    box-shadow: 0 1px 3px rgba(10,37,64,0.08), 0 4px 12px rgba(10,37,64,0.05);
                    border-top: 4px solid {accent_color}; height: 100%;">
            <p style="font-size:11px; color:{NEUTRAL}; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; font-weight:600;">
                {flag} {country}
            </p>
            <p style="font-size:28px; font-weight:700; color:{ACCENT}; margin:0; line-height:1.1;">{val_str}</p>
            {winner_badge}
        </div>
        """

    mx_wins = None
    if mv is not None and bv is not None:
        delta = mv - bv
        mx_wins = (delta > 0 and higher_is_better) or (delta < 0 and not higher_is_better)

    with col1:
        st.markdown(f"""
        <div style="background-color: {CARD_BG}; border-radius: 12px; padding: 16px 20px;
                    box-shadow: 0 1px 3px rgba(10,37,64,0.08), 0 4px 12px rgba(10,37,64,0.05);
                    border-top: 4px solid {ACCENT}; height: 100%;">
            <p style="font-size:11px; color:{NEUTRAL}; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; font-weight:600;">
                {label}
            </p>
            <p style="font-size:14px; color:{NEUTRAL}; margin:0; line-height:1.4;">Comparison metric</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(card_html(mv, "Mexico", COUNTRY_COLORS["Mexico"], mx_wins), unsafe_allow_html=True)

    with col3:
        st.markdown(card_html(bv, "Brazil", COUNTRY_COLORS["Brazil"], not mx_wins if mx_wins is not None else None), unsafe_allow_html=True)


def insight_box(markdown_text: str):
    """Render a colored analyst insight callout."""
    st.markdown(
        f"""
        <div style="background-color:#F0F7F4; border-left:4px solid {GOOD}; padding:16px 20px; margin:20px 0; border-radius:8px; box-shadow: 0 1px 3px rgba(10,37,64,0.06);">
            <span style="font-weight:700; color:{ACCENT}; font-size:14px;">💡 Insight</span>
            <p style="color:{ACCENT}; margin:6px 0 0 0; font-size:14px; line-height:1.5;">{markdown_text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def source_badge(kind: str, label: str):
    """Render a source badge: LIVE / Curated / SNAPSHOT."""
    if kind == "LIVE":
        badge = f"<span style='color:{GOOD}; font-weight:700;'>🟢 LIVE</span> · {label}"
    elif kind == "SNAPSHOT":
        badge = f"<span style='color:#E6A23C; font-weight:700;'>🟡 SNAPSHOT</span> · {label}"
    else:
        badge = f"<span style='color:{NEUTRAL}; font-weight:700;'>📄 Curated</span> · {label}"
    st.markdown(f"""
    <div style="display:inline-block; background-color:#F4F6F8; padding:6px 14px; border-radius:20px; font-size:12px; margin-top:12px; border:1px solid {BORDER};">
        {badge}
    </div>
    """, unsafe_allow_html=True)


def freshness_caption(source_flag: str, date_str: str | None = None):
    """Render a freshness caption below a chart/section."""
    today = date_str or date.today().isoformat()
    if source_flag == "LIVE":
        st.caption(f"🟢 Updated live from World Bank / IMF API · {today}")
    elif source_flag == "SNAPSHOT":
        st.caption(f"🟡 Local snapshot (API unavailable) · {today}")
    else:
        st.caption(f"📄 Curated data · {today}")


def country_filter_apply(df, countries):
    """Filter DataFrame by selected countries."""
    if "Country" not in df.columns:
        return df
    return df[df["Country"].isin(countries)].copy()
