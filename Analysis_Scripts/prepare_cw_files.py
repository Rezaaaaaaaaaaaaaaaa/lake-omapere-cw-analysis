"""
Prepare CW placement files with correct NZSEGMENT mappings and coverage categories
"""

import pandas as pd
import geopandas as gpd
import os

print("="*70)
print("Preparing CW Placement Files for Lake Omapere Model")
print("="*70)

# Read the subcatchment shapefile to get NZSEGMENT mapping
print("\n1. Reading subcatchment shapefile...")
subc_path = "Shapefiles/Subcatchments/Subs.shp"
subc_gdf = gpd.read_file(subc_path)
print(f"   [OK] Loaded {len(subc_gdf)} subcatchments")

# Create mapping of index to NZSEGMENT
nzseg_mapping = {idx: row['NZSEGMENT'] for idx, row in subc_gdf.iterrows()}
print(f"   [OK] Created NZSEGMENT mapping for {len(nzseg_mapping)} subcatchments")

# Read the coverage results
print("\n2. Reading CW coverage results...")
coverage_df = pd.read_csv('Results/CW_Coverage_by_Subcatchment.csv')
print(f"   [OK] Loaded coverage data for {len(coverage_df)} subcatchments")

# Map NZSEGMENT to coverage percentages
print("\n3. Creating NZSEGMENT to coverage mapping...")
cw_data = []
for idx, row in coverage_df.iterrows():
    sub_id = row['SubcatchmentID']
    combined_pct = row['Combined_Percent']

    if sub_id in nzseg_mapping:
        nzsegment = nzseg_mapping[sub_id]
        cw_data.append({
            'NZSEGMENT': nzsegment,
            'CW_Coverage_Pct': combined_pct
        })

cw_df = pd.DataFrame(cw_data)
print(f"   [OK] Mapped {len(cw_df)} subcatchments to NZSEGMENT")

# Filter to only subcatchments with CW (>0%)
cw_df_with_coverage = cw_df[cw_df['CW_Coverage_Pct'] > 0].copy()
print(f"   [OK] Found {len(cw_df_with_coverage)} subcatchments with CW coverage >0%")

# Categorize by coverage level
print("\n4. Categorizing by LRF coverage levels...")
cw_low = cw_df_with_coverage[cw_df_with_coverage['CW_Coverage_Pct'] < 2].copy()
cw_med = cw_df_with_coverage[(cw_df_with_coverage['CW_Coverage_Pct'] >= 2) &
                              (cw_df_with_coverage['CW_Coverage_Pct'] < 4)].copy()
cw_high = cw_df_with_coverage[cw_df_with_coverage['CW_Coverage_Pct'] >= 4].copy()

print(f"   <2% coverage: {len(cw_low)} subcatchments")
print(f"   2-4% coverage: {len(cw_med)} subcatchments")
print(f"   >4% coverage: {len(cw_high)} subcatchments")

# Save the files
print("\n5. Saving CW placement files...")
output_dir = "Model/InputData"
os.makedirs(output_dir, exist_ok=True)

# Save complete file (all subcatchments with coverage)
cw_all_path = os.path.join(output_dir, "CW_Subcatchments_All.csv")
cw_df_with_coverage.to_csv(cw_all_path, index=False)
print(f"   [OK] Saved: {cw_all_path}")

# Save category-specific files (only NZSEGMENT column needed for placement)
cw_low_path = os.path.join(output_dir, "CW_Subcatchments_Low.csv")
cw_low[['NZSEGMENT']].to_csv(cw_low_path, index=False)
print(f"   [OK] Saved: {cw_low_path}")

cw_med_path = os.path.join(output_dir, "CW_Subcatchments_Med.csv")
cw_med[['NZSEGMENT']].to_csv(cw_med_path, index=False)
print(f"   [OK] Saved: {cw_med_path}")

cw_high_path = os.path.join(output_dir, "CW_Subcatchments_High.csv")
cw_high[['NZSEGMENT']].to_csv(cw_high_path, index=False)
print(f"   [OK] Saved: {cw_high_path}")

# Replace the original CW_Subcatchments.csv with the corrected complete version
cw_orig_path = os.path.join(output_dir, "CW_Subcatchments.csv")
cw_df_with_coverage.to_csv(cw_orig_path, index=False)
print(f"   [OK] Updated: {cw_orig_path}")

# Create a summary report
print("\n6. Creating summary report...")
summary = []
summary.append("="*70)
summary.append("CW PLACEMENT FILES SUMMARY")
summary.append("="*70)
summary.append(f"\nTotal subcatchments analyzed: {len(subc_gdf)}")
summary.append(f"Subcatchments with CW coverage: {len(cw_df_with_coverage)}")
summary.append(f"\nCoverage Categories:")
summary.append(f"  <2% coverage:  {len(cw_low):2d} subcatchments - Use Scenario 8 (CW_1)")
summary.append(f"  2-4% coverage: {len(cw_med):2d} subcatchments - Use Scenario 9 (CW_2)")
summary.append(f"  >4% coverage:  {len(cw_high):2d} subcatchments - Use Scenario 10 (CW_3)")
summary.append(f"\nFiles Created:")
summary.append(f"  1. CW_Subcatchments_All.csv  - All subcatchments with CW (for reference)")
summary.append(f"  2. CW_Subcatchments_Low.csv  - Subcatchments with <2% coverage")
summary.append(f"  3. CW_Subcatchments_Med.csv  - Subcatchments with 2-4% coverage")
summary.append(f"  4. CW_Subcatchments_High.csv - Subcatchments with >4% coverage")
summary.append(f"  5. CW_Subcatchments.csv      - Updated original file (all CW)")
summary.append(f"\nModel Run Strategy:")
summary.append(f"  Run the model 3 times, once for each coverage category:")
summary.append(f"    Run 1: Modify PlacementRules.py to use CW_Subcatchments_Low.csv, use Scenario 8")
summary.append(f"    Run 2: Modify PlacementRules.py to use CW_Subcatchments_Med.csv, use Scenario 9")
summary.append(f"    Run 3: Modify PlacementRules.py to use CW_Subcatchments_High.csv, use Scenario 10")
summary.append(f"  Then combine the generated loads from all three runs.")
summary.append("="*70)

summary_text = "\n".join(summary)
print(summary_text)

# Save summary to file
summary_path = "CW_Files_Summary.txt"
with open(summary_path, 'w') as f:
    f.write(summary_text)
print(f"\n[OK] Summary saved to: {summary_path}")

print("\n" + "="*70)
print("CW placement files prepared successfully!")
print("="*70)
