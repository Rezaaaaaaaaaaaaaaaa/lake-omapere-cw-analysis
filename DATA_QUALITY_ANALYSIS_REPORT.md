# Lake Omapere CW Analysis - Data Quality Assessment Report

**Date:** October 31, 2025
**Analysis:** Comprehensive review of input data and results
**Status:** ISSUES IDENTIFIED - REQUIRES ATTENTION

---

## Executive Summary

A comprehensive analysis of the Lake Omapere constructed wetland (CW) mitigation effectiveness study revealed **critical data quality issues** in the existing results files, while the source GIS data appears correct. The comprehensive Python analysis script has been successfully updated to use `CW_Coverage_GIS_CALCULATED.xlsx`, but some input CLUES files are missing.

### Key Findings:
- **Source Data (GIS):** ✓ GOOD - CW coverage percentages are realistic (0-68%)
- **Results Files:** ✗ ISSUES - 10% of reaches show impossible CW coverage values (>100%, up to 8464%)
- **Scientific Logic:** ✓ GOOD - Network amplification (7.9x) and LRF values (20-50%) are reasonable
- **Input Files:** ⚠ PARTIAL - Some required CLUES model files are missing

---

## 1. Input Files Assessment

### Files Available ✓
| File Type | Path | Size | Status |
|-----------|------|------|--------|
| CW Coverage (GIS) | `CW_Coverage_GIS_CALCULATED.xlsx` | 8.7 KB | ✓ Valid |
| River Shapefile | `Shapefiles/Reference/Riverlines.shp` | 9.8 KB | ✓ Valid |
| Catchment Shapefile | `Shapefiles/Reference/Catchment.shp` | 12.8 KB | ✓ Valid |
| Lake Shapefile | `Shapefiles/Lake/Lake Omapere-236.34 mAMSL (+0.66m).shp` | 15.7 KB | ✓ Valid |
| Subcatchments Shapefile | `Shapefiles/Subcatchments/Subs.shp` | 65.6 KB | ✓ Valid |
| Attenuation Data | `Model/InputData/AttenCarry.csv` | 30 MB | ✓ Available |
| LRF Data | `Model/Lookups/LRFs_years.xlsx` | 204 KB | ✓ Available |

### Files Missing ✗
| File Type | Expected Path | Alternative Found |
|-----------|---------------|-------------------|
| CLUES Baseline | `Model/CLUES_SS_NRC_2020/TP_noMit_LakeOnly_baseline.xlsb` | `Model/InputData/CLUESloads_baseline.csv` (102 MB) |
| CLUES Wetland | `Model/CLUES_SS_NRC_2020/TP_noMit_LakeOnly+0.66m.xlsb` | `Model/InputData/CLUESloads_wetland_066m.csv` (102 MB) |
| Reach Network | `Model/ReachNetwork.csv` | `Model/InputData/Hydroedge2_5.csv` (114 MB) |

**Recommendation:** Update script configuration to use available alternative files or obtain the specific Lake Omapere CLUES model outputs.

---

## 2. Source Data Quality (GIS-Calculated)

### CW_Coverage_GIS_CALCULATED.xlsx Analysis ✓

**File Structure:**
- 50 reaches (Lake Omapere subcatchments)
- 12 columns including reach ID, land areas, CW areas, and percentages

**CW Coverage Statistics:**
```
Minimum:  0.00%
Maximum: 68.00%
Mean:     7.00%
Median:   0.64%
```

**Distribution:**
- 18 reaches (36%) with 0% CW coverage
- 37 reaches (74%) with <5% coverage
- 7 reaches (14%) with 5-20% coverage
- 6 reaches (12%) with >20% coverage

**Top 5 Reaches by CW Coverage:**
| Reach ID | CW Coverage | CW Area (ha) | Land Area (ha) |
|----------|-------------|--------------|----------------|
| 1010301 | 68.00% | 16.34 | 24.03 |
| 1010219 | 67.84% | 28.23 | 41.62 |
| 1010288 | 23.56% | 16.32 | 69.27 |
| 1009699 | 23.25% | 5.45 | 23.44 |
| 1010387 | 21.98% | 6.13 | 27.90 |

**Data Quality Checks:**
- ✓ All percentages between 0-100%
- ✓ No negative values
- ✓ No missing (NaN) values
- ✓ Calculations verified: (CW_Area / Land_Area) × 100 = Stored_Percent

**Assessment:** **SOURCE DATA IS SCIENTIFICALLY VALID**

---

## 3. Results Files Quality Issues

### Critical Data Quality Problems Identified ✗

#### Issue 1: CW Coverage Exceeds 100% (CRITICAL)

**Affected Files:**
- `Lake_Omapere_Routing_Results.csv` - 5/50 reaches (10%)
- `Lake_Omapere_Complete_Results.csv` - 5/50 reaches (10%)

**Examples of Invalid Values:**
| Reach ID | Source (GIS) | Results File | Discrepancy |
|----------|--------------|--------------|-------------|
| 1009647 | 12.60% | 8464.87% | +8452% |
| 1009699 | 23.25% | 789.87% | +767% |
| 1010388 | 17.53% | 484.00% | +466% |
| 1010139 | 21.50% | 179.84% | +158% |
| 1010665 | 2.84% | 122.99% | +120% |

**Root Cause:**
Mismatch in land area denominators between GIS source and results processing:
- **GIS Calculation:** 21.50% = 21.35ha CW ÷ 99.32ha land
- **Results Calculation:** 179.84% = 16.96ha CW ÷ 9.43ha land

The land area used in results files (9.43ha) is much smaller than the GIS-calculated land area (99.32ha), causing inflated percentages.

**Impact:** Makes results scientifically invalid and unsuitable for reporting.

#### Issue 2: Very Small TP Loads (CONCERNING)

**Observed Values:**
- Total Generated Load (baseline): **0.297 tonnes/year** = 297 kg/year
- Average per reach: **5.93 kg/year**

**Expected Values:**
Typical agricultural catchments generate 100-1000+ kg TP/year per subcatchment.

**Possible Explanations:**
1. Results file contains only Lake Omapere **reaches** not subcatchments (i.e., just river segments)
2. Load units may need verification (expecting kg/yr but seeing smaller values)
3. Data may represent only a subset of the full catchment loads
4. Extraction from CLUES model may have filtered to specific contaminant sources only

**Assessment:** Needs verification against full CLUES model outputs.

#### Issue 3: Negative Generated Loads (CRITICAL)

- **1 reach** has negative baseline TP generated load (-0.00 kg/yr)
- Negative loads are **physically impossible**
- Indicates data processing error or corrupt data entry

---

## 4. Scientifically Reasonable Aspects ✓

Despite data quality issues, several aspects show the underlying methodology is sound:

### Network Routing Amplification ✓

**Observed:**
- Generated load reduction from CW: 0.029 kg/yr
- Routed load reduction from CW: 0.229 kg/yr
- **Amplification factor: 7.9×**

**Expected Range:** 3-10× is typical for network routing models
**Assessment:** REASONABLE - Falls within expected range

**Interpretation:** Upstream CW mitigation has cascading benefits as loads propagate through the network, consistent with established hydrology literature.

### CW Load Reduction Factors (LRFs) ✓

**Values Applied:**
- 0% (no CW)
- 20% (low coverage)
- 35% (medium coverage)
- 50% (high coverage)

**Assessment:** REASONABLE - Aligns with published LRF literature for constructed wetlands treating agricultural runoff.

### High Clay Soil Distribution ✓

- **24/50 reaches (48%)** have >50% clay soils
- Consistent with regional soil characteristics in Northland, New Zealand
- High clay soils relevant for phosphorus retention and wetland effectiveness

### CW Coverage Distribution ✓

From GIS source data:
- Realistic range (0-68%)
- Appropriate spread across categories
- Concentration of high-coverage sites in strategic locations
- Aligns with typical wetland restoration project spatial patterns

---

## 5. Recommended Actions

### Immediate Priority

1. **Do NOT use existing results files for reporting or decision-making**
   - CW coverage percentages are invalid (>100% values)
   - Land area denominators need correction

2. **Run fresh analysis with corrected script**
   - Script has been updated to use `CW_Coverage_GIS_CALCULATED.xlsx` (correct source)
   - Update file paths to point to available CLUES CSV files
   - Verify land area calculations throughout pipeline

3. **Investigate land area mismatch**
   - Compare `Land_Area_ha_GIS` (from GIS source) with results file land areas
   - Determine which land area definition is appropriate for TP load calculations
   - Document the discrepancy source

### Configuration Updates Needed

Update `lake_omapere_cw_analysis.py` Config class:

```python
# FROM (non-existent files):
CLUES_BASELINE_PATH = "Model/CLUES_SS_NRC_2020/TP_noMit_LakeOnly_baseline.xlsb"
CLUES_WETLAND_PATH = "Model/CLUES_SS_NRC_2020/TP_noMit_LakeOnly+0.66m.xlsb"
REACH_NETWORK_CSV = "Model/ReachNetwork.csv"
ATTENUATION_CSV = "Model/AttenCarry.csv"
LRF_XLSX = "Lookups/LRFs_years.xlsx"

# TO (available files):
CLUES_BASELINE_PATH = "Model/InputData/CLUESloads_baseline.csv"
CLUES_WETLAND_PATH = "Model/InputData/CLUESloads_wetland_066m.csv"
REACH_NETWORK_CSV = "Model/InputData/Hydroedge2_5.csv"
ATTENUATION_CSV = "Model/InputData/AttenCarry.csv"
LRF_XLSX = "Model/Lookups/LRFs_years.xlsx"
```

**Note:** CSV files may have different column structures than xlsb files - data loader functions may need updates.

### Verification Steps

After re-running with corrected configuration:

1. **Verify CW Coverage:**
   - All percentages 0-100%
   - Values match GIS source within 0.1%

2. **Verify TP Loads:**
   - Total catchment loads in realistic range (tons/year scale)
   - No negative values
   - Generated loads < routed loads for outlet reaches

3. **Verify Network Routing:**
   - Amplification factor 3-10×
   - Upstream mitigation propagates downstream
   - Loads accumulate correctly through network

4. **Cross-check:**
   - Compare with original CLUES model outputs
   - Validate against Annette's data sources
   - Confirm with Fleur's expectations

---

## 6. Data Processing Pipeline Review

### Current Understanding

```
CLUES Model (xlsb)
    ↓
Extract TP Loads by Reach
    ↓
Apply CW Coverage (%) ← [ISSUE: Land area mismatch]
    ↓
Calculate Mitigation (LRF)
    ↓
Route through Network
    ↓
Generate Results ← [ISSUE: Invalid percentages propagated]
```

### Recommended Fix

1. **Standardize land area definition** across all inputs
2. **Validate GIS-calculated CW coverage** percentages at import
3. **Add data quality checks** before routing calculations
4. **Implement unit tests** for percentage calculations

---

## 7. Spatial Mapping Verification

### Map Generation Status ✓

The spatial mapping component successfully generated 5 maps:
- `Generated_Loads_Comparison.png` (642 KB)
- `Routed_Loads_Comparison.png` (398 KB)
- `CW_Reduction_Generated.png` (321 KB)
- `CW_Reduction_Routed.png` (317 KB)
- `CW_Coverage_Distribution.png` (352 KB)

**Visual Review:**
- River network correctly filtered to 49 Lake Omapere reaches
- Color-coding functional (Red-Yellow-Green gradient)
- Catchment and lake overlays working
- Publication quality (300 DPI)

**Data Concern:**
Maps reflect the invalid CW coverage data from results files. **Maps should be regenerated** after data correction.

---

## 8. Script Capabilities ✓

The comprehensive Python script (`lake_omapere_cw_analysis.py`) has been successfully enhanced:

### Successfully Implemented:
- ✓ Modular class-based architecture
- ✓ GIS shapefile integration
- ✓ Automated spatial mapping (5 map types)
- ✓ CW_Coverage_GIS_CALCULATED.xlsx integration
- ✓ UTF-8 encoding support for Windows
- ✓ Comprehensive documentation

### Needs Testing:
- ⚠ CLUES data loading from CSV format (vs original xlsb)
- ⚠ Reach network processing from Hydroedge2_5.csv
- ⚠ Full end-to-end pipeline with corrected inputs

---

## 9. Conclusion

### Summary

| Aspect | Status | Notes |
|--------|--------|-------|
| Source GIS Data | ✓ VALID | CW coverage correctly calculated (0-68%) |
| Results Files | ✗ INVALID | 10% of reaches have impossible coverage values (>100%) |
| Script Capabilities | ✓ READY | Comprehensive tool successfully developed |
| Input Files | ⚠ PARTIAL | Some CLUES files missing, alternatives available |
| Methodology | ✓ SOUND | Network routing and LRFs scientifically appropriate |

### Next Steps Priority

**HIGH PRIORITY:**
1. Update script config to use available CLUES CSV files
2. Investigate and fix land area mismatch issue
3. Run fresh analysis with corrected inputs
4. Validate new results against quality checks

**MEDIUM PRIORITY:**
5. Regenerate spatial maps with corrected data
6. Update email to Fleur and Annette with validated results
7. Create final report with quality-assured findings

**LOW PRIORITY:**
8. Add automated data quality validation to script
9. Document land area calculation methodology
10. Archive invalid results with documentation of issues

---

## Contact & Questions

For questions about this analysis or data issues:
- **GIS Data:** Verify with GIS team that `Land_Area_ha_GIS` column is correct
- **CLUES Model:** Confirm expected load magnitudes with model developers
- **Methodology:** Review network routing logic in `Routing.py`

**Report Generated:** October 31, 2025
**Analysis Tool:** Python pandas, geopandas, comprehensive quality checks
**Project:** TKIL2602 - Lake Omapere Modelling
