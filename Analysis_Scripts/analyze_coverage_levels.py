"""
Analyze CW coverage levels to inform LRF (Load Reduction Factor) discussions.

This script analyzes the CW coverage data to categorize subcatchments by coverage
and help determine appropriate coverage thresholds for the model.
"""

import pandas as pd
import numpy as np

# Read the corrected CW data
df = pd.read_csv('CW_Coverage_CORRECTED.csv')

print("=" * 80)
print("CW COVERAGE ANALYSIS FOR LRF CATEGORIZATION")
print("=" * 80)
print()

# Filter out subcatchments with zero land area (they're in the lake)
valid_df = df[df['Land_Area_ha'] > 0].copy()

print(f"Total subcatchments: {len(df)}")
print(f"Subcatchments with land area > 0: {len(valid_df)}")
print()

# Identify problematic subcatchments (>100% coverage)
problem_df = valid_df[valid_df['Combined_Percent'] > 100]
print(f"WARNING: Subcatchments with >100% coverage: {len(problem_df)}")
if len(problem_df) > 0:
    print("    (These have CW areas in the lake zone - need clipping)")
    for _, row in problem_df.iterrows():
        print(f"    - SC-{row['SubcatchmentID']}: {row['Combined_Percent']:.1f}%")
print()

# Filter to valid coverage values only (0-100%)
valid_coverage_df = valid_df[valid_df['Combined_Percent'] <= 100].copy()
print(f"Subcatchments with valid coverage (0-100%): {len(valid_coverage_df)}")
print()

# Analyze coverage distribution
print("=" * 80)
print("COVERAGE DISTRIBUTION (Valid subcatchments only)")
print("=" * 80)
print()

coverage = valid_coverage_df['Combined_Percent'].values

print("Coverage Statistics:")
print(f"  Mean:   {coverage.mean():.2f}%")
print(f"  Median: {np.median(coverage):.2f}%")
print(f"  Min:    {coverage.min():.2f}%")
print(f"  Max:    {coverage.max():.2f}%")
print(f"  Std:    {coverage.std():.2f}%")
print()

# Categorize using current LRF thresholds (<2%, 2-4%, >4%)
current_low = valid_coverage_df[valid_coverage_df['Combined_Percent'] < 2]
current_med = valid_coverage_df[(valid_coverage_df['Combined_Percent'] >= 2) &
                                 (valid_coverage_df['Combined_Percent'] < 4)]
current_high = valid_coverage_df[valid_coverage_df['Combined_Percent'] >= 4]

print("=" * 80)
print("CURRENT LRF THRESHOLDS (from Lookups/LRFs_years.xlsx)")
print("=" * 80)
print()
print(f"Coverage <2%:     {len(current_low)} subcatchments ({len(current_low)/len(valid_coverage_df)*100:.1f}%)")
print(f"Coverage 2-4%:    {len(current_med)} subcatchments ({len(current_med)/len(valid_coverage_df)*100:.1f}%)")
print(f"Coverage >4%:     {len(current_high)} subcatchments ({len(current_high)/len(valid_coverage_df)*100:.1f}%)")
print()

# Show subcatchments in each category
print("Subcatchments by Category:")
print()
print("LOW Coverage (<2%):")
if len(current_low) > 0:
    for _, row in current_low.iterrows():
        if row['Combined_Percent'] > 0:
            print(f"  SC-{int(row['SubcatchmentID']):2d} (nzsegment {int(row['nzsegment'])}): {row['Combined_Percent']:5.2f}%")
else:
    print("  None")
print()

print("MEDIUM Coverage (2-4%):")
if len(current_med) > 0:
    for _, row in current_med.iterrows():
        print(f"  SC-{int(row['SubcatchmentID']):2d} (nzsegment {int(row['nzsegment'])}): {row['Combined_Percent']:5.2f}%")
else:
    print("  None")
print()

print("HIGH Coverage (>4%):")
if len(current_high) > 0:
    for _, row in current_high.iterrows():
        print(f"  SC-{int(row['SubcatchmentID']):2d} (nzsegment {int(row['nzsegment'])}): {row['Combined_Percent']:5.2f}%")
else:
    print("  None")
print()

# Alternative thresholds suggestion
print("=" * 80)
print("ALTERNATIVE THRESHOLD SUGGESTIONS")
print("=" * 80)
print()

# Option 1: Tertiles
tertile_33 = np.percentile(coverage[coverage > 0], 33.33)
tertile_67 = np.percentile(coverage[coverage > 0], 66.67)
print(f"Option 1 - Tertiles (equal number of subcatchments):")
print(f"  Low:    <{tertile_33:.1f}%")
print(f"  Medium: {tertile_33:.1f}% - {tertile_67:.1f}%")
print(f"  High:   >{tertile_67:.1f}%")
print()

# Option 2: Natural breaks based on data
print(f"Option 2 - Natural breaks based on Lake Omapere data:")
print(f"  Low:    <5%")
print(f"  Medium: 5% - 25%")
print(f"  High:   >25%")
print()

# Create summary table for model input
print("=" * 80)
print("SUMMARY FOR MODEL INPUT")
print("=" * 80)
print()

# Save coverage levels to CSV for model
output_df = valid_coverage_df[['nzsegment', 'SubcatchmentID', 'Combined_Percent']].copy()
output_df = output_df.sort_values('nzsegment')

# Assign coverage category
def assign_category(pct):
    if pct < 2:
        return 'Low'
    elif pct < 4:
        return 'Medium'
    else:
        return 'High'

output_df['Coverage_Category'] = output_df['Combined_Percent'].apply(assign_category)

# Save to file
output_file = 'CW_Coverage_Categories.csv'
output_df.to_csv(output_file, index=False)
print(f"[SAVED] Coverage categories saved to: {output_file}")
print()

# Print summary
print("Coverage category distribution:")
print(output_df['Coverage_Category'].value_counts().sort_index())
print()

print("=" * 80)
print("RECOMMENDATION FOR FLEUR")
print("=" * 80)
print()
print("The current LRF thresholds (<2%, 2-4%, >4%) result in:")
print(f"  - Most subcatchments ({len(current_high)}) in the HIGH category")
print(f"  - Very few subcatchments ({len(current_med)}) in the MEDIUM category")
print(f"  - Some subcatchments ({len(current_low)}) in the LOW category")
print()
print("Consider discussing whether:")
print("  1. The current thresholds are appropriate for Lake Omapere")
print("  2. Alternative thresholds would better represent the mitigation gradient")
print("  3. Different LRF values should be used for the >100% subcatchments")
print("     (once the lake clipping issue is resolved)")
print()
print("=" * 80)
