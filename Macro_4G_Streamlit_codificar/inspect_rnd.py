import pandas as pd
import os

file_path = r"c:\Users\pledesma\Documents\Piero Ledesma\Piero Ledesma\Nuevas Macros\Macro_4G_Streamlit_codificar\LA781 - TEKNICA\LA781 - TEKNICA\RND_ULA781_WCDMA1900_900_20251104-141953.xlsx"

print(f"Inspecting file: {file_path}")

try:
    xls = pd.ExcelFile(file_path, engine='openpyxl')
    print("Sheet names found:")
    for sheet in xls.sheet_names:
        print(f" - {sheet}")

    target_sheet = None
    for sheet in xls.sheet_names:
        if sheet.strip().upper() == 'RFBRANCH':
            target_sheet = sheet
            break
    
    if target_sheet:
        print(f"\nReading sheet: {target_sheet}")
        df = pd.read_excel(file_path, sheet_name=target_sheet, engine='openpyxl', nrows=5)
        print("Columns found:")
        print(df.columns.tolist())
        print("\nFirst 5 rows:")
        print(df)
    else:
        print("\nSheet 'RfBranch' NOT found.")

except Exception as e:
    print(f"Error reading file: {e}")
