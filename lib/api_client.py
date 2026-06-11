"""
lib/api_client.py — Live API client for World Bank + IMF with fallback to snapshot CSV.
"""

import requests
import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime

SNAPSHOT_DIR = Path(__file__).resolve().parent.parent / "data" / "snapshot"

WB_INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": "GDP_Growth_Pct",
    "FP.CPI.TOTL.ZG": "Inflation_CPI_Pct",
    "SL.UEM.TOTL.ZS": "Unemployment_Pct",
    "BX.KLT.DINV.WD.GD.ZS": "FDI_Inflows_Pct_GDP",
    "NV.IND.MANF.ZS": "Manufacturing_Pct_GDP",
    "NE.EXP.GNFS.ZS": "Exports_Pct_GDP",
    "NY.GDP.MKTP.CD": "GDP_Current_USD",
}

ISO3_TO_NAME = {"MEX": "Mexico", "BRA": "Brazil"}


def _save_snapshot(df: pd.DataFrame, name: str):
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SNAPSHOT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)


def _load_snapshot(name: str) -> pd.DataFrame:
    path = SNAPSHOT_DIR / f"{name}.csv"
    return pd.read_csv(path)


@st.cache_data(ttl=86400)
def fetch_worldbank(indicator: str, countries: str = "MEX;BRA", start: int = 2015, end: int = 2024) -> pd.DataFrame:
    url = (
        f"https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}"
        f"?format=json&date={start}:{end}&per_page=500"
    )
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, list) or len(data) < 2:
        raise ValueError("Unexpected World Bank response structure")
    records = data[1]
    rows = []
    for r in records:
        iso = r.get("countryiso3code")
        year = r.get("date")
        val = r.get("value")
        if iso and year and val is not None:
            rows.append({
                "Country": ISO3_TO_NAME.get(iso, iso),
                "Year": int(year),
                WB_INDICATORS[indicator]: float(val),
            })
    return pd.DataFrame(rows)


@st.cache_data(ttl=86400)
def fetch_imf(indicator: str, countries: tuple = ("MEX", "BRA"), start: int = 2015, end: int = 2026) -> pd.DataFrame:
    url = f"https://www.imf.org/external/datamapper/api/v1/{indicator}/{'/'.join(countries)}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    values = data.get("values", {}).get(indicator, {})
    rows = []
    for iso in countries:
        iso_upper = iso.upper()
        country_name = ISO3_TO_NAME.get(iso_upper, iso_upper)
        country_data = values.get(iso_upper, {})
        for year_str, val in country_data.items():
            y = int(year_str)
            if val is not None and start <= y <= end:
                rows.append({
                    "Country": country_name,
                    "Year": y,
                    indicator: float(val),
                })
    return pd.DataFrame(rows)


def get_macro() -> tuple[pd.DataFrame, str]:
    """
    Fetch macro data from World Bank API with fallback to snapshot.
    Returns (DataFrame, source_flag) where source_flag is 'LIVE' or 'SNAPSHOT'.
    """
    try:
        dfs = []
        for code, col in WB_INDICATORS.items():
            df = fetch_worldbank(code)
            if not df.empty:
                dfs.append(df)
        if not dfs:
            raise ValueError("No data from API")
        # Merge all indicator DataFrames on Country + Year
        merged = dfs[0]
        for d in dfs[1:]:
            merged = merged.merge(d, on=["Country", "Year"], how="outer")
        # Convert GDP_Current_USD from absolute USD to billions
        if "GDP_Current_USD" in merged.columns:
            merged["GDP_Current_USD"] = merged["GDP_Current_USD"] / 1e9
        # Sort
        merged = merged.sort_values(["Country", "Year"]).reset_index(drop=True)
        _save_snapshot(merged, "worldbank_macro")
        return merged, "LIVE"
    except Exception:
        df = _load_snapshot("worldbank_macro")
        return df, "SNAPSHOT"


def get_forecast() -> tuple[pd.DataFrame, str]:
    """
    Fetch IMF forecast data with fallback to snapshot.
    Returns (DataFrame, source_flag).
    """
    imf_indicators = {
        "NGDP_RPCH": "GDP_Growth_Pct",
        "PCPIPCH": "Inflation_CPI_Pct",
        "LUR": "Unemployment_Pct",
    }
    try:
        dfs = []
        for code, col in imf_indicators.items():
            df = fetch_imf(code)
            if not df.empty:
                df = df.rename(columns={code: col})
                dfs.append(df)
        if not dfs:
            raise ValueError("No IMF data")
        merged = dfs[0]
        for d in dfs[1:]:
            merged = merged.merge(d, on=["Country", "Year"], how="outer")
        merged["Note"] = merged["Year"].apply(lambda y: "Forecast" if y >= 2025 else "Actual")
        merged = merged.sort_values(["Country", "Year"]).reset_index(drop=True)
        _save_snapshot(merged, "imf_forecast")
        return merged, "LIVE"
    except Exception:
        df = _load_snapshot("imf_forecast")
        return df, "SNAPSHOT"
