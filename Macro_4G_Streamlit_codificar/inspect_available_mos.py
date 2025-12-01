import pandas as pd
import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from Macro.functions.data_reader import _read_node_all_mos, _read_equipment_profiles

def inspect_mos():
    rnd_file = r"c:\Users\pledesma\Documents\Piero Ledesma\Piero Ledesma\Nuevas Macros\Macro_4G_Streamlit_codificar\GFG222_script_REMOTOS\RND_GFG222_LTE2600_1900.xlsx"
    
    print(f"Inspecting {rnd_file}...\n")
    
    # Check Node sheet
    try:
        node_mos = _read_node_all_mos(rnd_file)
        print("--- MOs found in 'Node' sheet ---")
        for mo in sorted(node_mos.keys()):
            print(f"- {mo} ({len(node_mos[mo])} attributes)")
            # Print a few keys to see what they look like
            keys = list(node_mos[mo].keys())[:5]
            print(f"  Sample keys: {keys}")
    except Exception as e:
        print(f"Error reading Node sheet: {e}")

    print("\n")

    # Check Equipment sheet
    try:
        drx, qci = _read_equipment_profiles(rnd_file)
        print(f"--- Equipment Profiles ---")
        print(f"DrxProfiles found: {len(drx)}")
        print(f"QciProfiles found: {len(qci)}")
    except Exception as e:
        print(f"Error reading Equipment sheet: {e}")

if __name__ == "__main__":
    inspect_mos()
