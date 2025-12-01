# functions/eutran_relation_generator.py
"""
Generador para EUtranRelation (.mos)
Lectura robusta del RND (lee todas las hojas) y generación dinámica
de las 3 secciones:
 - EUtranFrequency
 - EUtranFreqRelation
 - EUtranCellRelation

Función pública:
    generate_eutran_relation_mos(rnd_file_xlsx, nemonico, release) -> str
"""
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd

TARGET_MOS = ("EUtranFrequency", "EUtranFreqRelation", "EUtranCellRelation")


# -------------------- UTILIDADES DE LECTURA / NORMALIZACIÓN --------------------

def _read_all_rows_from_excel(rnd_file_xlsx: Any) -> List[List[Any]]:
    """Lee todas las hojas del Excel y devuelve una lista de filas (listas)."""
    try:
        excel = pd.read_excel(rnd_file_xlsx, sheet_name=None, header=None, engine="openpyxl")
    except Exception as e:
        raise RuntimeError(f"Error al leer RND Excel: {e}")

    rows: List[List[Any]] = []
    for sheet_name, df in excel.items():
        for _, r in df.iterrows():
            if r.isna().all():
                continue
            rows.append(list(r.values))
    return rows


def _normalize_cell_value(v):
    """Normaliza valor de celda a string ('' si NaN)."""
    if pd.isna(v):
        return ""
    # Aseguramos que los valores numéricos se manejen correctamente como strings
    if isinstance(v, (int, float)):
        # Si es un número entero como 1.0, lo convierte a '1'
        if v == int(v):
            s = str(int(v))
        else:
            s = str(v)
    else:
        s = str(v)
        
    return s.replace("\r", " ").replace("\n", " ").replace("\t", " ").strip()


def _collect_mo_attributes(rows: List[List[Any]]) -> Dict[str, Dict[str, List[str]]]:
    """
    Construye data[MO][attribute] = [val1, val2, ...]
    Solo guarda MO en TARGET_MOS (para eficiencia y claridad).
    """
    data: Dict[str, Dict[str, List[str]]] = {}
    for row in rows:
        if len(row) < 2:
            continue
        mo = _normalize_cell_value(row[0])
        if not mo or mo not in TARGET_MOS:
            continue
        attr = _normalize_cell_value(row[1])
        vals = [_normalize_cell_value(c) for c in row[2:]]
        if mo not in data:
            data[mo] = {}
        data[mo][attr] = vals
    return data


def _safe_get_col_length(*lists_of_vals: List[List[str]]) -> int:
    """Longitud máxima entre listas dadas."""
    maxlen = 0
    for l in lists_of_vals:
        if l:
            maxlen = max(maxlen, len(l))
    return maxlen


def _val_at(vals: List[str], idx: int) -> str:
    """Retorna valor seguro en índice o ''."""
    if not vals or idx < 0 or idx >= len(vals):
        return ""
    return vals[idx]


# -------------------- ORDENES DE SET (PARA SALIDA CONSISTENTE) --------------------

EUTRANFREQRELATION_SET_ORDER = [
    "allowedMeasBandwidth",
    "anrMeasOn",
    "cellReselectionPriority",
    "connectedModeMobilityPrio",
    "createdBy",
    "eutranFreqToQciProfileRelation",  # trato especial
    "interFreqMeasType",
    "lbActivationThreshold",
    "lbBnrPolicy",
    "mobilityAction",
    "neighCellConfig",
    "pMax",
    "presenceAntennaPort1",
    "qOffsetFreq",
    "qQualMin",
    "qRxLevMin",
    "threshXHigh",
    "threshXHighQ",
    "threshXLow",
    "threshXLowQ",
    "tReselectionEutra",
    "tReselectionEutraSfHigh",
    "tReselectionEutraSfMedium",
    "userLabel",
    "voicePrio",
    "caTriggeredRedirectionActive",
    "arpPrio",
    "nonPlannedPhysCellId",
    "nonPlannedPhysCellIdRange",
    "nonPlannedPciCIO",
    "nonPlannedPciTargetIdType",
    "a5Thr1RsrpFreqOffset",
    "a5Thr1RsrqFreqOffset",
    "a5Thr2RsrpFreqOffset",
    "a5Thr2RsrqFreqOffset",
    "atoAllowed",
    "cellSleepCovCellMeasOn",
    "csgCellTargetIdType",
    "csgPhysCellId",
    "csgPhysCellIdRange",
    "hybridCsgPhysCellId",
    "hybridCsgPhysCellIdRange",
    "interFreqMeasTypeUlSinr",
    "caFreqPriority",
    "endcAwareIdleModePriority",
    "caFreqProportion",
    "asmHitRateAddThreshold",
    "asmHitRateRemoveThreshold",
    "asmSCellDetection",
    "endcHoFreqPriority",
]

EUTRANCELLRELATION_SET_ORDER = [
    "cellIndividualOffsetEUtran",
    "coverageIndicator",
    "lbBnrAllowed",
    "includeInSystemInformation",
    "isHoAllowed",
    "loadBalancing",
    "qOffsetCellEUtran",
    "sCellCandidate",
    "lbCovIndicated",
    "sleepModeCovCellCandidate",
    "crsAssistanceInfoPriority",
    "isRemoveAllowed",
    "amoAllowed",
    "asmSCellDlOnlyAllowed",
]


# -------------------- LECTURA HOJA NODE (VALORES PARA QCI) --------------------

def _read_node_sheet_values(rnd_file_xlsx: Any) -> Dict[str, str]:
    """
    Lee la hoja 'Node' y devuelve:
      - ENodeBFunction (valor simple, p.e. '1' o 'zzzTemporary86')
      - QciTable
      - QciProfilePredefined
    """
    out = {"ENodeBFunction": "", "QciTable": "", "QciProfilePredefined": ""}

    try:
        df_node = pd.read_excel(rnd_file_xlsx, sheet_name='Node', header=None, engine="openpyxl")
    except Exception:
        return out # Retorna vacío para que se usen los defaults

    # Recorremos fila por fila y analizamos columnas 0..n buscando combinaciones:
    for _, row in df_node.iterrows():
        # Convertir a lista de strings y limpiar
        vals = [_normalize_cell_value(x) for x in row.tolist()]

        # Caso preferente (formato de la imagen: MO | Atributo | Valor)
        if len(vals) >= 3:
            mo = vals[0].strip().lower()
            attr = vals[1].strip().lower()
            third = vals[2].strip()
            
            # Busca ENodeBFunction en el formato de 3 columnas
            if mo == "enodebfunction" and "enodebfunction=" in attr:
                if third:
                    out["ENodeBFunction"] = third
                    continue

        # Detección tolerante para QCI/Perfiles
        for i, cell in enumerate(vals):
            if not cell: continue
            low = cell.lower()
            
            # QciTable detection
            if "qcitable" in low or "qci table" in low or low == "qci_table":
                # Si está en el formato 'QciTable=default' en una celda
                if "=" in cell:
                    right = cell.split("=", 1)[1].strip()
                    if right: out["QciTable"] = right
                # Si está en dos celdas 'QciTable' | 'default'
                elif i + 1 < len(vals) and vals[i + 1]:
                    out["QciTable"] = vals[i + 1].strip()
                continue

            # QciProfilePredefined detection
            if "qciprofilepredefined" in low.replace(" ", "") or "qci profile predefined" in low:
                if "=" in cell:
                    right = cell.split("=", 1)[1].strip()
                    if right: out["QciProfilePredefined"] = right
                elif i + 1 < len(vals) and vals[i + 1]:
                    out["QciProfilePredefined"] = vals[i + 1].strip()
                continue
                
    # defaults si no se encontró nada explícito
    if not out["ENodeBFunction"]:
        out["ENodeBFunction"] = "1"
    if not out["QciTable"]:
        out["QciTable"] = "default"
    if not out["QciProfilePredefined"]:
        out["QciProfilePredefined"] = "qci6"

    return out


# -------------------- GENERADOR PRINCIPAL --------------------

def generate_eutran_relation_mos(rnd_file_xlsx: Any, nemonico: str, release: str) -> str:
    """
    Genera el contenido .mos para EUtranRelation a partir del archivo RND.
    rnd_file_xlsx puede ser un buffer (UploadedFile) o ruta.
    """
    # 1) Leer RND
    rows = _read_all_rows_from_excel(rnd_file_xlsx)

    # 2) Extraer MO/atributos
    data = _collect_mo_attributes(rows)

    # 2.b) Node values (para qciProfileRef -> ENodeBFunction real)
    node_vals = _read_node_sheet_values(rnd_file_xlsx)
    
    # Usar el valor limpio directamente de la función
    enodeb_value = node_vals.get("ENodeBFunction", "1")
    qci_table_val = node_vals.get("QciTable", "default")
    qci_profile_predef = node_vals.get("QciProfilePredefined", "qci6")
    
    # 3) Conteos + header
    dt_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nem = nemonico.upper() if nemonico else "NEMONICO"
    release_str = release or ""

    # contar EUtranFrequency (basado en fila header que contiene EUtraNetwork/EUtranFrequency)
    eu_freq_header_vals: List[str] = []
    if "EUtranFrequency" in data:
        for attr in data["EUtranFrequency"].keys():
            low = attr.lower()
            if "eutranfrequency" in low or "eutranetwork" in low or ("eutran" in low and "frequency" in low):
                eu_freq_header_vals = data["EUtranFrequency"].get(attr, [])
                break
        if not eu_freq_header_vals:
            eu_freq_header_vals = next(iter(data["EUtranFrequency"].values()))
    count_freq = len([v for v in eu_freq_header_vals if v != ""])

    # contar EUtranFreqRelation (basado en header cells)
    freqrel_cell_header = []
    if "EUtranFreqRelation" in data:
        for attr in data["EUtranFreqRelation"].keys():
            low = attr.lower()
            if "enodebfunction" in low or "eutrancellfdd" in low or "eutranCellFDD" in attr:
                freqrel_cell_header = data["EUtranFreqRelation"].get(attr, [])
                break
        if not freqrel_cell_header:
            freqrel_cell_header = next(iter(data["EUtranFreqRelation"].values()))
    count_freqrel = len([v for v in freqrel_cell_header if v != ""])

    # contar EUtranCellRelation (basado en EUtranCellRelation= row)
    cellrel_ids = []
    if "EUtranCellRelation" in data:
        for k, v in data["EUtranCellRelation"].items():
            if "eutrancellrelation" in k.lower() or "eutranCellRelation" in k:
                cellrel_ids = v
                break
        if not cellrel_ids:
            vals = list(data["EUtranCellRelation"].values())
            if len(vals) >= 3:
                cellrel_ids = vals[2]
    count_cellrel = len([v for v in cellrel_ids if v != ""])

    # HEADER
    lines: List[str] = []
    lines.append("// ====================================================================")
    lines.append("// == Archivo para la creación de EUtranRelation")
    lines.append("// ====================================================================")
    lines.append(f"// NEMONICO: {nem}")
    lines.append(f"// FECHA: {dt_now}")
    lines.append(f"// AUTOR: Piero Ledesma")
    lines.append("//")
    lines.append(f"// ✔ EUtranFrequency encontrados: {count_freq}")
    lines.append(f"// ✔ EUtranFreqRelation encontrados: {count_freqrel}")
    lines.append(f"// ✔ EUtranCellRelation encontrados: {count_cellrel}")
    lines.append("// ====================================================================")
    lines.append("")
    lines.append("confb+")
    lines.append("gs+")
    lines.append("")

    # -------------------- EUtranFrequency --------------------
    lines.append("// ========== EUtranFrequency ==========")
    if "EUtranFrequency" not in data or not data["EUtranFrequency"]:
        lines.append("// No se encontraron EUtranFrequency")
        lines.append("")
    else:
        # seleccionar header attr que contiene EUtraNetwork/EUtranFrequency
        freq_header_attr = None
        for attr in data["EUtranFrequency"].keys():
            low = attr.lower()
            if "eutranfrequency" in low or "eutranetwork" in low or ("eutran" in low and "frequency" in low):
                freq_header_attr = attr
                break
        if freq_header_attr is None:
            freq_header_attr = list(data["EUtranFrequency"].keys())[0]

        freq_ids = data["EUtranFrequency"].get(freq_header_attr, [])
        arfcn_vals = data["EUtranFrequency"].get("arfcnValueEUtranDl", []) or data["EUtranFrequency"].get("arfcnValueEutranDl", [])
        # iterar frecuencias
        for idx in range(len(freq_ids)):
            freq_id = _val_at(freq_ids, idx)
            if not freq_id:
                continue
            lines.append(f"cr  ENodeBFunction=1,EUtraNetwork=1,EUtranFrequency={freq_id}")
            # imprimir arfcn si existe
            arfcn = _val_at(arfcn_vals, idx)
            if arfcn:
                lines.append(f"{arfcn} #arfcnValueEUtranDl")
            # imprimir sets para otros atributos (omitir freqBand siempre)
            for attr, vals in data["EUtranFrequency"].items():
                if attr == freq_header_attr or attr.lower().startswith("arfcn") or "freqband" in attr.lower():
                    continue
                val = _val_at(vals, idx)
                if val == "":
                    continue
                set_attr = attr.strip()
                lines.append(f" set   ENodeBFunction=1,EUtraNetwork=1,EUtranFrequency={freq_id} {set_attr} {val}")
            lines.append("")

    # preparar conjunto de ids de EUtranFrequency para mapeos en EUtranFreqRelation
    eu_freq_id_set = set([v for v in eu_freq_header_vals if v != ""])

    # -------------------- EUtranFreqRelation --------------------
    lines.append("// ========== EUtranFreqRelation ==========")
    if "EUtranFreqRelation" not in data or not data["EUtranFreqRelation"]:
        lines.append("// No se encontraron EUtranFreqRelation")
        lines.append("")
    else:
        # header: fila con ENodeBFunction=1,EUtranCellFDD= (cells)
        freqrel_cell_header_attr = None
        for attr in data["EUtranFreqRelation"].keys():
            low = attr.lower()
            if "enodebfunction" in low or "eutrancellfdd" in low or "eutranCellFDD" in attr:
                freqrel_cell_header_attr = attr
                break
        if freqrel_cell_header_attr is None:
            freqrel_cell_header_attr = list(data["EUtranFreqRelation"].keys())[0]

        cells = data["EUtranFreqRelation"].get(freqrel_cell_header_attr, [])
        # encontrar attr con ids de EUtranFreqRelation
        freqrel_id_attr = None
        for attr in data["EUtranFreqRelation"].keys():
            if "eutranfreqrelation" in attr.lower() or attr.lower().startswith("eutranfreqrelation"):
                freqrel_id_attr = attr
                break
        if freqrel_id_attr is None:
            for a in data["EUtranFreqRelation"].keys():
                if "eu" in a.lower() and "freq" in a.lower():
                    freqrel_id_attr = a
                    break
        if freqrel_id_attr is None:
            freqrel_id_attr = list(data["EUtranFreqRelation"].keys())[0]
        freqrel_ids = data["EUtranFreqRelation"].get(freqrel_id_attr, [])

        maxcols = _safe_get_col_length(cells, freqrel_ids)
        for idx in range(maxcols):
            cell = _val_at(cells, idx)
            freqrel = _val_at(freqrel_ids, idx)
            if not cell and not freqrel:
                continue
            # cr line
            lines.append(f"cr  ENodeBFunction=1,EUtranCellFDD={cell},EUtranFreqRelation={freqrel}")
            # si freqrel corresponde a una EUtranFrequency existente, agregar la línea de mapping
            if freqrel and freqrel in eu_freq_id_set:
                lines.append(f" ENodeBFunction=1,EUtraNetwork=1,EUtranFrequency={freqrel}")
                # intentar imprimir cellReselectionPriority si existe
                crp_val = ""
                for k in data["EUtranFreqRelation"].keys():
                    if k.strip().lower().startswith("cellreselectionpriority"):
                        crp_val = _val_at(data["EUtranFreqRelation"][k], idx)
                        break
                if crp_val != "":
                    lines.append(f"{crp_val}")

            # Construir sets en orden pedido, omitiendo atributos que no deben imprimirse
            attrs_present = {a: vals for a, vals in data["EUtranFreqRelation"].items()
                             if a not in (freqrel_cell_header_attr, freqrel_id_attr)}

            # Eliminar keys que no deben producir set por formato (ej. EUtranFreqRelationId)
            forbidden_prefixes = ("eutranfreqrelationid", "a5thr1", "a5thr2") 
            keys_to_drop = [k for k in attrs_present.keys() if any(k.strip().lower().startswith(p) for p in forbidden_prefixes)]
            for k in keys_to_drop:
                attrs_present.pop(k, None)

            # producir sets en orden
            for attr_name in EUTRANFREQRELATION_SET_ORDER:
                key_match = None
                for k in list(attrs_present.keys()):
                    if k.strip().lower().startswith(attr_name.lower()):
                        key_match = k
                        break
                if not key_match:
                    continue
                val = _val_at(attrs_present[key_match], idx)
                if val == "":
                    attrs_present.pop(key_match, None)
                    continue

                set_attr = key_match.strip()

                # ----- TRATO ESPECIAL: eutranFreqToQciProfileRelation -----
                if set_attr.lower().startswith("eutranfreqtoqciprofilerelation"):
                    # construir el valor combinando:
                    a5_thr2 = ""
                    a5_thr1 = ""
                    # buscar claves parecidas (case-insensitive)
                    for k2 in list(attrs_present.keys()):
                        kl = k2.strip().lower()
                        if "a5thr2" in kl and "rsrp" in kl:
                            a5_thr2 = _val_at(attrs_present[k2], idx)
                        if "a5thr1" in kl and "rsrp" in kl:
                            a5_thr1 = _val_at(attrs_present[k2], idx)
                    # fallback buscando en el nodo completo
                    if not a5_thr2:
                        for k2, v2 in data["EUtranFreqRelation"].items():
                            if "a5thr2" in k2.strip().lower() and "rsrp" in k2.strip().lower():
                                a5_thr2 = _val_at(v2, idx)
                                break
                    if not a5_thr1:
                        for k2, v2 in data["EUtranFreqRelation"].items():
                            if "a5thr1" in k2.strip().lower() and "rsrp" in k2.strip().lower():
                                a5_thr1 = _val_at(v2, idx)
                                break

                    if a5_thr2 == "":
                        a5_thr2 = "0"
                    if a5_thr1 == "":
                        a5_thr1 = "0"

                    # qciProfileRef se toma del valor limpio de la hoja Node (ENodeBFunction)
                    qci_profile_ref = enodeb_value 
                    qci_table = qci_table_val
                    qci_profile_pre = qci_profile_predef

                    eutran_qci_val = (
                        f"a5Thr2RsrpFreqQciOffset={a5_thr2},"
                        f"a5Thr1RsrpFreqQciOffset={a5_thr1},"
                        f"qciProfileRef=ENodeBFunction={qci_profile_ref},"
                        f"QciTable={qci_table},"
                        f"QciProfilePredefined={qci_profile_pre}"
                    )

                    # Formato EXACTO requerido
                    lines.append(f" set  ENodeBFunction=1,EUtranCellFDD={cell},EUtranFreqRelation={freqrel}$ EUtranFreqToQciProfileRelation {eutran_qci_val}")
                    attrs_present.pop(key_match, None)
                    continue

                # ----- FIN TRATO ESPECIAL -----

                lines.append(f" set  ENodeBFunction=1,EUtranCellFDD={cell},EUtranFreqRelation={freqrel}$ {set_attr} {val}")
                attrs_present.pop(key_match, None)

            # imprimir atributos restantes (evitar imprimir ids y atributos problemáticos)
            for other_attr, vals in sorted(attrs_present.items()):
                val = _val_at(vals, idx)
                if val == "":
                    continue
                set_attr = other_attr.strip()
                low = set_attr.lower()
                # evitar imprimir IDs o atributos formateados incorrectamente
                if low.endswith("id") or "_id" in low:
                    continue
                if "freqband" in low:
                    continue
                # Evitar sub-atributos de QCI duplicados
                if "qci" in low or "profile" in low: 
                    continue
                
                lines.append(f" set  ENodeBFunction=1,EUtranCellFDD={cell},EUtranFreqRelation={freqrel}$ {set_attr} {val}")
            lines.append("")

    # -------------------- EUtranCellRelation --------------------
    lines.append("// ========== EUtranCellRelation ==========")
    if "EUtranCellRelation" not in data or not data["EUtranCellRelation"]:
        lines.append("// No se encontraron EUtranCellRelation")
        lines.append("")
    else:
        # detectar atributos cabecera típicos
        parent_cell_attr = None
        freqrel_attr = None
        cellrelation_attr = None

        for attr in data["EUtranCellRelation"].keys():
            low = attr.lower()
            if "eutrancellfdd" in low or "eutran cellfdd" in low or "eutrancellfdd" in attr:
                parent_cell_attr = parent_cell_attr or attr
            if "eutranfreqrelation" in low or "eutran freq" in low:
                freqrel_attr = freqrel_attr or attr
            if "eutrancellrelation" in low or "eutranCellRelation" in attr:
                cellrelation_attr = cellrelation_attr or attr

        # pick explicit names if no match fino
        for attr in data["EUtranCellRelation"].keys():
            if "EUtranCellFDD" in attr and parent_cell_attr is None:
                parent_cell_attr = attr
            if "EUtranFreqRelation" in attr and freqrel_attr is None:
                freqrel_attr = attr
            if "EUtranCellRelation" in attr and cellrelation_attr is None:
                cellrelation_attr = attr

        keys_list = list(data["EUtranCellRelation"].keys())
        if parent_cell_attr is None and len(keys_list) >= 1:
            parent_cell_attr = keys_list[0]
        if freqrel_attr is None and len(keys_list) >= 2:
            freqrel_attr = keys_list[1]
        if cellrelation_attr is None and len(keys_list) >= 3:
            cellrelation_attr = keys_list[2]

        parents = data["EUtranCellRelation"].get(parent_cell_attr, [])
        freqrels = data["EUtranCellRelation"].get(freqrel_attr, [])
        cellrels = data["EUtranCellRelation"].get(cellrelation_attr, [])

        maxcols = _safe_get_col_length(parents, freqrels, cellrels)

        # neighborCellRef (si existe) para mostrar línea inmediata después del CR
        neighbor_row_key = None
        for k in data["EUtranCellRelation"].keys():
            if k.strip().lower().startswith("neighborcellref"):
                neighbor_row_key = k
                break
        neighbor_vals = data["EUtranCellRelation"].get(neighbor_row_key, []) if neighbor_row_key else []

        for idx in range(maxcols):
            parent = _val_at(parents, idx)
            freqrel = _val_at(freqrels, idx)
            crel = _val_at(cellrels, idx)
            if not (parent or freqrel or crel):
                continue

            # CR line (mantener espacios tal como ejemplo)
            cr_parts = ["ENodeBFunction=1", f"EUtranCellFDD={parent}", f"EUtranFreqRelation={freqrel}", f"EUtranCellRelation={crel}"]
            cr_line = "cr  " + ",".join(cr_parts)
            lines.append(cr_line)

            # neighbor line si aplica (Línea de referencia, NO SET)
            neighbor = _val_at(neighbor_vals, idx)
            if neighbor:
                lines.append(f" EUtranCellFDD={neighbor}")

            # sets: construidos en orden EUTRANCELLRELATION_SET_ORDER (si existen)
            attrs_present = {a: vals for a, vals in data["EUtranCellRelation"].items()
                             if a not in (parent_cell_attr, freqrel_attr, cellrelation_attr)}
            
            # --- CORRECCIÓN FINAL: ELIMINAR neighborCellRef DE LOS SETS ---
            # Si el atributo neighborCellRef se encontró en el RND, lo eliminamos
            # de la lista de atributos para evitar el SET duplicado.
            if neighbor_row_key:
                attrs_present.pop(neighbor_row_key, None)
            # -----------------------------------------------------------------

            # imprimir en orden pedido
            for attr_name in EUTRANCELLRELATION_SET_ORDER:
                key_match = None
                for k in list(attrs_present.keys()):
                    if k.strip().lower().startswith(attr_name.lower()):
                        key_match = k
                        break
                if key_match:
                    val = _val_at(attrs_present[key_match], idx)
                    if val != "":
                        set_attr = key_match.strip()
                        lines.append(f" set {','.join(['ENodeBFunction=1', f'EUtranCellFDD={parent}', f'EUtranFreqRelation={freqrel}', f'EUtranCellRelation={crel}'])}$ {set_attr} {val}")
                    attrs_present.pop(key_match, None)

            # any remaining attrs (stable order)
            for other_attr, vals in sorted(attrs_present.items()):
                val = _val_at(vals, idx)
                if val == "":
                    continue
                set_attr = other_attr.strip()
                low = set_attr.lower()
                if low.endswith("id") or "_id" in low:
                    continue
                lines.append(f" set {','.join(['ENodeBFunction=1', f'EUtranCellFDD={parent}', f'EUtranFreqRelation={freqrel}', f'EUtranCellRelation={crel}'])}$ {set_attr} {val}")
            lines.append("")

    # FOOTER
    lines.append("confb-")
    lines.append("gs-")

    mos_content = "\n".join(lines)
    return mos_content