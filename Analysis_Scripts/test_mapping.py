#!/usr/bin/env python3
"""
Test script for spatial mapping functionality

This script tests the MapGenerator class using existing results data.
"""

import sys
import pandas as pd
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import MapGenerator from main script
try:
    from lake_omapere_cw_analysis import MapGenerator, Config
    print("[OK] Successfully imported MapGenerator")
except Exception as e:
    print(f"[ERROR] Error importing: {e}")
    sys.exit(1)

def main():
    print("\n" + "="*70)
    print("TESTING SPATIAL MAPPING FUNCTIONALITY")
    print("="*70)

    # Load existing results
    results_file = "../Results/LAKE_OMAPERE_RESULTS/Data/Lake_Omapere_Routing_Results.csv"

    print(f"\n[1] Loading results from: {results_file}")
    try:
        results = pd.read_csv(results_file)
        print(f"    Loaded {len(results)} reaches")
        print(f"    Columns: {list(results.columns[:5])}...")
    except Exception as e:
        print(f"    [ERROR] Error loading results: {e}")
        return False

    # Rename columns to match expected names
    print("\n[2] Renaming columns to match MapGenerator expectations...")
    column_mapping = {
        'NZSEGMENT': 'reach_id',
        'TPGen_baseline': 'generated_baseline',
        'TPGen_wetland_noCW': 'generated_wetland',
        'TPGen_wetland_withCW': 'generated_cw',
        'TPRouted_baseline': 'routed_baseline',
        'TPRouted_wetland_noCW': 'routed_wetland',
        'TPRouted_wetland_withCW': 'routed_cw',
        'RoutedReduction_CWEffect': 'routed_reduction',
        'GenReduction_CWEffect': 'cw_reduction',
        'Combined_Percent': 'CW_Coverage_Percent',
        'CW_Category': 'coverage_category',
        'HighClay_Over50Pct': 'HighClay'
    }

    results_renamed = results.rename(columns=column_mapping)
    print(f"    [OK] Renamed columns")
    print(f"    New columns: {list(results_renamed.columns[:5])}...")

    # Calculate percentage reduction if not present
    if 'routed_reduction_percent' not in results_renamed.columns:
        results_renamed['routed_reduction_percent'] = (
            (results_renamed['routed_reduction'] /
             results_renamed['routed_baseline']) * 100
        ).fillna(0)
        print(f"    [OK] Calculated routed_reduction_percent")

    # Check for required columns
    required_cols = ['reach_id', 'generated_baseline', 'routed_baseline',
                    'generated_cw', 'routed_cw']
    missing_cols = [col for col in required_cols if col not in results_renamed.columns]

    if missing_cols:
        print(f"    [ERROR] Missing required columns: {missing_cols}")
        return False
    else:
        print(f"    [OK] All required columns present")

    # Display sample data
    print("\n[3] Sample data:")
    print(results_renamed[['reach_id', 'generated_baseline', 'routed_baseline',
                           'CW_Coverage_Percent']].head(3).to_string())

    # Test MapGenerator
    print("\n[4] Testing MapGenerator...")

    # Update Config paths (in case they're different)
    Config.RIVER_SHAPEFILE = "../Shapefiles/Reference/Riverlines.shp"
    Config.CATCHMENT_SHAPEFILE = "../Shapefiles/Reference/Catchment.shp"
    Config.LAKE_SHAPEFILE = "../Shapefiles/Lake/Lake Omapere-236.34 mAMSL (+0.66m).shp"
    Config.MAPS_DIR = "../Results/LAKE_OMAPERE_RESULTS/Maps"

    try:
        # Generate all maps
        created_maps = MapGenerator.generate_all_maps(results_renamed)

        print(f"\n[5] Results:")
        if created_maps:
            print(f"    [OK] Successfully created {len(created_maps)} maps:")
            for map_path in created_maps:
                print(f"      - {map_path}")
        else:
            print(f"    [WARNING] No maps created (check warnings above)")
            print(f"    Possible reasons:")
            print(f"      - geopandas not installed")
            print(f"      - Shapefiles not found")
            print(f"      - Missing data columns")

        return len(created_maps) > 0

    except Exception as e:
        print(f"    [ERROR] Error generating maps: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\nTest Mapping Functionality")
    print("-" * 70)

    success = main()

    print("\n" + "="*70)
    if success:
        print("[OK] MAPPING TEST SUCCESSFUL")
        print("\nMaps saved to: Results/LAKE_OMAPERE_RESULTS/Maps/")
    else:
        print("[ERROR] MAPPING TEST FAILED")
        print("\nCheck error messages above for details")
    print("="*70 + "\n")

    sys.exit(0 if success else 1)
