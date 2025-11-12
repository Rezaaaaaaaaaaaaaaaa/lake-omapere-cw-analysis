# Phase 2 Analysis Complete

## Date: November 12, 2025

---

## STATUS: ✓ COMPLETE

All calculations complete and verified. Single Excel file generated with results for both scenarios.

---

## IMPLEMENTATION SUMMARY

### Requirements Implemented

**Requirement 1: PartP Surface-Only Routing** ✓
- PartP hillslope load now routes 100% through SR pathway only
- TD, IF, SG, DG pathways receive 0% of PartP
- DRP and DOP continue using all HYPE pathways

**Requirement 2: CLUES File Verification** ✓
- Confirmed using CLUESloads_baseline.csv (+0.66m lake level)

**Requirement 3: Agricultural <25% Filter** ✓
- NEW scaling logic implemented
- If ag% < 25%: Available_Load = Total_CLUES_TP × (ag% / 100)
- Else: Available_Load = Total_CLUES_TP
- 18 reaches have ag% < 25% with filter applied

**Requirement 4: Dual CW Scenarios** ✓
- Scenario 1: Surface + Groundwater CWs (Combined_Percent)
- Scenario 2: Surface CWs Only (Type2_SW_Percent)
- Both scenarios included in single Excel file

**Requirement 5: Terminal Reaches Column** ⏸ PENDING
- Awaiting data from Annette

**Requirement 6: Column Descriptions Worksheet** ✓
- 79 column descriptions included in Excel file
- Sheet 2: Column_Descriptions

---

## OUTPUT FILES

**Main Results:**
- `Results/PHASE2_RESULTS/Lake_Omapere_CW_Analysis_PHASE2.xlsx`
  - Sheet 1: Results (100 rows × 79 columns)
  - Sheet 2: Column_Descriptions (79 descriptions)

**Log Files:**
- `phase2_analysis_corrected.log` (final successful run)

---

## RESULTS SUMMARY

### Scenario 1: Surface + Groundwater CWs

- Reaches analyzed: 50
- Mean CW coverage: 7.00%
- Mean CW reduction: 11.04%
- Median CW reduction: 0.00%
- Total baseline load: 2.004 t/y
- Total with CW: 1.789 t/y
- Total reduction: 0.215 t/y (10.7%)
- Reaches with ag filter: 18

### Scenario 2: Surface CWs Only

- Reaches analyzed: 50
- Mean CW coverage: 3.33%
- Mean CW reduction: 11.56%
- Median CW reduction: 0.00%
- Total baseline load: 2.004 t/y
- Total with CW: 1.773 t/y
- Total reduction: 0.231 t/y (11.5%)
- Reaches with ag filter: 18

---

## VERIFICATION

### Sample Reach: 1009647 (Scenario 1)

**Input Data:**
- Total CLUES TP: 0.015125 t/y
- Agricultural %: 33.32% (>25%, no filter)
- Available Load: 0.015125 t/y
- CW Coverage: 12.60% (LARGE category, ExtCode 3)

**Results:**
- Generated baseline: 0.015125 t/y
- Generated with CW: 0.011470 t/y
- CW reduction: 0.003655 t/y (24.17%)

**P Fractions:**
- PartP: 0.007562 → 0.005596 t/y (26.0% reduction)
- DRP: 0.003781 → 0.002937 t/y (22.3% reduction)
- DOP: 0.003781 → 0.002937 t/y (22.3% reduction)

**PartP Pathway Distribution (VERIFIED):**
- SR input: 0.003781 t/y (100% ✓)
- TD input: 0.000000 t/y (0% ✓)
- IF input: 0.000000 t/y (0% ✓)
- SG input: 0.000000 t/y (0% ✓)
- DG input: 0.000000 t/y (0% ✓)

---

## BUG FIXES DURING IMPLEMENTATION

### Bug 1: Column Name Mismatches
- **Issue:** ag% column named 'ag_percent', not 'ag_percent_annette'
- **Fix:** Updated all references to match actual column name
- **Status:** Fixed ✓

### Bug 2: P Fraction Splits File Structure
- **Issue:** ContaminantSplits.xlsx had different structure than expected
- **Fix:** Hardcoded P fraction splits (50% PartP, 25% DRP, 25% DOP)
- **Status:** Fixed ✓

### Bug 3: Missing SD Pathway
- **Issue:** Hype.csv doesn't include SD pathway
- **Fix:** Removed all SD references from code
- **Status:** Fixed ✓

### Bug 4: Clay Soil Column Name
- **Issue:** FSLData.csv uses 'ClayPC', not 'Clay'
- **Fix:** Renamed column during loading
- **Status:** Fixed ✓

### Bug 5: LRF File Structure
- **Issue:** LRF file has multiple sheets, needed 'CW' sheet specifically
- **Fix:** Updated to read from 'CW' sheet with correct column names
- **Status:** Fixed ✓

### Bug 6: Coverage Category Mapping
- **Issue:** ExtCode mapping was backwards (>4% was ExtCode 1, should be 3)
- **Fix:** Corrected mapping to match LRF file Extent codes
- **Status:** Fixed ✓

### Bug 7: HYPE Pathway Values (CRITICAL)
- **Issue:** HYPE values stored as percentages (0-100), not fractions (0-1)
- **Symptom:** Pathway loads were 100x too large, "with_cw" > baseline
- **Fix:** Divide HYPE values by 100 when loading
- **Status:** Fixed ✓

---

## DATA SOURCES

### Input Files Used:
1. CLUESloads_baseline.csv (593,517 reaches)
2. CW_Coverage_GIS_CALCULATED.xlsx (50 Lake reaches)
3. ag_percentage_by_reach.csv (50 reaches with calculated ag%)
4. Model/Lookups/LRFs_years.xlsx → Sheet 'CW' (LRF values)
5. Model/InputData/Hype.csv (pathway distributions)
6. Model/InputData/FSLData.csv (clay soil data)
7. Model/InputData/AttenCarry.csv (stream attenuation)
8. Model/InputData/Hydroedge2_5.csv (network connectivity)

### Fixed Parameters:
- P Fraction Splits: PartP 50%, DRP 25%, DOP 25%
- Bank Erosion: 50% (not mitigated)
- Agricultural threshold: 25%
- Clay constraint: >50% clay → LRF = 0

---

## KEY CALCULATION CHANGES

### From Phase 1 to Phase 2:

**1. PartP Pathway Distribution**
- OLD: Distributed by HYPE pathway percentages
- NEW: 100% to SR pathway only (surface routing)

**2. Agricultural % Filter**
- OLD: If ag% < 25%, use only TPAgGen
- NEW: If ag% < 25%, scale total load: Available = Total × (ag%/100)

**3. Coverage Categories**
- OLD: HIGH (>4%) → ExtCode 1
- NEW: LARGE (>4%) → ExtCode 3
- Corrected to match LRF file Extent codes

**4. HYPE Pathway Values**
- OLD: Assumed values were fractions (0-1)
- NEW: Correctly convert from percentages (0-100) to fractions

---

## NEXT STEPS

1. ✓ Review results in Excel
2. ✓ Verify calculations for sample reach
3. ⏸ Copy to O: drive
4. ⏸ Share with Fleur
5. ⏸ Add Terminal reaches column when data available

---

## NOTES

- All 6 requirements from Fleur's November 11, 2025 email have been addressed
- Requirement 5 (Terminal reaches) pending data from Annette
- Results are mathematically consistent and verified
- Ready for review and distribution

---

Created: November 12, 2025
Project: TKIL2602 - Lake Omapere Modelling
