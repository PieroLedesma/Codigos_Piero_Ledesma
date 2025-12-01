import pandas as pd
import sys

file_path = r"c:\Users\pledesma\Documents\Piero Ledesma\Piero Ledesma\Nuevas Macros\Macro_4G_Streamlit_codificar\GFG222_script_REMOTOS\RND_GFG222_LTE2600_1900.xlsx"

try:
    xls = pd.ExcelFile(file_path, engine='openpyxl')
    print(f"Sheet names: {xls.sheet_names}")
    
    # Inspect Node sheet
    if 'Node' in xls.sheet_names:
        print("\n--- Sheet: Node ---")
        df = pd.read_excel(xls, sheet_name='Node', header=None)
        print(df.to_string())

    # Inspect other relevant sheets
    target_sheets = ['GUtranRelation', 'ExternalGNodeBFunction', 'TermPointToGNB', 'ExternalGUtranCell', 'GUtranSyncSignalFrequency', 'GUtranFreqRelation']
    
    for sheet in xls.sheet_names:
        if sheet in target_sheets or any(x in sheet for x in ['GUtran', 'External']):
            print(f"\n--- Sheet: {sheet} ---")
            df = pd.read_excel(xls, sheet_name=sheet, header=None)
            # Print first 10 rows
            print(df.head(10).to_string())
            
            # Print rows where col 0 contains 'GUtran' or 'External'
            print(f"\n--- Sample Data in {sheet} ---")
            mask = df[0].astype(str).str.contains('GUtran|External', case=False, na=False)
            if not mask.any():
                 mask = df[1].astype(str).str.contains('GUtran|External', case=False, na=False)
            
            if mask.any():
                print(df[mask].head(5).to_string())
            else:
                print("No MO found in first columns")

except Exception as e:
    print(f"Error reading excel: {e}")
