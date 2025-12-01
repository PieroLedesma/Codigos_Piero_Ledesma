# functions/utran_relation_generator.py
import datetime
from io import BytesIO
from typing import Any, Dict, List, Tuple, Optional
import re
import pandas as pd
import numpy as np

_EXT_ID_RE = re.compile(r'\d{3,5}-\d{3,5}-\d{3,6}')  # patrón flexible para 7301-1323-26211 etc.


def _read_rnd_sheet(rnd_file: Any, sheet_name: str) -> Optional[pd.DataFrame]:
    """Leer hoja del RND desde el BytesIO del uploader de Streamlit."""
    if rnd_file is None:
        return None
    try:
        # rnd_file puede ser un UploadedFile (has getvalue) o un buffer
        if hasattr(rnd_file, "getvalue"):
            raw = BytesIO(rnd_file.getvalue())
        else:
            # asumimos ya es un buffer-like
            raw = BytesIO(rnd_file)
        df = pd.read_excel(raw, sheet_name=sheet_name, header=0, dtype=str, engine='openpyxl')
        # Normalizar: strip en nombres de columnas
        df.columns = df.columns.astype(str).str.strip()
        # Rellenar NaN con empty string para facilitar comparaciones
        df = df.replace({np.nan: ""})
        return df
    except Exception as e:
        print(f"[utran_relation] Error leyendo hoja {sheet_name}: {e}")
        return None


def _extract_utran_frequencies(df_eq: pd.DataFrame) -> Tuple[List[Dict[str, str]], Dict[int, str]]:
    """
    Extrae UtranFrequency desde MO == 'UtranFrequency'.
    Devuelve:
      - lista de dicts con keys: 'freq_id' (ej. _412), 'arfcn', 'userLabel'
      - mapping col_index -> freq_id (para mapear columnas completas)
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
    arfcn_row = None
    userlabel_row = None
    for idx, val in rows['Atributo'].astype(str).str.strip().items():
        if 'arfcnValueUtranDl' in val:
            arfcn_row = rows.loc[idx]
        if 'userLabel' == val or 'userLabel' in val:
            userlabel_row = rows.loc[idx]

    resultado = []
    col_map = {}

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
        if not freq_id or freq_id.lower() in ('nan', 'vacio', ''):
            continue

        arfcn = ""
        if arfcn_row is not None:
            try:
                arfcn = str(arfcn_row.iloc[col_index]).strip()
            except Exception:
                arfcn = ""

        userlabel = ""
        if userlabel_row is not None:
            try:
                userlabel = str(userlabel_row.iloc[col_index]).strip()
            except Exception:
                userlabel = ""

        resultado.append({
            'freq_id': freq_id,
            'arfcn': arfcn,
            'userLabel': userlabel
        })
        col_map[col_index] = freq_id

    return resultado, col_map


def _extract_external_utran_cells(df_eq: pd.DataFrame, col_map: Dict[int, str]) -> List[Dict]:
    """
    Busca ExternalUtranCellFDD en las columnas escaneando valores que cumplan pattern ext_id.
    Devuelve lista de dicts:
      {'ext_id': '7301-1323-26211', 'col_index': X, 'attrs': {'cellIdentity': 'cId=26211,rncId=1323', ...}, 'freq_id': '_412'}
    """
    if df_eq is None:
        return []

    results = []
    # localizamos índice de 'Atributo'
    try:
        atributo_index = list(df_eq.columns).index('Atributo')
    except ValueError:
        atributo_index = 0

    # convertimos todas las celdas a str para buscar regex
    # iteramos por columna (valores a la derecha de 'Atributo')
    for col_index in range(atributo_index + 1, len(df_eq.columns)):
        col_series = df_eq.iloc[:, col_index].astype(str).fillna("")
        found_exts = set()
        for cell_val in col_series:
            if not cell_val:
                continue
            for m in _EXT_ID_RE.findall(cell_val):
                found_exts.add(m)

        if not found_exts:
            continue

        # para cada external id encontrado, intentar extraer atributos cercanos en la hoja
        for ext in sorted(found_exts):
            attrs = {}
            # buscar filas relevantes por nombre de Atributo (cellIdentity, physicalCellIdentity, plmnIdentity, lac, rac, userLabel, etc.)
            # iterar sobre filas para extraer el valor en esta columna
            for _, row in df_eq.iterrows():
                attr_name = str(row['Atributo']).strip()
                if not attr_name:
                    continue
                try:
                    val = str(row.iloc[col_index]).strip()
                except Exception:
                    val = ""
                # Normalizamos nombres de atributos que nos importan
                normalized = attr_name.lower()
                if any(k in normalized for k in ('cellidentity', 'cellidentity cId', 'cellidentity cid', 'cellidentity cId')):
                    attrs['cellIdentity'] = val
                elif 'physicalcellidentity' in normalized or 'physicalCellIdentity'.lower() in normalized:
                    attrs['physicalCellIdentity'] = val
                elif 'plmnidentity' in normalized:
                    attrs['plmnIdentity'] = val
                elif 'lac' == normalized or 'lac ' in normalized:
                    attrs['lac'] = val
                elif 'rac' in normalized:
                    attrs['rac'] = val
                elif 'rimcapable' in normalized:
                    attrs['rimCapable'] = val
                elif 'srvcccapability' in normalized or 'srvcc' in normalized:
                    attrs['srvccCapability'] = val
                elif 'userlabel' in normalized:
                    attrs['userLabel'] = val
                elif 'isremoveallowed' in normalized:
                    attrs['isRemoveAllowed'] = val
                elif 'lbutrancelloffloadcapacity' in normalized or 'lbUtranCellOffloadCapacity'.lower() in normalized:
                    attrs['lbUtranCellOffloadCapacity'] = val

            # frecuencia asociada: si tenemos col_map
            freq_id = col_map.get(col_index, "")
            results.append({
                'ext_id': ext,
                'col_index': col_index,
                'attrs': attrs,
                'freq_id': freq_id
            })

    return results


def _extract_utran_freq_relations(df_eq: pd.DataFrame) -> List[Dict]:
    """
    Extrae UtranFreqRelation: devuelve lista de relaciones por columna:
    cada item: {'eutran_cell': <str>, 'utran_freq': <str>, 'attrs': {attr: value, ...}, 'allowed_plmns': [...]}
    """
    if df_eq is None:
        return []

    rows = df_eq[df_eq['MO'].astype(str).str.strip() == 'UtranFreqRelation']
    if rows.empty:
        return []

    # encontrar row que tenga el encabezado con ENodeBFunction=1,EUtranCellFDD=
    header_row = None
    for idx, val in rows['Atributo'].astype(str).items():
        if val.strip().startswith('ENodeBFunction=1,EUtranCellFDD='):
            header_row = rows.loc[idx]
            break
    if header_row is None:
        return []

    # localizar index de Atributo
    try:
        atributo_index = list(df_eq.columns).index('Atributo')
    except ValueError:
        atributo_index = 0
    first_value_col = atributo_index + 1

    # obtener fila que contiene 'UtranFreqRelation=' para obtener freq por columna
    ufr_row = None
    for idx, val in rows['Atributo'].astype(str).items():
        if val.strip().startswith('UtranFreqRelation='):
            ufr_row = rows.loc[idx]
            break

    relations = []
    # atributos que nos interesan (orden aproximado)
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

        # si utran_freq vacío, saltar (no queremos crear relaciones con nan)
        if not utran_freq:
            continue

        attrs = {}
        for attr in core_attrs:
            # buscar fila exacta con Atributo == attr
            matches = rows[rows['Atributo'].astype(str).str.strip() == attr]
            if not matches.empty:
                try:
                    v = str(matches.iloc[0].iloc[col_index]).strip()
                    if v and v.lower() not in ('nan', 'vacio', ''):
                        attrs[attr] = v
                except Exception:
                    continue

        # allowedPlmnList
        allowed_plmns = []
        try:
            mcc_row = rows[rows['Atributo'].astype(str).str.strip().str.contains('allowedPlmnList_mcc', na=False)].iloc[0]
            mnc_row = rows[rows['Atributo'].astype(str).str.strip().str.contains('allowedPlmnList_mnc', na=False)].iloc[0]
            mncLen_row = rows[rows['Atributo'].astype(str).str.strip().str.contains('allowedPlmnList_mncLength', na=False)].iloc[0]

            mcc_vals = str(mcc_row.iloc[col_index]).strip().split()
            mnc_vals = str(mnc_row.iloc[col_index]).strip().split()
            mncLen_vals = str(mncLen_row.iloc[col_index]).strip().split()

            for triple in zip(mcc_vals, mnc_vals, mncLen_vals):
                if triple[0] and triple[1]:
                    allowed_plmns.append((triple[0], triple[1], triple[2] if len(triple) > 2 else '2'))
        except Exception:
            allowed_plmns = []

        relations.append({
            'eutran_cell': eutran_cell,
            'utran_freq': utran_freq,
            'attrs': attrs,
            'allowed_plmns': allowed_plmns,
            'col_index': col_index
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
            label = f.get('userLabel', '').strip()

            if not fid:
                continue
            body_lines.append(f" cr  ENodeBFunction=1,UtraNetwork=1,UtranFrequency={fid}")
            if arfcn:
                body_lines.append(f"{arfcn} #arfcnValueUtranDl")
            # SET userLabel con formato del ejemplo (uso del $)
            if label:
                body_lines.append(f" set    ENodeBFunction=1,UtraNetwork=1,UtranFrequency={fid}$ userLabel  {label}")
            body_lines.append("")  # separación
    else:
        body_lines.append("// No se encontraron UtranFrequency en el RND -> Ninguna frecuencia UTRAN creada")
        body_lines.append("")

    # 2) Crear UtranFreqRelation por cada EUtranCellFDD (cr ... y sets)
    if relations:
        for rel in relations:
            eutran = rel['eutran_cell']
            utran = rel['utran_freq']
            attrs = rel.get('attrs', {})

            if not eutran or not utran:
                continue

            body_lines.append(f" cr  ENodeBFunction=1,EUtranCellFDD={eutran},UtranFreqRelation={utran}")
            # línea con referencia a UtraNetwork y UtranFrequency (formato exacto)
            body_lines.append(f" UtraNetwork=1,UtranFrequency={utran}   #utranFrequencyRef")
            # cellReselectionPriority como línea aparte si existe
            cr_priority = attrs.get('cellReselectionPriority', '')
            if cr_priority:
                body_lines.append(f"{cr_priority}   #cellReselectionPriority        ")

            # ahora los SETs en orden fijo (omitimos cellReselectionPriority)
            # queremos mantener el orden: anrMeasOn, connectedMode..., etc. Usamos attrs dict
            # iteramos ordenado por keys para dar estabilidad pero preferimos el orden 'attrs' anterior si existe
            ordered_keys = [
                'anrMeasOn','connectedModeMobilityPrio','csFallbackPrio','csFallbackPrioEC','lbBnrPolicy',
                'mobilityAction','mobilityActionCsfb','pMaxUtra','qOffsetFreq','qQualMin','qRxLevMin','threshXHigh',
                'threshXHighQ','threshXLow','threshXLowQ','userLabel','utranFreqToQciProfileRelation','voicePrio',
                'altCsfbTargetPrio','altCsfbTargetPrioEc','b2Thr1RsrpUtraFreqOffset','b2Thr1RsrqUtraFreqOffset',
                'b2Thr2EcNoUtraFreqOffset','b2Thr2RscpUtraFreqOffset','atoAllowed'
            ]
            for k in ordered_keys:
                if k == 'cellReselectionPriority':
                    continue
                v = attrs.get(k, "")
                if v is None:
                    continue
                vstr = str(v).strip()
                # si es userLabel y está vacío, replicamos el comportamiento del ejemplo (set ... userLabel  )
                if k == 'userLabel' and vstr == "":
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
            # si freq vacío, intentar deducir: buscar numero ARFCN en attrs.cellIdentity si contiene cId etc.
            if not freq:
                # fallback: si extid tiene patrón... intentar deducir por parte del extid (no siempre fiable)
                # preferimos dejar freq vacío si no se detecta
                pass

            body_lines.append(f" crn  ENodeBFunction=1,UtraNetwork=1,UtranFrequency={freq},ExternalUtranCellFDD={extid}")
            # cellIdentity
            cellIdentity = attrs.get('cellIdentity', '')
            if cellIdentity:
                body_lines.append(f"cellIdentity {cellIdentity}")
            else:
                # intentar extraer cId,rncId desde el extid si viene formato conocido (último segmento es CID)
                parts = extid.split('-')
                if len(parts) >= 3:
                    cid = parts[-1]
                    rnc = parts[-2]
                    body_lines.append(f"cellIdentity cId={cid},rncId={rnc}")
                else:
                    body_lines.append("cellIdentity ")
            # isRemoveAllowed
            isRemove = attrs.get('isRemoveAllowed', 'false')
            if isRemove == '':
                isRemove = 'false'
            body_lines.append(f"isRemoveAllowed {isRemove}")
            # lac
            lac = attrs.get('lac', '')
            if lac:
                body_lines.append(f"lac {lac}")
            else:
                # si no existe, poner default si deseas, por ahora dejamos vacío como en ejemplo
                body_lines.append("lac ")
            # lbUtranCellOffloadCapacity
            lbcap = attrs.get('lbUtranCellOffloadCapacity', '')
            if not lbcap:
                lbcap = '1000'
            body_lines.append(f"lbUtranCellOffloadCapacity {lbcap}")
            # masterUtranCellId (vacío en ejemplo)
            body_lines.append("masterUtranCellId ")
            # physicalCellIdentity
            phys = attrs.get('physicalCellIdentity', attrs.get('physicalCellIdentity', ''))
            if phys:
                body_lines.append(f"physicalCellIdentity {phys}")
            else:
                body_lines.append("physicalCellIdentity ")
            # plmnIdentity
            plmn = attrs.get('plmnIdentity', '')
            if plmn:
                # si ya está en formato mcc=...,mnc=..., usamos directo
                body_lines.append(f"plmnIdentity {plmn}")
            else:
                # default ejemplo (730/1/2) si no existe, pero mejor dejar vacío o colocar tu valor base
                body_lines.append("plmnIdentity mcc=730,mnc=1,mncLength=2")
            # rac
            rac = attrs.get('rac', '')
            if rac:
                body_lines.append(f"rac {rac}")
            else:
                body_lines.append("rac ")
            # rimCapable
            rim = attrs.get('rimCapable', '')
            if not rim:
                rim = '0'
            body_lines.append(f"rimCapable {rim}")
            # srvccCapability
            srvcc = attrs.get('srvccCapability', '')
            if not srvcc:
                srvcc = '1'
            body_lines.append(f"srvccCapability {srvcc}")
            # userLabel
            userlabel = attrs.get('userLabel', '')
            body_lines.append(f"userLabel {userlabel}")
            body_lines.append("")  # línea vacía entre atributos (el ejemplo tiene blank line before end)
            body_lines.append("end")
            body_lines.append("")  # separación entre bloques

    # 4) UtranCellRelation blocks (mapping EUtranCellFDD -> ExternalUtranCellFDD)
    # Buscamos por cada relation si en la misma columna (col_index) existen external cells detectadas -> crear UtranCellRelation blocks
    if relations and external_cells:
        # mapear ext by column para búsqueda rápida
        ext_by_col = {}
        for ext in external_cells:
            ext_by_col.setdefault(ext['col_index'], []).append(ext)

        for rel in relations:
            eutran = rel['eutran_cell']
            utran = rel['utran_freq']
            col_index = rel.get('col_index')
            if col_index is None:
                continue
            exts_here = ext_by_col.get(col_index, [])
            for ext in exts_here:
                extid = ext['ext_id']
                # bloque crn tipo EUtranCellFDD ... UtranCellRelation=extid
                body_lines.append(f" crn  ENodeBFunction=1,EUtranCellFDD={eutran},UtranFreqRelation={utran},UtranCellRelation={extid}")
                body_lines.append("coverageIndicator 0")
                body_lines.append(f"externalUtranCellFDDRef UtraNetwork=1,UtranFrequency={utran},ExternalUtranCellFDD={extid}")
                body_lines.append("isHoAllowed true")
                body_lines.append("isRemoveAllowed true")
                body_lines.append("lbBnrAllowed true")
                body_lines.append("lbCovIndicated false")
                body_lines.append("loadBalancing 0")
                body_lines.append("end")
                body_lines.append("")  # separación

    # 5) allowedPlmnList (global) si existe en relations
    all_allowed = []
    for r in relations:
        for triple in r.get('allowed_plmns', []):
            if triple not in all_allowed:
                all_allowed.append(triple)
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
// == UTRAN RELATION - GENERADO AUTOMATICAMENTE
// ====================================================================
// AUTOR: Macro_App
// FECHA: {current_date}
// NEMONICO: {nemonico_upper}
// NOTA: Generado desde Equipment-Configuration (RND)
//
//"""
    return signature + final
