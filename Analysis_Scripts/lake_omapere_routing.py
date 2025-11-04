#!/usr/bin/env python3
"""
Lake Omapere CW Mitigation - Routing Analysis
==============================================
Routes TP loads downstream through reach network using Pokaiwhenua methodology.
Calculates cumulative loads at each reach with attenuation.

Based on Annette's instructions from Documentation/annette.txt
Project: TKIL2602 - Lake Omapere Modelling
Date: October 30, 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("LAKE OMAPERE CW MITIGATION - ROUTING ANALYSIS")
print("="*80)
print("\nFollowing Pokaiwhenua methodology (Annette's instructions)")
print("Routing loads downstream with attenuation factors\n")

# ============================================================================
# STEP 1: Load Input Data
# ============================================================================
print("[1/7] Loading input data...")

# Load Lake Omapere reach list (50 subcatchments)
lake_reaches = pd.read_csv('CW_Analysis_Results/CW_Coverage_CORRECTED.csv')
lake_nzsegments = set(lake_reaches['nzsegment'].values)
print(f"  - Lake Omapere reaches: {len(lake_nzsegments)}")

# Load reach network connectivity
hydroedge = pd.read_csv('Model/InputData/Hydroedge2_5.csv')
print(f"  - Total reaches in network: {len(hydroedge)}")

# Load attenuation factors (PstreamCarry for TP routing)
atten_baseline = pd.read_csv('Model/InputData/AttenCarry_baseline.csv')
atten_wetland = pd.read_csv('Model/InputData/AttenCarry_wetland_066m.csv')
print(f"  - Attenuation factors loaded")

# Load CLUES loads (generated loads - local subcatchment only)
clues_baseline = pd.read_csv('Model/InputData/CLUESloads_baseline.csv')
clues_wetland = pd.read_csv('Model/InputData/CLUESloads_wetland_066m.csv')
print(f"  - CLUES loads loaded (baseline & wetland)")

# Load CW mitigation results
cw_results = pd.read_csv('Results/LAKE_OMAPERE_FINAL/Data/Lake_Omapere_Complete_Results.csv')
print(f"  - CW mitigation results loaded")

# ============================================================================
# STEP 2: Prepare Reach Network
# ============================================================================
print("\n[2/7] Building reach network...")

# Create network dictionary: reach -> list of upstream reaches
network = {}
downstream = {}  # reach -> downstream reach

for _, row in hydroedge.iterrows():
    seg = row['NZSEGMENT']
    from_node = row['FROM_NODE']
    to_node = row['TO_NODE']

    # Store downstream connection
    downstream[seg] = to_node

    # Find all reaches that flow into this reach
    upstream_reaches = hydroedge[hydroedge['TO_NODE'] == from_node]['NZSEGMENT'].tolist()
    network[seg] = upstream_reaches

print(f"  - Network built: {len(network)} reaches")
print(f"  - Downstream connections: {len(downstream)}")

# ============================================================================
# STEP 3: Prepare Generated Loads with CW Mitigation
# ============================================================================
print("\n[3/7] Preparing generated loads with CW mitigation...")

# Merge all data
loads_df = hydroedge[['NZSEGMENT', 'HYDSEQ', 'FROM_NODE', 'TO_NODE']].copy()

# Add baseline loads
loads_df = loads_df.merge(
    clues_baseline[['NZSEGMENT', 'TPGen']].rename(columns={'TPGen': 'TPGen_baseline'}),
    on='NZSEGMENT', how='left'
)

# Add wetland loads (before CW mitigation)
loads_df = loads_df.merge(
    clues_wetland[['NZSEGMENT', 'TPGen']].rename(columns={'TPGen': 'TPGen_wetland_noCW'}),
    on='NZSEGMENT', how='left'
)

# Add CW mitigation effects for Lake Omapere reaches
# For Lake Omapere reaches: apply CW removal to wetland loads
# For other reaches: wetland loads unchanged (no CW mitigation)
cw_lookup = cw_results.set_index('NZSEGMENT')['CW_Removal_Pct'].to_dict()

loads_df['CW_Removal_Pct'] = loads_df['NZSEGMENT'].map(cw_lookup).fillna(0)
loads_df['TPGen_wetland_withCW'] = loads_df.apply(
    lambda row: row['TPGen_wetland_noCW'] * (1 - row['CW_Removal_Pct']/100)
    if row['NZSEGMENT'] in lake_nzsegments else row['TPGen_wetland_noCW'],
    axis=1
)

# Add attenuation factors
loads_df = loads_df.merge(
    atten_baseline[['NZSEGMENT', 'PstreamCarry']].rename(columns={'PstreamCarry': 'Patten_baseline'}),
    on='NZSEGMENT', how='left'
)
loads_df = loads_df.merge(
    atten_wetland[['NZSEGMENT', 'PstreamCarry']].rename(columns={'PstreamCarry': 'Patten_wetland'}),
    on='NZSEGMENT', how='left'
)

# Fill missing values
loads_df.fillna(0, inplace=True)

print(f"  - Generated loads prepared for {len(loads_df)} reaches")
print(f"  - CW mitigation applied to {len(cw_lookup)} Lake Omapere reaches")

# ============================================================================
# STEP 4: Route Loads Downstream - BASELINE SCENARIO
# ============================================================================
print("\n[4/7] Routing baseline loads...")

# Sort by HYDSEQ to process in upstream->downstream order
loads_df = loads_df.sort_values('HYDSEQ').reset_index(drop=True)

# Initialize routed load columns
loads_df['TPRouted_baseline'] = 0.0

# Create dictionaries for fast lookup
routed_dict = {}  # seg -> routed load
patten_dict = loads_df.set_index('NZSEGMENT')['Patten_baseline'].to_dict()
tpgen_dict = loads_df.set_index('NZSEGMENT')['TPGen_baseline'].to_dict()

# Route loads downstream
for idx, row in loads_df.iterrows():
    seg = row['NZSEGMENT']

    # Start with local generated load
    local_load = tpgen_dict.get(seg, 0)

    # Add upstream contributions (attenuated)
    upstream_load = 0.0
    if seg in network:
        for upstream_seg in network[seg]:
            if upstream_seg in routed_dict:
                # Apply attenuation to upstream routed load
                upstream_load += routed_dict[upstream_seg] * patten_dict.get(upstream_seg, 1.0)

    # Total routed load = local + attenuated upstream
    total_routed = local_load + upstream_load
    routed_dict[seg] = total_routed
    loads_df.at[idx, 'TPRouted_baseline'] = total_routed

    # Progress indicator
    if idx % 100000 == 0:
        print(f"    Processed {idx}/{len(loads_df)} reaches...")

print(f"  - Baseline routing complete")
print(f"  - Total generated TP (baseline): {loads_df['TPGen_baseline'].sum():.4f} tpy")
print(f"  - Total routed TP (baseline) at outlets: {loads_df.nlargest(5, 'HYDSEQ')['TPRouted_baseline'].mean():.4f} tpy")

# ============================================================================
# STEP 5: Route Loads Downstream - WETLAND SCENARIOS
# ============================================================================
print("\n[5/7] Routing wetland loads (with and without CW)...")

# Initialize columns
loads_df['TPRouted_wetland_noCW'] = 0.0
loads_df['TPRouted_wetland_withCW'] = 0.0

# Create dictionaries for wetland routing
tpgen_wetland_noCW_dict = loads_df.set_index('NZSEGMENT')['TPGen_wetland_noCW'].to_dict()
tpgen_wetland_withCW_dict = loads_df.set_index('NZSEGMENT')['TPGen_wetland_withCW'].to_dict()
patten_wetland_dict = loads_df.set_index('NZSEGMENT')['Patten_wetland'].to_dict()

# Route wetland loads WITHOUT CW mitigation
routed_wetland_noCW_dict = {}
for idx, row in loads_df.iterrows():
    seg = row['NZSEGMENT']
    local_load = tpgen_wetland_noCW_dict.get(seg, 0)
    upstream_load = 0.0

    if seg in network:
        for upstream_seg in network[seg]:
            if upstream_seg in routed_wetland_noCW_dict:
                upstream_load += routed_wetland_noCW_dict[upstream_seg] * patten_wetland_dict.get(upstream_seg, 1.0)

    total_routed = local_load + upstream_load
    routed_wetland_noCW_dict[seg] = total_routed
    loads_df.at[idx, 'TPRouted_wetland_noCW'] = total_routed

    if idx % 100000 == 0:
        print(f"    Wetland (no CW): {idx}/{len(loads_df)} reaches...")

# Route wetland loads WITH CW mitigation
routed_wetland_withCW_dict = {}
for idx, row in loads_df.iterrows():
    seg = row['NZSEGMENT']
    local_load = tpgen_wetland_withCW_dict.get(seg, 0)
    upstream_load = 0.0

    if seg in network:
        for upstream_seg in network[seg]:
            if upstream_seg in routed_wetland_withCW_dict:
                upstream_load += routed_wetland_withCW_dict[upstream_seg] * patten_wetland_dict.get(upstream_seg, 1.0)

    total_routed = local_load + upstream_load
    routed_wetland_withCW_dict[seg] = total_routed
    loads_df.at[idx, 'TPRouted_wetland_withCW'] = total_routed

    if idx % 100000 == 0:
        print(f"    Wetland (with CW): {idx}/{len(loads_df)} reaches...")

print(f"  - Wetland routing complete (both scenarios)")
print(f"  - Total generated TP (wetland, no CW): {loads_df['TPGen_wetland_noCW'].sum():.4f} tpy")
print(f"  - Total generated TP (wetland, with CW): {loads_df['TPGen_wetland_withCW'].sum():.4f} tpy")

# ============================================================================
# STEP 6: Calculate Reductions for Lake Omapere Reaches
# ============================================================================
print("\n[6/7] Calculating reductions for Lake Omapere reaches...")

# Filter to Lake Omapere reaches
lake_df = loads_df[loads_df['NZSEGMENT'].isin(lake_nzsegments)].copy()

# Calculate reductions
# Generated loads
lake_df['GenReduction_WetlandOnly'] = lake_df['TPGen_baseline'] - lake_df['TPGen_wetland_noCW']
lake_df['GenReduction_WetlandPlusCW'] = lake_df['TPGen_baseline'] - lake_df['TPGen_wetland_withCW']
lake_df['GenReduction_CWEffect'] = lake_df['TPGen_wetland_noCW'] - lake_df['TPGen_wetland_withCW']

# Routed loads
lake_df['RoutedReduction_WetlandOnly'] = lake_df['TPRouted_baseline'] - lake_df['TPRouted_wetland_noCW']
lake_df['RoutedReduction_WetlandPlusCW'] = lake_df['TPRouted_baseline'] - lake_df['TPRouted_wetland_withCW']
lake_df['RoutedReduction_CWEffect'] = lake_df['TPRouted_wetland_noCW'] - lake_df['TPRouted_wetland_withCW']

# Percentage reductions
lake_df['RoutedReduction_Pct'] = (lake_df['RoutedReduction_WetlandPlusCW'] / lake_df['TPRouted_baseline'] * 100).replace([np.inf, -np.inf], 0)

# Add CW category info
lake_df = lake_df.merge(
    cw_results[['NZSEGMENT', 'CW_Category', 'HighClay_Over50Pct', 'Combined_Percent']],
    on='NZSEGMENT', how='left'
)

print(f"  - Lake Omapere reaches analyzed: {len(lake_df)}")
print(f"\n  GENERATED LOADS SUMMARY:")
print(f"    Baseline total: {lake_df['TPGen_baseline'].sum():.4f} tpy")
print(f"    Wetland (no CW) total: {lake_df['TPGen_wetland_noCW'].sum():.4f} tpy")
print(f"    Wetland (with CW) total: {lake_df['TPGen_wetland_withCW'].sum():.4f} tpy")
print(f"    Reduction from wetland scenario: {lake_df['GenReduction_WetlandOnly'].sum():.4f} tpy ({lake_df['GenReduction_WetlandOnly'].sum()/lake_df['TPGen_baseline'].sum()*100:.2f}%)")
print(f"    Reduction from CW mitigation: {lake_df['GenReduction_CWEffect'].sum():.4f} tpy")
print(f"    Total reduction (wetland+CW): {lake_df['GenReduction_WetlandPlusCW'].sum():.4f} tpy ({lake_df['GenReduction_WetlandPlusCW'].sum()/lake_df['TPGen_baseline'].sum()*100:.2f}%)")

print(f"\n  ROUTED LOADS SUMMARY:")
print(f"    Baseline total: {lake_df['TPRouted_baseline'].sum():.4f} tpy")
print(f"    Wetland (no CW) total: {lake_df['TPRouted_wetland_noCW'].sum():.4f} tpy")
print(f"    Wetland (with CW) total: {lake_df['TPRouted_wetland_withCW'].sum():.4f} tpy")
print(f"    Reduction from wetland scenario: {lake_df['RoutedReduction_WetlandOnly'].sum():.4f} tpy ({lake_df['RoutedReduction_WetlandOnly'].sum()/lake_df['TPRouted_baseline'].sum()*100:.2f}%)")
print(f"    Reduction from CW mitigation: {lake_df['RoutedReduction_CWEffect'].sum():.4f} tpy")
print(f"    Total reduction (wetland+CW): {lake_df['RoutedReduction_WetlandPlusCW'].sum():.4f} tpy ({lake_df['RoutedReduction_WetlandPlusCW'].sum()/lake_df['TPRouted_baseline'].sum()*100:.2f}%)")

# ============================================================================
# STEP 7: Save Results
# ============================================================================
print("\n[7/7] Saving results...")

# Create output directory
output_dir = Path('Results/LAKE_OMAPERE_ROUTING')
output_dir.mkdir(parents=True, exist_ok=True)

# Save complete routing results for Lake Omapere
output_cols = [
    'NZSEGMENT', 'HYDSEQ',
    'TPGen_baseline', 'TPGen_wetland_noCW', 'TPGen_wetland_withCW',
    'TPRouted_baseline', 'TPRouted_wetland_noCW', 'TPRouted_wetland_withCW',
    'GenReduction_WetlandOnly', 'GenReduction_CWEffect', 'GenReduction_WetlandPlusCW',
    'RoutedReduction_WetlandOnly', 'RoutedReduction_CWEffect', 'RoutedReduction_WetlandPlusCW',
    'RoutedReduction_Pct', 'CW_Removal_Pct', 'CW_Category', 'HighClay_Over50Pct', 'Combined_Percent'
]

lake_df[output_cols].to_csv(output_dir / 'Lake_Omapere_Routing_Results.csv', index=False)
print(f"  - Saved: {output_dir / 'Lake_Omapere_Routing_Results.csv'}")

# Save all reaches routing data (for reference)
loads_df.to_csv(output_dir / 'All_Reaches_Routing_Complete.csv', index=False)
print(f"  - Saved: {output_dir / 'All_Reaches_Routing_Complete.csv'}")

# ============================================================================
# STEP 8: Generate Visualizations
# ============================================================================
print("\n[8/9] Creating visualizations...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Lake Ōmāpere CW Mitigation - Routed Loads Analysis', fontsize=16, fontweight='bold', y=0.995)

# Plot 1: Generated vs Routed Loads Comparison
ax1 = axes[0, 0]
x = np.arange(3)
width = 0.35
generated = [lake_df['TPGen_baseline'].sum(), lake_df['TPGen_wetland_noCW'].sum(), lake_df['TPGen_wetland_withCW'].sum()]
routed = [lake_df['TPRouted_baseline'].sum(), lake_df['TPRouted_wetland_noCW'].sum(), lake_df['TPRouted_wetland_withCW'].sum()]

bars1 = ax1.bar(x - width/2, generated, width, label='Generated Loads', color='steelblue', alpha=0.8)
bars2 = ax1.bar(x + width/2, routed, width, label='Routed Loads', color='coral', alpha=0.8)

ax1.set_xlabel('Scenario', fontweight='bold')
ax1.set_ylabel('Total TP Load (tonnes/year)', fontweight='bold')
ax1.set_title('Generated vs Routed Loads', fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(['Baseline', 'Wetland\n(no CW)', 'Wetland\n(with CW)'])
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom', fontsize=9)

# Plot 2: Routing Effect by CW Category
ax2 = axes[0, 1]
cat_summary = lake_df.groupby('CW_Category').agg({
    'RoutedReduction_CWEffect': 'sum',
    'NZSEGMENT': 'count'
}).reset_index()
cat_summary.columns = ['CW_Category', 'CW_Reduction', 'Count']
cat_summary = cat_summary.sort_values('CW_Reduction', ascending=True)

colors_map = {
    'HighCW_>4pct': 'darkgreen',
    'MediumCW_2-4pct': 'orange',
    'LowCW_<2pct': 'gold',
    'NoCW': 'lightgray',
    'HighClay_ZeroRemoval': 'brown'
}
colors = [colors_map.get(cat, 'gray') for cat in cat_summary['CW_Category']]

bars = ax2.barh(range(len(cat_summary)), cat_summary['CW_Reduction'], color=colors, alpha=0.8)
ax2.set_yticks(range(len(cat_summary)))
ax2.set_yticklabels([f"{cat} (n={count})" for cat, count in zip(cat_summary['CW_Category'], cat_summary['Count'])])
ax2.set_xlabel('TP Reduction from CW (tonnes/year)', fontweight='bold')
ax2.set_title('CW Mitigation Effect by Category (Routed)', fontweight='bold')
ax2.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, val) in enumerate(zip(bars, cat_summary['CW_Reduction'])):
    ax2.text(val, i, f' {val:.4f}', va='center', fontsize=9)

# Plot 3: Scatter - Generated vs Routed Reduction %
ax3 = axes[1, 0]
lake_df_clean = lake_df[(lake_df['TPGen_baseline'] > 0) & (lake_df['TPRouted_baseline'] > 0)].copy()
lake_df_clean['GenReduction_Pct'] = (lake_df_clean['GenReduction_WetlandPlusCW'] / lake_df_clean['TPGen_baseline'] * 100)

scatter = ax3.scatter(lake_df_clean['GenReduction_Pct'], lake_df_clean['RoutedReduction_Pct'],
                      c=lake_df_clean['Combined_Percent'], cmap='viridis', s=100, alpha=0.7, edgecolors='black', linewidth=0.5)
ax3.plot([-100, 100], [-100, 100], 'r--', alpha=0.5, label='1:1 line')
ax3.set_xlabel('Generated Load Reduction (%)', fontweight='bold')
ax3.set_ylabel('Routed Load Reduction (%)', fontweight='bold')
ax3.set_title('Generated vs Routed Reduction Comparison', fontweight='bold')
ax3.grid(alpha=0.3)
ax3.legend()

cbar = plt.colorbar(scatter, ax=ax3)
cbar.set_label('CW Coverage (%)', fontweight='bold')

# Plot 4: Top Reaches by Routed Reduction
ax4 = axes[1, 1]
top_reaches = lake_df.nlargest(10, 'RoutedReduction_WetlandPlusCW')
colors4 = [colors_map.get(cat, 'gray') for cat in top_reaches['CW_Category']]

bars = ax4.barh(range(len(top_reaches)), top_reaches['RoutedReduction_WetlandPlusCW'], color=colors4, alpha=0.8)
ax4.set_yticks(range(len(top_reaches)))
ax4.set_yticklabels([f"{seg} ({cat})" for seg, cat in zip(top_reaches['NZSEGMENT'], top_reaches['CW_Category'])], fontsize=9)
ax4.set_xlabel('TP Reduction (tonnes/year)', fontweight='bold')
ax4.set_title('Top 10 Reaches by Total Reduction (Routed)', fontweight='bold')
ax4.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, val) in enumerate(zip(bars, top_reaches['RoutedReduction_WetlandPlusCW'])):
    ax4.text(val, i, f' {val:.4f}', va='center', fontsize=8)

plt.tight_layout()
plt.savefig(output_dir / 'Lake_Omapere_Routing_Analysis.png', dpi=300, bbox_inches='tight')
print(f"  - Saved: {output_dir / 'Lake_Omapere_Routing_Analysis.png'}")

plt.close()

# ============================================================================
# STEP 9: Generate Summary Report
# ============================================================================
print("\n[9/9] Generating summary report...")

summary_file = output_dir / 'Routing_Analysis_Summary.txt'
with open(summary_file, 'w') as f:
    f.write("="*80 + "\n")
    f.write("LAKE OMAPERE CW MITIGATION - ROUTING ANALYSIS SUMMARY\n")
    f.write("="*80 + "\n")
    f.write(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Project: TKIL2602 - Lake Omapere Modelling\n")
    f.write(f"Methodology: Pokaiwhenua routing approach (Annette's instructions)\n\n")

    f.write("ANALYSIS SCOPE:\n")
    f.write(f"  Total reaches analyzed: {len(lake_df)}\n")
    f.write(f"  Lake Omapere reaches: {min(lake_df['NZSEGMENT'])} to {max(lake_df['NZSEGMENT'])}\n")
    f.write(f"  Reaches with CW coverage: {(lake_df['Combined_Percent'] > 0).sum()}\n")
    f.write(f"  Reaches with high clay (>50%): {lake_df['HighClay_Over50Pct'].sum()}\n\n")

    f.write("="*80 + "\n")
    f.write("GENERATED LOADS (Local Subcatchment Contributions Only)\n")
    f.write("="*80 + "\n")
    f.write(f"  Baseline Total TP Load: {lake_df['TPGen_baseline'].sum():.4f} tonnes/year\n")
    f.write(f"  Wetland (no CW) Total TP Load: {lake_df['TPGen_wetland_noCW'].sum():.4f} tonnes/year\n")
    f.write(f"  Wetland (with CW) Total TP Load: {lake_df['TPGen_wetland_withCW'].sum():.4f} tonnes/year\n\n")

    f.write(f"  Reduction from wetland scenario alone: {lake_df['GenReduction_WetlandOnly'].sum():.4f} tpy ({lake_df['GenReduction_WetlandOnly'].sum()/lake_df['TPGen_baseline'].sum()*100:.2f}%)\n")
    f.write(f"  Reduction from CW mitigation: {lake_df['GenReduction_CWEffect'].sum():.4f} tpy\n")
    f.write(f"  Total reduction (wetland + CW): {lake_df['GenReduction_WetlandPlusCW'].sum():.4f} tpy ({lake_df['GenReduction_WetlandPlusCW'].sum()/lake_df['TPGen_baseline'].sum()*100:.2f}%)\n\n")

    f.write("="*80 + "\n")
    f.write("ROUTED LOADS (Cumulative Downstream with Attenuation)\n")
    f.write("="*80 + "\n")
    f.write(f"  Baseline Total TP Load: {lake_df['TPRouted_baseline'].sum():.4f} tonnes/year\n")
    f.write(f"  Wetland (no CW) Total TP Load: {lake_df['TPRouted_wetland_noCW'].sum():.4f} tonnes/year\n")
    f.write(f"  Wetland (with CW) Total TP Load: {lake_df['TPRouted_wetland_withCW'].sum():.4f} tonnes/year\n\n")

    f.write(f"  Reduction from wetland scenario alone: {lake_df['RoutedReduction_WetlandOnly'].sum():.4f} tpy ({lake_df['RoutedReduction_WetlandOnly'].sum()/lake_df['TPRouted_baseline'].sum()*100:.2f}%)\n")
    f.write(f"  Reduction from CW mitigation: {lake_df['RoutedReduction_CWEffect'].sum():.4f} tpy\n")
    f.write(f"  Total reduction (wetland + CW): {lake_df['RoutedReduction_WetlandPlusCW'].sum():.4f} tpy ({lake_df['RoutedReduction_WetlandPlusCW'].sum()/lake_df['TPRouted_baseline'].sum()*100:.2f}%)\n\n")

    f.write("="*80 + "\n")
    f.write("EFFECTIVENESS BY CW CATEGORY (Routed Loads)\n")
    f.write("="*80 + "\n")
    for _, row in cat_summary.iterrows():
        f.write(f"  {row['CW_Category']}: {row['Count']} reaches, {row['CW_Reduction']:.4f} tpy reduction\n")
    f.write("\n")

    f.write("="*80 + "\n")
    f.write("TOP 10 REACHES BY TOTAL REDUCTION (Routed)\n")
    f.write("="*80 + "\n")
    for i, row in enumerate(top_reaches.itertuples(), 1):
        f.write(f"  {i}. NZSEGMENT {row.NZSEGMENT}: {row.RoutedReduction_WetlandPlusCW:.4f} tpy ({row.RoutedReduction_Pct:.1f}%, {row.CW_Category})\n")
    f.write("\n")

    f.write("="*80 + "\n")
    f.write("KEY FINDINGS:\n")
    f.write("="*80 + "\n")
    f.write(f"1. Routing amplifies loads through cumulative downstream contributions\n")
    f.write(f"2. CW mitigation reduces {lake_df['RoutedReduction_CWEffect'].sum():.4f} tpy in routed loads\n")
    f.write(f"3. Overall reduction (wetland+CW): {lake_df['RoutedReduction_WetlandPlusCW'].sum()/lake_df['TPRouted_baseline'].sum()*100:.2f}%\n")
    f.write(f"4. {lake_df['HighClay_Over50Pct'].sum()} reaches constrained by high clay soils\n")
    f.write(f"5. Attenuation factors reduce downstream load propagation\n")
    f.write("="*80 + "\n")

print(f"  - Saved: {summary_file}")

print("\n" + "="*80)
print("ROUTING ANALYSIS COMPLETE")
print("="*80)
print(f"\nResults saved to: {output_dir}/")
print(f"  - Lake_Omapere_Routing_Results.csv")
print(f"  - Lake_Omapere_Routing_Analysis.png")
print(f"  - Routing_Analysis_Summary.txt")
print(f"\nKEY INSIGHT: Routed loads show cumulative downstream effects")
print(f"CW mitigation reduces {lake_df['RoutedReduction_CWEffect'].sum():.4f} tpy in routed loads")
print("="*80)
