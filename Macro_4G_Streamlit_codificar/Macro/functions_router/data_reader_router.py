import pandas as pd
import re
from typing import Dict, Tuple, Optional, Any

# =====================================================================
# 1. FUNCIÓN DE ANÁLISIS RÁPIDO (PARA LA UI)
# =====================================================================

def extract_router_info(atnd_file: Any) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Analiza el archivo ATND y extrae información clave del router.
    INCLUYE LIMPIEZA ROBUSTA PARA DETECTAR '500'.
    """
    try:
        xls = pd.ExcelFile(atnd_file)
        
        # Inicializar valores por defecto
        nemonico = "NO_DETECTADO"
        router_name = "NO_DETECTADO"
        vlan_type = "ALL_VLAN"  # Por defecto
        
        # --- A. DETECTAR TIPO DE VLAN ---
        if 'RAN IP Addressing' in xls.sheet_names:
            try:
                df_ran = pd.read_excel(xls, 'RAN IP Addressing', header=None)
                
                # Buscamos "MASTER VLAN"
                mask = df_ran.astype(str).apply(lambda x: x.str.contains('MASTER VLAN', case=False, na=False))
                rows, cols = mask.values.nonzero()
                
                if len(rows) > 0:
                    r, c = rows[0], cols[0]
                    
                    # Buscamos en las siguientes 3 filas (por si hay celdas combinadas)
                    for offset in range(1, 4):
                        if r + offset < len(df_ran):
                            val_crudo = df_ran.iloc[r + offset, c]
                            
                            # --- LIMPIEZA PROFUNDA (Igual que en el lector principal) ---
                            val_str = str(val_crudo)
                            if val_str.endswith('.0'): val_str = val_str[:-2] # Quitar decimal
                            # Quitar todo lo que no sea alfanumérico (quita _x000D_, \n, espacios)
                            val_limpio = re.sub(r'[^a-zA-Z0-9]', '', val_str)
                            
                            if val_limpio == '500':
                                vlan_type = "MASTER_VLAN"
                                print(f"DEBUG (Info): Detectado MASTER VLAN (Valor encontrado: {val_limpio})")
                                break
                            elif val_limpio not in ['nan', 'None', '', 'NAT']:
                                # Si encontramos un valor distinto a 500 y distinto a vacío, paramos
                                break

            except Exception as e:
                print(f"Warning: Error leyendo RAN IP Addressing en extract_info: {e}")
        
        # --- B. INTENTAR EXTRAER NEMÓNICO DEL FILENAME ---
        if hasattr(atnd_file, 'name'):
            filename = atnd_file.name
            parts = filename.split('_')
            # Lógica simple: si empieza con ATND, el segundo elemento suele ser el nemonico
            if len(parts) >= 2 and 'ATND' in parts[0].upper():
                nemonico = parts[1]

        # --- C. EXTRAER NOMBRE DEL ROUTER ---
        # (Mantenemos tu lógica original de búsqueda de ROUTER NAME)
        if 'RAN IP Addressing' in xls.sheet_names:
            try:
                df_ran_name = pd.read_excel(xls, 'RAN IP Addressing', header=None)
                mask_router_name = df_ran_name.astype(str).apply(lambda x: x.str.contains('ROUTER NAME', case=False, na=False))
                rows_rname, cols_rname = mask_router_name.values.nonzero()
                
                if len(rows_rname) > 0:
                    r, c = rows_rname[0], cols_rname[0]
                    for i in range(r + 1, min(r + 5, len(df_ran_name))):
                        name_val = str(df_ran_name.iloc[i, c]).strip()
                        if name_val and name_val.lower() != 'nan':
                            router_name = name_val
                            break
            except: pass

        # Fallback para Router Name en Layer 3
        if router_name == "NO_DETECTADO" and 'Router Layer 3 Configuration' in xls.sheet_names:
            try:
                df_l3 = pd.read_excel(xls, 'Router Layer 3 Configuration', header=None)
                mask_name = df_l3.astype(str).apply(lambda x: x.str.contains('Router Name|Hostname', case=False, na=False))
                rows, cols = mask_name.values.nonzero()
                if len(rows) > 0:
                    r, c = rows[0], cols[0]
                    if c + 1 < len(df_l3.columns):
                        val = str(df_l3.iloc[r, c+1]).strip()
                        if val and val.lower() != 'nan': router_name = val
            except: pass

        # --- D. PREPARAR RESPUESTA ---
        vlan_type_display = "Master VLAN" if vlan_type == "MASTER_VLAN" else "All VLAN"
        
        info = {
            'nemonico': nemonico,
            'router_name': router_name,
            'vlan_type': vlan_type,
            'vlan_type_display': vlan_type_display
        }
        
        return info, None
        
    except Exception as e:
        return None, f"Error al analizar ATND: {str(e)}"


# =====================================================================
# 2. FUNCIONES HELPER PARA EXTRAER DATAFRAMES
# =====================================================================

def get_master_vlan_data(atnd_data: Dict[str, pd.DataFrame]) -> Optional[pd.DataFrame]:
    """ Extrae datos de la hoja 'Layer 2 MASTER VLAN'. """
    # 1. Chequear si la hoja general 'Layer 2 Data' es Master
    if 'VLAN_TYPE' in atnd_data and not atnd_data['VLAN_TYPE'].empty:
        if atnd_data['VLAN_TYPE'].iloc[0]['TIPO'] == 'MASTER_VLAN':
            return atnd_data.get('Layer 2 Data')
            
    # 2. Fallback: Buscar por nombre exacto
    if 'Layer 2 MASTER VLAN' in atnd_data:
        return atnd_data['Layer 2 MASTER VLAN']
    return None

def get_all_client_vlan_data(atnd_data: Dict[str, pd.DataFrame]) -> Optional[pd.DataFrame]:
    """ Extrae datos de la hoja 'Layer 2 ALL CLIENT'. """
    # 1. Chequear si es ALL VLAN
    if 'VLAN_TYPE' in atnd_data and not atnd_data['VLAN_TYPE'].empty:
         if atnd_data['VLAN_TYPE'].iloc[0]['TIPO'] != 'MASTER_VLAN':
            return atnd_data.get('Layer 2 Data')
    else:
        # Si no hay info, asumimos que Layer 2 Data es All Client
        if 'Layer 2 Data' in atnd_data:
             return atnd_data.get('Layer 2 Data')

    # 2. Fallback
    if 'Layer 2 ALL CLIENT' in atnd_data:
        return atnd_data['Layer 2 ALL CLIENT']
    return None


# =====================================================================
# 3. FUNCIÓN PRINCIPAL DE LECTURA (PARA EL GENERADOR)
# =====================================================================

def leer_atnd_router(atnd_file: Any) -> Tuple[Optional[Dict[str, pd.DataFrame]], Optional[str]]:
    """
    Lee el ATND detectando dinámicamente si es MASTER VLAN o ALL VLAN.
    """
    try:
        xls = pd.ExcelFile(atnd_file)
        atnd_data = {}
        
        # --- LÓGICA DE DETECCIÓN INTELIGENTE ---
        tipo_vlan = "ALL_VLAN"
        nombre_hoja_layer2 = "Layer 2 ALL CLIENT"
        
        if 'RAN IP Addressing' in xls.sheet_names:
            try:
                df_ran = pd.read_excel(xls, 'RAN IP Addressing', header=None)
                atnd_data['RAN IP Addressing'] = df_ran
                
                mask = df_ran.astype(str).apply(lambda x: x.str.contains('MASTER VLAN', case=False, na=False))
                rows, cols = mask.values.nonzero()
                
                if len(rows) > 0:
                    r, c = rows[0], cols[0]
                    encontrado_500 = False
                    
                    for offset in range(1, 4):
                        if r + offset < len(df_ran):
                            val_crudo = df_ran.iloc[r+offset, c]
                            
                            # --- LIMPIEZA PROFUNDA ---
                            val_str = str(val_crudo)
                            if val_str.endswith('.0'): val_str = val_str[:-2]
                            val_limpio = re.sub(r'[^a-zA-Z0-9]', '', val_str)
                            
                            print(f"DEBUG: Fila {r+offset} | Crudo: '{val_crudo}' | Limpio: '{val_limpio}'")
                            
                            if val_limpio == '500':
                                encontrado_500 = True
                                break 
                    
                    if encontrado_500:
                        tipo_vlan = "MASTER_VLAN"
                        nombre_hoja_layer2 = "Layer 2 MASTER VLAN"
                        print("DEBUG: !!! DETECTADO TIPO MASTER VLAN (500) !!!")
                    else:
                        print("DEBUG: No se encontró '500' limpio. Se asume ALL VLAN.")
                        
            except Exception as e:
                print(f"Warning: Error leyendo RAN IP para deteccion: {e}")

        # Guardamos el tipo detectado
        atnd_data['VLAN_TYPE'] = pd.DataFrame({'TIPO': [tipo_vlan]})
        
        hojas_a_leer = {
            'Summary': 'Summary',
            'Router': 'Router', 
            'TDM': 'TDM',
            'Synchronization': 'Synchronization',
            'Port Detail': 'Port Detail',
            'Router Layer 3 Configuration': 'Router Layer 3 Configuration',
            'Router Network Management': 'Router Network Management',
            'QoS R6672_BB': 'QoS R6672_BB',
            'TWAMP': 'TWAMP',
            'Layer 2 Data': nombre_hoja_layer2 
        }

        for clave_interna, nombre_hoja_excel in hojas_a_leer.items():
            if nombre_hoja_excel in xls.sheet_names:
                atnd_data[clave_interna] = pd.read_excel(xls, nombre_hoja_excel)
            else:
                # Manejo robusto de hoja Layer 2 faltante
                if clave_interna == 'Layer 2 Data':
                     if tipo_vlan == 'MASTER_VLAN' and 'Layer 2 ALL CLIENT' in xls.sheet_names:
                         print("DEBUG: Hoja Master no encontrada, revirtiendo a All Client")
                         atnd_data['Layer 2 Data'] = pd.read_excel(xls, 'Layer 2 ALL CLIENT')
                     elif 'Layer 2 ALL CLIENT' in xls.sheet_names:
                         atnd_data['Layer 2 Data'] = pd.read_excel(xls, 'Layer 2 ALL CLIENT')
                     else:
                         return None, f"Falta la hoja requerida: {nombre_hoja_excel} (y no se encontró alternativa)"
                else:
                    atnd_data[clave_interna] = pd.DataFrame()

        return atnd_data, None

    except Exception as e:
        return None, f"Error general al leer ATND: {str(e)}"