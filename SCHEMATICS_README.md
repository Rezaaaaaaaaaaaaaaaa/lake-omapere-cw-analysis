# Lake Ōmāpere Project Schematics - PDF Guide
**File:** `Lake_Omapere_Project_Schematics.pdf`
**Generated:** October 30, 2025
**Pages:** 6
**Size:** 80 KB

---

## Overview

This PDF contains comprehensive schematics and diagrams showing the complete architecture, data flows, and processing logic of the Lake Ōmāpere Constructed Wetland (CW) mitigation project.

---

## PAGE 1: Overall Project Architecture

**Title:** Lake Ōmāpere CW Mitigation Project - Overall Architecture & Data Flow

### Content:
Shows the complete end-to-end flow of the project:

1. **Input Sources:**
   - CLUES Spreadsheets (Baseline & +0.66m lake levels)
   - GIS Shapefiles (CW Sites, Lake boundaries)

2. **Data Processing:**
   - Extract TP Loads from CLUES
   - Calculate CW Coverage by Subcatchment
   - Update Attenuation factors

3. **Model Configuration:**
   - Selection CSV (50 reaches)
   - Placement Rules (CW from GIS)
   - Scenario Lookups (LRF thresholds)

4. **Models:**
   - StandAloneDNZ2.py (Baseline)
   - StandAloneDNZ2_Wetland066m.py (Wetland)
   - LakeOmapere_Routing_Template.py (Routing)

5. **Outputs:**
   - Baseline Results
   - Wetland Scenario Results
   - Analysis Results

---

## PAGE 2: Model Input Files & Data Structure

**Title:** Model Input Files & Data Structure

### Content:
Details of all input data files used by the models:

#### CLUESloads Files:
- `CLUESloads_baseline.csv`
- `CLUESloads_wetland_066m.csv`
- **Columns:** TPAgGen, soilP, TPGen, TPps
- **Purpose:** Total Phosphorus loads by reach

#### Attenuation Files:
- `AttenCarry_baseline.csv`
- `AttenCarry_wetland_066m.csv`
- **Columns:** PstreamCarry, PresCarry (by reach)
- **Purpose:** TP attenuation/retention factors

#### Selection & Coverage Files:
- `LakeOmapere_Selection.csv` - 50 reaches selection
- `CW_Subcatchments.csv` - CW coverage % for 34 subcatchments

#### Scenario Configuration:
- `Scenarios_LakeOmapere.xlsx` - 3 LRF scenarios (<2%, 2-4%, >4%)
- `LRFs_years.xlsx` - LRF values by coverage level and time period

---

## PAGE 3: Model Configuration & Processing Logic

**Title:** Model Configuration & Processing Logic

### Content:
Shows side-by-side comparison of two model runs:

#### BASELINE MODEL (Left):
1. **Input:** Current lake area, no CW mitigation
2. **Configuration:** Load baseline CSVs, set reach selection, initialize GIS
3. **Placement Rules:** Identify eligible subcatchments, set mitigation = 0
4. **Calculation:** Baseline loads, reach routing, attenuation, no reduction
5. **Output:** GenSS TP by reach, load increments, concentrations

#### WETLAND SCENARIO MODEL (Right):
1. **Input:** Lake area +0.66m, with CW mitigation
2. **Configuration:** Load wetland CSVs, updated attenuation, new lake GIS
3. **Placement Rules:** Override rule - if CW in GIS → mitigation=1, else 0
4. **Calculation:** With CW removal, apply LRF values based on coverage %, attenuation
5. **Output:** GenSS TP (reduced), removal efficiency, concentrations

#### Comparison & Analysis:
Compares baseline vs wetland scenario to calculate load reduction and percentage changes

---

## PAGE 4: Complete Data Flow & Processing Pipeline

**Title:** Complete Data Flow & Processing Pipeline - From CLUES to Final Analysis

### Content:
Hierarchical data flow diagram showing all processing stages:

#### SOURCE DATA (Top):
- CLUES Spreadsheets
- GIS Shapefiles
- Field Surveys

#### DATA PREPARATION:
- Extract TP Loads by Reach
- Calculate CW Coverage by Subcatchment
- Update Attenuation Factors

#### MODEL CONFIGURATION:
- Create Selection CSV
- Setup Placement Rules

#### MODEL EXECUTION:
- StandAloneDNZ2.py (Baseline Model Run)
- StandAloneDNZ2_Wetland066m.py (Wetland Model Run)

#### ANALYSIS & OUTPUTS:
- Baseline Results (TP Loads)
- Comparison & Analysis (Reductions)
- Routing & Reporting (Maps/Tables)

---

## PAGE 5: Scenario Comparison & Analysis Strategy

**Title:** Scenario Comparison & Analysis Strategy - Baseline vs Wetland CW Mitigation

### Content:
Detailed breakdown of the two scenarios being modeled:

#### SCENARIO 1: BASELINE
- **Lake Area:** Current
- **CW Status:** No implementation, no TP removal
- **Model Configuration:** Current CLUES loads, baseline attenuation
- **Processing:** No mitigation, standard routing
- **Outputs:** Baseline TP loads, reach concentrations

#### SCENARIO 2: WETLAND (CW MITIGATION)
- **Lake Area:** +0.66m
- **CW Status:** Surface & groundwater CW with removal
- **Model Configuration:** Updated CLUES loads, revised attenuation, new lake GIS
- **Processing:** Apply CW placement rules, select LRF by coverage %
- **Outputs:** Reduced TP loads, removal efficiency

#### COMPARISON & ANALYSIS:
For each reach:
- Load difference = Baseline - Wetland
- % reduction = (Difference / Baseline) × 100
- Concentration change (mg/L)
- Effectiveness by subcatchment

#### KEY PERFORMANCE INDICATORS:
- Total TP load reduction (tonnes/year)
- % reduction by subcatchment
- Reaches with >50% reduction
- Cost-effectiveness analysis

---

## PAGE 6: Project Directory Structure & Output Files

**Title:** Project Directory Structure & Output Files

### Content:
Complete visual representation of project organization:

#### MAIN DIRECTORIES:
1. **Model/** - Model scripts and configurations
2. **CLUES_Data/** - CLUES spreadsheet inputs
3. **Analysis_Scripts/** - Python analysis utilities
4. **Documentation/** - Project documentation

#### MODEL SUBDIRECTORIES:
- **InputData/** - CLUESloads, AttenCarry CSV files
- **SelectionFiles/** - Reach selection CSVs
- **Lookups/** - Scenarios and LRF configurations
- **Outputs/** - Model results and generated loads

#### KEY SCRIPTS:
- StandAloneDNZ2.py (Baseline model)
- StandAloneDNZ2_Wetland066m.py (Wetland scenario)
- LakeOmapere_Routing_Template.py (Routing analysis)
- PlacementRules.py (CW placement logic)

#### OUTPUT FILES GENERATED:
- GenSS_Baseline.csv - Baseline TP loads
- GenSS_Wetland.csv - Wetland scenario TP
- TP_Reduction.csv - Load reduction values
- Comparison.xlsx - Scenario comparison

#### ARCHIVE SECTION:
- Model_DNZ_OriginalTemplate/ - Old DNZ template files (not used)

#### PROJECT STATISTICS:
- 7 active Python scripts
- 20+ CSV & Excel data files
- 15+ GIS shapefiles
- 10+ documentation files
- ~500 MB total project size

---

## How to Use This PDF

1. **Quick Overview:** Start with Page 1 (Architecture)
2. **Input Details:** Refer to Page 2 (Input Files) when examining model inputs
3. **Running Models:** Use Page 3 (Configuration) when executing scripts
4. **Data Source:** Use Page 4 (Data Flow) to trace data from source to output
5. **Scenario Planning:** Use Page 5 (Comparison) to understand scenario differences
6. **File Management:** Use Page 6 (Directory) to locate specific files

---

## Related Documents

For additional information, see:
- `LAKE_OMAPERE_MODEL_READY.md` - Complete model setup guide
- `PROJECT_STATUS.md` - Project status and outstanding issues
- `QUICK_START.txt` - Quick reference guide
- `COMPLETION_REPORT.md` - Work completed summary

---

## Contact Information

- **Analyst:** Reza Moghaddam (Reza.Moghaddam@niwa.co.nz)
- **Reviewer:** Annette Semadeni-Davies (Annette.Davies@niwa.co.nz)
- **Project Lead:** Fleur Matheson (Fleur.Matheson@niwa.co.nz)

---

## Technical Notes

- All diagrams created using matplotlib (Python)
- Color coding: Blue (processes), Orange (outputs), Green (scenarios), Purple (data)
- PDF is vector-based for high-quality printing
- Scalable to any paper size without quality loss

---

**Generated:** October 30, 2025
**Project:** TKIL2602 - Lake Ōmāpere Model Setup
**Status:** Production Ready
