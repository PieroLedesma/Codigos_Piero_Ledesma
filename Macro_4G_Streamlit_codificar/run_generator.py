import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Macro'))
from functions.Gutran_relation_generator import generate_gutran_relation_mos

excel_path = r"c:\Users\pledesma\Documents\Piero Ledesma\Piero Ledesma\Nuevas Macros\Macro_4G_Streamlit_codificar\GFG222_script_REMOTOS\RND_GFG222_LTE2600_1900.xlsx"
output_path = "generated_output.mos"

try:
    content = generate_gutran_relation_mos(excel_path, "GFG222", "R1")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully generated {output_path}")
except Exception as e:
    print(f"Error: {e}")
