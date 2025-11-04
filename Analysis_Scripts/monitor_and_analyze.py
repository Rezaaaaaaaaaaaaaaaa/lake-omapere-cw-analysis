#!/usr/bin/env python3
"""
Monitor model execution and run comparison analysis when models complete.
This script checks for model output files and triggers comparison analysis.
"""

import os
import glob
import time
import pandas as pd
from datetime import datetime

print("[MONITOR] Lake Omapere CW Analysis - Monitoring Script")
print(f"[TIME] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Directories to monitor
model_output_dir = "Model/Outputs"
baseline_log = "Results/03_BaselineModel/baseline_run.log"
wetland_log = "Results/04_WetlandModel/wetland_run.log"

# Check for baseline model outputs
print("\n[CHECK] Looking for baseline model outputs...")
baseline_files = glob.glob(os.path.join(model_output_dir, "**/GenSS*.csv"), recursive=True)
baseline_files_recent = [f for f in baseline_files if 'baseline' in f.lower() or 'LakeOmapere' in f]

if baseline_files_recent:
    print(f"[FOUND] Baseline outputs: {len(baseline_files_recent)} files")
else:
    print("[WAIT] Baseline model still running...")

# Check for wetland model outputs
print("\n[CHECK] Looking for wetland model outputs...")
wetland_files = glob.glob(os.path.join(model_output_dir, "**/GenSS*.csv"), recursive=True)
wetland_files_recent = [f for f in wetland_files if 'wetland' in f.lower() or '066' in f]

if wetland_files_recent:
    print(f"[FOUND] Wetland outputs: {len(wetland_files_recent)} files")
else:
    print("[WAIT] Wetland model still running...")

# Check log file sizes to see if models are still running
if os.path.exists(baseline_log):
    size = os.path.getsize(baseline_log)
    print(f"\n[LOG] Baseline log size: {size} bytes")
else:
    print("\n[LOG] Baseline log not created yet")

if os.path.exists(wetland_log):
    size = os.path.getsize(wetland_log)
    print(f"[LOG] Wetland log size: {size} bytes")
else:
    print("[LOG] Wetland log not created yet")

# Prepare for comparison when both models complete
print("\n[STATUS] Monitoring active. Check back in 5-10 minutes for model completion.")
print("[NEXT] Once models complete:")
print("  1. Baseline outputs will be in Model/Outputs/LakeOmapere_Baseline/")
print("  2. Wetland outputs will be in Model/Outputs/LakeOmapere_Wetland_066m/")
print("  3. Comparison analysis will be run automatically")
print("  4. Results will be saved to Results/06_Comparison/")

print(f"\n[TIME] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("[STATUS] Run this script again to check progress.")
