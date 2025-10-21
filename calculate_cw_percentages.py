"""
Calculate % of sub-catchment area occupied by potential CW sites
Project: TKIL2602 - Lake Ōmāpere Modelling
Author: Reza Moghaddam
Date: October 2025
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set up paths
BASE_DIR = Path(__file__).parent
SHAPEFILE_DIR = BASE_DIR / "Shapefiles"
RESULTS_DIR = BASE_DIR / "Results"
RESULTS_DIR.mkdir(exist_ok=True)

# Input shapefiles
SUBS_SHP = SHAPEFILE_DIR / "Subcatchments" / "Subs.shp"
TYPE1_SHP = SHAPEFILE_DIR / "CW_Sites" / "MaxDepth to GW 1m_WL-20%tile(+0.66)_clipped_v2.shp"
TYPE2_SHP = SHAPEFILE_DIR / "CW_Sites" / "Lake Omapere Catchment- topographic depressions_clipped_v2.shp"

print("="*70)
print("CW Site Analysis - Lake Omapere")
print("="*70)

# Load shapefiles
print("\n1. Loading shapefiles...")
try:
    subs = gpd.read_file(SUBS_SHP)
    print(f"   [OK] Loaded {len(subs)} sub-catchments")
    print(f"   [OK] CRS: {subs.crs}")

    type1_cw = gpd.read_file(TYPE1_SHP)
    print(f"   [OK] Loaded Type 1 CW sites (Groundwater fed): {len(type1_cw)} features")

    type2_cw = gpd.read_file(TYPE2_SHP)
    print(f"   [OK] Loaded Type 2 CW sites (Surface water fed): {len(type2_cw)} features")

except Exception as e:
    print(f"   [ERROR] Error loading shapefiles: {e}")
    exit(1)

# Ensure all layers have the same CRS
print("\n2. Checking coordinate reference systems...")
if type1_cw.crs != subs.crs:
    print(f"   -> Reprojecting Type 1 CW from {type1_cw.crs} to {subs.crs}")
    type1_cw = type1_cw.to_crs(subs.crs)

if type2_cw.crs != subs.crs:
    print(f"   -> Reprojecting Type 2 CW from {type2_cw.crs} to {subs.crs}")
    type2_cw = type2_cw.to_crs(subs.crs)

print("   [OK] All layers aligned")

# Calculate areas
print("\n3. Calculating areas...")

# Prepare results dataframe
results = []

for idx, sub in subs.iterrows():
    # Get sub-catchment ID (adjust field name as needed)
    # Common field names: 'ID', 'FID', 'OBJECTID', 'Name', etc.
    sub_id = sub.get('ID', sub.get('FID', sub.get('OBJECTID', idx)))

    # Calculate sub-catchment area in hectares
    sub_area_m2 = sub.geometry.area
    sub_area_ha = sub_area_m2 / 10000  # Convert m² to hectares

    # Intersect with Type 1 CW sites
    type1_intersect = type1_cw[type1_cw.intersects(sub.geometry)]
    if len(type1_intersect) > 0:
        type1_clipped = gpd.clip(type1_intersect, sub.geometry)
        type1_area_m2 = type1_clipped.geometry.area.sum()
        type1_area_ha = type1_area_m2 / 10000
        type1_percent = (type1_area_ha / sub_area_ha) * 100 if sub_area_ha > 0 else 0
    else:
        type1_area_ha = 0
        type1_percent = 0

    # Intersect with Type 2 CW sites
    type2_intersect = type2_cw[type2_cw.intersects(sub.geometry)]
    if len(type2_intersect) > 0:
        type2_clipped = gpd.clip(type2_intersect, sub.geometry)
        type2_area_m2 = type2_clipped.geometry.area.sum()
        type2_area_ha = type2_area_m2 / 10000
        type2_percent = (type2_area_ha / sub_area_ha) * 100 if sub_area_ha > 0 else 0
    else:
        type2_area_ha = 0
        type2_percent = 0

    # Calculate combined area (union of Type 1 and Type 2)
    if len(type1_intersect) > 0 or len(type2_intersect) > 0:
        # Combine both types
        combined_cw = pd.concat([type1_intersect, type2_intersect])
        combined_clipped = gpd.clip(combined_cw, sub.geometry)

        # Dissolve to merge overlapping polygons
        combined_dissolved = combined_clipped.dissolve()
        combined_area_m2 = combined_dissolved.geometry.area.sum()
        combined_area_ha = combined_area_m2 / 10000
        combined_percent = (combined_area_ha / sub_area_ha) * 100 if sub_area_ha > 0 else 0
    else:
        combined_area_ha = 0
        combined_percent = 0

    # Store results
    results.append({
        'SubcatchmentID': sub_id,
        'Subcatchment_Area_ha': round(sub_area_ha, 2),
        'Type1_GW_Area_ha': round(type1_area_ha, 2),
        'Type1_GW_Percent': round(type1_percent, 2),
        'Type2_SW_Area_ha': round(type2_area_ha, 2),
        'Type2_SW_Percent': round(type2_percent, 2),
        'Combined_Area_ha': round(combined_area_ha, 2),
        'Combined_Percent': round(combined_percent, 2)
    })

    print(f"   [OK] Processed sub-catchment {sub_id}: {combined_percent:.2f}% CW coverage")

# Create results dataframe
results_df = pd.DataFrame(results)

# Calculate summary statistics
print("\n4. Summary Statistics:")
print(f"   Total sub-catchments: {len(results_df)}")
print(f"   Total catchment area: {results_df['Subcatchment_Area_ha'].sum():.2f} ha")
print(f"   Total Type 1 (GW) CW area: {results_df['Type1_GW_Area_ha'].sum():.2f} ha")
print(f"   Total Type 2 (SW) CW area: {results_df['Type2_SW_Area_ha'].sum():.2f} ha")
print(f"   Total Combined CW area: {results_df['Combined_Area_ha'].sum():.2f} ha")
print(f"   Average Type 1 coverage: {results_df['Type1_GW_Percent'].mean():.2f}%")
print(f"   Average Type 2 coverage: {results_df['Type2_SW_Percent'].mean():.2f}%")
print(f"   Average Combined coverage: {results_df['Combined_Percent'].mean():.2f}%")

# Save results
print("\n5. Saving results...")

# Save as CSV
csv_file = RESULTS_DIR / "CW_Coverage_by_Subcatchment.csv"
results_df.to_csv(csv_file, index=False)
print(f"   [OK] Saved: {csv_file}")

# Save as Excel with formatting
excel_file = RESULTS_DIR / "CW_Coverage_by_Subcatchment.xlsx"
with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    results_df.to_excel(writer, sheet_name='Subcatchment Analysis', index=False)

    # Add summary sheet
    summary_df = pd.DataFrame({
        'Metric': [
            'Total Sub-catchments',
            'Total Catchment Area (ha)',
            'Total Type 1 GW Area (ha)',
            'Total Type 2 SW Area (ha)',
            'Total Combined Area (ha)',
            'Avg Type 1 Coverage (%)',
            'Avg Type 2 Coverage (%)',
            'Avg Combined Coverage (%)'
        ],
        'Value': [
            len(results_df),
            round(results_df['Subcatchment_Area_ha'].sum(), 2),
            round(results_df['Type1_GW_Area_ha'].sum(), 2),
            round(results_df['Type2_SW_Area_ha'].sum(), 2),
            round(results_df['Combined_Area_ha'].sum(), 2),
            round(results_df['Type1_GW_Percent'].mean(), 2),
            round(results_df['Type2_SW_Percent'].mean(), 2),
            round(results_df['Combined_Percent'].mean(), 2)
        ]
    })
    summary_df.to_excel(writer, sheet_name='Summary', index=False)

print(f"   [OK] Saved: {excel_file}")

print("\n" + "="*70)
print("Analysis complete!")
print("="*70)
print(f"\nResults saved in: {RESULTS_DIR}")
print("\nNext steps:")
print("- Review the results files")
print("- Share with Fleur and Annette")
print("- Update project documentation")
