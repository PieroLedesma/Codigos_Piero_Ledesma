# functions/utran_relation_generator.py
import datetime
from io import BytesIO
from typing import Any, Dict, List, Tuple, Optional
import re
import pandas as pd
import numpy as np

_EXT_ID_RE = re.compile(r'\d{3,5}-\d{3,5}-\d{3,6}') # patrón flexible para 7301-1323-26211 etc.

# Defaults (Solo para atributos seguros o deducibles. Se ELIMINAN lac, rac y physicalCellIdentity)
_DEFAULTS = {
    "lbUtranCellOffloadCapacity": "1000",
    "isRemoveAllowed": "false",
    "srvccCapability": "1",
    "rimCapable": "0",
    # 'lac', 'rac', y 'physicalCellIdentity' se extraen SIEMPRE del RND.
}


def _read_rnd_sheet(rnd_file: Any, sheet_name: str) -> Optional[pd.DataFrame]:
    """Leer hoja del RND desde el BytesIO del uploader de Streamlit."""
    if rnd_file is None:
        return None
    try:
        # rnd_file puede ser un UploadedFile (has getvalue) o un buffer
        if hasattr(rnd_file, "getvalue"):
            raw = BytesIO(rnd_file.getvalue())
        else:
            raw = BytesIO(rnd_file)
        df = pd.read_excel(raw, sheet_name=sheet_name, header=0, dtype=str, engine='openpyxl')
        # Normalizar: strip en nombres de columnas
        df.columns = df.columns.astype(str).str.strip()
        # Rellenar NaN con empty string para facilitar comparaciones
        df = df.replace({np.nan: ""})
        # Asegurar columna 'MO' y 'Atributo' existen (si no, retornar None)
        if 'MO' not in df.columns or 'Atributo' not in df.columns:
            return None
        return df
    except Exception as e:
        print(f"[utran_relation] Error leyendo hoja {sheet_name}: {e}")
        return None


def _extract_utran_frequencies(df_eq: pd.DataFrame) -> Tuple[List[Dict[str, str]], Dict[int, str]]:
    """
    Extrae UtranFrequency desde MO == 'UtranFrequency'.
    Mapea columnas incluso si los IDs son dispersos, propagando la última frecuencia conocida.
    """
    if df_eq is None:
        return [], {}

    rows = df_eq[df_eq['MO'].astype(str).str.strip() == 'UtranFrequency']
    if rows.empty:
        return [], {}

    # buscamos la fila que contenga UtranFrequency= o UtranFrequencyId
    id_row = None
    for idx, val in rows['Atributo'].astype(str).str.strip().items():
        if val.startswith('UtranFrequency=') or val.startswith('UtranFrequencyId') or val.startswith('UtranFrequency'):
            id_row = rows.loc[idx]
            break
    if id_row is None:
        # fallback: intentar usar la primer fila de rows
        id_row = rows.iloc[0]

    # filas auxiliares
    arfcn_row = rows[rows['Atributo'].astype(str).str.strip() == 'arfcnValueUtranDl'].iloc[0] if not rows[rows['Atributo'].astype(str).str.strip() == 'arfcnValueUtranDl'].empty else None
    userlabel_row = rows[rows['Atributo'].astype(str).str.strip().str.contains('userLabel', na=False)].iloc[0] if not rows[rows['Atributo'].astype(str).str.strip().str.contains('userLabel', na=False)].empty else None

    resultado = []
    col_map = {}
    last_freq_id = "" # Variable para propagar la frecuencia
    unique_freqs = set() # Para asegurar que resultado solo contenga una entrada por frecuencia

    # identificar índice de columna 'Atributo' para determinar las columnas de valores
    try:
        atributo_index = list(df_eq.columns).index('Atributo')
    except ValueError:
        atributo_index = 0

    # iterar columnas donde están los valores (columna siguiente a 'Atributo' hacia la derecha)
    for col_index in range(atributo_index + 1, len(df_eq.columns)):
        try:
            freq_id_raw = id_row.iloc[col_index]
        except Exception:
            freq_id_raw = ""
        freq_id = str(freq_id_raw).strip()
        
        is_freq_header = bool(freq_id and freq_id.lower() not in ('nan', 'vacio', ''))

        if is_freq_header:
            last_freq_id = freq_id # Actualizar la última frecuencia conocida
            
            if freq_id not in unique_freqs:
                unique_freqs.add(freq_id)
                
                # Extraer metadata solo una vez para la frecuencia única
                arfcn = str(arfcn_row.iloc[col_index]).strip() if arfcn_row is not None else ""
                userlabel = str(userlabel_row.iloc[col_index]).strip() if userlabel_row is not None else ""
                
                resultado.append({
                    'freq_id': freq_id,
                    'arfcn': arfcn,
                    'userLabel': userlabel
                })
        
        # Mapear la columna a la última frecuencia conocida,
        # incluso si la celda actual está vacía (estructura dispersa)
        if last_freq_id:
            col_map[col_index] = last_freq_id

    return resultado, col_map


def _extract_external_utran_cells(df_eq: pd.DataFrame, col_map: Dict[int, str]) -> List[Dict]:
    """
    Busca ExternalUtranCellFDD usando la fila 'externalUtrancellFDDid' como índice principal.
    Devuelve lista de dicts con la información de cada celda externa.
    """
    if df_eq is None:
        return []

    results = []
    # Localizamos las filas relevantes para ExternalUtranCellFDD
    ext_rows = df_eq[df_eq['MO'].astype(str).str.strip() == 'ExternalUtranCellFDD']
    if ext_rows.empty:
        return []

    # 1. Encontrar la fila que contiene los External IDs
    extid_row_match = ext_rows[ext_rows['Atributo'].astype(str).str.strip().str.lower() == 'externalutrancellfddid']
    if extid_row_match.empty:
        # Fallback si no está el nombre exacto
        extid_row_match = ext_rows[ext_rows['Atributo'].astype(str).str.strip().str.contains('externalutrancellfddid', case=False, na=False)]
    if extid_row_match.empty:
        return []

    # Se asume que solo hay una fila con 'externalUtrancellFDDid'
    extid_row = extid_row_match.iloc[0]

    # Localizamos índice de 'Atributo' para empezar a iterar por valores
    try:
        atributo_index = list(df_eq.columns).index('Atributo')
    except ValueError:
        atributo_index = 0
    first_value_col = atributo_index + 1
    
    # Mapeo de Atributos del RND a Filas de índice rápido
    attr_to_row = {}
    for _, row in ext_rows.iterrows():
        attr_name = str(row['Atributo']).strip()
        if attr_name:
            attr_to_row[attr_name] = row

    # Mapeo de Atributos del RND a Keys del MOS
    attr_map = {
        'externalUtrancellFDDid': 'externalId',
        'physicalCellIdentity': 'physicalCellIdentity',
        'lac': 'lac',
        'rac': 'rac',
        'isRemoveAllowed': 'isRemoveAllowed',
        'srvccCapability': 'srvccCapability',
        'userLabel': 'userLabel', 
        'rimCapable': 'rimCapable',
        'lbUtranCellOffloadCapacity': 'lbUtranCellOffloadCapacity'
    }

    # 2. Iterar por columna de valor
    for col_index in range(first_value_col, len(df_eq.columns)):
        # Obtener el External ID de la fila de índice
        ext_id = str(extid_row.iloc[col_index]).strip()
        
        # Obtener la frecuencia asociada a esta columna
        freq_id = col_map.get(col_index, "")
        
        # Solo procesar si hay un ID externo y una frecuencia asociada
        if not ext_id or ext_id.lower() in ('nan', 'vacio', '') or not freq_id:
            continue

        attrs: Dict[str, str] = {}
        
        # 3. Recolectar atributos verticalmente
        for RND_attr, MOS_key in attr_map.items():
            if RND_attr in attr_to_row:
                try:
                    val = str(attr_to_row[RND_attr].iloc[col_index]).strip()
                    if val and val.lower() not in ('nan', 'vacio', ''):
                        attrs[MOS_key] = val
                except Exception:
                    continue
        
        # === DEDUCCIONES Y DEFAULTS ===
        
        # 3.1. cellIdentity: Formatear cId=CellID,rncId=RNCID desde ext_id (ej. 7301-1323-26211)
        parts = ext_id.split('-')
        if len(parts) >= 3:
            # Asegurar que la deducción de cId y rncId se hace correctamente
            attrs['cellIdentity'] = f"cId={parts[-1]},rncId={parts[-2]}"
        
        # 3.2. plmnIdentity: Formatear mcc=xxx,mnc=y,mncLength=z desde ext_id (ej. 7301 -> mcc=730,mnc=1)
        mcc_mnc = parts[0]
        if len(mcc_mnc) >= 4:
            mcc = mcc_mnc[:3]
            mnc = mcc_mnc[3:]
            attrs['plmnIdentity'] = f"mcc={mcc},mnc={mnc},mncLength={len(mnc)}"
        
        results.append({
            'ext_id': ext_id,
            'col_index': col_index,
            'attrs': attrs,
            'freq_id': freq_id
        })

    return results


def _extract_utran_freq_relations(df_eq: pd.DataFrame) -> List[Dict]:
    """
    Extrae UtranFreqRelation.
    """
    if df_eq is None:
        return []

    rows = df_eq[df_eq['MO'].astype(str).str.strip() == 'UtranFreqRelation']
    if rows.empty:
        return []

    # encontrar row que tenga el encabezado con ENodeBFunction=1,EUtranCellFDD=
    header_row = None
    for idx, val in rows['Atributo'].astype(str).items():
        if str(val).strip().startswith('ENodeBFunction=1,EUtranCellFDD='):
            header_row = rows.loc[idx]
            break
    if header_row is None:
        return []

    try:
        atributo_index = list(df_eq.columns).index('Atributo')
    except ValueError:
        atributo_index = 0
    first_value_col = atributo_index + 1

    # obtener fila que contiene 'UtranFreqRelation=' para obtener freq por columna
    ufr_row = None
    for idx, val in rows['Atributo'].astype(str).items():
        if str(val).strip().startswith('UtranFreqRelation='):
            ufr_row = rows.loc[idx]
            break

    relations = []
    core_attrs = [
        'anrMeasOn', 'cellReselectionPriority', 'connectedModeMobilityPrio', 'csFallbackPrio',
        'csFallbackPrioEC', 'lbBnrPolicy', 'mobilityAction', 'mobilityActionCsfb', 'pMaxUtra',
        'qOffsetFreq', 'qQualMin', 'qRxLevMin', 'threshXHigh', 'threshXHighQ', 'threshXLow',
        'threshXLowQ', 'userLabel', 'utranFreqToQciProfileRelation', 'voicePrio',
        'altCsfbTargetPrio', 'altCsfbTargetPrioEc', 'b2Thr1RsrpUtraFreqOffset',
        'b2Thr1RsrqUtraFreqOffset', 'b2Thr2EcNoUtraFreqOffset', 'b2Thr2RscpUtraFreqOffset',
        'atoAllowed'
    ]

    # filtrar columnas válidas (donde header_row tiene eutran cell no vacío)
    for col_index in range(first_value_col, len(df_eq.columns)):
        eutran_cell = str(header_row.iloc[col_index]).strip()
        if not eutran_cell or eutran_cell.lower() in ('nan', 'vacio', ''):
            continue

        utran_freq = ""
        if ufr_row is not None:
            try:
                utran_freq = str(ufr_row.iloc[col_index]).strip()
            except Exception:
                utran_freq = ""

        # si utran_freq vacío, saltar (evita cr con _nan)
        if not utran_freq:
            continue

        attrs: Dict[str, str] = {}
        for attr in core_attrs:
            matches = rows[rows['Atributo'].astype(str).str.strip() == attr]
            if not matches.empty:
                try:
                    v = str(matches.iloc[0].iloc[col_index]).strip()
                    if v and v.lower() not in ('nan', 'vacio', ''):
                        # force userLabel to empty where required by spec
                        if attr == 'userLabel':
                            attrs['userLabel'] = ""
                        else:
                            attrs[attr] = v
                except Exception:
                    continue

        # allowedPlmnList
        allowed_plmns = []
        try:
            mcc_row_match = rows[rows['Atributo'].astype(str).str.strip().str.contains('allowedPlmnList_mcc', na=False)]
            mnc_row_match = rows[rows['Atributo'].astype(str).str.strip().str.contains('allowedPlmnList_mnc', na=False)]
            mncLen_row_match = rows[rows['Atributo'].astype(str).str.strip().str.contains('allowedPlmnList_mncLength', na=False)]

            if not mcc_row_match.empty and not mnc_row_match.empty and not mncLen_row_match.empty:
                mcc_row = mcc_row_match.iloc[0]
                mnc_row = mnc_row_match.iloc[0]
                mncLen_row = mncLen_row_match.iloc[0]
            
                mcc_vals = str(mcc_row.iloc[col_index]).strip().split()
                mnc_vals = str(mnc_row.iloc[col_index]).strip().split()
                mncLen_vals = str(mncLen_row.iloc[col_index]).strip().split()

                # Usa zip para asegurar consistencia
                for mcc, mnc, mncLen in zip(mcc_vals, mnc_vals, mncLen_vals):
                    if mcc and mnc:
                        allowed_plmns.append((mcc, mnc, mncLen if mncLen else '2'))
        except Exception as e:
            allowed_plmns = []

        relations.append({
            'eutran_cell': eutran_cell,
            'utran_freq': utran_freq,
            'attrs': attrs,
            'allowed_plmns': allowed_plmns,
            'col_index': col_index
        })

    return relations

def _extract_utran_cell_relations(df_eq: pd.DataFrame) -> List[Dict]:
    """
    Extrae UtranCellRelation (vecinos 3G) desde MO == 'UtranCellRelation'.
    """
    if df_eq is None:
        return []

    rows = df_eq[df_eq['MO'].astype(str).str.strip() == 'UtranCellRelation']
    if rows.empty:
        return []
    
    # 1. Encontrar la fila que contiene la celda LTE (header)
    eutran_row_match = rows[rows['Atributo'].astype(str).str.strip().str.contains('EUtranCellFDD=', na=False)]
    if eutran_row_match.empty:
        return []
    eutran_row = eutran_row_match.iloc[0]

    # 2. Encontrar la fila de la Frecuencia 3G
    utran_freq_row_match = rows[rows['Atributo'].astype(str).str.strip() == 'UtranFreqRelation']
    if utran_freq_row_match.empty:
        return []
    utran_freq_row = utran_freq_row_match.iloc[0]

    # 3. Encontrar la fila del Vecino 3G (el ID de la UtranCellRelation)
    utran_cell_row_match = rows[rows['Atributo'].astype(str).str.strip() == 'UtranCellRelation']
    if utran_cell_row_match.empty:
        return []
    utran_cell_row = utran_cell_row_match.iloc[0]

    # 4. Encontrar fila de 'coverageIndicator'
    cov_ind_row_match = rows[rows['Atributo'].astype(str).str.strip() == 'coverageIndicator']
    cov_ind_row = cov_ind_row_match.iloc[0] if not cov_ind_row_match.empty else None
    
    try:
        atributo_index = list(df_eq.columns).index('Atributo')
    except ValueError:
        atributo_index = 0
    first_value_col = atributo_index + 1

    relations = []
    
    for col_index in range(first_value_col, len(df_eq.columns)):
        eutran_cell = str(eutran_row.iloc[col_index]).strip()
        utran_freq = str(utran_freq_row.iloc[col_index]).strip()
        utran_cell_id = str(utran_cell_row.iloc[col_index]).strip()
        
        if not all([eutran_cell, utran_freq, utran_cell_id]) or utran_cell_id.lower() in ('nan', 'vacio', ''):
            continue
        
        attrs: Dict[str, str] = {}
        
        if cov_ind_row is not None:
            try:
                # El RND podría tener un valor para coverageIndicator, si no, se usará '0' en el MOS
                val = str(cov_ind_row.iloc[col_index]).strip()
                attrs['coverageIndicator'] = val if val else '0'
            except:
                attrs['coverageIndicator'] = '0'
        
        relations.append({
            'eutran_cell': eutran_cell,
            'utran_freq': utran_freq,
            'utran_cell': utran_cell_id,
            'attrs': attrs
        })

    return relations


def generar_utran_relation_mos(nemonico: str, rnd_node_file: Any) -> str:
    """
    Genera el MOS para UtranRelation basándose en la hoja Equipment-Configuration del RND.
    Retorna el contenido .mos (string).
    """
    nemonico_upper = nemonico.upper()
    df_eq = _read_rnd_sheet(rnd_node_file, 'Equipment-Configuration')
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    freqs, col_map = _extract_utran_frequencies(df_eq)
    relations = _extract_utran_freq_relations(df_eq)
    external_cells = _extract_external_utran_cells(df_eq, col_map)
    cell_relations = _extract_utran_cell_relations(df_eq)

    header = f"""confb+
gs+

lt all

"""
    body_lines: List[str] = []

    # 1) Crear UtranFrequency
    if freqs:
        for f in freqs:
            fid = f.get('freq_id', '').strip()
            arfcn = f.get('arfcn', '').strip()
            # Obtener el userLabel
            user_label = f.get('userLabel', '').strip() 
            
            if not fid:
                continue
            
            body_lines.append(f" cr  ENodeBFunction=1,UtraNetwork=1,UtranFrequency={fid}")
            if arfcn:
                body_lines.append(f"{arfcn} #arfcnValueUtranDl")
                
            # Usar el userLabel extraído del RND para UtranFrequency
            if user_label:
                body_lines.append(f" set   ENodeBFunction=1,UtraNetwork=1,UtranFrequency={fid}$ userLabel  {user_label}")
            else:
                # Si está vacío en RND, se setea a vacío
                body_lines.append(f" set   ENodeBFunction=1,UtraNetwork=1,UtranFrequency={fid}$ userLabel  ")

            body_lines.append("")  # separación
    else:
        body_lines.append("// No se encontraron UtranFrequency en el RND -> Ninguna frecuencia UTRAN creada")
        body_lines.append("")

    # 2) Crear UtranFreqRelation
    if relations:
        for rel in relations:
            eutran = rel['eutran_cell']
            utran = rel['utran_freq']
            attrs = rel.get('attrs', {})

            if not eutran or not utran:
                continue

            body_lines.append(f" cr  ENodeBFunction=1,EUtranCellFDD={eutran},UtranFreqRelation={utran}")
            # línea con referencia exacta
            body_lines.append(f" UtraNetwork=1,UtranFrequency={utran}  #utranFrequencyRef")
            # cellReselectionPriority como línea aparte si existe
            cr_priority = attrs.get('cellReselectionPriority', '')
            if cr_priority:
                body_lines.append(f"{cr_priority}   #cellReselectionPriority         ")

            # ahora los SETs en orden fijo
            ordered_keys = [
                'anrMeasOn','connectedModeMobilityPrio','csFallbackPrio','csFallbackPrioEC','lbBnrPolicy',
                'mobilityAction','mobilityActionCsfb','pMaxUtra','qOffsetFreq','qQualMin','qRxLevMin','threshXHigh',
                'threshXHighQ','threshXLow','threshXLowQ','userLabel','utranFreqToQciProfileRelation','voicePrio',
                'altCsfbTargetPrio','altCsfbTargetPrioEc','b2Thr1RsrpUtraFreqOffset','b2Thr1RsrqUtraFreqOffset',
                'b2Thr2EcNoUtraFreqOffset','b2Thr2RscpUtraFreqOffset','atoAllowed'
            ]
            for k in ordered_keys:
                v = attrs.get(k, "")
                if v is None:
                    continue
                vstr = str(v).strip()
                if k == 'userLabel':
                    # userLabel DEBE ser vacío para UtranFreqRelation
                    body_lines.append(f" set ENodeBFunction=1,EUtranCellFDD={eutran},UtranFreqRelation={utran} userLabel  ")
                elif vstr != "" and vstr.lower() not in ('nan', 'vacio'):
                    body_lines.append(f" set ENodeBFunction=1,EUtranCellFDD={eutran},UtranFreqRelation={utran} {k} {vstr}")
            body_lines.append("")  # separación
    else:
        body_lines.append("// No se encontraron UtranFreqRelation en el RND -> Ninguna relación creada")
        body_lines.append("")

    # 3) ExternalUtranCellFDD: crear bloques crn por cada external cell detectada
    if external_cells:
        for ext in external_cells:
            extid = ext['ext_id']
            attrs = ext.get('attrs', {})
            freq = ext.get('freq_id', '')

            if not extid or extid.lower() in ('nan', 'vacio', ''):
                continue

            body_lines.append(f" crn  ENodeBFunction=1,UtraNetwork=1,UtranFrequency={freq},ExternalUtranCellFDD={extid}")

            # cellIdentity (usar el deducido/extraído)
            cId_val = attrs.get('cellIdentity', '').strip()
            if not cId_val:
                cId_val = " " 
            body_lines.append(f"cellIdentity {cId_val}")
            
            # isRemoveAllowed (usa RND, si no, DEFAULT SEGURO)
            isRemove = attrs.get('isRemoveAllowed', '').strip()
            if not isRemove or isRemove.lower() in ('nan', 'vacio'):
                isRemove = _DEFAULTS.get('isRemoveAllowed', 'false') # Usar default
            body_lines.append(f"isRemoveAllowed {isRemove}")

            # lac (SOLO RND: si está vacío, queda vacío)
            lac = attrs.get('lac', '').strip()
            body_lines.append(f"lac {lac}")

            # lbUtranCellOffloadCapacity (usa RND, si no, DEFAULT SEGURO)
            lbcap = attrs.get('lbUtranCellOffloadCapacity', '').strip()
            if not lbcap or lbcap.lower() in ('nan', 'vacio'):
                lbcap = _DEFAULTS.get('lbUtranCellOffloadCapacity', '1000') # Usar default
            body_lines.append(f"lbUtranCellOffloadCapacity {lbcap}")

            # masterUtranCellId (vacío)
            body_lines.append("masterUtranCellId ")

            # physicalCellIdentity (SOLO RND: si está vacío, queda vacío)
            phys = attrs.get('physicalCellIdentity', '').strip()
            body_lines.append(f"physicalCellIdentity {phys}")

            # plmnIdentity (DEDUCIDO, si no default de ejemplo)
            plmn = attrs.get('plmnIdentity', '').strip()
            if not plmn or plmn.lower() in ('nan', 'vacio'):
                body_lines.append("plmnIdentity mcc=730,mnc=1,mncLength=2")
            else:
                body_lines.append(f"plmnIdentity {plmn}")

            # rac (SOLO RND: si está vacío, queda vacío)
            rac = attrs.get('rac', '').strip()
            body_lines.append(f"rac {rac}")

            # rimCapable (usa RND, si no, DEFAULT SEGURO)
            rim = attrs.get('rimCapable', '').strip()
            if not rim or rim.lower() in ('nan', 'vacio'):
                rim = _DEFAULTS.get('rimCapable', '0') # Usar default
            body_lines.append(f"rimCapable {rim}")

            # srvccCapability (usa RND, si no, DEFAULT SEGURO)
            srvcc = attrs.get('srvccCapability', '').strip()
            if not srvcc or srvcc.lower() in ('nan', 'vacio'):
                srvcc = _DEFAULTS.get('srvccCapability', '1') # Usar default
            body_lines.append(f"srvccCapability {srvcc}")

            # userLabel (FORZADO VACÍO)
            body_lines.append("userLabel ")

            body_lines.append("")
            body_lines.append("end")
            body_lines.append("")
    else:
        body_lines.append("// No se encontraron ExternalUtranCellFDD en el RND -> Ninguna celda externa creada")
        body_lines.append("")


    # 4) UtranCellRelation blocks
    if cell_relations: 
        for rel in cell_relations:
            eutran = rel['eutran_cell']
            utran_freq = rel['utran_freq']
            extid = rel['utran_cell'] # ID del vecino 3G (ExternalUtranCellFDD)
            attrs = rel['attrs']

            if not eutran or not utran_freq or not extid:
                continue
            
            # crn
            body_lines.append(f" crn  ENodeBFunction=1,EUtranCellFDD={eutran},UtranFreqRelation={utran_freq},UtranCellRelation={extid}")
            
            # Atributos: coverageIndicator
            cov_ind = attrs.get('coverageIndicator', '0').strip()
            if not cov_ind or cov_ind.lower() in ('nan', 'vacio'):
                cov_ind = '0'
            body_lines.append(f"coverageIndicator {cov_ind}")
            
            # externalUtranCellFDDRef
            body_lines.append(f"externalUtranCellFDDRef UtraNetwork=1,UtranFrequency={utran_freq},ExternalUtranCellFDD={extid}")
            
            # Atributos fijos (según el ejemplo)
            body_lines.append("isHoAllowed true")
            body_lines.append("isRemoveAllowed true")
            body_lines.append("lbBnrAllowed true")
            body_lines.append("lbCovIndicated false")
            body_lines.append("loadBalancing 0")
            
            body_lines.append("end")
            body_lines.append("")  # separación
    else:
        body_lines.append("// No se encontraron UtranCellRelation en el RND -> Ninguna relación de vecino creada")
        body_lines.append("")

    # 5) allowedPlmnList (global)
    all_allowed = []
    for r in relations:
        for triple in r.get('allowed_plmns', []):
            all_allowed.append(triple)

    # si no hay allowed_plmns recogidos, se genera el default repetido (para cumplir ejemplo)
    if not all_allowed:
        # default example repeated N times (ajustable)
        repeat_count = 15
        default_trip = ('1', '1', '2')
        all_allowed = [default_trip] * repeat_count

    if all_allowed:
        plmn_entries = []
        for (mcc, mnc, mlen) in all_allowed:
            plmn_entries.append(f"mcc={mcc},mnc={mnc},mncLength={mlen}")
        joined = ";".join(plmn_entries)
        body_lines.append(f" set ,UtranFreqRelation= allowedPlmnList {joined}")
        body_lines.append("")

    footer = "\n confb-\n gs-\n"

    final = header + "\n".join(body_lines) + footer
    signature = f"""// ====================================================================
//  ARCHIVO PARA CREACIÓN DE UTRANFREQ Y EXTERNALFREQ
// ====================================================================
// AUTOR: Piero Ledesma
// FECHA: {current_date}
// NEMONICO: {nemonico_upper}
// NOTA: Generado desde Equipment-Configuration (RND)
//

"""
    return signature + final