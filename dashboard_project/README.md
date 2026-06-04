# ⚡ Ember Yearly Electricity Dashboard

**Course:** Exploratory Data Analysis  
**Instructor:** Ali Hassan Sherazi  
**Submission Date:** 05-June-2026  
**Dataset:** `europe_yearly_full_release_long_format.csv`  
**Topic:** Country-level annual electricity mix and emissions intensity from Ember Climate

---

## 📂 Project Structure

```
dashboard_project/
├── data/
│   └── europe_yearly_full_release_long_format.csv   ← Original dataset (DO NOT rename)
├── notebooks/
│   └── analysis.ipynb                               ← Exploratory Data Analysis
├── app.py                                           ← Main Streamlit dashboard
├── charts.py                                        ← All 10+ chart functions
├── filters.py                                       ← Data loading, cleaning & filters
├── requirements.txt                                 ← Python dependencies
└── README.md                                        ← This file
```

---

## 🚀 Installation & Running

### 1. Clone / unzip the project folder

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the dashboard
```bash
streamlit run app.py
```

The dashboard opens automatically in your browser at `http://localhost:8501`.

### 4. Run the EDA notebook
```bash
cd notebooks
jupyter notebook analysis.ipynb
```

---

## 🗂️ Dataset Overview

| Feature | Details |
|---|---|
| Source | Ember Climate |
| File | `europe_yearly_full_release_long_format.csv` |
| Shape | 69,348 rows × 18 columns |
| Countries | 38 European countries + EU aggregate |
| Year range | 1990 – 2025 |
| Categories | Electricity demand, generation, imports, power sector emissions |
| Key variables | CO2 intensity, Renewables, Solar, Wind, Hydro, Nuclear, Coal, Gas, Fossil, Demand |
| Units | TWh, MWh, %, MtCO2e, gCO2e/kWh |

---

## 📊 Charts Implemented

| # | Chart Type | Purpose |
|---|---|---|
| 1 | **Pie Chart** | Energy generation mix for a selected country & year |
| 2 | **Histogram** | Frequency distribution of CO₂ intensity |
| 3 | **Line Chart** | Variable trend over time for selected countries |
| 4 | **Bar Chart** | Cross-country comparison of any variable in a given year |
| 5 | **Scatter Plot** | Renewables % vs CO₂ intensity with trend line |
| 6 | **Box Plot** | EU vs Non-EU distribution of any variable |
| 7 | **Heatmap** | Correlation matrix of key electricity variables |
| 8 | **Area Chart** | Renewables share over time (multi-country) |
| 9 | **Count Plot** | Record count by data category |
| 10 | **Violin Plot** | Variable distribution by decade |
| ★ | **Bubble Chart** *(Bonus)* | Renewables × CO₂ × Demand in one view |

---

## 🎛️ Filters Implemented

| Filter | Type | Effect |
|---|---|---|
| Year Range | Slider | Limits all charts to selected year span |
| Countries | Multi-select | Filters by one or more countries |
| Data Category | Multi-select | Limits to selected Ember categories |
| Variables | Multi-select | Limits to chosen electricity variables |
| Search | Text input | Keyword search across Area, Variable, Category |
| Single Year | Slider | Picks year for cross-country charts |
| Pie country | Dropdown | Selects country for the Pie Chart |
| Reset | Button | Reruns app to restore defaults |

All filters are connected — every chart updates dynamically when any filter changes.

---

## 💡 Key Insights

1. **Norway, Switzerland, Sweden** consistently show the lowest CO₂ intensity in Europe (<50 gCO₂e/kWh) due to dominant hydroelectric and nuclear generation.

2. **Kosovo and Poland** carry the heaviest coal burden, with CO₂ intensity exceeding 690 gCO₂e/kWh — more than 20× Norway's figure.

3. **EU aggregate CO₂ intensity** fell by over 40% between 1990 and 2023, the fastest power-sector decarbonisation in the world.

4. **Solar growth** accelerated sharply post-2015 across Spain, Italy, Greece and Germany, explaining a kink in the Renewables trend line.

5. **Strong negative correlation** (≈ −0.85) between Renewables share and CO₂ intensity — visible in both the Scatter Plot and Heatmap.

---

## 🛠️ Technical Stack

| Tool | Role |
|---|---|
| Python 3.x | Core language |
| Pandas | Data loading, cleaning, filtering, aggregation |
| NumPy | Numerical operations |
| Matplotlib | Core chart creation |
| Seaborn | Statistical visualisations (box, violin, heatmap, count) |
| Streamlit | Interactive dashboard frontend |

---

## ⚠️ Important Notes

- **Do NOT rename** the dataset file.
- All charts respond to the sidebar filters simultaneously.
- The dashboard is designed for **dark mode** — best viewed in a modern browser.
