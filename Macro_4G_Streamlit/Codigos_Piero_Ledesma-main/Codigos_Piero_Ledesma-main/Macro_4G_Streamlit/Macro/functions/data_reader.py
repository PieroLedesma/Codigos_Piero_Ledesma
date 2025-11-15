# functions/data_reader.py

import pandas as pd
from typing import Dict, Any, Tuple, Optional

def leer_datos_wsh_lte(wsh_file: Any, nemonico: str) -> Tuple[Optional[Dict[str, str]], str]:
    """
    Lee los datos de red (IPs, VLANs, DGWs, Mask) del archivo WSHReport
    y devuelve un diccionario con las variables clave.
    """
    if not wsh_file:
        return None, "Error de datos: El archivo WSHReport no ha sido cargado."
    if not nemonico:
        return None, "Error de datos: El Némonico es requerido para buscar en el WSH."

    try:
        # Usar pd.read_excel() directamente con el nombre de la hoja
        df_lte = pd.read_excel(wsh_file, sheet_name='LTE')
        
    except ValueError:
        return None, "Error de formato: El archivo cargado no parece ser un Excel válido, o la hoja 'LTE' no existe."
    except Exception as e:
        return None, f"Error al leer el archivo WSHReport como Excel: {e}"
        
    if 'Nemonico' not in df_lte.columns:
        return None, "Error de columna: No se encontró la columna 'Nemonico' en la hoja 'LTE' del WSHReport. Por favor, verifica el encabezado."

    df_nemonico = df_lte[df_lte['Nemonico'].astype(str).str.upper() == nemonico.upper()]

    if df_nemonico.empty:
        return None, f"Error de búsqueda: Némonico '{nemonico}' no encontrado en la hoja 'LTE' del WSHReport."
    
    row = df_nemonico.iloc[0]
    
    try:
        # Lógica de extracción de datos del WSH
        # Se asume 'Mask' para tráfico y 'Mask.1' para OAM, o se usa 'Mask' si solo hay una.
        mask_oam_col = 'Mask.1' if 'Mask.1' in df_lte.columns else 'Mask'
        mask_oam = str(int(row[mask_oam_col]))
        mask_trafico = str(int(row['Mask'])) # Asume que el primer 'Mask' es el de Trafico
        
        data = {
            'VLAN_OAM_LTE': str(int(row['Vlan OAM_LTE'])),
            'IP_OAM_LTE': row['IP OAM_LTE'],
            'MASK_OAM': mask_oam,
            'DGW_OAM_LTE': row['DGW OAM_LTE'],
            'VLAN_LTE': str(int(row['Vlan LTE'])),
            'IP_TRAFICO_LTE': row['IP Trafico LTE'],
            'MASK_TRAFICO': mask_trafico,
            'DGW_TRAFICO_LTE': row['DGW Trafico LTE'],
            'DNS_SERVER': '10.170.15.20'
        }
        data = {k: str(v) for k, v in data.items()}
        
        return data, "Datos de WSH extraídos con éxito."
    except KeyError as e:
        return None, f"Error de columna: Una de las columnas clave no se encontró. Revisa los encabezados del archivo. Columna faltante: {e}"
    except Exception as e:
        return None, f"Error inesperado durante la extracción de datos: {e}"