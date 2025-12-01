from Macro.functions.Gutran_relation_generator import parse_equipment_config_sheet
import pandas as pd

df = pd.read_excel(r'GFG222_script_REMOTOS\RND_GFG222_LTE2600_1900.xlsx', sheet_name='Equipment-Configuration')
data = parse_equipment_config_sheet(df)

if "ExternalGUtranCell" in data:
    print("ExternalGUtranCell keys:")
    for k in data["ExternalGUtranCell"].keys():
        print(f"  '{k}'")
        print(f"    Values: {data['ExternalGUtranCell'][k][:5]}")  # First 5 values
