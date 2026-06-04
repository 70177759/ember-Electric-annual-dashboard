"""
charts.py — All visualization functions for the Ember Electricity Dashboard
Rewritten with Plotly for interactive, downloadable charts.
Charts: Pie, Histogram, Line, Bar, Scatter, Box, Heatmap, Area, Count, Violin, Bubble
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# GLOBAL THEME
# ─────────────────────────────────────────────

PALETTE = [
    "#2563EB", "#16A34A", "#DC2626", "#D97706", "#7C3AED",
    "#0891B2", "#DB2777", "#65A30D", "#EA580C", "#6366F1",
]

BACKGROUND = "#0F172A"
CARD_BG    = "#1E293B"
TEXT_COLOR = "#F1F5F9"
GRID_COLOR = "#334155"
ACCENT     = "#38BDF8"

LAYOUT_DEFAULTS = dict(
    paper_bgcolor=BACKGROUND,
    plot_bgcolor=CARD_BG,
    font=dict(color=TEXT_COLOR, family="Inter, Segoe UI, sans-serif", size=12),
    title_font=dict(color=TEXT_COLOR, size=15, family="Inter, Segoe UI, sans-serif"),
    legend=dict(
        bgcolor=CARD_BG,
        bordercolor=GRID_COLOR,
        borderwidth=1,
        font=dict(color=TEXT_COLOR, size=10),
    ),
    xaxis=dict(
        gridcolor=GRID_COLOR,
        linecolor=GRID_COLOR,
        tickcolor=TEXT_COLOR,
        tickfont=dict(color=TEXT_COLOR),
        title_font=dict(color=TEXT_COLOR),
        zerolinecolor=GRID_COLOR,
    ),
    yaxis=dict(
        gridcolor=GRID_COLOR,
        linecolor=GRID_COLOR,
        tickcolor=TEXT_COLOR,
        tickfont=dict(color=TEXT_COLOR),
        title_font=dict(color=TEXT_COLOR),
        zerolinecolor=GRID_COLOR,
    ),
    margin=dict(l=60, r=40, t=60, b=60),
)


def _apply_theme(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(title=dict(text=title, x=0.5, xanchor="center"), **LAYOUT_DEFAULTS)
    return fig


def _empty_fig(msg: str = "No data available") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=msg, xref="paper", yref="paper",
                       x=0.5, y=0.5, showarrow=False,
                       font=dict(color=TEXT_COLOR, size=14))
    return _apply_theme(fig)


# ─────────────────────────────────────────────
# 1. PIE CHART — Energy mix proportions
# ─────────────────────────────────────────────

def chart_pie(df: pd.DataFrame, country: str, year: int) -> go.Figure:
    """Proportional electricity generation mix for a single country & year."""
    fuel_vars = ["Coal", "Gas", "Nuclear", "Hydro", "Wind", "Solar",
                 "Bioenergy", "Other renewables", "Other fossil"]
    sub = df[
        (df["Area"] == country) &
        (df["Year"] == year) &
        (df["Variable"].isin(fuel_vars)) &
        (df["Unit"] == "%")
    ].dropna(subset=["Value"])

    if sub.empty:
        return _empty_fig(f"No data for {country} ({year})")

    sub = sub.groupby("Variable")["Value"].sum().reset_index()
    sub = sub[sub["Value"] > 0].sort_values("Value", ascending=False)

    fig = go.Figure(go.Pie(
        labels=sub["Variable"],
        values=sub["Value"],
        marker=dict(colors=PALETTE[:len(sub)], line=dict(color=BACKGROUND, width=2)),
        textinfo="label+percent",
        textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>Share: %{percent}<br>Value: %{value:.1f}%<extra></extra>",
        pull=[0.03] * len(sub),
    ))
    return _apply_theme(fig, f"Electricity Generation Mix — {country} ({year})")


# ─────────────────────────────────────────────
# 2. HISTOGRAM — CO2 intensity distribution
# ─────────────────────────────────────────────

def chart_histogram(df: pd.DataFrame) -> go.Figure:
    """Frequency distribution of CO2 intensity across countries & years."""
    sub = df[df["Variable"] == "CO2 intensity"].dropna(subset=["Value"])

    if sub.empty:
        return _empty_fig("No CO2 intensity data")

    mean_val = sub["Value"].mean()
    median_val = sub["Value"].median()

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=sub["Value"],
        nbinsx=40,
        marker=dict(color=ACCENT, line=dict(color=BACKGROUND, width=0.6)),
        opacity=0.85,
        name="CO₂ Intensity",
        hovertemplate="Range: %{x}<br>Count: %{y}<extra></extra>",
    ))
    fig.add_vline(x=mean_val, line=dict(color="#F59E0B", dash="dash", width=2),
                  annotation_text=f"Mean: {mean_val:.0f}",
                  annotation_font=dict(color="#F59E0B"),
                  annotation_position="top right")
    fig.add_vline(x=median_val, line=dict(color="#34D399", dash="dot", width=2),
                  annotation_text=f"Median: {median_val:.0f}",
                  annotation_font=dict(color="#34D399"),
                  annotation_position="top left")

    fig.update_layout(
        xaxis_title="CO₂ Intensity (gCO₂e per kWh)",
        yaxis_title="Frequency",
        bargap=0.05,
    )
    return _apply_theme(fig, "Distribution of CO₂ Intensity Across Countries & Years")


# ─────────────────────────────────────────────
# 3. LINE CHART — Trend over time
# ─────────────────────────────────────────────

def chart_line(df: pd.DataFrame, countries: list, variable: str, unit: str = None) -> go.Figure:
    """Line chart of a chosen variable over time for selected countries."""
    sub = df[(df["Variable"] == variable) & (df["Area"].isin(countries))].copy()
    if unit:
        sub = sub[sub["Unit"] == unit]
    sub = sub.dropna(subset=["Year", "Value"])

    if sub.empty:
        return _empty_fig("No data for selection")

    unit_label = sub["Unit"].iloc[0] if not sub.empty else ""
    fig = go.Figure()

    for i, country in enumerate(countries):
        data = sub[sub["Area"] == country].sort_values("Year")
        if data.empty:
            continue
        fig.add_trace(go.Scatter(
            x=data["Year"], y=data["Value"],
            mode="lines+markers",
            name=country,
            line=dict(color=PALETTE[i % len(PALETTE)], width=2.5),
            marker=dict(size=5),
            hovertemplate=f"<b>{country}</b><br>Year: %{{x}}<br>{variable}: %{{y:.2f}} {unit_label}<extra></extra>",
        ))

    fig.update_layout(
        xaxis_title="Year",
        yaxis_title=f"{variable} ({unit_label})",
        legend_title="Country",
        hovermode="x unified",
    )
    return _apply_theme(fig, f"{variable} Trend Over Time")


# ─────────────────────────────────────────────
# 4. BAR CHART — Country comparison
# ─────────────────────────────────────────────

def chart_bar(df: pd.DataFrame, variable: str, year: int, top_n: int = 15) -> go.Figure:
    """Horizontal bar chart comparing countries for a variable in a given year."""
    sub = df[
        (df["Variable"] == variable) &
        (df["Year"] == year) &
        df["is_country"]
    ].dropna(subset=["Value"])
    sub = sub.groupby("Area")["Value"].mean().nlargest(top_n).reset_index()
    sub = sub.sort_values("Value")

    if sub.empty:
        return _empty_fig("No data")

    unit_str = df[df["Variable"] == variable]["Unit"].dropna().iloc[0] \
        if not df[df["Variable"] == variable].empty else ""

    colors = [PALETTE[i % len(PALETTE)] for i in range(len(sub))]

    fig = go.Figure(go.Bar(
        x=sub["Value"], y=sub["Area"],
        orientation="h",
        marker=dict(color=colors, line=dict(color=BACKGROUND, width=0.5)),
        text=sub["Value"].round(1),
        textposition="outside",
        textfont=dict(color=TEXT_COLOR, size=10),
        hovertemplate="<b>%{y}</b><br>" + variable + ": %{x:.1f} " + unit_str + "<extra></extra>",
    ))
    fig.update_layout(
        xaxis_title=f"{variable} ({unit_str})",
        yaxis_title="",
        height=max(350, len(sub) * 28),
    )
    return _apply_theme(fig, f"Top {top_n} Countries — {variable} ({year})")


# ─────────────────────────────────────────────
# 5. SCATTER PLOT — Two variables relationship
# ─────────────────────────────────────────────

def chart_scatter(df: pd.DataFrame, year: int) -> go.Figure:
    """Scatter: Renewables % vs CO2 intensity per country."""
    ren = df[
        (df["Variable"] == "Renewables") & (df["Unit"] == "%") &
        (df["Year"] == year) & df["is_country"]
    ][["Area", "Value"]].rename(columns={"Value": "Renewables_%"})

    co2 = df[
        (df["Variable"] == "CO2 intensity") &
        (df["Year"] == year) & df["is_country"]
    ][["Area", "Value"]].rename(columns={"Value": "CO2_intensity"})

    merged = ren.merge(co2, on="Area").dropna()

    if merged.empty:
        return _empty_fig("No data for scatter")

    # Trend line
    z = np.polyfit(merged["Renewables_%"], merged["CO2_intensity"], 1)
    xs = np.linspace(merged["Renewables_%"].min(), merged["Renewables_%"].max(), 100)
    trend_y = np.poly1d(z)(xs)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=merged["Renewables_%"], y=merged["CO2_intensity"],
        mode="markers+text",
        text=merged["Area"],
        textposition="top center",
        textfont=dict(size=9, color=TEXT_COLOR),
        marker=dict(
            size=10,
            color=merged["CO2_intensity"],
            colorscale="RdYlGn_r",
            showscale=True,
            colorbar=dict(title="CO₂ Intensity", tickfont=dict(color=TEXT_COLOR),
                          title_font=dict(color=TEXT_COLOR)),
            line=dict(color=BACKGROUND, width=0.8),
        ),
        hovertemplate="<b>%{text}</b><br>Renewables: %{x:.1f}%<br>CO₂: %{y:.1f} gCO₂e/kWh<extra></extra>",
        name="Countries",
    ))
    fig.add_trace(go.Scatter(
        x=xs, y=trend_y,
        mode="lines",
        line=dict(color="#F59E0B", dash="dash", width=2),
        name="Trend",
        hoverinfo="skip",
    ))
    fig.update_layout(
        xaxis_title="Renewables Share (%)",
        yaxis_title="CO₂ Intensity (gCO₂e per kWh)",
    )
    return _apply_theme(fig, f"Renewables vs CO₂ Intensity — {year}")


# ─────────────────────────────────────────────
# 6. BOX PLOT — Distribution per region group
# ─────────────────────────────────────────────

def chart_box(df: pd.DataFrame, variable: str) -> go.Figure:
    """Box plot of variable distribution by EU membership."""
    sub = df[
        (df["Variable"] == variable) & df["is_country"]
    ].dropna(subset=["Value"]).copy()
    sub["Group"] = sub["EU"].map({1: "EU Member", 0: "Non-EU"})

    if sub.empty:
        return _empty_fig("No data")

    unit_str = sub["Unit"].dropna().iloc[0] if not sub.empty else ""
    fig = go.Figure()

    for group, color in [("EU Member", PALETTE[0]), ("Non-EU", PALETTE[2])]:
        vals = sub[sub["Group"] == group]["Value"]
        fig.add_trace(go.Box(
            y=vals, name=group,
            marker=dict(color=color, outliercolor=ACCENT, size=4),
            line=dict(color=color),
            boxmean="sd",
            hovertemplate=f"<b>{group}</b><br>Value: %{{y:.1f}} {unit_str}<extra></extra>",
        ))

    fig.update_layout(
        yaxis_title=f"{variable} ({unit_str})",
        showlegend=True,
    )
    return _apply_theme(fig, f"{variable} — EU vs Non-EU Distribution (All Years)")


# ─────────────────────────────────────────────
# 7. HEATMAP — Correlation matrix
# ─────────────────────────────────────────────

def chart_heatmap(df: pd.DataFrame, year: int) -> go.Figure:
    """Correlation heatmap of key electricity variables."""
    key_vars = ["Demand", "Renewables", "Fossil", "Nuclear",
                "CO2 intensity", "Solar", "Wind", "Hydro"]
    sub = df[
        (df["Year"] == year) & df["is_country"] &
        (df["Variable"].isin(key_vars))
    ].dropna(subset=["Value"])

    pivot = sub.pivot_table(index="Area", columns="Variable", values="Value", aggfunc="mean")
    pivot = pivot.dropna(thresh=3)

    if pivot.empty or pivot.shape[1] < 2:
        return _empty_fig("Not enough data for heatmap")

    corr = pivot.corr().round(2)
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    corr_masked = corr.where(~mask)

    fig = go.Figure(go.Heatmap(
        z=corr_masked.values,
        x=corr_masked.columns.tolist(),
        y=corr_masked.index.tolist(),
        colorscale="RdBu",
        zmid=0,
        text=corr_masked.values.round(2),
        texttemplate="%{text}",
        textfont=dict(size=10, color=TEXT_COLOR),
        hovertemplate="<b>%{y} × %{x}</b><br>Correlation: %{z:.2f}<extra></extra>",
        colorbar=dict(tickfont=dict(color=TEXT_COLOR), title_font=dict(color=TEXT_COLOR),
                      title="Correlation"),
    ))
    fig.update_layout(
        height=500,
        xaxis=dict(tickangle=30),
    )
    return _apply_theme(fig, f"Correlation Matrix of Electricity Variables ({year})")


# ─────────────────────────────────────────────
# 8. AREA CHART — Cumulative trends
# ─────────────────────────────────────────────

def chart_area(df: pd.DataFrame, countries: list, variable: str = "Renewables") -> go.Figure:
    """Area chart showing variable share over time for selected countries."""
    sub = df[
        (df["Variable"] == variable) &
        (df["Unit"] == "%") &
        (df["Area"].isin(countries)) &
        df["is_country"]
    ].dropna(subset=["Year", "Value"])

    pivot = sub.pivot_table(index="Year", columns="Area", values="Value", aggfunc="mean")
    pivot = pivot.sort_index().ffill().fillna(0)

    if pivot.empty:
        return _empty_fig("No data for area chart")

    cols = pivot.columns.tolist()[:10]
    fig = go.Figure()

    for i, col in enumerate(cols):
        fig.add_trace(go.Scatter(
            x=pivot.index, y=pivot[col],
            mode="lines",
            name=col,
            fill="tozeroy",
            fillcolor=f"rgba({int(PALETTE[i % len(PALETTE)][1:3], 16)}, "
                       f"{int(PALETTE[i % len(PALETTE)][3:5], 16)}, "
                       f"{int(PALETTE[i % len(PALETTE)][5:7], 16)}, 0.25)",
            line=dict(color=PALETTE[i % len(PALETTE)], width=2),
            hovertemplate=f"<b>{col}</b><br>Year: %{{x}}<br>{variable}: %{{y:.1f}}%<extra></extra>",
        ))

    fig.update_layout(
        xaxis_title="Year",
        yaxis_title=f"{variable} (%)",
        hovermode="x unified",
        legend_title="Country",
    )
    return _apply_theme(fig, f"{variable} Share Over Time — Selected Countries")


# ─────────────────────────────────────────────
# 9. COUNT PLOT — Frequency of categorical data
# ─────────────────────────────────────────────

def chart_count(df: pd.DataFrame) -> go.Figure:
    """Bar chart: number of data entries per Category."""
    sub = df[df["is_country"]].copy()

    if sub.empty:
        return _empty_fig("No data")

    counts = sub["Category"].value_counts().reset_index()
    counts.columns = ["Category", "Count"]

    fig = go.Figure(go.Bar(
        x=counts["Category"], y=counts["Count"],
        marker=dict(
            color=PALETTE[:len(counts)],
            line=dict(color=BACKGROUND, width=0.5),
        ),
        text=counts["Count"].apply(lambda v: f"{v:,}"),
        textposition="outside",
        textfont=dict(color=TEXT_COLOR, size=10),
        hovertemplate="<b>%{x}</b><br>Records: %{y:,}<extra></extra>",
    ))
    fig.update_layout(
        xaxis_title="Data Category",
        yaxis_title="Number of Records",
        xaxis_tickangle=15,
    )
    return _apply_theme(fig, "Record Count by Electricity Data Category")


# ─────────────────────────────────────────────
# 10. VIOLIN PLOT — Distribution & density
# ─────────────────────────────────────────────

def chart_violin(df: pd.DataFrame, variable: str) -> go.Figure:
    """Violin plot of a variable across decades."""
    sub = df[
        (df["Variable"] == variable) & df["is_country"]
    ].dropna(subset=["Year", "Value"]).copy()
    sub["Decade"] = (sub["Year"] // 10 * 10).astype(str) + "s"

    if sub.empty or sub["Decade"].nunique() < 2:
        return _empty_fig("Not enough data for violin")

    unit_str = sub["Unit"].dropna().iloc[0] if not sub.empty else ""
    decade_order = sorted(sub["Decade"].unique())
    fig = go.Figure()

    for i, decade in enumerate(decade_order):
        vals = sub[sub["Decade"] == decade]["Value"]
        fig.add_trace(go.Violin(
            y=vals, name=decade,
            box_visible=True,
            meanline_visible=True,
            fillcolor=PALETTE[i % len(PALETTE)],
            line_color=PALETTE[i % len(PALETTE)],
            opacity=0.75,
            hovertemplate=f"<b>{decade}</b><br>Value: %{{y:.1f}} {unit_str}<extra></extra>",
        ))

    fig.update_layout(
        yaxis_title=f"{variable} ({unit_str})",
        xaxis_title="Decade",
        violinmode="overlay",
    )
    return _apply_theme(fig, f"{variable} Distribution by Decade")


# ─────────────────────────────────────────────
# BONUS — BUBBLE CHART
# ─────────────────────────────────────────────

def chart_bubble(df: pd.DataFrame, year: int) -> go.Figure:
    """Bubble chart: Renewables (x) vs CO2 (y), bubble size = Demand."""
    ren = df[(df["Variable"] == "Renewables") & (df["Unit"] == "%") &
             (df["Year"] == year) & df["is_country"]
             ][["Area", "Value"]].rename(columns={"Value": "Ren"})
    co2 = df[(df["Variable"] == "CO2 intensity") & (df["Year"] == year) &
             df["is_country"]
             ][["Area", "Value"]].rename(columns={"Value": "CO2"})
    dem = df[(df["Variable"] == "Demand") & (df["Year"] == year) &
             df["is_country"]
             ][["Area", "Value"]].rename(columns={"Value": "Demand"})

    merged = ren.merge(co2, on="Area").merge(dem, on="Area").dropna()

    if merged.empty:
        return _empty_fig("No data")

    fig = go.Figure(go.Scatter(
        x=merged["Ren"], y=merged["CO2"],
        mode="markers+text",
        text=merged["Area"],
        textposition="top center",
        textfont=dict(size=9, color=TEXT_COLOR),
        marker=dict(
            size=((merged["Demand"] / merged["Demand"].max()) * 60 + 10),
            color=merged["CO2"],
            colorscale="RdYlGn_r",
            showscale=True,
            colorbar=dict(title="CO₂ Intensity", tickfont=dict(color=TEXT_COLOR),
                          title_font=dict(color=TEXT_COLOR)),
            line=dict(color=TEXT_COLOR, width=0.6),
            opacity=0.85,
        ),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Renewables: %{x:.1f}%<br>"
            "CO₂: %{y:.1f} gCO₂e/kWh<br>"
            "Demand: %{marker.size:.0f} (scaled)<extra></extra>"
        ),
    ))
    fig.update_layout(
        xaxis_title="Renewables Share (%)",
        yaxis_title="CO₂ Intensity (gCO₂e per kWh)",
    )
    return _apply_theme(fig, f"Bubble Chart — Renewables vs CO₂ (bubble = Demand) [{year}]")
