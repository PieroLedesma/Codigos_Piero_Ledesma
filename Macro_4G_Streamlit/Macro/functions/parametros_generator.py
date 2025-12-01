# parametros_generator.py
# =====================================================================
# Generador de Parámetros 4G LTE - Estilo MML Explícito
# =====================================================================
# AUTOR: PIERO LEDESMA
# =====================================================================

import pandas as pd
from typing import Any, Dict, List
from datetime import datetime

# Importaciones de data_reader (se asume existencia)
try:
    from .data_reader import _read_node_mos_grouped, _read_features_sheet, _read_equipment_profiles, _read_equipment_all_mos
except Exception:
    # Stubs para ejecución independiente
    def _read_node_mos_grouped(x): return {}
    def _read_features_sheet(x): return {}
    def _read_equipment_profiles(x): return ({}, {})
    def _read_equipment_all_mos(x): return {}

# =====================================================================
# FUNCIONES AUXILIARES
# =====================================================================

def _looks_like_id_key(k: str) -> bool:
    if not k: return False
    kl = k.lower()
    if kl.startswith('struct['):
        return False
    return kl.endswith('id') or kl.endswith('_id') or kl == 'id' or kl.endswith('id ')

def _fmt_bool(val: Any) -> str:
    """Normaliza booleanos/strings a 'true'/'false' lowercase."""
    if isinstance(val, bool):
        return 'true' if val else 'false'
    s = str(val).strip()
    if s.lower() in ('true', 'false', 'yes', 'no'):
        return 'true' if s.lower() in ('true', 'yes') else 'false'
    return s

def _read_cell_carrier_full(rnd_file_xlsx: Any) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Lee la hoja Cell-Carrier y organiza los datos por Celda -> MO -> Atributo -> Valor.
    """
    try:
        df = pd.read_excel(rnd_file_xlsx, sheet_name='Cell-Carrier', engine='openpyxl', header=None)
        # Validación crítica: Debe tener al menos 2 columnas (MO, Atributo)
        if df.empty or df.shape[1] < 2:
            return {}
    except Exception:
        return {}

    header_row_idx = -1
    for idx, row in df.iterrows():
        # Acceso seguro por posición
        try:
            val0 = str(row.iloc[0]).strip()
            val1 = str(row.iloc[1]).strip()
            if val0 == "MO" and val1 == "Atributo":
                header_row_idx = idx
                break
        except IndexError:
            continue
            
    if header_row_idx == -1:
        return {}

    # Buscar fila con IDs EUtranCellFDD
    cell_id_row_idx = -1
    for idx, row in df.iterrows():
        try:
            val0 = str(row.iloc[0]).strip()
            val1 = str(row.iloc[1]).strip()
            if val0 == "EUtranCellFDD" and "EUtranCellFDD" in val1:
                cell_id_row_idx = idx
                break
        except IndexError:
            continue

    target_row_idx = cell_id_row_idx if cell_id_row_idx != -1 else header_row_idx
    target_row = df.iloc[target_row_idx]
    cells = {}
    for col_idx in range(2, len(target_row)):
        try:
            val = target_row.iloc[col_idx]
            if pd.notna(val) and str(val).strip() != "":
                cells[col_idx] = str(val).strip()
        except IndexError:
            continue

    data = {cell: {} for cell in cells.values()}

    for idx in range(header_row_idx + 1, len(df)):
        row = df.iloc[idx]
        try:
            mo_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            attr_name = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
        except IndexError:
            continue
            
        if not mo_name or not attr_name:
            continue
        if "=" in attr_name and attr_name.endswith("="):
            continue
        for col_idx, cell_name in cells.items():
            # Validación de índice de columna
            if col_idx >= len(row): continue
            
            try:
                val = row.iloc[col_idx]
                if pd.notna(val) and str(val).strip() != "":
                    if mo_name not in data[cell_name]:
                        data[cell_name][mo_name] = {}
                    data[cell_name][mo_name][attr_name] = val
            except IndexError:
                continue
    return data

# =====================================================================
# FUNCIÓN PRINCIPAL DE GENERACIÓN
# =====================================================================

def generate_parametros_mos(nemonico: str, rnd_file_xlsx: Any) -> str:
    """
    Genera el archivo parametros .mos con estructura explícita por secciones.
    """
    try:
        lines: List[str] = []

        # 1. LECTURA DE DATOS
        node_mos_grouped = _read_node_mos_grouped(rnd_file_xlsx) or {}
        eq_mos_grouped = _read_equipment_all_mos(rnd_file_xlsx) or {}
        features = _read_features_sheet(rnd_file_xlsx) or {}
        drx_profiles, qci_profiles = _read_equipment_profiles(rnd_file_xlsx)
        cell_data = _read_cell_carrier_full(rnd_file_xlsx)
        sorted_cells = sorted(cell_data.keys())

        # Merge de diccionarios (node + equipment)
        all_mos = {}
        for src in (node_mos_grouped, eq_mos_grouped):
            for k, v in src.items():
                if k not in all_mos:
                    all_mos[k] = []
                if isinstance(v, list):
                    all_mos[k].extend(v)
                elif isinstance(v, dict):
                    all_mos[k].append(v)
    except Exception as e:
        import traceback
        return f"// ERROR CRÍTICO AL GENERAR PARÁMETROS: {e}\n// {traceback.format_exc()}"

    # 2. HEADER
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append("// ====================================================================")
    lines.append("//  ARCHIVO PARA CREACIÓN DE PARÁMETROS")
    lines.append("// ====================================================================")
    lines.append("// AUTOR: PIERO LEDESMA")
    lines.append(f"// FECHA: {now}")
    lines.append("// ====================================================================")
    lines.append("")
    lines.append("confb+")
    lines.append("gs+")
    lines.append("")
    lines.append("lt all")
    lines.append("")

    # =====================================================================
    # SECCIONES DE PARÁMETROS
    # =====================================================================

    # --- AnrFunctionNR ---
    lines.append("##################################################")
    lines.append("############### AnrFunctionNR ###############")
    lines.append("##################################################")
    if 'AnrFunctionNR' in all_mos:
        for inst in all_mos['AnrFunctionNR']:
            lines.append("set ENodeBFunction=1,AnrFunction=1,AnrFunctionNR=1")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set ENodeBFunction=1,AnrFunction=1,AnrFunctionNR=1 {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- ReportConfigB1GUtra (Por Celda) ---
    lines.append("##################################################")
    lines.append("############### ReportConfigB1GUtra ###############")
    lines.append("##################################################")
    for cell in sorted_cells:
        mo_data = cell_data[cell].get('ReportConfigB1GUtra', {})
        if mo_data:
            for k, v in mo_data.items():
                if str(v).strip() != "":
                    lines.append(f"set EUtranCellFDD={cell},UeMeasControl=1,ReportConfigB1GUtra=1 {k} {_fmt_bool(v)}")
    lines.append("")

    # --- EndcProfile ---
    lines.append("##################################################")
    lines.append("############### EndcProfile ###############")
    lines.append("##################################################")
    if 'EndcProfile' in all_mos:
        for inst in all_mos['EndcProfile']:
            inst_id = inst.get('EndcProfileId', inst.get('endcProfileId', ''))
            if not inst_id: # Buscar cualquier ID
                 for k in inst:
                     if _looks_like_id_key(k): inst_id = inst[k]; break
            
            full_id = f"ENodeBFunction=1,EndcProfile={inst_id}" if inst_id else "ENodeBFunction=1,EndcProfile"
            lines.append(f"cr {full_id}")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set {full_id} {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- PmFlexCounterFilter ---
    lines.append("##################################################")
    lines.append("############### pmFlexCounterFilter ###############")
    lines.append("##################################################")
    if 'PmFlexCounterFilter' in all_mos:
        for inst in all_mos['PmFlexCounterFilter']:
            inst_id = inst.get('PmFlexCounterFilterId', '')
            full_id = f"ENodeBFunction=1,PmFlexCounterFilter={inst_id}" if inst_id else "ENodeBFunction=1,PmFlexCounterFilter"
            lines.append(f"cr {full_id}")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set {full_id} {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- McpcPSCellProfileUeCfg ---
    lines.append("##################################################")
    lines.append("############### McpcPSCellProfileUeCfg ###############")
    lines.append("##################################################")
    if 'McpcPSCellProfileUeCfg' in all_mos:
        for inst in all_mos['McpcPSCellProfileUeCfg']:
            inst_id = inst.get('McpcPSCellProfileUeCfgId', '')
            full_id = f"McpcPSCellProfileUeCfg={inst_id}" if inst_id else "McpcPSCellProfileUeCfg"
            lines.append(f"cr {full_id}")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set {full_id} {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- SubscriberGroupProfile (Orden Estricto) ---
    lines.append("##################################################")
    lines.append("############### SubscriberGroupProfile ###############")
    lines.append("##################################################")
    sg_allowed_order = [
        "dlAiLaDeltaSinrMax", "dlDynBlerTargetAlg", "dlDynBlerTargetMax",
        "dlDynBlerTargetMin", "dlHarqBlerTarget", "profilePriority",
        "selectionProbability", "pdcchFlexibleBlerMode"
    ]
    if 'SubscriberGroupProfile' in all_mos:
        for inst in all_mos['SubscriberGroupProfile']:
            # Identificar ID
            id_key = next((k for k in inst.keys() if _looks_like_id_key(k) and 'subscriber' in k.lower()), None)
            inst_id = inst.get(id_key, "") if id_key else ""
            
            lines.append(f"crn ENodeBFunction=1,SubscriberGroupProfile={inst_id}")
            for attr in sg_allowed_order:
                if attr in inst:
                    val = inst.get(attr, "")
                    val_str = "" if pd.isna(val) else str(val).strip()
                    if val_str == "":
                        lines.append(f"{attr} ")
                    else:
                        lines.append(f"{attr} {_fmt_bool(val)}")
            lines.append("end")
            lines.append("")
    lines.append("")

    # --- QciProfileOperatorDefined (Orden Estricto y Combinados) ---
    lines.append("##################################################")
    lines.append("############### QciProfileOperatorDefined ###############")
    lines.append("##################################################")
    qci_allowed_order = [
        "absPrioOverride", "aqmMode", "bitRateRecommendationEnabled", "counterActiveMode",
        "caOffloadingEnabled", "dataFwdPerQciEnabled", "dlMaxHARQTxQci", "dlMaxWaitingTime",
        "dlMinBitRate", "dlResourceAllocationStrategy", "drxPriority", "drxProfileRef",
        "dscp", "dscpArpMap", "endcProfileRef", "essResourceAllocationMode", "harqPriority",
        "inactivityTimerOffset", "laaSupported", "lessMaxDelayThreshold", "logicalChannelGroupRef",
        "measReportConfigParams", "paPartitionOverride", "pdb", "pdbOffset", "pdcpSNLength",
        "priority", "priorityFraction", "qci", "qciACTuning", "qciSubscriptionQuanta",
        "relativePriority", "relativePriorityBr", "resourceAllocationStrategy", "resourceType",
        "rlcMode", "rlcSNLength", "rlfPriority", "rlfProfileRef", "rohcEnabled",
        "rohcForUlDataEnabled", "schedulingAlgorithm", "serviceType", "srsAllocationStrategy",
        "tReorderingDl", "tReorderingUl", "timerPriority", "timerProfileRef", "ulMaxHARQTxQci",
        "ulMaxWaitingTime", "ulMinBitRate", "userLabel", "zzzTemporary1", "zzzTemporary2",
        "zzzTemporary3", "zzzTemporary4", "zzzTemporary5"
    ]

    if 'QciProfileOperatorDefined' in all_mos:
        for inst in all_mos['QciProfileOperatorDefined']:
            # ID
            qci_val = inst.get('qci', '')
            if not qci_val or str(qci_val).strip() == "":
                for k in inst:
                    if _looks_like_id_key(k) and str(inst[k]).strip() != "":
                        qci_val = inst[k]; break
            
            qci_suffix = f"qci{str(qci_val).strip()}" if qci_val else ""
            
            # Combinar measReportConfigParams (Lógica Segura)
            meas_parts = {}
            for k, v in inst.items():
                if k.startswith('measReportConfigParams'):
                    suffix = ""
                    if '_' in k:
                        parts = k.split('_', 1)
                        if len(parts) > 1: suffix = parts[1]
                    elif ' ' in k:
                        parts = k.split(' ', 1)
                        if len(parts) > 1: suffix = parts[1]
                    
                    if suffix: meas_parts[suffix] = v

            if meas_parts:
                inst['measReportConfigParams'] = ",".join([f"{k}={_fmt_bool(v)}" for k, v in meas_parts.items()])

            # Combinar dscpArpMap (Lógica Segura)
            dscp_parts = {}
            for k, v in inst.items():
                if k.startswith('dscpArpMap'):
                    suffix = ""
                    if '_' in k:
                        parts = k.split('_', 1)
                        if len(parts) > 1: suffix = parts[1]
                    elif ' ' in k:
                        parts = k.split(' ', 1)
                        if len(parts) > 1: suffix = parts[1]
                    
                    if suffix: dscp_parts[suffix] = v

            if dscp_parts:
                import re
                def _dscp_sort(k):
                    m = re.search(r'(\d+)$', k)
                    return int(m.group(1)) if m else 999
                ordered_keys = sorted(dscp_parts.keys(), key=_dscp_sort)
                inst['dscpArpMap'] = ",".join([f"{k}={_fmt_bool(dscp_parts[k])}" for k in ordered_keys])

            lines.append(f"crn QciTable=default,QciProfileOperatorDefined={qci_suffix}")
            
            for attr in qci_allowed_order:
                if attr in inst:
                    val = inst.get(attr, "")
                    if attr == 'caOffloadingEnabled' and str(val).lower() == 'true':
                        formatted = 'True'
                    else:
                        formatted = _fmt_bool(val)
                    
                    if pd.isna(val) or str(val).strip() == "":
                        lines.append(f"{attr} ")
                    else:
                        lines.append(f"{attr} {formatted}")
                elif attr in ('endcProfileRef', 'timerProfileRef', 'userLabel', 'zzzTemporary1', 'zzzTemporary2', 'zzzTemporary3', 'zzzTemporary4', 'zzzTemporary5'):
                    lines.append(f"{attr} ")
            
            lines.append("end")
            lines.append("")
    lines.append("")

    # --- QciProfileOperatorDefined V2 (Específico para qci254) ---
    lines.append("##################################################")
    lines.append("############### QciProfileOperatorDefined    V2 ###############")
    lines.append("##################################################")
    if 'QciProfileOperatorDefined' in all_mos:
        for inst in all_mos['QciProfileOperatorDefined']:
            # ID check
            qci_val = inst.get('qci', '')
            if not qci_val or str(qci_val).strip() == "":
                for k in inst:
                    if _looks_like_id_key(k) and str(inst[k]).strip() != "":
                        qci_val = inst[k]; break
            
            qci_suffix = f"qci{str(qci_val).strip()}"
            
            # Combinar measReportConfigParams (Lógica Segura)
            meas_parts = {}
            for k, v in inst.items():
                if k.startswith('measReportConfigParams'):
                    suffix = ""
                    if '_' in k:
                        parts = k.split('_', 1)
                        if len(parts) > 1: suffix = parts[1]
                    elif ' ' in k:
                        parts = k.split(' ', 1)
                        if len(parts) > 1: suffix = parts[1]
                    
                    if suffix: meas_parts[suffix] = v

            if meas_parts:
                inst['measReportConfigParams'] = ",".join([f"{k}={_fmt_bool(v)}" for k, v in meas_parts.items()])

            # Crear MO
            lines.append(f"cr ENodeBFunction=1,QciTable=default,QciProfileOperatorDefined={qci_suffix}")
            
            # Comentarios informativos (simulando ejemplo usuario)
            if 'dscp' in inst: lines.append(f"{_fmt_bool(inst['dscp'])} #dscp")
            if 'logicalChannelGroupRef' in inst: lines.append(f"{_fmt_bool(inst['logicalChannelGroupRef'])} #logicalChannelGroupRef")
            if 'priority' in inst: lines.append(f"{_fmt_bool(inst['priority'])} #priority")
            if 'qci' in inst: lines.append(f"{_fmt_bool(inst['qci'])} #qci")
            if 'resourceType' in inst: lines.append(f"{_fmt_bool(inst['resourceType'])} #resourceType")
            lines.append("")

            # lset commands
            base_lset = f"lset ENodeBFunction=1,QciTable=default,QciProfileOperatorDefined={qci_suffix}$"
            
            # Orden específico o iterar sobre todos? Usaremos el orden permitido para consistencia, pero con lset
            for attr in qci_allowed_order:
                if attr in inst and pd.notna(inst[attr]) and str(inst[attr]).strip() != "":
                    val = inst[attr]
                    if attr == 'caOffloadingEnabled' and str(val).lower() == 'true':
                        formatted = 'TRUE' # Usuario usó TRUE en mayúsculas en ejemplo lset
                    elif attr == 'rohcEnabled' and str(val).lower() == 'false':
                        formatted = 'FALSE' # Usuario usó FALSE en mayúsculas
                    else:
                        formatted = _fmt_bool(val)
                    
                    lines.append(f"{base_lset} {attr} {formatted}")
            lines.append("")
    lines.append("")

    # --- AdmissionControl ---
    lines.append("##################################################")
    lines.append("############### AdmissionControl ###############")
    lines.append("##################################################")
    if 'AdmissionControl' in all_mos:
        for inst in all_mos['AdmissionControl']:
            lines.append("set AdmissionControl=1")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set AdmissionControl=1 {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- AnrFunction ---
    lines.append("##################################################")
    lines.append("############### AnrFunction ###############")
    lines.append("##################################################")
    if 'AnrFunction' in all_mos:
        for inst in all_mos['AnrFunction']:
            lines.append("set AnrFunction=1")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set AnrFunction=1 {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- AnrFunctionUtran ---
    lines.append("##################################################")
    lines.append("############### AnrFunctionUtran ###############")
    lines.append("##################################################")
    if 'AnrFunctionUtran' in all_mos:
        for inst in all_mos['AnrFunctionUtran']:
            lines.append("set AnrFunction=1,AnrFunctionUtran=1")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set AnrFunction=1,AnrFunctionUtran=1 {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- AnrFunctionEUtran ---
    lines.append("##################################################")
    lines.append("############### AnrFunctionEUtran ###############")
    lines.append("##################################################")
    if 'AnrFunctionEUtran' in all_mos:
        for inst in all_mos['AnrFunctionEUtran']:
            lines.append("set AnrFunction=1,AnrFunctionEUtran=1")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set AnrFunction=1,AnrFunctionEUtran=1 {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- ENodeBFunction ---
    lines.append("##################################################")
    lines.append("############### ENodeBFunction ###############")
    lines.append("##################################################")
    if 'ENodeBFunction' in all_mos:
        for inst in all_mos['ENodeBFunction']:
            lines.append("set ENodeBFunction=1")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set ENodeBFunction=1 {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- AutoCellCapEstFunction ---
    lines.append("##################################################")
    lines.append("############### AutoCellCapEstFunction ###############")
    lines.append("##################################################")
    if 'AutoCellCapEstFunction' in all_mos:
        for inst in all_mos['AutoCellCapEstFunction']:
            lines.append("set AutoCellCapEstFunction=1")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set AutoCellCapEstFunction=1 {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- CarrierAggregationFunction ---
    lines.append("##################################################")
    lines.append("############### CarrierAggregationFunction ###############")
    lines.append("##################################################")
    if 'CarrierAggregationFunction' in all_mos:
        for inst in all_mos['CarrierAggregationFunction']:
            lines.append("set CarrierAggregationFunction=1")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set CarrierAggregationFunction=1 {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- DrxProfile ---
    lines.append("##################################################")
    lines.append("############### DrxProfile ###############")
    lines.append("##################################################")
    sorted_drx_ids = sorted((drx_profiles or {}).keys(), key=lambda x: int(x) if str(x).isdigit() else x)
    for drx_id in sorted_drx_ids:
        attrs = (drx_profiles or {}).get(drx_id, {})
        for k, v in attrs.items():
            if "drxprofile" in k.lower() or "=" in k: continue
            lines.append(f"set DrxProfile={drx_id} {k} {_fmt_bool(v)}")
    lines.append("")

    # --- DataRadioBearer ---
    lines.append("##################################################")
    lines.append("############### DataRadioBearer ###############")
    lines.append("##################################################")
    if 'DataRadioBearer' in all_mos:
        for inst in all_mos['DataRadioBearer']:
            inst_id = next((inst[k] for k in inst if _looks_like_id_key(k)), "")
            full_id = f"DataRadioBearer={inst_id}" if inst_id else "DataRadioBearer"
            lines.append(f"set {full_id}")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set {full_id} {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- QciProfilePredefined ---
    lines.append("##################################################")
    lines.append("############### QciProfilePredefined ###############")
    lines.append("##################################################")
    def qci_sort_key(k):
        if k == "default": return (0, 0)
        if k.startswith("qci"):
            try: return (1, int(k[3:]))
            except: return (1, 999)
        return (2, k)
    sorted_qci_ids = sorted((qci_profiles or {}).keys(), key=qci_sort_key)
    for qci_id in sorted_qci_ids:
        attrs = (qci_profiles or {}).get(qci_id, {})
        id_str = qci_id + ("$" if not qci_id.endswith("$") else "")
        for k, v in attrs.items():
            if "qciprofile" in k.lower() or "=" in k or k.startswith('measReportConfigParams_'): continue
            lines.append(f"set QciTable=default,QciProfilePredefined={id_str} {k} {_fmt_bool(v)}")
    lines.append("")

    # --- Paging ---
    lines.append("##################################################")
    lines.append("############### Paging ###############")
    lines.append("##################################################")
    if 'Paging' in all_mos:
        for inst in all_mos['Paging']:
            lines.append("set Paging=1")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set Paging=1 {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- PmService ---
    lines.append("##################################################")
    lines.append("############### PmService ###############")
    lines.append("##################################################")
    if 'PmService' in all_mos:
        for inst in all_mos['PmService']:
            lines.append("set PmService=1")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set PmService=1 {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- SignalingRadioBearer ---
    lines.append("##################################################")
    lines.append("############### SignalingRadioBearer ###############")
    lines.append("##################################################")
    if 'SignalingRadioBearer' in all_mos:
        for inst in all_mos['SignalingRadioBearer']:
            inst_id = next((inst[k] for k in inst if _looks_like_id_key(k)), "")
            full_id = f"SignalingRadioBearer={inst_id}" if inst_id else "SignalingRadioBearer"
            lines.append(f"set {full_id}")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set {full_id} {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- LoadBalancingFunction ---
    lines.append("##################################################")
    lines.append("############### LoadBalancingFunction ###############")
    lines.append("##################################################")
    if 'LoadBalancingFunction' in all_mos:
        for inst in all_mos['LoadBalancingFunction']:
            lines.append("set LoadBalancingFunction=1")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set LoadBalancingFunction=1 {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- RlfProfile ---
    lines.append("##################################################")
    lines.append("############### RlfProfile ###############")
    lines.append("##################################################")
    if 'RlfProfile' in all_mos:
        for inst in all_mos['RlfProfile']:
            lines.append("set RlfProfile=1$")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set RlfProfile=1$ {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- Rrc ---
    lines.append("##################################################")
    lines.append("############### Rrc ###############")
    lines.append("##################################################")
    if 'Rrc' in all_mos:
        for inst in all_mos['Rrc']:
            lines.append("set Rrc=1")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set Rrc=1 {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- Sctp ---
    lines.append("##################################################")
    lines.append("############### Sctp ###############")
    lines.append("##################################################")
    if 'Sctp' in all_mos:
        for inst in all_mos['Sctp']:
            lines.append("set Sctp=1")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set Sctp=1 {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- SctpProfile ---
    lines.append("##################################################")
    lines.append("############### SctpProfile ###############")
    lines.append("##################################################")
    if 'SctpProfile' in all_mos:
        for inst in all_mos['SctpProfile']:
            inst_id = next((inst[k] for k in inst if _looks_like_id_key(k)), "")
            full_id = f"SctpProfile={inst_id}" if inst_id else "SctpProfile"
            lines.append(f"set {full_id}")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set {full_id} {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- SecurityHandling ---
    lines.append("##################################################")
    lines.append("############### SecurityHandling ###############")
    lines.append("##################################################")
    if 'SecurityHandling' in all_mos:
        for inst in all_mos['SecurityHandling']:
            lines.append("set SecurityHandling=1")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set SecurityHandling=1 {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- Rcs ---
    lines.append("##################################################")
    lines.append("############### Rcs ###############")
    lines.append("##################################################")
    if 'Rcs' in all_mos:
        for inst in all_mos['Rcs']:
            lines.append("set Rcs=1")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set Rcs=1 {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- PreschedulingProfile ---
    lines.append("##################################################")
    lines.append("############### PreschedulingProfile ###############")
    lines.append("##################################################")
    if 'PreschedulingProfile' in all_mos:
        for inst in all_mos['PreschedulingProfile']:
            lines.append("set PreschedulingProfile=initial")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set PreschedulingProfile=initial {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- MACConfiguration ---
    lines.append("##################################################")
    lines.append("############### MACConfiguration ###############")
    lines.append("##################################################")
    if 'MACConfiguration' in all_mos:
        for inst in all_mos['MACConfiguration']:
            lines.append("set ENodeBFunction=1,RadioBearerTable=default,MACConfiguration=1")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set ENodeBFunction=1,RadioBearerTable=default,MACConfiguration=1 {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- CellSleepFunction (Por Celda) ---
    lines.append("##################################################")
    lines.append("############### CellSleepFunction ###############")
    lines.append("##################################################")
    for cell in sorted_cells:
        mo_data = cell_data[cell].get('CellSleepFunction', {})
        if mo_data:
            for k, v in mo_data.items():
                lines.append(f"set EUtranCellFDD={cell},CellSleepFunction=1 {k} {_fmt_bool(v)}")
    lines.append("")

    # --- ReportConfig (Varios, Por Celda) ---
    report_mos = [
        "ReportConfigA5", "ReportConfigSearch", "ReportConfigA1Prim", "ReportConfigA5Anr",
        "ReportConfigA5SoftLock", "ReportConfigA5UlTrig", "ReportConfigB2Utra",
        "ReportConfigB2UtraUlTrig", "ReportConfigCsfbUtra", "ReportConfigEUtraBadCovPrim",
        "ReportConfigEUtraBadCovSec", "ReportConfigEUtraBestCell", "ReportConfigEUtraBestCellAnr",
        "ReportConfigEUtraInterFreqLb", "ReportConfigSCellA1A2", "ReportConfigA5EndcHo"
    ]
    for cell in sorted_cells:
        ue_meas = cell_data[cell].get('UeMeasControl', {})
        for k, v in ue_meas.items():
            lines.append(f"set EUtranCellFDD={cell},UeMeasControl=1 {k} {_fmt_bool(v)}")
        
        for mo in report_mos:
            mo_data = cell_data[cell].get(mo, {})
            if not mo_data: continue
            if mo == "ReportConfigSearch":
                combined_attrs = [f"{k}={_fmt_bool(v)}" for k, v in mo_data.items()]
                if combined_attrs:
                    lines.append(f"set EUtranCellFDD={cell},UeMeasControl=1,{mo}=1 {','.join(combined_attrs)}")
            else:
                for k, v in mo_data.items():
                    lines.append(f"set EUtranCellFDD={cell},UeMeasControl=1,{mo}=1 {k} {_fmt_bool(v)}")
    lines.append("")

    # --- MimoSleepFunction (Por Celda) ---
    lines.append("##################################################")
    lines.append("############### MimoSleepFunction ###############")
    lines.append("##################################################")
    for cell in sorted_cells:
        mo_data = cell_data[cell].get('MimoSleepFunction', {})
        if mo_data:
            for k, v in mo_data.items():
                lines.append(f"set EUtranCellFDD={cell},MimoSleepFunction=1 {k} {_fmt_bool(v)}")
    lines.append("")

    # --- Transport ---
    lines.append("##################################################")
    lines.append("############### Transport ###############")
    lines.append("##################################################")
    if 'Transport' in all_mos:
        for inst in all_mos['Transport']:
            lines.append("cr Transport=1")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set Transport=1 {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- Router ---
    lines.append("##################################################")
    lines.append("############### Router ###############")
    lines.append("##################################################")
    if 'Router' in all_mos:
        for inst in all_mos['Router']:
            inst_id = next((inst[k] for k in inst if _looks_like_id_key(k)), "")
            full_id = f"Router={inst_id}" if inst_id else "Router"
            lines.append(f"set {full_id}")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set {full_id} {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- SystemFunctions ---
    lines.append("##################################################")
    lines.append("############### SystemFunctions ###############")
    lines.append("##################################################")
    if 'SystemFunctions' in all_mos:
        for inst in all_mos['SystemFunctions']:
            lines.append("set SystemFunctions=1")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set SystemFunctions=1 {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- SubscriberProfileID ---
    lines.append("##################################################")
    lines.append("############### SubscriberProfileID ###############")
    lines.append("##################################################")
    if 'SubscriberProfileID' in all_mos:
        for inst in all_mos['SubscriberProfileID']:
            inst_id = next((inst[k] for k in inst if _looks_like_id_key(k)), "")
            full_id = f"ENodeBFunction=1,SubscriberProfileID={inst_id}" if inst_id else "ENodeBFunction=1,SubscriberProfileID"
            lines.append(f"cr {full_id}")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set {full_id} {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- TimerProfile ---
    lines.append("##################################################")
    lines.append("############### TimerProfile ###############")
    lines.append("##################################################")
    if 'TimerProfile' in all_mos:
        for inst in all_mos['TimerProfile']:
            inst_id = next((inst[k] for k in inst if _looks_like_id_key(k)), "")
            full_id = f"ENodeBFunction=1,TimerProfile={inst_id}" if inst_id else "ENodeBFunction=1,TimerProfile"
            lines.append(f"cr {full_id}")
            for k, v in inst.items():
                if _looks_like_id_key(k): continue
                if pd.notna(v) and str(v).strip() != "":
                    lines.append(f"set {full_id} {k} {_fmt_bool(v)}")
            lines.append("")
    lines.append("")

    # --- NbIotCell (Lógica Especial) ---
    if 'NbIotCell' in all_mos:
        lines.append("##################################################")
        lines.append("############### NbIotCell ###############")
        lines.append("##################################################")
        
        crn_attrs_list = [
            'cellId', 'eutranCellRef', 'physicalLayerCellId', 'nbIotCellType', 
            'tac', 'ulAnchPrbIndex', 'dlAnchPrbIndex', 'plmnIdList'
        ]
        
        for inst in all_mos['NbIotCell']:
            # PLMN List Logic
            plmn_attrs = {k.split('_', 1)[1]: v for k, v in inst.items() if k.startswith(('activePlmnList_', 'plmnIdList_'))}
            if plmn_attrs:
                parts = []
                if 'mcc' in plmn_attrs: parts.append(f"mcc={plmn_attrs['mcc']}")
                if 'mnc' in plmn_attrs: parts.append(f"mnc={plmn_attrs['mnc']}")
                if 'mncLength' in plmn_attrs: parts.append(f"mncLength={plmn_attrs['mncLength']}")
                inst['plmnIdList'] = ",".join(parts)

            # ID Logic
            id_key = next((k for k in inst if 'nbiotcell' in k.lower() and k != 'nbIotCellType'), None)
            if not id_key:
                id_key = next((k for k in inst if _looks_like_id_key(k) and k not in ('cellId', 'physicalLayerCellId')), None)
            inst_id = inst.get(id_key, "") if id_key else ""

            # EutranCellRef Logic
            if 'eutranCellRef' in inst and not str(inst['eutranCellRef']).startswith('EUtranCellFDD='):
                inst['eutranCellRef'] = f"EUtranCellFDD={inst['eutranCellRef']}"

            # CRN
            lines.append(f"crn ENodeBFunction=1,NbIotCell={inst_id}")
            for attr in crn_attrs_list:
                if attr in inst:
                    lines.append(f"{attr} {_fmt_bool(inst[attr])}")
            lines.append("End")
            
            # SET
            base_set = f"set ENodeBFunction=1,NbIotCell={inst_id}"
            if 'administrativeState' in inst: lines.append(f"{base_set} administrativeState {_fmt_bool(inst['administrativeState'])}")
            if 'cellRange' in inst: lines.append(f"{base_set} cellRange {_fmt_bool(inst['cellRange'])}")
            lines.append(f"{base_set} nprachAllocConfig ")
            if 'pZeroNominalNPusch' in inst: lines.append(f"{base_set} pZeroNominalNPusch {_fmt_bool(inst['pZeroNominalNPusch'])}")
            if 'qQualMin' in inst: lines.append(f"{base_set} intraFrequencyInfo qQualMin={_fmt_bool(inst['qQualMin'])}")
            if 'qRxLevMin' in inst: lines.append(f"{base_set} intraFrequencyInfo qRxLevMin={_fmt_bool(inst['qRxLevMin'])}")
            if 'ulAnchPrbIndex' in inst: lines.append(f"{base_set} ulAnchPrbIndex {_fmt_bool(inst['ulAnchPrbIndex'])}")
            if 'dlAnchPrbIndex' in inst: lines.append(f"{base_set} dlAnchPrbIndex {_fmt_bool(inst['dlAnchPrbIndex'])}")
            if 'qHyst' in inst: lines.append(f"{base_set} qHyst {_fmt_bool(inst['qHyst'])}")
            if 'preambleIniRecTargetPower' in inst: lines.append(f"{base_set} preambleIniRecTargetPower {_fmt_bool(inst['preambleIniRecTargetPower'])}")
            if 'nprachAllocConfig' in inst: lines.append(f"{base_set} nprachAllocConfig {_fmt_bool(inst['nprachAllocConfig'])}")
            lines.append("")
    lines.append("")

    # --- Features ---
    lines.append("##################################################")
    lines.append("############### Features ###############")
    lines.append("##################################################")
    lines.append(f"set ENodeBFunction=1 eNBId  {nemonico[3:] if len(nemonico)>3 else '10215'}")
    lines.append("set Lm=1,FeatureState=CXC4011803 featureState 1")
    lines.append("")
    for feature, state in (features or {}).items():
        lines.append(f"set {feature}  featurestate {state}")
    lines.append("")

    # 3. CIERRE
    lines.append("cvms Parametros_Pledesma")
    lines.append("")
    lines.append("confb-")
    lines.append("gs-")
    lines.append("")

    return "\n".join(lines)
