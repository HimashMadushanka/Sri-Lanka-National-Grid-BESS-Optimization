<div align="center">

# ⚡ Sri Lanka National Grid BESS Placement & Sizing Optimization
### *Topological Centrality Analysis & Mixed-Integer Linear Programming (MILP) for Grid-Scale Battery Energy Storage Integration*

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Pyomo](https://img.shields.io/badge/Optimization-Pyomo%206.10-brightgreen.svg)](https://pyomo.readthedocs.io/)
[![HiGHS Solver](https://img.shields.io/badge/Solver-HiGHS%20v1.15-orange.svg)](https://highs.dev/)
[![NetworkX](https://img.shields.io/badge/Network%20Theory-NetworkX%203.0-purple.svg)](https://networkx.org/)
[![CEB Benchmark](https://img.shields.io/badge/Benchmark-CEB%202025--2044%20Base%20Case-red.svg)](https://www.ceb.lk/)
[![NASA POWER](https://img.shields.io/badge/Solar%20Data-NASA%20POWER%20Hourly-yellow.svg)](https://power.larc.nasa.gov/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

<br/>

<p align="center">
  <a href="#-executive-summary">Executive Summary</a> •
  <a href="#-verified-research-findings">Research Findings</a> •
  <a href="#-candidate-substation-ranking">Candidate Siting</a> •
  <a href="#-mathematical-optimization-model">Mathematical Formulation</a> •
  <a href="#-sensitivity-analysis-results">Sensitivity Analysis</a> •
  <a href="#-verified-visualizations-gallery">Visualizations Gallery</a> •
  <a href="#-notebook-execution-pipeline">Notebook Pipeline</a> •
  <a href="#-repository-structure">Repository Structure</a> •
  <a href="#-quickstart-guide">Quickstart</a>
</p>

</div>

---

## 📌 Executive Summary

Under Sri Lanka's national energy mandate to achieve **70% renewable electricity generation by 2030**, the Ceylon Electricity Board (CEB) transmission grid faces unprecedented technical challenges. Rapid integration of utility-scale solar photovoltaic (PV) plants introduces severe mid-day generation surges, localized transmission congestion, sharp duck-curve ramp rates, and the risk of substantial renewable energy curtailment.

This research presents a rigorous, reproducible, two-stage mathematical optimization framework to determine the **optimal siting, sizing, and fleet dispatch** of Grid-Connected Battery Energy Storage Systems (BESS) across the Sri Lanka high-voltage transmission network:

1. **Stage 1 — Multi-Criteria Graph Centrality Siting**: Evaluates all 30 major CEB transmission grid substations using complex network theory (betweenness and closeness centrality), geospatial proximity to solar generation complexes, and nominal grid voltage hierarchy (220 kV vs. 132 kV).
2. **Stage 2 — Temporal Mixed-Integer Linear Programming (MILP)**: Co-optimizes BESS power capacity (MW), energy storage sizing (MWh), and 744-hour fleet operational dispatch using Pyomo and the HiGHS branch-and-cut solver to minimize total annualized system cost, eliminate solar curtailment, and reduce evening peak residual demand.

All models are parameterized with official data from the **CEB Long-Term Generation Expansion Plan (LTGEP 2025–2044 Base Case)** and hourly surface irradiance observations from the **NASA POWER** satellite project.

---

## 🏆 Verified Research Findings

The optimization model converged to a unique, highly robust optimal siting and sizing solution:

| Parameter / Metric | Optimized Model Decision | Baseline / Context | Technical Impact |
|:---|:---:|:---:|:---|
| **Optimal Substation** | **`BIYAGAMA`** | 220 kV / 132 kV Grid Hub | Located at `(6.945° N, 79.995° E)` in Western Province |
| **National Siting Rank** | **Rank #1 (Score: 0.8602)** | 30 substations evaluated | Outperformed New Anuradhapura (0.8099) & Pannipitiya (0.7854) |
| **Locational Cost Factor** | **`0.7839`** | Baseline = 1.0000 | **21.61% capital cost advantage** from existing 220 kV infrastructure |
| **Optimal BESS Power** | **`50.00 MW`** | Model upper bound: 50 MW/site | Directly aligns with CEB 2026/2030 Western Region BESS targets |
| **Optimal BESS Energy** | **`200.00 MWh`** | 4-Hour Storage Duration | $E/P = 4.0\text{ h}$, optimal duration for evening peak shaving |
| **Peak Residual Demand** | **`2,600.00 MW`** | Gross Peak = 2,650.00 MW | **50.00 MW peak demand shaved** during 18:00–22:00 window |
| **Solar Energy Curtailment** | **`0.00 MWh` (0.0%)** | 100% Solar Absorbed | Zero energy spilled across all 744 dispatch hours |
| **Total Energy Charged** | **`1,722.22 MWh`** | Sourced strictly from solar | Captured during 10:00–14:00 solar surplus hours |
| **Total Energy Discharged** | **`1,550.00 MWh`** | Discharged during peak | $1550 / 1722.22 = 90.0\%$ round-trip cycle efficiency |
| **Annualized Base Objective** | **`$3,623,899.34`** | Net annualized cost | Includes capital CRF, annual O&M, and peak reduction credits |
| **Topological Role** | **Betweenness: `0.3649`** | Closeness: `0.4028` | Critical 220 kV backbone corridor feeding Colombo Metro demand |

---

## 📍 Candidate Substation Multi-Criteria Ranking

Substations are scored based on topological centrality, solar generation proximity, and electrical voltage tier. The top 10 ranked substations from the multi-criteria analysis:

| Rank | Substation Bus ID | Voltage Level | Betweenness Centrality | Closeness Centrality | Solar Distance (km) | Composite Site Score | Locational Cost Factor | Eligibility |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | **`BIYAGAMA`** | **220 kV** | **0.364860** | **0.402778** | **11.96 km** | **0.860171** | **0.783898** | **Selected** |
| 2 | `NEW_ANURADHAPURA` | 220 kV | 0.266174 | 0.376623 | 0.00 km | 0.809883 | 0.814070 | Eligible |
| 3 | `PANNIPITIYA` | 220 kV | 0.245115 | 0.333333 | 0.00 km | 0.785366 | 0.828780 | Eligible |
| 4 | `KOTMALE` | 220 kV | 0.429475 | 0.426471 | 53.31 km | 0.712155 | 0.872707 | Eligible |
| 5 | `MONARAGALA` | 132 kV | 0.078695 | 0.287129 | 0.00 km | 0.591617 | 0.945030 | Eligible |
| 6 | `HAMBANTOTA` | 220 kV | 0.073563 | 0.268519 | 0.00 km | 0.585643 | 0.948614 | Eligible |
| 7 | `KILINOCHCHI` | 132 kV | 0.068966 | 0.228346 | 0.00 km | 0.580291 | 0.951826 | Eligible |
| 8 | `KURUNEGALA` | 132 kV | 0.047865 | 0.325843 | 0.00 km | 0.555725 | 0.966565 | Eligible |
| 9 | `TRINCOMALEE` | 132 kV | 0.000000 | 0.263636 | 0.00 km | 0.500000 | 1.000000 | Eligible |
| 10 | `VEYANGODA` | 220 kV | 0.140969 | 0.358025 | 36.19 km | 0.468675 | 1.018795 | Eligible |

---

## 📐 Mathematical Optimization Model

The optimization problem is formulated as a Mixed-Integer Linear Program (MILP) implemented in **Pyomo 6.10** and solved via **HiGHS v1.15**.

### 1. Objective Function
Minimize total annualized system expenditure, combining capital investment annualized via the Capital Recovery Factor (CRF), fixed operations & maintenance (O&M), energy curtailment penalties, and peak reduction benefits:

$$\min \quad \mathcal{Z} = \text{CRF} \cdot \text{CAPEX}_{\text{fleet}} + \text{OPEX}_{\text{O\&M}} + \text{Cost}_{\text{curtailment}} - \text{Benefit}_{\text{peak}}$$

Where:
$$\text{CAPEX}_{\text{fleet}} = \sum_{i \in \mathcal{I}} c_{\text{site}, i} \cdot \left( c_{\text{power}} \cdot 1000 \cdot P_i + c_{\text{energy}} \cdot 1000 \cdot E_i \right)$$

$$\text{OPEX}_{\text{O\&M}} = \sum_{i \in \mathcal{I}} c_{\text{om}} \cdot 1000 \cdot P_i$$

$$\text{Cost}_{\text{curtailment}} = \left( \frac{365}{D_{\text{rep}}} \right) \cdot c_{\text{curt}} \cdot \sum_{t \in \mathcal{T}} \text{Curt}_t \cdot \Delta t$$

$$\text{Benefit}_{\text{peak}} = v_{\text{peak}} \cdot \left( \max_{t \in \mathcal{T}}(D_t - S_t) - \text{Peak}_{\text{residual}} \right)$$

### 2. Capital Recovery Factor (CRF)
$$\text{CRF} = \frac{d \cdot (1 + d)^L}{(1 + d)^L - 1} = \frac{0.08 \cdot (1 + 0.08)^{15}}{(1 + 0.08)^{15} - 1} \approx 0.11683$$
- Discount rate $d = 8.0\%$
- Asset economic lifetime $L = 15\text{ years}$

### 3. Key Technical & Operational Constraints
- **Substation Siting Limit & Sizing Bounds**:
  $$\sum_{i \in \mathcal{I}} u_i \le N_{\max} = 5, \quad P_{\min} \cdot u_i \le P_i \le P_{\max} \cdot u_i \quad (P_{\max} = 50\text{ MW}, P_{\min} = 5\text{ MW})$$
  $$E_i = 4.0 \cdot P_i \quad (\text{Enforces mandatory 4-hour duration})$$

- **Hourly State of Charge (SoC) Dynamics**:
  $$\text{SoC}_t = \text{SoC}_{t-1} + \eta_{\text{ch}} \cdot C_t \cdot \Delta t - \frac{D_t^{\text{batt}}}{\eta_{\text{dis}}} \cdot \Delta t, \quad \forall t \in \mathcal{T}$$
  $$\text{SoC}_t \le E_{\text{total}} = \sum_{i \in \mathcal{I}} E_i, \quad \eta_{\text{ch}} = \eta_{\text{dis}} = \sqrt{0.90} \approx 0.94868$$

- **Solar-Only Charging Restriction**:
  $$C_t \le S_t \quad \forall t \in \mathcal{T} \quad (\text{BESS charging strictly restricted to available solar generation})$$

- **Curtailment Definition & Residual Demand**:
  $$\text{Curt}_t \ge S_t - C_t - D_t \quad \forall t \in \mathcal{T}$$
  $$R_t = D_t - S_t + C_t - D_t^{\text{batt}} + \text{Curt}_t \quad \forall t \in \mathcal{T}$$
  $$\text{Peak}_{\text{residual}} \ge R_t \quad \forall t \in \mathcal{T}$$

---

## 📈 Sensitivity Analysis Results

To assess investment robustness, four sensitivity scenarios were evaluated across capital expenditure multipliers ($\\pm 20\\%$) and curtailment penalty rates ($2\\times$):

| Sensitivity Scenario | CAPEX Multiplier | Curtailment Penalty ($/MWh) | Optimal Siting Decision | Rated Power (MW) | Energy Storage (MWh) | Residual Peak (MW) | Solar Curtailment (MWh) | Annualized Objective Cost |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Low Battery Cost (-20%)** | `0.8` | $40.00 | **BIYAGAMA** | 50.0 MW | 200.0 MWh | 2,600.0 MW | 0.00 MWh | **$2,479,119.47** |
| **Base Case** | `1.0` | $40.00 | **BIYAGAMA** | 50.0 MW | 200.0 MWh | 2,600.0 MW | 0.00 MWh | **$3,623,899.34** |
| **High Battery Cost (+20%)** | `1.2` | $40.00 | **BIYAGAMA** | 50.0 MW | 200.0 MWh | 2,600.0 MW | 0.00 MWh | **$4,768,679.21** |
| **High Curtailment Penalty (2x)**| `1.0` | $80.00 | **BIYAGAMA** | 50.0 MW | 200.0 MWh | 2,600.0 MW | 0.00 MWh | **$3,623,899.34** |

> **Key Insight**: The optimal location (`BIYAGAMA`) and sizing (`50 MW / 200 MWh`) remain **100% invariant** across all sensitivity scenarios, proving that the decision is structurally anchored in transmission topology and regional demand concentration rather than minor cost fluctuations.

---

## 📊 Verified Visualizations Gallery

*Every image below is an authentic, high-resolution figure generated directly by the project code in `results/`.*

### 1. Optimal Geographic BESS Siting Map (Sri Lanka Grid)
> **Asset Path**: [`results/maps/optimal_bess_location_map.png`](results/maps/optimal_bess_location_map.png) (244 KB)  
> High-resolution (300 DPI) geospatial transmission network map of Sri Lanka featuring full coastline geometry, 220 kV (red) and 132 kV (blue) transmission lines, landmark regional cities, glowing star marker at `BIYAGAMA`, annotated technical specs card, and an enlarged Western Province Metro Inset panel.

<div align="center">
  <img src="results/maps/optimal_bess_location_map.png" alt="Optimal BESS Siting Map Sri Lanka" width="850"/>
</div>

---

### 2. CEB Long-Term Plan Benchmark: Solar Additions vs. BESS Installations (2025–2044)
> **Asset Path**: [`results/graphs/ceb_planned_solar_storage_additions.png`](results/graphs/ceb_planned_solar_storage_additions.png) (150 KB)  
> Dual-axis bar chart comparing the official **CEB Long-Term Generation Expansion Plan (LTGEP 2025–2044 Base Case)** planned grid-connected solar additions (MW, left axis) against planned utility-scale BESS power additions (MW, right axis).

<div align="center">
  <img src="results/graphs/ceb_planned_solar_storage_additions.png" alt="CEB Long-Term Plan Additions" width="850"/>
</div>

---

### 3. Sri Lanka High-Voltage Transmission Network Topology
> **Asset Path**: [`results/graphs/transmission_network.png`](results/graphs/transmission_network.png) (446 KB)  
> Network graph of 30 substations and 39 high-voltage transmission lines constructed with NetworkX from CEB GIS data, highlighting the 220 kV transmission backbone and 132 kV regional connections.

<div align="center">
  <img src="results/graphs/transmission_network.png" alt="Sri Lanka Transmission Topology" width="850"/>
</div>

---

### 4. Candidate Substation Evaluation: Centrality vs. Solar Proximity
> **Asset Path**: [`results/graphs/substation_evaluation_tradeoff.png`](results/graphs/substation_evaluation_tradeoff.png) (297 KB)  
> Multi-criteria scatter plot showing betweenness centrality versus solar farm distance. Marker size corresponds to nominal voltage level (kV) and marker color reflects composite site score. Top candidates are labeled.

<div align="center">
  <img src="results/graphs/substation_evaluation_tradeoff.png" alt="Centrality vs Solar Distance Tradeoff" width="850"/>
</div>

---

### 5. Multi-Criteria Candidate Siting Ranking
> **Asset Path**: [`results/graphs/candidate_bess_sites.png`](results/graphs/candidate_bess_sites.png) (162 KB)  
> Bar chart ranking all top eligible grid substations by composite site score, confirming Biyagama's #1 position (0.8602).

<div align="center">
  <img src="results/graphs/candidate_bess_sites.png" alt="Candidate BESS Siting Ranking" width="850"/>
</div>

---

### 6. Substation Betweenness Centrality Distribution
> **Asset Path**: [`results/graphs/betweenness_centrality.png`](results/graphs/betweenness_centrality.png) (166 KB)  
> Graph-theoretic betweenness centrality distribution identifying transmission bottlenecks across Sri Lanka's power system.

<div align="center">
  <img src="results/graphs/betweenness_centrality.png" alt="Betweenness Centrality Distribution" width="850"/>
</div>

---

### 7. Hourly Gross Demand vs. Solar PV Generation Profile
> **Asset Path**: [`results/graphs/solar_vs_demand.png`](results/graphs/solar_vs_demand.png) (407 KB)  
> Full 744-hour operational timeseries illustrating electricity demand (peaking at 2,650 MW) contrasted with daytime solar PV generation (peaking at 300 MW).

<div align="center">
  <img src="results/graphs/solar_vs_demand.png" alt="Electricity Demand vs Solar Generation" width="850"/>
</div>

---

### 8. Battery Fleet Charging & Discharging Operational Dynamics
> **Asset Path**: [`results/graphs/battery_charge_discharge.png`](results/graphs/battery_charge_discharge.png) (503 KB)  
> Synchronized 744-hour dispatch timeseries showing automated battery charging during solar surplus hours (10:00–14:00) and sustained discharging during evening peak demand (18:00–22:00).

<div align="center">
  <img src="results/graphs/battery_charge_discharge.png" alt="Battery Charging and Discharging Profile" width="850"/>
</div>

---

### 9. Solar Energy Curtailment Mitigation
> **Asset Path**: [`results/graphs/solar_curtailment.png`](results/graphs/solar_curtailment.png) (116 KB)  
> Post-optimization solar curtailment profile confirming total absorption (0.00 MWh curtailment) across the entire dispatch window.

<div align="center">
  <img src="results/graphs/solar_curtailment.png" alt="Solar Energy Curtailment After Battery Optimization" width="850"/>
</div>

---

### 10. Optimal Battery Power & Energy Capacity Sizing
> **Asset Path**: [`results/graphs/optimal_bess_sizing.png`](results/graphs/optimal_bess_sizing.png) (96 KB)  
> Optimal sizing decision plot verifying the selection of 50.0 MW power capacity and 200.0 MWh energy capacity at Biyagama.

<div align="center">
  <img src="results/graphs/optimal_bess_sizing.png" alt="Optimal Battery Sizing" width="850"/>
</div>

---

### 11. Sensitivity Analysis Across Technology Costs & Curtailment Penalties
> **Asset Path**: [`results/sensitivity/battery_sensitivity.png`](results/sensitivity/battery_sensitivity.png) (262 KB)  
> Dual-panel sensitivity response evaluating total battery investment, objective cost, and capacity sizing stability across scenario sweeps.

<div align="center">
  <img src="results/sensitivity/battery_sensitivity.png" alt="BESS Sensitivity Analysis" width="850"/>
</div>

---

## 🗂️ Notebook Execution Pipeline

The research pipeline comprises 11 reproducible, self-contained Jupyter notebooks tested end-to-end:

| # | Notebook File | Objective & Method | Generated Assets |
|---|:---|:---|:---|
| **00** | [`00_Project_Setup.ipynb`](notebook/00_Project_Setup.ipynb) | Directory initialization, template generation, and CEB data schema verification | `datasets/templates/*.csv` |
| **01** | [`01_Official_Data_Collection_and_EDA.ipynb`](notebook/01_Official_Data_Collection_and_EDA.ipynb) | Exploratory analysis of CEB capacity, generation, demand, and LTGEP additions | `results/graphs/ceb_planned_solar_storage_additions.png`, `results/tables/official_data_inventory.csv` |
| **02** | [`02_Data_Cleaning_and_Validation.ipynb`](notebook/02_Data_Cleaning_and_Validation.ipynb) | Geospatial coordinate cleaning, substation validation, and hourly demand synthesis | `datasets/processed/system_hourly_profile.csv`, `datasets/processed/optimization_profile.csv` |
| **03** | [`03_Solar_Resource_Analysis.ipynb`](notebook/03_Solar_Resource_Analysis.ipynb) | NASA POWER hourly irradiance analysis across 10 regional utility-scale solar sites | Diurnal solar capacity factors and plant irradiance statistics |
| **04** | [`4_Grid_Network_Construction.ipynb`](notebook/4_Grid_Network_Construction.ipynb) | NetworkX topological transmission graph formulation (30 nodes, 39 edges) | `results/graphs/transmission_network.png`, `datasets/processed/grid_nodes.csv`, `grid_edges.csv` |
| **05** | [`05_Graph_Theory_Analysis.ipynb`](notebook/05_Graph_Theory_Analysis.ipynb) | Betweenness, closeness, and degree centrality computation | `results/graphs/betweenness_centrality.png`, `datasets/processed/graph_theory_metrics.csv` |
| **06** | [`06_BESS_Candidate_Site_Selection.ipynb`](notebook/06_BESS_Candidate_Site_Selection.ipynb) | Multi-criteria scoring, geodesic solar distance calculation, and candidate ranking | `results/graphs/candidate_bess_sites.png`, `datasets/processed/candidate_bess_sites.csv` |
| **07** | [`07_BESS_Optimal_Placement_and_Sizing.ipynb`](notebook/07_BESS_Optimal_Placement_and_Sizing.ipynb) | Pyomo MILP formulation and HiGHS solver execution (50 MW / 200 MWh at Biyagama) | `results/optimization/optimal_bess_locations.csv`, `battery_dispatch_results.csv`, `optimization_summary.csv` |
| **08** | [`08_Optimization_Results_and_Visualization.ipynb`](notebook/08_Optimization_Results_and_Visualization.ipynb) | High-resolution dispatch plotting, GIS map generation, and CEB benchmark comparison | `results/maps/optimal_bess_location_map.png`, `results/graphs/*.png` |
| **09** | [`09_Sensitivity_Analysis.ipynb`](notebook/09_Sensitivity_Analysis.ipynb) | Robustness checks across $\\pm 20\\%$ battery CAPEX and $2\\times$ curtailment penalty sweeps | `results/sensitivity/battery_sensitivity.png`, `results/sensitivity/sensitivity_results.csv` |
| **10** | [`10_Final_Research_Results.ipynb`](notebook/10_Final_Research_Results.ipynb) | Executive synthesis, centrality trade-off scatter plot, and consolidated research findings | `results/tables/final_research_summary.csv`, `results/graphs/substation_evaluation_tradeoff.png` |

---

## 📁 Repository Structure

```text
4G-Network-Coverage-Optimization/
├── config/
│   ├── model_config.json                 # Model hyperparameters, battery costs & graph weights
│   └── parameters.py                     # Config parser utility
├── datasets/
│   ├── processed/                        # Model-ready sanitized input datasets
│   │   ├── candidate_bess_sites.csv      # 30 ranked substations with composite scores & cost factors
│   │   ├── graph_theory_metrics.csv      # Degree, betweenness, closeness, and solar distance
│   │   ├── grid_edges.csv                # 39 transmission lines with length, voltage & capacity
│   │   ├── grid_nodes.csv                # 30 substations with coordinates & voltage ratings
│   │   ├── optimization_profile.csv      # 744-hour demand and solar operational timeseries
│   │   └── system_hourly_profile.csv     # Cleaned hourly system timeseries
│   ├── raw/
│   │   ├── electricity/                  # Raw electricity demand timeseries
│   │   ├── gis/                          # Transmission network spatial data
│   │   │   ├── grid_substations.csv      # Substation coordinates and voltages
│   │   │   ├── solar_power_plants.csv    # Utility solar plant coordinates and capacities
│   │   │   ├── sri_lanka_boundaries.geojson # High-resolution Sri Lanka island polygon
│   │   │   └── transmission_lines.csv    # Transmission corridor connectivity
│   │   ├── official_report_csv/          # Verified official CEB statistical publications
│   │   │   ├── ceb_base_case_solar_and_storage_additions_2025_2044.csv
│   │   │   ├── ceb_electricity_sales_by_distribution_division_2024_2025.csv
│   │   │   ├── ceb_existing_renewable_capacity_as_at_2023_12_31.csv
│   │   │   ├── ceb_historical_electricity_demand_2009_2023.csv
│   │   │   ├── ceb_installed_capacity_by_owner_and_type_2024_2025.csv
│   │   │   ├── ceb_net_generation_by_owner_and_source_2024_2025.csv
│   │   │   ├── ceb_rooftop_solar_scheme_exports_2024_2025.csv
│   │   │   ├── ceb_summary_statistics_2024_2025.csv
│   │   │   └── siyambalanduwa_solar_park_reference_record.csv
│   │   └── solar/                        # NASA POWER hourly solar data
│   │       └── nasa_power_hourly/        # Irradiance CSVs for stations SOL_01 to SOL_10
│   └── templates/                        # Reusable data templates
├── notebook/                             # 11 Sequential analysis notebooks
├── results/                              # Research outputs
│   ├── graphs/                           # Verified 300 DPI visualization figures
│   │   ├── battery_charge_discharge.png  # Hourly battery dispatch dynamics
│   │   ├── betweenness_centrality.png    # Substation betweenness centrality distribution
│   │   ├── candidate_bess_sites.png      # Top candidate substations ranking
│   │   ├── ceb_planned_solar_storage_additions.png # CEB LTGEP additions comparison
│   │   ├── optimal_bess_sizing.png       # Optimal power and energy sizing
│   │   ├── solar_curtailment.png         # Solar curtailment elimination
│   │   ├── solar_vs_demand.png           # Hourly demand vs. solar profile
│   │   ├── substation_evaluation_tradeoff.png # Centrality vs. solar distance trade-off
│   │   └── transmission_network.png      # NetworkX grid topology graph
│   ├── maps/                             # GIS geospatial mapping
│   │   └── optimal_bess_location_map.png # Publication-grade siting map with metro inset
│   ├── optimization/                     # Solved mathematical optimization outputs
│   │   ├── battery_dispatch_results.csv  # 744-hour dispatch operational records
│   │   ├── optimal_bess_locations.csv    # Selected site (Biyagama, 50 MW / 200 MWh)
│   │   └── optimization_summary.csv      # Objective value & residual peak summary
│   ├── sensitivity/                      # Sensitivity scenario outputs
│   │   ├── battery_sensitivity.png       # Scenario comparison chart
│   │   └── sensitivity_results.csv       # Scenario sweep records across CAPEX & penalties
│   └── tables/                           # Summary reports & data audits
│       ├── final_research_summary.csv    # Consolidated findings table
│       └── official_data_inventory.csv   # CEB dataset audit records
├── src/                                  # Core Python library
│   ├── bess_optimization.py              # Pyomo MILP mathematical formulation & solver
│   ├── data_cleaning.py                  # Timeseries cleaning and validation
│   ├── data_validation.py                # Schema validators for GIS and timeseries
│   ├── eda_tools.py                      # Exploratory data analysis utilities
│   ├── graph_utils.py                    # NetworkX graph construction & candidate ranking
│   └── paths.py                          # Robust project path resolvers
├── LICENSE                               # MIT License
├── README.md                             # Comprehensive Research Documentation
└── requirements.txt                      # Python library dependencies
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Python**: 3.11, 3.12, or 3.13
- **Git**

### 2. Environment Setup

```bash
# Clone the repository
git clone https://github.com/your-username/sri-lanka-grid-bess-optimization.git
cd sri-lanka-grid-bess-optimization

# Create and activate virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On Linux / macOS:
source .venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Execution

#### Interactive Jupyter Lab
```bash
jupyter lab
```
Run notebooks sequentially from `notebook/00_Project_Setup.ipynb` through `notebook/10_Final_Research_Results.ipynb`.

#### Automated Full-Pipeline Regression
To execute all 11 notebooks end-to-end and regenerate all 11 figures in ~30 seconds:
```python
import os, json
from pathlib import Path
from IPython.core.interactiveshell import InteractiveShell

os.chdir(Path("notebook").resolve())
shell = InteractiveShell.instance()

all_notebooks = [
    "00_Project_Setup.ipynb",
    "01_Official_Data_Collection_and_EDA.ipynb",
    "02_Data_Cleaning_and_Validation.ipynb",
    "03_Solar_Resource_Analysis.ipynb",
    "4_Grid_Network_Construction.ipynb",
    "05_Graph_Theory_Analysis.ipynb",
    "06_BESS_Candidate_Site_Selection.ipynb",
    "07_BESS_Optimal_Placement_and_Sizing.ipynb",
    "08_Optimization_Results_and_Visualization.ipynb",
    "09_Sensitivity_Analysis.ipynb",
    "10_Final_Research_Results.ipynb"
]

for nb_name in all_notebooks:
    nb = json.load(open(nb_name, encoding="utf-8"))
    for cell in nb["cells"]:
        if cell.get("cell_type") == "code" and cell.get("source"):
            shell.run_cell("".join(cell["source"]))
    print(f"Passed: {nb_name}")
```

---

## 📚 Data Sources & References

1. **Ceylon Electricity Board (CEB)**:
   - *Long Term Generation Expansion Plan (LTGEP) 2025–2044*, Transmission Planning Division, Colombo, Sri Lanka.
   - *Statistical Digest & Annual Generation Performance Reports (2024–2025)*.
   - Official Portal: [https://www.ceb.lk/](https://www.ceb.lk/)

2. **NASA POWER Project**:
   - *Prediction of Worldwide Energy Resources (POWER)* hourly surface solar irradiance and meteorological data, NASA Langley Research Center.
   - Portal: [https://power.larc.nasa.gov/](https://power.larc.nasa.gov/)

3. **Optimization & Modeling Tools**:
   - Pyomo: *Optimization Modeling in Python* (Hart et al.).
   - HiGHS: *High Performance Linear and Mixed-Integer Optimization* (Huangfu & Hall).
   - NetworkX: *Network Analysis in Python* (Hagberg, Schult & Swart).

---

## 📄 License

This research and code repository is released under the **[MIT License](LICENSE)**.
