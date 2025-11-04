"""
Script to prepare model input files from CLUES spreadsheets:
1. Create selection CSV for 50 Lake Omapere reaches
2. Update CLUESloads.csv for baseline and wetland runs
3. Update AttenCarry.csv for baseline and wetland runs
"""

from pyxlsb import open_workbook
import pandas as pd
import os

baseline_file = r'C:\Users\moghaddamr\Reza_CW_Analysis\TP_noMit_LakeOnly_baseline.xlsb'
wetland_file = r'C:\Users\moghaddamr\Reza_CW_Analysis\TP_noMit_LakeOnly+0.66m.xlsb'
model_dir = r'C:\Users\moghaddamr\Reza_CW_Analysis\Model'

def read_xlsb_sheet(filename, sheet_name):
    """Read a sheet from an XLSB file into a pandas DataFrame"""
    with open_workbook(filename) as wb:
        with wb.get_sheet(sheet_name) as sheet:
            rows = []
            for row in sheet.rows():
                row_data = [item.v if item else None for item in row]
                rows.append(row_data)
    df = pd.DataFrame(rows[1:], columns=rows[0])
    return df

# ========== STEP 1: Get Lake Omapere reach list ==========
print("Step 1: Extracting Lake Omapere reach list...")
lomapere_reaches_df = read_xlsb_sheet(baseline_file, 'LOmapereReaches')
reach_list = lomapere_reaches_df['nzsegment'].dropna().astype(int).tolist()
print(f"Found {len(reach_list)} Lake Omapere reaches")

# ========== STEP 2: Create selection CSV ==========
print("\nStep 2: Creating selection CSV...")

# Read existing selection file to understand structure
selection_file = os.path.join(model_dir, 'SelectionFiles', 'REC2_5.csv')
selection_df = pd.read_csv(selection_file)
print(f"Original selection file shape: {selection_df.shape}")
print(f"Columns: {selection_df.columns.tolist()}")

# Create new selection with 1s for Lake Omapere reaches, 0s for others
new_selection_df = selection_df.copy()
# Assuming the reach ID column - check what it's called
if 'nzsegment' in new_selection_df.columns:
    reach_col = 'nzsegment'
elif 'NZSEGMENT' in new_selection_df.columns:
    reach_col = 'NZSEGMENT'
else:
    reach_col = new_selection_df.columns[0]  # Assume first column is reach ID

print(f"Using reach column: {reach_col}")

# Set Value column based on whether reach is in Lake Omapere list
if 'Value' in new_selection_df.columns:
    new_selection_df['Value'] = new_selection_df[reach_col].apply(
        lambda x: 1 if x in reach_list else 0
    )
else:
    print("Warning: No 'Value' column found in selection file")
    print(f"Available columns: {new_selection_df.columns.tolist()}")

# Save new selection file
output_selection_file = os.path.join(model_dir, 'SelectionFiles', 'LakeOmapere_Selection.csv')
new_selection_df.to_csv(output_selection_file, index=False)
print(f"Created: {output_selection_file}")
print(f"Number of reaches with Value=1: {(new_selection_df['Value'] == 1).sum() if 'Value' in new_selection_df.columns else 'N/A'}")

# ========== STEP 3: Extract data from CLUES spreadsheets ==========
print("\nStep 3: Extracting data from CLUES spreadsheets...")

def extract_clues_data(filename, scenario_name):
    """Extract required columns from CLUES spreadsheet"""
    reaches_df = read_xlsb_sheet(filename, 'Reaches')

    # Extract columns (using indices since column names might vary slightly):
    # Column indices: nzsegment=0, T=19, AF=31, BC=54, BD=55, BF=57
    data = pd.DataFrame({
        'nzsegment': reaches_df['nzsegment'],
        'soilP': reaches_df.iloc[:, 19],  # Column T: P_Sed
        'TPAgGen': reaches_df.iloc[:, 31],  # Column AF: OVERSEER Load
        'LoadIncrement': reaches_df.iloc[:, 54],  # Column BC: LoadIncrement
        'PstreamCarry': reaches_df.iloc[:, 55],  # Column BD: StreamCarry
        'PresCarry': reaches_df.iloc[:, 57],  # Column BF: ResCarry
    })

    # Calculate TPGen = LoadIncrement - TPAgGen - soilP
    data['TPGen'] = data['LoadIncrement'] - data['TPAgGen'] - data['soilP']

    print(f"\n{scenario_name} data extracted:")
    print(f"  Shape: {data.shape}")
    print(f"  Sample values for reach {reach_list[0]}:")
    sample = data[data['nzsegment'] == reach_list[0]]
    if not sample.empty:
        print(f"    soilP (T): {sample['soilP'].values[0]}")
        print(f"    TPAgGen (AF): {sample['TPAgGen'].values[0]}")
        print(f"    LoadIncrement (BC): {sample['LoadIncrement'].values[0]}")
        print(f"    TPGen (calculated): {sample['TPGen'].values[0]}")
        print(f"    PstreamCarry (BD): {sample['PstreamCarry'].values[0]}")
        print(f"    PresCarry (BF): {sample['PresCarry'].values[0]}")

    return data

baseline_data = extract_clues_data(baseline_file, "Baseline")
wetland_data = extract_clues_data(wetland_file, "Wetland (+0.66m)")

# ========== STEP 4: Update CLUESloads.csv ==========
print("\nStep 4: Updating CLUESloads.csv files...")

# Read original CLUESloads.csv to understand structure
cluesloads_file = os.path.join(model_dir, 'InputData', 'CLUESloads.csv')
cluesloads_df = pd.read_csv(cluesloads_file)
print(f"Original CLUESloads.csv shape: {cluesloads_df.shape}")
print(f"Columns: {cluesloads_df.columns.tolist()}")

def update_cluesloads(original_df, clues_data, output_name):
    """Update CLUESloads.csv with data from CLUES spreadsheet"""
    updated_df = original_df.copy()

    # Determine reach column name
    if 'nzsegment' in updated_df.columns:
        reach_col = 'nzsegment'
    elif 'NZSEGMENT' in updated_df.columns:
        reach_col = 'NZSEGMENT'
    else:
        reach_col = updated_df.columns[0]

    # Merge data
    # Columns H, I, J should be: TPAgGen, soilP, TPGen (or similar names)
    # Need to check actual column names in CLUESloads.csv
    print(f"\n  Updating {output_name}...")
    print(f"  Reach column: {reach_col}")

    # Map the data
    for idx, row in updated_df.iterrows():
        reach_id = row[reach_col]
        clues_row = clues_data[clues_data['nzsegment'] == reach_id]
        if not clues_row.empty:
            # Update columns H, I, J (indices 7, 8, 9)
            # Assuming columns are: ..., TPAgGen, soilP, TPGen, ...
            # Check which columns correspond to H, I, J
            if 'TPAgGen' in updated_df.columns:
                updated_df.at[idx, 'TPAgGen'] = clues_row['TPAgGen'].values[0]
            if 'soilP' in updated_df.columns:
                updated_df.at[idx, 'soilP'] = clues_row['soilP'].values[0]
            if 'TPGen' in updated_df.columns:
                updated_df.at[idx, 'TPGen'] = clues_row['TPGen'].values[0]

    # Save
    output_file = os.path.join(model_dir, 'InputData', f'CLUESloads_{output_name}.csv')
    updated_df.to_csv(output_file, index=False)
    print(f"  Created: {output_file}")
    return updated_df

baseline_cluesloads = update_cluesloads(cluesloads_df, baseline_data, 'baseline')
wetland_cluesloads = update_cluesloads(cluesloads_df, wetland_data, 'wetland_066m')

# ========== STEP 5: Update AttenCarry.csv ==========
print("\nStep 5: Updating AttenCarry.csv files...")

attencarry_file = os.path.join(model_dir, 'InputData', 'AttenCarry.csv')
attencarry_df = pd.read_csv(attencarry_file)
print(f"Original AttenCarry.csv shape: {attencarry_df.shape}")
print(f"Columns: {attencarry_df.columns.tolist()}")

def update_attencarry(original_df, clues_data, output_name):
    """Update AttenCarry.csv with PstreamCarry and PresCarry values"""
    updated_df = original_df.copy()

    # Determine reach column name
    if 'nzsegment' in updated_df.columns:
        reach_col = 'nzsegment'
    elif 'NZSEGMENT' in updated_df.columns:
        reach_col = 'NZSEGMENT'
    else:
        reach_col = updated_df.columns[0]

    print(f"\n  Updating {output_name}...")
    print(f"  Reach column: {reach_col}")

    # Map the data
    for idx, row in updated_df.iterrows():
        reach_id = row[reach_col]
        clues_row = clues_data[clues_data['nzsegment'] == reach_id]
        if not clues_row.empty:
            # Update PstreamCarry and PresCarry columns
            if 'PstreamCarry' in updated_df.columns:
                updated_df.at[idx, 'PstreamCarry'] = clues_row['PstreamCarry'].values[0]
            if 'PresCarry' in updated_df.columns:
                updated_df.at[idx, 'PresCarry'] = clues_row['PresCarry'].values[0]

    # Save
    output_file = os.path.join(model_dir, 'InputData', f'AttenCarry_{output_name}.csv')
    updated_df.to_csv(output_file, index=False)
    print(f"  Created: {output_file}")
    return updated_df

baseline_attencarry = update_attencarry(attencarry_df, baseline_data, 'baseline')
wetland_attencarry = update_attencarry(attencarry_df, wetland_data, 'wetland_066m')

print("\n" + "="*60)
print("DATA PREPARATION COMPLETE!")
print("="*60)
print("\nFiles created:")
print(f"  1. {output_selection_file}")
print(f"  2. {os.path.join(model_dir, 'InputData', 'CLUESloads_baseline.csv')}")
print(f"  3. {os.path.join(model_dir, 'InputData', 'CLUESloads_wetland_066m.csv')}")
print(f"  4. {os.path.join(model_dir, 'InputData', 'AttenCarry_baseline.csv')}")
print(f"  5. {os.path.join(model_dir, 'InputData', 'AttenCarry_wetland_066m.csv')}")
