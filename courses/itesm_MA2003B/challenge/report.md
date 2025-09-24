# Technical Report: Air Quality Analysis System (MA2003B-Reto)

## Overview

This project implements a comprehensive air quality analysis system for SIMA (Sistema Integral de Monitoreo Ambiental) data spanning 2020-2025. The system processes multi-format Excel datasets, performs sophisticated data imputation, and generates AQI (Air Quality Index) metrics and visualizations following US EPA standards.

## Architecture and Data Flow

### 1. Raw Data Input
- **Location**: `data/raw/`
- **Format**: Multiple Excel files with varying sheet structures
- **Coverage**: 2020-2025 time period across multiple monitoring stations
- **Files**:
  - `DATOS HISTÓRICOS 2020_2021_TODAS ESTACIONES.xlsx`
  - `DATOS HISTÓRICOS 2022_2023_TODAS ESTACIONES.xlsx`
  - `DATOS HISTÓRICOS 2023_2024_TODAS ESTACIONES_ITESM.xlsx`
  - `BD 2024.xlsx`
  - `BD 2025.xlsx`
  - `Etiquetas.xlsx`

### 2. Data Processing Pipeline

The processing pipeline consists of five sequential stages implemented in Jupyter notebooks and Python scripts:

#### Stage 1: Database Processing (`database_processing.ipynb`, `process_datasets.py`)

**Purpose**: Consolidate heterogeneous Excel datasets into a unified format

**Key Functions**:
- `process_datasets.py:47-273`: Main processing function that handles 5 different dataset formats
- Station code mapping system using `labels` dictionary (lines 5-33)
- Individual dataset processors for each time period

**Processing Logic**:
1. **Dataset 1 (2020-2021)**: Sheet-based processing with station name matching
2. **Dataset 2 (2022-2023)**: Similar sheet-based approach with refined station mapping
3. **Dataset 3 (2023-2024)**: Complex matrix-based processing with header extraction from rows 0-1
4. **Dataset 4 (2024)**: Column name normalization and parameter code matching
5. **Dataset 5 (2025)**: Header cleanup and date parsing

**Station Mapping System**:
```python
labels = {
    'stations': {
        'SE': 'sureste', 'NE': 'noreste', 'CE': 'centro',
        'NO': 'noroeste', 'SO': 'suroeste', 'NTE': 'norte',
        'SUR': 'sur', 'NO2': ['noroeste2', 'noroeste 2'], # Multiple aliases supported
        # ... additional mappings
    }
}
```

**Output**: `data/processed/main_dataframe.csv` - unified dataset with ~779K records

#### Stage 2: Data Exploration (`exploration.ipynb`)

**Purpose**: Initial data quality assessment and subset generation

**Key Features**:
- NaN value identification and replacement (`-9999` → `NaN`)
- Per-station dataset generation in `data/processed/subsets/`
- Basic data structure validation

**Functions**:
- Data filtering and cleaning
- Station-specific CSV export for granular analysis

#### Stage 3: Data Imputation (`data_imputation.ipynb`)

**Purpose**: Advanced missing data analysis and imputation using multi-level strategies

**Missing Data Analysis**:
- Comprehensive missingness heatmap generation by station × pollutant pairs
- Gap length characterization: short (≤6h), medium (7-48h), long (>48h)
- Coverage-based routing table for imputation strategy selection

**Imputation Methodology**:

1. **NOx Correction**: 
   - Physical consistency rule: `NOx = NO + NO₂` when NOx is missing but components are available
   - Preserves original measurements where they exist

2. **Method A (Short-gap seasonal template)**:
   - Targets gaps ≤6 hours
   - Uses robust climatology: median by (month, hour)
   - Fallback hierarchy: hour-of-day median → group overall median
   - Preserves diurnal/seasonal patterns

3. **Method B (Spatio-temporal neighbor fill)**:
   - Targets medium gaps (7-48h)
   - Cross-station borrowing using spatial neighbors
   - Temporal alignment prevents leakage between periods
   - Median-based aggregation for robustness

**Quality Controls**:
- Coverage thresholds: ≥80% (standard), 60-80% (conservative), <60% (exclude)
- Physical constraints: `NOx ≥ max(NO, NO₂)` for imputed values
- Value clamping to P99.9 percentile

**Routing Table System**:
- Decision matrix combining coverage % and gap length distributions
- Auditable policy: include_standard (A), include_conservative (A+B), include_with_longs, or exclude
- Prevents ad-hoc imputation decisions

#### Stage 4: Statistical Analysis (`statistical_analysis.ipynb`)

**Purpose**: Comprehensive statistical analysis with time series and distributional comparisons

**Key Analysis Functions**:

1. **Daily Max 8-hour Calculation**:
```python
def daily_max8h_for_group(g, contaminant):
    # Reindex to hourly grid for robust rolling
    idx = pd.date_range(g["date"].min().floor("H"), g["date"].max().ceil("H"), freq="H")
    s = g.set_index("date")[contaminant].reindex(idx)
    # 8-hour rolling average (min 6 valid points)
    m8 = s.rolling(window=8, min_periods=6).mean()
    # Daily maximum
    dmax = m8.resample("D").max()
```

2. **Boxplot Analysis by Period**:
- Comparative analysis across pandemic (Jan-Jul 2020), baseline (Jan-Jul 2024), and current (Jan-Jul 2025) periods
- City-level aggregation using equal-weight station averaging
- Statistical visualization for all monitored contaminants

3. **Time Series Overview**:
- Daily city averages with 7-day moving averages
- Period highlighting with temporal windows
- Trend analysis across 2020-2025 timeframe

**Contaminants Analyzed**: PM2.5, NO2, CO, O3, NO, NOx_final

#### Stage 5: Quantitative Analysis (`cuantitative_analysis.ipynb`)

**Purpose**: EPA-compliant AQI calculation and comprehensive metrics generation

**Monthly Metrics Calculation**:
- **AUC (Area Under Curve)**: Trapezoidal integration with 1-hour steps
- **Mean**: `AUC / valid_hours` for temporal averaging
- **Percentiles**: P50, P90 for distribution characterization
- **Maximum Daily**: Peak daily values within each month
- **Valid Hours**: Data completeness metric

**AQI Implementation (US EPA Standards)**:

1. **PM2.5**: 24-hour average (requires ≥18 valid hours, 75% coverage)
2. **O3**: Daily maximum 8-hour average (ppb→ppm conversion, ≥6 valid hours per window)
3. **CO**: Daily maximum 8-hour average (≥6 valid hours per window)
4. **NO2**: Daily maximum 1-hour value (≥18 valid hours per day)

**Breakpoint Tables**:
```python
PM25_BREAKPOINTS = [
    (0.0, 12.0, 0, 50),      # Good
    (12.1, 35.4, 51, 100),   # Moderate
    (35.5, 55.4, 101, 150),  # Unhealthy for Sensitive Groups
    # ... additional ranges
]
```

**IAQI Calculation**:
```python
def iaqi_from_bp(c, bps):
    for Clow, Chigh, Ilow, Ihigh in bps:
        if c <= Chigh:
            return (Ihigh - Ilow) / (Chigh - Clow) * (c - Clow) + Ilow
```

**City-Level AQI**: Daily maximum across all stations
**Temporal Smoothing**: 7-day moving average for trend analysis

### 3. Automation and Export System (`export_reports.py`)

**Purpose**: Automated notebook-to-report conversion pipeline

**Key Features**:
- Dependency checking (nbconvert, pandoc)
- Sequential notebook processing with predefined order
- Multi-format export (HTML, PDF)
- Error handling and verbose logging
- Index page generation for report navigation

**Export Order**:
1. Database Processing Report
2. Data Imputation Report  
3. Data Exploration Report
4. Statistical Analysis Report
5. Quantitative Analysis Report

**Command-line Interface**:
```bash
python scripts/export_reports.py [--format html|pdf|both] [--verbose]
```

## Technical Specifications

### Dependencies
- **Core**: `pandas`, `numpy`, `matplotlib`
- **I/O**: `openpyxl`, `pyarrow` 
- **ML**: `scikit-learn`
- **Export**: `nbconvert`, `pandoc` (optional for PDF)

### Data Structures

**Main DataFrame Schema**:
- `date`: DateTime index (hourly frequency)
- `station_code`: Categorical station identifier
- Contaminant columns: `PM2.5`, `NO2`, `CO`, `O3`, `NO`, `NOX_final`
- Meteorological parameters: `TOUT`, `RH`, `SR`, `RAINF`, `PRS`, `WSR`, `WDR`
- Imputation flags: `*_AB_imputed` boolean indicators

**Processing Outputs**:
- `data/processed/main_dataframe.csv`: Raw consolidated dataset
- `data/processed/pre_imputation_subset_AB_v1.csv`: Post-imputation dataset
- `data/processed/panel_BALANCED_MAIN_JanJul_2020_2024_2025_AB_v1.csv`: Analysis-ready panel
- `reports/tables/metrics_monthly.csv`: Monthly aggregated metrics
- `reports/tables/aqi_daily.csv`: Daily AQI calculations

### Station Network
15 monitoring stations with standardized codes:
- **Primary**: CE (centro), SE (sureste), NE (noreste), NO (noroeste), SO (suroeste)
- **Secondary**: NTE (norte), SUR (sur)
- **Expansion**: NO2, NE2, SE2, SO2, NTE2, SE3, NE3, NO3

### Quality Assurance

**Physical Constraints**:
- NOx ≥ max(NO, NO₂) enforcement
- Value clamping to prevent unrealistic outliers
- Minimum coverage requirements for statistical validity

**Temporal Consistency**:
- Period-based imputation prevents data leakage
- Consistent hourly resampling across all analyses
- Gap length classification for appropriate method selection

**Validation Metrics**:
- Coverage percentages by station-contaminant pairs
- Gap distribution statistics
- Imputation success rates and method performance

## Key Algorithmic Innovations

### 1. Multi-Level Imputation Strategy
The system implements a hierarchical imputation approach that considers both temporal patterns and spatial relationships:
- **Local temporal**: Seasonal templates for short gaps
- **Spatial borrowing**: Cross-station median for medium gaps
- **Conservative exclusion**: Long gaps left as missing to prevent data fabrication

### 2. Auditable Routing System
Decision-making is encoded in a routing table that maps (station, contaminant, period, coverage%, gap_distribution) → imputation_method, ensuring reproducible and transparent data processing.

### 3. Period-Aware Processing
The system maintains temporal boundaries between pandemic (2020-2021), baseline (2024), and current (2025) periods to prevent information leakage in comparative analyses.

### 4. EPA-Compliant AQI Implementation
Faithful implementation of US EPA AQI calculation methodology including:
- Proper concentration truncation rules
- Unit conversions (ppb→ppm for O3)
- Coverage requirements for averaging periods
- Breakpoint interpolation for index calculation

## Performance and Scalability

**Dataset Scale**: 
- Input: ~779K hourly records across 15 stations and 6 contaminants
- Processing time: ~5-10 minutes for full pipeline on standard hardware
- Memory usage: Peak ~2GB during processing

**Computational Complexity**:
- Data processing: O(n) where n = number of records
- Imputation: O(n·s) where s = number of stations (spatial neighbors)
- AQI calculation: O(n) with vectorized operations

## Output Products

### Tables
- Monthly metrics by station-contaminant: AUC, mean, percentiles, max daily
- Daily AQI by station: IAQI components and composite AQI
- City-level AQI time series with categories and moving averages

### Visualizations
- Missing data heatmaps by station-contaminant pairs
- Time series plots with period highlighting and lockdown markers
- Boxplot comparisons across pandemic/baseline/current periods
- AQI category distribution charts (count and percentage)
- Monthly metric trends with inter-station variability

### Reports
- HTML/PDF exports of all analysis notebooks
- Automated index generation for navigation
- Self-contained reports with embedded visualizations

This system provides a robust, transparent, and scientifically rigorous approach to air quality data analysis, suitable for environmental monitoring, policy analysis, and public health research applications.