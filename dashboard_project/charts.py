"""
charts.py — All visualization functions for the Ember Electricity Dashboard
Charts: Pie, Histogram, Line, Bar, Scatter, Box, Heatmap, Area, Count, Violin
Bonus : Bubble Chart
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ─────────────────────────────────────────────
# GLOBAL STYLE
# ─────────────────────────────────────────────

PALETTE = [
    "#2563EB", "#16A34A", "#DC2626", "#D97706", "#7C3AED",
    "#0891B2", "#DB2777", "#65A30D", "#EA580C", "#6366F1",
]

BACKGROUND  = "#0F172A"   # dark navy
CARD_BG     = "#1E293B"   # slightly lighter card
TEXT_COLOR  = "#F1F5F9"
GRID_COLOR  = "#334155"
ACCENT      = "#38BDF8"   # sky blue


def _base_style():
    plt.rcParams.update({
        "figure.facecolor":  BACKGROUND,
        "axes.facecolor":    CARD_BG,
        "axes.edgecolor":    GRID_COLOR,
        "axes.labelcolor":   TEXT_COLOR,
        "axes.titlecolor":   TEXT_COLOR,
        "axes.titlesize":    13,
        "axes.labelsize":    11,
        "xtick.color":       TEXT_COLOR,
        "ytick.color":       TEXT_COLOR,
        "xtick.labelsize":   9,
        "ytick.labelsize":   9,
        "grid.color":        GRID_COLOR,
        "grid.linestyle":    "--",
        "grid.alpha":        0.4,
        "legend.facecolor":  CARD_BG,
        "legend.edgecolor":  GRID_COLOR,
        "legend.labelcolor": TEXT_COLOR,
        "legend.fontsize":   9,
        "text.color":        TEXT_COLOR,
        "font.family":       "DejaVu Sans",
    })


def _fig(w=10, h=5):
    _base_style()
    return plt.subplots(figsize=(w, h))


def _save_close(fig, tight=True):
    if tight:
        fig.tight_layout()
    return fig


# ─────────────────────────────────────────────
# 1. PIE CHART — Energy mix proportions
# ─────────────────────────────────────────────

def chart_pie(df: pd.DataFrame, country: str, year: int):
    """
    Proportional electricity generation mix for a single country & year.
    """
    fuel_vars = ["Coal", "Gas", "Nuclear", "Hydro", "Wind", "Solar",
                 "Bioenergy", "Other renewables", "Other fossil"]
    sub = df[
        (df["Area"] == country) &
        (df["Year"] == year) &
        (df["Variable"].isin(fuel_vars)) &
        (df["Unit"] == "%")
    ].dropna(subset=["Value"])

    fig, ax = _fig(7, 6)
    if sub.empty:
        ax.text(0.5, 0.5, "No data available", ha="center", va="center",
                transform=ax.transAxes, color=TEXT_COLOR, fontsize=13)
        ax.set_title(f"Energy Mix — {country} ({year})")
        return _save_close(fig)

    sub = sub.groupby("Variable")["Value"].sum().reset_index()
    sub = sub[sub["Value"] > 0].sort_values("Value", ascending=False)

    wedges, texts, autotexts = ax.pie(
        sub["Value"],
        labels=sub["Variable"],
        autopct=lambda p: f"{p:.1f}%" if p > 3 else "",
        colors=PALETTE[:len(sub)],
        startangle=140,
        wedgeprops=dict(edgecolor=BACKGROUND, linewidth=1.5),
        textprops=dict(color=TEXT_COLOR, fontsize=9),
    )
    for at in autotexts:
        at.set_fontsize(8)
        at.set_color(BACKGROUND)
        at.set_fontweight("bold")

    ax.set_title(f"Electricity Generation Mix — {country} ({year})",
                 fontsize=14, fontweight="bold", pad=15)
    ax.legend(sub["Variable"], loc="lower right", fontsize=8,
              facecolor=CARD_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
    return _save_close(fig)


# ─────────────────────────────────────────────
# 2. HISTOGRAM — CO2 intensity distribution
# ─────────────────────────────────────────────

def chart_histogram(df: pd.DataFrame):
    """Frequency distribution of CO2 intensity across countries & years."""
    sub = df[df["Variable"] == "CO2 intensity"].dropna(subset=["Value"])

    fig, ax = _fig(9, 5)
    if sub.empty:
        ax.text(0.5, 0.5, "No CO2 intensity data", ha="center", va="center",
                transform=ax.transAxes, color=TEXT_COLOR)
        return _save_close(fig)

    ax.hist(sub["Value"], bins=40, color=ACCENT, edgecolor=BACKGROUND,
            alpha=0.85, linewidth=0.6)
    ax.axvline(sub["Value"].mean(), color="#F59E0B", linestyle="--",
               linewidth=1.8, label=f"Mean: {sub['Value'].mean():.0f}")
    ax.axvline(sub["Value"].median(), color="#34D399", linestyle=":",
               linewidth=1.8, label=f"Median: {sub['Value'].median():.0f}")

    ax.set_xlabel("CO₂ Intensity (gCO₂e per kWh)")
    ax.set_ylabel("Frequency")
    ax.set_title("Distribution of CO₂ Intensity Across Countries & Years",
                 fontweight="bold")
    ax.legend()
    ax.grid(axis="y")
    return _save_close(fig)


# ─────────────────────────────────────────────
# 3. LINE CHART — Trend over time
# ─────────────────────────────────────────────

def chart_line(df: pd.DataFrame, countries: list, variable: str, unit: str = None):
    """Line chart of a chosen variable over time for selected countries."""
    sub = df[(df["Variable"] == variable) & (df["Area"].isin(countries))].copy()
    if unit:
        sub = sub[sub["Unit"] == unit]
    sub = sub.dropna(subset=["Year", "Value"])

    fig, ax = _fig(11, 5)
    if sub.empty:
        ax.text(0.5, 0.5, "No data for selection", ha="center", va="center",
                transform=ax.transAxes, color=TEXT_COLOR)
        ax.set_title(f"{variable} — Trend Over Time")
        return _save_close(fig)

    for i, country in enumerate(countries):
        data = sub[sub["Area"] == country].sort_values("Year")
        if data.empty:
            continue
        ax.plot(data["Year"], data["Value"], marker="o", markersize=3,
                color=PALETTE[i % len(PALETTE)], label=country, linewidth=2)

    ax.set_xlabel("Year")
    ax.set_ylabel(f"{variable} ({sub['Unit'].iloc[0] if not sub.empty else ''})")
    ax.set_title(f"{variable} Trend — {', '.join(countries[:5])}",
                 fontweight="bold")
    ax.legend(loc="best", ncol=2)
    ax.grid(axis="y")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    return _save_close(fig)


# ─────────────────────────────────────────────
# 4. BAR CHART — Country comparison
# ─────────────────────────────────────────────

def chart_bar(df: pd.DataFrame, variable: str, year: int, top_n: int = 15):
    """Horizontal bar chart comparing countries for a variable in a given year."""
    sub = df[
        (df["Variable"] == variable) &
        (df["Year"] == year) &
        df["is_country"]
    ].dropna(subset=["Value"])
    sub = sub.groupby("Area")["Value"].mean().nlargest(top_n).reset_index()
    sub = sub.sort_values("Value")

    fig, ax = _fig(10, max(5, len(sub) * 0.45))
    if sub.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center",
                transform=ax.transAxes, color=TEXT_COLOR)
        return _save_close(fig)

    colors = [PALETTE[i % len(PALETTE)] for i in range(len(sub))]
    bars = ax.barh(sub["Area"], sub["Value"], color=colors, edgecolor=BACKGROUND,
                   height=0.7)

    # Value labels
    for bar, val in zip(bars, sub["Value"]):
        ax.text(bar.get_width() + bar.get_width() * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}", va="center", ha="left", fontsize=8, color=TEXT_COLOR)

    unit_str = df[df["Variable"] == variable]["Unit"].dropna().iloc[0] \
        if not df[df["Variable"] == variable].empty else ""
    ax.set_xlabel(f"{variable} ({unit_str})")
    ax.set_title(f"Top {top_n} Countries — {variable} ({year})", fontweight="bold")
    ax.grid(axis="x")
    return _save_close(fig)


# ─────────────────────────────────────────────
# 5. SCATTER PLOT — Two variables relationship
# ─────────────────────────────────────────────

def chart_scatter(df: pd.DataFrame, year: int):
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

    fig, ax = _fig(10, 6)
    if merged.empty:
        ax.text(0.5, 0.5, "No data for scatter", ha="center", va="center",
                transform=ax.transAxes, color=TEXT_COLOR)
        return _save_close(fig)

    scatter = ax.scatter(
        merged["Renewables_%"], merged["CO2_intensity"],
        c=merged["CO2_intensity"], cmap="RdYlGn_r",
        s=100, edgecolors=BACKGROUND, linewidth=0.8, alpha=0.9
    )
    cbar = fig.colorbar(scatter, ax=ax, pad=0.01)
    cbar.ax.yaxis.set_tick_params(color=TEXT_COLOR)
    cbar.set_label("CO₂ Intensity (gCO₂e/kWh)", color=TEXT_COLOR)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TEXT_COLOR)

    for _, row in merged.iterrows():
        ax.annotate(row["Area"], (row["Renewables_%"], row["CO2_intensity"]),
                    fontsize=7, color=TEXT_COLOR, alpha=0.8,
                    xytext=(3, 3), textcoords="offset points")

    # Trend line
    z = np.polyfit(merged["Renewables_%"], merged["CO2_intensity"], 1)
    p = np.poly1d(z)
    xs = np.linspace(merged["Renewables_%"].min(), merged["Renewables_%"].max(), 100)
    ax.plot(xs, p(xs), "--", color="#F59E0B", linewidth=1.5, label="Trend")

    ax.set_xlabel("Renewables Share (%)")
    ax.set_ylabel("CO₂ Intensity (gCO₂e per kWh)")
    ax.set_title(f"Renewables vs CO₂ Intensity — {year}", fontweight="bold")
    ax.legend()
    ax.grid()
    return _save_close(fig)


# ─────────────────────────────────────────────
# 6. BOX PLOT — Distribution per region group
# ─────────────────────────────────────────────

def chart_box(df: pd.DataFrame, variable: str):
    """Box plot of variable distribution by EU membership."""
    sub = df[
        (df["Variable"] == variable) & df["is_country"]
    ].dropna(subset=["Value"]).copy()

    sub["Group"] = sub["EU"].map({1: "EU Member", 0: "Non-EU"})

    fig, ax = _fig(9, 5)
    if sub.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center",
                transform=ax.transAxes, color=TEXT_COLOR)
        return _save_close(fig)

    sns.boxplot(
        data=sub, x="Group", y="Value",
        palette={"EU Member": PALETTE[0], "Non-EU": PALETTE[2]},
        width=0.5, flierprops=dict(marker="o", markersize=4,
                                   markerfacecolor=ACCENT, alpha=0.6),
        ax=ax
    )
    unit_str = sub["Unit"].dropna().iloc[0] if not sub.empty else ""
    ax.set_xlabel("Country Group")
    ax.set_ylabel(f"{variable} ({unit_str})")
    ax.set_title(f"{variable} — EU vs Non-EU Distribution (All Years)",
                 fontweight="bold")
    ax.grid(axis="y")
    return _save_close(fig)


# ─────────────────────────────────────────────
# 7. HEATMAP — Correlation matrix
# ─────────────────────────────────────────────

def chart_heatmap(df: pd.DataFrame, year: int):
    """
    Correlation heatmap of key electricity variables across countries for a year.
    """
    key_vars = ["Demand", "Renewables", "Fossil", "Nuclear",
                "CO2 intensity", "Solar", "Wind", "Hydro"]
    sub = df[
        (df["Year"] == year) & df["is_country"] &
        (df["Variable"].isin(key_vars))
    ].dropna(subset=["Value"])

    pivot = sub.pivot_table(index="Area", columns="Variable", values="Value", aggfunc="mean")
    pivot = pivot.dropna(thresh=3)

    fig, ax = _fig(10, 7)
    if pivot.empty or pivot.shape[1] < 2:
        ax.text(0.5, 0.5, "Not enough data for heatmap", ha="center", va="center",
                transform=ax.transAxes, color=TEXT_COLOR)
        return _save_close(fig)

    corr = pivot.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))

    sns.heatmap(
        corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm",
        center=0, linewidths=0.5, linecolor=BACKGROUND,
        annot_kws={"size": 9, "color": TEXT_COLOR},
        ax=ax, cbar_kws={"shrink": 0.8}
    )
    ax.set_title(f"Correlation Matrix of Electricity Variables ({year})",
                 fontweight="bold", pad=10)
    ax.tick_params(axis="x", rotation=30)
    ax.tick_params(axis="y", rotation=0)
    return _save_close(fig)


# ─────────────────────────────────────────────
# 8. AREA CHART — Cumulative trends
# ─────────────────────────────────────────────

def chart_area(df: pd.DataFrame, countries: list, variable: str = "Renewables"):
    """
    Stacked area chart showing cumulative variable over time for top countries.
    """
    sub = df[
        (df["Variable"] == variable) &
        (df["Unit"] == "%") &
        (df["Area"].isin(countries)) &
        df["is_country"]
    ].dropna(subset=["Year", "Value"])

    pivot = sub.pivot_table(index="Year", columns="Area", values="Value", aggfunc="mean")
    pivot = pivot.sort_index().ffill().fillna(0)

    fig, ax = _fig(12, 5)
    if pivot.empty:
        ax.text(0.5, 0.5, "No data for area chart", ha="center", va="center",
                transform=ax.transAxes, color=TEXT_COLOR)
        return _save_close(fig)

    cols = pivot.columns.tolist()[:10]
    pivot[cols].plot.area(ax=ax, stacked=False, alpha=0.35,
                          color=PALETTE[:len(cols)], linewidth=1.5)

    ax.set_xlabel("Year")
    ax.set_ylabel(f"{variable} (%)")
    ax.set_title(f"{variable} Share Over Time — Selected Countries",
                 fontweight="bold")
    ax.legend(loc="upper left", ncol=3, fontsize=8)
    ax.grid(axis="y")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    return _save_close(fig)


# ─────────────────────────────────────────────
# 9. COUNT PLOT — Frequency of categorical data
# ─────────────────────────────────────────────

def chart_count(df: pd.DataFrame):
    """Count plot: number of data entries per Category."""
    sub = df[df["is_country"]].copy()

    fig, ax = _fig(9, 5)
    if sub.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center",
                transform=ax.transAxes, color=TEXT_COLOR)
        return _save_close(fig)

    order = sub["Category"].value_counts().index.tolist()
    sns.countplot(data=sub, x="Category", order=order,
                  palette=PALETTE[:len(order)], ax=ax,
                  edgecolor=BACKGROUND)

    ax.set_xlabel("Data Category")
    ax.set_ylabel("Number of Records")
    ax.set_title("Record Count by Electricity Data Category", fontweight="bold")
    ax.tick_params(axis="x", rotation=15)
    ax.grid(axis="y")

    for p in ax.patches:
        ax.annotate(f"{int(p.get_height()):,}",
                    (p.get_x() + p.get_width() / 2, p.get_height()),
                    ha="center", va="bottom", fontsize=9, color=TEXT_COLOR)
    return _save_close(fig)


# ─────────────────────────────────────────────
# 10. VIOLIN PLOT — Distribution & density
# ─────────────────────────────────────────────

def chart_violin(df: pd.DataFrame, variable: str):
    """Violin plot of a variable across decades."""
    sub = df[
        (df["Variable"] == variable) & df["is_country"]
    ].dropna(subset=["Year", "Value"]).copy()

    sub["Decade"] = (sub["Year"] // 10 * 10).astype(str) + "s"

    fig, ax = _fig(10, 5)
    if sub.empty or sub["Decade"].nunique() < 2:
        ax.text(0.5, 0.5, "Not enough data for violin", ha="center", va="center",
                transform=ax.transAxes, color=TEXT_COLOR)
        return _save_close(fig)

    decade_order = sorted(sub["Decade"].unique())
    sns.violinplot(
        data=sub, x="Decade", y="Value", order=decade_order,
        palette=PALETTE[:len(decade_order)], inner="quartile",
        linewidth=1.2, ax=ax
    )
    unit_str = sub["Unit"].dropna().iloc[0] if not sub.empty else ""
    ax.set_xlabel("Decade")
    ax.set_ylabel(f"{variable} ({unit_str})")
    ax.set_title(f"{variable} Distribution by Decade", fontweight="bold")
    ax.grid(axis="y")
    return _save_close(fig)


# ─────────────────────────────────────────────
# BONUS — BUBBLE CHART
# ─────────────────────────────────────────────

def chart_bubble(df: pd.DataFrame, year: int):
    """
    Bubble chart: Renewables (x) vs CO2 (y) with bubble size = Demand.
    """
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

    fig, ax = _fig(11, 6)
    if merged.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center",
                transform=ax.transAxes, color=TEXT_COLOR)
        return _save_close(fig)

    sizes = (merged["Demand"] / merged["Demand"].max()) * 1500 + 100

    sc = ax.scatter(merged["Ren"], merged["CO2"], s=sizes,
                    c=merged["CO2"], cmap="RdYlGn_r",
                    edgecolors=TEXT_COLOR, linewidth=0.6, alpha=0.85)
    for _, row in merged.iterrows():
        ax.annotate(row["Area"], (row["Ren"], row["CO2"]),
                    fontsize=7, color=TEXT_COLOR, alpha=0.85,
                    xytext=(4, 4), textcoords="offset points")

    cbar = fig.colorbar(sc, ax=ax, pad=0.01)
    cbar.set_label("CO₂ Intensity (gCO₂e/kWh)", color=TEXT_COLOR)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TEXT_COLOR)

    ax.set_xlabel("Renewables Share (%)")
    ax.set_ylabel("CO₂ Intensity (gCO₂e per kWh)")
    ax.set_title(f"Bubble Chart — Renewables vs CO₂ (bubble = Demand) [{year}]",
                 fontweight="bold")
    ax.grid()
    return _save_close(fig)
