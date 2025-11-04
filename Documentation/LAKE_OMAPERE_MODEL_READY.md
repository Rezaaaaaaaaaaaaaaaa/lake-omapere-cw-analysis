# Lake Omapere CW Mitigation Model - Ready to Run

**Project:** TKIL2602 - Lake Omapere Modelling
**Date Prepared:** 2025-10-29
**Status:** MODEL READY FOR EXECUTION

---

## Executive Summary

All model preparation tasks have been completed. The Lake Omapere CW mitigation model is ready to run for both baseline and wetland (+0.66m) scenarios. This document provides everything needed to execute the model runs and combine results.

---

## What Has Been Completed

### 1. CW Coverage Analysis
- **File:** `CW_Coverage_CORRECTED.csv`
- **Analysis:** `CW_Coverage_Analysis_Report.txt` (run `python analyze_coverage_levels.py` to regenerate)
- **Categories:** `CW_Coverage_Categories.csv`
- **Status:**
  - 50 subcatchments analyzed
  - 25 subcatchments have CW coverage
  - Coverage categorized by thresholds: <2%, 2-4%, >4%
  - **Outstanding Issue:** 5 subcatchments have >100% coverage due to lake overlap (awaiting Annette/Fleur guidance)

### 2. Model Input Files Created
All files in `Model/InputData/`:
- `LakeOmapere_Selection.csv` - Selection of 50 Lake Omapere reaches
- `CLUESloads_baseline.csv` - Baseline phosphorus loads
- `CLUESloads_wetland_066m.csv` - Wetland scenario phosphorus loads
- `AttenCarry_baseline.csv` - Baseline attenuation factors
- `AttenCarry_wetland_066m.csv` - Wetland scenario attenuation factors
- `CW_Subcatchments.csv` - List of 25 subcatchments with CW coverage

### 3. Scenario Lookup File
- **File:** `Model/Lookups/Scenarios_LakeOmapere.xlsx`
- **Scenarios Defined:**
  1. CW <2% coverage (ExtCode 1)
  2. CW 2-4% coverage (ExtCode 2)
  3. CW >4% coverage (ExtCode 3)

### 4. Model Scripts Ready
Two versions prepared:

#### Baseline Run
- **File:** `Model/StandAloneDNZ2.py`
- **Run Name:** LakeOmapere_Baseline
- **Inputs:**
  - AttenCarry_baseline.csv
  - CLUESloads_baseline.csv
  - Scenarios_LakeOmapere.xlsx
  - LakeOmapere_Selection.csv

#### Wetland Run (+0.66m)
- **File:** `Model/StandAloneDNZ2_Wetland066m.py`
- **Run Name:** LakeOmapere_Wetland066m
- **Inputs:**
  - AttenCarry_wetland_066m.csv
  - CLUESloads_wetland_066m.csv
  - Scenarios_LakeOmapere.xlsx
  - LakeOmapere_Selection.csv

### 5. Placement Rules Modified
- **File:** `Model/PlacementRules.py`
- **Change:** CW placement now based on actual GIS wetland locations (reads from `CW_Subcatchments.csv`)
- **Previous:** Soil-based placement rules
- **Current:** GIS-based placement for the 25 subcatchments with identified CW sites

---

## How to Run the Model

### Prerequisites
Ensure you're in the Model directory:
```bash
cd Model
```

### Step 1: Run Baseline Scenario
```bash
python StandAloneDNZ2.py
```

**Expected Output:**
- Directory: `Model/Outputs/LakeOmapere_Baseline/`
- Files:
  - `GenP_Scen1.csv` - Generated P loads for Scenario 1 (CW <2%)
  - `GenP_Scen2.csv` - Generated P loads for Scenario 2 (CW 2-4%)
  - `GenP_Scen3.csv` - Generated P loads for Scenario 3 (CW >4%)
  - Additional output files as configured in the model

### Step 2: Run Wetland Scenario (+0.66m)
```bash
python StandAloneDNZ2_Wetland066m.py
```

**Expected Output:**
- Directory: `Model/Outputs/LakeOmapere_Wetland066m/`
- Files: Same structure as baseline

### Step 3: Combine Results (If Variable Extents Used)
If different subcatchments have different CW coverage levels and need to be combined:

1. Export generated loads from each scenario run
2. Combine using the approach from Pokaiwhenua (see `annette.txt` lines 48-56)
3. Route combined loads using routing script

**Reference:** `Model/Outputs/Pokaiwhenua10-12Aug1/ScenRouting.py`

---

## File Structure

```
C:\Users\moghaddamr\Reza_CW_Analysis\
│
├── CW_Coverage_CORRECTED.csv              # Corrected CW coverage data
├── CW_Coverage_Categories.csv             # Coverage categories for model
├── CW_Coverage_Analysis_Report.txt        # Coverage analysis results
│
├── TP_noMit_LakeOnly_baseline.xlsb       # CLUES spreadsheet (baseline)
├── TP_noMit_LakeOnly+0.66m.xlsb          # CLUES spreadsheet (wetland)
│
├── Model/
│   ├── StandAloneDNZ2.py                  # BASELINE model script
│   ├── StandAloneDNZ2_Wetland066m.py     # WETLAND model script
│   ├── PlacementRules.py                  # Modified placement rules
│   │
│   ├── InputData/
│   │   ├── CLUESloads_baseline.csv
│   │   ├── CLUESloads_wetland_066m.csv
│   │   ├── AttenCarry_baseline.csv
│   │   ├── AttenCarry_wetland_066m.csv
│   │   └── CW_Subcatchments.csv
│   │
│   ├── SelectionFiles/
│   │   └── LakeOmapere_Selection.csv
│   │
│   ├── Lookups/
│   │   ├── Scenarios_LakeOmapere.xlsx     # CW scenarios
│   │   └── LRFs_years.xlsx                # Load reduction factors
│   │
│   └── Outputs/                            # Model outputs will be here
│       ├── LakeOmapere_Baseline/          # (created on run)
│       └── LakeOmapere_Wetland066m/       # (created on run)
│
├── Analysis Scripts/
│   ├── analyze_coverage_levels.py         # Analyze CW coverage
│   ├── create_scenarios.py                # Create scenario file
│   └── prepare_model_inputs.py            # Prepare input CSVs
│
└── Documentation/
    ├── LAKE_OMAPERE_MODEL_READY.md        # This file
    ├── MODEL_SETUP_SUMMARY.md             # Detailed setup notes
    ├── CORRECTIONS_SUMMARY.md             # CW analysis corrections
    ├── DATA_MATCHING_VERIFICATION.md      # Data verification
    └── SESSION_SUMMARY.txt                # Previous session notes
```

---

## Key Model Configuration

### Contaminant
- **Primary:** Total Phosphorus (P)
- **Pathways:** BE, SD, SR, TD, IF, SG, DG
- **Fractions:** PartP, DRP, DOP

### CW Coverage Thresholds (Current)
- **Low:** <2% coverage (21 subcatchments with CW, 61.8%)
- **Medium:** 2-4% coverage (2 subcatchments, 5.9%)
- **High:** >4% coverage (11 subcatchments, 32.4%)

**Note:** These thresholds should be discussed with Fleur to ensure they're appropriate for Lake Omapere.

### CW Placement
- **Method:** GIS-based (actual wetland locations)
- **Total subcatchments with CW:** 25 out of 50
- **Coverage range (valid):** 0.16% to 88.43%

---

## Outstanding Issues & Next Steps

### 1. Lake Overlap Issue (URGENT)
**Problem:** 5 subcatchments have >100% CW coverage because ~19 ha of CW sites are in the +0.66m lake inundation zone.

**Affected Subcatchments:**
- SC-0: 8,465% coverage
- SC-3: 790% coverage
- SC-34: 484% coverage
- SC-15: 180% coverage
- SC-47: 123% coverage

**Action Required:**
- Send draft email to Annette & Fleur (in `DRAFT_EMAIL_SHORT.txt`)
- Await guidance on whether to re-clip CW shapefiles to exclude lake zone
- Once resolved, update CW areas and re-run analysis

### 2. LRF Thresholds Discussion
**Action Required:**
- Review coverage analysis report (`CW_Coverage_Analysis_Report.txt`)
- Discuss with Fleur whether current thresholds (<2%, 2-4%, >4%) are appropriate
- Consider alternatives suggested in the analysis

### 3. Model Testing
**Recommended:**
- Test baseline run with a small subset first
- Verify outputs are in expected format
- Check that routing works correctly
- Review with Annette before full production runs

### 4. Variable Extent Handling
**If needed:**
- Each subcatchment can have different CW coverage levels
- May need to run scenarios separately and combine results
- Follow Pokaiwhenua methodology (see `annette.txt`)
- Create custom routing script

---

## Quick Command Reference

### Regenerate Coverage Analysis
```bash
python analyze_coverage_levels.py
```

### Recreate Scenario File
```bash
python create_scenarios.py
```

### Check Model Setup
```bash
cd Model
python -c "import pandas as pd; print('Selection CSV:'); print(pd.read_csv('SelectionFiles/LakeOmapere_Selection.csv').head()); print('\nCW Subcatchments:'); print(pd.read_csv('InputData/CW_Subcatchments.csv').head())"
```

### Verify Input Files Exist
```bash
cd Model
dir InputData\*Lake*.csv
dir InputData\CW_*.csv
dir InputData\Atten*.csv
dir InputData\CLUES*.csv
```

---

## Contact Information

**Team:**
- Reza Moghaddam (Analyst) - Reza.Moghaddam@niwa.co.nz
- Annette Semadeni-Davies (Reviewer) - Annette.Davies@niwa.co.nz
- Fleur Matheson (Project Lead) - Fleur.Matheson@niwa.co.nz

**Project Path:** O:\TKIL2602\Working\Lake Omapere Trust\

---

## References

### Key Documents
1. `annette.txt` - Original model setup instructions from Annette
2. `SESSION_SUMMARY.txt` - Previous session summary (CW analysis phase)
3. `MODEL_SETUP_SUMMARY.md` - Detailed technical notes on model setup
4. `CORRECTIONS_SUMMARY.md` - Documentation of CW coverage corrections

### External References
- CLUES model documentation
- Pokaiwhenua project methodology
- DNZ23201 model structure

---

## Model Run Checklist

Before running the model, verify:

- [ ] All input CSV files exist in `Model/InputData/`
- [ ] Selection file exists: `Model/SelectionFiles/LakeOmapere_Selection.csv`
- [ ] Scenario file exists: `Model/Lookups/Scenarios_LakeOmapere.xlsx`
- [ ] LRF file exists: `Model/Lookups/LRFs_years.xlsx`
- [ ] PlacementRules.py has been modified for GIS-based CW placement
- [ ] Output directories have write permissions
- [ ] Python environment has all required packages (pandas, geopandas, numpy, xarray, openpyxl)
- [ ] Current working directory is `Model/` when running scripts

**After baseline run completes successfully:**
- [ ] Verify output directory created: `Model/Outputs/LakeOmapere_Baseline/`
- [ ] Check output files for reasonable values
- [ ] Review with team before running wetland scenario

**After wetland run completes successfully:**
- [ ] Verify output directory created: `Model/Outputs/LakeOmapere_Wetland066m/`
- [ ] Compare baseline vs wetland results
- [ ] Combine results if variable extents were used
- [ ] Prepare summary tables and visualizations

---

## Troubleshooting

### Common Issues

**Issue:** Module not found error
**Solution:** Ensure you're running from the `Model/` directory where all module files are located

**Issue:** File not found error for input CSVs
**Solution:** Check that file paths in the script match actual file locations. Use `dir InputData\` to verify files exist.

**Issue:** No output generated
**Solution:** Check that output directory has write permissions. Look for error messages in console output.

**Issue:** Placement rules not working
**Solution:** Verify `CW_Subcatchments.csv` exists and contains the correct NZSEGMENT values

---

## Version History

**v1.0 - 2025-10-29**
- Initial model setup completed
- All input files prepared
- Baseline and wetland scripts configured
- Scenario file created
- Placement rules modified for GIS-based CW locations
- Documentation completed

---

**MODEL IS READY TO RUN**

Follow the "How to Run the Model" section above to execute baseline and wetland scenarios.
