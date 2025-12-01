import pandas as pd

df = pd.read_excel(r'GFG222_script_REMOTOS\RND_GFG222_LTE2600_1900.xlsx', sheet_name='Equipment-Configuration', header=None)
rows = df[df[0].astype(str).str.contains('ExternalGUtranCell', na=False)]

print("ExternalGUtranCell rows:")
for idx, row in rows.iterrows():
    print(f"\nRow {idx}:")
    print(f"  Col 0: {row[0]}")
    print(f"  Col 1: {row[1]}")
    print(f"  Col 2: {row[2]}")
    print(f"  Col 3: {row[3]}")
