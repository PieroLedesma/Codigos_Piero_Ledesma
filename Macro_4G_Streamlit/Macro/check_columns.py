import pandas as pd
import sys

file_path = r"c:\Users\pledesma\Documents\Piero Ledesma\Piero Ledesma\Nuevas Macros\Macro_4G_Streamlit_codificar\LA781 - TEKNICA\LA781 - TEKNICA\RND_ULA781_WCDMA1900_900_20251104-141953.xlsx"

try:
    # Try finding the sheet with case insensitivity logic if needed, but usually exact match first
    # Based on previous steps, the sheet might be named 'EutranFreqRelation'
    df = pd.read_excel(file_path, sheet_name='MscParameter')
    print("Columns in MscParameter:")
    for col in df.columns:
        print(f"'{col}'")
except Exception as e:
    print(f"Error: {e}")
