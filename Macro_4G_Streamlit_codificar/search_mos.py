import pandas as pd

file_path = r"c:\Users\pledesma\Documents\Piero Ledesma\Piero Ledesma\Nuevas Macros\Macro_4G_Streamlit_codificar\GFG222_script_REMOTOS\RND_GFG222_LTE2600_1900.xlsx"

try:
    xls = pd.ExcelFile(file_path, engine='openpyxl')
    print(f"Sheet names: {xls.sheet_names}")
    
    for sheet in xls.sheet_names:
        print(f"\n--- Sheet: {sheet} ---")
        df = pd.read_excel(xls, sheet_name=sheet, header=None)
        
        # Search for 'GUtran' in the first column
        mask = df[0].astype(str).str.contains('GUtran', case=False, na=False)
        if mask.any():
            print(f"FOUND GUtran in {sheet}!")
            print(df[mask].head(10).to_string())
        else:
            print(f"No GUtran found in {sheet} col 0")
            
        # Search for 'External' in the first column
        mask_ext = df[0].astype(str).str.contains('External', case=False, na=False)
        if mask_ext.any():
            print(f"FOUND External in {sheet}!")
            print(df[mask_ext].head(10).to_string())

except Exception as e:
    print(f"Error: {e}")
