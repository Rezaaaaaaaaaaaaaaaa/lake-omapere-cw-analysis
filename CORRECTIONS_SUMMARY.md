# CW Analysis Corrections Summary

**Date:** 2025-10-20
**Prepared by:** Reza Moghaddam
**Requested by:** Annette Semadeni-Davies & Fleur Matheson

## Corrections Applied

Based on Annette's email dated 2025-10-20, the following corrections have been applied to the CW coverage analysis:

### 1. Added NZSegment Column ✓
- **Requirement:** Include nzsegment number for indexing
- **Why:** Required for CLUES and mitigation model applications
- **Status:** Complete - nzsegment column now included as first column

### 2. Ordered Data by HydSeq ✓
- **Requirement:** Order by HydSeq in ascending order
- **Why:** Flow sequence from headwaters to coast; ensures reaches have consistent positions for reading input data
- **Status:** Complete - all 50 subcatchments now ordered by HydSeq (9454 to 10697)

### 3. Updated Area Calculations ✓
- **Requirement:** Use Annette's land area calculations that exclude lake area
- **Source:** `O:\TKIL2602\Working\Lake Omapere Trust\CLUES_SS_NRC_2020\LakeAreaUpdate.xlsx` (Column 73: "AREALand (HA)")
- **Why:** Original calculations included lake area; need to calculate CW coverage as % of land area only
- **Status:** Complete - Land areas updated and all percentages recalculated

### 4. Recalculated CW Coverage Percentages ✓
- **Change:** CW areas now calculated as % of corrected land area (excluding lake)
- **Status:** Complete

## Output Files

### Corrected Files:
1. **C:\Users\moghaddamr\Reza_CW_Analysis\CW_Coverage_CORRECTED.csv**
2. **C:\Users\moghaddamr\Reza_CW_Analysis\CW_Coverage_CORRECTED.xlsx**
3. **O:\TKIL2602\Working\Lake Omapere Trust\CW_Analysis_Results\CW_Coverage_CORRECTED.csv**
4. **O:\TKIL2602\Working\Lake Omapere Trust\CW_Analysis_Results\CW_Coverage_CORRECTED.xlsx**

### Reference File (copied to project):
- **C:\Users\moghaddamr\Reza_CW_Analysis\LakeAreaUpdate.xlsx** (Annette's calculations)

## Data Structure

| Column | Description |
|--------|-------------|
| nzsegment | NZ Segment identifier (required for CLUES) |
| HydSeq | Hydrological sequence number (headwaters to coast) |
| SubcatchmentID | Subcatchment ID (0-49) |
| Land_Area_ha | Land area excluding lake (from Annette's calculations) |
| Type1_GW_Area_ha | Type 1 groundwater-fed CW area (ha) |
| Type1_GW_Percent | Type 1 coverage (% of land area) |
| Type2_SW_Area_ha | Type 2 surface water-fed CW area (ha) |
| Type2_SW_Percent | Type 2 coverage (% of land area) |
| Combined_Area_ha | Combined CW area (ha) |
| Combined_Percent | Combined coverage (% of land area) |

## Summary Statistics

- **Total subcatchments:** 50
- **Total land area (excluding lake):** 1,267.36 ha
- **Total Type1 GW area:** 91.49 ha
- **Total Type2 SW area:** 68.75 ha
- **Total Combined CW area:** 128.36 ha

For subcatchments with land area > 1 ha (29 subcatchments):
- **Average Type1 GW coverage:** 9.17%
- **Average Type2 SW coverage:** 6.32%
- **Average Combined coverage:** 12.96%

## Verification Example

**Subcatchment 5** (matches Annette's example of 24.03 ha):
- nzsegment: 1009728
- HydSeq: 9526
- Land Area: 24.03 ha (matches Annette's calculation)
- Type1 Coverage: 20.72%
- Type2 Coverage: 1.04%
- Combined Coverage: 21.31%

## Notes and Observations

### Subcatchments with Very Small Land Areas
Several subcatchments have very small or zero land areas after excluding lake area:
- SC-0: 0.04 ha (mostly lake)
- SC-1: 0.00 ha (entirely lake)
- SC-3: 0.59 ha (mostly lake)
- SC-16: 0.00 ha (entirely lake)

These subcatchments show very high or undefined CW coverage percentages, which may need special handling in the mitigation model.

### Potential CW Areas in Lake Zone
Some subcatchments show CW areas larger than the available land area, suggesting that some potential CW sites identified in the original analysis may be located in areas that would be inundated with the +0.66m lake level. This should be reviewed with Fleur and Annette.

## Next Steps

1. Review corrected data with Annette and Fleur
2. Confirm handling of subcatchments with very small land areas
3. Consider whether CW areas need to be clipped to exclude lake zone areas
4. Proceed with MSCMM modeling using corrected data

## Questions for Discussion

1. How should we handle subcatchments that are mostly or entirely lake?
2. Should potential CW areas be re-clipped to exclude the +0.66m lake area?
3. Any additional corrections needed before proceeding with CLUES/MSCMM?
