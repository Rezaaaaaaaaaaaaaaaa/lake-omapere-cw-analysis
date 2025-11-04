#!/usr/bin/env python3
"""
Lake Omapere CW Mitigation Analysis - Complete Pipeline
Analyzes ONLY the 50 Lake Omapere subcatchments
Compares baseline vs. wetland scenario with CW mitigation
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

print("="*80)
print("LAKE OMAPERE CW MITIGATION ANALYSIS")
print("="*80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Create output directories
output_base = "Results/LAKE_OMAPERE_FINAL"
os.makedirs(output_base, exist_ok=True)
os.makedirs(f"{output_base}/Data", exist_ok=True)
os.makedirs(f"{output_base}/Figures", exist_ok=True)
os.makedirs(f"{output_base}/Summary", exist_ok=True)

print("[1/10] Loading Lake Omapere reach selection...")
# Load Lake Omapere subcatchments
cw_coverage = pd.read_csv("CW_Analysis_Results/CW_Coverage_CORRECTED.csv")
lake_omapere_reaches = cw_coverage['nzsegment'].values
print(f"  Found {len(lake_omapere_reaches)} Lake Omapere subcatchments")
print(f"  Reach range: {lake_omapere_reaches.min()} to {lake_omapere_reaches.max()}")

print("\n[2/10] Loading baseline CLUES loads...")
# Load baseline TP loads
clues_baseline = pd.read_csv("Model/InputData/CLUESloads_baseline.csv")
clues_baseline_lake = clues_baseline[clues_baseline['NZSEGMENT'].isin(lake_omapere_reaches)].copy()
print(f"  Loaded {len(clues_baseline_lake)} reaches")
print(f"  TP columns: {[col for col in clues_baseline_lake.columns if 'TP' in col]}")

print("\n[3/10] Loading wetland CLUES loads (+0.66m scenario)...")
# Load wetland TP loads
clues_wetland = pd.read_csv("Model/InputData/CLUESloads_wetland_066m.csv")
clues_wetland_lake = clues_wetland[clues_wetland['NZSEGMENT'].isin(lake_omapere_reaches)].copy()
print(f"  Loaded {len(clues_wetland_lake)} reaches")

print("\n[4/10] Loading attenuation factors...")
# Load attenuation factors
atten_baseline = pd.read_csv("Model/InputData/AttenCarry_baseline.csv")
atten_wetland = pd.read_csv("Model/InputData/AttenCarry_wetland_066m.csv")
print(f"  Baseline attenuation: {len(atten_baseline)} reaches")
print(f"  Wetland attenuation: {len(atten_wetland)} reaches")

print("\n[5/10] Loading clay soil constraints...")
# Load clay analysis
clay_analysis = pd.read_csv("Results/01_SoilAnalysis/Clay_Analysis_by_Reach.csv")
high_clay = pd.read_csv("Results/01_SoilAnalysis/HighClay_Reaches_Over50Percent.csv")
high_clay_reaches = set(high_clay['NZSEGMENT'].astype(int).values)
print(f"  Total high-clay reaches (>50%): {len(high_clay_reaches)}")

# Check which Lake Omapere reaches have high clay
lake_omapere_high_clay = [r for r in lake_omapere_reaches if r in high_clay_reaches]
print(f"  Lake Omapere reaches with >50% clay: {len(lake_omapere_high_clay)}")

print("\n[6/10] Calculating baseline TP loads...")
# Calculate total TP for baseline
if 'TPGen' in clues_baseline_lake.columns:
    baseline_tp_col = 'TPGen'
elif 'TPAgGen' in clues_baseline_lake.columns:
    baseline_tp_col = 'TPAgGen'
else:
    print("  WARNING: Using first TP column found")
    baseline_tp_col = [col for col in clues_baseline_lake.columns if 'TP' in col][0]

clues_baseline_lake['TP_Baseline_tpy'] = clues_baseline_lake[baseline_tp_col]
print(f"  Using column: {baseline_tp_col}")
print(f"  Total baseline TP: {clues_baseline_lake['TP_Baseline_tpy'].sum():.2f} tonnes/year")
print(f"  Mean per reach: {clues_baseline_lake['TP_Baseline_tpy'].mean():.2f} tpy")
print(f"  Range: {clues_baseline_lake['TP_Baseline_tpy'].min():.2f} - {clues_baseline_lake['TP_Baseline_tpy'].max():.2f} tpy")

print("\n[7/10] Applying CW mitigation to wetland scenario...")
# Calculate wetland TP with CW mitigation
clues_wetland_lake['TP_Wetland_tpy'] = clues_wetland_lake[baseline_tp_col]

# Merge with CW coverage data
results = clues_baseline_lake[['NZSEGMENT', 'TP_Baseline_tpy']].copy()
results = results.merge(
    cw_coverage[['nzsegment', 'SubcatchmentID', 'Land_Area_ha', 'Combined_Area_ha', 'Combined_Percent']],
    left_on='NZSEGMENT',
    right_on='nzsegment',
    how='left'
)
results = results.merge(
    clues_wetland_lake[['NZSEGMENT', 'TP_Wetland_tpy']],
    on='NZSEGMENT',
    how='left'
)

# Add clay constraint
results['HighClay_Over50Pct'] = results['NZSEGMENT'].isin(high_clay_reaches)

# Apply CW removal based on coverage
# LRF values (Load Reduction Factors) from literature:
# <2% coverage: 20% removal
# 2-4% coverage: 35% removal
# >4% coverage: 50% removal
# But ZERO removal if high clay (>50%)

def apply_cw_mitigation(row):
    if row['HighClay_Over50Pct']:
        # Zero removal in high-clay areas
        return row['TP_Wetland_tpy'], 0.0, "HighClay_ZeroRemoval"

    cw_pct = row['Combined_Percent']

    if pd.isna(cw_pct) or cw_pct == 0:
        # No CW coverage
        return row['TP_Wetland_tpy'], 0.0, "NoCW"
    elif cw_pct < 2:
        # Low coverage: 20% removal
        removal_factor = 0.20
        category = "LowCW_<2pct"
    elif cw_pct < 4:
        # Medium coverage: 35% removal
        removal_factor = 0.35
        category = "MediumCW_2-4pct"
    else:
        # High coverage: 50% removal
        removal_factor = 0.50
        category = "HighCW_>4pct"

    tp_after_cw = row['TP_Wetland_tpy'] * (1 - removal_factor)
    removal_pct = removal_factor * 100

    return tp_after_cw, removal_pct, category

results[['TP_Wetland_WithCW_tpy', 'CW_Removal_Pct', 'CW_Category']] = results.apply(
    lambda row: pd.Series(apply_cw_mitigation(row)), axis=1
)

print(f"  Applied CW mitigation to {len(results)} reaches")
print(f"  CW categories distribution:")
for cat in results['CW_Category'].value_counts().items():
    print(f"    {cat[0]}: {cat[1]} reaches")

print("\n[8/10] Calculating load reductions...")
# Calculate reductions
results['TP_Reduction_tpy'] = results['TP_Baseline_tpy'] - results['TP_Wetland_WithCW_tpy']
results['Reduction_Percent'] = (results['TP_Reduction_tpy'] / results['TP_Baseline_tpy'] * 100).fillna(0)

# Summary statistics
total_baseline = results['TP_Baseline_tpy'].sum()
total_wetland = results['TP_Wetland_WithCW_tpy'].sum()
total_reduction = results['TP_Reduction_tpy'].sum()
overall_reduction_pct = (total_reduction / total_baseline * 100)

print(f"\n  SUMMARY STATISTICS:")
print(f"  Total Baseline TP Load: {total_baseline:.2f} tonnes/year")
print(f"  Total Wetland TP Load (with CW): {total_wetland:.2f} tonnes/year")
print(f"  Total TP Reduction: {total_reduction:.2f} tonnes/year")
print(f"  Overall Reduction: {overall_reduction_pct:.1f}%")
print(f"\n  Reaches with >25% reduction: {(results['Reduction_Percent'] > 25).sum()}")
print(f"  Reaches with >50% reduction: {(results['Reduction_Percent'] > 50).sum()}")
print(f"  Reaches with zero reduction (constrained): {(results['Reduction_Percent'] == 0).sum()}")

print("\n[9/10] Generating visualizations...")

# Figure 1: TP Load Comparison
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Lake Omapere CW Mitigation Analysis', fontsize=16, fontweight='bold')

# Subplot 1: Total loads comparison
ax1 = axes[0, 0]
load_data = pd.DataFrame({
    'Scenario': ['Baseline', 'Wetland+CW'],
    'TP_Load_tpy': [total_baseline, total_wetland]
})
ax1.bar(load_data['Scenario'], load_data['TP_Load_tpy'], color=['#E74C3C', '#27AE60'])
ax1.set_ylabel('Total TP Load (tonnes/year)', fontsize=11)
ax1.set_title('Total TP Load: Baseline vs. Wetland+CW', fontsize=12, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)
for i, v in enumerate(load_data['TP_Load_tpy']):
    ax1.text(i, v + 1, f'{v:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# Subplot 2: Reduction by CW category
ax2 = axes[0, 1]
category_summary = results.groupby('CW_Category').agg({
    'TP_Reduction_tpy': 'sum',
    'NZSEGMENT': 'count'
}).reset_index()
category_summary.columns = ['Category', 'Reduction_tpy', 'Count']
ax2.bar(range(len(category_summary)), category_summary['Reduction_tpy'], color='#3498DB')
ax2.set_xticks(range(len(category_summary)))
ax2.set_xticklabels(category_summary['Category'], rotation=45, ha='right', fontsize=9)
ax2.set_ylabel('TP Reduction (tonnes/year)', fontsize=11)
ax2.set_title('TP Reduction by CW Category', fontsize=12, fontweight='bold')
ax2.grid(axis='y', alpha=0.3)

# Subplot 3: Reduction percentage distribution
ax3 = axes[1, 0]
reduction_bins = [0, 10, 25, 50, 100]
reduction_labels = ['0-10%', '10-25%', '25-50%', '>50%']
results['Reduction_Bin'] = pd.cut(results['Reduction_Percent'], bins=reduction_bins, labels=reduction_labels, include_lowest=True)
reduction_dist = results['Reduction_Bin'].value_counts().sort_index()
ax3.bar(range(len(reduction_dist)), reduction_dist.values, color='#F39C12')
ax3.set_xticks(range(len(reduction_dist)))
ax3.set_xticklabels(reduction_dist.index, fontsize=10)
ax3.set_ylabel('Number of Reaches', fontsize=11)
ax3.set_xlabel('Reduction Percentage', fontsize=11)
ax3.set_title('Distribution of TP Reduction Effectiveness', fontsize=12, fontweight='bold')
ax3.grid(axis='y', alpha=0.3)
for i, v in enumerate(reduction_dist.values):
    ax3.text(i, v + 0.5, str(v), ha='center', va='bottom', fontsize=10, fontweight='bold')

# Subplot 4: Reach-by-reach comparison (top 15)
ax4 = axes[1, 1]
top_reduction = results.nlargest(15, 'TP_Reduction_tpy')[['NZSEGMENT', 'TP_Reduction_tpy']].copy()
ax4.barh(range(len(top_reduction)), top_reduction['TP_Reduction_tpy'], color='#9B59B6')
ax4.set_yticks(range(len(top_reduction)))
ax4.set_yticklabels([f"{int(r)}" for r in top_reduction['NZSEGMENT']], fontsize=8)
ax4.set_xlabel('TP Reduction (tonnes/year)', fontsize=11)
ax4.set_ylabel('NZSEGMENT', fontsize=11)
ax4.set_title('Top 15 Reaches by TP Reduction', fontsize=12, fontweight='bold')
ax4.grid(axis='x', alpha=0.3)
ax4.invert_yaxis()

plt.tight_layout()
plt.savefig(f"{output_base}/Figures/Lake_Omapere_CW_Analysis_Summary.png", dpi=300, bbox_inches='tight')
print(f"  Saved: {output_base}/Figures/Lake_Omapere_CW_Analysis_Summary.png")

# Figure 2: Detailed scatter plot
fig2, ax = plt.subplots(figsize=(12, 8))
scatter = ax.scatter(results['TP_Baseline_tpy'], results['Reduction_Percent'],
                    c=results['Combined_Percent'], cmap='viridis',
                    s=100, alpha=0.6, edgecolors='black', linewidth=0.5)
ax.set_xlabel('Baseline TP Load (tonnes/year)', fontsize=12, fontweight='bold')
ax.set_ylabel('Reduction Percentage (%)', fontsize=12, fontweight='bold')
ax.set_title('TP Reduction vs. Baseline Load (colored by CW Coverage %)',
             fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.axhline(y=50, color='red', linestyle='--', alpha=0.5, label='50% Reduction Target')
ax.axhline(y=25, color='orange', linestyle='--', alpha=0.5, label='25% Reduction')
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('CW Coverage (%)', fontsize=11, fontweight='bold')
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig(f"{output_base}/Figures/Reduction_vs_Baseline_Load.png", dpi=300, bbox_inches='tight')
print(f"  Saved: {output_base}/Figures/Reduction_vs_Baseline_Load.png")

print("\n[10/10] Saving results...")

# Save detailed results
results_export = results[[
    'NZSEGMENT', 'SubcatchmentID', 'Land_Area_ha', 'Combined_Area_ha', 'Combined_Percent',
    'TP_Baseline_tpy', 'TP_Wetland_WithCW_tpy', 'TP_Reduction_tpy', 'Reduction_Percent',
    'CW_Removal_Pct', 'CW_Category', 'HighClay_Over50Pct'
]].copy()

results_export = results_export.sort_values('TP_Reduction_tpy', ascending=False)
results_export.to_csv(f"{output_base}/Data/Lake_Omapere_Complete_Results.csv", index=False)
print(f"  Saved: {output_base}/Data/Lake_Omapere_Complete_Results.csv")

# Save summary statistics
with open(f"{output_base}/Summary/Analysis_Summary.txt", 'w') as f:
    f.write("="*80 + "\n")
    f.write("LAKE OMAPERE CW MITIGATION ANALYSIS - SUMMARY REPORT\n")
    f.write("="*80 + "\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Project: TKIL2602 - Lake Omapere Modelling\n\n")

    f.write("ANALYSIS SCOPE:\n")
    f.write(f"  Total subcatchments analyzed: {len(results)}\n")
    f.write(f"  Lake Omapere reaches: {lake_omapere_reaches.min()} to {lake_omapere_reaches.max()}\n")
    f.write(f"  Reaches with CW coverage: {(results['Combined_Percent'] > 0).sum()}\n")
    f.write(f"  Reaches with high clay (>50%): {len(lake_omapere_high_clay)}\n\n")

    f.write("TP LOAD SUMMARY:\n")
    f.write(f"  Baseline Total TP Load: {total_baseline:.2f} tonnes/year\n")
    f.write(f"  Wetland+CW Total TP Load: {total_wetland:.2f} tonnes/year\n")
    f.write(f"  Total TP Reduction: {total_reduction:.2f} tonnes/year\n")
    f.write(f"  Overall Reduction: {overall_reduction_pct:.1f}%\n\n")

    f.write("EFFECTIVENESS DISTRIBUTION:\n")
    for cat, count in results['CW_Category'].value_counts().items():
        cat_reduction = results[results['CW_Category'] == cat]['TP_Reduction_tpy'].sum()
        f.write(f"  {cat}: {count} reaches, {cat_reduction:.2f} tpy reduction\n")

    f.write("\nREACHES BY REDUCTION LEVEL:\n")
    f.write(f"  >50% reduction: {(results['Reduction_Percent'] > 50).sum()} reaches\n")
    f.write(f"  25-50% reduction: {((results['Reduction_Percent'] >= 25) & (results['Reduction_Percent'] <= 50)).sum()} reaches\n")
    f.write(f"  10-25% reduction: {((results['Reduction_Percent'] >= 10) & (results['Reduction_Percent'] < 25)).sum()} reaches\n")
    f.write(f"  <10% reduction: {(results['Reduction_Percent'] < 10).sum()} reaches\n")
    f.write(f"  Zero reduction (constrained): {(results['Reduction_Percent'] == 0).sum()} reaches\n\n")

    f.write("TOP 10 REACHES BY TP REDUCTION:\n")
    for idx, row in results.nlargest(10, 'TP_Reduction_tpy').iterrows():
        f.write(f"  NZSEGMENT {int(row['NZSEGMENT'])}: {row['TP_Reduction_tpy']:.2f} tpy ")
        f.write(f"({row['Reduction_Percent']:.1f}% reduction, {row['CW_Category']})\n")

    f.write("\n" + "="*80 + "\n")
    f.write("KEY FINDINGS:\n")
    f.write(f"1. CW mitigation achieves {overall_reduction_pct:.1f}% overall TP reduction\n")
    f.write(f"2. {len(lake_omapere_high_clay)} reaches constrained by high clay soils (zero removal)\n")
    f.write(f"3. Average reduction per reach: {results['TP_Reduction_tpy'].mean():.2f} tonnes/year\n")
    f.write(f"4. Most effective areas: {(results['Reduction_Percent'] > 40).sum()} reaches with >40% reduction\n")
    f.write("="*80 + "\n")

print(f"  Saved: {output_base}/Summary/Analysis_Summary.txt")

# Create quick reference guide
with open(f"{output_base}/READ_ME_FIRST.txt", 'w') as f:
    f.write("LAKE OMAPERE CW MITIGATION ANALYSIS - QUICK REFERENCE\n")
    f.write("="*60 + "\n\n")
    f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d')}\n")
    f.write(f"Total Subcatchments: {len(results)}\n")
    f.write(f"Overall TP Reduction: {overall_reduction_pct:.1f}%\n")
    f.write(f"Total Reduction: {total_reduction:.2f} tonnes/year\n\n")
    f.write("KEY FILES:\n")
    f.write("  Data/Lake_Omapere_Complete_Results.csv - Full results\n")
    f.write("  Figures/Lake_Omapere_CW_Analysis_Summary.png - Main viz\n")
    f.write("  Summary/Analysis_Summary.txt - Detailed report\n\n")
    f.write("INTERPRETATION:\n")
    f.write("- Baseline: Current lake, no CW mitigation\n")
    f.write("- Wetland+CW: +0.66m lake with CW implementation\n")
    f.write("- Constraints applied: High clay soils (>50%) = zero removal\n")
    f.write("- LRF applied: <2%=20%, 2-4%=35%, >4%=50% removal\n")

print(f"  Saved: {output_base}/READ_ME_FIRST.txt")

print("\n" + "="*80)
print("ANALYSIS COMPLETE!")
print("="*80)
print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\nResults saved to: {output_base}/")
print("\nQuick Summary:")
print(f"  Total Baseline TP: {total_baseline:.2f} tonnes/year")
print(f"  Total Wetland+CW TP: {total_wetland:.2f} tonnes/year")
print(f"  Total Reduction: {total_reduction:.2f} tonnes/year ({overall_reduction_pct:.1f}%)")
print(f"\nCheck {output_base}/READ_ME_FIRST.txt for details")
print("="*80)
