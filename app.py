"""
app.py — Ember Yearly Electricity Dashboard
Main Streamlit application entry point.

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd

# ── Local modules ────────────────────────────────────────────────────────────
from filters import load_data, apply_filters, compute_kpis, get_countries, \
    get_year_range, get_variables, get_categories
from charts import (
    chart_pie, chart_histogram, chart_line, chart_bar,
    chart_scatter, chart_box, chart_heatmap, chart_area,
    chart_count, chart_violin, chart_bubble,
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="⚡ Ember Electricity Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS for dark professional theme ───────────────────────────────────
st.markdown("""
<style>
  /* ---- global ---- */
  html, body, [class*="css"] {
    background-color: #0F172A !important;
    color: #F1F5F9 !important;
    font-family: 'Inter', 'Segoe UI', sans-serif;
  }

  /* ---- sidebar ---- */
  [data-testid="stSidebar"] {
    background-color: #1E293B !important;
    border-right: 1px solid #334155;
  }
  [data-testid="stSidebar"] * { color: #CBD5E1 !important; }

  /* ---- KPI cards ---- */
  .kpi-card {
    background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  }
  .kpi-val  { font-size: 2rem; font-weight: 700; color: #38BDF8; }
  .kpi-sub  { font-size: 0.78rem; color: #94A3B8; margin-top: 4px; }
  .kpi-label{ font-size: 0.9rem;  color: #CBD5E1; margin-bottom: 6px; }

  /* ---- section headers ---- */
  .section-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: #38BDF8;
    border-left: 4px solid #38BDF8;
    padding-left: 10px;
    margin: 24px 0 10px 0;
  }

  /* ---- chart containers ---- */
  [data-testid="stImage"] {
    border-radius: 10px;
    overflow: hidden;
  }

  /* ---- buttons ---- */
  div.stButton > button {
    background: #2563EB;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 600;
    width: 100%;
  }
  div.stButton > button:hover { background: #1D4ED8; }

  /* ---- tabs ---- */
  .stTabs [data-baseweb="tab-list"] { background: #1E293B; border-radius: 8px; }
  .stTabs [data-baseweb="tab"]      { color: #94A3B8 !important; }
  .stTabs [aria-selected="true"]    { color: #38BDF8 !important; border-bottom: 2px solid #38BDF8; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ════════════════════════════════════════════════════════════════════════════

df_raw = load_data()

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR — FILTERS
# ════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.image("https://ember-climate.org/wp-content/uploads/2021/03/Ember-logo-1.png",
             use_container_width=True)
    st.markdown("## ⚡ Ember Electricity")
    st.markdown("*Country-level annual electricity mix & emissions from Ember Climate*")
    st.divider()

    # ── Year range ───────────────────────────────────────────────────────────
    yr_min, yr_max = get_year_range(df_raw)
    year_range = st.slider(
        "📅 Year Range",
        min_value=yr_min, max_value=yr_max,
        value=(yr_min, yr_max), step=1,
    )

    # ── Country multi-select ─────────────────────────────────────────────────
    all_countries = get_countries(df_raw)
    default_countries = ["Germany", "France", "Poland", "Norway", "Spain",
                         "United Kingdom", "Italy", "Sweden"]
    default_countries = [c for c in default_countries if c in all_countries]

    selected_countries = st.multiselect(
        "🌍 Countries",
        options=all_countries,
        default=default_countries,
    )

    # ── Category filter ──────────────────────────────────────────────────────
    all_categories = get_categories(df_raw)
    selected_categories = st.multiselect(
        "📂 Data Category",
        options=all_categories,
        default=all_categories,
    )

    # ── Variable filter ──────────────────────────────────────────────────────
    all_variables = get_variables(df_raw)
    selected_variables = st.multiselect(
        "📊 Variables",
        options=all_variables,
        default=all_variables,
    )

    # ── Search / text filter ─────────────────────────────────────────────────
    search_text = st.text_input("🔍 Search (keyword in any column)", value="")

    st.divider()

    # ── Single-year picker (used by several charts) ──────────────────────────
    selected_year = st.select_slider(
        "📆 Single Year (for cross-country charts)",
        options=list(range(yr_min, yr_max + 1)),
        value=min(2022, yr_max),
    )

    # ── Pie chart country ────────────────────────────────────────────────────
    pie_country = st.selectbox(
        "🥧 Country for Pie Chart",
        options=all_countries,
        index=all_countries.index("Germany") if "Germany" in all_countries else 0,
    )

    st.divider()

    # ── Reset button ─────────────────────────────────────────────────────────
    if st.button("🔄 Reset All Filters"):
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# APPLY FILTERS
# ════════════════════════════════════════════════════════════════════════════

filtered_df = apply_filters(
    df_raw,
    countries=selected_countries,
    year_range=year_range,
    categories=selected_categories,
    variables=selected_variables,
    search_text=search_text,
)


# ════════════════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style='text-align:center; padding: 20px 0 10px 0;'>
  <h1 style='font-size:2.4rem; color:#38BDF8; font-weight:800; letter-spacing:-0.5px;'>
    ⚡ Ember Yearly Electricity Dashboard
  </h1>
  <p style='color:#94A3B8; font-size:1rem; margin-top:-8px;'>
    Country-level annual electricity mix and emissions intensity · Source: Ember Climate
  </p>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# KPI SUMMARY CARDS
# ════════════════════════════════════════════════════════════════════════════

kpis = compute_kpis(df_raw, filtered_df)

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class='kpi-card'>
      <div class='kpi-label'>📄 Total Records</div>
      <div class='kpi-val'>{kpis['total_records']:,}</div>
      <div class='kpi-sub'>Filtered dataset rows</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class='kpi-card'>
      <div class='kpi-label'>📅 Latest Year</div>
      <div class='kpi-val'>{kpis['latest_year']}</div>
      <div class='kpi-sub'>Most recent data point</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class='kpi-card'>
      <div class='kpi-label'>💨 Avg CO₂ Intensity</div>
      <div class='kpi-val'>{kpis['avg_co2_intensity']}</div>
      <div class='kpi-sub'>gCO₂e / kWh (filtered)</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class='kpi-card'>
      <div class='kpi-label'>🌿 Top Renewables</div>
      <div class='kpi-val'>{kpis['top_ren_val']}%</div>
      <div class='kpi-sub'>{kpis['top_ren_country']}</div>
    </div>""", unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class='kpi-card'>
      <div class='kpi-label'>🏭 Highest CO₂</div>
      <div class='kpi-val'>{kpis['top_co2_val']}</div>
      <div class='kpi-sub'>{kpis['top_co2_country']} (gCO₂e/kWh)</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════

tabs = st.tabs([
    "🥧 Energy Mix",
    "📈 Trends",
    "🏆 Country Compare",
    "🔬 Deep Analysis",
    "🎯 Bonus",
    "🗂️ Raw Data",
])


# ── TAB 1: Energy Mix ────────────────────────────────────────────────────────
with tabs[0]:
    st.markdown("<div class='section-header'>Energy Generation Mix</div>",
                unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f"**🥧 Pie Chart — {pie_country} ({selected_year})**")
        fig = chart_pie(filtered_df, pie_country, selected_year)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Proportional electricity generation mix for the selected country and year.")

    with col2:
        st.markdown(f"**📊 Count Plot — Records by Category**")
        fig = chart_count(filtered_df)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Number of data records per electricity data category in the filtered dataset.")

    st.divider()
    st.markdown("<div class='section-header'>CO₂ Intensity Distribution</div>",
                unsafe_allow_html=True)
    fig = chart_histogram(filtered_df)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Frequency distribution of CO₂ intensity (gCO₂e/kWh) across all countries and years.")


# ── TAB 2: Trends ────────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown("<div class='section-header'>Time-Series Trends</div>",
                unsafe_allow_html=True)

    line_var = st.selectbox(
        "Variable for Line/Area Chart",
        options=[v for v in all_variables if v in filtered_df["Variable"].unique()],
        index=0, key="line_var",
    )

    line_countries = st.multiselect(
        "Countries to display",
        options=selected_countries if selected_countries else all_countries,
        default=(selected_countries if selected_countries else all_countries)[:6],
        key="line_countries",
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**📈 Line Chart — Trend Over Time**")
        fig = chart_line(filtered_df, line_countries, line_var)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Year-by-year trend for the selected variable and countries.")

    with col2:
        st.markdown("**🌊 Area Chart — Cumulative Share**")
        fig = chart_area(filtered_df, line_countries, "Renewables")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Renewables share over time (area = overlapping, non-stacked for easy reading).")


# ── TAB 3: Country Compare ───────────────────────────────────────────────────
with tabs[2]:
    st.markdown("<div class='section-header'>Cross-Country Comparison</div>",
                unsafe_allow_html=True)

    bar_var = st.selectbox(
        "Variable for Bar Chart",
        options=[v for v in ["CO2 intensity", "Renewables", "Demand",
                              "Solar", "Wind", "Nuclear", "Fossil"]
                 if v in filtered_df["Variable"].unique()],
        index=0, key="bar_var",
    )
    top_n = st.slider("Top N countries", 5, 35, 15, key="top_n")

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown(f"**📊 Bar Chart — {bar_var} ({selected_year})**")
        fig = chart_bar(filtered_df, bar_var, selected_year, top_n)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Horizontal bar chart ranking countries by the selected variable.")

    with col2:
        st.markdown(f"**📦 Box Plot — EU vs Non-EU**")
        fig = chart_box(filtered_df, bar_var)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Spread and outliers of the variable for EU vs Non-EU countries.")


# ── TAB 4: Deep Analysis ─────────────────────────────────────────────────────
with tabs[3]:
    st.markdown("<div class='section-header'>Statistical Deep Dive</div>",
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**🔵 Scatter Plot — Renewables vs CO₂ ({selected_year})**")
        fig = chart_scatter(filtered_df, selected_year)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Each point is a country. Trend line shows inverse correlation.")

    with col2:
        st.markdown(f"**🎻 Violin Plot — Distribution by Decade**")
        violin_var = st.selectbox(
            "Variable for Violin",
            options=["CO2 intensity", "Renewables", "Solar", "Wind", "Fossil"],
            key="vio_var",
        )
        fig = chart_violin(filtered_df, violin_var)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Distribution shape and probability density across decades.")

    st.divider()
    st.markdown(f"<div class='section-header'>Heatmap — Correlation Matrix ({selected_year})</div>",
                unsafe_allow_html=True)
    fig = chart_heatmap(filtered_df, selected_year)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Pearson correlation between key electricity variables across European countries.")


# ── TAB 5: Bonus ─────────────────────────────────────────────────────────────
with tabs[4]:
    st.markdown("<div class='section-header'>🎯 Bonus — Bubble Chart</div>",
                unsafe_allow_html=True)
    st.markdown(f"**Renewables (x) · CO₂ Intensity (y) · Bubble Size = Demand — [{selected_year}]**")
    fig = chart_bubble(filtered_df, selected_year)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Bubble size represents total electricity demand (TWh). "
        "Color scale: red = high CO₂, green = low CO₂. "
        "Countries toward top-left have high fossil dependence; bottom-right = clean & high-renewable."
    )

    st.divider()
    st.markdown("### 📌 Key Insights")
    col1, col2 = st.columns(2)
    with col1:
        st.info(
            "🌿 **Renewables Growth**: Nordic countries (Norway, Sweden) have maintained "
            ">70% renewables for decades, driven by hydroelectric resources. "
            "Southern Europe (Spain, Portugal) saw rapid solar growth post-2015."
        )
        st.info(
            "💨 **Wind Revolution**: The UK and Denmark lead offshore wind, dramatically "
            "cutting CO₂ intensity since 2010."
        )
    with col2:
        st.warning(
            "🏭 **Coal Dependency**: Poland and Kosovo consistently show the highest "
            "CO₂ intensity in Europe, reflecting heavy coal dependence."
        )
        st.success(
            "⚡ **Decarbonization Trend**: EU aggregate CO₂ intensity dropped by over 40% "
            "between 1990 and 2023, the fastest rate of power sector decarbonisation globally."
        )


# ── TAB 6: Raw Data ──────────────────────────────────────────────────────────
with tabs[5]:
    st.markdown("<div class='section-header'>🗂️ Filtered Raw Data</div>",
                unsafe_allow_html=True)

    st.markdown(f"**{len(filtered_df):,} rows · {filtered_df.shape[1]} columns** — based on current filters")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows (filtered)", f"{len(filtered_df):,}")
    with col2:
        st.metric("Countries", filtered_df["Area"].nunique())
    with col3:
        st.metric("Year span", f"{int(filtered_df['Year'].min())}–{int(filtered_df['Year'].max())}"
                  if not filtered_df.empty else "N/A")

    st.dataframe(
        filtered_df.sort_values(["Area", "Year"]).head(2000),
        use_container_width=True,
        height=450,
    )
    st.caption("Showing up to 2,000 rows. Apply filters to narrow results.")

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Filtered CSV",
        data=csv_data,
        file_name="ember_electricity_filtered.csv",
        mime="text/csv",
    )


# ── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style='text-align:center; color:#475569; font-size:0.8rem; padding: 10px 0;'>
  ⚡ Ember Yearly Electricity Dashboard &nbsp;|&nbsp;
  Data: Ember Climate &nbsp;|&nbsp;
  Built with Streamlit · Pandas · Plotly &nbsp;|&nbsp;
  EDA Course Project
</div>
""", unsafe_allow_html=True)
