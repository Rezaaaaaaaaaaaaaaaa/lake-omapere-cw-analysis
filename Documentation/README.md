# Reza's CW Analysis Workspace
**Project:** TKIL2602 - Lake Ōmāpere Modelling
**Task:** Calculate % of sub-catchment area occupied by potential CW sites

---

## Task Overview

Calculate the percentage of sub-catchment area occupied by potential Constructed Wetland (CW) sites for:
1. **Type 1 - Groundwater fed wetlands** (separately)
2. **Type 2 - Surface water fed wetlands** (separately)
3. **Combined** (both types together)

---

## Shapefiles Provided

### CW Sites (in `Shapefiles/CW_Sites/`)

1. **MaxDepth to GW 1m_WL-20%tile(+0.66)_clipped_v2.shp**
   - Groundwater fed wetlands (Type 1)
   - Areas where shallow groundwater is predicted to be within 1m of ground surface 80% of the time
   - Suitable for CWs intercepting mostly subsurface flows

2. **Lake Omapere Catchment- topographic depressions_clipped_v2.shp**
   - Surface water fed wetlands (Type 2)
   - Areas with topographic depressions
   - Suitable for CWs intercepting mostly surface flows

### Sub-catchments (in `Shapefiles/Subcatchments/`)

- **Subs.shp** - Sub-catchment boundaries for the Lake Omapere catchment

### Reference Files (in `Shapefiles/Reference/`)

- **Catchment.shp** - Overall catchment boundary
- **Riverlines.shp** - River network

---

## Analysis Requirements

For each sub-catchment, calculate:

1. **Total sub-catchment area** (m² or hectares)
2. **Area of Type 1 CW sites** within the sub-catchment
3. **Area of Type 2 CW sites** within the sub-catchment
4. **Area of Combined CW sites** (union of Type 1 and Type 2)
5. **Percentage calculations:**
   - % Type 1 = (Area Type 1 / Total sub-catchment area) × 100
   - % Type 2 = (Area Type 2 / Total sub-catchment area) × 100
   - % Combined = (Area Combined / Total sub-catchment area) × 100

---

## Important Notes

- Regardless of CW type (Type 1 or Type 2), assume they intercept all flowpaths operating in each sub-catchment:
  - Surface runoff
  - Surface drains
  - Tile drains
  - Interflow
  - Shallow groundwater

- When combining Type 1 and Type 2, use **spatial union** to avoid double-counting overlapping areas

---

## Output Format

The results should be saved as a CSV or Excel file with columns:

| SubcatchmentID | Subcatchment_Area_ha | Type1_Area_ha | Type1_Percent | Type2_Area_ha | Type2_Percent | Combined_Area_ha | Combined_Percent |
|----------------|---------------------|---------------|---------------|---------------|---------------|------------------|------------------|
| ...            | ...                 | ...           | ...           | ...           | ...           | ...              | ...              |

---

## Getting Started

1. Run the setup script to organize files:
   ```bash
   python setup_reza_workspace.py
   ```

2. Use the analysis script template:
   ```bash
   python calculate_cw_percentages.py
   ```

3. Review results in the `Results/` folder

---

## Contact

- **Fleur Matheson** - Project Lead
- **Annette Semadeni-Davies** - GIS Support

---

## References

- Meeting notes: `O:\TKIL2602\Working\Lake Omapere Trust\Team meeting notes\TKIL2602 Omapere_ Meeting notes_13_October_2025.docx`
- Source files: `O:\TKIL2602\Working\Lake Omapere Trust\From WWLA\`
