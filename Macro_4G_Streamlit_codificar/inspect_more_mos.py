import pandas as pd
import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

def inspect_more_mos():
    rnd_file = r"c:\Users\pledesma\Documents\Piero Ledesma\Piero Ledesma\Nuevas Macros\Macro_4G_Streamlit_codificar\GFG222_script_REMOTOS\RND_GFG222_LTE2600_1900.xlsx"
    
    print(f"Inspecting {rnd_file}...\n")
    
    try:
        df = pd.read_excel(rnd_file, sheet_name='Cell-Carrier', engine='openpyxl')
        
        mos_to_check = ["MimoSleepFunction", "ReportConfig", "UeMeasControl", "SectorCarrier"]
        
        for mo in mos_to_check:
            print(f"\n--- Searching for '{mo}' in MO column ---")
            found = df[df.iloc[:, 0].astype(str).str.contains(mo, case=False, na=False)]
            if not found.empty:
                print(f"Found {len(found)} entries. Sample:")
                print(found.iloc[:, :2].head())
            else:
                print(f"{mo} NOT found.")
            
    except Exception as e:
        print(f"Error reading Cell-Carrier sheet: {e}")

if __name__ == "__main__":
    inspect_more_mos()
