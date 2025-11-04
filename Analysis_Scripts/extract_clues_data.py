"""
Script to extract reach list and required data from CLUES spreadsheets
"""

from pyxlsb import open_workbook
import pandas as pd

baseline_file = r'C:\Users\moghaddamr\Reza_CW_Analysis\TP_noMit_LakeOnly_baseline.xlsb'
wetland_file = r'C:\Users\moghaddamr\Reza_CW_Analysis\TP_noMit_LakeOnly+0.66m.xlsb'

def read_xlsb_sheet(filename, sheet_name):
    """Read a sheet from an XLSB file into a pandas DataFrame"""
    with open_workbook(filename) as wb:
        with wb.get_sheet(sheet_name) as sheet:
            rows = []
            for row in sheet.rows():
                row_data = [item.v if item else None for item in row]
                rows.append(row_data)

    # First row is header
    df = pd.DataFrame(rows[1:], columns=rows[0])
    return df

# Read LOmapereReaches sheet to get the list of 50 reaches
print("Reading Lake Omapere reach list...")
lomapere_reaches_df = read_xlsb_sheet(baseline_file, 'LOmapereReaches')
print(f"\nLOmapereReaches sheet shape: {lomapere_reaches_df.shape}")
print(f"First few rows:")
print(lomapere_reaches_df.head(10))
print(f"\nAll columns: {lomapere_reaches_df.columns.tolist()}")

# Save the reach list
reach_list = lomapere_reaches_df['nzsegment'].dropna().tolist()
print(f"\nNumber of Lake Omapere reaches: {len(reach_list)}")
print(f"Reach IDs: {reach_list}")

# Read the Reaches sheet to get column headers
print("\n\nReading Reaches sheet...")
reaches_df = read_xlsb_sheet(baseline_file, 'Reaches')
print(f"\nReaches sheet shape: {reaches_df.shape}")
print(f"\nColumn headers:")
for i, col in enumerate(reaches_df.columns):
    # Convert Excel column number to letter
    if i < 26:
        col_letter = chr(65 + i)
    elif i < 702:  # AA to ZZ
        col_letter = chr(65 + i // 26 - 1) + chr(65 + i % 26)
    else:
        col_letter = f"Col{i}"
    print(f"  {col_letter} (col {i}): {col}")

# Find the columns we need:
# Column T (19): P_Sed -> soilP
# Column AF (31): OVERSEER Load (t/y) -> TPAgGen
# Column BC (54): LoadIncrement -> for calculating TPGen
# Column BD (55): PstreamCarry
# Column BF (57): PresCarry

print("\n\nLooking for required columns...")
column_mapping = {
    'T': 19,   # P_Sed
    'AF': 31,  # OVERSEER Load
    'BC': 54,  # LoadIncrement
    'BD': 55,  # PstreamCarry
    'BF': 57   # PresCarry
}

for col_letter, col_idx in column_mapping.items():
    if col_idx < len(reaches_df.columns):
        print(f"Column {col_letter} (index {col_idx}): {reaches_df.columns[col_idx]}")
    else:
        print(f"Column {col_letter} (index {col_idx}): Index out of range")
