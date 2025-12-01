import pandas as pd
import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

def inspect_cell_carrier_columns():
    rnd_file = r"c:\Users\pledesma\Documents\Piero Ledesma\Piero Ledesma\Nuevas Macros\Macro_4G_Streamlit_codificar\GFG222_script_REMOTOS\RND_GFG222_LTE2600_1900.xlsx"
    
    print(f"Inspecting {rnd_file}...\n")
    
    try:
        df = pd.read_excel(rnd_file, sheet_name='Cell-Carrier', engine='openpyxl')
        print("--- Columns in 'Cell-Carrier' ---")
        print(df.columns.tolist())
        
        print("\n--- First 20 rows of 'Cell-Carrier' (MO and Attribute columns) ---")
        # Assuming first few columns are MO and Attribute. 
        # Based on previous knowledge, col 0 is MO, col 1 is Attribute.
        print(df.iloc[:20, :2])
        
        print("\n--- Searching for 'NbIotCell' in MO column ---")
        nb_iot = df[df.iloc[:, 0].astype(str).str.contains("NbIotCell", case=False, na=False)]
        if not nb_iot.empty:
            print("Found NbIotCell entries:")
            print(nb_iot.iloc[:, :2])
        else:
            print("NbIotCell NOT found in MO column.")

        print("\n--- Searching for 'CellSleepFunction' in MO column ---")
        sleep = df[df.iloc[:, 0].astype(str).str.contains("CellSleepFunction", case=False, na=False)]
        if not sleep.empty:
            print("Found CellSleepFunction entries:")
            print(sleep.iloc[:, :2].head())
        else:
            print("CellSleepFunction NOT found in MO column.")
            
    except Exception as e:
        print(f"Error reading Cell-Carrier sheet: {e}")

if __name__ == "__main__":
    inspect_cell_carrier_columns()
