# =====================================================================
# NR_Relation_Parametros.py - Generación de script Relations y Parámetros para 5G NR
# =====================================================================
# AUTOR: PIERO LEDESMA
# =====================================================================

import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime

# =====================================================================
# FUNCIONES DE UTILIDAD PARA PARSEO GENÉRICO
# =====================================================================

def parse_rnd_sheet(df: pd.DataFrame) -> List[Dict[str, Dict[str, str]]]:
    """
    Parsea una hoja genérica del RND (Node, Cell-Carrier, Equipment, etc.)
    Retorna una lista de diccionarios, donde cada diccionario representa una INSTANCIA (columna).
    Estructura: [ { 'MO_Name': {'Attribute': 'Value', ...}, ... }, ... ]
    """
    instances_data = []
    
    if df is None or df.empty:
        return instances_data
        
    # Validar estructura mínima (MO, Atributo, Instancia 1...)
    if len(df.columns) < 3:
        return instances_data
        
    # Las columnas de instancias empiezan en el índice 2
    instance_cols = df.columns[2:]
    
    for col in instance_cols:
        instance_dict = {}
        # Guardar el ID de la columna (header) por si acaso
        instance_dict['_instance_id'] = str(col)
        
        for _, row in df.iterrows():
            # Columna 0: MO Class / Object
            mo_name = str(row.iloc[0]).strip()
            # Columna 1: Attribute Name
            attr_name = str(row.iloc[1]).strip()
            # Columna Actual: Value
            value = str(row[col]).strip()
            
            # Saltar valores vacíos o inválidos
            if not mo_name or not attr_name or not value or value.lower() == 'nan':
                continue
                
            if mo_name not in instance_dict:
                instance_dict[mo_name] = {}
            
            instance_dict[mo_name][attr_name] = value
            
        if instance_dict:
            instances_data.append(instance_dict)
            
    return instances_data

def parse_features_sheet(df: pd.DataFrame) -> Dict[str, str]:
    """
    Parsea la hoja 'Features' que tiene una estructura diferente.
    Retorna un diccionario {FeatureName: FeatureState}
    """
    features_map = {}
    if df is None or df.empty:
        return features_map
        
    for _, row in df.iterrows():
        if len(row) < 3: continue
        
        # Asumimos estructura: [MO, FeatureName, State] o similar
        # Buscamos valores que parezcan licencias (CXC...)
        feat_name = str(row.iloc[1]).strip()
        feat_state = str(row.iloc[2]).strip()
        
        if feat_name.startswith('CXC'):
            # Normalizar estado
            if feat_state.lower() == 'true': 
                feat_state = '1'
            elif feat_state.lower() == 'false': 
                feat_state = '0'
            else:
                try:
                    # Convertir float string (e.g. "1.0") a int string ("1")
                    feat_state = str(int(float(feat_state)))
                except (ValueError, TypeError):
                    pass
            
            features_map[feat_name] = feat_state
            
    return features_map

# =====================================================================
# FUNCIÓN PRINCIPAL DE GENERACIÓN
# =====================================================================

def generar_nr_relation_parametros_5g(
    nemonico: str,
    wsh_data: Dict[str, Any],
    rnd_data: Dict[str, pd.DataFrame]
) -> str:
    """
    Función principal que genera el script MML para NR Relations y Parámetros.
    Sigue el estilo de node_generator.py con variables arriba y mml_output.append().
    """
    mml_output = []
    
    # =====================================================================
    # 1. CARGA DE VARIABLES DESDE EL RND (TODAS LAS HOJAS)
    # =====================================================================
    
    # Hoja: Node
    df_node = rnd_data.get('Node')
    node_instances = parse_rnd_sheet(df_node) if df_node is not None else []
    
    # Hoja: Cell-Carrier
    df_cell = rnd_data.get('Cell-Carrier')
    cell_instances = parse_rnd_sheet(df_cell) if df_cell is not None else []
    
    # Hoja: Equipment-Configuration
    df_equipment = rnd_data.get('Equipment-Configuration')
    equipment_instances = parse_rnd_sheet(df_equipment) if df_equipment is not None else []
    
    # Hoja: Features
    df_features = rnd_data.get('Features')
    features_map = parse_features_sheet(df_features) if df_features is not None else {}
    
    # =====================================================================
    # 2. EXTRACCIÓN DE DATOS DE NRFrequency
    # =====================================================================
    
    # Buscar instancias de NRFrequency en Equipment-Configuration
    nrfreq_data_list = []
    for inst in equipment_instances:
        if 'NRFrequency' in inst:
            nrfreq_data_list.append(inst['NRFrequency'])
    
    # =====================================================================
    # 3. EXTRACCIÓN DE DATOS DE NRCellCU y NRFreqRelation y CgSwitchCfg
    # =====================================================================
    
    # Buscar instancias de NRCellCU y NRFreqRelation en Cell-Carrier
    nrcellcu_list = []
    nrfreqrel_data_list = []
    cgswitch_data_list = []
    
    for inst in cell_instances:
        if 'NRCellCU' in inst:
            nrcellcu_list.append(inst['NRCellCU'])
        if 'NRFreqRelation' in inst:
            nrfreqrel_data_list.append(inst['NRFreqRelation'])
        if 'CgSwitchCfg' in inst:
            cgswitch_data_list.append(inst['CgSwitchCfg'])
    
    # Si no hay datos en cell_instances, buscar en equipment_instances
    if not nrfreqrel_data_list:
        for inst in equipment_instances:
            if 'NRFreqRelation' in inst:
                nrfreqrel_data_list.append(inst['NRFreqRelation'])
    
    # =====================================================================
    # 4. GENERACIÓN DEL HEADER DEL SCRIPT
    # =====================================================================
    
    mml_output.append(f"// ====================================================================")
    mml_output.append(f"// 03_{nemonico}_NR_RELATION_PARAM.mos - Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    mml_output.append(f"// AUTOR: PIERO LEDESMA")
    mml_output.append(f"// Nemonico: {nemonico}")
    mml_output.append(f"// ====================================================================\n")
    
    # =====================================================================
    # 5. SECCIÓN: HEADER Y TRAMA (TN_IDL_B)
    # =====================================================================
    
    mml_output.append("confb+")
    mml_output.append("gs+")
    mml_output.append("get Transport=1,EthernetPort= ethernetPortId > TN_IDL_B\n\n")
    
    # =====================================================================
    # 6. SECCIÓN: NRNetwork
    # =====================================================================
    
    mml_output.append("confb+")
    mml_output.append("gs+")
    mml_output.append("cr GNBCUCPFunction=1,NRNetwork=1\n")
    
    # =====================================================================
    # 7. SECCIÓN: NRFrequency (DINÁMICO)
    # =====================================================================
    
    mml_output.append("################################################################")
    mml_output.append("## NRFrequency  V3 ")
    mml_output.append("################################################################")
    
    if nrfreq_data_list:
        for nrfreq_attrs in nrfreq_data_list:
            # --- Extracción de valores clave ---
            arfcn = nrfreq_attrs.get('arfcnValueNRDl', '')
            scs = nrfreq_attrs.get('smtcScs', '')
            
            # Determinar ID: Prioridad 1: nRFrequencyId, Prioridad 2: Construido arfcn-scs
            mo_id = nrfreq_attrs.get('nRFrequencyId')
            if not mo_id and arfcn and scs:
                mo_id = f"{arfcn}-{scs}"
            elif not mo_id:
                mo_id = nrfreq_attrs.get('_instance_id', '1') # Fallback
            
            # Path del MO
            mo_path = f"GNBCUCPFunction=1,NRNetwork=1,NRFrequency={mo_id}"
            
            # Extracción explícita de atributos en el orden requerido
            arfcn_val = nrfreq_attrs.get('arfcnValueNRDl', '')
            duration = nrfreq_attrs.get('smtcDuration', '')
            offset = nrfreq_attrs.get('smtcOffset', '')
            periodicity = nrfreq_attrs.get('smtcPeriodicity', '')
            scs_val = nrfreq_attrs.get('smtcScs', '')
            
            # --- Generación del bloque MML ---
            mml_output.append(f"crn {mo_path}")
            
            # Atributos en orden estricto
            if arfcn_val: mml_output.append(f"arfcnValueNRDl {arfcn_val}")
            if duration: mml_output.append(f"smtcDuration {duration}")
            if offset: mml_output.append(f"smtcOffset {offset}")
            if periodicity: mml_output.append(f"smtcPeriodicity {periodicity}")
            if scs_val: mml_output.append(f"smtcScs {scs_val}")
            
            mml_output.append("end\n")
    else:
        mml_output.append("// WARNING: No se encontraron datos de NRFrequency en Equipment-Configuration\n")

    mml_output.append("\nbl nrcell|sector \n")
    
    # =====================================================================
    # 8. SECCIÓN: NRFreqRelation (DINÁMICO)
    # =====================================================================
    
    mml_output.append("\n################################################################")
    mml_output.append("## NRFreqRelation  V2 ")
    mml_output.append("################################################################\n")
    
    # Generar NRFreqRelation para cada celda
    if nrcellcu_list:
        # Usar el primer NRFreqRelation como template si existe, sino usar valores por defecto
        nrfreqrel_template = nrfreqrel_data_list[0] if nrfreqrel_data_list else {}
        
        for nrcellcu_attrs in nrcellcu_list:
            # --- Extracción de valores clave ---
            cell_id = nrcellcu_attrs.get('nRCellCUId', nrcellcu_attrs.get('_instance_id', '1'))
            
            # El ID del NRFreqRelation es el arfcnValueNRDl (del primer NRFrequency)
            freq_relation_id = nrfreq_data_list[0].get('arfcnValueNRDl', '620736') if nrfreq_data_list else '620736'
            
            # Path del MO
            mo_path = f"GNBCUCPFunction=1,NRCellCU={cell_id},NRFreqRelation={freq_relation_id}"
            
            # Extracción de atributos de NRFreqRelation (con valores por defecto del ejemplo)
            cell_resel_priority = nrfreqrel_template.get('cellReselectionPriority', '7')
            p_max = nrfreqrel_template.get('pMax', '23')
            q_offset_freq = nrfreqrel_template.get('qOffsetFreq', '0')
            q_rx_lev_min = nrfreqrel_template.get('qRxLevMin', '-140')
            s_intra_search_p = nrfreqrel_template.get('sIntraSearchP', '62')
            t_resel_nr = nrfreqrel_template.get('tReselectionNR', '2')
            thresh_x_high_p = nrfreqrel_template.get('threshXHighP', '4')
            thresh_x_low_p = nrfreqrel_template.get('threshXLowP', '0')
            
            # nRFrequencyRef apunta al NRFrequency creado anteriormente
            # Usar el ID del primer NRFrequency
            nrfreq_ref_id = nrfreq_data_list[0].get('nRFrequencyId', f"{freq_relation_id}-30") if nrfreq_data_list else f"{freq_relation_id}-30"
            nr_frequency_ref = f"NRNetwork=1,NRFrequency={nrfreq_ref_id}"
            
            # --- Generación del bloque MML ---
            mml_output.append(f"crn {mo_path}")
            mml_output.append(f"cellReselectionPriority {cell_resel_priority}")
            mml_output.append(f"nRFrequencyRef {nr_frequency_ref}")
            mml_output.append(f"pMax {p_max}")
            mml_output.append(f"qOffsetFreq {q_offset_freq}")
            mml_output.append(f"qRxLevMin {q_rx_lev_min}")
            mml_output.append(f"sIntraSearchP {s_intra_search_p}")
            mml_output.append(f"tReselectionNR {t_resel_nr}")
            mml_output.append(f"threshXHighP {thresh_x_high_p}")
            mml_output.append(f"threshXLowP {thresh_x_low_p}")
            mml_output.append("end\n")
    else:
        mml_output.append("// WARNING: No se encontraron datos de NRCellCU\n")
    
    mml_output.append("\nbl nrcell|sector \n")
    
    # =====================================================================
    # 9. SECCIÓN: Features (DINÁMICO)
    # =====================================================================
    
    mml_output.append("\n################################################################")
    mml_output.append("## features  V4")
    mml_output.append("################################################################")
    mml_output.append("BL AAS|SECTOR|CELL")
    
    # Generar comandos SET para cada feature
    if features_map:
        for feature_name, feature_state in features_map.items():
            mml_output.append(f"set {feature_name} featurestate {feature_state}")
    else:
        mml_output.append("// WARNING: No se encontraron features en la hoja Features\n")
        
    # =====================================================================
    # 10. SECCIÓN: CgSwitchCfg (DINÁMICO)
    # =====================================================================
    
    mml_output.append("\n##########################################")
    mml_output.append("### CgSwitchCfg ")
    mml_output.append("##################################################\n")
    
    # Si no hay datos de CgSwitchCfg en el RND, usamos los de NRCellCU para iterar
    target_list = cgswitch_data_list if cgswitch_data_list else nrcellcu_list
    
    if target_list:
        for i, item in enumerate(target_list):
            # Obtener ID de la celda (N37811, etc.)
            # Si estamos iterando sobre CgSwitchCfg, buscamos 'CgSwitchCfgId'
            # Si estamos iterando sobre NRCellCU, buscamos 'nRCellCUId'
            if cgswitch_data_list:
                mo_id = item.get('CgSwitchCfgId', item.get('_instance_id', f'N3781{i+1}'))
            else:
                mo_id = item.get('nRCellCUId', item.get('_instance_id', f'N3781{i+1}'))
            
            # Path del MO
            mo_path = f"GNBDUFunction=1,UeCC=1,CgSwitchCfg={mo_id}"
            
            # Valores (sin defaults, solo lo que hay en RND)
            dl_cg_switch_mode = item.get('dlCgSwitchMode')
            dl_scg_low_qual_thresh = item.get('dlScgLowQualThresh')
            dl_scg_low_qual_hyst = item.get('dlScgLowQualHyst')
            
            # Generar bloque
            mml_output.append(f"cr {mo_path}")
            if dl_cg_switch_mode: mml_output.append(f"Set {mo_path} dlCgSwitchMode {dl_cg_switch_mode}")
            if dl_scg_low_qual_thresh: mml_output.append(f"Set {mo_path} dlScgLowQualThresh {dl_scg_low_qual_thresh}")
            if dl_scg_low_qual_hyst: mml_output.append(f"Set {mo_path} dlScgLowQualHyst {dl_scg_low_qual_hyst}\n")
    else:
        mml_output.append("// WARNING: No se encontraron celdas para generar CgSwitchCfg\n")
    
    # =====================================================================
    # 11. SECCIÓN: CUCP5qiTable y CUUP5qiTable (ESTÁTICO)
    # =====================================================================
    
    mml_output.append("\n##########################################")
    mml_output.append("### CUCP5qiTable=1")
    mml_output.append("##########################################\n")
    
    # CUCP5qiTable principal
    mml_output.append("crn GNBCUCPFunction=1,CUCP5qiTable=1")
    mml_output.append("default5qiTable true")
    mml_output.append("end\n")
    
    # Configuraciones CUCP5qi individuales
    cucp5qi_configs = [
        {'id': 1, 'pdcpSnSize': 12, 'rlcMode': 1, 'tPdcpDiscard': 150, 'tReorderingDl': 200, 'tReorderingUl': 40},
        {'id': 2, 'pdcpSnSize': 12, 'rlcMode': 1, 'tPdcpDiscard': 200, 'tReorderingDl': 200, 'tReorderingUl': 40},
        {'id': 3, 'pdcpSnSize': 12, 'rlcMode': 0, 'tPdcpDiscard': 200, 'tReorderingDl': 200, 'tReorderingUl': 40},
        {'id': 4, 'pdcpSnSize': 12, 'rlcMode': 0, 'tPdcpDiscard': 200, 'tReorderingDl': 200, 'tReorderingUl': 40},
        {'id': 5, 'pdcpSnSize': 12, 'rlcMode': 0, 'tPdcpDiscard': 2147483646, 'tReorderingDl': 200, 'tReorderingUl': 40},
        {'id': 6, 'pdcpSnSize': 12, 'rlcMode': 0, 'tPdcpDiscard': 1500, 'tReorderingDl': 200, 'tReorderingUl': 40},
        {'id': 7, 'pdcpSnSize': 12, 'rlcMode': 0, 'tPdcpDiscard': 1500, 'tReorderingDl': 200, 'tReorderingUl': 40},
        {'id': 8, 'pdcpSnSize': 18, 'rlcMode': 0, 'tPdcpDiscard': 1500, 'tReorderingDl': 200, 'tReorderingUl': 40},
        {'id': 9, 'pdcpSnSize': 18, 'rlcMode': 0, 'tPdcpDiscard': 1500, 'tReorderingDl': 200, 'tReorderingUl': 40},
    ]
    
    for config in cucp5qi_configs:
        mml_output.append(f"crn GNBCUCPFunction=1,CUCP5qiTable=1,CUCP5qi={config['id']}")
        mml_output.append("nrdcSnTerminationRef")
        mml_output.append(f"pdcpSnSize {config['pdcpSnSize']}")
        mml_output.append(f"profile5qi {config['id']}")
        mml_output.append(f"rlcMode {config['rlcMode']}")
        mml_output.append(f"tPdcpDiscard {config['tPdcpDiscard']}")
        mml_output.append(f"tReorderingDl {config['tReorderingDl']}")
        mml_output.append(f"tReorderingUl {config['tReorderingUl']}")
        mml_output.append("userLabel")
        mml_output.append("end\n")
    
    # CUUP5qiTable principal
    mml_output.append("crn GNBCUUPFunction=1,CUUP5qiTable=1")
    mml_output.append("default5qiTable true")
    mml_output.append("end\n")
    
    # Configuraciones CUUP5qi individuales
    cuup5qi_configs = [
        {'id': 6, 'dscp': 20},
        {'id': 7, 'dscp': 12},
        {'id': 8, 'dscp': 14},
        {'id': 9, 'dscp': 18},
    ]
    
    for config in cuup5qi_configs:
        mml_output.append(f"CRN GNBCUUPFunction=1,CUUP5qiTable=1,CUUP5qi={config['id']}")
        mml_output.append("counterActiveMode false")
        mml_output.append("drbRef GNBCUUPFunction=1,UeCC=1,Drb=Default_other")
        mml_output.append(f"dscp {config['dscp']}")
        mml_output.append(f"profile5qi {config['id']}")
        mml_output.append("userLabel")
        mml_output.append("end\n")
    
    # =====================================================================
    # 12. SECCIÓN: GNBCUUPFunction - GtpuSupervision (ESTÁTICO)
    # =====================================================================
    
    mml_output.append("\n##########################################")
    mml_output.append("### GNBCUUPFunction")
    mml_output.append("##################################################")
    
    mml_output.append("CR GNBCUUPFunction=1,GtpuSupervision=1")
    mml_output.append("SET GNBCUUPFunction=1,GtpuSupervision=1 gtpuErrorIndDscp 40")
    mml_output.append("SET GNBCUUPFunction=1,GtpuSupervision=1 gtpuSupervisionId 1")
    mml_output.append("bl nrcell|sector")
    mml_output.append("bl nrcell|sector")
    
    # =====================================================================
    # CIERRE DEL SCRIPT
    # =====================================================================
    
    mml_output.append("gs-")
    mml_output.append("confb-")
    mml_output.append(f"cvms PL_REL_PARAM_{nemonico}")
    mml_output.append("\n////////////////- fin -///////////////////////////////////////")
    
    # =====================================================================
    # RETORNO DEL CONTENIDO COMPLETO
    # =====================================================================
    
    return "\n".join(mml_output)