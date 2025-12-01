import pandas as pd

file_path = r"c:\Users\pledesma\Documents\Piero Ledesma\Piero Ledesma\Nuevas Macros\Macro_4G_Streamlit_codificar\GFG222_script_REMOTOS\RND_GFG222_LTE2600_1900.xlsx"

try:
    xls = pd.ExcelFile(file_path, engine='openpyxl')
    
    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet, header=None)
        
        # Check gNodeBPlmnId
        mask = df[1].astype(str).str.contains('gNodeBPlmnId', case=False, na=False)
        if mask.any():
            print(f"\n--- Found gNodeBPlmnId in {sheet} ---")
            print(df[mask].head(5).to_string())
            
        # Check allowedPlmnList
        mask2 = df[1].astype(str).str.contains('allowedPlmnList', case=False, na=False)
        if mask2.any():
            print(f"\n--- Found allowedPlmnList in {sheet} ---")
            print(df[mask2].head(5).to_string())

except Exception as e:
    print(f"Error: {e}")
