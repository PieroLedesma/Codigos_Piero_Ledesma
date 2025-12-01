# =====================================================================
# data_reader_5G.py - Lectura de datos WSH y RND para 5G NR (CORREGIDO)
# =====================================================================

import pandas as pd
from typing import Dict, Any, Tuple, Optional
import numpy as np # Necesario para pd.notna

# =====================================================================
# FUNCIÓN DE UTILIDAD: Lectura WSH
# =====================================================================

def leer_datos_wsh_5g(wsh_file: Any, nemonico: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Lee el archivo WSHReport hoja '5G' y extrae los datos necesarios para 5G NR.
    Busca la primera fila donde el nemónico empiece con 'N'.
    """
    try:
        # Leer todas las hojas para encontrar la correcta
        xls = pd.ExcelFile(wsh_file, engine='openpyxl')
        sheet_name_5g = None
        
        # Buscar hoja que se llame '5G' o similar
        for sheet in xls.sheet_names:
            if sheet.strip().upper() == '5G':
                sheet_name_5g = sheet
                break
        
        if not sheet_name_5g:
             # Intento secundario: buscar si contiene '5G'
             for sheet in xls.sheet_names:
                 if '5G' in sheet.upper():
                     sheet_name_5g = sheet
                     break
        
        if not sheet_name_5g:
             # Check if it looks like an RND file
             if 'Node' in xls.sheet_names:
                 return None, f"Error: El archivo cargado parece ser el RND (contiene hoja 'Node'). Por favor carga el archivo WSHReport en el campo correcto (Campo 1)."
             return None, f"Error: No se encontró la hoja '5G' en el archivo WSH. Hojas disponibles: {xls.sheet_names}"

        # Leer la hoja encontrada
        df_wsh = pd.read_excel(wsh_file, sheet_name=sheet_name_5g, engine='openpyxl')
        df_wsh.columns = df_wsh.columns.astype(str).str.strip() # Limpiar columnas
        
        # Buscar la primera fila donde el nemónico (primera columna) empiece con 'N'
        fila = None
        for _, row in df_wsh.iterrows():
            # Buscar en la primera columna (Nemonico) si empieza con 'N'
            if isinstance(row.iloc[0], str) and row.iloc[0].strip().upper().startswith('N'):
                fila = row
                break
        
        if fila is None:
            return None, f"Error: No se encontró ningún nemónico que empiece con 'N' en la hoja 5G del archivo WSH."
        
        # Extraer datos relevantes para 5G
        # Las columnas se acceden por índice para ser robustos a cambios de nombre
        wsh_data = {
            'NEMONICO': nemonico.upper(),  # Usar el nemónico del formulario SIN 'N'
            # IPs y Gateways
            'IP_TRAFICO': str(fila.iloc[11]).strip() if len(fila) > 11 and pd.notna(fila.iloc[11]) else '0.0.0.0',
            'GATEWAY_TRAFICO': str(fila.iloc[12]).strip() if len(fila) > 12 and pd.notna(fila.iloc[12]) else '0.0.0.0',
            'IP_OAM': str(fila.iloc[15]).strip() if len(fila) > 15 and pd.notna(fila.iloc[15]) else '0.0.0.0',
            'GATEWAY_OAM': str(fila.iloc[16]).strip() if len(fila) > 16 and pd.notna(fila.iloc[16]) else '0.0.0.0',
            # VLANs
            # Intentar convertir a int y luego a str, con manejo de errores para NaN o string no numérico
            'VLAN_TRAFICO': str(int(fila.iloc[10])) if len(fila) > 10 and pd.notna(fila.iloc[10]) and str(fila.iloc[10]).isdigit() else '0',
            'VLAN_OAM': str(int(fila.iloc[14])) if len(fila) > 14 and pd.notna(fila.iloc[14]) and str(fila.iloc[14]).isdigit() else '0',
            # Trama - por defecto TN_IDL_B
            'TRAMA': 'TN_IDL_B',
            # DNS y NTP estáticos (no se leen del Excel)
            'DNS': '10.170.15.42',
            'NTP1': '172.16.50.41',
            'NTP2': '172.16.50.42',
        }
        
        return wsh_data, ""
        
    except Exception as e:
        return None, f"Error al leer hoja '5G' del archivo WSH: {str(e)}"

# =====================================================================
# FUNCIÓN CORREGIDA: Lectura RND Centralizada (HÍBRIDA)
# =====================================================================

def leer_rnd_sheets_5g(rnd_file: Any) -> Tuple[Optional[Dict[str, pd.DataFrame]], str]:
    """
    Lee las hojas necesarias del RND con diferentes estrategias:
    - 'Node': header=2 con columnas nombradas (para node_generator.py)
    - Otras hojas: header=None (para parse_rnd_sheet en NR_Relation_Parametros.py y carrier_cell_generator.py)
    """
    required_sheets = ['Node', 'Cell-Carrier', 'Equipment-Configuration', 'Features']
    rnd_data: Dict[str, pd.DataFrame] = {}
    
    try:
        xls = pd.ExcelFile(rnd_file, engine='openpyxl')
    except Exception as e:
        return None, f"Error al abrir el archivo RND. Asegúrese de que sea un archivo Excel válido. Error: {e}"

    for sheet_name in required_sheets:
        if sheet_name not in xls.sheet_names:
            if sheet_name == 'Node':
                return None, f"Error: La hoja crítica '{sheet_name}' no se encontró en el RND."
            continue 

        try:
            if sheet_name == 'Node':
                # HOJA NODE: Leer con header=2 y estandarizar columnas (para node_generator.py)
                df = xls.parse(sheet_name, header=2)
                df.columns = df.columns.astype(str).str.strip()
                df_cols = df.columns.tolist()
                
                if len(df_cols) < 3:
                    return None, f"La hoja '{sheet_name}' no tiene al menos 3 columnas para procesar."
                
                # Renombrar a nombres estándar
                mo_col_temp = df_cols[0]
                attr_col_temp = df_cols[1]
                value_col_temp = df_cols[2]
                
                df.rename(columns={mo_col_temp: 'MO', attr_col_temp: 'Atributo', value_col_temp: 'Valor'}, inplace=True)
                df.dropna(subset=['MO', 'Atributo'], how='all', inplace=True)
                df['MO'] = df['MO'].ffill()
                
                rnd_data[sheet_name] = df[['MO', 'Atributo', 'Valor']].copy()
                
            else:
                # HOJAS MULTI-INSTANCIA: Leer con header=None (para parse_rnd_sheet)
                df = xls.parse(sheet_name, header=None)
                
                if len(df.columns) < 3:
                    return None, f"La hoja '{sheet_name}' no tiene al menos 3 columnas para procesar."
                
                rnd_data[sheet_name] = df
            
        except Exception as e:
            return None, f"Error al leer la hoja '{sheet_name}' del RND. Error: {e}"

    # Verificación de que al menos las hojas críticas tienen contenido
    if 'Node' in rnd_data and not rnd_data['Node'].empty:
        return rnd_data, "Lectura RND exitosa."
    else:
        return None, "La hoja 'Node' del RND está vacía o no se pudo leer."