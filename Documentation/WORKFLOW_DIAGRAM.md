# Lake Omapere CW Analysis - Data Flow Workflow

## Complete Processing Pipeline: Input → Output

```mermaid
flowchart TB
    subgraph INPUT["📁 INPUT DATA FILES"]
        CLUES1["CLUESloads_baseline.csv<br/>(WITH +0.66m inundation)<br/>TPAgGen + soilP + TPGen"]
        CLUES2["CLUESloads.csv<br/>(WITHOUT inundation)<br/>TPAgGen + soilP + TPGen"]
        CW["CW_Coverage_GIS_CALCULATED.xlsx<br/>Combined_Percent<br/>Type2_SW_Percent"]
        AG["ag_percentage_by_reach.csv<br/>Agricultural %"]
        HYPE["Hype.csv<br/>Pathway percentages<br/>(SR, TD, IF, SG, DG)"]
        LRF["LRFs_years.xlsx<br/>Load Reduction Factors<br/>(ExtCode 1/2/3)"]
        CLAY["FSLData.csv<br/>Clay percentage<br/>(>50% constraint)"]
        ATTEN["AttenCarry.csv<br/>PstreamCarry<br/>(stream attenuation)"]
    end

    subgraph STEP1["STEP 1: DATA LOADING & MERGING"]
        MERGE["Merge all datasets by NZSEGMENT<br/>Sort by HYDSEQ"]
        INUND["Calculate Inundation Impact:<br/>Inundation_Reduction_TP =<br/>Total_TP_NoInundation - Total_CLUES_TP"]
    end

    subgraph STEP2["STEP 2: AGRICULTURAL FILTER"]
        AGFILTER["Check: ag_percent < 25%?"]
        SCALE["YES: Available_Load =<br/>Total_CLUES_TP × (ag%/100)"]
        NOSCALE["NO: Available_Load =<br/>Total_CLUES_TP"]
    end

    subgraph STEP3["STEP 3: P FRACTION SPLITS"]
        PSPLIT["Split Available_Load into:<br/>PartP (50%)<br/>DRP (25%)<br/>DOP (25%)"]
        BANK["Bank Erosion Split (50%):<br/>Not mitigated by CW"]
        HILL["Hillslope Load (50%):<br/>Available for CW mitigation"]
    end

    subgraph STEP4A["STEP 4A: PATHWAY DISTRIBUTION"]
        PARTP["PartP Pathways:<br/>100% → SR only<br/>(Surface-only routing)"]
        DRPDOP["DRP/DOP Pathways:<br/>Use HYPE % distribution<br/>(SR, TD, IF, SG, DG)"]
    end

    subgraph STEP4B["STEP 4B: CW MITIGATION"]
        EXTCODE["Determine ExtCode:<br/>SMALL=1, MEDIUM=2, LARGE=3<br/>Based on CW_Coverage_%"]
        CLAYLRF["Check Clay Constraint:<br/>clay% > 50% → LRF = 0<br/>clay% ≤ 50% → Use LRF table"]
        CWCALC["For each pathway:<br/>removed = input × LRF<br/>remaining = input × (1 - LRF)"]
    end

    subgraph STEP4C["STEP 4C: COMBINE RESULTS"]
        COMBINE["Combine pathway results:<br/>baseline = bank_erosion + hillslope<br/>with_cw = bank_erosion + pathway_remaining<br/>reduction = baseline - with_cw"]
    end

    subgraph STEP5["STEP 5: ROUTING TO LAKE"]
        ROUTE["Apply stream attenuation:<br/>routed_baseline = generated_baseline × PstreamCarry<br/>routed_with_cw = generated_with_cw × PstreamCarry<br/>routed_reduction = routed_baseline - routed_with_cw"]
    end

    subgraph SCENARIOS["🔀 DUAL SCENARIOS"]
        SC1["Scenario 1: Surface + GW<br/>Uses Combined_Percent"]
        SC2["Scenario 2: Surface Only<br/>Uses Type2_SW_Percent"]
    end

    subgraph OUTPUT["📊 OUTPUT FILES"]
        EXCEL["Lake_Omapere_CW_Analysis_PHASE2_with_comparison.xlsx<br/>100 rows × 83 columns<br/>Sheets: Results + Column_Descriptions"]
        FORMAT["Formatted with:<br/>- 5 decimal precision (loads)<br/>- 2 decimal precision (percentages)<br/>- Scenario-based row coloring<br/>- HYDSEQ ordering"]
        ODRIVE["Copied to O: drive:<br/>Phase2_Results folder"]
    end

    subgraph VALIDATION["✓ VALIDATION"]
        VALID["47 verification checks:<br/>- PartP 100% to SR<br/>- Clay constraint<br/>- No over-reduction (>100%)<br/>- No illogical negatives<br/>- P fraction sums"]
    end

    %% Connections - Input to Step 1
    CLUES1 --> MERGE
    CLUES2 --> MERGE
    CW --> MERGE
    AG --> MERGE
    HYPE --> MERGE
    LRF --> MERGE
    CLAY --> MERGE
    ATTEN --> MERGE

    CLUES1 --> INUND
    CLUES2 --> INUND

    %% Step 1 to Step 2
    MERGE --> AGFILTER
    INUND --> AGFILTER

    %% Step 2 branches
    AGFILTER -->|"ag% < 25%"| SCALE
    AGFILTER -->|"ag% ≥ 25%"| NOSCALE
    SCALE --> PSPLIT
    NOSCALE --> PSPLIT

    %% Step 3
    PSPLIT --> BANK
    PSPLIT --> HILL

    %% Step 4
    HILL --> PARTP
    HILL --> DRPDOP
    PARTP --> EXTCODE
    DRPDOP --> EXTCODE
    EXTCODE --> CLAYLRF
    CLAYLRF --> CWCALC
    CWCALC --> COMBINE
    BANK --> COMBINE

    %% Step 5
    COMBINE --> ROUTE

    %% Scenarios
    ROUTE --> SC1
    ROUTE --> SC2

    %% Output
    SC1 --> EXCEL
    SC2 --> EXCEL
    EXCEL --> FORMAT
    FORMAT --> ODRIVE

    %% Validation
    EXCEL --> VALID

    style INPUT fill:#e1f5ff
    style STEP1 fill:#fff4e1
    style STEP2 fill:#ffe1f5
    style STEP3 fill:#e1ffe1
    style STEP4A fill:#f5e1ff
    style STEP4B fill:#f5e1ff
    style STEP4C fill:#f5e1ff
    style STEP5 fill:#ffe1e1
    style SCENARIOS fill:#fff9c4
    style OUTPUT fill:#c8e6c9
    style VALIDATION fill:#b2dfdb
```

---

## Processing Summary

### Input Layer (8 files)
- **2 CLUES files** for inundation comparison
- **CW coverage data** (2 scenarios)
- **Agricultural percentages**
- **Pathway distributions** (HYPE)
- **Mitigation factors** (LRF)
- **Soil constraints** (Clay)
- **Stream routing** (Attenuation)

### Processing Pipeline

1. **Merge & Compare** → Calculate inundation impact (33.51% average reduction)
2. **Filter** → Apply agricultural 25% threshold (18 reaches affected)
3. **Split** → Divide into P fractions (PartP 50%, DRP 25%, DOP 25%) and sources (Bank/Hillslope)
4. **Distribute** → Route through pathways (**PartP special: 100% to SR only**)
5. **Mitigate** → Apply CW effectiveness with clay constraint (>50% → LRF=0)
6. **Route** → Apply stream attenuation to calculate lake delivery

### Dual Scenarios
- **Scenario 1:** Surface + GW (Combined_Percent coverage)
- **Scenario 2:** Surface Only (Type2_SW_Percent coverage)

### Output (83 columns)
- Identification & Scenario (3 cols)
- Input parameters (7 cols)
- **Inundation comparison (4 cols)** ← NEW!
- Generated/routed loads (12 cols)
- P fractions detail (57 cols)

### Final Result
**50 reaches × 2 scenarios = 100 output rows** with complete traceability from source data to final results.

---

**Date:** November 12, 2025
**Project:** TKIL2602 - Lake Omapere Modelling
**Version:** Phase 2 with Inundation Comparison
