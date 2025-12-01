# functions/data_reader.py

import pandas as pd
from typing import Dict, Any, Tuple, Optional
from io import BytesIO
import numpy as np

# ============================================================
# 1. FUNCIÓN EXISTENTE — NO SE MODIFICA
# ============================================================

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
        df_lte = pd.read_excel(wsh_file, sheet_name='LTE')
    except ValueError:
        return None, "Error de formato: El archivo cargado no parece ser un Excel válido, o la hoja 'LTE' no existe."
    except Exception as e:
        return None, f"Error al leer el archivo WSHReport como Excel: {e}"
        
    if 'Nemonico' not in df_lte.columns:
        return None, "Error de columna: No se encontró la columna 'Nemonico' en la hoja 'LTE'."

    df_nemonico = df_lte[df_lte['Nemonico'].astype(str).str.upper() == nemonico.upper()]

    if df_nemonico.empty:
        return None, f"Error de búsqueda: Némonico '{nemonico}' no encontrado."

    row = df_nemonico.iloc[0]

    try:
        mask_oam_col = 'Mask.1' if 'Mask.1' in df_lte.columns else 'Mask'
        mask_oam = str(int(row[mask_oam_col]))
        mask_trafico = str(int(row['Mask']))
        
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
    except Exception as e:
        return None, f"Error inesperado durante la extracción de datos: {e}"


# ============================================================
# 2. NUEVO LECTOR RND — REEMPLAZA SOLO TU LECTOR ACTUAL
# ============================================================

def _read_rnd_equipment(rnd_file):
    """
    Lee la hoja Equipment-Configuration del RND en formato:
    MO | Atributo | valor1 | valor2 | valor3...
    """
    if rnd_file is None:
        raise ValueError("No se recibió archivo RND.")

    # Adaptar UploadedFile o buffer
    if hasattr(rnd_file, "getvalue"):
        raw = BytesIO(rnd_file.getvalue())
    else:
        rnd_file.seek(0)
        raw = BytesIO(rnd_file.read())

    SHEET_NAME = "Equipment-Configuration"

    df = pd.read_excel(
        raw,
        sheet_name=SHEET_NAME,
        header=None,
        dtype=str,
        engine="openpyxl"
    )

    # Limpiar filas vacías
    df.dropna(how="all", inplace=True)

    # Normalización
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    return df


# ============================================================
# 3. PARSEADOR DE INSTANCIAS — NUEVO
# ============================================================

def _parse_rnd_instances(df):
    """
    Convierte el DataFrame plano del RND en instancias estructuradas.
    """
    if df.shape[1] < 3:
        raise ValueError("El Excel del RND no tiene columnas suficientes.")

    mos = df[0].tolist()
    attrs = df[1].tolist()
    values = df.iloc[:, 2:]

    freqs = {}
    freq_rel = {}
    cell_rel = {}

    for col in values.columns:
        current_mo = None
        temp = {}
        col_data = values[col].tolist()

        for i in range(len(df)):
            mo = mos[i]
            attr = attrs[i]
            val = col_data[i]

            if pd.isna(val) or val == "":
                continue

            if mo != current_mo:
                if current_mo and temp:
                    _store_instance(current_mo, temp, freqs, freq_rel, cell_rel)
                temp = {}
                current_mo = mo

            temp[attr] = val

        if current_mo and temp:
            _store_instance(current_mo, temp, freqs, freq_rel, cell_rel)

    return freqs, freq_rel, cell_rel


def _store_instance(mo, attrs, freqs, freq_rel, cell_rel):
    """
    Clasifica instancias según el tipo de MO.
    """

    # EUtranFrequency
    if mo == "EUtranFrequency":
        freq_id = attrs.get("EUtranFrequency=", None)
        if freq_id:
            freqs[freq_id] = attrs
        return

    # EUtranFreqRelation
    if mo == "EUtranFreqRelation":
        cell = attrs.get("EUtranCellFDD=", None)
        freq = attrs.get("EUtranFreqRelation=", None)
        if cell and freq:
            freq_rel[(cell, freq)] = attrs
        return

    # EUtranCellRelation
    if mo == "EUtranCellRelation":
        cell = attrs.get("EUtranCellFDD=", None)
        freq = attrs.get("EUtranFreqRelation=", None)
        rel  = attrs.get("EUtranCellRelation=", None)
        if cell and freq and rel:
            cell_rel[(cell, freq, rel)] = attrs
        return
