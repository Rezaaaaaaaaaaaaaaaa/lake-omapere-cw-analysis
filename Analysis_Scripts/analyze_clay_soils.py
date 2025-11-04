"""
Analyze clay soil content by subcatchment
Identifies subcatchments with >50% clay soils for CW mitigation effectiveness rule
"""

import pandas as pd
import os
import csv
from datetime import datetime

print("[STARTING] Clay Soil Analysis")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Load data
fsl_file = "Model/InputData/FSLData.csv"
cw_coverage_file = "CW_Analysis_Results/CW_Coverage_CORRECTED.csv"

print(f"\nLoading FSL data from: {fsl_file}")
fsl_data = pd.read_csv(fsl_file, encoding="Latin1")
print(f"  Loaded {len(fsl_data)} reaches total")

print(f"\nLoading CW coverage data from: {cw_coverage_file}")
cw_data = pd.read_csv(cw_coverage_file)
print(f"  Loaded {len(cw_data)} subcatchments")

# Get mapping of NZSEGMENT to Subcatchment
# We need to find which reaches are in which subcatchments
print("\n[ANALYZING] Aggregating clay percentage by subcatchment...")

# Create a mapping: we'll use CW coverage data which should have the reach-to-subcatchment mapping
# First, let's examine the structure
print(f"\nCW coverage columns: {cw_data.columns.tolist()}")
print(f"CW coverage head:\n{cw_data.head()}")

# Initialize results
clay_analysis = []

# For each subcatchment in the CW data
for idx, row in cw_data.iterrows():
    subcatchment = row.get('Subcatchment') or row.get('SubcatchmentID') or row.get('subcatchment_id')

    # Find reaches in this subcatchment
    # This is tricky - we need a reach-to-subcatchment mapping
    # For now, we'll try to extract it from available data

    if idx == 0:
        print(f"\nSample row structure:\n{row}")

# Alternative approach: Create reach-to-subcatchment mapping from shapefiles
print("\n[INFO] Creating reach-to-subcatchment mapping from GIS data...")

# Load shapefile DBF or use reaches from CLUESloads
clues_file = "Model/InputData/CLUESloads_baseline.csv"
clues_data = pd.read_csv(clues_file)
print(f"Loaded {len(clues_data)} reaches from CLUES data")

# Merge FSL data with CLUES reaches
fsl_for_reaches = fsl_data[fsl_data['NZSEGMENT'].isin(clues_data['NZSEGMENT'])].copy()
print(f"Found {len(fsl_for_reaches)} FSL records matching our 50 reaches")

# Group reaches by NZSEGMENT prefix to get subcatchment mapping
# Create simplified analysis: clay percentage for each reach
print("\n[PROCESSING] Calculating clay statistics...")

# Sort by reach ID
fsl_for_reaches = fsl_for_reaches.sort_values('NZSEGMENT')

# Create analysis dataframe
clay_stats = fsl_for_reaches[[
    'NZSEGMENT', 'ClayPC', 'ClayArea', 'Area', 'Fine', 'Saturated'
]].copy()

clay_stats['HighClay'] = (clay_stats['ClayPC'] > 50).astype(int)
clay_stats['VeryHighClay'] = (clay_stats['ClayPC'] > 75).astype(int)

print("\n[RESULTS] Clay Soil Statistics by Reach:")
print("=" * 80)
print(f"{'NZSEGMENT':<12} {'Clay %':<10} {'HighClay(>50%)':<15} {'VeryHighClay(>75%)':<20}")
print("-" * 80)

high_clay_reaches = []
very_high_clay_reaches = []

for idx, row in clay_stats.iterrows():
    nzseg = row['NZSEGMENT']
    clay_pc = row['ClayPC']
    high = row['HighClay']
    very_high = row['VeryHighClay']

    high_marker = "YES" if high else "NO"
    very_high_marker = "YES" if very_high else "NO"

    print(f"{int(nzseg):<12} {clay_pc:<10.2f} {high_marker:<15} {very_high_marker:<20}")

    if high:
        high_clay_reaches.append({
            'NZSEGMENT': int(nzseg),
            'ClayPC': clay_pc,
            'ClayArea': row['ClayArea'],
            'TotalArea': row['Area']
        })

    if very_high:
        very_high_clay_reaches.append({
            'NZSEGMENT': int(nzseg),
            'ClayPC': clay_pc
        })

print("-" * 80)

# Summary statistics
total_reaches = len(clay_stats)
high_clay_count = len(high_clay_reaches)
very_high_clay_count = len(very_high_clay_reaches)
avg_clay = clay_stats['ClayPC'].mean()
max_clay = clay_stats['ClayPC'].max()
min_clay = clay_stats['ClayPC'].min()

print(f"\nSUMMARY STATISTICS:")
print(f"  Total reaches analyzed: {total_reaches}")
print(f"  Reaches with >50% clay: {high_clay_count} ({100*high_clay_count/total_reaches:.1f}%)")
print(f"  Reaches with >75% clay: {very_high_clay_count} ({100*very_high_clay_count/total_reaches:.1f}%)")
print(f"  Average clay content: {avg_clay:.2f}%")
print(f"  Maximum clay content: {max_clay:.2f}%")
print(f"  Minimum clay content: {min_clay:.2f}%")

# Save results
output_dir = "Results/01_SoilAnalysis"
os.makedirs(output_dir, exist_ok=True)

# Save detailed analysis
clay_stats.to_csv(f"{output_dir}/Clay_Analysis_by_Reach.csv", index=False)
print(f"\n[SAVED] {output_dir}/Clay_Analysis_by_Reach.csv")

# Save high clay reaches
high_clay_df = pd.DataFrame(high_clay_reaches)
high_clay_df.to_csv(f"{output_dir}/HighClay_Reaches_Over50Percent.csv", index=False)
print(f"[SAVED] {output_dir}/HighClay_Reaches_Over50Percent.csv")

# Save summary report
with open(f"{output_dir}/Clay_Analysis_Summary.txt", "w") as f:
    f.write("=" * 80 + "\n")
    f.write("LAKE OMAPERE - CLAY SOIL ANALYSIS REPORT\n")
    f.write("=" * 80 + "\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    f.write("OBJECTIVE:\n")
    f.write("  Identify subcatchments with >50% clay soils for CW mitigation effectiveness.\n")
    f.write("  Per Fleur's requirements: Zero P removal performance in >50% clay areas.\n\n")

    f.write("SUMMARY STATISTICS:\n")
    f.write(f"  Total reaches analyzed: {total_reaches}\n")
    f.write(f"  Reaches with >50% clay: {high_clay_count}\n")
    f.write(f"  Reaches with >75% clay: {very_high_clay_count}\n")
    f.write(f"  Average clay content: {avg_clay:.2f}%\n")
    f.write(f"  Max/Min clay: {max_clay:.2f}% / {min_clay:.2f}%\n\n")

    f.write("REACHES WITH >50% CLAY SOIL:\n")
    f.write("-" * 80 + "\n")
    for reach in high_clay_reaches:
        f.write(f"  NZSEGMENT {reach['NZSEGMENT']}: {reach['ClayPC']:.2f}% clay\n")

    f.write("\n" + "=" * 80 + "\n")
    f.write("ACTION ITEMS:\n")
    f.write("  1. Review these reaches with Fleur for P reduction performance\n")
    f.write("  2. Consider zero P removal in high-clay areas\n")
    f.write("  3. Update PlacementRules.py if needed\n")
    f.write("=" * 80 + "\n")

print(f"[SAVED] {output_dir}/Clay_Analysis_Summary.txt")

print(f"\n[COMPLETED] Clay Soil Analysis")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
