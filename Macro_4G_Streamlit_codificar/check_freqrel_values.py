import pandas as pd
import sys

rnd_file = r"c:\Users\pledesma\Documents\Piero Ledesma\Piero Ledesma\Nuevas Macros\Macro_4G_Streamlit_codificar\GFG222_script_REMOTOS\RND_GFG222_LTE2600_1900.xlsx"

try:
    excel = pd.read_excel(rnd_file, sheet_name=None, header=None, engine="openpyxl")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

for sheet, df in excel.items():
    for _, row in df.iterrows():
        if pd.isna(row[0]): continue
        mo = str(row[0]).strip()
        if "GUtranFreqRelation" in mo:
            attr = str(row[1]).strip()
            if "cellReselectionPriority" in attr:
                print(f"Found cellReselectionPriority in sheet {sheet}:")
                print(row.values)
