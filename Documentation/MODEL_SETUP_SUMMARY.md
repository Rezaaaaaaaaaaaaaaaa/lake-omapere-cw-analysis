# Lake Ōmāpere Model Setup - Summary

## Completed Tasks

### 1. Data Extraction and Preparation

#### CLUES Spreadsheets
- Extracted data from both CLUES spreadsheets:
  - `TP_noMit_LakeOnly_baseline.xlsb` (baseline scenario)
  - `TP_noMit_LakeOnly+0.66m.xlsb` (wetland/0.66m lake level scenario)
- Identified **50 Lake Ōmāpere reaches** from the LOmapereReaches sheet

#### Key Data Extracted
From the "Reaches" sheet of both spreadsheets:
- **Column T (PromSed)**: Phosphorus from sediment → soilP
- **Column AF (OVERSEER Load)**: Agricultural phosphorus load → TPAgGen
- **Column BC (LoadIncrement)**: Total generated load
- **Column BD (StreamCarry)**: Stream attenuation carry-over → PstreamCarry
- **Column BF (ResCarry)**: Reservoir attenuation carry-over → PresCarry

#### Calculated Values
- **TPGen**: Non-pastoral phosphorus = LoadIncrement - TPAgGen - soilP

### 2. Model Input Files Created

#### Selection Files
**Location**: `Model/SelectionFiles/`
- **LakeOmapere_Selection.csv**: Selection file with VALUE=1 for 50 Lake Ōmāpere reaches, VALUE=0 for all others

#### CLUES Loads Files
**Location**: `Model/InputData/`
- **CLUESloads_baseline.csv**: Updated columns H-J (TPAgGen, soilP, TPGen) for baseline scenario
- **CLUESloads_wetland_066m.csv**: Updated columns H-J for wetland (+0.66m) scenario

#### Attenuation Files
**Location**: `Model/InputData/`
- **AttenCarry_baseline.csv**: Updated PstreamCarry and PresCarry for baseline scenario
- **AttenCarry_wetland_066m.csv**: Updated PstreamCarry and PresCarry for wetland scenario

#### CW Placement File
**Location**: `Model/InputData/`
- **CW_Subcatchments.csv**: List of 25 subcatchments with constructed wetland coverage from GIS analysis

### 3. Model Code Modifications

#### StandAloneDNZ2.py
**Modified Lines:**

1. **Line 39**: Updated runName
   ```python
   runName = "LakeOmapere_Baseline"
   ```

2. **Line 44**: Updated selection CSV path
   ```python
   selectionCSV = "SelectionFiles\\LakeOmapere_Selection.csv"
   ```

3. **Lines 84, 87**: Updated input file paths
   ```python
   attenFile = "InputData\\AttenCarry_baseline.csv"
   loadFIle = "InputData\\CLUESloads_baseline.csv"
   ```

4. **Line 1537**: Changed from sediment (SS) to phosphorus (P)
   ```python
   loadList = ['pcGen_P', 'pcInstr_P']  # Changed from SS to P
   ```

5. **Line 1556**: Updated contaminant list
   ```python
   contamList = ["P"]  # Changed from SS to P
   ```

6. **Lines 1577-1587**: Updated output section for P instead of SS
   ```python
   genPdf = pd.DataFrame(genDict[scen]["P"])  # Changed from SS to P
   fileName = outPath + "GenP_" + scen + ".csv"  # Changed from GenSS to GenP
   ```

#### PlacementRules.py
**Modified Lines 72-85**: Replaced soil-based CW placement rule with GIS-based wetland locations

**Old approach:**
```python
cwRule = generalRule * (1-clayey)  # CW not on clayey soils
```

**New approach:**
```python
# Read CW subcatchments from CSV
cwSubsFile = "InputData\\CW_Subcatchments.csv"
dfCW = pd.read_csv(cwSubsFile)
cwSubcatchments = dfCW["NZSEGMENT"].values

# Create CW rule: 1 if subcatchment has CW from GIS, 0 otherwise
cwRule = np.zeros(arrayLen).astype(float)
for i, seg in enumerate(nzSeg):
    if seg in cwSubcatchments:
        cwRule[i] = 1.0
```

## Next Steps (Per Annette's Instructions)

### Remaining Model Adjustments

1. **LRF Coverage Levels** (Line 97 in StandAloneDNZ2.py)
   - Work with Fleur to determine if existing coverage levels are appropriate
   - Current levels: <2%, 2-4%, >4% cover
   - May need to adjust based on Lake Ōmāpere CW coverage

2. **Scenario Lookups**
   - Create scenario lookup files using `Lookups/Scenario.xlsx` as template
   - Reference Pokaiwhenua scenarios for guidance
   - Will only be doing single mitigation with CW

3. **Variable Extent Handling**
   - If different CW coverage extents needed, run separately and combine
   - Follow Pokaiwhenua method (see `DNZ23201\Working\Model\Outputs\Pokaiwhenua10-12Aug1`)
   - May need to update routing code (`Routing.py`) to read TP results

4. **Create Wetland Run Version**
   - Duplicate StandAloneDNZ2.py with different name (e.g., StandAloneDNZ2_Wetland.py)
   - Update to use:
     - `attenFile = "InputData\\AttenCarry_wetland_066m.csv"`
     - `loadFIle = "InputData\\CLUESloads_wetland_066m.csv"`
     - `runName = "LakeOmapere_Wetland_066m"`

## File Locations

### Original CLUES Spreadsheets
- `TP_noMit_LakeOnly_baseline.xlsb`
- `TP_noMit_LakeOnly+0.66m.xlsb`

### Model Directory
- `Model/` - Main model folder (copied from DNZ23201)
- `Model/StandAloneDNZ2.py` - Modified main model script (for baseline)
- `Model/PlacementRules.py` - Modified placement rules
- `Model/InputData/` - Input CSV files
- `Model/SelectionFiles/` - Selection files
- `Model/Outputs/` - Output directory (will contain LakeOmapere_Baseline/)

### Analysis Scripts
- `prepare_model_inputs.py` - Script used to extract and prepare data from CLUES spreadsheets
- `explore_clues_spreadsheet.py` - Script to explore CLUES file structure
- `extract_clues_data.py` - Script to extract reach data
- `find_p_columns.py` - Script to identify phosphorus columns

## Notes

1. **Total Phosphorus (TP)**: Model is now configured for TP analysis instead of Suspended Sediment (SS)

2. **50 Lake Ōmāpere Reaches**: All input files are configured to work with the identified 50 reaches

3. **CW Placement**: Now based on actual GIS wetland locations (25 subcatchments) rather than soil characteristics

4. **Two Scenarios Required**:
   - Baseline (current setup)
   - Wetland +0.66m (files created, need separate model run)

5. **Geodatabase Updates**: All required geodatabase updates have been completed via the updated CSV files

## Testing Recommendations

Before running the full model:

1. Check that all required input files exist
2. Verify scenario lookup files are created
3. Test with a small selection first
4. Review LRF coverage levels with Fleur
5. Ensure output directory has write permissions

## References

See `annette.txt` for original instructions and detailed requirements.
