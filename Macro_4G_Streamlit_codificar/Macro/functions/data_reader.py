# functions/data_reader.py
import pandas as pd
from typing import Dict, Any, Tuple, Optional, List
from io import BytesIO
import numpy as np

# ------------------------------
# 1) Función existente: NO TOCAR (WSH reader)
# ------------------------------
def leer_datos_wsh_lte(wsh_file: Any, nemonico: str) -> Tuple[Optional[Dict[str, str]], str]:
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


# ======================================================================
# 2) CORRECCIÓN DEFINITIVA
#    Lector exclusivo de la hoja NODE
# ======================================================================
def _read_node_sheet_values(rnd_file_xlsx: Any) -> Dict[str, str]:
    """
    Lee EXCLUSIVAMENTE la hoja 'Node'
    y extrae únicamente el valor correcto del MO:

        ENodeBFunction | ENodeBFunction= | 1

    Devuelve un diccionario:
        {"ENodeBFunction": "1"}
    """

    result = {"ENodeBFunction": "1"}  # fallback por si no existe hoja o valor

    try:
        df = pd.read_excel(rnd_file_xlsx, sheet_name='Node', header=None, engine='openpyxl')
    except Exception:
        return result  # si la hoja no existe, retorno fallback

    for _, row in df.iterrows():
        values = [("" if pd.isna(v) else str(v).strip()) for v in row.tolist()]
        if len(values) < 3:
            continue

        mo, attr, val = values[0], values[1], values[2]

        # Debe ser EXACTO:
        #   ENodeBFunction | ENodeBFunction= | 1
        if mo.lower() == "enodebfunction" and attr.lower() == "enodebfunction=":
            if val.strip() != "":
                result["ENodeBFunction"] = val.strip()
            break

    return result


# ======================================================================
# 2.1) Lector Genérico de la hoja NODE
# ======================================================================
def _read_node_all_mos(rnd_file_xlsx: Any) -> Dict[str, Dict[str, str]]:
    """
    Lee la hoja 'Node' y extrae TODOS los MOs encontrados.
    Devuelve: { "MO_NAME": { "attr": "val", ... }, ... }
    NOTA: Si hay múltiples instancias, solo devuelve la última (comportamiento legacy).
    Para múltiples instancias, usar _read_node_mos_grouped.
    """
    result = {}
    try:
        df = pd.read_excel(rnd_file_xlsx, sheet_name='Node', header=None, engine='openpyxl')
    except Exception:
        return result

    for _, row in df.iterrows():
        values = [("" if pd.isna(v) else str(v).strip()) for v in row.tolist()]
        if len(values) < 3:
            continue

        mo_raw, attr, val = values[0], values[1], values[2]
        mo_name = mo_raw.strip()
        
        if mo_name not in result:
            result[mo_name] = {}
            
        if attr.endswith("="): 
            result[mo_name][attr] = val
        else:
            result[mo_name][attr] = val
            
    return result

def _read_node_mos_grouped(rnd_file_xlsx: Any) -> Dict[str, List[Dict[str, str]]]:
    """
    Lee la hoja 'Node' y agrupa las instancias por MO.
    Devuelve: { "MO_NAME": [ {attr: val, ...}, {attr: val, ...} ] }
    """
    result = {}
    try:
        df = pd.read_excel(rnd_file_xlsx, sheet_name='Node', header=None, engine='openpyxl')
    except Exception:
        return result

    # Estructura temporal para agrupar
    # Asumimos que las filas de una misma instancia están contiguas O
    # que cada instancia comienza con el atributo ID (termina en '=')
    
    current_mo_type = None
    current_instance = {}
    
    # Iteramos filas
    for _, row in df.iterrows():
        values = [("" if pd.isna(v) else str(v).strip()) for v in row.tolist()]
        if len(values) < 3:
            continue

        mo_type, attr, val = values[0], values[1], values[2]
        
        # Si cambia el tipo de MO, guardamos la instancia anterior si existe
        if mo_type != current_mo_type:
            if current_mo_type and current_instance:
                if current_mo_type not in result:
                    result[current_mo_type] = []
                result[current_mo_type].append(current_instance)
            
            current_mo_type = mo_type
            current_instance = {}
            
        # Si encontramos un atributo ID (termina en =), y ya tenemos datos en current_instance,
        # asumimos que es una NUEVA instancia del MISMO tipo
        if attr.endswith("=") and current_instance:
             # Verificar si este atributo YA existe en la instancia actual
             # Si ya existe, definitivamente es una nueva instancia
             # O si es el atributo definitorio (ej: EndcProfile=)
             if attr in current_instance:
                 if current_mo_type not in result:
                     result[current_mo_type] = []
                 result[current_mo_type].append(current_instance)
                 current_instance = {}
        
        current_instance[attr] = val

    # Guardar la última
    if current_mo_type and current_instance:
        if current_mo_type not in result:
            result[current_mo_type] = []
        result[current_mo_type].append(current_instance)
        
    return result


# ======================================================================
# 2.2) Lector de Features
# ======================================================================
def _read_features_sheet(rnd_file_xlsx: Any) -> Dict[str, str]:
    """
    Lee la hoja 'Features' y devuelve un diccionario {feature_id: state}.
    Formato esperado:
        Features | CXC... | 1.0
    """
    result = {}
    try:
        df = pd.read_excel(rnd_file_xlsx, sheet_name='Features', header=None, engine='openpyxl')
    except Exception:
        return result

    for _, row in df.iterrows():
        values = [("" if pd.isna(v) else str(v).strip()) for v in row.tolist()]
        if len(values) < 3:
            continue

        mo, feature, val = values[0], values[1], values[2]

        if mo.lower() == "features":
            # Convertir valor a int si es float (1.0 -> 1)
            try:
                val_int = int(float(val))
                result[feature] = str(val_int)
            except:
                result[feature] = val
            
    return result


# ======================================================================
# 3) Lector robusto de Equipment-Configuration
# ======================================================================
def _read_rnd_equipment(rnd_file: Any) -> pd.DataFrame:
    if rnd_file is None:
        raise ValueError("No se recibió archivo RND.")

    if hasattr(rnd_file, "getvalue"):
        raw = BytesIO(rnd_file.getvalue())
    else:
        rnd_file.seek(0)
        raw = BytesIO(rnd_file.read())

    SHEET_NAME = 'Equipment-Configuration'
    raw.seek(0)

    try:
        temp = pd.read_excel(raw, sheet_name=SHEET_NAME, header=None, nrows=500, engine="openpyxl")
    except Exception:
        raw.seek(0)
        temp = pd.read_excel(raw, sheet_name=0, header=None, nrows=500, engine="openpyxl")

    header_row = None
    for i, row in temp.iterrows():
        first = str(row.iloc[0]).strip().upper() if not pd.isna(row.iloc[0]) else ""
        if first == "MO":
            header_row = i
            break

    if header_row is None:
        for i, row in temp.iterrows():
            first = str(row.iloc[0]).strip().upper()
            if "ATRIBU" in first:
                header_row = i
                break

    if header_row is None:
        raise ValueError("No se encontró encabezado en Equipment-Configuration.")

    raw.seek(0)
    try:
        df = pd.read_excel(raw, sheet_name=SHEET_NAME, header=header_row, engine="openpyxl")
    except Exception:
        raw.seek(0)
        df = pd.read_excel(raw, sheet_name=0, header=header_row, engine="openpyxl")

    df.columns = df.columns.astype(str).str.strip()

    if "Atributo" in df.columns and "Atributo_Name" not in df.columns:
        df = df.rename(columns={"Atributo": "Atributo_Name"})

    if "MO" not in df.columns or "Atributo_Name" not in df.columns:
        cols = list(df.columns)
        if len(cols) >= 2:
            df = df.rename(columns={cols[0]: "MO", cols[1]: "Atributo_Name"})
        else:
            raise ValueError("Formato inesperado: falta MO/Atributo_Name")

    df["MO"] = df["MO"].ffill().astype(str).str.strip()
    df["Atributo_Name"] = df["Atributo_Name"].astype(str).str.strip()
    df = df.dropna(subset=["Atributo_Name"])
    df = df.loc[:, ~df.columns.str.contains("Unnamed")]

    data_cols = [c for c in df.columns if c not in ("MO", "Atributo_Name")]
    for col in data_cols:
        df[col] = df[col].apply(
            lambda x: np.nan
            if (pd.isna(x) or str(x).strip() == "" or str(x).strip().upper() == "NAN")
            else str(x).strip()
        )

    return df


# ======================================================================
# 4) Parser de instancias (NO MODIFICADO)
# ======================================================================
def _parse_rnd_instances(df: pd.DataFrame):
    data_cols = [c for c in df.columns if c not in ("MO", "Atributo_Name")]
    inst_by_col = {col: {} for col in data_cols}

    for col in data_cols:
        for _, row in df.iterrows():
            mo = str(row["MO"]).strip()
            attr = str(row["Atributo_Name"]).strip()
            val = row[col]
            if pd.isna(val):
                continue
            inst_by_col[col].setdefault(mo, {})[attr] = str(val).strip()

    freqs = {}
    freq_rel = {}
    cell_rel = {}

    for col, mos in inst_by_col.items():
        for mo_name, attrs in mos.items():

            if mo_name.lower().startswith("eutranfrequency"):
                mo_attrs = list(attrs.keys())
                id_attr = next(
                    (a for a in mo_attrs if a.strip().endswith("=") or ("EUtranFrequency" in a and "=" in a)), None
                )
                if id_attr:
                    freq_id = str(attrs.get(id_attr, col))
                else:
                    freq_id = str(attrs.get("arfcnValueEUtranDl", col))

                try:
                    freq_id = str(int(float(freq_id)))
                except:
                    pass

                freqs.setdefault(freq_id, {}).update(attrs)

            elif mo_name.lower().startswith("eutranfreqrelation"):
                keys = list(attrs.keys())
                if len(keys) >= 2:
                    cell = str(attrs[keys[0]])
                    freq = str(attrs[keys[1]])
                    try:
                        freq = str(int(float(freq)))
                    except:
                        pass
                    key = (cell, freq)
                    freq_rel.setdefault(key, {}).update(attrs)
                else:
                    freq = str(attrs.get(keys[0], ""))
                    freq_rel.setdefault((col, freq), {}).update(attrs)

            elif mo_name.lower().startswith("eutrancellrelation"):
                keys = list(attrs.keys())
                if len(keys) >= 3:
                    cell = str(attrs[keys[0]])
                    freq = str(attrs[keys[1]])
                    rel = str(attrs[keys[2]])
                    try:
                        freq = str(int(float(freq)))
                    except:
                        pass

                    key = (cell, freq, rel)
                    cell_rel.setdefault(key, {}).update(attrs)
                else:
                    for a, v in attrs.items():
                        rel = str(v)
                        cell_rel.setdefault((col, "", rel), {})[a] = v

    return freqs, freq_rel, cell_rel


# ======================================================================
# 5) Lector de Perfiles (DrxProfile, QciProfilePredefined)
# ======================================================================
def _read_equipment_all_mos(rnd_file: Any) -> Dict[str, List[Dict[str, str]]]:
    """
    Lee Equipment-Configuration y extrae TODOS los MOs encontrados.
    Devuelve: { "MO_NAME": [ {attr: val, ...}, ... ] }
    """
    result = {}
    
    try:
        # Leer sin header para obtener todo
        df = pd.read_excel(rnd_file, sheet_name='Equipment-Configuration', header=None, engine='openpyxl')
    except Exception:
        return {}

    # Asumimos col 0 = MO, col 1 = Atributo, col 2+ = Valores
    num_cols = df.shape[1]
    
    for col_idx in range(2, num_cols):
        current_instances = {} # MO -> Dict[attr, val]
        
        # Iterar filas
        for _, row in df.iterrows():
            if pd.isna(row[0]) or pd.isna(row[1]):
                continue
                
            mo = str(row[0]).strip()
            attr = str(row[1]).strip()
            val = row[col_idx]
            
            if pd.isna(val) or str(val).strip() == "" or str(val).upper() == "NAN":
                continue
            
            val_str = str(val).strip()
            
            if mo not in current_instances:
                current_instances[mo] = {}
            
            current_instances[mo][attr] = val_str
            
        # Agregar instancias encontradas en esta columna al resultado global
        for mo, attrs in current_instances.items():
            if mo not in result:
                result[mo] = []
            result[mo].append(attrs)
            
    return result

# Wrapper para compatibilidad si es necesario, o actualizar llamadas
def _read_equipment_profiles(rnd_file: Any) -> Tuple[Dict[str, Dict[str, str]], Dict[str, Dict[str, str]]]:
    """
    Wrapper legacy para mantener compatibilidad con codigo existente que espera drx y qci separados.
    """
    all_mos = _read_equipment_all_mos(rnd_file)
    
    drx_profiles = {}
    qci_profiles = {}
    
    # Convertir lista de dicts a dict por ID para Drx y Qci
    if 'DrxProfile' in all_mos:
        for inst in all_mos['DrxProfile']:
            # Buscar ID
            inst_id = next((v for k, v in inst.items() if k.endswith('=') or 'drxprofile=' in k.lower()), None)
            if inst_id:
                drx_profiles[inst_id] = inst
                
    if 'QciProfilePredefined' in all_mos:
        for inst in all_mos['QciProfilePredefined']:
            inst_id = next((v for k, v in inst.items() if k.endswith('=') or 'qciprofilepredefined=' in k.lower()), None)
            if inst_id:
                qci_profiles[inst_id] = inst
                
    return drx_profiles, qci_profiles
