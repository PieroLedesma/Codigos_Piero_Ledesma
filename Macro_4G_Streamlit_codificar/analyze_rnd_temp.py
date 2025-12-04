import pandas as pd
import json

excel_path = r'LA781 - TEKNICA\LA781 - TEKNICA\RND_ULA781_WCDMA1900_900_20251104-141953.xlsx'

# Cargar el archivo Excel
xl = pd.ExcelFile(excel_path)

print("=" * 80)
print("ANÁLISIS DEL ARCHIVO RND 3G - WCDMA")
print("=" * 80)

# Resumen general
summary = {}
for sheet in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet)
    summary[sheet] = {
        'filas': len(df),
        'columnas': len(df.columns),
        'nombres_columnas': list(df.columns)
    }

# Mostrar resumen de todas las hojas
print("\n### RESUMEN DE TODAS LAS HOJAS ###\n")
for sheet_name, info in summary.items():
    print(f"{sheet_name:30s} - Filas: {info['filas']:5d} | Columnas: {info['columnas']:3d}")

# Analizar hojas principales en detalle
print("\n" + "=" * 80)
print("DETALLES DE HOJAS PRINCIPALES")
print("=" * 80)

# UtranCell
print("\n### HOJA: UtranCell (Celdas 3G) ###")
df_utran = pd.read_excel(xl, sheet_name='UtranCell')
print(f"Total de celdas: {len(df_utran)}")
print(f"Columnas ({len(df_utran.columns)}): {', '.join(list(df_utran.columns)[:10])}...")
if len(df_utran) > 0:
    print("\nPrimera celda:")
    print(df_utran[['RNC', 'Site', 'UtranCell', 'cId', 'lac', 'primaryScramblingCode']].head(1).to_string(index=False))

# NodeBFunction
print("\n### HOJA: NodeBFunction (Parámetros del NodeB) ###")
df_nodeb = pd.read_excel(xl, sheet_name='NodeBFunction')
print(f"Total de registros: {len(df_nodeb)}")
print(f"Columnas: {', '.join(list(df_nodeb.columns))}")

# UtranRelation
print("\n### HOJA: UtranRelation (Relaciones entre celdas 3G) ###")
df_utranrel = pd.read_excel(xl, sheet_name='UtranRelation')
print(f"Total de relaciones: {len(df_utranrel)}")
print(f"Columnas: {', '.join(list(df_utranrel.columns))}")
if len(df_utranrel) > 0:
    print("\nPrimeras 3 relaciones:")
    print(df_utranrel.head(3).to_string(index=False))

# GSMRelation
print("\n### HOJA: GSMRelation___All_RNC (Relaciones 3G->2G) ###")
df_gsmrel = pd.read_excel(xl, sheet_name='GSMRelation___All_RNC')
print(f"Total de relaciones: {len(df_gsmrel)}")
print(f"Columnas: {', '.join(list(df_gsmrel.columns))}")

# EutranCellRelation
print("\n### HOJA: EutranCellRelation (Relaciones 3G->4G) ###")
df_eutranrel = pd.read_excel(xl, sheet_name='EutranCellRelation')
print(f"Total de relaciones: {len(df_eutranrel)}")
print(f"Columnas: {', '.join(list(df_eutranrel.columns))}")

# IubDataStreams
print("\n### HOJA: IubDataStreams (Transmisión Iub) ###")
df_iub = pd.read_excel(xl, sheet_name='IubDataStreams')
print(f"Total de registros: {len(df_iub)}")
print(f"Columnas: {', '.join(list(df_iub.columns))}")

# AntennaUnit
print("\n### HOJA: AntennaUnit (Configuración de Antenas) ###")
df_antenna = pd.read_excel(xl, sheet_name='AntennaUnit')
print(f"Total de antenas: {len(df_antenna)}")
print(f"Columnas: {', '.join(list(df_antenna.columns))}")

print("\n" + "=" * 80)
print("FIN DEL ANÁLISIS")
print("=" * 80)
