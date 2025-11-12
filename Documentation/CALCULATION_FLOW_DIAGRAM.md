# Lake Omapere CW Analysis - Calculation Flow Diagram

## Date: November 12, 2025

---

## SIMPLIFIED FLOW

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INPUT DATA FILES                             │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      STEP 1: LOAD CLUES DATA                        │
│  CLUESloads_baseline.csv (+0.66m lake level)                        │
│  ─────────────────────────────────────────────                      │
│  TPAgGen + soilP + TPGen = Total_CLUES_TP                          │
│                                                                      │
│  Example: 0.009746 + 0.001940 + 0.003440 = 0.015125 t/y            │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│               STEP 2: APPLY AGRICULTURAL % FILTER (NEW!)            │
│  LakeAreaUpdate_ASD.xlsx → Column BY                                │
│  ─────────────────────────────────────────────                      │
│  IF ag% < 25%:                                                      │
│    Available_Load = Total_CLUES_TP × (ag% / 100)                   │
│  ELSE:                                                              │
│    Available_Load = Total_CLUES_TP                                 │
│                                                                      │
│  Example: ag% = 65.33% → Available = 0.015125 t/y (no scaling)     │
│  Example: ag% = 15.00% → Available = 0.015125 × 0.15 = 0.002269    │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  STEP 3: SPLIT INTO P FRACTIONS                     │
│  ContaminantSplits.xlsx                                             │
│  ─────────────────────────────────────────────                      │
│  PartP = Available_Load × 50%                                       │
│  DRP   = Available_Load × 25%                                       │
│  DOP   = Available_Load × 25%                                       │
│                                                                      │
│  Example: PartP = 0.015125 × 0.50 = 0.007563 t/y                   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│             STEP 4: SPLIT INTO BANK EROSION vs HILLSLOPE            │
│  Fixed: 50% / 50%                                                   │
│  ─────────────────────────────────────────────                      │
│  For each P fraction:                                               │
│    Bank_Erosion = P_fraction × 50%  (NOT mitigated)                │
│    Hillslope    = P_fraction × 50%  (goes to pathways)             │
│                                                                      │
│  Example PartP:                                                     │
│    Bank = 0.007563 × 0.50 = 0.003781 t/y (passes through)          │
│    Hill = 0.007563 × 0.50 = 0.003781 t/y (to pathways)             │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│            STEP 5: DISTRIBUTE BY HYPE PATHWAYS (NEW LOGIC!)         │
│  Hype.csv → SR, TD, IF, SG, DG, SD percentages                     │
│  ─────────────────────────────────────────────                      │
│  PartP (SURFACE ONLY - NEW!):                                       │
│    PartP_SR = Hillslope × 100%  (ALL to SR)                        │
│    PartP_TD = 0  (NOT ALLOWED)                                      │
│    PartP_IF = 0  (NOT ALLOWED)                                      │
│    PartP_SG = 0  (NOT ALLOWED)                                      │
│    PartP_DG = 0  (NOT ALLOWED)                                      │
│                                                                      │
│  DRP & DOP (ALL PATHWAYS):                                          │
│    DRP_SR = Hillslope × SR%                                         │
│    DRP_TD = Hillslope × TD%                                         │
│    DRP_IF = Hillslope × IF%                                         │
│    ... etc for all pathways                                         │
│                                                                      │
│  Example PartP:                                                     │
│    PartP_SR = 0.003781 × 1.0 = 0.003781 t/y (ALL here!)            │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│              STEP 6: APPLY LOAD REDUCTION FACTORS (LRFs)            │
│  LRFs_years.xlsx + CW_Coverage_GIS_CALCULATED.xlsx                  │
│  ─────────────────────────────────────────────                      │
│  Coverage Category:                                                 │
│    HIGH (>4%)   → ExtCode 1 → 77% removed (23% remains)            │
│    MEDIUM (2-4%)→ ExtCode 2 → 58% removed (42% remains)            │
│    LOW (<2%)    → ExtCode 3 → 52% removed (48% remains)            │
│                                                                      │
│  Clay Constraint:                                                   │
│    IF Clay% > 50% → LRF = 0 (no effectiveness)                     │
│                                                                      │
│  TWO SCENARIOS:                                                     │
│    Scenario 1: Use Combined_Percent (Surface + GW CWs)             │
│    Scenario 2: Use Type2_SW_Percent (Surface CWs only)             │
│                                                                      │
│  Example PartP_SR (HIGH coverage, ExtCode 1):                       │
│    Load in = 0.003781 t/y                                           │
│    LRF = 23% remaining (77% removed)                                │
│    Removed = 0.003781 × 0.77 = 0.002911 t/y                        │
│    Remaining = 0.003781 × 0.23 = 0.000870 t/y                      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  STEP 7: SUM ALL PATHWAY OUTPUTS                    │
│  ─────────────────────────────────────────────                      │
│  Total_TP_with_CW = Bank_Erosion + Sum(Remaining from all pathways)│
│                                                                      │
│  Example PartP:                                                     │
│    Bank_Erosion:   0.003781 t/y                                     │
│    SR_remaining:   0.000870 t/y                                     │
│    TD_remaining:   0.000000 t/y                                     │
│    ... etc                                                          │
│    ─────────────────────────                                        │
│    Total PartP:    0.004651 t/y                                     │
│                                                                      │
│  Total_TP = PartP + DRP + DOP (with CW)                            │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   STEP 8: APPLY STREAM ATTENUATION                  │
│  AttenCarry.csv → PstreamCarry                                      │
│  Hydroedge2_5.csv → Network connectivity                            │
│  ─────────────────────────────────────────────                      │
│  Route downstream:                                                  │
│    Routed_Load = Generated_Load × PstreamCarry                     │
│                                                                      │
│  Example:                                                           │
│    Generated = 0.015125 t/y                                         │
│    PstreamCarry = 0.9735                                            │
│    Routed = 0.015125 × 0.9735 = 0.014723 t/y                       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         OUTPUT DATA FILES                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## DETAILED INPUT/OUTPUT MAPPING

### INPUT FILES (10 files)

```
1. CLUESloads_baseline.csv (593,517 reaches)
   ├─ NZSEGMENT
   ├─ TPAgGen  ────────┐
   ├─ soilP    ────────┼──→ Total_CLUES_TP
   └─ TPGen    ────────┘

2. LakeAreaUpdate_ASD.xlsx
   └─ Column BY ──────────→ ag_percent (NEW!)

3. CW_Coverage_GIS_CALCULATED.xlsx
   ├─ Type1_GW_Percent ──→ Scenario 1 (with Type2_SW)
   ├─ Type2_SW_Percent ──→ Scenario 2 (alone)
   └─ Combined_Percent ──→ Scenario 1

4. ContaminantSplits.xlsx
   ├─ PartP: 50% ────────┐
   ├─ DRP:   25% ────────┼──→ P fractions
   └─ DOP:   25% ────────┘

5. Hype.csv
   ├─ SR  ─────────────┐
   ├─ TD  ─────────────┤
   ├─ IF  ─────────────┼──→ Pathway distribution
   ├─ SG  ─────────────┤
   ├─ DG  ─────────────┤
   └─ SD  ─────────────┘

6. LRFs_years.xlsx
   ├─ ExtCode 1, 2, 3 ─┐
   ├─ Pathway         ─┼──→ Load reduction factors
   └─ PartP/DRP/DOP   ─┘

7. FSLData.csv
   └─ Clay% ──────────────→ If >50%, LRF = 0

8. Hydroedge2_5.csv
   ├─ FROM_NODE ──────────┐
   └─ TO_NODE ────────────┼──→ Network routing

9. AttenCarry.csv
   └─ PstreamCarry ───────→ In-stream loss

10. Bank Erosion
    └─ 50% (fixed) ────────→ Non-mitigated portion
```

### OUTPUT FILES

```
SCENARIO 1: Surface + Groundwater CWs
├─ Lake_Omapere_CW_Analysis_Scenario1_SurfaceGW.csv
├─ Lake_Omapere_CW_Analysis_Scenario1_SurfaceGW.xlsx
│  ├─ Sheet 1: Results (50 reaches × ~120 columns)
│  └─ Sheet 2: Column Descriptions
└─ Maps and Figures (5 PNG files)

SCENARIO 2: Surface CWs Only
├─ Lake_Omapere_CW_Analysis_Scenario2_SurfaceOnly.csv
├─ Lake_Omapere_CW_Analysis_Scenario2_SurfaceOnly.xlsx
│  ├─ Sheet 1: Results (50 reaches × ~120 columns)
│  └─ Sheet 2: Column Descriptions
└─ Maps and Figures (5 PNG files)

SUMMARY FILES
├─ analysis_summary_scenario1.json
├─ analysis_summary_scenario2.json
├─ scenario_comparison.xlsx
└─ PHASE_2_COMPLETE.md
```

---

## KEY OUTPUT COLUMNS

```
Identification:
  ├─ reach_id
  ├─ Scenario ("Surface+GW" or "Surface_Only")
  └─ ag_percent (from Column BY)

Loads:
  ├─ Total_CLUES_TP (before ag filter)
  ├─ Available_Load (after ag filter if <25%)
  ├─ generated_baseline
  ├─ generated_with_cw
  ├─ cw_reduction
  └─ cw_reduction_percent

CW Coverage:
  ├─ Type2_SW_Percent (Surface only)
  ├─ Combined_Percent (Surface + GW)
  ├─ CW_Coverage_Percent (which one used for this scenario)
  └─ coverage_category (HIGH/MEDIUM/LOW)

By P Fraction:
  ├─ generated_baseline_PartP/DRP/DOP
  ├─ generated_with_cw_PartP/DRP/DOP
  └─ cw_reduction_PartP/DRP/DOP

By Pathway:
  ├─ PartP_SR, PartP_TD, PartP_IF, etc.
  ├─ DRP_SR, DRP_TD, DRP_IF, etc.
  └─ DOP_SR, DOP_TD, DOP_IF, etc.

Routing:
  ├─ routed_baseline
  ├─ routed_with_cw
  └─ routed_reduction_percent

Constraints:
  ├─ clay_percent
  ├─ ag_filter_applied (TRUE/FALSE)
  └─ Terminal_066m (when available)
```

---

## CALCULATION SUMMARY

```
INPUT: Raw loads from CLUES
   ↓
FILTER: Agricultural % scaling (if <25%)
   ↓
SPLIT: Into P fractions (50% / 25% / 25%)
   ↓
SPLIT: Into Bank Erosion (50%) vs Hillslope (50%)
   ↓
DISTRIBUTE: By pathways
   ├─ PartP → SURFACE ONLY (100% to SR)
   └─ DRP/DOP → ALL pathways (by HYPE %)
   ↓
MITIGATE: Apply LRFs by coverage category
   ├─ Scenario 1: Use Combined_Percent
   └─ Scenario 2: Use Type2_SW_Percent
   ↓
SUM: Bank Erosion + Remaining from all pathways
   ↓
ROUTE: Apply in-stream attenuation (PstreamCarry)
   ↓
OUTPUT: Results for 50 reaches × 2 scenarios
```

---

Created: November 12, 2025
Project: TKIL2602 - Lake Omapere Modelling
