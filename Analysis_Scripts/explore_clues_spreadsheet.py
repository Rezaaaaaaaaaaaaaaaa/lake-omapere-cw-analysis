"""
Script to explore the structure of CLUES XLSB spreadsheets
and extract reach information and required data
"""

from pyxlsb import open_workbook
import pandas as pd

# Open the baseline spreadsheet
baseline_file = r'C:\Users\moghaddamr\Reza_CW_Analysis\TP_noMit_LakeOnly_baseline.xlsb'

print("Opening baseline spreadsheet...")
with open_workbook(baseline_file) as wb:
    # Get sheet names
    sheet_names = wb.sheets
    print(f"\nSheet names in workbook:")
    for sheet in sheet_names:
        print(f"  - {sheet}")

    # Try to read the main data sheet (likely first sheet or one with data)
    # Let's try a few common sheet names
    for sheet_name in sheet_names[:5]:  # Check first 5 sheets
        print(f"\n\nExploring sheet: {sheet_name}")
        try:
            with wb.get_sheet(sheet_name) as sheet:
                # Read first few rows to understand structure
                rows = []
                for i, row in enumerate(sheet.rows()):
                    if i > 10:  # Only read first 10 rows for exploration
                        break
                    row_data = [item.v if item else None for item in row]
                    rows.append(row_data)

                if rows:
                    df = pd.DataFrame(rows)
                    print(f"First 10 rows of sheet '{sheet_name}':")
                    print(df.head(10))
                    print(f"\nShape: {df.shape}")
        except Exception as e:
            print(f"Error reading sheet {sheet_name}: {e}")
