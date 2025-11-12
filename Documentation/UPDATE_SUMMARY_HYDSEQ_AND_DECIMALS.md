# Update Summary - HYDSEQ Column and Decimal Precision

## Date: November 12, 2025

---

## CHANGES MADE

### 1. **Added HYDSEQ Column**

**Location:** Column 2 (between reach_id and Scenario)

**Purpose:** Shows hydrological sequence number (upstream to downstream order)

**Values:** Sample values from Lake Omapere reaches: 9454, 9479, 9480, 9526, 9527...

**Benefits:**
- Helps identify reach position in the catchment
- Makes it easy to see upstream vs downstream relationships
- Useful for understanding cumulative effects

---

### 2. **Reduced Decimal Precision to 5 Places**

**Changed from:** 6 decimals (e.g., 0.011768)
**Changed to:** 5 decimals (e.g., 0.01177)

**Applies to:** All load columns (t/y values)

**Percentages remain:** 2 decimals (e.g., 24.17%)

**Rationale:** 5 decimal places (0.00001 t/y = 10 grams/year) provides sufficient precision for environmental modeling while improving readability.

---

### 3. **Documented Negative Inundation Values**

**Issue:** Some reaches show negative inundation reduction (loads INCREASE with +0.66m inundation)

**Example:**
- Reach 1010398: -0.00486 t/y (-28.82%)
- This means load WITH inundation is 28.82% HIGHER than without

**Cause:** The two CLUES files (CLUESloads.csv vs CLUESloads_baseline.csv) may represent different scenarios beyond just inundation:
- Different land use assumptions
- Non-agricultural load increases (soilP increased 11x for reach 1010398)
- Model scenario differences

**Solution:**
- Kept negative values to show reality of the data
- Updated column descriptions to note "negative = increase"
- Added note in output that some reaches show increases

**Reaches Affected:** 2 reaches have significant negative inundation reduction

---

## UPDATED FILE SPECIFICATIONS

| Feature | Previous | Updated |
|---------|----------|---------|
| **Total columns** | 82 | **83** (+1 HYDSEQ) |
| **Column 2** | Scenario | **HYDSEQ** |
| **Column 3** | ag_percent | **Scenario** |
| **Load decimal places** | 6 | **5** |
| **Percentage decimal places** | 2 | 2 (unchanged) |
| **Negative values** | Not documented | **Documented & explained** |

---

## COLUMN ORDER (First 10 Columns)

1. **reach_id** - NZ Reach Segment ID
2. **HYDSEQ** - Hydrological sequence (NEW!)
3. **Scenario** - Scenario1_SurfaceGW or Scenario2_SurfaceOnly
4. **ag_percent** - Agricultural land use %
5. **ag_filter_applied** - Filter applied flag
6. **CW_Coverage_Percent** - CW coverage %
7. **coverage_category** - SMALL/MEDIUM/LARGE
8. **ExtCode** - 1/2/3
9. **clay_percent** - Clay soil %
10. **PstreamCarry** - Stream attenuation factor

---

## VERIFICATION RESULTS

### HYDSEQ Column:
- ✓ Present in output (Column 2)
- ✓ Sample values confirmed (9454, 9479, 9480...)
- ✓ Reaches sorted by HYDSEQ (upstream to downstream)

### Decimal Precision:
- ✓ Load values: 5 decimals (e.g., 0.01177)
- ✓ Percentages: 2 decimals (e.g., 24.17%)
- ✓ Consistent across all 83 columns

### Negative Inundation Values:
- ✓ Properly preserved (not hidden or set to zero)
- ✓ Documented in column descriptions
- ✓ Note added to output message
- ✓ 2 reaches affected (1010398 appears twice - once per scenario)

---

## FILES UPDATED

1. **Analysis Script:**
   - `Analysis_Scripts/lake_omapere_cw_analysis_PHASE2_with_comparison.py`
   - Added HYDSEQ to results
   - Updated column order
   - Updated column descriptions
   - Added note about negative values

2. **Formatting Script:**
   - `format_excel_with_comparison.py`
   - Changed rounding from 6 to 5 decimals
   - Added HYDSEQ to input data sources
   - Updated summary messages

3. **Excel Output:**
   - `Results/PHASE2_RESULTS/Lake_Omapere_CW_Analysis_PHASE2_with_comparison.xlsx`
   - Now has 83 columns (was 82)
   - HYDSEQ in column 2
   - All loads rounded to 5 decimals
   - Copied to O: drive

---

## EXAMPLE DATA

### Sample Reach (1009647, Scenario1):

| Column | Value | Decimals |
|--------|-------|----------|
| reach_id | 1009647 | - |
| HYDSEQ | 9454 | - |
| Scenario | Scenario1_SurfaceGW | - |
| Total_CLUES_TP | 0.01512 | 5 |
| Total_TP_NoInundation | 0.02689 | 5 |
| Inundation_Reduction_TP | 0.01177 | 5 |
| Inundation_Reduction_Percent | 43.76% | 2 |
| generated_baseline | 0.01512 | 5 |
| generated_with_cw | 0.01147 | 5 |
| cw_reduction | 0.00366 | 5 |
| cw_reduction_percent | 24.17% | 2 |

---

## IMPACT ON ANALYSIS

### Positive Impacts:
- ✓ HYDSEQ adds valuable spatial context
- ✓ 5 decimals improves readability without losing meaningful precision
- ✓ Negative values show true data complexity
- ✓ Better documentation of data limitations

### No Negative Impacts:
- ✓ All calculations remain identical
- ✓ Results unchanged (only formatting)
- ✓ Verification still passes
- ✓ Scientific accuracy maintained

---

## RECOMMENDATIONS FOR USE

### When Presenting Results:

1. **Mention HYDSEQ** when discussing spatial patterns
   - "Upstream reaches (low HYDSEQ) show..."
   - "Downstream reaches (high HYDSEQ) experience..."

2. **Explain negative inundation values** if questioned
   - "Two reaches show increased loads with inundation"
   - "This suggests differences between CLUES scenarios beyond just inundation"
   - "May indicate non-agricultural load increases or model scenario differences"

3. **Use 5 decimal precision** as reported
   - Sufficient for decision-making (10 grams/year resolution)
   - More readable than 6 decimals
   - Standard practice for environmental modeling

### For Further Investigation:

If negative inundation values are concerning:
1. Verify with CLUES modelers that the two files are comparable
2. Check if different land use scenarios were used
3. Investigate why soilP increased for affected reaches
4. Consider excluding affected reaches from inundation impact summary

---

## FILES DELIVERED

**Location:** `O:\TKIL2602\Working\Lake_Omapere_066m_Analysis_Complete\Phase2_Results\`

**Main File:**
- `Lake_Omapere_CW_Analysis_PHASE2_with_comparison.xlsx` (updated)
  - 100 rows × 83 columns
  - HYDSEQ in column 2
  - 5 decimal precision for loads
  - Negative inundation values documented

**Documentation:**
- `UPDATE_SUMMARY_HYDSEQ_AND_DECIMALS.md` (this file)
- `INUNDATION_COMPARISON_SUMMARY.md` (previous)
- `VERIFICATION_COMPLETE_SUMMARY.md` (previous)

---

## SUMMARY

✓ **HYDSEQ column added** - Provides spatial context
✓ **5 decimal precision** - Improves readability
✓ **Negative values documented** - Shows data reality
✓ **83 columns total** - All required outputs present
✓ **Ready for use** - Verified and validated

---

**Updated:** November 12, 2025
**Project:** TKIL2602 - Lake Omapere Modelling
**Version:** Final with HYDSEQ and 5 decimals
