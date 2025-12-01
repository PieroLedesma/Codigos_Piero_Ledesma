# =====================================================================
# carrier_cell_generator.py - Generación de script Carrier/Cell MOS para 5G NR
# =====================================================================

import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime

# =====================================================================
# CONSTANTES DE CONFIGURACIÓN DE MOS (VARIABLES)
# =====================================================================

# MO Paths y Constantes para FieldReplaceableUnit
MO_NAME_AAS = "FieldReplaceableUnit"
ATTR_SHARED = "isSharedWithExternalMe"
MO_PATH_AAS_PREFIX = "Equipment=1,FieldReplaceableUnit="

# MO Names (Variables para uso futuro)
MO_VAR_NR_CELL_CU = "NRCellCU"
MO_VAR_NR_CELL_DU = "NRCellDU"
MO_VAR_NR_SECTOR_CARRIER = "NRSectorCarrier"
MO_VAR_BWP_DL = "BwpDl" 
MO_VAR_BWP_UL = "BwpUl" 

# MO Base Paths
MO_PATH_CUCP_BASE = "GNBCUCPFunction=1"
MO_PATH_DU_BASE = "GNBDUFunction=1"

# =====================================================================
# FUNCIONES DE UTILIDAD PARA PARSEO (CELL-CARRIER)
# =====================================================================

def parse_cell_carrier_data(df: pd.DataFrame) -> List[Dict[str, Dict[str, str]]]:
    """
    Parsea la hoja 'Cell-Carrier' (RAW) y retorna una lista de diccionarios.
    Cada elemento de la lista representa una INSTANCIA (Cell/Sector) y contiene
    un diccionario de MOs y sus atributos.
    """
    instances_data = []
    
    if df is None or df.empty:
        return instances_data
        
    # Identificar columnas de instancias (desde índice 2 en adelante)
    if len(df.columns) < 3:
        return instances_data
        
    instance_cols = df.columns[2:]
    
    for col in instance_cols:
        instance_dict = {}
        
        # Iterar sobre las filas del DataFrame
        for _, row in df.iterrows():
            mo_name = str(row.iloc[0]).strip() # Columna 0: MO
            attr_name = str(row.iloc[1]).strip() # Columna 1: Atributo
            value = str(row[col]).strip() # Valor de la instancia actual
            
            # Ignorar valores vacíos o NaN
            if not mo_name or not attr_name or not value or value.lower() == 'nan':
                continue
                
            if mo_name not in instance_dict:
                instance_dict[mo_name] = {}
                # Guardar el ID de la instancia (nombre de la columna) como fallback
                instance_dict[mo_name]['_id_from_header'] = str(col)
            
            instance_dict[mo_name][attr_name] = value
            
        if instance_dict:
            instances_data.append(instance_dict)
            
    return instances_data

# =====================================================================
# GENERACIÓN DE COMANDOS FieldReplaceableUnit (DINÁMICO - AAS)
# =====================================================================

def generate_aas_mml(df_equipment: pd.DataFrame) -> str:
    """
    Genera comandos para FieldReplaceableUnit (AAS) usando lógica dinámica
    robusta, extrayendo IDs y el atributo isSharedWithExternalMe del RND.
    """
    
    # 1. Filtrar solo filas de FieldReplaceableUnit
    # Se busca 'FieldReplaceableUnit' en la primera columna (índice 0)
    df_aas = df_equipment[df_equipment.iloc[:, 0].astype(str).str.strip().str.contains(MO_NAME_AAS, na=False, regex=False)].copy()
    
    if df_aas.empty or df_aas.shape[1] < 3:
        return "// ERROR: No se encontraron datos válidos de FieldReplaceableUnit en Equipment-Configuration o el formato de columna es incorrecto."

    # Definimos el índice de la columna de Atributo (índice 1)
    atributo_col_index = 1
    
    # === CORRECCIÓN CLAVE: BUSCAR 'FieldReplaceableUnit=' (con el =) ===
    # Fila que contiene los IDs de AAS (Ej: AAS-1, AAS-2...)
    aas_id_row = df_aas[df_aas.iloc[:, atributo_col_index].astype(str).str.strip() == f'{MO_NAME_AAS}=']
    
    # Fila que contiene el atributo isSharedWithExternalMe
    shared_row = df_aas[df_aas.iloc[:, atributo_col_index].astype(str).str.strip() == ATTR_SHARED]

    if aas_id_row.empty or shared_row.empty:
        return f"// ERROR: Faltan las filas de IDs ({MO_NAME_AAS}=) o {ATTR_SHARED} en el RND."

    # 3. Extracción de datos
    # Extraemos los valores de todas las columnas desde el índice 2 en adelante
    # Usamos .iloc[0] para tomar la primera (y única) fila de cada atributo MO
    aas_ids = aas_id_row.iloc[0, 2:].fillna('').astype(str).str.strip().tolist()
    shared_values = shared_row.iloc[0, 2:].fillna('').astype(str).str.strip().tolist()
    
    # Combinar los IDs y los valores en un diccionario {AAS-ID: isSharedValue}
    # Solo tomamos IDs que son válidos
    aas_data = {
        aas_id: shared_values[i] 
        for i, aas_id in enumerate(aas_ids) 
        if aas_id and aas_id.lower() not in ('nan', 'none', '') and i < len(shared_values)
    }

    if not aas_data:
        return "// WARNING: No se encontraron IDs válidos de AAS (AAS-1, AAS-2, etc.) en el RND. Output vacío."

    # 4. Generación del MML
    mml_output = "confb+\ngs+\n\n"
    mml_output += "set NodeSupport=1,MpClusterHandling=1 primaryCoreRef FieldReplaceableUnit=BB-1\n"
    mml_output += "################################################################\n"
    mml_output += "## FieldReplaceableUnit V2 \n"
    mml_output += "################################################################"
    
    for aas_id, shared_value in aas_data.items():
        
        # Bloques CR/CRN estáticos (MML de plantilla)
        mml_output += f"""
cr {MO_PATH_AAS_PREFIX}{aas_id}
crn {MO_PATH_AAS_PREFIX}{aas_id},Transceiver=1
maxTotalTilt 900
mechanicalAntennaTilt 0
minTotalTilt -900
retSubUnitRef
end

crn {MO_PATH_AAS_PREFIX}{aas_id},Transceiver=1,AasData=1
antSegmentation 1
end

cr {MO_PATH_AAS_PREFIX}{aas_id},RiPort=DATA_1
cr {MO_PATH_AAS_PREFIX}{aas_id},RiPort=DATA_1,RiEthernetPort=1
cr {MO_PATH_AAS_PREFIX}{aas_id},RiPort=DATA_2
cr {MO_PATH_AAS_PREFIX}{aas_id},RiPort=DATA_2,RiEthernetPort=1
"""
        
        # Comando SET DINÁMICO: set Equipment=1,FieldReplaceableUnit=AAS-X isSharedWithExternalMe true
        if shared_value.lower() == 'true':
            mml_output += f"\nset {MO_PATH_AAS_PREFIX}{aas_id} {ATTR_SHARED} true"
        
        mml_output += "\n"
        
    return mml_output.strip()

# =====================================================================
# GENERACIÓN DE COMANDOS SectorEquipmentFunction (DINÁMICO - CRN/END)
# =====================================================================

def generate_sector_equipment_function_mml(df_equipment: pd.DataFrame) -> str:
    """
    Genera comandos SectorEquipmentFunction en formato CRN/END, extrayendo IDs y atributos del RND.
    """
    
    # Constantes específicas de SEF (tomadas de las constantes globales)
    MO_NAME_SEF = "SectorEquipmentFunction"
    # El prefijo para el comando MML (CRN NodeSupport=1,SectorEquipmentFunction=ID)
    MO_PATH_SEF_PREFIX = "NodeSupport=1,SectorEquipmentFunction="
    
    # 1. Filtrar filas relevantes
    df_sef = df_equipment[df_equipment.iloc[:, 0].astype(str).str.strip().str.contains(MO_NAME_SEF, na=False, regex=False)].copy()
    
    if df_sef.empty or df_sef.shape[1] < 3:
        return "// WARNING: No se encontraron datos válidos de SectorEquipmentFunction en Equipment-Configuration."

    atributo_col_index = 1
    mml_output = "\n\n################################################################\n## SectorEquipmentFunction V2 \n################################################################"

    # Fila que contiene los IDs de SEF.
    # CORRECCIÓN: En el RND, esta fila aparece como 'NodeSupport=1,SectorEquipmentFunction='
    # Buscamos la fila que coincida exactamente O que termine en 'SectorEquipmentFunction=' para ser más robustos.
    
    # Opción 1: Búsqueda exacta (basada en debug)
    target_id_label = "NodeSupport=1,SectorEquipmentFunction="
    sef_id_row = df_sef[df_sef.iloc[:, atributo_col_index].astype(str).str.strip() == target_id_label]
    
    # Opción 2: Si falla la exacta, buscar por sufijo (fallback)
    if sef_id_row.empty:
         sef_id_row = df_sef[df_sef.iloc[:, atributo_col_index].astype(str).str.strip().str.endswith(f'{MO_NAME_SEF}=')]

    if sef_id_row.empty:
        return f"// ERROR: Faltan las filas de IDs ({target_id_label}) en el RND."

    # IDs extraídos (75, 76, 77...)
    sef_ids = sef_id_row.iloc[0, 2:].fillna('').astype(str).str.strip().tolist()
    
    # 2. Generación del MML
    for i, sef_id in enumerate(sef_ids):
        sef_id = sef_id.strip()
        if not sef_id or sef_id.lower() in ('nan', 'none', ''):
            continue
            
        # Función auxiliar local para extraer el valor de un atributo para un sector (columna 2 + index)
        def _get_attr_val(attribute_name: str) -> str:
            attr_row = df_sef[df_sef.iloc[:, atributo_col_index].astype(str).str.strip() == attribute_name]
            if attr_row.empty:
                return ""
            if 2 + i < attr_row.shape[1]:
                value = str(attr_row.iloc[0, 2 + i]).strip()
                # Solo tomamos valores que no son NaN o cadenas vacías
                return value if value.lower() not in ('nan', 'none', '') else ""
            return ""

        # Extraer valores dinámicos
        administrative_state = _get_attr_val("administrativeState")
        rf_branch_ref = _get_attr_val("rfBranchRef")
        user_label = _get_attr_val("userLabel")

        # 2.2. Construir el bloque CRN/END
        # Usamos MO_PATH_SEF_PREFIX que ya incluye "NodeSupport=1,SectorEquipmentFunction="
        mml_output += f"\n\ncrn {MO_PATH_SEF_PREFIX}{sef_id}"
        
        # administrativeState
        if administrative_state:
            mml_output += f"\nadministrativeState {administrative_state}"
            
        # rfBranchRef (Referencia a AAS)
        if rf_branch_ref:
            mml_output += f"\nrfBranchRef {rf_branch_ref}"
        
        # userLabel
        if user_label:
            mml_output += f"\nuserLabel {user_label}"
            
        mml_output += "\nend"
            
    return mml_output

# =====================================================================
# GENERACIÓN DE COMANDOS NRSectorCarrier (DINÁMICO)
# =====================================================================

def generate_nr_sector_carrier_mml(instance_data: Dict[str, Dict[str, str]]) -> str:
    """
    Genera comandos para NRSectorCarrier (CRN/END) usando los datos de la instancia.
    """
    attributes = instance_data.get(MO_VAR_NR_SECTOR_CARRIER, {})
    if not attributes:
        return ""
        
    # Obtener ID del MO. 
    # Prioridad 1: Atributo 'nRSectorCarrierId'
    # Prioridad 2: ID extraído del header de la columna (_id_from_header)
    mo_id = attributes.get('nRSectorCarrierId') or attributes.get('_id_from_header')
    
    if not mo_id:
        return f"// WARNING: No se encontró ID para {MO_VAR_NR_SECTOR_CARRIER}"

    mml_output = []
    
    mo_full_path = f"{MO_PATH_DU_BASE},{MO_VAR_NR_SECTOR_CARRIER}={mo_id}"
    
    mml_output.append(f"\ncrn {mo_full_path}")
    
    # Lista de atributos a incluir en orden específico (basado en el ejemplo del usuario)
    ordered_attrs = [
        'administrativeState',
        'altitude',
        'arfcnDL',
        'bSChannelBwDL',
        'bSChannelBwUL',
        'configuredMaxTxPower',
        # 'coverage' se maneja especial
        'latitude',
        'longitude',
        'nullSteeringMode',
        'radioTransmitPerfMode',
        'arfcnUL',
        'sectorEquipmentFunctionRef',
        'txDirection',
        'txPowerChangeRate',
        'txPowerPersistentLock',
        'txPowerRatio',
        'noOfRxAntennas',
        'noOfTxAntennas',
        'nRMicroSleepTxEnabled'
    ]
    
    for attr in ordered_attrs:
        val = attributes.get(attr)
        if val:
            mml_output.append(f"{attr} {val}")
            
    # Manejo especial de COVERAGE
    # El usuario quiere: coverage bearing=X,openingAngle=1,radius=1
    # En el RND tenemos 'coverage_bearing'.
    bearing = attributes.get('coverage_bearing')
    if bearing:
        mml_output.insert(6, f"coverage bearing={bearing},openingAngle=1,radius=1") # Insertar en la posición correcta aprox
        
    mml_output.append("end\n")
        
    return "\n".join(mml_output)

# =====================================================================
# GENERACIÓN DE COMANDOS NRCellDU (DINÁMICO)
# =====================================================================

def generate_nr_cell_du_mml(instance_data: Dict[str, Dict[str, str]]) -> str:
    """
    Genera comandos para NRCellDU (CRN/END + LSET) usando los datos de la instancia.
    """
    attributes = instance_data.get(MO_VAR_NR_CELL_DU, {})
    if not attributes:
        return ""
        
    # Obtener ID del MO desde la fila GNBDUFunction=1,NRCellDU=
    mo_id = attributes.get('GNBDUFunction=1,NRCellDU=') or attributes.get('_id_from_header')
    
    if not mo_id:
        return f"// WARNING: No se encontró ID para {MO_VAR_NR_CELL_DU}"

    mml_output = []
    
    # Bloque CRN inicial con atributos básicos
    mo_full_path = f"{MO_PATH_DU_BASE},{MO_VAR_NR_CELL_DU}={mo_id}"
    
    mml_output.append(f"\ncrn {mo_full_path}")
    
    # 1. Atributos que van ANTES de pLMNIdList
    crn_attrs_antes_plmn = ['cellLocalId', 'nRPCI', 'nRTAC']
    
    for attr in crn_attrs_antes_plmn:
        val = attributes.get(attr)
        if val:
            mml_output.append(f"{attr} {val}")
    
    # 2. Manejo especial de pLMNIdList (NUEVA POSICIÓN)
    mcc = attributes.get('pLMNIdList_mcc')
    mnc = attributes.get('pLMNIdList_mnc')
    if mcc and mnc:
        # Este se inserta justo después de nRTAC y antes del siguiente loop
        mml_output.append(f"pLMNIdList  mcc={mcc},mnc={mnc}")
    
    # 3. Atributos que van DESPUÉS de pLMNIdList
    crn_attrs_despues_plmn = [
        'nRSectorCarrierRef', 
        'subCarrierSpacing', 
        'ssbSubCarrierSpacing', 
        'tddUlDlPattern', 
        'tddSpecialSlotPattern'
    ]
    
    for attr in crn_attrs_despues_plmn:
        val = attributes.get(attr)
        if val:
            mml_output.append(f"{attr} {val}")
    
    mml_output.append("end\n")
    
    # Bloques LSET para todos los demás atributos
    # Diccionario de atributos compuestos que necesitan formato especial
    composite_attrs = {
        'csiRsActivePortConfig': lambda attrs: f"{attrs.get('csiRsActivePortConfig', '')}",
        'csiRsConfig16P': lambda attrs: f"csiRsControl16Ports={attrs.get('csiRsConfig16P_csiRsControl16Ports', '')}",
        'csiRsConfig2P': lambda attrs: f"aRestriction={attrs.get('csiRsConfig2P_aRestriction', '')},csiRsControl2Ports={attrs.get('csiRsConfig2P_csiRsControl2Ports', '')}",
        'csiRsConfig32P': lambda attrs: f"csiRsControl32Ports={attrs.get('csiRsConfig32P_csiRsControl32Ports', '')},i11Restriction={attrs.get('csiRsConfig32P_i11Restriction', '')},i12Restriction={attrs.get('csiRsConfig32P_i12Restriction', '')}",
        'csiRsConfig4P': lambda attrs: f"csiRsControl4Ports={attrs.get('csiRsConfig4P_csiRsControl4Ports', '')},i11Restriction={attrs.get('csiRsConfig4P_i11Restriction', '')}",
        'csiRsConfig8P': lambda attrs: f"csiRsControl8Ports={attrs.get('csiRsConfig8P_csiRsControl8Ports', '')},i11Restriction={attrs.get('csiRsConfig8P_i11Restriction', '')}",
        'sibType2': lambda attrs: f"siBroadcastStatus={attrs.get('sibType2_siBroadcastStatus', '')},siPeriodicity={attrs.get('sibType2_siPeriodicity', '')}",
        'sibType4': lambda attrs: f"siBroadcastStatus={attrs.get('sibType4_siBroadcastStatus', '')},siPeriodicity={attrs.get('sibType4_siPeriodicity', '')}",
        'sibType5': lambda attrs: f"siBroadcastStatus={attrs.get('sibType5_siBroadcastStatus', '')},siPeriodicity={attrs.get('sibType5_siPeriodicity', '')}",
        'sibType6': lambda attrs: f"siBroadcastStatus={attrs.get('sibType6_siBroadcastStatus', '')},siPeriodicity={attrs.get('sibType6_siPeriodicity', '')}",
        'sibType7': lambda attrs: f"siBroadcastStatus={attrs.get('sibType7_siBroadcastStatus', '')},siPeriodicity={attrs.get('sibType7_siPeriodicity', '')}",
        'sibType8': lambda attrs: f"siBroadcastStatus={attrs.get('sibType8_siBroadcastStatus', '')},siPeriodicity={attrs.get('sibType8_siPeriodicity', '')}",
    }
    
    # Lista de atributos simples para LSET (en el orden del ejemplo del usuario)
    lset_attrs = [
        'advancedDlSuMimoEnabled', 'maxNoOfAdvancedDlMuMimoLayers', 'ailgDlPrbLoadLevel',
        'ailgModType', 'ailgPdcchLoadLevel', 'bandListManual', 'cellBarred', 'cellLocalId',
        'cellRange', 'cellReservedForOperator', 'cellState', 'csiReportFormat',
        'csiRsActivePortConfig', 'csiRsPeriodicity', 'csiRsShiftingPrimary', 'csiRsShiftingSecondary',
        'dftSOfdmMsg3Enabled', 'dftSOfdmPuschEnabled', 'dftSOfdmPuschStartRsrpThresh',
        'dl256QamEnabled', 'dlMaxMuMimoLayers', 'dlRobustLaEnabled', 'dlStartCrb',
        'maxUeSpeed', 'nCI', 'nRCellDUId', 'nRPCI', 'nRTAC',
        'pdschAllowedInDmrsSym', 'pMax', 'pZeroNomPucch', 'pZeroNomPuschGrant',
        'pZeroNomSrs', 'pZeroUePuschOffset256Qam', 'pdschStartPrbStrategy', 'puschStartPrbStrategy',
        'pwsBroadcastOngoing', 'qQualMin', 'qQualMinOffset', 'qRxLevMin', 'qRxLevMinOffset',
        'rachPreambleFormat', 'rachPreambleRecTargetPower', 'rachPreambleTransMax', 'rachRootSequence',
        'secondaryCellOnly', 'siWindowLength', 'srsPeriodicity', 'ssbDuration', 'ssbFrequency',
        'ssbFrequencyAutoSelected', 'ssbOffset', 'ssbPeriodicity', 'ssbPowerBoost',
        'tddUlDlPattern', 'trsPeriodicity', 'trsPowerBoosting', 'ul256QamEnabled',
        'ulMaxMuMimoLayers', 'ulRobustLaEnabled', 'ulStartCrb', 'nrLteCoexistence',
        'userLabel', 'puschAllowedInDmrsSym', 'srsHoppingBandwidth', 'sfnOffset',
        'trsResourceShifting', 'pdcchLaSinrOffset', 'dlDmrsMuxSinrThresh',
        'drxProfileEnabled', 'drxProfileRef'
    ]
    
    # Generar comandos LSET para atributos simples
    for attr in lset_attrs:
        val = attributes.get(attr)
        if val and val.lower() not in ('nan', 'none', ''):
            mml_output.append(f"lset {MO_VAR_NR_CELL_DU}={mo_id} {attr} {val}")
    
    # Generar comandos LSET para atributos compuestos
    for comp_attr, formatter in composite_attrs.items():
        formatted_val = formatter(attributes)
        # Solo agregar si tiene contenido válido (no solo comas y =)
        if formatted_val and not all(c in '=,' for c in formatted_val.replace(' ', '')):
            mml_output.append(f"lset {MO_VAR_NR_CELL_DU}={mo_id} {comp_attr} {formatted_val}")
    
    mml_output.append("")  # Línea en blanco al final
    
    return "\n".join(mml_output)

# =====================================================================
# GENERACIÓN DE COMANDOS NRCellCU (DINÁMICO)
# =====================================================================

def generate_nr_cell_cu_mml(instance_data: Dict[str, Dict[str, str]]) -> str:
    """
    Genera comandos para NRCellCU (CR + cellLocalId + SET + LSET) usando los datos de la instancia.
    """
    attributes = instance_data.get(MO_VAR_NR_CELL_CU, {})
    if not attributes:
        return ""
        
    # Obtener ID del MO desde la fila GNBCUCPFunction=1,NRCellCU=
    mo_id = attributes.get('GNBCUCPFunction=1,NRCellCU=') or attributes.get('_id_from_header')
    
    if not mo_id:
        return f"// WARNING: No se encontró ID para {MO_VAR_NR_CELL_CU}"

    mml_output = []
    
    # Bloque CR inicial
    mo_full_path = f"{MO_PATH_CUCP_BASE},{MO_VAR_NR_CELL_CU}={mo_id}"
    
    mml_output.append(f"\ncr {mo_full_path}")
    
    # Línea con cellLocalId (número solo)
    cell_local_id = attributes.get('cellLocalId', '')
    if cell_local_id:
        mml_output.append(cell_local_id)
    
    # Comando SET para primaryPLMNId (compuesto: mcc y mnc)
    mcc = attributes.get('primaryPLMNId_mcc')
    mnc = attributes.get('primaryPLMNId_mnc')
    if mcc and mnc:
        mml_output.append(f"set {mo_full_path} primaryPLMNId mcc={mcc},mnc={mnc}")
    
    # Lista de atributos para LSET (en el orden del ejemplo del usuario)
    lset_attrs = [
        'nRFrequencyRef',
        'cellState',
        'intraFreqMCCellProfileRef',
        'mcpcPSCellEnabled',
        'mcpcPSCellProfileRef',
        'nCI',
        'nRCellCUId',
        'nRTAC',
        'pSCellCapable',
        'qHyst',
        'sNonIntraSearchP',
        'threshServingLowP',
        'transmitSib2',
        'transmitSib4',
        'transmitSib5',
        'userLabel'
    ]
    
    # Generar comandos LSET
    for attr in lset_attrs:
        val = attributes.get(attr)
        if val and val.lower() not in ('nan', 'none', ''):
            mml_output.append(f"lset {MO_VAR_NR_CELL_CU}={mo_id} {attr} {val}")
    
    mml_output.append("")  # Línea en blanco al final
    
    return "\n".join(mml_output)

# =====================================================================
# GENERACIÓN DE COMANDOS CommonBeamforming (DINÁMICO)
# =====================================================================

def generate_common_beamforming_mml(df_equipment: pd.DataFrame) -> str:
    """
    Genera comandos para CommonBeamforming (CR/LSET/END) extrayendo atributos del RND.
    Lee los valores desde la hoja Equipment-Configuration.
    """
    
    # Constantes específicas de CBF
    MO_NAME_CBF = "CommonBeamforming"
    
    # 1. Filtrar filas relevantes
    df_cbf = df_equipment[df_equipment.iloc[:, 0].astype(str).str.strip().str.contains(MO_NAME_CBF, na=False, regex=False)].copy()
    
    if df_cbf.empty or df_cbf.shape[1] < 3:
        return "// WARNING: No se encontraron datos válidos de CommonBeamforming en Equipment-Configuration."

    atributo_col_index = 1
    mml_output = ""
    
    # Extraer valores de cada atributo para cada instancia (columnas 2+)
    num_instances = df_cbf.shape[1] - 2  # Columnas de instancias
    
    for i in range(num_instances):
        instance_id = str(i + 1)  # IDs: 1, 2, 3...
        
        # Función auxiliar local para extraer el valor de un atributo para una instancia
        def _get_attr_val(attribute_name: str) -> str:
            attr_row = df_cbf[df_cbf.iloc[:, atributo_col_index].astype(str).str.strip() == attribute_name]
            if attr_row.empty:
                return ""
            if 2 + i < attr_row.shape[1]:
                value = str(attr_row.iloc[0, 2 + i]).strip()
                return value if value.lower() not in ('nan', 'none', '') else ""
            return ""
        
        # Extraer valores dinámicos
        cbf_macro_taper = _get_attr_val('cbfMacroTaperType')
        coverage_shape = _get_attr_val('coverageShape')
        digital_tilt = _get_attr_val('digitalTilt')
        used_digital_tilt = _get_attr_val('usedDigitalTilt')
        used_digital_pan = _get_attr_val('usedDigitalPan')
        
        # VALIDACIÓN: Solo generar si al menos un atributo tiene valor
        # Esto evita crear bloques vacíos para instancias que no existen
        has_data = any([cbf_macro_taper, coverage_shape, digital_tilt, used_digital_tilt, used_digital_pan])
        
        if not has_data:
            continue  # Saltar esta instancia si no tiene datos
        
        # Construir el path completo del MO
        mo_full_path = f"{MO_PATH_DU_BASE},{MO_VAR_NR_SECTOR_CARRIER}={instance_id},CommonBeamforming=1"
        
        # Generar MML
        mml_output += f"\ncr {mo_full_path}\n"
        
        if cbf_macro_taper:
            mml_output += f"lset {mo_full_path} cbfMacroTaperType {cbf_macro_taper}\n"
        if coverage_shape:
            mml_output += f"lset {mo_full_path} coverageShape {coverage_shape}\n"
        if digital_tilt:
            mml_output += f"lset {mo_full_path} digitalTilt {digital_tilt}\n"
        if used_digital_tilt:
            mml_output += f"lset {mo_full_path} usedDigitalTilt {used_digital_tilt}\n"
        if used_digital_pan:
            mml_output += f"lset {mo_full_path} usedDigitalPan {used_digital_pan}\n"
            
        mml_output += "end\n"
    
    return mml_output

# =====================================================================
# FUNCIÓN PRINCIPAL DE GENERACIÓN
# =====================================================================

def generar_carrier_cell_mos_5g(
    nemonico: str, 
    wsh_data: Dict[str, Any], 
    rnd_data: Dict[str, pd.DataFrame]
) -> str:
    """
    Función principal que orquesta la generación del script Carrier/Cell MOS.
    Genera AAS, SectorEquipmentFunction, NRSectorCarrier, NRCellDU, CommonBeamforming y NRCellCU.
    """
    
    mos_content = f"// ====================================================================\n"
    mos_content += f"// 02_{nemonico}_NR_HW_CELL.mos - Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    mos_content += f"// AUTOR: PIERO LEDESMA\n"
    mos_content += f"// Nemonico: {nemonico}\n"
    mos_content += f"// ====================================================================\n\n"
    
    # 1. GENERAR BLOQUE AAS/FieldReplaceableUnit (DINÁMICO Y ÚNICO)
    df_equipment = rnd_data.get('Equipment-Configuration')
    if df_equipment is not None:
        mos_content += generate_aas_mml(df_equipment)
        mos_content += "\n" 
        
        # 2. GENERAR BLOQUE SEF/SectorEquipmentFunction (DINÁMICO Y ÚNICO)
        mos_content += generate_sector_equipment_function_mml(df_equipment) 
        mos_content += "\n" 
    else:
        mos_content += "// WARNING: No se encontró 'Equipment-Configuration' para AAS/SEF.\n"
        
    mos_content += "\n"

    # 3. GENERAR BLOQUE NRSectorCarrier (DINÁMICO POR INSTANCIA)
    df_cell_carrier = rnd_data.get('Cell-Carrier')
    if df_cell_carrier is not None:
        mos_content += "\n################################################################\n"
        mos_content += "## NRSectorCarrier V2 \n"
        mos_content += "################################################################\n\n"
        
        instances = parse_cell_carrier_data(df_cell_carrier)
        
        for instance_data in instances:
            mos_content += generate_nr_sector_carrier_mml(instance_data)
            
    else:
        mos_content += "// WARNING: No se encontró 'Cell-Carrier' para generar NRSectorCarrier.\n"
    
    # 4. GENERAR BLOQUE CommonBeamforming (DINÁMICO DESDE EQUIPMENT-CONFIGURATION)
    if df_equipment is not None:
        mos_content += "\n################################################################\n"
        mos_content += "## CommonBeamforming V2 \n"
        mos_content += "################################################################            \n\n"
        
        mos_content += generate_common_beamforming_mml(df_equipment)
    
    # 5. GENERAR BLOQUE NRCellDU (DINÁMICO POR INSTANCIA)
    if df_cell_carrier is not None:
        mos_content += "\n################################################################\n"
        mos_content += "## GNBDUFunction->NRCellDU V2 \n"
        mos_content += "################################################################\n\n"
        mos_content += "bl cell\n"
        
        for instance_data in instances:
            mos_content += generate_nr_cell_du_mml(instance_data)
    
    # 6. GENERAR BLOQUE NRCellCU (DINÁMICO POR INSTANCIA)
    if df_cell_carrier is not None:
        mos_content += "\n################################################################\n"
        mos_content += "## GNBCUCPFunction -> NRCellCU V2 \n"
        mos_content += "################################################################\n"
        
        for instance_data in instances:
            mos_content += generate_nr_cell_cu_mml(instance_data)
    
    # 7. FOOTER DEL SCRIPT
    mos_content += "\n\ngs-\n"
    mos_content += "confb-\n"
    mos_content += f"cvms PL_NRCELL_HW_{nemonico}\n"
    mos_content += "############ FIN SCRIPT #############\n"
    
    return mos_content.strip()