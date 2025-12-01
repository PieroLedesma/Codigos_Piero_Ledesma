# functions/Gutran_relation_generator.py
"""
Generador dinámico para GUtranRelation (.mos)
Versión corregida para coincidir exactamente con el archivo de referencia.
Función pública:
    generate_gutran_relation_mos(rnd_file_xlsx, nemonico, release) -> str
"""
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd

TARGET_MOS = (
    "GUtranSyncSignalFrequency",
    "GUtranFreqRelation",
    "GUtranCellRelation",
    "ExternalGNodeBFunction",
    "TermPointToGNB",
    "ExternalGUtranCell",
    "GUtraNetwork",
)

GUTRANFREQRELATION_SET_ORDER = [
    "allowedPlmnList",
    "anrMeasOn",
    "b1ThrRsrpFreqOffset",
    "b1ThrRsrqFreqOffset",
    "cellReselectionPriority",
    "connectedModeMobilityPrio",
    "deriveSsbIndexFromCell",
    "endcB1MeasPriority",
    "gUtranSyncSignalFrequencyRef",
    "pMaxNR",
    "qOffsetFreq",
    "qQualMin",
    "qRxLevMin",
    "threshXHigh",
    "threshXHighQ",
    "threshXLow",
    "threshXLowQ",
]

GUTRANCELLRELATION_SET_ORDER = [
    "coverageIndicator",
    "essEnabled",
    "isEndcAllowed",
    "isHoAllowed",
    "isRemoveAllowed",
    "isVoiceHoAllowed",
    "neighborCellRef",
    "userLabel",
]

SKIP_EMPTY_VALUES = {"", "vacio", "Vacio", "Vacio ", "Vacio\t", None}

# -------------------- UTILIDADES --------------------
def _read_all_rows_from_excel(rnd_file_xlsx: Any) -> List[List[Any]]:
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
    if pd.isna(v):
        return ""
    s = str(v).replace("\r", " ").replace("\n", " ").replace("\t", " ").strip()
    return s


def _normalize_for_print(v: str) -> str:
    """Devuelve '' si el valor es considerado vacío; normaliza booleanos a minúsculas."""
    if v is None:
        return ""
    vv = str(v).strip()
    if vv.lower() in ("true", "false"):
        return vv.lower()
    if vv in SKIP_EMPTY_VALUES:
        return ""
    return vv


def _collect_mo_attributes(rows: List[List[Any]]) -> Dict[str, Dict[str, List[str]]]:
    data: Dict[str, Dict[str, List[str]]] = {}
    for row in rows:
        if len(row) < 2:
            continue
        mo_raw = _normalize_cell_value(row[0])
        if not mo_raw:
            continue
        mo_key = None
        for t in TARGET_MOS:
            if t.lower() in mo_raw.lower():
                mo_key = t
                break
        if mo_key is None:
            continue
        attr = _normalize_cell_value(row[1])
        vals = [_normalize_cell_value(c) for c in row[2:]]
        if mo_key not in data:
            data[mo_key] = {}
        data[mo_key][attr] = vals
    return data


def _safe_get_col_length(*lists_of_vals: List[List[str]]) -> int:
    maxlen = 0
    for l in lists_of_vals:
        if l:
            maxlen = max(maxlen, len(l))
    return maxlen


def _val_at(vals: List[str], idx: int) -> str:
    if not vals or idx < 0 or idx >= len(vals):
        return ""
    return vals[idx]


# -------------------- NODE sheet --------------------
def _read_node_sheet_values(rnd_file_xlsx: Any) -> Dict[str, str]:
    out = {"ENodeBFunction": "1", "GUtraNetwork": "1"}
    try:
        df_node = pd.read_excel(rnd_file_xlsx, sheet_name='Node', header=None, engine="openpyxl")
    except Exception:
        return out

    for _, row in df_node.iterrows():
        vals = ["" if pd.isna(x) else str(x).strip() for x in row.tolist()]
        if len(vals) >= 3:
            mo = vals[0].strip().lower()
            attr = vals[1].strip()
            third = vals[2].strip()
            if mo == "enodebfunction" and attr.lower().startswith("enodebfunction="):
                if third:
                    out["ENodeBFunction"] = third
                    break
                else:
                    right = attr.split("=", 1)[1].strip() if "=" in attr else ""
                    if right:
                        out["ENodeBFunction"] = right
                        break
        for i, cell in enumerate(vals):
            if not cell:
                continue
            low = cell.lower()
            if "gutranetwork" in low.replace(" ", ""):
                if "=" in cell:
                    right = cell.split("=", 1)[1].strip()
                    if right:
                        out["GUtraNetwork"] = right
                        break
                if i + 1 < len(vals) and vals[i + 1]:
                    out["GUtraNetwork"] = vals[i + 1].strip()
                    break
    return out


# -------------------- GENERADOR PRINCIPAL --------------------
def generate_gutran_relation_mos(rnd_file_xlsx: Any, nemonico: str, release: str) -> str:
    rows = _read_all_rows_from_excel(rnd_file_xlsx)
    data = _collect_mo_attributes(rows)
    node_vals = _read_node_sheet_values(rnd_file_xlsx)
    enodeb_value = node_vals.get("ENodeBFunction", "1")
    gutra_network_value = node_vals.get("GUtraNetwork", "1")

    dt_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nem = nemonico.upper() if nemonico else "NEMONICO"
    release_str = release or ""

    lines: List[str] = []
    lines.append("confb+      ")
    lines.append("gs+     ")
    lines.append("         ")
    lines.append("")

    # -------------------- GUtraNetwork --------------------
    lines.append(f"cr ENodeBFunction=1,GUtraNetwork={gutra_network_value}")
    lines.append("false ")
    lines.append("")

    # ========================================
    # GUtranSyncSignalFrequency
    # ========================================
    lines.append("")
    lines.append("#########################################")
    lines.append("##### GUtranSyncSignalFrequency #####")
    lines.append("#########################################")
    lines.append("")
    
    # -------------------- GUtranSyncSignalFrequency --------------------
    if "GUtranSyncSignalFrequency" in data:
        gu_sync = data["GUtranSyncSignalFrequency"]
        id_key = None
        for k in gu_sync.keys():
            if "gutransyncsignalfrequencyid" in k.replace(" ", "").lower() or k.strip().lower().startswith("enodebfunction=") or "gutransync" in k.lower() or k.strip().lower().endswith("="):
                id_key = k
                break
        if id_key is None:
            id_key = next(iter(gu_sync.keys()))

        ids = gu_sync.get(id_key, [])
        attr_keys = [k for k in gu_sync.keys() if k != id_key]

        for idx in range(len(ids)):
            id_val = _val_at(ids, idx)
            if not _normalize_for_print(id_val):
                continue
            lines.append(f"crn ENodeBFunction=1,GUtraNetwork={gutra_network_value},GUtranSyncSignalFrequency={id_val}")
            
            for a in attr_keys:
                v = _normalize_for_print(_val_at(gu_sync[a], idx))
                low = a.strip().lower()
                
                if "userlabel" in low:
                    continue
                if v == "":
                    continue
                if ("id" in low and "gutransync" in low) or low.endswith("="):
                    continue

                if "arfcn" in low:
                    lines.append(f"arfcn {v}")
                elif low == "band":
                    lines.append(f"band {v}")
                elif "smtcduration" in low:
                    lines.append(f"smtcDuration {v}")
                elif "smtcoffset" in low:
                    lines.append(f"smtcOffset {v}")
                elif "smtcperiodicity" in low:
                    lines.append(f"smtcPeriodicity {v}")
                elif "smtcscs" in low:
                    lines.append(f"smtcScs {v}")
            
            lines.append(f"userLabel ")
            lines.append("end")
            lines.append("")

    # ========================================
    # GUtranFreqRelation
    # ========================================
    lines.append("")
    lines.append("#########################################")
    lines.append("##### GUtranFreqRelation #####")
    lines.append("#########################################")
    lines.append("")
    
    # -------------------- GUtranFreqRelation (crn + set) --------------------
    if "GUtranFreqRelation" in data:
        attrs_map = data["GUtranFreqRelation"]
        cell_key = None
        freqrel_key = None
        for k in attrs_map.keys():
            kl = k.strip().lower()
            if "eutrancellfdd" in kl or ("eutran" in kl and "cell" in kl):
                cell_key = k
            if "gutranfreqrelation" in kl or (kl.endswith("=") and "freq" in kl):
                freqrel_key = k
        keys_list = list(attrs_map.keys())
        if cell_key is None and len(keys_list) >= 1:
            cell_key = keys_list[0]
        if freqrel_key is None and len(keys_list) >= 2:
            freqrel_key = keys_list[1]

        cells = attrs_map.get(cell_key, [])
        freqrels = attrs_map.get(freqrel_key, [])

        maxcols = _safe_get_col_length(cells, freqrels)
        for idx in range(maxcols):
            cell = _val_at(cells, idx)
            freqrel = _val_at(freqrels, idx)
            if not (cell or freqrel):
                continue
            
            # CRN block
            lines.append(f"crn ENodeBFunction=1,EUtranCellFDD={cell},GUtranFreqRelation={freqrel}")
            lines.append("allowedPlmnList ")
            
            attrs_present = {a: vals for a, vals in attrs_map.items() if a not in (cell_key, freqrel_key)}
            for attr_name in GUTRANFREQRELATION_SET_ORDER[1:]:  # Skip allowedPlmnList ya impreso
                key_match = None
                for k in list(attrs_present.keys()):
                    if k.strip().lower().startswith(attr_name.lower()):
                        key_match = k
                        break
                if key_match:
                    v = _normalize_for_print(_val_at(attrs_present[key_match], idx))
                    if v != "":
                        lowk = key_match.strip().lower()
                        if not (("gutranfreqrelation" in lowk) or (lowk.endswith("id") and "gUtranFreqRelation" in key_match)):
                            lines.append(f"{key_match.strip()} {v}")
                    attrs_present.pop(key_match, None)
            
            lines.append("end")
            lines.append("")

            # SET block
            attrs_present = {a: vals for a, vals in attrs_map.items() if a not in (cell_key, freqrel_key)}
            
            for attr_name in GUTRANFREQRELATION_SET_ORDER:
                key_match = None
                for k in list(attrs_present.keys()):
                    if k.strip().lower().startswith(attr_name.lower()):
                        key_match = k
                        break
                
                if attr_name == "allowedPlmnList":
                    val_to_print = ""
                    if key_match:
                        val_to_print = _normalize_for_print(_val_at(attrs_present[key_match], idx))
                        attrs_present.pop(key_match, None)
                    lines.append(f"set ENodeBFunction=1,EUtranCellFDD={cell},GUtranFreqRelation={freqrel} allowedPlmnList {val_to_print}")
                    continue

                if attr_name == "gUtranSyncSignalFrequencyRef":
                    val_to_print = ""
                    if key_match:
                        val_to_print = _normalize_for_print(_val_at(attrs_present[key_match], idx))
                        attrs_present.pop(key_match, None)
                    lines.append(f"set ENodeBFunction=1,EUtranCellFDD={cell},GUtranFreqRelation={freqrel} gUtranSyncSignalFrequencyRef {val_to_print}")
                    continue

                if key_match:
                    v = _normalize_for_print(_val_at(attrs_present[key_match], idx))
                    if v != "":
                        lines.append(f"set ENodeBFunction=1,EUtranCellFDD={cell},GUtranFreqRelation={freqrel} {key_match.strip()} {v}")
                    attrs_present.pop(key_match, None)
            
            lines.append("")

    lines.append(" ")
    lines.append(" ")
    lines.append(" ")

    # ========================================
    # ExternalGNodeBFunction
    # ========================================
    lines.append("")
    lines.append("#########################################")
    lines.append("##### ExternalGNodeBFunction #####")
    lines.append("#########################################")
    lines.append("")
    
    # -------------------- ExternalGNodeBFunction --------------------
    if "ExternalGNodeBFunction" in data:
        ext_map = data["ExternalGNodeBFunction"]
        first_key = next(iter(ext_map.keys()))
        ids = ext_map[first_key]
        for idx in range(len(ids)):
            ext_id = _val_at(ids, idx)
            if not _normalize_for_print(ext_id):
                continue
            lines.append(f"crn ENodeBFunction=1,GUtraNetwork={gutra_network_value},ExternalGNodeBFunction={ext_id}")
            
            mcc = ""
            mnc = ""
            mnc_len = ""
            
            for k, vals in ext_map.items():
                low = k.strip().lower()
                val = _normalize_for_print(_val_at(vals, idx))
                if "gnodebplmnid_mcc" in low:
                    mcc = val
                elif "gnodebplmnid_mnc" in low and "length" not in low:
                    mnc = val
                elif "gnodebplmnid_mnclength" in low:
                    mnc_len = val
            
            for a, vlist in ext_map.items():
                v = _normalize_for_print(_val_at(vlist, idx))
                low = a.strip().lower()
                
                if "gnodebplmnid" in low:
                    continue
                if v == "":
                    continue
                if "externalgnodebfunction" in low and (v == ext_id or v == ""):
                    continue
                
                if "gnodebidlength" in low:
                    lines.append(f"gNodeBIdLength {v}")
                elif "gnodebid" in low and "length" not in low:
                    lines.append(f"gNodeBId {v}")
                elif "userlabel" in low:
                    continue
                else:
                    if "externalgnodebfunction" in low and "id" in low:
                        continue
                    lines.append(f"{a.strip()} {v}")
            
            if mcc and mnc and mnc_len:
                lines.append(f"gNodeBPlmnId mcc={mcc},mnc={mnc},mncLength={mnc_len}")
            
            user_label_key = next((k for k in ext_map.keys() if k.strip().lower() == "userlabel"), None)
            if user_label_key:
                v = _normalize_for_print(_val_at(ext_map[user_label_key], idx))
                lines.append(f"userLabel {v}")
            
            lines.append("end")
            lines.append("")

    # ========================================
    # TermPointToGNB
    # ========================================
    lines.append("")
    lines.append("#########################################")
    lines.append("##### TermPointToGNB #####")
    lines.append("#########################################")
    lines.append("")
    
    # -------------------- TermPointToGNB --------------------
    if "TermPointToGNB" in data:
        tp_map = data["TermPointToGNB"]
        first_key = next(iter(tp_map.keys()))
        ids = tp_map[first_key]
        for idx in range(len(ids)):
            tp_id = _val_at(ids, idx)
            if not _normalize_for_print(tp_id):
                continue
            lines.append(f"crn ENodeBFunction=1,GUtraNetwork={gutra_network_value},ExternalGNodeBFunction={tp_id},TermPointToGNB={tp_id}")
            
            for a, vlist in tp_map.items():
                v = _normalize_for_print(_val_at(vlist, idx))
                low = a.strip().lower()
                if "termpointtognb" in low:
                    continue
                if "administrativestate" in low or "operationalstate" in low:
                    if v != "":
                        lines.append(f"{a.strip()} {v}")
            
            domain_found = False
            ip_found = False
            for a, vlist in tp_map.items():
                low = a.strip().lower()
                if "domainname" in low:
                    domain_found = True
                    v = _normalize_for_print(_val_at(vlist, idx))
                    lines.append(f"domainName {v}")
                elif "ipaddress" in low:
                    ip_found = True
                    v = _normalize_for_print(_val_at(vlist, idx))
                    if v == "":
                        v = "0.0.0.0"
                    lines.append(f"ipAddress {v}")
            
            if not domain_found:
                lines.append("domainName ")
            if not ip_found:
                lines.append("ipAddress 0.0.0.0")
            
            lines.append("end")
            lines.append("")

    # ========================================
    # ExternalGUtranCell
    # ========================================
    lines.append("")
    lines.append("#########################################")
    lines.append("##### ExternalGUtranCell #####")
    lines.append("#########################################")
    lines.append("")
    
    # -------------------- ExternalGUtranCell --------------------
    if "ExternalGUtranCell" in data:
        extcell_map = data["ExternalGUtranCell"]
        
        # Buscar la clave que contiene "ExternalGUtranCell=" (los IDs únicos)
        id_key = None
        for k in extcell_map.keys():
            k_stripped = k.strip()
            # Buscar la clave que es exactamente "ExternalGUtranCell=" o termina con "ExternalGUtranCell="
            if k_stripped == "ExternalGUtranCell=" or k_stripped.endswith("ExternalGUtranCell="):
                id_key = k
                break
        
        # Si no encontramos la clave específica, buscar cualquiera que contenga "ExternalGUtranCell="
        if id_key is None:
            for k in extcell_map.keys():
                if "ExternalGUtranCell=" in k:
                    id_key = k
                    break
        
        # Fallback: usar la primera clave
        if id_key is None:
            id_key = next(iter(extcell_map.keys()))
        
        ids = extcell_map[id_key]
        
        ext_gnb_id = ""
        plmn_mcc = ""
        plmn_mnc = ""
        plmn_mnc_len = ""
        
        if "ExternalGNodeBFunction" in data:
            ext_map = data["ExternalGNodeBFunction"]
            first_ext_key = next(iter(ext_map.keys()))
            ext_ids = ext_map[first_ext_key]
            if ext_ids:
                ext_gnb_id = _val_at(ext_ids, 0)
            
            # Extraer plmnId de ExternalGNodeBFunction
            for k, vals in ext_map.items():
                low = k.strip().lower()
                val = _normalize_for_print(_val_at(vals, 0))
                if "gnodebplmnid_mcc" in low:
                    plmn_mcc = val
                elif "gnodebplmnid_mnc" in low and "length" not in low:
                    plmn_mnc = val
                elif "gnodebplmnid_mnclength" in low:
                    plmn_mnc_len = val
        
        for idx in range(len(ids)):
            extcell_id = _val_at(ids, idx)
            if not _normalize_for_print(extcell_id):
                continue
            
            lines.append(f"crn ENodeBFunction=1,GUtraNetwork={gutra_network_value},ExternalGNodeBFunction={ext_gnb_id},ExternalGUtranCell={extcell_id}")
            
            # Buscar valores en el Excel o usar defaults
            abs_subframe = "0"
            abs_time = "0"
            gutran_sync_ref = ""
            is_remove = "true"
            local_cell = "7"
            plmn_list_override = ""
            
            for a, vlist in extcell_map.items():
                v = _normalize_for_print(_val_at(vlist, idx))
                low = a.strip().lower()
                if "abssubframeoffset" in low and v != "":
                    abs_subframe = v
                elif "abstimeoffset" in low and v != "":
                    abs_time = v
                elif ("gutransyncsignal" in low or "gutransync" in low) and v != "":
                    gutran_sync_ref = v
                elif "isremoveallowed" in low and v != "":
                    is_remove = v
                elif "localcellid" in low and v != "":
                    local_cell = v
                elif "plmnidlist" in low and v != "":
                    plmn_list_override = v
            
            # Imprimir en orden específico
            lines.append(f"absSubFrameOffset {abs_subframe}")
            lines.append(f"absTimeOffset {abs_time}")
            if gutran_sync_ref:
                lines.append(f"gUtranSyncSignalFrequencyRef {gutran_sync_ref}")
            lines.append(f"isRemoveAllowed {is_remove}")
            lines.append(f"localCellId {local_cell}")
            
            # plmnIdList: usar override del Excel o construir desde ExternalGNodeBFunction
            if plmn_list_override:
                lines.append(f"plmnIdList {plmn_list_override}")
            elif plmn_mcc and plmn_mnc and plmn_mnc_len:
                lines.append(f"plmnIdList mcc={plmn_mcc},mnc={plmn_mnc},mncLength={plmn_mnc_len}")
            
            lines.append("end")
            lines.append("")

    # ========================================
    # GUtranCellRelation
    # ========================================
    lines.append("")
    lines.append("#########################################")
    lines.append("##### GUtranCellRelation #####")
    lines.append("#########################################")
    lines.append("")
    
    # -------------------- GUtranCellRelation --------------------
    if "GUtranCellRelation" in data:
        cellrel_map = data["GUtranCellRelation"]
        keys = list(cellrel_map.keys())
        parent_key = None
        freqrel_key = None
        crel_key = None
        for k in keys:
            kl = k.strip().lower()
            if "eutrancellfdd" in kl or ("eutran" in kl and "cell" in kl):
                parent_key = parent_key or k
            if "gutranfreqrelation" in kl or ("gutran" in kl and "freq" in kl):
                freqrel_key = freqrel_key or k
            if "gutrancellrelation" in kl or "gutran cellrelation" in kl:
                crel_key = crel_key or k
        if parent_key is None and len(keys) >= 1:
            parent_key = keys[0]
        if freqrel_key is None and len(keys) >= 2:
            freqrel_key = keys[1]
        if crel_key is None and len(keys) >= 3:
            crel_key = keys[2]

        parents = cellrel_map.get(parent_key, [])
        freqrels = cellrel_map.get(freqrel_key, [])
        crels = cellrel_map.get(crel_key, [])

        maxcols = _safe_get_col_length(parents, freqrels, crels)
        
        # Obtener el ext_gnb_id para construir neighborCellRef
        ext_gnb_id = ""
        if "ExternalGNodeBFunction" in data:
            ext_map = data["ExternalGNodeBFunction"]
            first_ext_key = next(iter(ext_map.keys()))
            ext_ids = ext_map[first_ext_key]
            if ext_ids:
                ext_gnb_id = _val_at(ext_ids, 0)

        for idx in range(maxcols):
            parent = _val_at(parents, idx)
            freqrel = _val_at(freqrels, idx)
            crel = _val_at(crels, idx)
            if not (parent or freqrel or crel):
                continue
            
            lines.append(f"crn ENodeBFunction=1,EUtranCellFDD={parent},GUtranFreqRelation={freqrel},GUtranCellRelation={crel}")
            
            attrs_present = {a: vals for a, vals in cellrel_map.items() if a not in (parent_key, freqrel_key, crel_key)}
            
            # Buscar valores o usar defaults
            coverage_ind = "0"
            ess_enabled = "false"
            is_endc = "true"
            is_ho = "true"
            is_remove = "true"
            is_voice_ho = "true"
            neighbor_ref = f"GUtraNetwork={gutra_network_value},ExternalGNodeBFunction={ext_gnb_id},ExternalGUtranCell={crel}"
            user_label = ""
            
            for attr_name in GUTRANCELLRELATION_SET_ORDER:
                key_match = None
                for k in list(attrs_present.keys()):
                    k_lower = k.strip().lower().replace("_", "")
                    attr_lower = attr_name.lower().replace("_", "")
                    if k_lower.startswith(attr_lower) or attr_lower in k_lower:
                        key_match = k
                        break
                
                if key_match:
                    v = _normalize_for_print(_val_at(attrs_present[key_match], idx))
                    if v != "":
                        if attr_name == "coverageIndicator":
                            coverage_ind = v
                        elif attr_name == "essEnabled":
                            ess_enabled = v
                        elif attr_name == "isEndcAllowed":
                            is_endc = v
                        elif attr_name == "isHoAllowed":
                            is_ho = v
                        elif attr_name == "isRemoveAllowed":
                            is_remove = v
                        elif attr_name == "isVoiceHoAllowed":
                            is_voice_ho = v
                        elif attr_name == "neighborCellRef":
                            neighbor_ref = v
                        elif attr_name == "userLabel":
                            user_label = v
                    attrs_present.pop(key_match, None)
            
            # Imprimir en orden específico
            lines.append(f"coverageIndicator {coverage_ind}")
            lines.append(f"essEnabled {ess_enabled}")
            lines.append(f"isEndcAllowed {is_endc}")
            lines.append(f"isHoAllowed {is_ho}")
            lines.append(f"isRemoveAllowed {is_remove}")
            lines.append(f"isVoiceHoAllowed {is_voice_ho}")
            lines.append(f"neighborCellRef {neighbor_ref}")
            lines.append(f"userLabel {user_label}")
            
            lines.append("end")
            lines.append("")

    lines.append(" ")
    lines.append(" ")
    lines.append(" ")
    lines.append("         ")
    lines.append("confb-")
    lines.append("gs-")

    mos_content = "\n".join(lines)
    return mos_content
