"""
lib/data_loader.py — Load curated CSV files with caching.
"""

import pandas as pd
import streamlit as st
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "curated"


@st.cache_data
def load_cpi() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "CPI_Corruption.csv")
    df["Year"] = df["Year"].astype(int)
    return df


@st.cache_data
def load_economic_freedom() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "Economic_Freedom.csv")
    df["Year"] = df["Year"].astype(int)
    return df


@st.cache_data
def load_wgi() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "WGI_Governance.csv")
    df["Year"] = df["Year"].astype(int)
    return df


@st.cache_data
def load_credit_ratings() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "Credit_Ratings.csv")


@st.cache_data
def load_manufacturing_ev() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "Manufacturing_EV.csv")


@st.cache_data
def load_comparison() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "Comparison.csv")


@st.cache_data
def load_sources() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "Sources.csv")


def load_all_curated() -> dict:
    """Load all curated datasets into a dictionary."""
    return {
        "cpi": load_cpi(),
        "economic_freedom": load_economic_freedom(),
        "wgi": load_wgi(),
        "credit_ratings": load_credit_ratings(),
        "manufacturing_ev": load_manufacturing_ev(),
        "comparison": load_comparison(),
        "sources": load_sources(),
    }
