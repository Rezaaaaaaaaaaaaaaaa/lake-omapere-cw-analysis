# Lake Ōmāpere CW Analysis - Usage Guide

## Overview

`lake_omapere_cw_analysis.py` is a comprehensive Python script that automates the complete CW mitigation effectiveness analysis for Lake Ōmāpere.

**What it does:**
- Loads CLUES spreadsheets (baseline and wetland scenarios)
- Extracts phosphorus (TP) loads for 50 Lake reaches
- Applies CW mitigation with Load Reduction Factors (LRFs)
- Routes loads through the reach network with attenuation
- Generates comprehensive results, visualizations, and summaries

---

## Quick Start

### Installation

1. **Ensure Python 3.7+ is installed**
```bash
python --version
```

2. **Install required packages**
```bash
pip install pandas numpy matplotlib openpyxl
```

3. **Navigate to script directory**
```bash
cd Analysis_Scripts
```

### Run Analysis

**Basic usage:**
```bash
python lake_omapere_cw_analysis.py
```

**With output to file:**
```bash
python lake_omapere_cw_analysis.py > analysis_log.txt 2>&1
```

---

## Configuration

### Step 1: Update File Paths

Edit `lake_omapere_cw_analysis.py` and update the `Config` class with your file paths:

```python
class Config:
    # File paths
    CLUES_BASELINE_PATH = "path/to/TP_noMit_LakeOnly_baseline.xlsx"
    CLUES_WETLAND_PATH = "path/to/TP_noMit_LakeOnly+0.66m.xlsx"
    CW_COVERAGE_CSV = "path/to/CW_Coverage_by_Subcatchment.csv"
    REACH_NETWORK_CSV = "path/to/ReachNetwork.csv"
    ATTENUATION_CSV = "path/to/AttenCarry.csv"
```

**File Requirements:**
| File | Description | Required Columns |
|------|-------------|-----------------|
| CLUES Baseline | CLUES spreadsheet | NZSEGMENT, LoadIncrement, OVERSEER Load, P_Sed |
| CLUES Wetland | Wetland scenario | Same as baseline |
| CW Coverage | CW site distribution | reach_id, CW_Coverage_Percent |
| Reach Network | Network connectivity | NZSEGMENT, FROM_NODE, TO_NODE, HYDSEQ |
| Attenuation | Stream reach factors | reach_id, PstreamCarry |

### Step 2: Adjust LRF Factors

Update Load Reduction Factors based on Fleur's recommendations:

```python
LRF_FACTORS = {
    'low': 0.15,         # <2% coverage
    'medium': 0.18,      # 2-4% coverage
    'high': 0.20         # >4% coverage
}
```

**LRF Explanation:**
- LRF = Load Reduction Factor (% reduction per % coverage)
- Example: LRF=0.20, Coverage=5% → Reduction = 5% × 0.20 = 1% of load
- Higher LRF = more effective CW mitigation


### Step 3: Set Coverage Thresholds

Define what constitutes low/medium/high coverage:

```python
COVERAGE_THRESHOLDS = {
    'low': 2.0,         # <2%: low coverage
    'medium': 4.0       # 2-4%: medium coverage
                        # >4%: high coverage
}
```

### Step 4: Configure Output Directories

By default, outputs save to `Results/LAKE_OMAPERE_RESULTS/`. Modify if needed:

```python
OUTPUT_DIR = "Results/LAKE_OMAPERE_RESULTS"
DATA_DIR = "Results/LAKE_OMAPERE_RESULTS/Data"
FIGURES_DIR = "Results/LAKE_OMAPERE_RESULTS/Figures"
SUMMARY_DIR = "Results/LAKE_OMAPERE_RESULTS/Summary"
```

---

## Data Format Requirements

### CLUES Spreadsheet Format

The script expects CLUES spreadsheets with these columns:

| Column | Letter | Name | Description |
|--------|--------|------|-------------|
| Reach ID | - | NZSEGMENT | Unique reach identifier |
| Agricultural TP | AF | OVERSEER Load | Agricultural TP from OVERSEER (t/y) |
| Sediment P | T | P_Sed | Sediment phosphorus (t/y) |
| Total Load | BC | LoadIncrement | Total TP load (t/y) |

**If your columns differ**, edit the column mappings:

```python
CLUES_COLUMNS = {
    'reach_id': 'NZSEGMENT',    # Change if needed
    'overseer_load': 'AF',       # Change to your column
    'sediment_p': 'T',           # Change to your column
    'load_increment': 'BC'       # Change to your column
}
```

### CW Coverage CSV Format

```csv
reach_id,CW_Coverage_Percent
1010001,0.0
1010002,2.5
1010003,5.2
...
```

### Reach Network CSV Format

```csv
NZSEGMENT,FROM_NODE,TO_NODE,HYDSEQ
1010001,A100,B100,1000
1010002,B100,C100,1001
...
```

### Attenuation CSV Format

```csv
reach_id,PstreamCarry
1010001,0.92
1010002,0.89
...
```

---

## Understanding the Analysis Pipeline

### Step 1: Load Data
- Reads CLUES baseline and wetland spreadsheets
- Loads CW coverage, network, and attenuation data
- Validates data quality

### Step 2: Calculate Generated Loads
**Generated loads** = Direct TP from each reach's subcatchment

For each reach:
```
BaselineTP = OVERSEER_Load + Sediment_P + (LoadIncrement - OVERSEER_Load - Sediment_P)
WetlandTP = Same calculation from wetland CLUES
```

### Step 3: Apply CW Mitigation
**CW reduction** = Amount of load removed by Clean Water sites

Formula:
```
CW_Reduction = WetlandTP × (CW_Coverage% / 100) × LRF_Factor
Final_Load = WetlandTP - CW_Reduction
```

Example:
- WetlandTP = 0.50 t/y
- CW Coverage = 5%
- LRF = 0.20
- CW_Reduction = 0.50 × 0.05 × 0.20 = 0.005 t/y
- Final = 0.495 t/y

### Step 4: Route Loads Through Network
**Routed loads** = Cumulative TP from all upstream reaches

Algorithm:
```
For each reach (in hydrological sequence order):
    Routed[i] = Generated[i] + Σ(Upstream_Routed[j] × Attenuation[i])

Where:
  - Generated[i] = local load contribution
  - Upstream_Routed[j] = already-routed load from upstream
  - Attenuation[i] = PstreamCarry factor (0.80-0.99)
```

This shows how upstream CW benefits propagate downstream.

### Step 5: Generate Outputs
Creates:
- **CSV files** with detailed results for each reach
- **Visualizations** (PNG charts)
- **Summary statistics** (JSON and text)

---

## Output Files

### Data Files (in `Results/LAKE_OMAPERE_RESULTS/Data/`)

**Lake_Omapere_Analysis_Results.csv** - Main results file
```
reach_id, generated_baseline, generated_wetland, generated_cw,
cw_reduction, cw_reduction_percent, routed_baseline, routed_cw,
routed_reduction, routed_reduction_percent, CW_Coverage_Percent,
coverage_category, ...
```

**Key columns:**
- `generated_*` = Direct loads from reach
- `routed_*` = Cumulative loads with upstream contribution
- `cw_reduction*` = Amount/percent removed by CW
- `coverage_category` = High/Medium/Low/None classification

### Visualizations (in `Figures/`)

1. **CW_Analysis_Summary.png**
   - 4-panel chart showing:
     - Top reaches by baseline load
     - Top reaches by CW reduction
     - Coverage distribution
     - Total load comparison

2. **Reduction_Percent_Top_Reaches.png**
   - Bar chart of top 15 reaches by % reduction

### Summaries (in `Summary/`)

1. **analysis_summary.json**
   - Machine-readable summary statistics
   - Total loads, reductions, means, std dev
   - CW coverage statistics

2. **analysis_summary.txt**
   - Human-readable summary
   - Key findings and metrics
   - Comparison of generated vs routed

---

## Understanding Results

### Key Metrics

**Generated Reduction**
- What: Direct TP removed by CW at point of implementation
- Use: Understand local CW effectiveness
- Example: "CW removes 0.029 tpy of local load" (8.2%)

**Routed Reduction**
- What: TP removed after routing through network
- Use: Predict lake water quality improvement
- Example: "CW removes 0.229 tpy of routed load" (7.7%)
- Usually larger due to upstream amplification

**Amplification Factor**
- What: Routed reduction / Generated reduction
- Example: 0.229 / 0.029 = 7.9×
- Meaning: Upstream benefits amplified 8× through network

### Coverage Categories

| Category | Range | Meaning |
|----------|-------|---------|
| High | >4% | Significant CW implementation |
| Medium | 2-4% | Moderate implementation |
| Low | <2% | Minimal implementation |
| None | 0% | No CW sites |

### Interpreting Reach Results

For each reach, you get:
- **Generated loads**: Local effectiveness only
- **Routed loads**: Includes upstream contributions
- **HighClay flag**: >50% clay (less suitable for CW)
- **Coverage category**: Level of CW implementation

**Example interpretation:**
```
Reach 1010326:
  Generated reduction: 0.001 tpy (minimal local CW)
  Routed reduction: 0.019 tpy (8× amplified!)
  Coverage: NoCW (no direct CW in this reach)
  Reason: Benefits from upstream CW in network
```

---

## Common Issues and Solutions

### Issue: CLUES file not found
**Solution:** Check file path in Config. Ensure file exists and path is correct.

### Issue: Columns not recognized
**Solution:** Examine CLUES spreadsheet to find actual column names. Update `CLUES_COLUMNS` mapping.

### Issue: CW coverage file not found
**Solution:** Script will continue with zero coverage. Provide CSV with columns: `reach_id, CW_Coverage_Percent`

### Issue: Network file missing
**Solution:** Script will use simplified routing. For accurate results, provide network connectivity CSV.

### Issue: Visualizations not generating
**Solution:** Ensure matplotlib is installed (`pip install matplotlib`). Check file write permissions.

### Issue: Results show very small numbers
**Solution:** Check if loads are in correct units (should be t/y). Verify CLUES column selection.

### Issue: Routed loads smaller than generated
**Solution:** Check attenuation factors. If all attenuation <1.0, this is expected. Verify PstreamCarry values.

---

## Customization Examples

### Change LRF Values (Try Different Effectiveness)

```python
# Conservative estimate (lower effectiveness)
Config.LRF_FACTORS = {
    'low': 0.10,
    'medium': 0.12,
    'high': 0.15
}

# Optimistic estimate (higher effectiveness)
Config.LRF_FACTORS = {
    'low': 0.20,
    'medium': 0.25,
    'high': 0.30
}
```

### Filter to Specific Reaches

Add this after loading data:
```python
# Only analyze high clay reaches
results_filtered = results[results['HighClay'] == True]

# Only high coverage reaches
results_filtered = results[results['coverage_category'] == 'high']

# Specific reach IDs
target_reaches = [1010001, 1010002, 1010003]
results_filtered = results[results['reach_id'].isin(target_reaches)]
```

### Modify Output Location

```python
Config.OUTPUT_DIR = "Results/Alternative_Scenario"
Config.DATA_DIR = "Results/Alternative_Scenario/Data"
Config.FIGURES_DIR = "Results/Alternative_Scenario/Figures"
Config.SUMMARY_DIR = "Results/Alternative_Scenario/Summary"
```

---

## Advanced Options

### Run Without Network Routing

```python
# In run_full_analysis() method:
# Skip the route_loads() step
analysis = LakeOmapereAnalysis()
analysis.load_all_data()
analysis.calculate_generated_loads()
analysis.apply_cw_mitigation()
# Skip: analysis.route_loads()
summary = analysis.generate_outputs()
```

### Generate Specific Visualizations Only

```python
# Import visualization module
from lake_omapere_cw_analysis import ResultsGenerator

# Generate specific chart
gen = ResultsGenerator()
gen.generate_visualizations(results_df, summary_stats)
```

### Export to Different Format

Add custom export function:
```python
# Export to Excel
results.to_excel('Results/Lake_Omapere_Results.xlsx', index=False)

# Export to JSON
results.to_json('Results/Lake_Omapere_Results.json', orient='records')
```

---

## Performance Notes

**Script Runtime:**
- With 50 reaches: ~5-10 seconds
- With full network (593K reaches): ~1-2 minutes
- Visualization generation: +10-20 seconds

**Memory Usage:**
- Baseline: ~100 MB
- With large network: ~500 MB
- Adequate for modern computers

**Optimization Tips:**
- If slow, disable visualizations (comment out `gen_visualizations()`)
- Use simpler routing if network file missing
- Reduce output file sizes with fewer decimal places

---

## Support and Troubleshooting

### Check Script Version
```python
# Add to top of script:
__version__ = "1.0.0"
print(f"Script version: {__version__}")
```

### Enable Debug Mode
```python
# In Config class:
DEBUG_MODE = True  # Enables extra output
SAVE_DEBUG_DATA = True  # Saves intermediate files
```

### Get More Details
```python
# Run with verbose output
python lake_omapere_cw_analysis.py 2>&1 | tee analysis_output.log
```

### Validate Input Data

Add validation before analysis:
```python
from lake_omapere_cw_analysis import DataValidator

validator = DataValidator()
validator.validate_clues(baseline_clues)
validator.validate_cw_coverage(cw_coverage)
validator.validate_network(reach_network)
```

---

## Reference: Analysis Methodology

For detailed methodology explanation, see:
- **EMAIL_TO_FLEUR_AND_ANNETTE.md** - Comprehensive methodology document
- **ROUTING_ANALYSIS_COMPLETE.md** - Detailed routing explanation
- **Results/LAKE_OMAPERE_RESULTS/README.md** - Results interpretation guide

---

## Questions?

If you encounter issues:

1. Check this usage guide
2. Review error messages (usually indicate what went wrong)
3. Examine input files (column names, data formats)
4. Enable debug mode for more output
5. Test with smaller dataset first

For methodology questions, contact Annette or Fleur.

---

**Last Updated:** October 30, 2025
**Project:** TKIL2602 - Lake Ōmāpere Modelling
