"""
app.py — Ember Yearly Electricity Dashboard
Gradio-based EDA application (no Streamlit).

Run with:  python app.py
"""

import warnings
warnings.filterwarnings("ignore")

import io
import pandas as pd
import gradio as gr

from filters import load_data, apply_filters, compute_kpis, get_countries, \
    get_year_range, get_variables, get_categories
from charts import (
    chart_pie, chart_histogram, chart_line, chart_bar,
    chart_scatter, chart_box, chart_heatmap, chart_area,
    chart_count, chart_violin, chart_bubble,
)

# ── Load data once ────────────────────────────────────────────────────────────
df_raw = load_data()
all_countries  = get_countries(df_raw)
yr_min, yr_max = get_year_range(df_raw)
all_variables  = get_variables(df_raw)
all_categories = get_categories(df_raw)

DEFAULT_COUNTRIES = [c for c in
    ["Germany","France","Poland","Norway","Spain","United Kingdom","Italy","Sweden"]
    if c in all_countries]
DEFAULT_YEAR      = min(2022, yr_max)


# ── Helper ────────────────────────────────────────────────────────────────────

def _filter(countries, year_min, year_max, categories, variables, search):
    return apply_filters(
        df_raw,
        countries=countries,
        year_range=(int(year_min), int(year_max)),
        categories=categories,
        variables=variables,
        search_text=search,
    )


def _kpi_html(kpis):
    def card(label, val, sub):
        return f"""
        <div class='kpi-card'>
          <div class='kpi-label'>{label}</div>
          <div class='kpi-val'>{val}</div>
          <div class='kpi-sub'>{sub}</div>
        </div>"""
    return (
        "<div class='kpi-row'>"
        + card("📄 Total Records",   f"{kpis['total_records']:,}", "Filtered dataset rows")
        + card("📅 Latest Year",      kpis['latest_year'],          "Most recent data point")
        + card("💨 Avg CO₂ Intensity",kpis['avg_co2_intensity'],    "gCO₂e / kWh (filtered)")
        + card(f"🌿 Top Renewables",  f"{kpis['top_ren_val']}%",   kpis['top_ren_country'])
        + card("🏭 Highest CO₂",      kpis['top_co2_val'],          f"{kpis['top_co2_country']} (gCO₂e/kWh)")
        + "</div>"
    )


KPI_CSS = """
<style>
  .kpi-row  { display:flex; gap:12px; flex-wrap:wrap; margin-bottom:10px; }
  .kpi-card {
    flex:1; min-width:140px;
    background:linear-gradient(135deg,#1E293B 0%,#0F172A 100%);
    border:1px solid #334155; border-radius:12px;
    padding:14px 16px; text-align:center;
    box-shadow:0 4px 15px rgba(0,0,0,.3);
  }
  .kpi-val   { font-size:1.7rem; font-weight:700; color:#38BDF8; }
  .kpi-sub   { font-size:.75rem; color:#94A3B8; margin-top:4px; }
  .kpi-label { font-size:.85rem; color:#CBD5E1; margin-bottom:6px; }
</style>
"""


# ── Tab renderers ─────────────────────────────────────────────────────────────

def render_energy_mix(countries, year_min, year_max, categories, variables,
                      search, pie_country, selected_year):
    df = _filter(countries, year_min, year_max, categories, variables, search)
    kpis = compute_kpis(df_raw, df)
    kpi_html = KPI_CSS + _kpi_html(kpis)
    fig_pie  = chart_pie(df, pie_country, int(selected_year))
    fig_cnt  = chart_count(df)
    fig_hist = chart_histogram(df)
    return kpi_html, fig_pie, fig_cnt, fig_hist


def render_trends(countries, year_min, year_max, categories, variables,
                  search, line_var, line_countries):
    df = _filter(countries, year_min, year_max, categories, variables, search)
    if not line_countries:
        line_countries = countries[:6] if countries else all_countries[:6]
    fig_line = chart_line(df, line_countries, line_var)
    fig_area = chart_area(df, line_countries, "Renewables")
    return fig_line, fig_area


def render_compare(countries, year_min, year_max, categories, variables,
                   search, bar_var, top_n, selected_year):
    df = _filter(countries, year_min, year_max, categories, variables, search)
    fig_bar = chart_bar(df, bar_var, int(selected_year), int(top_n))
    fig_box = chart_box(df, bar_var)
    return fig_bar, fig_box


def render_deep(countries, year_min, year_max, categories, variables,
                search, violin_var, selected_year):
    df = _filter(countries, year_min, year_max, categories, variables, search)
    fig_sc  = chart_scatter(df, int(selected_year))
    fig_vio = chart_violin(df, violin_var)
    fig_hm  = chart_heatmap(df, int(selected_year))
    return fig_sc, fig_vio, fig_hm


def render_bonus(countries, year_min, year_max, categories, variables,
                 search, selected_year):
    df = _filter(countries, year_min, year_max, categories, variables, search)
    fig_bub = chart_bubble(df, int(selected_year))
    return fig_bub


def render_raw(countries, year_min, year_max, categories, variables,
               search):
    df = _filter(countries, year_min, year_max, categories, variables, search)
    preview = df.sort_values(["Area","Year"]).head(2000)
    return preview


def download_csv(countries, year_min, year_max, categories, variables, search):
    df = _filter(countries, year_min, year_max, categories, variables, search)
    path = "/tmp/ember_electricity_filtered.csv"
    df.to_csv(path, index=False)
    return path


# ── Gradio UI ─────────────────────────────────────────────────────────────────

DARK_THEME = gr.themes.Base(
    primary_hue="sky",
    secondary_hue="slate",
    neutral_hue="slate",
).set(
    body_background_fill="#0F172A",
    body_text_color="#F1F5F9",
    block_background_fill="#1E293B",
    block_border_color="#334155",
    input_background_fill="#0F172A",
    input_border_color="#334155",
)

with gr.Blocks(theme=DARK_THEME, title="⚡ Ember Electricity Dashboard") as demo:

    gr.Markdown("""
    <h1 style='text-align:center;color:#38BDF8;font-size:2rem;'>
      ⚡ Ember Yearly Electricity Dashboard
    </h1>
    <p style='text-align:center;color:#94A3B8;'>
      Country-level annual electricity mix and emissions intensity · Source: Ember Climate
    </p>
    """)

    # ── Global sidebar-style filters (Accordion at top) ───────────────────────
    with gr.Accordion("🔧 Filters", open=True):
        with gr.Row():
            sel_countries  = gr.Dropdown(all_countries, value=DEFAULT_COUNTRIES,
                                         multiselect=True, label="🌍 Countries")
            sel_categories = gr.Dropdown(all_categories, value=all_categories,
                                         multiselect=True, label="📂 Category")
            sel_variables  = gr.Dropdown(all_variables, value=all_variables,
                                         multiselect=True, label="📊 Variables")
        with gr.Row():
            sel_year_min = gr.Slider(yr_min, yr_max, value=yr_min, step=1,
                                     label="📅 Year From")
            sel_year_max = gr.Slider(yr_min, yr_max, value=yr_max, step=1,
                                     label="📅 Year To")
            sel_search   = gr.Textbox(value="", label="🔍 Keyword Search")
        with gr.Row():
            sel_year     = gr.Slider(yr_min, yr_max, value=DEFAULT_YEAR, step=1,
                                     label="📆 Single Year (cross-country charts)")
            sel_pie_ctry = gr.Dropdown(all_countries, value="Germany",
                                       label="🥧 Country for Pie Chart")

    filter_inputs = [sel_countries, sel_year_min, sel_year_max,
                     sel_categories, sel_variables, sel_search]

    # ── Tabs ──────────────────────────────────────────────────────────────────
    with gr.Tabs():

        # Tab 1 — Energy Mix
        with gr.Tab("🥧 Energy Mix"):
            kpi_out  = gr.HTML()
            with gr.Row():
                pie_out = gr.Plot(label="Pie Chart — Energy Mix")
                cnt_out = gr.Plot(label="Count Plot — Records by Category")
            hist_out = gr.Plot(label="CO₂ Intensity Distribution")

            mix_btn = gr.Button("▶ Render Energy Mix", variant="primary")
            mix_btn.click(
                render_energy_mix,
                inputs=filter_inputs + [sel_pie_ctry, sel_year],
                outputs=[kpi_out, pie_out, cnt_out, hist_out],
            )

        # Tab 2 — Trends
        with gr.Tab("📈 Trends"):
            with gr.Row():
                line_var_dd = gr.Dropdown(all_variables, value=all_variables[0],
                                          label="Variable for Line/Area Chart")
                line_ctry   = gr.Dropdown(all_countries, value=DEFAULT_COUNTRIES[:6],
                                          multiselect=True, label="Countries to display")
            with gr.Row():
                line_out = gr.Plot(label="Line Chart — Trend Over Time")
                area_out = gr.Plot(label="Area Chart — Renewables Share")

            trend_btn = gr.Button("▶ Render Trends", variant="primary")
            trend_btn.click(
                render_trends,
                inputs=filter_inputs + [line_var_dd, line_ctry],
                outputs=[line_out, area_out],
            )

        # Tab 3 — Country Compare
        with gr.Tab("🏆 Country Compare"):
            with gr.Row():
                bar_var_dd = gr.Dropdown(
                    [v for v in ["CO2 intensity","Renewables","Demand","Solar",
                                 "Wind","Nuclear","Fossil"] if v in all_variables],
                    value="CO2 intensity", label="Variable for Bar Chart")
                top_n_sl   = gr.Slider(5, 35, value=15, step=1, label="Top N Countries")
            with gr.Row():
                bar_out = gr.Plot(label="Bar Chart")
                box_out = gr.Plot(label="Box Plot — EU vs Non-EU")

            cmp_btn = gr.Button("▶ Render Comparison", variant="primary")
            cmp_btn.click(
                render_compare,
                inputs=filter_inputs + [bar_var_dd, top_n_sl, sel_year],
                outputs=[bar_out, box_out],
            )

        # Tab 4 — Deep Analysis
        with gr.Tab("🔬 Deep Analysis"):
            violin_var_dd = gr.Dropdown(
                ["CO2 intensity","Renewables","Solar","Wind","Fossil"],
                value="CO2 intensity", label="Variable for Violin Plot")
            with gr.Row():
                sc_out  = gr.Plot(label="Scatter — Renewables vs CO₂")
                vio_out = gr.Plot(label="Violin — Distribution by Decade")
            hm_out = gr.Plot(label="Heatmap — Correlation Matrix")

            deep_btn = gr.Button("▶ Render Deep Analysis", variant="primary")
            deep_btn.click(
                render_deep,
                inputs=filter_inputs + [violin_var_dd, sel_year],
                outputs=[sc_out, vio_out, hm_out],
            )

        # Tab 5 — Bonus
        with gr.Tab("🎯 Bonus"):
            bub_out = gr.Plot(label="Bubble Chart — Renewables vs CO₂ (size = Demand)")
            bonus_btn = gr.Button("▶ Render Bubble Chart", variant="primary")
            bonus_btn.click(
                render_bonus,
                inputs=filter_inputs + [sel_year],
                outputs=[bub_out],
            )
            gr.Markdown("""
### 📌 Key Insights
- 🌿 **Renewables Growth**: Nordic countries (Norway, Sweden) have maintained >70% renewables for decades. Southern Europe saw rapid solar growth post-2015.
- 💨 **Wind Revolution**: The UK and Denmark lead offshore wind, dramatically cutting CO₂ intensity since 2010.
- 🏭 **Coal Dependency**: Poland and Kosovo consistently show the highest CO₂ intensity in Europe.
- ⚡ **Decarbonization Trend**: EU aggregate CO₂ intensity dropped by over 40% between 1990 and 2023.
            """)

        # Tab 6 — Raw Data
        with gr.Tab("🗂️ Raw Data"):
            raw_table = gr.Dataframe(label="Filtered Dataset (up to 2,000 rows)",
                                     interactive=False, wrap=False)
            with gr.Row():
                raw_btn  = gr.Button("▶ Load Table", variant="primary")
                dl_btn   = gr.Button("⬇️ Download CSV")
            dl_file = gr.File(label="Download")

            raw_btn.click(render_raw, inputs=filter_inputs, outputs=[raw_table])
            dl_btn.click(download_csv, inputs=filter_inputs, outputs=[dl_file])

    gr.Markdown("""
    <p style='text-align:center;color:#475569;font-size:.8rem;margin-top:12px;'>
      ⚡ Ember Yearly Electricity Dashboard &nbsp;|&nbsp;
      Data: Ember Climate &nbsp;|&nbsp;
      Built with Gradio · Pandas · Matplotlib · Seaborn &nbsp;|&nbsp;
      EDA Course Project
    </p>
    """)


if __name__ == "__main__":
    demo.launch()
