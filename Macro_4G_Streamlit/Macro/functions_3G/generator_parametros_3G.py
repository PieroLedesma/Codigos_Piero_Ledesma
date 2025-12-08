# =====================================================================
# generator_parametros_3G.py - Generación de script Parametros MOS para 3G WCDMA
# =====================================================================

from typing import Tuple, Dict, Any, Optional
from datetime import datetime
try:
    from .feature_mapping import FEATURE_MAPPING
except ImportError:
    # Fallback for direct execution or different path structure
    from functions_3G.feature_mapping import FEATURE_MAPPING


# =====================================================================
# CONSTANTES DE CONFIGURACIÓN
# =====================================================================

OUTPUT_FILENAME = "02_Nemonico_PL_Parametros.mos"


# =====================================================================
# FUNCIÓN PRINCIPAL DE GENERACIÓN
# =====================================================================

def generate_parametros_mos(nemonico: str, wsh_data: Optional[Dict[str, Any]] = None, rnd_data: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, str]:
    """
    Genera el contenido del archivo MOS de Parámetros para 3G WCDMA.
    
    Args:
        nemonico: Nombre del sitio
        wsh_data: Diccionario con datos del WSH (opcional)
        
    Returns:
        Tuple con (success, contenido_mos, mensaje)
    """
    try:
        # Generar contenido del MOS
        mos_content = generate_parametros_mml(nemonico, wsh_data, rnd_data)
        
        return True, mos_content, f"Parámetros generados exitosamente para {nemonico}"
        
    except Exception as e:
        return False, "", f"Error al generar archivo Parámetros: {str(e)}"


def generate_parametros_mml(nemonico: str, wsh_data: Optional[Dict[str, Any]] = None, rnd_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Genera el contenido MML completo del script Parámetros.
    """
    mml_output = []
    
    # ============================================================
    # ENCABEZADO
    # ============================================================
    mml_output.append(generate_header(nemonico))
    
    # ============================================================
    # COMANDOS INICIALES ESTÁTICOS
    # ============================================================
    mml_output.append(generate_initial_commands())
    
    # ============================================================
    # SECCIÓN ESTÁTICA: Feature States
    # ============================================================
    mml_output.append(generate_feature_states())
    
    # ============================================================
    # SECCIÓN DINÁMICA: VLAN WCDMA
    # ============================================================
    mml_output.append(generate_vlan_wcdma_section(wsh_data))
    
    # ============================================================
    # SECCIÓN DINÁMICA: Router WCDMA
    # ============================================================
    mml_output.append(generate_router_wcdma_section(wsh_data))
    
    # ============================================================
    # SECCIÓN ESTÁTICA: SctpEndpoint NBAP WCDMA
    # ============================================================
    mml_output.append(generate_sctpendpoint_nbap_section())
    
    # ============================================================
    # SECCIÓN DINÁMICA: NodeBFunction WCDMA
    # ============================================================
    mml_output.append(generate_nodebfunction_wcdma_section(rnd_data))
    
    # ============================================================
    # SECCIÓN DINÁMICA: Iub WCDMA
    # ============================================================
    mml_output.append(generate_iub_wcdma_section(rnd_data))
    
    # ============================================================
    # SECCIÓN SEMI-ESTÁTICA: NbapCommon - NbapDedicated WCDMA
    # ============================================================
    mml_output.append(generate_nbap_common_dedicated_section(rnd_data))
    
    # ============================================================
    # SECCIÓN SEMI-ESTÁTICA: NodeBLocalCellGroup WCDMA
    # ============================================================
    mml_output.append(generate_nodeblocalcellgroup_section(nemonico))
    
    # ============================================================
    # SECCIÓN DINÁMICA: NodeBLocalCell WCDMA
    # ============================================================
    mml_output.append(generate_nodeblocalcell_wcdma_section(rnd_data))
    
    # ============================================================
    # SECCIÓN DINÁMICA: NodeBSectorCarrier WCDMA
    # ============================================================
    mml_output.append(generate_nodebsectorcarrier_wcdma_section(rnd_data))
    
    # ============================================================
    # SECCIÓN DINÁMICA: Features WCDMA
    # ============================================================
    mml_output.append(generate_features_wcdma_section(rnd_data))
    
    # ============================================================
    # CIERRE DE SCRIPT
    # ============================================================
    mml_output.append(generate_closing_commands(nemonico))
    
    return "\n".join(mml_output)


# =====================================================================
# GENERACIÓN DE ENCABEZADO
# =====================================================================

def generate_header(nemonico: str) -> str:
    """
    Genera el encabezado del script con información dinámica.
    """
    now = datetime.now()
    hora = now.strftime("%H:%M:%S")
    fecha = now.strftime("%d-%m-%Y")
    
    header = f"""/////////////////////////////////////////////////////////////
//
// SCRIPT     : Parametros
// AUTOR      : PIERO LEDESMA
// NEMONICO   : {nemonico}
// HORA       : {hora}
// FECHA      : {fecha}
//
/////////////////////////////////////////////////////////////
"""
    return header


# =====================================================================
# COMANDOS INICIALES
# =====================================================================

def generate_initial_commands() -> str:
    """
    Genera los comandos iniciales del script.
    """
    commands = """
confb+
gs+
lt all
lt all
"""
    return commands.strip()


# =====================================================================
# FEATURE STATES (ESTÁTICA)
# =====================================================================

def generate_feature_states() -> str:
    """
    Genera la configuración estática de feature states.
    """
    mml_output = []
    
    mml_output.append("\nset  CXC4011018 featurestate 1")
    mml_output.append("set  CXC4012015 featurestate 1")
    mml_output.append("set  CXC4012016 featurestate 1")
    mml_output.append("set  CXC4020051 featurestate 1")
    
    return "\n".join(mml_output)


# =====================================================================
# NodeBFunction WCDMA (DINÁMICA)
# =====================================================================

def generate_nodebfunction_wcdma_section(rnd_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Genera la sección NodeBFunction WCDMA con valores del RND.
    """
    mml_output = []
    
    mml_output.append("\n#############################################################")
    mml_output.append("### NodeBFunction WCDMA                    ")
    mml_output.append("#############################################################")
    mml_output.append("lt all\n")
    
    # Valores por defecto (VACÍOS para detectar errores)
    params = {
        'eul2msFirstSchedStep': '',
        'eulDchMaxAllowedSchRate': '',
        'eulInactivityHighRateTime': '',
        'eulInactivityLowRateTime': '',
        'eulLowRate': '',
        'eulLowUsageTime': '',
        'eulMaxAllowedSchRate': '',
        'eulMaxShoRate': '',
        'eulMaxTotalProtectedRate': '',
        'eulNonServHwRate': '',
        'eulNoReschUsers': '',
        'eulSchedulingWeight': '',
        'eulTargetRate': '',
        'nbapDscp': ''
    }
    
    # Intentar leer del RND
    # La llave en rnd_data viene de data_reader_3G.py que usa .title(), así que probablemente sea 'Nodebfunction'
    df = None
    if rnd_data:
        # Buscar la llave correcta ignorando mayúsculas/minúsculas
        for key in rnd_data.keys():
            if key.lower() == 'nodebfunction':
                df = rnd_data[key]
                print(f"DEBUG: Found NodeBFunction data in key: {key}")
                break
        
        if df is None:
             print(f"DEBUG: NodeBFunction sheet not found in rnd_data keys: {list(rnd_data.keys())}")

    if df is not None:
        if not df.empty:
            # Asumimos que la primera fila tiene los valores, similar a la imagen
            # Iteramos sobre las columnas que nos interesan
            for key in params.keys():
                # Buscar columna que coincida (case insensitive)
                col_match = None
                for col in df.columns:
                    if col.strip().lower() == key.lower():
                        col_match = col
                        break
                
                if col_match:
                    val = str(df.iloc[0][col_match]).strip()
                    if val and val.lower() != 'nan':
                        # Si es float (ej: 160.0), convertir a int string
                        if val.replace('.','',1).isdigit() and '.' in val:
                            try:
                                val = str(int(float(val)))
                            except:
                                pass
                        params[key] = val
    
    mml_output.append("cr NodeBFunction=1")
    
    site_val = "" # Default fallback
    if df is not None:
        for col in df.columns:
            if col.strip().lower() == 'site':
                val = str(df.iloc[0][col]).strip()
                if val and val.lower() != 'nan':
                    site_val = val
                break
    
    mml_output.append(f"set NodeBFunction=1 Site {site_val}")
    
    # Orden específico de parámetros según el ejemplo del usuario
    ordered_keys = [
        'eul2msFirstSchedStep',
        'eulDchMaxAllowedSchRate',
        'eulInactivityHighRateTime',
        'eulInactivityLowRateTime',
        'eulLowRate',
        'eulLowUsageTime',
        'eulMaxAllowedSchRate',
        'eulMaxShoRate',
        'eulMaxTotalProtectedRate',
        'eulNonServHwRate',
        'eulNoReschUsers',
        'eulSchedulingWeight',
        'eulTargetRate',
        'nbapDscp'
    ]
    
    for key in ordered_keys:
        val = params[key]
        # Si el valor es vacío, se pone solo el comando? 
        # En el ejemplo: set NodeBFunction=1 eulInactivityLowRateTime 
        # Parece que si está vacío, se imprime vacío.
        mml_output.append(f"set NodeBFunction=1 {key} {val}".strip())
        
    return "\n".join(mml_output)


# =====================================================================
# Iub WCDMA (DINÁMICA)
# =====================================================================

def generate_iub_wcdma_section(rnd_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Genera la sección Iub WCDMA con valores de Iublink e IubDataStreams del RND.
    """
    mml_output = []
    
    mml_output.append("\n#############################################################")
    mml_output.append("### Iub WCDMA                     ")
    mml_output.append("#############################################################")
    mml_output.append("lt all\n")
    
    # ---------------------------------------------------------
    # PARTE 1: Iublink
    # ---------------------------------------------------------
    
    # Valores por defecto (VACÍOS para detectar errores)
    iub_params = {
        'Site': '',
        'Iub': '',
        'dlHwAdm': '',
        'rbsId': '',
        'softCongThreshGbrBwDl': '',
        'softCongThreshGbrBwUl': '',
        'ulHwAdm': ''
    }
    
    df_iub = None
    if rnd_data:
        # Buscar hoja Iublink
        for key in rnd_data.keys():
            if key.lower() == 'iublink':
                df_iub = rnd_data[key]
                break
    
    if df_iub is not None and not df_iub.empty:
        for key in iub_params.keys():
            col_match = None
            for col in df_iub.columns:
                if col.strip().lower() == key.lower():
                    col_match = col
                    break
            
            if col_match:
                val = str(df_iub.iloc[0][col_match]).strip()
                if val and val.lower() != 'nan':
                     # Si es float, convertir a int string
                    if val.replace('.','',1).isdigit() and '.' in val:
                        try:
                            val = str(int(float(val)))
                        except:
                            pass
                    iub_params[key] = val

    iub_id = iub_params['Iub'] # Ej: Iub_ULA781
    rbs_id = iub_params['rbsId']
    
    if not iub_id:
        mml_output.append("# ERROR: No se encontró valor para 'Iub' en hoja Iublink")
    
    mml_output.append(f"cr NodeBFunction=1,Iub={iub_id}")
    mml_output.append("Router=WCDMA,InterfaceIPv4=1,AddressIPv4=1 #ipv4Address")
    mml_output.append(f"{rbs_id} #rbsId")
    
    iub_ordered_keys = [
        'Site',
        'Iub',
        'dlHwAdm',
        'rbsId',
        'softCongThreshGbrBwDl',
        'softCongThreshGbrBwUl',
        'ulHwAdm'
    ]
    
    for key in iub_ordered_keys:
        val = iub_params[key]
        mml_output.append(f"set NodeBFunction=1,Iub={iub_id} {key} {val}")
        
    mml_output.append("") # Separador
    
    # ---------------------------------------------------------
    # PARTE 2: IubDataStreams
    # ---------------------------------------------------------
    
    stream_params = {
        'Iub': '',
        'hsDataFrameDelayThreshold': '',
        'hsRbrDiscardProbability': '',
        'hsRbrWeight': '',
        'maxHsRate': '',
        'schHsFlowControlOnOff': '',
        'UserLabel': '',
        'noOfCommonStreams': '',
        'noOfDedicatedStreams': ''
    }
    
    df_stream = None
    if rnd_data:
        # Buscar hoja IubDataStreams
        for key in rnd_data.keys():
            if key.lower() == 'iubdatastreams':
                df_stream = rnd_data[key]
                break
                
    if df_stream is not None and not df_stream.empty:
        for key in stream_params.keys():
            col_match = None
            for col in df_stream.columns:
                if col.strip().lower() == key.lower():
                    col_match = col
                    break
            
            if col_match:
                val = str(df_stream.iloc[0][col_match]).strip()
                if val and val.lower() != 'nan':
                     # Si es float, convertir a int string (excepto si es una lista separada por espacios)
                    if val.replace('.','',1).isdigit() and '.' in val and ' ' not in val:
                        try:
                            val = str(int(float(val)))
                        except:
                            pass
                    stream_params[key] = val
    
    # Fallback: Si 'Iub' no vino en IubDataStreams, usar el mismo ID que en Iublink
    if not stream_params['Iub'] and iub_id:
        stream_params['Iub'] = iub_id
                    
    mml_output.append(f"cr NodeBFunction=1,Iub={iub_id},IubDataStreams=1")
    
    stream_ordered_keys = [
        'Iub',
        'hsDataFrameDelayThreshold',
        'hsRbrDiscardProbability',
        'hsRbrWeight',
        'maxHsRate',
        'schHsFlowControlOnOff',
        'UserLabel',
        'noOfCommonStreams',
        'noOfDedicatedStreams'
    ]
    
    for key in stream_ordered_keys:
        val = stream_params[key]
        mml_output.append(f"set NodeBFunction=1,Iub={iub_id},IubDataStreams=1 {key} {val}")

    return "\n".join(mml_output)


# =====================================================================
# NbapCommon - NbapDedicated WCDMA (SEMI-ESTÁTICA)
# =====================================================================

def generate_nbap_common_dedicated_section(rnd_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Genera la sección NbapCommon y NbapDedicated usando la variable Iub.
    """
    mml_output = []
    
    mml_output.append("\n#############################################################")
    mml_output.append("### NbapCommon - NbapDedicated WCDMA                       ")
    mml_output.append("#############################################################")
    mml_output.append("lt all\n")
    
    # Obtener Iub ID (mismo método que en Iub WCDMA)
    iub_id = ""
    if rnd_data:
        df_iub = None
        for key in rnd_data.keys():
            if key.lower() == 'iublink':
                df_iub = rnd_data[key]
                break
        
        if df_iub is not None and not df_iub.empty:
            # Buscar columna Iub
            for col in df_iub.columns:
                if col.strip().lower() == 'iub':
                    val = str(df_iub.iloc[0][col]).strip()
                    if val and val.lower() != 'nan':
                        iub_id = val
                    break
    
    if not iub_id:
         mml_output.append("# ERROR: No se encontró valor para 'Iub' en hoja Iublink para sección NBAP")
    
    # NbapCommon
    mml_output.append(f"cr NodeBFunction=1,Iub={iub_id},NbapCommon=1")
    mml_output.append("SctpEndpoint=NBAP-C #sctpEndpointRef")
    mml_output.append(f"lset NodeBFunction=1,Iub={iub_id},NbapCommon=1$ auditRetransmissionT 5")
    mml_output.append(f"lset NodeBFunction=1,Iub={iub_id},NbapCommon=1$ l3EstablishSupervisionT 302")
    mml_output.append(f"lset NodeBFunction=1,Iub={iub_id},NbapCommon=1$ userLabel\n")
    
    # NbapDedicated
    mml_output.append(f"cr NodeBFunction=1,Iub={iub_id},NbapDedicated=1")
    mml_output.append("SctpEndpoint=NBAP-D #sctpEndpointRef")
    mml_output.append(f"lset NodeBFunction=1,Iub={iub_id},NbapDedicated=1$ userLabel")
    
    return "\n".join(mml_output)


# =====================================================================
# NodeBLocalCellGroup WCDMA (SEMI-ESTÁTICA)
# =====================================================================

def generate_nodeblocalcellgroup_section(nemonico: str) -> str:
    """
    Genera la sección NodeBLocalCellGroup WCDMA usando el nemónico como userLabel.
    """
    mml_output = []
    
    mml_output.append("\n#############################################################")
    mml_output.append("### NodeBLocalCellGroup WCDMA                        ")
    mml_output.append("#############################################################")
    mml_output.append("lt all\n")
    
    mml_output.append("cr NodeBFunction=1,NodeBLocalCellGroup=1")
    mml_output.append("lset NodeBFunction=1,NodeBLocalCellGroup=1 administrativeState 1")
    mml_output.append("lset NodeBFunction=1,NodeBLocalCellGroup=1$ multiCarrierPair1")
    mml_output.append("lset NodeBFunction=1,NodeBLocalCellGroup=1$ multiCarrierPair2")
    mml_output.append("lset NodeBFunction=1,NodeBLocalCellGroup=1$ multiCarrierPair3")
    mml_output.append("lset NodeBFunction=1,NodeBLocalCellGroup=1$ multiCarrierPair4")
    mml_output.append("lset NodeBFunction=1,NodeBLocalCellGroup=1$ multiCarrierPair5")
    mml_output.append("lset NodeBFunction=1,NodeBLocalCellGroup=1$ multiCarrierPair6")
    mml_output.append(f"lset NodeBFunction=1,NodeBLocalCellGroup=1$ userLabel {nemonico}")
    
    return "\n".join(mml_output)


# =====================================================================
# NodeBLocalCell WCDMA (DINÁMICA)
# =====================================================================

def generate_nodeblocalcell_wcdma_section(rnd_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Genera la sección NodeBLocalCell WCDMA iterando sobre las celdas en la hoja NodeBLocalCell.
    """
    mml_output = []
    
    mml_output.append("\n#############################################################")
    mml_output.append("### NodeBLocalCell WCDMA                        ")
    mml_output.append("#############################################################")
    mml_output.append("lt all\n")
    
    df = None
    if rnd_data:
        for key in rnd_data.keys():
            if key.lower() == 'nodeblocalcell':
                df = rnd_data[key]
                break
    
    if df is None or df.empty:
        mml_output.append("# ERROR: No se encontró la hoja 'NodeBLocalCell' en el RND")
        return "\n".join(mml_output)
        
    # Lista de parámetros a configurar en el comando SET
    params_list = [
        'airRateTypeSelector', 'chQualOffset', 'cqiAdjustmentOn', 'cqiErrors', 'cqiErrorsAbsent',
        'defaultCqiHsFach', 'eHichMinCodePower', 'eulMaxNoSchEDch', 'eulMcActivationDelayTime',
        'eulMcCapability', 'eulMinMarginCoverage', 'eulNoERgchGroups', 'extraCompEnhUeDrx',
        'extraCompForSigHsFach', 'extraCompHsFach', 'extraHsScchCompEnhUeDrx',
        'extraHsScchCompForSigHsFach', 'extraHsScchCompHsFach', 'extraHsScchPowerForSrbOnHsdpa',
        'extraPowerForSrbOnHsdpa', 'hsdpaDbMcCapability', 'hsdpaMcActivityBufferThreshold',
        'hsdpaMcCapability', 'hsdpaMcInactivityTimer', 'hsdpaPowerSharingCapability',
        'hsPowerMargin', 'hsScchMaxCodePower', 'hsScchMinCodePower', 'localCellId',
        'maxDlPowerCapability', 'maxEAgchPowerDl', 'maxEAgchPowerDlTti2', 'maxNumEulUsers',
        'maxNumHsdpaUsers', 'maxNumHsPdschCodes', 'maxUserEHichERgchPowerDl',
        'maxUserEHichPowerDlTti2', 'minBitRate', 'minBitRateMinCqi', 'minDlPowerCapability',
        'minSpreadingFactor', 'powerSharingMaxTransmissionPower', 'qualityCheckPower',
        'qualityCheckPowerEHich', 'queueSelectAlgorithm', 'schCongPeriodGbr', 'schCongThreshGbr',
        'schCongThreshNonGbr', 'schMaxDelay', 'schMinPowerNonGbrHsUsers', 'schNoCongPeriodGbr',
        'schNoCongThreshGbr', 'schPowerDeltaCongGbr', 'schPrioForAbsResSharing', 'schWeight',
        'featCtrlEnhUeDrx', 'featCtrlEnhancedLayer2', 'featCtrlEulMc', 'featCtrlFDpchSrbOnHsdpa',
        'featCtrlHsFach', 'featCtrlHsdpaDbMc', 'featCtrlHsdpaDynamicCodeAllocation',
        'featCtrlHsdpaIncrementalRedundancy', 'featCtrlHsdpaMc', 'featCtrlHsdpaMcInactCtrl',
        'featCtrlHsdpaPowerSharing', 'featCtrlImprovedLayer2', 'featCtrlNbir', 'uarfcnDL', 'uarfcnUL'
    ]
    
    for index, row in df.iterrows():
        # Extraer identificadores principales
        cell_id = ""
        local_cell_id = ""
        operating_band = ""
        uarfcn_dl = ""
        
        # Helper para buscar valor case-insensitive
        def get_val(row_data, col_name):
            for col in df.columns:
                if col.strip().lower() == col_name.lower():
                    val = str(row_data[col]).strip()
                    if val and val.lower() != 'nan':
                        # Convertir float a int string si es número entero
                        if val.replace('.','',1).isdigit() and '.' in val and ' ' not in val:
                            try:
                                val = str(int(float(val)))
                            except:
                                pass
                        return val
            return ""

        cell_id = get_val(row, 'NodeBLocalCellId') # Ej: S1C1
        local_cell_id = get_val(row, 'localCellId')
        operating_band = get_val(row, 'operatingBand')
        uarfcn_dl = get_val(row, 'uarfcnDL')
        
        if not cell_id:
            continue # Skip si no hay ID
            
        # Generar bloque CR
        mml_output.append(f"cr NodeBFunction=1,NodeBLocalCellGroup=1,NodeBLocalCell={cell_id}")
        mml_output.append(f"{local_cell_id} #localCellId")
        mml_output.append(f"{operating_band} #operatingBand")
        mml_output.append(f"{uarfcn_dl} #uarfcnDL\n")
        
        # Generar comandos SET
        for param in params_list:
            val = get_val(row, param)
            mml_output.append(f"set NodeBFunction=1,NodeBLocalCellGroup=1,NodeBLocalCell={cell_id} {param} {val}")
            
        mml_output.append("") # Separador entre celdas
        
    return "\n".join(mml_output)


# =====================================================================
# NodeBSectorCarrier WCDMA (DINÁMICA)
# =====================================================================

def generate_nodebsectorcarrier_wcdma_section(rnd_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Genera la sección NodeBSectorCarrier WCDMA iterando sobre las celdas en la hoja NodeBSectorCarrier.
    """
    mml_output = []
    
    mml_output.append("\n#############################################################")
    mml_output.append("### NodeBSectorCarrier WCDMA                        ")
    mml_output.append("#############################################################")
    mml_output.append("lt all\n")
    
    df = None
    if rnd_data:
        for key in rnd_data.keys():
            if key.lower() == 'nodebsectorcarrier':
                df = rnd_data[key]
                break
    
    if df is None or df.empty:
        mml_output.append("# ERROR: No se encontró la hoja 'NodeBSectorCarrier' en el RND")
        return "\n".join(mml_output)
        
    # Lista de parámetros a configurar en el comando SET
    params_list = [
        'Utrancell', 'NodeBSectorCarrierid', 'cellRange', 'BandwidthDL', 'eulLockedNoiseFloor',
        'eulMaxOwnUuLoad', 'eulMaxRotCoverage', 'eulNoiseFloorLock', 'eulThermalLevelPrior',
        'fccRotMarginHigh', 'fccRotMarginLow', 'maxDlPowerCapability', 'minDlPowerCapability',
        'numOfRxAntennas', 'numOfTxAntennas', 'BandwidthUL', 'nbirAlgorithm',
        'nbirFixedNotchPosition', 'beamdirection', 'configuredMaxTxPower', 'height',
        'numOfBranchWithNbir', 'latitude', 'longitude', 'latHemisphere'
    ]
    
    for index, row in df.iterrows():
        # Helper para buscar valor case-insensitive
        def get_val(row_data, col_name):
            for col in df.columns:
                if col.strip().lower() == col_name.lower():
                    val = str(row_data[col]).strip()
                    if val and val.lower() != 'nan':
                        # Convertir float a int string si es número entero
                        if val.replace('.','',1).isdigit() and '.' in val and ' ' not in val:
                            try:
                                val = str(int(float(val)))
                            except:
                                pass
                        return val
            return ""

        sector_carrier_id = get_val(row, 'NodeBSectorCarrierid') # Ej: S1C1
        num_rx = get_val(row, 'numOfRxAntennas')
        num_tx = get_val(row, 'numOfTxAntennas')
        
        if not sector_carrier_id:
            continue # Skip si no hay ID
            
        # Calcular SectorEquipmentFunctionRef basado en el ID (S1C1 -> 1, S2C1 -> 2)
        # Asumimos formato S{sector}C{carrier}
        sector_eq_ref = "1" # Default
        try:
            if 'S' in sector_carrier_id and 'C' in sector_carrier_id:
                sector_part = sector_carrier_id.split('S')[1].split('C')[0]
                if sector_part.isdigit():
                    sector_eq_ref = sector_part
        except:
            pass
            
        # Generar bloque CR
        # Nota: NodeBLocalCell se asume igual a NodeBSectorCarrierid según ejemplo
        mml_output.append(f"cr NodeBFunction=1,NodeBLocalCellGroup=1,NodeBLocalCell={sector_carrier_id},NodeBSectorCarrier={sector_carrier_id}")
        mml_output.append(f"{num_rx} #numOfRxAntennas")
        mml_output.append(f"{num_tx} #numOfTxAntennas")
        mml_output.append(f"SectorEquipmentFunction={sector_eq_ref} #sectorEquipmentFunctionRef\n")
        
        # Generar comandos SET
        for param in params_list:
            val = get_val(row, param)
            
            # Formateo especial para latitude y longitude (quitar decimales si existen)
            if param in ['latitude', 'longitude']:
                if ',' in val:
                    val = val.split(',')[0]
                elif '.' in val:
                    val = val.split('.')[0]
            
            mml_output.append(f"set NodeBFunction=1,NodeBLocalCellGroup=1,NodeBLocalCell={sector_carrier_id},NodeBSectorCarrier={sector_carrier_id} {param} {val}")
            
        mml_output.append("") # Separador entre celdas
        
    return "\n".join(mml_output)


# =====================================================================
# Features WCDMA (DINÁMICA)
# =====================================================================

def generate_features_wcdma_section(rnd_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Genera la sección Features WCDMA leyendo la hoja 'Features' y mapeando nombres a CXC codes.
    """
    mml_output = []
    
    mml_output.append("\n#############################################################")
    mml_output.append("### Features WCDMA                        ")
    mml_output.append("#############################################################")
    mml_output.append("lt all")
    mml_output.append("lt all")
    mml_output.append("lt all\n")
    
    df = None
    if rnd_data:
        for key in rnd_data.keys():
            if key.lower() == 'features':
                df = rnd_data[key]
                break
    
    if df is None or df.empty:
        mml_output.append("# ERROR: No se encontró la hoja 'Features' en el RND")
        return "\n".join(mml_output)
        
    # Iterar sobre las columnas del DataFrame
    # Asumimos que la primera fila tiene los valores (similar a otros sheets)
    if len(df) > 0:
        row = df.iloc[0]
        
        # Crear un mapa inverso o usar el existente para buscar keys
        # El diccionario FEATURE_MAPPING es Nombre -> CXC
        
        for col_name in df.columns:
            clean_col_name = col_name.strip()
            
            # Buscar en el mapping
            # Intentamos match exacto primero
            cxc_key = FEATURE_MAPPING.get(clean_col_name)
            
            # Si no encontramos match exacto, podríamos intentar case-insensitive
            if not cxc_key:
                for k, v in FEATURE_MAPPING.items():
                    if k.lower() == clean_col_name.lower():
                        cxc_key = v
                        break
            
            if cxc_key:
                val = str(row[col_name]).strip()
                if val and val.lower() != 'nan':
                     # Si es float, convertir a int string
                    if val.replace('.','',1).isdigit() and '.' in val:
                        try:
                            val = str(int(float(val)))
                        except:
                            pass
                    
                    # Generar comando: set CXC...$ featurestate VALUE #FeatureName
                    mml_output.append(f"set {cxc_key}$ featurestate {val} #{clean_col_name}")
            else:
                # Opcional: Loggear features no encontrados en el mapping
                # mml_output.append(f"# WARNING: Feature '{clean_col_name}' no encontrado en diccionario")
                pass
                
    return "\n".join(mml_output)


# =====================================================================
# CIERRE DE SCRIPT
# =====================================================================

def generate_closing_commands(nemonico: str) -> str:
    """
    Genera los comandos de cierre del script.
    """
    mml_output = []
    
    mml_output.append("\n##########################")
    mml_output.append("###### Cierre de Script ######")
    mml_output.append("##########################")
    mml_output.append("confb+")
    mml_output.append("gs+")
    mml_output.append("set SwM=1,UpgradePackage=CXP9024418/15-R53M22  uri sftp://mm-software@172.25.7.33:22/smrsroot/software/radionode/RadioNode_CXP9024418_15_R53M22_22.Q2")
    mml_output.append("set SystemFunctions=1,SwM=1,UpgradePackage=CXP9024418/15-R53M22 password password=1:yxoOasH4WLb21cr3uJCcJ6vznNB47SI5")
    mml_output.append("confb+")
    mml_output.append("gs+")
    mml_output.append("set . vswrSupervisionSensitivity 1")
    mml_output.append("deb rfport")
    mml_output.append("set . featCtrlEulFach 1")
    mml_output.append("bl FieldReplaceableUnit=SUP")
    mml_output.append("del Transport=1,Synchronization=1,RadioEquipmentClock=1,RadioEquipmentClockReference=PTP_FASE")
    mml_output.append("deb cell|sector|pl")
    mml_output.append("")
    mml_output.append(f"cvms 3G_parametros_PL_{nemonico}")
    mml_output.append("")
    mml_output.append("############################################################################")
    mml_output.append("#############                  fin script Parametros          ##############")
    mml_output.append("############################################################################")
    
    return "\n".join(mml_output)


# =====================================================================
# VLAN WCDMA (DINÁMICA)
# =====================================================================

def generate_vlan_wcdma_section(wsh_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Genera la sección VLAN WCDMA con el valor de VLAN_TRAFICO del WSH.
    """
    mml_output = []
    
    mml_output.append("\n#############################################################")
    mml_output.append("### VLAN WCDMA                   ")
    mml_output.append("#############################################################\n")
    
    # Obtener VLAN de tráfico (default 1300 si no está disponible)
    vlan_trafico = "1300"  # Default
    if wsh_data and 'VLAN_TRAFICO' in wsh_data:
        vlan_trafico = wsh_data['VLAN_TRAFICO']
    
    mml_output.append("get Transport=1,EthernetPort= ethernetPortId > $eth\n")
    mml_output.append("cr Transport=1,VlanPort=WCDMA")
    mml_output.append("EthernetPort=$eth #encapsulation")
    mml_output.append(vlan_trafico)
    
    return "\n".join(mml_output)


# =====================================================================
# Router WCDMA (DINÁMICA)
# =====================================================================

def generate_router_wcdma_section(wsh_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Genera la sección Router WCDMA con los valores de IP, máscara y gateway del WSH.
    """
    mml_output = []
    
    mml_output.append("\n#############################################################")
    mml_output.append("### Router WCDMA")
    mml_output.append("#############################################################")
    mml_output.append("lt all\n")
    
    # Obtener valores del WSH (con defaults)
    ip_trafico = "10.31.102.54"
    mask_trafico = "26"
    gateway_trafico = "10.31.102.1"
    
    if wsh_data:
        ip_trafico = wsh_data.get('IP_TRAFICO', ip_trafico)
        mask_trafico = wsh_data.get('MASK_TRAFICO', mask_trafico)
        gateway_trafico = wsh_data.get('GATEWAY_TRAFICO', gateway_trafico)
    
    # Construir IP/MASK
    ip_con_mask = f"{ip_trafico}/{mask_trafico}"
    
    # Router WCDMA
    mml_output.append("cr Transport=1,Router=WCDMA")
    mml_output.append("lset Transport=1,Router=WCDMA$ hopLimit 64")
    mml_output.append("lset Transport=1,Router=WCDMA$ pathMtuExpiresIPv6 86400")
    mml_output.append("lset Transport=1,Router=WCDMA$ routingPolicyLocal")
    mml_output.append("lset Transport=1,Router=WCDMA$ ttl 64")
    mml_output.append("lset Transport=1,Router=WCDMA$ userLabel\n")
    
    # InterfaceIPv4
    mml_output.append("cr Transport=1,Router=WCDMA,InterfaceIPv4=1")
    mml_output.append("VlanPort=WCDMA #encapsulation")
    mml_output.append("false #loopback")
    mml_output.append("lset Transport=1,Router=WCDMA,InterfaceIPv4=1$ aclEgress")
    mml_output.append("lset Transport=1,Router=WCDMA,InterfaceIPv4=1$ aclIngress")
    mml_output.append("lset Transport=1,Router=WCDMA,InterfaceIPv4=1$ arpTimeout 300")
    mml_output.append("lset Transport=1,Router=WCDMA,InterfaceIPv4=1$ bfdProfile")
    mml_output.append("lset Transport=1,Router=WCDMA,InterfaceIPv4=1$ bfdStaticRoutes 0")
    mml_output.append("lset Transport=1,Router=WCDMA,InterfaceIPv4=1$ egressQosMarking")
    mml_output.append("lset Transport=1,Router=WCDMA,InterfaceIPv4=1$ ingressQosMarking")
    mml_output.append("lset Transport=1,Router=WCDMA,InterfaceIPv4=1$ mtu 1500")
    mml_output.append("lset Transport=1,Router=WCDMA,InterfaceIPv4=1$ pcpArp 6")
    mml_output.append("lset Transport=1,Router=WCDMA,InterfaceIPv4=1$ routesHoldDownTimer")
    mml_output.append("lset Transport=1,Router=WCDMA,InterfaceIPv4=1$ routingPolicyIngress\n")
    
    # AddressIPv4
    mml_output.append("cr Transport=1,Router=WCDMA,InterfaceIPv4=1,AddressIPv4=1")
    mml_output.append(ip_con_mask)
    mml_output.append("0 #configurationMode")
    mml_output.append("lset Transport=1,Router=WCDMA,InterfaceIPv4=1,AddressIPv4=1$ dhcpClientIdentifier")
    mml_output.append("lset Transport=1,Router=WCDMA,InterfaceIPv4=1,AddressIPv4=1$ dhcpClientIdentifierType 0")
    mml_output.append("lset Transport=1,Router=WCDMA,InterfaceIPv4=1,AddressIPv4=1$ userLabel")
    
    # RouteTableIPv4Static
    mml_output.append("cr Transport=1,Router=WCDMA,RouteTableIPv4Static=1")
    mml_output.append("cr Transport=1,Router=WCDMA,RouteTableIPv4Static=1,Dst=1")
    mml_output.append("0.0.0.0/0 #dst\n")
    
    # NextHop
    mml_output.append("cr Transport=1,Router=WCDMA,RouteTableIPv4Static=1,Dst=1,NextHop=1")
    mml_output.append(gateway_trafico)
    mml_output.append("false #discard\n")
    mml_output.append("1 #adminDistance")
    mml_output.append("lset Transport=1,Router=WCDMA,RouteTableIPv4Static=1,Dst=1,NextHop=1$ bfdMonitoring true")
    
    return "\n".join(mml_output)


# =====================================================================
# SctpEndpoint NBAP WCDMA (ESTÁTICA)
# =====================================================================

def generate_sctpendpoint_nbap_section() -> str:
    """
    Genera la sección SctpEndpoint NBAP WCDMA estática.
    """
    mml_output = []
    
    mml_output.append("\n#############################################################")
    mml_output.append("### SctpEndpoint NBAP WCDMA                   ")
    mml_output.append("#############################################################")
    mml_output.append("lt all\n")
    
    # NBAP-C
    mml_output.append("cr Transport=1,SctpEndpoint=NBAP-C")
    mml_output.append("Transport=1,Router=WCDMA,InterfaceIPv4=1,AddressIPv4=1 #localIpAddress")
    mml_output.append("5113 #portNumber")
    mml_output.append("SctpProfile=1 #sctpProfile")
    mml_output.append("lset Transport=1,SctpEndpoint=NBAP-C userLabel\n")
    
    # NBAP-D
    mml_output.append("cr Transport=1,SctpEndpoint=NBAP-D")
    mml_output.append("Transport=1,Router=WCDMA,InterfaceIPv4=1,AddressIPv4=1 #localIpAddress")
    mml_output.append("5114 #portNumber")
    mml_output.append("SctpProfile=1 #sctpProfile")
    mml_output.append("lset Transport=1,SctpEndpoint=NBAP-D userLabel")
    
    return "\n".join(mml_output)


if __name__ == "__main__":
    print("Corre este archivo importándolo desde generator_logic_3G.py")
