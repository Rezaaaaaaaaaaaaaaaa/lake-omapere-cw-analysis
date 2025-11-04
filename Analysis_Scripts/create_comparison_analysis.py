"""
Compare baseline and wetland scenario model results
Generate analysis of CW effectiveness
"""

import pandas as pd
import os
from datetime import datetime

print("[STARTING] Comparison Analysis")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

output_dir = "Results/06_Comparison"
os.makedirs(output_dir, exist_ok=True)

try:
    # Look for model outputs
    print("\n[INFO] Searching for model outputs...")

    model_outputs = []
    for root, dirs, files in os.walk("Model/Outputs"):
        for file in files:
            if file.endswith(".csv") and ("GenSS" in file or "generated" in file):
                full_path = os.path.join(root, file)
                model_outputs.append(full_path)
                print(f"  Found: {full_path}")

    if not model_outputs:
        print("\n[WARNING] No model output files found yet (models still running)")
        print("  Outputs will be at: Model/Outputs/")

    # Create placeholder comparison report
    report_text = """
===============================================================================
LAKE OMAPERE - CW MITIGATION EFFECTIVENESS ANALYSIS
===============================================================================

Generated: {datetime}
Status: BASELINE & WETLAND MODEL RESULTS - COMPARISON ANALYSIS

PROJECT OVERVIEW:
  Scenario 1: Baseline (no CW implementation)
    - Current lake area
    - No TP removal from wetlands
    - Natural attenuation only

  Scenario 2: Wetland Mitigation (CW implementation)
    - Lake area +0.66m
    - CW coverage based on GIS analysis
    - P removal efficiency based on LRF thresholds
    - Zero performance in >50% clay soils (Fleur requirement)
    - Zero performance in >50% interflow areas (Fleur requirement)

DATA SOURCES:
  Baseline Model Output: Model/Outputs/*Baseline*.csv
  Wetland Model Output: Model/Outputs/*Wetland*.csv

COMPARISON METRICS:
  1. Total TP Load Reduction (tonnes/year)
     = SUM(Baseline TP) - SUM(Wetland TP)

  2. Percentage Reduction by Reach
     = (Baseline_TP - Wetland_TP) / Baseline_TP * 100

  3. Reach-by-Reach Effectiveness
     - Reaches with >50% reduction
     - Reaches with >75% reduction
     - Reaches with minimal effectiveness (clay/interflow)

  4. Subcatchment-Level Analysis
     - Average reduction per subcatchment
     - Total catchment reduction
     - Variation by reach

CLAY SOIL CONSTRAINT:
  Applied Zero P Removal in:
  {high_clay_count} reaches with >50% clay content
  See Results/01_SoilAnalysis/ for details

INTERFLOW CONSTRAINT:
  Applied Zero P Removal in:
  - Reaches with >50% dissolved P inflow
  - Requires extraction from CLUES model
  See Results/02_FlowPathAnalysis/ for details

NEXT STEPS:
  1. Verify model runs completed successfully
  2. Load GenSS output files
  3. Merge baseline and wetland results
  4. Calculate reduction metrics
  5. Create visualization plots
  6. Generate final summary report

FILES TO GENERATE:
  - TP_Load_Comparison.csv
  - Reduction_by_Reach.csv
  - Reduction_Summary.txt
  - Effectiveness_Plot.png
  - Reduction_Maps.png

CONTACT:
  Reza Moghaddam - reza.moghaddam@niwa.co.nz

===============================================================================
""".format(
        datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        high_clay_count=0  # Will be updated when clay analysis loads
    )

    with open(f"{output_dir}/Comparison_Analysis_README.txt", "w") as f:
        f.write(report_text)

    print(f"\n[SAVED] {output_dir}/Comparison_Analysis_README.txt")

    # Create a template for expected comparison output
    template_csv = """NZSEGMENT,Baseline_TP_tpy,Wetland_TP_tpy,TP_Reduction_tpy,Reduction_Percent,EffectivenessCat
1000002,45.23,22.15,23.08,51.0,Medium
1000003,67.45,0.00,67.45,100.0,Very_High_Clay
1000004,54.12,18.99,35.13,64.9,High
1000005,78.56,0.00,78.56,100.0,Very_High_Clay
"""

    with open(f"{output_dir}/Comparison_Template.csv", "w") as f:
        f.write(template_csv)

    print(f"[SAVED] {output_dir}/Comparison_Template.csv (template)")

    print(f"\n[STATUS] Comparison Analysis - Framework Ready")
    print("  Awaiting model output files...")
    print(f"\n[COMPLETED] Comparison Analysis Setup")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

except Exception as e:
    print(f"\n[ERROR] Comparison analysis setup failed: {e}")
    import traceback
    traceback.print_exc()
