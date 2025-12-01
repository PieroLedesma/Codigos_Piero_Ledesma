import pandas as pd

excel_path = r"c:\Users\pledesma\Documents\Piero Ledesma\Piero Ledesma\Nuevas Macros\Macro_4G_Streamlit_codificar\GFG222_script_REMOTOS\RND_GFG222_LTE2600_1900.xlsx"

def inspect_mo_data(mo_name):
    print(f"\n--- Inspecting {mo_name} ---")
    try:
        excel = pd.read_excel(excel_path, sheet_name=None, header=None, engine="openpyxl")
        for sheet, df in excel.items():
            df[0] = df[0].astype(str).str.strip()
            matches = df[df[0].str.contains(mo_name, case=False, na=False)]
            if not matches.empty:
                print(f"Found in sheet: {sheet}")
                # Print all rows found
                print(matches.iloc[:, :5].to_string())
    except Exception as e:
        print(f"Error: {e}")

inspect_mo_data("ExternalGNodeBFunction")
