import pandas as pd

file_path = r"c:\Users\pledesma\Documents\Piero Ledesma\Piero Ledesma\Nuevas Macros\Macro_4G_Streamlit_codificar\GFG222_script_REMOTOS\RND_GFG222_LTE2600_1900.xlsx"

target_sheets = [
    'GUtranSyncSignalFrequency', 
    'GUtranFreqRelation', 
    'ExternalGNodeBFunction', 
    'TermPointToGNB', 
    'ExternalGUtranCell', 
    'GUtranCellRelation'
]

try:
    xls = pd.ExcelFile(file_path, engine='openpyxl')
    print(f"All Sheet names: {xls.sheet_names}")
    
    for sheet in target_sheets:
        if sheet in xls.sheet_names:
            print(f"\n--- Sheet: {sheet} ---")
            df = pd.read_excel(xls, sheet_name=sheet, header=None, nrows=10)
            print(df.to_string())
        else:
            print(f"\n--- Sheet {sheet} NOT FOUND ---")
            # Try to find it by partial match
            matches = [s for s in xls.sheet_names if sheet.lower() in s.lower()]
            if matches:
                print(f"Found similar sheets: {matches}")
                for m in matches:
                    print(f"--- Content of {m} ---")
                    df = pd.read_excel(xls, sheet_name=m, header=None, nrows=10)
                    print(df.to_string())

except Exception as e:
    print(f"Error: {e}")
