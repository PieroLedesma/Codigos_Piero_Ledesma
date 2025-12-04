# =====================================================================
# data_reader_3G.py - Lectura de datos WSH y RND para 3G WCDMA
# =====================================================================

import pandas as pd
from typing import Dict, Any, Tuple, Optional
import numpy as np

# =====================================================================
# FUNCIÓN: Lectura WSH para 3G (INTACTA)
# =====================================================================

def leer_datos_wsh_3g(wsh_file: Any, nemonico: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Lee el archivo WSHReport hoja '2G-3G' y extrae los datos necesarios para 3G WCDMA.
    """
    try:
        # Leer todas las hojas para encontrar la correcta
        xls = pd.ExcelFile(wsh_file, engine='openpyxl')
        sheet_name_3g = None
        
        # Buscar hoja que se llame '2G-3G' o similar
        for sheet in xls.sheet_names:
            if sheet.strip().upper() == '2G-3G':
                sheet_name_3g = sheet
                break
        
        if not sheet_name_3g:
            # Intento secundario: buscar si contiene '3G'
            for sheet in xls.sheet_names:
                if '3G' in sheet.upper():
                    sheet_name_3g = sheet
                    break
        
        if not sheet_name_3g:
            # Check if it looks like an RND file
            if 'Node' in xls.sheet_names or 'RfPort' in xls.sheet_names:
                return None, f"Error: El archivo cargado parece ser el RND. Por favor carga el archivo WSHReport en el campo correcto."
            return None, f"Error: No se encontró la hoja '2G-3G' en el archivo WSH. Hojas disponibles: {xls.sheet_names}"

        # Leer la hoja encontrada
        df_wsh = pd.read_excel(wsh_file, sheet_name=sheet_name_3g, engine='openpyxl')
        df_wsh.columns = df_wsh.columns.astype(str).str.strip()
        
        # Buscar la primera fila donde el nemónico (primera columna) contenga el nemonico buscado
        fila = None
        for _, row in df_wsh.iterrows():
            # Buscar en la primera columna (Nemonico)
            if isinstance(row.iloc[0], str) and nemonico.upper() in row.iloc[0].strip().upper():
                fila = row
                break
        
        if fila is None:
            return None, f"Error: No se encontró el nemónico '{nemonico}' en la hoja '2G-3G' del archivo WSH."
        
        # Extraer datos relevantes para 3G WCDMA
        
        # Leer IPs sin máscara
        ip_trafico = str(fila.iloc[12]).strip() if len(fila) > 12 and pd.notna(fila.iloc[12]) else '0.0.0.0'
        ip_oam = str(fila.iloc[17]).strip() if len(fila) > 17 and pd.notna(fila.iloc[17]) else '0.0.0.0'
        
        # Leer máscaras
        mask_trafico = str(int(fila.iloc[15])) if len(fila) > 15 and pd.notna(fila.iloc[15]) and str(fila.iloc[15]).replace('.0','').isdigit() else '26'
        mask_oam = str(int(fila.iloc[19])) if len(fila) > 19 and pd.notna(fila.iloc[19]) and str(fila.iloc[19]).replace('.0','').isdigit() else '26'
        
        wsh_data = {
            'NEMONICO': nemonico.upper(),
            'IP_OAM': ip_oam,
            'IP_TRAFICO': ip_trafico,
            'MASK_OAM': mask_oam,
            'MASK_TRAFICO': mask_trafico,
            'GATEWAY_TRAFICO': str(fila.iloc[14]).strip() if len(fila) > 14 and pd.notna(fila.iloc[14]) else '0.0.0.0',
            'GATEWAY_OAM': str(fila.iloc[18]).strip() if len(fila) > 18 and pd.notna(fila.iloc[18]) else '0.0.0.0',
            'VLAN_TRAFICO': str(int(fila.iloc[11])) if len(fila) > 11 and pd.notna(fila.iloc[11]) and str(fila.iloc[11]).replace('.0','').isdigit() else '1300',
            'VLAN_OAM': str(int(fila.iloc[16])) if len(fila) > 16 and pd.notna(fila.iloc[16]) and str(fila.iloc[16]).replace('.0','').isdigit() else '1301',
            'DNS': '10.170.15.20',
            'NTP1': '172.16.50.41',
            # Aquí termina la información del archivo WSH
        }
        
        return wsh_data, None

    except FileNotFoundError:
        return None, "Error: Archivo WSH no encontrado."
    except Exception as e:
        return None, f"Error inesperado durante la lectura del WSH: {e}"


# =====================================================================
# FUNCIÓN: Lectura RND para 3G (MODIFICADA)
# =====================================================================

def leer_rnd_sheets_3g(rnd_file: Any) -> Tuple[Optional[Dict[str, pd.DataFrame]], str]:
    """
    Lee las hojas necesarias del RND para 3G.
    Se ha eliminado la obligatoriedad estricta de la hoja 'Node'.
    Se prioriza 'RfPort'.
    """
    rnd_data: Dict[str, pd.DataFrame] = {}
    
    try:
        xls = pd.ExcelFile(rnd_file, engine='openpyxl')
    except Exception as e:
        return None, f"Error al abrir el archivo RND: {e}"

    # Mapa de nombres reales de las hojas (Normalizado: MAYUSCULAS y sin espacios)
    # Esto permite encontrar 'RfPort ' o 'rfport' sin errores.
    sheet_map = {name.strip().upper(): name for name in xls.sheet_names}
    
    # 1. Lectura de RfPort (CRITICA PARA TU SCRIPT DE SECTOR)
    if 'RFPORT' in sheet_map:
        try:
            real_name = sheet_map['RFPORT']
            # header=0 es estándar para RfPort (tiene nombres de columna en fila 1)
            df = xls.parse(real_name, header=0, dtype=str)
            df.columns = df.columns.str.strip() # Limpiar espacios en nombres de columna
            rnd_data['RfPort'] = df
        except Exception as e:
            return None, f"Error al leer hoja RfPort: {e}"
    else:
        # Si no está RfPort, avisamos, pero no retornamos None si queremos probar otras cosas
        # (Aunque para tu script Sector es obligatorio)
        print("ADVERTENCIA: No se encontró la hoja 'RfPort' en el RND.")

# 1.5. Lectura de RfBranch (Agregado para Sector_generator)
    if 'RFBRANCH' in sheet_map:
        try:
            real_name = sheet_map['RFBRANCH']
            df = xls.parse(real_name, header=0, dtype=str)
            
            # *** VERIFICACIÓN CLAVE: Asegurarse de que haya columnas ***
            if not df.empty and len(df.columns) > 0:
                # Si hay columnas, las limpiamos
                df.columns = df.columns.str.strip()
                rnd_data['RfBranch'] = df
            else:
                print("Advertencia: La hoja 'RfBranch' estaba vacía o no se pudo leer.")
            
        except Exception as e:
            # Capturar el error y no detener el flujo si no es esencial
            print(f"Error al leer hoja RfBranch: {e}")

    # 2. Lectura de Node (OPCIONAL AHORA)
    if 'NODE' in sheet_map:
        try:
            real_name = sheet_map['NODE']
            # La hoja Node suele tener estructura MO/Atributo/Valor tras un encabezado
            df = xls.parse(real_name, header=2, dtype=str)
            df.columns = df.columns.str.strip()
            
            if len(df.columns) >= 3:
                df.rename(columns={df.columns[0]: 'MO', df.columns[1]: 'Atributo', df.columns[2]: 'Valor'}, inplace=True)
                df.dropna(subset=['MO', 'Atributo'], how='all', inplace=True)
                df['MO'] = df['MO'].ffill()
                rnd_data['Node'] = df[['MO', 'Atributo', 'Valor']].copy()
        except Exception as e:
            print(f"Advertencia: Error leyendo hoja Node (se omitirá): {e}")
    else:
        # Ya no retornamos error si falta Node
        print("Aviso: Hoja 'Node' no presente en el RND. Se continuará sin ella.")

    # 3. Lectura de Otras Hojas Útiles (Generico)
    # Agregamos 'SiteConfiguration' o 'Equipment-Configuration' si existen
    other_sheets = ['SITECONFIGURATION', 'EQUIPMENT-CONFIGURATION', 'UTRANCELL', 'NODEBSECTORCARRIER']
    
    for sh_key in other_sheets:
        if sh_key in sheet_map:
            try:
                real_name = sheet_map[sh_key]
                # Leemos con header=0 por defecto para tablas normales
                df = xls.parse(real_name, header=0, dtype=str)
                df.columns = df.columns.str.strip()
                # Guardamos con un nombre amigable (Title Case)
                friendly_name = sh_key.title().replace('-', '') # Ej: SiteConfiguration
                rnd_data[friendly_name] = df
                rnd_data[sh_key] = df # Guardamos también con la llave original por si acaso
            except Exception:
                pass

    # Verificación Final
    # Si logramos leer ALGO, retornamos éxito.
    if rnd_data:
        # Aseguramos que 'RfPort' esté disponible bajo esa clave exacta para Sector_generator
        if 'RfPort' not in rnd_data and 'RFPORT' in sheet_map:
             # Fallback por si acaso
             pass 
             
        return rnd_data, None
    else:
        return None, "No se pudieron leer datos válidos del archivo RND (Verifique que contenga RfPort o SiteConfiguration)."