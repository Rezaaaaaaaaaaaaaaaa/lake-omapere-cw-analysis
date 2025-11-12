#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lake Omapere CW Mitigation Effectiveness Analysis - PHASE 2 WITH INUNDATION COMPARISON
======================================================================================

Implements Fleur's 6 requirements from November 11, 2025 email:
1. PartP surface-only routing (SR pathway only, no subsurface)
2. CLUES file verification (+0.66m lake level - CONFIRMED)
3. Agricultural <25% filter with NEW scaling logic
4. Dual CW scenarios (Surface+GW and Surface-only)
5. Terminal reaches column (pending Annette's data)
6. Column descriptions worksheet

NEW ADDITIONS:
- CLUES loads WITHOUT inundation for comparison
- Validation for illogical negative values
- Reaches sorted by HYDSEQ (upstream to downstream order)

Key Calculation Changes:
- NEW: If ag% < 25%, Available_Load = Total_CLUES_TP × (ag% / 100)
- NEW: PartP hillslope load goes 100% to SR pathway only
- DRP and DOP continue to use all HYPE pathways
- NEW: Inundation impact comparison columns

Usage:
    python lake_omapere_cw_analysis_PHASE2_with_comparison.py

Author: Analysis Team
Date: November 12, 2025
Project: TKIL2602 - Lake Omapere Modelling
"""

import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
import json

# Set UTF-8 encoding for Windows console
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration for Lake Omapere Phase 2 analysis"""

    # Input data files
    CLUES_WITH_INUNDATION_PATH = "Model/InputData/CLUESloads_baseline.csv"  # +0.66m
    CLUES_WITHOUT_INUNDATION_PATH = "Model/InputData/CLUESloads.csv"  # Baseline
    CW_COVERAGE_XLSX = "CW_Coverage_GIS_CALCULATED.xlsx"
    AG_PERCENT_CSV = "ag_percentage_by_reach.csv"  # Our calculated ag%
    CONTAMINANT_SPLITS_XLSX = "Model/Lookups/ContaminantSplits.xlsx"
    HYPE_CSV = "Model/InputData/Hype.csv"
    LRF_XLSX = "Model/Lookups/LRFs_years.xlsx"
    FSL_DATA_CSV = "Model/InputData/FSLData.csv"
    REACH_NETWORK_CSV = "Model/InputData/Hydroedge2_5.csv"
    ATTENUATION_CSV = "Model/InputData/AttenCarry.csv"

    # Output
    OUTPUT_DIR = "Results/PHASE2_RESULTS"
    OUTPUT_FILE = "Lake_Omapere_CW_Analysis_PHASE2_with_comparison.xlsx"

    # Fixed percentages
    BANK_EROSION_PERCENT = 50.0  # 50% of load from bank erosion (not mitigated)
    AG_THRESHOLD = 25.0  # Agricultural % threshold for filtering

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"{title}")
    print("="*80)

def print_subsection(title):
    """Print a formatted subsection header"""
    print(f"\n{title}")
    print("-"*80)

def validate_no_negative_values(df, column_name, description, tolerance=-1e-6):
    """
    Check for negative values where they don't make sense

    tolerance: Small negative values below this threshold are considered rounding errors
    Returns: True if valid, False if problems found
    """
    if column_name not in df.columns:
        return True

    # Check for significantly negative values (not just rounding errors)
    significantly_negative = (df[column_name] < tolerance).sum()
    total_negative = (df[column_name] < 0).sum()

    if significantly_negative > 0:
        print(f"  WARNING: {significantly_negative} significantly negative values found in {column_name} ({description})")
        print(f"    Min value: {df[column_name].min():.6f}")

        # Show examples
        negative_rows = df[df[column_name] < tolerance][['reach_id', column_name]].head(3)
        print(f"    Examples:")
        for _, row in negative_rows.iterrows():
            print(f"      Reach {int(row['reach_id'])}: {row[column_name]:.6f}")

        return False
    elif total_negative > 0:
        # Only rounding errors
        print(f"  NOTE: {total_negative} very small negative values in {column_name} (likely rounding errors)")
        print(f"    Min value: {df[column_name].min():.9f} (within tolerance)")

    return True

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_clues_with_comparison():
    """
    Load BOTH CLUES files for comparison:
    - CLUESloads_baseline.csv: WITH +0.66m inundation
    - CLUESloads.csv: WITHOUT inundation (current baseline)
    """
    print_subsection("Loading CLUES loads WITH and WITHOUT inundation...")

    # Load WITH inundation (+0.66m)
    df_with = pd.read_csv(Config.CLUES_WITH_INUNDATION_PATH)
    print(f"  Loaded {len(df_with):,} reaches WITH +0.66m inundation")
    df_with['Total_TP_WithInundation'] = df_with['TPAgGen'] + df_with['soilP'] + df_with['TPGen']

    # Load WITHOUT inundation (baseline)
    df_without = pd.read_csv(Config.CLUES_WITHOUT_INUNDATION_PATH)
    print(f"  Loaded {len(df_without):,} reaches WITHOUT inundation")
    df_without['Total_TP_NoInundation'] = df_without['TPAgGen'] + df_without['soilP'] + df_without['TPGen']

    # Merge for comparison
    df = df_with[['NZSEGMENT', 'HYDSEQ', 'TPAgGen', 'soilP', 'TPGen', 'Total_TP_WithInundation']].copy()
    df = df.merge(
        df_without[['NZSEGMENT', 'Total_TP_NoInundation']],
        on='NZSEGMENT',
        how='left'
    )

    # Calculate inundation impact
    df['Inundation_Reduction_TP'] = df['Total_TP_NoInundation'] - df['Total_TP_WithInundation']
    df['Inundation_Reduction_Percent'] = (
        (df['Inundation_Reduction_TP'] / df['Total_TP_NoInundation']) * 100.0
    ).fillna(0)

    # Rename for consistency with original code
    df.rename(columns={'Total_TP_WithInundation': 'Total_CLUES_TP'}, inplace=True)

    print(f"\n  Inundation Impact Summary:")
    print(f"    Mean TP with inundation: {df['Total_CLUES_TP'].mean():.6f} t/y")
    print(f"    Mean TP without inundation: {df['Total_TP_NoInundation'].mean():.6f} t/y")
    print(f"    Mean reduction from inundation: {df['Inundation_Reduction_TP'].mean():.6f} t/y ({df['Inundation_Reduction_Percent'].mean():.2f}%)")

    return df[['NZSEGMENT', 'HYDSEQ', 'TPAgGen', 'soilP', 'TPGen', 'Total_CLUES_TP',
               'Total_TP_NoInundation', 'Inundation_Reduction_TP', 'Inundation_Reduction_Percent']].copy()

def load_cw_coverage():
    """Load CW coverage data from GIS calculations"""
    print_subsection("Loading CW coverage data...")

    df = pd.read_excel(Config.CW_COVERAGE_XLSX)
    print(f"  Loaded {len(df)} reaches with CW coverage")

    # Check for required columns
    required_cols = ['nzsegment', 'Type1_GW_Percent', 'Type2_SW_Percent', 'Combined_Percent']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in CW coverage: {missing}")

    print(f"  Combined_Percent range: {df['Combined_Percent'].min():.2f}% - {df['Combined_Percent'].max():.2f}%")
    print(f"  Type2_SW_Percent range: {df['Type2_SW_Percent'].min():.2f}% - {df['Type2_SW_Percent'].max():.2f}%")

    return df

def load_ag_percent():
    """Load agricultural % by reach"""
    print_subsection("Loading agricultural % data...")

    df = pd.read_csv(Config.AG_PERCENT_CSV)
    print(f"  Loaded {len(df)} reaches with ag%")

    # Check for <25% threshold
    below_threshold = df[df['ag_percent'] < Config.AG_THRESHOLD]
    print(f"  Reaches with <{Config.AG_THRESHOLD}% ag: {len(below_threshold)}")
    print(f"  Ag % range: {df['ag_percent'].min():.2f}% - {df['ag_percent'].max():.2f}%")

    return df[['nzsegment', 'ag_percent']].copy()

def load_p_fraction_splits():
    """
    Load P fraction split percentages (PartP, DRP, DOP)

    Fixed values from Annette's methodology:
    PartP: 50% (Particulate P)
    DRP: 25% (Dissolved Reactive P)
    DOP: 25% (Dissolved Organic P)
    """
    print_subsection("Loading P fraction splits...")

    splits = {
        'PartP': 50.0,
        'DRP': 25.0,
        'DOP': 25.0
    }

    print(f"  PartP: {splits['PartP']:.1f}%")
    print(f"  DRP: {splits['DRP']:.1f}%")
    print(f"  DOP: {splits['DOP']:.1f}%")
    print(f"  Total: {sum(splits.values()):.1f}%")

    return splits

def load_hype_pathways():
    """Load HYPE pathway percentages"""
    print_subsection("Loading HYPE pathways...")

    df = pd.read_csv(Config.HYPE_CSV)
    print(f"  Loaded {len(df)} reaches with HYPE pathway data")

    # IMPORTANT: HYPE values are stored as percentages (0-100), convert to fractions (0-1)
    pathway_cols = ['SR', 'TD', 'IF', 'SG', 'DG']
    for col in pathway_cols:
        df[col] = df[col] / 100.0

    # Check pathways sum to ~1.0
    df['pathway_sum'] = df[pathway_cols].sum(axis=1)

    if not np.allclose(df['pathway_sum'], 1.0, atol=0.01):
        print(f"  WARNING: Some pathways don't sum to 1.0")
        print(f"  Range: {df['pathway_sum'].min():.6f} - {df['pathway_sum'].max():.6f}")
    else:
        print(f"  Pathways sum to 1.0 (valid)")

    return df[['NZSEGMENT'] + pathway_cols].copy()

def load_lrfs():
    """
    Load Load Reduction Factors from CW sheet

    Returns DataFrame with columns: ExtCode, Pathway, PartP, DRP, DOP
    where PartP/DRP/DOP are % REMAINING after CW treatment
    """
    print_subsection("Loading LRFs...")

    df = pd.read_excel(Config.LRF_XLSX, sheet_name='CW')
    print(f"  Loaded {len(df)} LRF entries from CW sheet")

    # Extract relevant columns (use median values: PartPmed, DRPmed, DOPmed)
    lrf_df = df[['ExtCode', 'Pathway', 'PartPmed', 'DRPmed', 'DOPmed']].copy()
    lrf_df.rename(columns={'PartPmed': 'PartP', 'DRPmed': 'DRP', 'DOPmed': 'DOP'}, inplace=True)

    # Drop duplicates (keep first occurrence for each ExtCode-Pathway pair)
    lrf_df = lrf_df.drop_duplicates(subset=['ExtCode', 'Pathway'], keep='first')

    # Check ExtCodes
    extcodes = sorted(lrf_df['ExtCode'].unique())
    print(f"  ExtCodes: {extcodes}")
    print(f"  Pathways: {sorted(lrf_df['Pathway'].unique())}")

    # Show example LRF values
    print(f"\n  Example LRF values (% remaining):")
    for extcode in [1.0, 2.0, 3.0]:
        sr_row = lrf_df[(lrf_df['ExtCode'] == extcode) & (lrf_df['Pathway'] == 'SR')]
        if len(sr_row) > 0:
            sr_row = sr_row.iloc[0]
            print(f"    ExtCode {int(extcode)}, SR: PartP={sr_row['PartP']:.0f}%, DRP={sr_row['DRP']:.0f}%, DOP={sr_row['DOP']:.0f}%")

    return lrf_df

def load_clay_constraint():
    """Load clay soil constraint data"""
    print_subsection("Loading clay soil data...")

    df = pd.read_csv(Config.FSL_DATA_CSV)
    print(f"  Loaded {len(df)} reaches with clay %")

    above_50 = df[df['ClayPC'] > 50]
    print(f"  Reaches with >50% clay: {len(above_50)} (LRF = 0)")

    # Rename column to 'Clay' for consistency
    df = df[['NZSEGMENT', 'ClayPC']].copy()
    df.rename(columns={'ClayPC': 'Clay'}, inplace=True)

    return df

def load_reach_network():
    """Load reach network connectivity"""
    print_subsection("Loading reach network...")

    df = pd.read_csv(Config.REACH_NETWORK_CSV)
    print(f"  Loaded {len(df)} network connections")

    return df

def load_attenuation():
    """Load stream attenuation factors"""
    print_subsection("Loading attenuation factors...")

    df = pd.read_csv(Config.ATTENUATION_CSV)
    print(f"  Loaded {len(df)} reaches with PstreamCarry")
    print(f"  PstreamCarry range: {df['PstreamCarry'].min():.6f} - {df['PstreamCarry'].max():.6f}")

    return df[['NZSEGMENT', 'PstreamCarry']].copy()

# ============================================================================
# COVERAGE CATEGORY FUNCTIONS
# ============================================================================

def assign_coverage_category(coverage_percent):
    """
    Assign coverage category based on % coverage
    (Matching LRF file's Extent codes)

    ExtCode 1: <2% coverage (77% removal - most efficient per unit area)
    ExtCode 2: 2-4% coverage (58% removal)
    ExtCode 3: >4% coverage (52% removal - least efficient per unit area)
    """
    if coverage_percent < 2.0:
        return 'SMALL', 1
    elif coverage_percent <= 4.0:
        return 'MEDIUM', 2
    else:
        return 'LARGE', 3

# ============================================================================
# CORE CALCULATION FUNCTIONS
# ============================================================================

def apply_ag_filter(total_clues_tp, ag_percent):
    """
    NEW REQUIREMENT #3: Agricultural % filter

    If ag% < 25%:
        Available_Load = Total_CLUES_TP × (ag% / 100)
    Else:
        Available_Load = Total_CLUES_TP

    This represents the portion of load that can be mitigated by CWs
    """
    if ag_percent < Config.AG_THRESHOLD:
        available = total_clues_tp * (ag_percent / 100.0)
        filter_applied = True
    else:
        available = total_clues_tp
        filter_applied = False

    return available, filter_applied

def split_p_fractions(available_load, p_splits):
    """Split available load into P fractions (PartP, DRP, DOP)"""
    return {
        'PartP': available_load * (p_splits['PartP'] / 100.0),
        'DRP': available_load * (p_splits['DRP'] / 100.0),
        'DOP': available_load * (p_splits['DOP'] / 100.0)
    }

def split_bank_erosion(p_fraction_load):
    """
    Split P fraction into bank erosion (50%) and hillslope (50%)

    Bank erosion is NOT mitigated by CWs
    Hillslope load goes through pathways and CW mitigation
    """
    bank = p_fraction_load * (Config.BANK_EROSION_PERCENT / 100.0)
    hillslope = p_fraction_load * ((100.0 - Config.BANK_EROSION_PERCENT) / 100.0)
    return bank, hillslope

def distribute_by_pathways_PHASE2(hillslope_load, p_fraction_name, hype_pathways):
    """
    NEW REQUIREMENT #1: PartP surface-only routing

    PartP: 100% to SR (surface runoff) only
           0% to all other pathways (TD, IF, SG, DG)

    DRP & DOP: Distribute by HYPE pathway percentages (all pathways)
    """
    pathway_loads = {}

    if p_fraction_name == 'PartP':
        # NEW: PartP goes ONLY to surface runoff
        pathway_loads['SR'] = hillslope_load * 1.0  # 100% to SR
        pathway_loads['TD'] = 0.0
        pathway_loads['IF'] = 0.0
        pathway_loads['SG'] = 0.0
        pathway_loads['DG'] = 0.0
    else:
        # DRP and DOP use all HYPE pathways
        pathway_loads['SR'] = hillslope_load * hype_pathways['SR']
        pathway_loads['TD'] = hillslope_load * hype_pathways['TD']
        pathway_loads['IF'] = hillslope_load * hype_pathways['IF']
        pathway_loads['SG'] = hillslope_load * hype_pathways['SG']
        pathway_loads['DG'] = hillslope_load * hype_pathways['DG']

    return pathway_loads

def apply_lrf(pathway_load, p_fraction_name, pathway_name, extcode, lrf_data, clay_percent):
    """
    Apply Load Reduction Factor

    If clay% > 50%: LRF = 0 (no effectiveness)
    Otherwise: Use LRF from lookup table

    LRF represents % REMAINING after CW treatment
    """
    # Clay constraint
    if clay_percent > 50:
        return 0.0, pathway_load  # No reduction, all remains

    # Get LRF from lookup
    lrf_row = lrf_data[(lrf_data['ExtCode'] == extcode) & (lrf_data['Pathway'] == pathway_name)]

    if len(lrf_row) == 0:
        # No LRF found, assume no treatment
        return 0.0, pathway_load

    lrf_percent = lrf_row.iloc[0][p_fraction_name]  # % remaining

    removed = pathway_load * ((100.0 - lrf_percent) / 100.0)
    remaining = pathway_load * (lrf_percent / 100.0)

    return removed, remaining

# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def run_analysis_for_scenario(scenario_name, coverage_column, all_data, p_splits, lrf_data):
    """
    Run complete analysis for one scenario

    scenario_name: "Scenario1_SurfaceGW" or "Scenario2_SurfaceOnly"
    coverage_column: "Combined_Percent" or "Type2_SW_Percent"
    """
    print_section(f"RUNNING {scenario_name}")

    results = []

    for idx, row in all_data.iterrows():
        reach_id = int(row['NZSEGMENT'])

        # 1. CLUES Load (with +0.66m inundation)
        total_clues = row['Total_CLUES_TP']

        # NEW: CLUES load without inundation
        total_clues_no_inundation = row['Total_TP_NoInundation']
        inundation_reduction_tp = row['Inundation_Reduction_TP']
        inundation_reduction_percent = row['Inundation_Reduction_Percent']

        # 2. Agricultural % Filter (NEW!)
        ag_percent = row['ag_percent']
        available_load, ag_filter_applied = apply_ag_filter(total_clues, ag_percent)

        # 3. P Fraction Splits
        p_fractions = split_p_fractions(available_load, p_splits)

        # 4. CW Coverage and Category
        cw_coverage = row[coverage_column]
        coverage_category, extcode = assign_coverage_category(cw_coverage)

        # 5. Clay Constraint
        clay_percent = row['Clay']

        # 6. Process each P fraction
        total_baseline = 0.0
        total_with_cw = 0.0
        total_removed = 0.0

        p_fraction_results = {}

        for p_name in ['PartP', 'DRP', 'DOP']:
            p_load = p_fractions[p_name]

            # Split bank erosion vs hillslope
            bank_erosion, hillslope = split_bank_erosion(p_load)

            # Distribute hillslope by pathways (NEW LOGIC for PartP!)
            hype_pathways = {
                'SR': row['SR'],
                'TD': row['TD'],
                'IF': row['IF'],
                'SG': row['SG'],
                'DG': row['DG']
            }

            pathway_loads = distribute_by_pathways_PHASE2(hillslope, p_name, hype_pathways)

            # Apply LRFs to each pathway
            p_removed = 0.0
            p_remaining_pathways = 0.0

            pathway_results = {}

            for pathway in ['SR', 'TD', 'IF', 'SG', 'DG']:
                pathway_load = pathway_loads[pathway]

                if pathway_load > 0:
                    removed, remaining = apply_lrf(
                        pathway_load, p_name, pathway, extcode, lrf_data, clay_percent
                    )
                    p_removed += removed
                    p_remaining_pathways += remaining

                    pathway_results[f'{p_name}_{pathway}_input'] = pathway_load
                    pathway_results[f'{p_name}_{pathway}_removed'] = removed
                    pathway_results[f'{p_name}_{pathway}_remaining'] = remaining
                else:
                    pathway_results[f'{p_name}_{pathway}_input'] = 0.0
                    pathway_results[f'{p_name}_{pathway}_removed'] = 0.0
                    pathway_results[f'{p_name}_{pathway}_remaining'] = 0.0

            # Total for this P fraction
            p_baseline = p_load
            p_with_cw = bank_erosion + p_remaining_pathways

            total_baseline += p_baseline
            total_with_cw += p_with_cw
            total_removed += (p_baseline - p_with_cw)

            # Store P fraction results
            p_fraction_results[f'{p_name}_baseline'] = p_baseline
            p_fraction_results[f'{p_name}_bank_erosion'] = bank_erosion
            p_fraction_results[f'{p_name}_hillslope'] = hillslope
            p_fraction_results[f'{p_name}_with_cw'] = p_with_cw
            p_fraction_results[f'{p_name}_removed'] = p_baseline - p_with_cw
            p_fraction_results.update(pathway_results)

        # 7. Calculate totals
        cw_reduction = total_removed
        cw_reduction_percent = (cw_reduction / total_baseline * 100.0) if total_baseline > 0 else 0.0

        # 8. Apply stream attenuation (routing to lake)
        pstream_carry = row['PstreamCarry']
        routed_baseline = total_baseline * pstream_carry
        routed_with_cw = total_with_cw * pstream_carry
        routed_reduction = routed_baseline - routed_with_cw
        routed_reduction_percent = (routed_reduction / routed_baseline * 100.0) if routed_baseline > 0 else 0.0

        # Store all results
        result = {
            'reach_id': reach_id,
            'HYDSEQ': row['HYDSEQ'],
            'Scenario': scenario_name,
            'ag_percent': ag_percent,
            'ag_filter_applied': ag_filter_applied,
            'Total_CLUES_TP': total_clues,
            'Total_TP_NoInundation': total_clues_no_inundation,
            'Inundation_Reduction_TP': inundation_reduction_tp,
            'Inundation_Reduction_Percent': inundation_reduction_percent,
            'Available_Load': available_load,
            'CW_Coverage_Percent': cw_coverage,
            'coverage_category': coverage_category,
            'ExtCode': extcode,
            'clay_percent': clay_percent,
            'generated_baseline': total_baseline,
            'generated_with_cw': total_with_cw,
            'cw_reduction': cw_reduction,
            'cw_reduction_percent': cw_reduction_percent,
            'PstreamCarry': pstream_carry,
            'routed_baseline': routed_baseline,
            'routed_with_cw': routed_with_cw,
            'routed_reduction': routed_reduction,
            'routed_reduction_percent': routed_reduction_percent,
        }

        # Add P fraction results
        result.update(p_fraction_results)

        results.append(result)

    # Convert to DataFrame
    results_df = pd.DataFrame(results)

    # Summary statistics
    print(f"\n{scenario_name} Summary:")
    print(f"  Reaches: {len(results_df)}")
    print(f"  Mean CW coverage: {results_df['CW_Coverage_Percent'].mean():.2f}%")
    print(f"  Mean CW reduction: {results_df['cw_reduction_percent'].mean():.2f}%")
    print(f"  Total baseline load: {results_df['generated_baseline'].sum():.3f} t/y")
    print(f"  Total with CW: {results_df['generated_with_cw'].sum():.3f} t/y")
    print(f"  Total reduction: {results_df['cw_reduction'].sum():.3f} t/y ({results_df['cw_reduction'].sum() / results_df['generated_baseline'].sum() * 100:.1f}%)")
    print(f"  Reaches with ag filter: {results_df['ag_filter_applied'].sum()}")
    print(f"\n  Inundation Impact:")
    print(f"    Mean TP without inundation: {results_df['Total_TP_NoInundation'].mean():.6f} t/y")
    print(f"    Mean TP with +0.66m inundation: {results_df['Total_CLUES_TP'].mean():.6f} t/y")
    print(f"    Mean reduction from inundation: {results_df['Inundation_Reduction_Percent'].mean():.2f}%")

    return results_df

# ============================================================================
# COLUMN DESCRIPTIONS
# ============================================================================

def generate_column_descriptions():
    """Generate descriptions for all output columns"""

    descriptions = [
        ('reach_id', 'NZ Reach Segment ID (NZSEGMENT)'),
        ('HYDSEQ', 'Hydrological sequence number (upstream to downstream order)'),
        ('Scenario', 'Analysis scenario (Scenario1_SurfaceGW or Scenario2_SurfaceOnly)'),
        ('ag_percent', 'Agricultural land use percentage'),
        ('ag_filter_applied', 'Whether agricultural <25% filter was applied (TRUE/FALSE)'),
        ('Total_CLUES_TP', 'Total CLUES TP load WITH +0.66m inundation (t/y)'),
        ('Total_TP_NoInundation', 'Total CLUES TP load WITHOUT inundation (baseline) (t/y)'),
        ('Inundation_Reduction_TP', 'TP reduction from inundation (NoInundation - WithInundation); negative = increase (t/y)'),
        ('Inundation_Reduction_Percent', 'Percentage reduction from inundation; negative = increase (%)'),
        ('Available_Load', 'Load available for CW mitigation after ag% filter (t/y)'),
        ('CW_Coverage_Percent', 'Constructed wetland coverage as % of reach area'),
        ('coverage_category', 'CW coverage category (SMALL, MEDIUM, LARGE)'),
        ('ExtCode', 'Extent code for LRF lookup (1, 2, or 3)'),
        ('clay_percent', 'Clay soil percentage (>50% → LRF = 0)'),
        ('generated_baseline', 'Total generated TP baseline without CW (t/y)'),
        ('generated_with_cw', 'Total generated TP with CW mitigation (t/y)'),
        ('cw_reduction', 'TP reduction by CW (t/y)'),
        ('cw_reduction_percent', 'TP reduction by CW as percentage (%)'),
        ('PstreamCarry', 'Stream attenuation factor (proportion reaching lake)'),
        ('routed_baseline', 'Routed TP baseline without CW (t/y)'),
        ('routed_with_cw', 'Routed TP with CW mitigation (t/y)'),
        ('routed_reduction', 'Routed TP reduction by CW (t/y)'),
        ('routed_reduction_percent', 'Routed TP reduction by CW as percentage (%)'),

        # P Fractions
        ('PartP_baseline', 'Particulate P baseline load (t/y)'),
        ('PartP_bank_erosion', 'PartP from bank erosion (not mitigated) (t/y)'),
        ('PartP_hillslope', 'PartP from hillslope (mitigated by CW) (t/y)'),
        ('PartP_with_cw', 'PartP after CW mitigation (t/y)'),
        ('PartP_removed', 'PartP removed by CW (t/y)'),

        ('DRP_baseline', 'Dissolved Reactive P baseline load (t/y)'),
        ('DRP_bank_erosion', 'DRP from bank erosion (not mitigated) (t/y)'),
        ('DRP_hillslope', 'DRP from hillslope (mitigated by CW) (t/y)'),
        ('DRP_with_cw', 'DRP after CW mitigation (t/y)'),
        ('DRP_removed', 'DRP removed by CW (t/y)'),

        ('DOP_baseline', 'Dissolved Organic P baseline load (t/y)'),
        ('DOP_bank_erosion', 'DOP from bank erosion (not mitigated) (t/y)'),
        ('DOP_hillslope', 'DOP from hillslope (mitigated by CW) (t/y)'),
        ('DOP_with_cw', 'DOP after CW mitigation (t/y)'),
        ('DOP_removed', 'DOP removed by CW (t/y)'),

        # Pathways - PartP
        ('PartP_SR_input', 'PartP input to SR pathway (100% for PartP - NEW!) (t/y)'),
        ('PartP_SR_removed', 'PartP removed by CW in SR pathway (t/y)'),
        ('PartP_SR_remaining', 'PartP remaining after CW in SR pathway (t/y)'),
        ('PartP_TD_input', 'PartP input to TD pathway (0% for PartP - NEW!) (t/y)'),
        ('PartP_TD_removed', 'PartP removed by CW in TD pathway (t/y)'),
        ('PartP_TD_remaining', 'PartP remaining after CW in TD pathway (t/y)'),
        ('PartP_IF_input', 'PartP input to IF pathway (0% for PartP - NEW!) (t/y)'),
        ('PartP_IF_removed', 'PartP removed by CW in IF pathway (t/y)'),
        ('PartP_IF_remaining', 'PartP remaining after CW in IF pathway (t/y)'),
        ('PartP_SG_input', 'PartP input to SG pathway (0% for PartP - NEW!) (t/y)'),
        ('PartP_SG_removed', 'PartP removed by CW in SG pathway (t/y)'),
        ('PartP_SG_remaining', 'PartP remaining after CW in SG pathway (t/y)'),
        ('PartP_DG_input', 'PartP input to DG pathway (0% for PartP - NEW!) (t/y)'),
        ('PartP_DG_removed', 'PartP removed by CW in DG pathway (t/y)'),
        ('PartP_DG_remaining', 'PartP remaining after CW in DG pathway (t/y)'),

        # Pathways - DRP
        ('DRP_SR_input', 'DRP input to SR pathway (by HYPE %) (t/y)'),
        ('DRP_SR_removed', 'DRP removed by CW in SR pathway (t/y)'),
        ('DRP_SR_remaining', 'DRP remaining after CW in SR pathway (t/y)'),
        ('DRP_TD_input', 'DRP input to TD pathway (by HYPE %) (t/y)'),
        ('DRP_TD_removed', 'DRP removed by CW in TD pathway (t/y)'),
        ('DRP_TD_remaining', 'DRP remaining after CW in TD pathway (t/y)'),
        ('DRP_IF_input', 'DRP input to IF pathway (by HYPE %) (t/y)'),
        ('DRP_IF_removed', 'DRP removed by CW in IF pathway (t/y)'),
        ('DRP_IF_remaining', 'DRP remaining after CW in IF pathway (t/y)'),
        ('DRP_SG_input', 'DRP input to SG pathway (by HYPE %) (t/y)'),
        ('DRP_SG_removed', 'DRP removed by CW in SG pathway (t/y)'),
        ('DRP_SG_remaining', 'DRP remaining after CW in SG pathway (t/y)'),
        ('DRP_DG_input', 'DRP input to DG pathway (by HYPE %) (t/y)'),
        ('DRP_DG_removed', 'DRP removed by CW in DG pathway (t/y)'),
        ('DRP_DG_remaining', 'DRP remaining after CW in DG pathway (t/y)'),

        # Pathways - DOP
        ('DOP_SR_input', 'DOP input to SR pathway (by HYPE %) (t/y)'),
        ('DOP_SR_removed', 'DOP removed by CW in SR pathway (t/y)'),
        ('DOP_SR_remaining', 'DOP remaining after CW in SR pathway (t/y)'),
        ('DOP_TD_input', 'DOP input to TD pathway (by HYPE %) (t/y)'),
        ('DOP_TD_removed', 'DOP removed by CW in TD pathway (t/y)'),
        ('DOP_TD_remaining', 'DOP remaining after CW in TD pathway (t/y)'),
        ('DOP_IF_input', 'DOP input to IF pathway (by HYPE %) (t/y)'),
        ('DOP_IF_removed', 'DOP removed by CW in IF pathway (t/y)'),
        ('DOP_IF_remaining', 'DOP remaining after CW in IF pathway (t/y)'),
        ('DOP_SG_input', 'DOP input to SG pathway (by HYPE %) (t/y)'),
        ('DOP_SG_removed', 'DOP removed by CW in SG pathway (t/y)'),
        ('DOP_SG_remaining', 'DOP remaining after CW in SG pathway (t/y)'),
        ('DOP_DG_input', 'DOP input to DG pathway (by HYPE %) (t/y)'),
        ('DOP_DG_removed', 'DOP removed by CW in DG pathway (t/y)'),
        ('DOP_DG_remaining', 'DOP remaining after CW in DG pathway (t/y)'),
    ]

    return pd.DataFrame(descriptions, columns=['Column', 'Description'])

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_results(results_df, scenario_name):
    """
    Validate results for illogical values

    Checks for:
    - Negative TP loads
    - Negative percentages
    - Negative reductions
    - Reductions > baseline (>100%)
    """
    print_section(f"VALIDATING {scenario_name} RESULTS")

    all_valid = True

    # Check for negative TP loads
    load_columns = ['Total_CLUES_TP', 'Total_TP_NoInundation', 'Available_Load',
                    'generated_baseline', 'generated_with_cw', 'routed_baseline', 'routed_with_cw']

    for col in load_columns:
        if not validate_no_negative_values(results_df, col, "TP load"):
            all_valid = False

    # Check for negative coverage percentages
    if not validate_no_negative_values(results_df, 'CW_Coverage_Percent', "CW coverage %"):
        all_valid = False

    if not validate_no_negative_values(results_df, 'ag_percent', "Agricultural %"):
        all_valid = False

    # Check for negative reductions
    reduction_columns = ['cw_reduction', 'routed_reduction',
                         'PartP_removed', 'DRP_removed', 'DOP_removed']

    for col in reduction_columns:
        if not validate_no_negative_values(results_df, col, "reduction"):
            all_valid = False

    # Check for over-reduction (>100%)
    over_reduction = (results_df['cw_reduction_percent'] > 100).sum()
    if over_reduction > 0:
        print(f"  WARNING: {over_reduction} reaches have >100% reduction (illogical)")
        all_valid = False

    # Check with_cw > baseline (illogical)
    cw_increase = (results_df['generated_with_cw'] > results_df['generated_baseline']).sum()
    if cw_increase > 0:
        print(f"  WARNING: {cw_increase} reaches have with_cw > baseline (CWs increasing load?)")
        all_valid = False

    if all_valid:
        print(f"\n  All validation checks passed!")
    else:
        print(f"\n  VALIDATION FAILED - Please review warnings above")

    return all_valid

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""

    print_section("LAKE OMAPERE CW ANALYSIS - PHASE 2 WITH INUNDATION COMPARISON")
    print("Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Project: TKIL2602 - Lake Omapere Modelling")
    print("\nImplementing Fleur's 6 requirements PLUS inundation comparison:")
    print("  1. PartP surface-only routing (SR only)")
    print("  2. CLUES +0.66m lake level (CONFIRMED)")
    print("  3. Agricultural <25% filter with NEW scaling")
    print("  4. Dual CW scenarios (Surface+GW and Surface-only)")
    print("  5. Terminal reaches column (pending)")
    print("  6. Column descriptions worksheet")
    print("  NEW: CLUES loads WITHOUT inundation for comparison")
    print("  NEW: Validation for illogical negative values")
    print("  NEW: Reaches sorted by HYDSEQ (upstream to downstream)")

    # ========================================================================
    # STEP 1: LOAD ALL DATA
    # ========================================================================

    print_section("STEP 1: LOADING INPUT DATA")

    clues = load_clues_with_comparison()  # NEW: Loads both with/without inundation
    cw_coverage = load_cw_coverage()
    ag_percent = load_ag_percent()
    p_splits = load_p_fraction_splits()
    hype = load_hype_pathways()
    lrf_data = load_lrfs()
    clay = load_clay_constraint()
    network = load_reach_network()
    attenuation = load_attenuation()

    # ========================================================================
    # STEP 2: MERGE ALL DATA
    # ========================================================================

    print_section("STEP 2: MERGING DATA")

    # Start with CLUES
    all_data = clues.copy()
    print(f"Starting with {len(all_data)} reaches from CLUES")

    # Merge with CW coverage
    all_data = all_data.merge(
        cw_coverage.rename(columns={'nzsegment': 'NZSEGMENT'}),
        on='NZSEGMENT',
        how='inner'
    )
    print(f"After CW coverage merge: {len(all_data)} reaches")

    # Merge with ag%
    all_data = all_data.merge(
        ag_percent.rename(columns={'nzsegment': 'NZSEGMENT'}),
        on='NZSEGMENT',
        how='left'
    )
    print(f"After ag% merge: {len(all_data)} reaches")

    # Merge with HYPE
    all_data = all_data.merge(hype, on='NZSEGMENT', how='left')
    print(f"After HYPE merge: {len(all_data)} reaches")

    # Merge with clay
    all_data = all_data.merge(clay, on='NZSEGMENT', how='left')
    print(f"After clay merge: {len(all_data)} reaches")

    # Merge with attenuation
    all_data = all_data.merge(attenuation, on='NZSEGMENT', how='left')
    print(f"After attenuation merge: {len(all_data)} reaches")

    # Fill any missing values
    all_data['Clay'] = all_data['Clay'].fillna(0)
    all_data['PstreamCarry'] = all_data['PstreamCarry'].fillna(1.0)

    # NEW: Sort by HYDSEQ (upstream to downstream order)
    all_data = all_data.sort_values('HYDSEQ').reset_index(drop=True)
    print(f"\nSorted by HYDSEQ (upstream to downstream)")

    print(f"\nFinal dataset: {len(all_data)} Lake Omapere reaches ready for analysis")

    # ========================================================================
    # STEP 3: RUN ANALYSIS FOR BOTH SCENARIOS
    # ========================================================================

    # Scenario 1: Surface + Groundwater CWs
    results_scenario1 = run_analysis_for_scenario(
        scenario_name='Scenario1_SurfaceGW',
        coverage_column='Combined_Percent',
        all_data=all_data,
        p_splits=p_splits,
        lrf_data=lrf_data
    )

    # Scenario 2: Surface CWs Only
    results_scenario2 = run_analysis_for_scenario(
        scenario_name='Scenario2_SurfaceOnly',
        coverage_column='Type2_SW_Percent',
        all_data=all_data,
        p_splits=p_splits,
        lrf_data=lrf_data
    )

    # ========================================================================
    # STEP 4: VALIDATE RESULTS
    # ========================================================================

    valid_scenario1 = validate_results(results_scenario1, 'Scenario1_SurfaceGW')
    valid_scenario2 = validate_results(results_scenario2, 'Scenario2_SurfaceOnly')

    if not valid_scenario1 or not valid_scenario2:
        print("\nWARNING: Validation issues found. Please review before using results.")

    # ========================================================================
    # STEP 5: COMBINE AND SAVE RESULTS
    # ========================================================================

    print_section("STEP 5: SAVING RESULTS")

    # Combine both scenarios
    all_results = pd.concat([results_scenario1, results_scenario2], ignore_index=True)

    # NEW: Reorder columns in logical, reviewer-friendly order
    print("\nReordering columns for reviewer...")

    column_order = [
        # 1. Identification & Scenario
        'reach_id',
        'HYDSEQ',
        'Scenario',

        # 2. Input Parameters
        'ag_percent',
        'ag_filter_applied',
        'CW_Coverage_Percent',
        'coverage_category',
        'ExtCode',
        'clay_percent',
        'PstreamCarry',

        # 3. CLUES Loads (Inundation Comparison)
        'Total_TP_NoInundation',
        'Total_CLUES_TP',
        'Inundation_Reduction_TP',
        'Inundation_Reduction_Percent',

        # 4. Available Load
        'Available_Load',

        # 5. Generated Loads (reach-level)
        'generated_baseline',
        'generated_with_cw',
        'cw_reduction',
        'cw_reduction_percent',

        # 6. Routed Loads (to lake)
        'routed_baseline',
        'routed_with_cw',
        'routed_reduction',
        'routed_reduction_percent',

        # 7. P Fractions Summary
        'PartP_baseline',
        'PartP_bank_erosion',
        'PartP_hillslope',
        'PartP_with_cw',
        'PartP_removed',

        'DRP_baseline',
        'DRP_bank_erosion',
        'DRP_hillslope',
        'DRP_with_cw',
        'DRP_removed',

        'DOP_baseline',
        'DOP_bank_erosion',
        'DOP_hillslope',
        'DOP_with_cw',
        'DOP_removed',

        # 8. Pathway Details - PartP
        'PartP_SR_input',
        'PartP_SR_removed',
        'PartP_SR_remaining',
        'PartP_TD_input',
        'PartP_TD_removed',
        'PartP_TD_remaining',
        'PartP_IF_input',
        'PartP_IF_removed',
        'PartP_IF_remaining',
        'PartP_SG_input',
        'PartP_SG_removed',
        'PartP_SG_remaining',
        'PartP_DG_input',
        'PartP_DG_removed',
        'PartP_DG_remaining',

        # 9. Pathway Details - DRP
        'DRP_SR_input',
        'DRP_SR_removed',
        'DRP_SR_remaining',
        'DRP_TD_input',
        'DRP_TD_removed',
        'DRP_TD_remaining',
        'DRP_IF_input',
        'DRP_IF_removed',
        'DRP_IF_remaining',
        'DRP_SG_input',
        'DRP_SG_removed',
        'DRP_SG_remaining',
        'DRP_DG_input',
        'DRP_DG_removed',
        'DRP_DG_remaining',

        # 10. Pathway Details - DOP
        'DOP_SR_input',
        'DOP_SR_removed',
        'DOP_SR_remaining',
        'DOP_TD_input',
        'DOP_TD_removed',
        'DOP_TD_remaining',
        'DOP_IF_input',
        'DOP_IF_removed',
        'DOP_IF_remaining',
        'DOP_SG_input',
        'DOP_SG_removed',
        'DOP_SG_remaining',
        'DOP_DG_input',
        'DOP_DG_removed',
        'DOP_DG_remaining',
    ]

    # Reorder columns
    all_results = all_results[column_order]

    print(f"  Columns organized in logical groups:")
    print(f"    1. Identification & Scenario (3 cols: reach_id, HYDSEQ, Scenario)")
    print(f"    2. Input Parameters (7 cols)")
    print(f"    3. CLUES Loads - Inundation Comparison (4 cols)")
    print(f"    4. Available Load (1 col)")
    print(f"    5. Generated Loads (4 cols)")
    print(f"    6. Routed Loads (4 cols)")
    print(f"    7. P Fractions Summary (15 cols)")
    print(f"    8-10. Pathway Details by P type (45 cols)")
    print(f"  Total: 83 columns")

    # Generate column descriptions
    column_descriptions = generate_column_descriptions()

    # Create output directory
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(Config.OUTPUT_DIR, Config.OUTPUT_FILE)

    # Write to Excel
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        all_results.to_excel(writer, sheet_name='Results', index=False)
        column_descriptions.to_excel(writer, sheet_name='Column_Descriptions', index=False)

    print(f"\nResults saved to: {output_path}")
    print(f"  Rows: {len(all_results)} ({len(results_scenario1)} + {len(results_scenario2)} for 2 scenarios)")
    print(f"  Columns: {len(all_results.columns)}")
    print(f"  Sheets: 2 (Results + Column_Descriptions)")

    print(f"\nNew columns added:")
    print(f"  - HYDSEQ: Hydrological sequence (upstream to downstream)")
    print(f"  - Total_TP_NoInundation: Baseline TP without inundation")
    print(f"  - Inundation_Reduction_TP: TP reduction from inundation (negative = increase)")
    print(f"  - Inundation_Reduction_Percent: Percent reduction from inundation (negative = increase)")

    print(f"\nNOTE: Some reaches show negative inundation reduction (load increases with inundation).")
    print(f"  This indicates differences between the two CLUES files beyond just inundation effects.")

    print_section("ANALYSIS COMPLETE")

    return all_results, column_descriptions

if __name__ == "__main__":
    main()
