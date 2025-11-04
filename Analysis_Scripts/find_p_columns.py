"""
Find P (phosphorus) related columns in the CLUES spreadsheet
"""

from pyxlsb import open_workbook
import pandas as pd

baseline_file = r'C:\Users\moghaddamr\Reza_CW_Analysis\TP_noMit_LakeOnly_baseline.xlsb'

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

# Read the Reaches sheet
reaches_df = read_xlsb_sheet(baseline_file, 'Reaches')

print("Searching for columns with 'P', 'Sed', 'phosph', or 'OVERSEER':")
print()

for i, col in enumerate(reaches_df.columns):
    if col and (
        'P' in str(col).upper() or
        'SED' in str(col).upper() or
        'PHOSPH' in str(col).upper() or
        'OVERSEER' in str(col).upper() or
        'LOAD' in str(col).upper() or
        'CARRY' in str(col).upper()
    ):
        # Convert index to Excel column letter
        if i < 26:
            col_letter = chr(65 + i)
        elif i < 702:
            col_letter = chr(65 + i // 26 - 1) + chr(65 + i % 26)
        else:
            col_letter = f"Col{i}"
        print(f"  {col_letter} (col {i}): {col}")

print("\n\nLooking at a few data rows for key columns:")
print("\nColumns around column T (19) - should be P_Sed:")
for i in range(17, 22):
    if i < len(reaches_df.columns):
        col = reaches_df.columns[i]
        if i < 26:
            col_letter = chr(65 + i)
        else:
            col_letter = chr(65 + i // 26 - 1) + chr(65 + i % 26)
        print(f"  {col_letter} (col {i}): {col}")

print("\nColumns around column AF (31) - should be OVERSEER Load:")
for i in range(29, 34):
    if i < len(reaches_df.columns):
        col = reaches_df.columns[i]
        if i < 26:
            col_letter = chr(65 + i)
        else:
            col_letter = chr(65 + i // 26 - 1) + chr(65 + i % 26)
        print(f"  {col_letter} (col {i}): {col}")

# Show some sample data for Lake Omapere reaches
lomapere_reaches = [1009647.0, 1009665.0, 1009698.0]
print("\n\nSample data for first 3 Lake Omapere reaches:")
for reach in lomapere_reaches:
    row = reaches_df[reaches_df['nzsegment'] == reach]
    if not row.empty:
        print(f"\nReach {int(reach)}:")
        # Column T (19), AF (31), BC (54), BD (55), BF (57)
        cols_to_show = [19, 31, 54, 55, 57]
        for col_idx in cols_to_show:
            col_name = reaches_df.columns[col_idx]
            value = row.iloc[0, col_idx]
            if col_idx < 26:
                col_letter = chr(65 + col_idx)
            else:
                col_letter = chr(65 + col_idx // 26 - 1) + chr(65 + col_idx % 26)
            print(f"  {col_letter} ({col_name}): {value}")
