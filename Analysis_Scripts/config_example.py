"""
Configuration file for Lake Ōmāpere CW Analysis

This file contains all configurable parameters for the analysis.
Modify these values to adapt the script to different scenarios.
"""

# ============================================================================
# FILE PATHS
# ============================================================================

# CLUES Input Files
CLUES_BASELINE_PATH = "Model/CLUES_SS_NRC_2020/TP_noMit_LakeOnly_baseline.xlsx"
CLUES_WETLAND_PATH = "Model/CLUES_SS_NRC_2020/TP_noMit_LakeOnly+0.66m.xlsx"

# Supporting Data Files
CW_COVERAGE_CSV = "Results/CW_Coverage_by_Subcatchment.csv"
REACH_NETWORK_CSV = "Model/ReachNetwork.csv"
ATTENUATION_CSV = "Model/AttenCarry.csv"
SOIL_ANALYSIS_CSV = "Results/01_SoilAnalysis/Clay_Analysis_by_Reach.csv"
LRF_XLSX = "Lookups/LRFs_years.xlsx"

# Output Directories
OUTPUT_DIR = "Results/LAKE_OMAPERE_RESULTS"
DATA_DIR = "Results/LAKE_OMAPERE_RESULTS/Data"
FIGURES_DIR = "Results/LAKE_OMAPERE_RESULTS/Figures"
SUMMARY_DIR = "Results/LAKE_OMAPERE_RESULTS/Summary"


# ============================================================================
# CLUES COLUMN MAPPINGS
# ============================================================================

# Column names in CLUES spreadsheets (adjust to match your file)
CLUES_COLUMNS = {
    'reach_id': 'NZSEGMENT',           # Reach identifier
    'overseer_load': 'AF',              # Agricultural TP (t/y)
    'sediment_p': 'T',                  # Sediment P (t/y)
    'load_increment': 'BC'              # Total TP load (t/y)
}

# Alternative column names to try if above don't work
CLUES_COLUMN_ALTERNATIVES = {
    'overseer_load': ['OVERSEER Load (t/y)', 'TPAgGen', 'AgLoad'],
    'sediment_p': ['P_Sed', 'soilP', 'Sediment_P'],
    'load_increment': ['LoadIncrement', 'TPGen', 'Total_Load']
}


# ============================================================================
# CW MITIGATION PARAMETERS
# ============================================================================

# Load Reduction Factors (LRF) by coverage extent
# These values represent % reduction per % CW coverage
# Example: If LRF=0.20 and coverage=5%, then reduction = 5% * 0.20 = 1% of load
LRF_FACTORS = {
    'low': 0.15,         # <2% coverage:  15% reduction per % coverage
    'medium': 0.18,      # 2-4% coverage: 18% reduction per % coverage
    'high': 0.20         # >4% coverage:  20% reduction per % coverage
}

# Coverage thresholds for categorization (%)
COVERAGE_THRESHOLDS = {
    'low': 2.0,          # Boundary between low and medium
    'medium': 4.0        # Boundary between medium and high
}

# Clay content threshold for HighClay categorization (%)
CLAY_THRESHOLD = 50.0   # Reaches with >50% clay flagged as HighClay


# ============================================================================
# NETWORK ROUTING PARAMETERS
# ============================================================================

# Default attenuation factor if not provided in data
DEFAULT_ATTENUATION = 0.90

# Typical PstreamCarry range (for reference)
ATTENUATION_MIN = 0.80
ATTENUATION_MAX = 0.99

# Network analysis parameters
HYDSEQ_COLUMN = 'HYDSEQ'      # Column name for hydrological sequence
FROM_NODE_COLUMN = 'FROM_NODE'  # Upstream node
TO_NODE_COLUMN = 'TO_NODE'      # Downstream node
REACH_ID_COLUMN = 'NZSEGMENT'  # Reach identifier


# ============================================================================
# LAKE ŌMĀPERE SPECIFIC
# ============================================================================

# Reaches to include in analysis (set to None to use all)
LAKE_REACHES = None  # Will load from data or use all reaches

# Number of Lake reaches expected
EXPECTED_LAKE_REACHES = 50

# Lake elevation scenario
LAKE_ELEVATION = "+0.66m"  # Lake level rise scenario


# ============================================================================
# ANALYSIS OPTIONS
# ============================================================================

# Generate visualizations?
GENERATE_PLOTS = True

# Save intermediate results?
SAVE_INTERMEDIATE = False

# Verbose output?
VERBOSE = True

# Number of decimal places in outputs
DECIMAL_PLACES = 4


# ============================================================================
# ADVANCED OPTIONS
# ============================================================================

# Use advanced routing (full network traversal)?
USE_ADVANCED_ROUTING = True

# Include uncertainty analysis?
INCLUDE_UNCERTAINTY = False
UNCERTAINTY_PERCENTILE_LOW = 5
UNCERTAINTY_PERCENTILE_HIGH = 95

# Sensitivity analysis parameters
SENSITIVITY_PARAMETERS = [
    'lrf_factors',
    'attenuation',
    'coverage_threshold'
]

# Seasonal analysis?
SEASONAL_ANALYSIS = False
SEASONS = ['Summer', 'Autumn', 'Winter', 'Spring']


# ============================================================================
# OUTPUT OPTIONS
# ============================================================================

# Output formats
OUTPUT_FORMATS = {
    'csv': True,         # CSV data files
    'excel': True,       # Excel spreadsheets
    'json': True,        # JSON summary
    'text': True,        # Text summaries
    'plots': True        # Visualization PNG files
}

# Plot DPI (resolution)
PLOT_DPI = 300

# Figure formats to save
FIGURE_FORMATS = ['png', 'pdf']


# ============================================================================
# VALIDATION PARAMETERS
# ============================================================================

# Data quality checks
VALIDATE_DATA = True

# Expected data ranges for validation
VALID_LOAD_RANGE = (0.0, 100.0)      # t/y - adjust as needed
VALID_COVERAGE_RANGE = (0.0, 100.0)  # %
VALID_ATTENUATION_RANGE = (0.0, 1.0) # factor

# Missing data handling
HANDLE_MISSING_DATA = 'fill_zero'    # 'skip', 'fill_zero', 'interpolate'

# Outlier detection
DETECT_OUTLIERS = True
OUTLIER_THRESHOLD = 3.0              # Standard deviations


# ============================================================================
# REPORTING
# ============================================================================

# Report detail level
REPORT_DETAIL_LEVEL = 'comprehensive'  # 'summary', 'standard', 'comprehensive'

# Include methodology in report?
INCLUDE_METHODOLOGY = True

# Include assumptions in report?
INCLUDE_ASSUMPTIONS = True

# Number of top reaches to highlight
TOP_REACHES_COUNT = 10

# Top metrics to report
REPORT_METRICS = [
    'total_reduction',
    'percent_reduction',
    'per_reach_average',
    'amplification_factor'
]


# ============================================================================
# COMPARISON SCENARIOS
# ============================================================================

# Compare against other scenarios?
COMPARISON_SCENARIOS = {
    'no_cw': False,        # Baseline vs wetland (no CW)
    'partial_cw': False,   # Compare different CW coverages
    'different_lrf': False # Compare different LRF values
}

# Sensitivity test LRF values
SENSITIVITY_LRF_VALUES = {
    'conservative': 0.10,  # Lower effectiveness estimate
    'best_case': 0.25      # Higher effectiveness estimate
}


# ============================================================================
# LOGGING AND DEBUGGING
# ============================================================================

# Log level
LOG_LEVEL = 'INFO'  # 'DEBUG', 'INFO', 'WARNING', 'ERROR'

# Log file path
LOG_FILE = 'Analysis_Scripts/analysis.log'

# Debug mode (extra output)
DEBUG_MODE = False

# Save intermediate DataFrames for inspection?
SAVE_DEBUG_DATA = False
