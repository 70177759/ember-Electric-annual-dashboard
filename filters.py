"""
filters.py — Data loading, cleaning, and filtering functions
Ember Yearly Electricity Dashboard
"""

import pandas as pd
import numpy as np

DATA_PATH = "data/europe_yearly_full_release_long_format.csv"


# ─────────────────────────────────────────────
# 1. LOAD & CLEAN
# ─────────────────────────────────────────────

def load_data() -> pd.DataFrame:
    try:
        import streamlit as st
        @st.cache_data
        def _inner():
            return _load()
        return _inner()
    except Exception:
        return _load()


def _load() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)

    # ── Basic cleaning ──────────────────────────────────────────────────
    df.columns = df.columns.str.strip()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df["YoY absolute change"] = pd.to_numeric(df["YoY absolute change"], errors="coerce")
    df["YoY % change"] = pd.to_numeric(df["YoY % change"], errors="coerce")

    # Drop rows where both Year and Value are null
    df.dropna(subset=["Year", "Value"], how="all", inplace=True)

    # ── Derived helpers ─────────────────────────────────────────────────
    for col in ["EU", "OECD", "G20", "G7", "ASEAN"]:
        df[col] = df[col].fillna(0).astype(int)

    df["is_country"] = df["Area type"].str.lower().str.contains("country", na=False)
    return df


# ─────────────────────────────────────────────
# 2. FILTER HELPERS
# ─────────────────────────────────────────────

def get_countries(df: pd.DataFrame) -> list:
    return sorted(df.loc[df["is_country"], "Area"].dropna().unique().tolist())


def get_year_range(df: pd.DataFrame):
    return int(df["Year"].min()), int(df["Year"].max())


def get_variables(df: pd.DataFrame) -> list:
    return sorted(df["Variable"].dropna().unique().tolist())


def get_categories(df: pd.DataFrame) -> list:
    return sorted(df["Category"].dropna().unique().tolist())


def apply_filters(
    df: pd.DataFrame,
    countries: list,
    year_range: tuple,
    categories: list,
    variables: list,
    search_text: str = "",
) -> pd.DataFrame:
    """Apply all sidebar filters and return filtered DataFrame."""
    filtered = df.copy()

    if countries:
        filtered = filtered[filtered["Area"].isin(countries)]

    filtered = filtered[
        (filtered["Year"] >= year_range[0]) & (filtered["Year"] <= year_range[1])
    ]

    if categories:
        filtered = filtered[filtered["Category"].isin(categories)]

    if variables:
        filtered = filtered[filtered["Variable"].isin(variables)]

    if search_text.strip():
        mask = (
            filtered["Area"].str.contains(search_text, case=False, na=False)
            | filtered["Variable"].str.contains(search_text, case=False, na=False)
            | filtered["Category"].str.contains(search_text, case=False, na=False)
            | filtered["Subcategory"].str.contains(search_text, case=False, na=False)
        )
        filtered = filtered[mask]

    return filtered.reset_index(drop=True)


# ─────────────────────────────────────────────
# 3. KPI HELPERS
# ─────────────────────────────────────────────

def compute_kpis(df: pd.DataFrame, filtered: pd.DataFrame) -> dict:
    total_records = len(filtered)
    latest_year = int(filtered["Year"].max()) if not filtered.empty else "N/A"

    co2_rows = filtered[filtered["Variable"] == "CO2 intensity"]["Value"]
    avg_co2 = round(co2_rows.mean(), 1) if not co2_rows.empty else "N/A"

    ren = filtered[
        (filtered["Variable"] == "Renewables")
        & (filtered["Unit"] == "%")
        & (filtered["Year"] == latest_year)
        & filtered["is_country"]
    ]
    if not ren.empty:
        idx = ren["Value"].idxmax()
        top_ren_country = ren.loc[idx, "Area"]
        top_ren_val = round(ren.loc[idx, "Value"], 1)
    else:
        top_ren_country, top_ren_val = "N/A", "N/A"

    co2_latest = filtered[
        (filtered["Variable"] == "CO2 intensity")
        & (filtered["Year"] == latest_year)
        & filtered["is_country"]
    ]
    if not co2_latest.empty:
        idx2 = co2_latest["Value"].idxmax()
        top_co2_country = co2_latest.loc[idx2, "Area"]
        top_co2_val = round(co2_latest.loc[idx2, "Value"], 1)
    else:
        top_co2_country, top_co2_val = "N/A", "N/A"

    return {
        "total_records": total_records,
        "latest_year": latest_year,
        "avg_co2_intensity": avg_co2,
        "top_ren_country": top_ren_country,
        "top_ren_val": top_ren_val,
        "top_co2_country": top_co2_country,
        "top_co2_val": top_co2_val,
    }
