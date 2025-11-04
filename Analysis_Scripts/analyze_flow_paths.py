"""
Analyze flow path contributions by subcatchment
Identifies subcatchments with >50% flow from tile drains, interflow, shallow GW
"""

import pandas as pd
import os
from datetime import datetime

print("[STARTING] Flow Path Analysis")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# For this analysis, we need flow path data from CLUES model
# This data should be in the CLUES spreadsheets or model outputs

print("\n[INFO] Looking for flow path data in CLUES spreadsheets...")

# Load CLUES data
clues_file = "Model/InputData/CLUESloads_baseline.csv"
try:
    clues_data = pd.read_csv(clues_file)
    print(f"Loaded CLUES data: {len(clues_data)} reaches")
    print(f"Columns available: {clues_data.columns.tolist()}")
except Exception as e:
    print(f"Error loading CLUES data: {e}")

# Check if we have flow path information in the spreadsheets
# According to documentation, flow path data should be in the Excel files
clues_xlsx_baseline = "CLUES_Data/TP_noMit_LakeOnly_baseline.xlsb"
clues_xlsx_wetland = "CLUES_Data/TP_noMit_LakeOnly+0.66m.xlsb"

print(f"\nCLUES Excel files for reference:")
print(f"  Baseline: {clues_xlsx_baseline}")
print(f"  Wetland: {clues_xlsx_wetland}")

# Create flow path analysis
output_dir = "Results/02_FlowPathAnalysis"
os.makedirs(output_dir, exist_ok=True)

# Create a placeholder analysis with guidance
analysis_text = """
===============================================================================
LAKE OMAPERE - FLOW PATH ANALYSIS (PLACEHOLDER)
===============================================================================

Generated: {datetime}

OBJECTIVE:
  Identify subcatchments where dissolved P dominates inflows due to >50% flow
  from tile drains, interflow, and shallow groundwater.
  Per Fleur's requirements: Zero P removal in these areas (dissolved P not
  removed by CW).

DATA REQUIRED:
  This analysis requires flow path contribution data from the CLUES model:

  1. Tile drain flow percentage (TileDrainPC)
  2. Interflow percentage (InterflowPC)
  3. Shallow groundwater flow percentage (ShallowGWPC)
  4. Per reach (NZSEGMENT) or per subcatchment

  These values should sum to 100% for total flow path contributions.

CLUES DATA SOURCES:
  1. Baseline model: CLUES_Data/TP_noMit_LakeOnly_baseline.xlsb
     - Check worksheets for flow path data by reach
     - Look for columns: TileDrain%, Interflow%, ShallowGW%, Baseflow%

  2. Wetland model: CLUES_Data/TP_noMit_LakeOnly+0.66m.xlsb
     - Same structure, updated for +0.66m lake level

NEXT STEPS:
  1. Extract flow path percentages from CLUES spreadsheets
  2. Map reaches to subcatchments
  3. Calculate: HighFlowPC = TileDrain% + Interflow% + ShallowGW%
  4. Flag subcatchments where HighFlowPC > 50%
  5. Create FlowPath_Analysis_by_Reach.csv
  6. Create HighFlowPath_Reaches_Over50Percent.csv

DISSOLVED P CONSIDERATION:
  - Dissolved P dominates where high proportion of flow is from tile drains
  - CW primarily removes particulate P, not dissolved P
  - Therefore: Set P_removal = 0 for these reaches
  - This constraint applies in addition to clay soil constraint

ACTION:
  1. Extract flow path data from CLUES Excel files
  2. Run analysis to identify affected reaches
  3. Integrate with PlacementRules.py

CONTACTS:
  - Annette Semadeni-Davies: For CLUES model interpretation
  - Fleur Matheson: For P removal performance assumptions

===============================================================================
""".format(datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

with open(f"{output_dir}/FlowPath_Analysis_README.txt", "w") as f:
    f.write(analysis_text)

print(f"\n[SAVED] {output_dir}/FlowPath_Analysis_README.txt")

# Create a template for what the analysis should contain
template = """NZSEGMENT,TileDrainPC,InterflowPC,ShallowGWPC,TotalHighFlowPC,HighFlow_Over50Percent
1000001,15.5,18.2,22.1,55.8,YES
1000002,8.3,12.5,15.2,36.0,NO
1000003,25.3,28.5,22.1,76.0,YES
1000004,5.2,8.9,9.1,23.2,NO
1000005,12.4,15.2,18.9,46.5,NO
"""

with open(f"{output_dir}/FlowPath_Analysis_Template.csv", "w") as f:
    f.write(template)

print(f"[SAVED] {output_dir}/FlowPath_Analysis_Template.csv (template)")

print(f"\n[STATUS] Flow Path Analysis - PLACEHOLDER")
print("  This requires extraction from CLUES Excel spreadsheets.")
print("  A template has been created for the expected output format.")
print(f"\n[COMPLETED] Flow Path Analysis Setup")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
