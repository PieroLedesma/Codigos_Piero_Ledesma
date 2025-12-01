import os
import sys

# Add the current directory to sys.path to allow importing modules from Macro
sys.path.append(os.getcwd())

from Macro.functions.parametros_generator import generate_parametros_mos

def test_generation():
    rnd_file = r"c:\Users\pledesma\Documents\Piero Ledesma\Piero Ledesma\Nuevas Macros\Macro_4G_Streamlit_codificar\GFG222_script_REMOTOS\RND_GFG222_LTE2600_1900.xlsx"
    nemonico = "GFG222"
    
    print(f"Generating parameters for {nemonico} using {rnd_file}...")
    
    try:
        content = generate_parametros_mos(nemonico, rnd_file)
        
        output_file = "Macro/05_GFG222_Parametros.mos"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"Successfully generated {output_file}")
        print(f"File size: {len(content)} bytes")
        
    except Exception as e:
        print(f"Error generating parameters: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generation()
