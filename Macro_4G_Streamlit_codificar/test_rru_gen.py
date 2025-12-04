import sys
import os
import pandas as pd

# Agregar paths para importar módulos
sys.path.insert(0, r'c:\Users\pledesma\Documents\Piero Ledesma\Piero Ledesma\Nuevas Macros\Macro_4G_Streamlit_codificar\Macro')

from functions_3G.data_reader_3G import leer_rnd_sheets_3g
from functions_3G.Sector_generator import generate_sector_mml

# Archivo RND real
RND_FILE = r'LA781 - TEKNICA\LA781 - TEKNICA\RND_ULA781_WCDMA1900_900_20251104-141953.xlsx'
FULL_RND_PATH = os.path.join(r'c:\Users\pledesma\Documents\Piero Ledesma\Piero Ledesma\Nuevas Macros\Macro_4G_Streamlit_codificar', RND_FILE)

print("=" * 80)
print("TEST: Generación Dinámica RRU - Sector 3G")
print("=" * 80)

# 1. Leer RND
print(f"\nLeyendo RND: {RND_FILE}...")
rnd_data, msg = leer_rnd_sheets_3g(FULL_RND_PATH)

if not rnd_data:
    print(f"[ERROR] Falló lectura RND: {msg}")
    sys.exit(1)

print(f"[OK] {msg}")
if 'RfPort' in rnd_data:
    print(f"  - Hoja RfPort encontrada: {len(rnd_data['RfPort'])} filas")
    print(f"  - Columnas: {list(rnd_data['RfPort'].columns)}")
else:
    print("  - [ERROR] Hoja RfPort NO encontrada en rnd_data")

# 2. Generar MML
print("\nGenerando MML de Sector...")
mml_content = generate_sector_mml("ULA781", rnd_data)

print("\n" + "=" * 80)
print("CONTENIDO GENERADO (SECCIÓN RRU)")
print("=" * 80)

# Filtrar solo la sección RRU para mostrar
lines = mml_content.split('\n')
in_rru_section = False
for line in lines:
    if "### HW - RRU" in line:
        in_rru_section = True
    
    if in_rru_section:
        print(line)
        if "sale de la hoja RfPort" in line:
            in_rru_section = False

print("\n" + "=" * 80)
print("TEST COMPLETADO")
print("=" * 80)
