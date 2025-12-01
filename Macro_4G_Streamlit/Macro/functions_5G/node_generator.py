# =====================================================================
# node_generator.py - Generación de script Node MOS para 5G NR
# =====================================================================

import pandas as pd
from typing import Dict, Any, List, Optional, Tuple 
from datetime import datetime

# =====================================================================
# CONSTANTES DE CONFIGURACIÓN DE MOS
# =====================================================================

# Paths base para MOs principales (usados en CR/SET)
MO_PATH_MANAGED_ELEMENT = "ManagedElement=1"
MO_PATH_CUCP = "GNBCUCPFunction=1"
MO_PATH_CUUP = "GNBCUUPFunction=1"
MO_PATH_DU = "GNBDUFunction=1"
MO_PATH_RRC = "GNBDUFunction=1,Rrc=1"
MO_PATH_QCI_EXT = "GNBCUCPFunction=1,QciProfileEndcConfigExt=1"
MO_PATH_DRX_UECFG = "GNBDUFunction=1,UeCC=1,DrxProfile=Default,DrxProfileUeCfg=Base"
MO_PATH_TERMPOINT_DU = "TermPointToGNBDU=1"
MO_PATH_TERMPOINT_CUCP = "GNBDUFunction=1,TermPointToGNBCUCP=1"
MO_PATH_DSCS_PCP = "Transport=1,QosProfiles=1,DscpPcpMap=1"
MO_PATH_SCTP_P2 = "Transport=1,SctpProfile=2"


# MOs que usan CRN/END con su ruta completa
CRN_END_MO_PATHS = {
    'SignalingRadioBearer': 'GNBDUFunction=1,RadioBearerTable=1,SignalingRadioBearer=1',
    'DrbRlcUeCfg': 'GNBDUFunction=1,UeCC=1,RadioLinkControl=1,DrbRlc=Default,DrbRlcUeCfg=Base',
    'GtpuSupervision': 'GNBCUUPFunction=1,GtpuSupervision=1',
    'CaCellMeasProfileUeCfg': 'GNBCUCPFunction=1,CarrierAggregation=1,CaCellMeasProfile=Default,CaCellMeasProfileUeCfg=Base',
    'PdcchReuseForPdschUeCfg': 'GNBDUFunction=1,UeCC=1,PdcchReuseForPdsch=Default,PdcchReuseForPdschUeCfg=Base',
    'PowerControlUeCfg': 'GNBDUFunction=1,UeCC=1,PowerControl=1,PowerControlUeCfg=opt',
    'UeBbProfileUeCfg': 'GNBDUFunction=1,UeCC=1,UeBb=1,UeBbProfile=Default,UeBbProfileUeCfg=Base',
}

# MOs que usan LD/CR con su ruta completa
LD_CR_MO_PATHS = {
    'InactivityProfileUeCfg': 'GNBCUCPFunction=1,UeCC=1,InactivityProfile=Default,InactivityProfileUeCfg=Base',
    'McpcPSCellProfileUeCfg': 'GNBCUCPFunction=1,Mcpc=1,McpcPSCellProfile=Default,McpcPSCellProfileUeCfg=Base',
    'IntraFreqMCCellProfileUeCfg': 'GNBCUCPFunction=1,IntraFreqMC=1,IntraFreqMCCellProfile=Default,IntraFreqMCCellProfileUeCfg=Base',
    'IntraFreqMCCellProfile': 'GNBCUCPFunction=1,IntraFreqMC=1,IntraFreqMCCellProfile=Default',
    'UeMC': 'GNBCUCPFunction=1,UeMC=1',
    'IntraFreqMC': 'GNBCUCPFunction=1,IntraFreqMC=1',
    'CUCP5qiTable': 'GNBCUCPFunction=1,CUCP5qiTable=1',
    'PowerSaving': 'NodeSupport=1,PowerSaving=1',
    'AnrFunction': 'GNBCUCPFunction=1,AnrFunction=1',
    'AnrFunctionNR': 'GNBCUCPFunction=1,AnrFunction=1,AnrFunctionNR=1',
}

# =====================================================================
# FUNCIONES DE UTILIDAD PARA LA LECTURA DEL RND (CORREGIDO)
# =====================================================================

import pandas as pd
from typing import Dict, Any, Tuple, Optional


def leer_rnd_sheets_5g(rnd_file: Any) -> Tuple[Optional[Dict[str, pd.DataFrame]], str]:
    """
    Lee las hojas específicas del RND ('Node', 'Cell-Carrier', 'Equipment-Configuration'), 
    aplicando el encabezado correcto (fila 3) y manteniendo la estructura RAW para 
    hojas de múltiples instancias.
    """
    
    # CRÍTICO: Incluir todas las hojas necesarias
    required_sheets = ['Node', 'Cell-Carrier', 'Equipment-Configuration'] 
    rnd_data: Dict[str, pd.DataFrame] = {}
    
    try:
        xls = pd.ExcelFile(rnd_file, engine='openpyxl')
        
        for sheet_name in required_sheets:
            if sheet_name in xls.sheet_names:
                
                # 1. CORRECCIÓN CLAVE: Leer el Excel especificando el encabezado en la tercera fila (índice 2).
                df = pd.read_excel(xls, sheet_name=sheet_name, header=2)
                
                # 2. Limpiar nombres de columna
                df.columns = [str(col).strip() for col in df.columns]
                df_cols = df.columns.tolist()
                
                # 3. Identificar la columna de atributos/parámetros.
                attribute_col_name = None
                if 'Atributo' in df_cols:
                    attribute_col_name = 'Atributo'
                elif 'Parametro' in df_cols:
                    attribute_col_name = 'Parametro'
                
                if 'MO' not in df.columns or attribute_col_name is None:
                    if sheet_name == 'Node':
                         return None, f"Error en la hoja '{sheet_name}'. No se encontró 'MO' ni 'Atributo'/'Parametro'."
                    else:
                         # Si no es Node, solo advertir y continuar
                         print(f"Advertencia: Hoja '{sheet_name}' ignorada por no contener 'MO' y 'Atributo'/'Parametro'.")
                         continue
                
                # 4. Limpieza básica de filas vacías
                df.dropna(subset=['MO', attribute_col_name], how='all', inplace=True)
                
                # 5. Lógica de manejo por tipo de hoja
                if sheet_name == 'Node':
                    # Hoja de INSTANCIA ÚNICA: Estandarizar a 3 columnas (MO, Atributo, Valor).
                    if len(df_cols) < 3:
                        return None, f"La hoja '{sheet_name}' no tiene una columna de valores para procesar."

                    value_col_name = df_cols[2]
                    # Solo seleccionar las columnas clave para estandarizar
                    df_standard = df[['MO', attribute_col_name, value_col_name]].copy()
                    df_standard.rename(columns={attribute_col_name: 'Atributo', value_col_name: 'Valor'}, inplace=True)
                    rnd_data[sheet_name] = df_standard
                    
                else:
                    # Hojas de MÚLTIPLES INSTANCIAS (RAW DATA)
                    # Dejar RAW para que los generadores de MML manejen las múltiples columnas de instancias.
                    rnd_data[sheet_name] = df
            
            # 6. Manejo de error para 'Node' faltante
            elif sheet_name == 'Node':
                 return None, f"La hoja requerida '{sheet_name}' no se encontró en el archivo RND."

    except Exception as e:
        return None, f"Error al leer el RND: {str(e)}"
    
    if not rnd_data:
        return None, "El RND se leyó, pero ninguna de las hojas requeridas se encontró o no tienen datos."

    return rnd_data, "Lectura RND exitosa."


def get_rnd_attributes(rnd_data: Dict[str, pd.DataFrame], sheet_name: str, mo: str, rnd_key: str = 'MO') -> Dict[str, str]:
    """ 
    Busca todos los atributos y valores para un MO dado en una hoja del RND. 
    NOTA: Esta función SOLO es segura para usarse con hojas que han sido 
    estandarizadas a columnas 'MO', 'Atributo' y 'Valor' (ej: 'Node').
    """
    if sheet_name not in rnd_data:
        return {}
    
    df = rnd_data[sheet_name]
    
    # Aquí se requiere que la hoja haya sido previamente estandarizada a 'Atributo' y 'Valor'
    if rnd_key not in df.columns or 'Atributo' not in df.columns or 'Valor' not in df.columns:
        return {}

    # Filtrar por el MO. Usamos .astype(str).str.strip() para asegurar que coincidan los tipos
    df_mo = df[df[rnd_key].astype(str).str.strip() == mo]
    
    attributes = {}
    for _, row in df_mo.iterrows():
        attribute = str(row['Atributo']).strip()
        value = str(row['Valor']).strip()
        
        # Ignorar valores vacíos/NaN/None
        if attribute and value and value.lower() != 'nan':
            attributes[attribute] = value
            
    return attributes

# =====================================================================
# GENERACIÓN DE COMANDOS GNBCUCPFunction (DINÁMICO)
# =====================================================================

def generate_cucp_mml_structure(rnd_data: Dict[str, pd.DataFrame], nem: str) -> str:
    """
    Genera la sección de comandos MML para GNBCUCPFunction.
    """
    mml_output = []
    
    # Obtener atributos de la hoja 'Node' para GNBCUCPFunction
    attributes = get_rnd_attributes(rnd_data, 'Node', 'GNBCUCPFunction')

    # Valores fijos (extraídos de los ejemplos del RND)
    MO_PATH_CUCP = "GNBCUCPFunction=1" # Constante definida anteriormente
    
    # Extraer valores de variables clave para comandos CR
    # Usar .get() para valores por defecto si no existen
    gNBId = attributes.get('gNBId', '123456') 
    mcc = attributes.get('PLMNId_mcc', '000') 
    mnc = attributes.get('PLMNId_mnc', '00') 

    # --- Header y comandos CR iniciales ---
    mml_output.append("\n################################################################")
    mml_output.append("## GNBCUCPFunction V2")
    mml_output.append("################################################################")
    
    # Comandos CR especiales que inician con el ID y PLMN (usando los datos del RND)
    mml_output.append(f"cr {MO_PATH_CUCP}")
    mml_output.append(f"{gNBId}")
    mml_output.append(f"mcc={mcc},mnc={mnc}\n")

    # Crn EndpointResource=1
    mml_output.append(f"crn {MO_PATH_CUCP},EndpointResource=1")
    mml_output.append("userLabel")
    mml_output.append("end\n")
    
    # Crn LocalSctpEndpoint=1 (Referencia SctpEndpoint=2)
    mml_output.append(f"crn {MO_PATH_CUCP},EndpointResource=1,LocalSctpEndpoint=1")
    mml_output.append("interfaceUsed 7")
    mml_output.append("sctpEndpointRef SctpEndpoint=2")
    mml_output.append("end\n")

    # Crn LocalSctpEndpoint=2 (Referencia SctpEndpoint=F1_NRCUCP)
    mml_output.append(f"crn {MO_PATH_CUCP},EndpointResource=1,LocalSctpEndpoint=2")
    mml_output.append("interfaceUsed 3")
    mml_output.append("sctpEndpointRef SctpEndpoint=F1_NRCUCP")
    mml_output.append("end\n")

    # --- Comandos SET dinámicos ---
    
    # Recorrer los atributos extraídos del RND y generar comandos SET
    for attribute, value in attributes.items():
        # Excluir los campos que ya se usaron para CR, y las referencias directas de la MO.
        if attribute.lower() in ['gnbcucpfunction=', 'userlabel', 'plmnid_mcc', 'plmnid_mnc', 'gnbid', 'endpointresourceref']:
            continue
            
        # Corregir el nombre del atributo MML para PLMNIdList (si se necesita)
        if attribute == 'PLMNId_mcc':
            attribute = 'pLMNIdList_mcc'
        elif attribute == 'PLMNId_mnc':
            attribute = 'pLMNIdList_mnc'
        
        mml_output.append(f"set {MO_PATH_CUCP} {attribute} {value}")

    # Agregar endpointResourceRef
    endpoint_ref = attributes.get('endpointResourceRef')
    if endpoint_ref:
        mml_output.append(f"set {MO_PATH_CUCP} endpointResourceRef {endpoint_ref}")
        
    # Agregar userLabel (usando el nemónico del formulario)
    mml_output.append(f"set {MO_PATH_CUCP} userLabel {nem}")
    
    return "\n".join(mml_output)

# =====================================================================
# GENERACIÓN DE COMANDOS QciProfileEndcConfigExt (DINÁMICO)
# =====================================================================

def generate_qci_ext_mml(rnd_data: Dict[str, pd.DataFrame]) -> str:
    """
    Genera la sección de comandos MML para QciProfileEndcConfigExt,
    leyendo atributos de la hoja 'Node'.
    """
    mml_output = []
    
    # Obtener atributos de la hoja 'Node' para QciProfileEndcConfigExt
    attributes = get_rnd_attributes(rnd_data, 'Node', 'QciProfileEndcConfigExt')

    # Path completo definido en las constantes
    MO_PATH_QCI_EXT = "GNBCUCPFunction=1,QciProfileEndcConfigExt=1"
    
    # --- Header y comandos CR iniciales ---
    mml_output.append("\n################################################################")
    mml_output.append("## GNBCUCPFunction -> QciProfileEndcConfigExt V2")
    mml_output.append("################################################################")
    
    # Este MO no usa CR/CRN, solo SET y el Path ya tiene la instancia incluida
    # mml_output.append(f"cr {MO_PATH_QCI_EXT}") # No requerido si solo se usa SET

    # --- Comandos SET dinámicos ---
    
    # Recorrer los atributos extraídos del RND y generar comandos SET
    for attribute, value in attributes.items():
        # Excluir el nombre de la MO
        if attribute.lower() == 'qciprofileendcconfigext=':
            continue
            
        mml_output.append(f"set {MO_PATH_QCI_EXT} {attribute} {value}")
    
    return "\n".join(mml_output)

# =====================================================================
# GENERACIÓN DE COMANDOS GNBCUUPFunction (DINÁMICO)
# =====================================================================

def generate_cuup_mml_structure(rnd_data: Dict[str, pd.DataFrame], nem: str) -> str:
    """
    Genera la sección de comandos MML para GNBCUUPFunction y sus subelementos,
    leyendo atributos de la hoja 'Node'.
    """
    mml_output = []
    
    # 1. Obtener atributos principales para GNBCUUPFunction
    attributes = get_rnd_attributes(rnd_data, 'Node', 'GNBCUUPFunction')
    
    # 2. Obtener atributos para LocalIpEndpoint
    # Buscamos la fila cuyo MO comience con el path completo de la instancia CUUP.
    # Nota: Asumimos que la lista de atributos del RND incluye 'interfaceList' para 'LocalIpEndpoint'.
    local_ip_df = rnd_data.get('Node')
    cuup_endpoint_attributes = {}
    
    if local_ip_df is not None:
        # Filtrar MO específico LocalIpEndpoint dentro de GNBCUUPFunction=1
        target_path = "GNBCUUPFunction=1,EndpointResource=1,LocalIpEndpoint=1" 
        
        # Buscar atributos de LocalIpEndpoint
        df_endpoint = local_ip_df[
            (local_ip_df['MO'].astype(str).str.strip() == 'LocalIpEndpoint') & 
            (local_ip_df['Atributo'].astype(str).str.contains('interfaceList')) # Solo necesitamos esta línea
        ]
        
        if not df_endpoint.empty:
            # Asumimos que la fila anterior a la de 'interfaceList' es el MO LocalIpEndpoint
            # Pero dado el RND, es más seguro buscar el valor directamente por la MO y Atributo:
            
            # Buscar la línea de 'interfaceList' para LocalIpEndpoint
            df_ip_list = local_ip_df[
                 (local_ip_df['MO'].astype(str).str.strip() == 'LocalIpEndpoint') &
                 (local_ip_df['Atributo'].astype(str).str.strip() == 'interfaceList')
            ]
            if not df_ip_list.empty:
                 # Asumir que el valor está en la columna 'Valor' (índice 2)
                 cuup_endpoint_attributes['interfaceList'] = str(df_ip_list.iloc[0]['Valor']).strip()

    MO_PATH_CUUP = "GNBCUUPFunction=1"
    
    # --- Extracción de valores clave ---
    gNBId = attributes.get('gNBId', '123456') 
    # Usamos los nombres del RND pLMNIdList_mcc/mnc para el valor MCC/MNC
    mcc = attributes.get('pLMNIdList_mcc', '000') 
    mnc = attributes.get('pLMNIdList_mnc', '00') 
    
    # Attributes for LocalIpEndpoint
    # Si no se encontró en el RND, usamos el valor por defecto del MML de ejemplo
    interface_list = cuup_endpoint_attributes.get('interfaceList', '4 5 7 6')
    address_ref = "Transport=1,Router=NR,InterfaceIPv4=1,AddressIPv4=1"
    
    # --- Header y comandos CR iniciales ---
    mml_output.append("\n################################################################")
    mml_output.append("## GNBCUUPFunction V2")
    mml_output.append("################################################################")
    
    # Comandos CR 
    mml_output.append(f"cr {MO_PATH_CUUP}")
    mml_output.append(f"{gNBId}")
    mml_output.append(f"mcc={mcc},mnc={mnc}\n")

    # Crn EndpointResource=1
    mml_output.append(f"crn {MO_PATH_CUUP},EndpointResource=1")
    mml_output.append("userLabel")
    mml_output.append("end\n")
    
    # Crn LocalIpEndpoint=1
    mml_output.append(f"crn {MO_PATH_CUUP},EndpointResource=1,LocalIpEndpoint=1")
    mml_output.append(f"interfaceList {interface_list}")
    mml_output.append(f"addressRef {address_ref}")
    mml_output.append("end\n")

    # --- Comandos SET dinámicos ---
    
    # Recorrer los atributos extraídos del RND y generar comandos SET
    for attribute, value in attributes.items():
        # Excluir los campos que ya se usaron para CR/CRN o son redundantes
        if attribute.lower() in ['gnbcuupfunction=', 'userlabel', 'gnbid', 'gnbcuupfunctionid', 'plmnidlist_mcc', 'plmnidlist_mnc']:
            continue
            
        mml_output.append(f"set {MO_PATH_CUUP} {attribute} {value}")

    # Agregar userLabel al final
    mml_output.append(f"set {MO_PATH_CUUP} userLabel {nem}")
    
    return "\n".join(mml_output)

# =====================================================================
# GENERACIÓN DE COMANDOS GNBDUFunction (DINÁMICO)
# =====================================================================

def generate_du_mml_structure(rnd_data: Dict[str, pd.DataFrame], nem: str) -> str:
    """
    Genera la sección de comandos MML para GNBDUFunction y sus subelementos,
    aplicando las exclusiones específicas solicitadas y manteniendo la flexibilidad CR.
    """
    mml_output = []
    
    # 1. Obtener atributos principales para GNBDUFunction
    attributes = get_rnd_attributes(rnd_data, 'Node', 'GNBDUFunction')

    MO_PATH_DU = "GNBDUFunction=1"
    
    # --- Extracción de valores clave ---
    gnb_du_id = attributes.get('gNBDUFunctionId', '1') 
    gNBId = attributes.get('gNBId', '123456') 
    mcc = attributes.get('dUpLMNId_mcc', '730') 
    mnc = attributes.get('dUpLMNId_mnc', '01') 
    
    # --- Header y comandos CR iniciales (Mantenemos la flexibilidad solicitada) ---
    mml_output.append("\n################################################################")
    mml_output.append("## GNBDUFunction V2 ")
    mml_output.append("################################################################")
    
    # CR Formato Estándar/Nuevo Release (Ejecutable)
    mml_output.append(f"cr {MO_PATH_DU}")
    mml_output.append(f"{gnb_du_id}") 
    mml_output.append(f"{gNBId}\n") 
    
    # CR Formato Legacy/Antiguo Release (Comentado como Referencia)
    mml_output.append(f"cr {MO_PATH_DU}")
    mml_output.append(f"{gNBId}")
    mml_output.append(f"mcc={mcc},mnc={mnc}\n")

    # Crn EndpointResource=1
    mml_output.append(f"crn {MO_PATH_DU},EndpointResource=1")
    mml_output.append("userLabel")
    mml_output.append("end\n")
    
    # Crn LocalSctpEndpoint=1
    mml_output.append(f"crn {MO_PATH_DU},EndpointResource=1,LocalSctpEndpoint=1")
    mml_output.append("interfaceUsed 3")
    mml_output.append("sctpEndpointRef SctpEndpoint=F1_NRDU")
    mml_output.append("end\n")

    # --- Comandos SET dinámicos ---
    
    # Atributos a EXCLUIR de la generación automática SET (los 3 solicitados + otros de control)
    EXCLUSION_LIST = [
        'gnbdufunction=', 'userlabel', 'gnbdufunctionid', 'gnbduid', 'endpointresourceref',
        # Los 3 atributos a eliminar (los pasaremos a SETs manuales si es necesario)
        'duplmnid_mcc', 'duplmnid_mnc', 'gnbidlength' 
    ]
    
    # Recorrer los atributos extraídos del RND y generar comandos SET
    for attribute, value in attributes.items():
        if attribute.lower() in EXCLUSION_LIST:
            continue
            
        # El atributo 'gNBId' se maneja fuera del bucle para asegurar su posición
        if attribute == 'gNBId':
            continue
            
        mml_output.append(f"set {MO_PATH_DU} {attribute} {value}")
        
    # --- Comandos SET Agregados/Reordenados (para satisfacer el requerimiento) ---
    
    # 1. Agregar set gNBId (Asumiendo que gnodebid se refiere a gNBId del RND)
    mml_output.append(f"set {MO_PATH_DU} gNBId {gNBId}")

    # 2. Agregar endpointResourceRef
    endpoint_ref = attributes.get('endpointResourceRef')
    if endpoint_ref:
        mml_output.append(f"set {MO_PATH_DU} endpointResourceRef {endpoint_ref}")

    # 3. Agregar userLabel al final
    mml_output.append(f"set {MO_PATH_DU} userLabel {nem}")
    
    return "\n".join(mml_output)

# =====================================================================
# GENERACIÓN DE COMANDOS Rrc (DINÁMICO)
# =====================================================================

def generate_rrc_mml(rnd_data: Dict[str, pd.DataFrame]) -> str:
    """
    Genera la sección de comandos MML para Rrc,
    leyendo atributos de la hoja 'Node' y usando SET.
    """
    mml_output = []
    
    # Obtener atributos de la hoja 'Node' para Rrc
    # El nombre de la MO en el RND debe ser 'Rrc'
    attributes = get_rnd_attributes(rnd_data, 'Node', 'Rrc')

    # Path completo definido en las constantes: GNBDUFunction=1,Rrc=1
    MO_PATH_RRC = "GNBDUFunction=1,Rrc=1"
    
    # --- Header ---
    mml_output.append("\n################################################################")
    mml_output.append("## GNBDUFunction -> Rrc V2")
    mml_output.append("################################################################")
    
    # --- Comandos SET dinámicos ---
    
    # Recorrer los atributos extraídos del RND y generar comandos SET
    for attribute, value in attributes.items():
        # Excluir el nombre de la MO
        if attribute.lower() == 'rrc=':
            continue
            
        mml_output.append(f"set {MO_PATH_RRC} {attribute} {value}")
    
    return "\n".join(mml_output)

# =====================================================================
# GENERACIÓN DE COMANDOS SignalingRadioBearer (DINÁMICO)
# =====================================================================

def generate_signaling_radio_bearer_mml(rnd_data: Dict[str, pd.DataFrame]) -> str:
    """
    Genera la sección de comandos MML para SignalingRadioBearer,
    leyendo atributos de la hoja 'Node' y usando SET, excluyendo atributos redundantes.
    """
    mml_output = []
    
    # Obtener atributos de la hoja 'Node' para SignalingRadioBearer
    attributes = get_rnd_attributes(rnd_data, 'Node', 'SignalingRadioBearer')

    # Path completo: GNBDUFunction=1,RadioBearerTable=1,SignalingRadioBearer=1
    MO_PATH = "GNBDUFunction=1,RadioBearerTable=1,SignalingRadioBearer=1" 
    
    # --- Header ---
    mml_output.append("\n################################################################")
    mml_output.append("## GNBDUFunction -> SignalingRadioBearer V2")
    mml_output.append("################################################################")
    
    # --- Comandos SET dinámicos ---
    
    # Atributos a EXCLUIR de la generación automática SET:
    # 1. El nombre de la MO seguido de = (Ej: SignalingRadioBearer=)
    # 2. El atributo SignalingRadioBearerId (redundante)
    # 3. La línea problemática que incluye el Path del MO como atributo (¡LA CORRECCIÓN!)
    MO_PATH_PREFIX = "GNBDUFunction=1,RadioBearerTable=1,SignalingRadioBearer="
    
    EXCLUSION_LIST = [
        'signalingradiobearer=', 
        'signalingradiobearerid',
        MO_PATH_PREFIX.lower() # Excluye la cadena del Path completo
    ]
    
    for attribute, value in attributes.items():
        # Limpiamos y convertimos a minúsculas para una comparación robusta
        clean_attribute = attribute.strip().lower() 
        
        if clean_attribute in EXCLUSION_LIST:
            continue
            
        mml_output.append(f"set {MO_PATH} {attribute} {value}")
    
    return "\n".join(mml_output)

# =====================================================================
# GENERACIÓN DE COMANDOS DrxProfileUeCfg (DINÁMICO)
# =====================================================================

def generate_drx_profile_ue_cfg_mml(rnd_data: Dict[str, pd.DataFrame]) -> str:
    """
    Genera la sección de comandos MML para DrxProfileUeCfg,
    leyendo atributos de la hoja 'Node' y usando SET.
    """
    mml_output = []
    
    # Obtener atributos de la hoja 'Node' para DrxProfileUeCfg
    attributes = get_rnd_attributes(rnd_data, 'Node', 'DrxProfileUeCfg')

    # Path completo: GNBDUFunction=1,UeCC=1,DrxProfile=Default,DrxProfileUeCfg=Base
    MO_PATH = "GNBDUFunction=1,UeCC=1,DrxProfile=Default,DrxProfileUeCfg=Base" 
    
    # --- Header ---
    mml_output.append("\n################################################################")
    mml_output.append("## GNBDUFunction -> DrxProfileUeCfg V2")
    mml_output.append("################################################################")
    
    # --- Comandos SET dinámicos ---
    
    for attribute, value in attributes.items():
        # Excluir el nombre de la MO
        if attribute.lower() == 'drxprofileuecfg=':
            continue
            
        mml_output.append(f"set {MO_PATH} {attribute} {value}")
    
    return "\n".join(mml_output)

# =====================================================================
# GENERACIÓN DE COMANDOS TermPointToGNBCUCP (ESTÁTICO)
# =====================================================================

def generate_term_point_to_gnbcucp_mml() -> str:
    """
    Genera la sección MML estática para TermPointToGNBCUCP,
    usando la IP 169.254.42.42.
    """
    mml_output = []
    
    MO_PATH = "GNBDUFunction=1,TermPointToGNBCUCP=1"
    IPV4_ADDR = "169.254.42.42" 
    
    mml_output.append("\n############################################################")
    mml_output.append("# TermPointToGNBCUCP Reference")
    mml_output.append("############################################################")
    
    mml_output.append(f"cr {MO_PATH}")
    mml_output.append(f"set {MO_PATH} ipv4Address {IPV4_ADDR}") 
    mml_output.append(f"deb {MO_PATH}")
    
    return "\n".join(mml_output)

# =====================================================================
# GENERACIÓN DE COMANDOS ServiceDiscoveryServer / ServiceDiscovery (ESTÁTICO)
# =====================================================================

def generate_service_discovery_mml() -> str:
    """
    Genera la sección MML estática para ServiceDiscoveryServer y ServiceDiscovery.
    """
    mml_output = []
    
    mml_output.append("\n############################################################")
    mml_output.append("# ServiceDiscoveryServer / ServiceDiscovery Reference")
    mml_output.append("############################################################")
    
    # Bloque ServiceDiscoveryServer
    mml_output.append("crn NodeSupport=1,ServiceDiscoveryServer=1")
    mml_output.append("cluster host=localhost,hostIPs=,port=8301,serviceArea=NR_NSA")
    mml_output.append("localAddress Router=NR,InterfaceIPv4=1,AddressIPv4=1")
    mml_output.append("nodeCredential")
    mml_output.append("trustCategory")
    mml_output.append("end\n") # Separador entre CRN's

    # Bloque ServiceDiscovery
    mml_output.append("crn NodeSupport=1,ServiceDiscovery=1")
    mml_output.append("localAddress Router=NR,InterfaceIPv4=1,AddressIPv4=1")
    mml_output.append("nodeCredential")
    mml_output.append("primaryGsds host=localhost,hostIPs=,port=8301,serviceArea=NR_NSA")
    mml_output.append("secondaryGsds")
    mml_output.append("trustCategory")
    mml_output.append("end")
    
    return "\n".join(mml_output)

# =====================================================================
# GENERACIÓN DE COMANDOS IntraFreqMC (ESTÁTICO/LD & CR)
# =====================================================================

def generate_intra_freq_mc_mml() -> str:
    """
    Genera la sección MML estática para IntraFreqMC (LD y CR).
    """
    mml_output = []
    
    MO_PATH = "GNBCUCPFunction=1,IntraFreqMC=1"
    
    mml_output.append("\n################################################################")
    mml_output.append("## GNBCUCPFunction -> IntraFreqMC V2")
    mml_output.append("################################################################")
    
    mml_output.append(f"ld {MO_PATH}")
    mml_output.append(f"cr {MO_PATH}")
    
    return "\n".join(mml_output)

# =====================================================================
# GENERACIÓN DE COMANDOS McpcPSCellProfileUeCfg (DINÁMICO)
# =====================================================================

def generate_mcpc_p_s_cell_profile_mml(rnd_data: Dict[str, pd.DataFrame]) -> str:
    """
    Genera la sección de comandos MML para McpcPSCellProfileUeCfg,
    leyendo atributos de la hoja 'Node', usando LD, CR y SET, y corrigiendo el formato.
    """
    mml_output = []
    
    # 1. Obtener atributos de la hoja 'Node' para McpcPSCellProfileUeCfg
    attributes = get_rnd_attributes(rnd_data, 'Node', 'McpcPSCellProfileUeCfg')

    # Path completo
    MO_PATH = "GNBCUCPFunction=1,Mcpc=1,McpcPSCellProfile=Default,McpcPSCellProfileUeCfg=Base" 
    
    # --- Header ---
    mml_output.append("\n################################################################")
    mml_output.append("## GNBCUCPFunction -> McpcPSCellProfileUeCfg V2")
    mml_output.append("################################################################")
    
    # --- Comandos LD y CR fijos ---
    mml_output.append(f"ld {MO_PATH}")
    mml_output.append(f"cr {MO_PATH}\n") 
    
    # --- Comandos SET dinámicos ---
    
    # Atributos a EXCLUIR (los que dan la línea redundante y el ID)
    MO_PATH_PREFIX = "GNBCUCPFunction=1,Mcpc=1,McpcPSCellProfile=Default,McpcPSCellProfileUeCfg="
    EXCLUSION_LIST = [
        'mcpcpscellprofileuecfg=', # MO name
        'mcpcpscellprofileuecfgid', # ID attribute
        MO_PATH_PREFIX.lower() # Línea redundante del Path
    ]
    
    # Reordenamiento y Procesamiento de atributos
    processed_attributes = {}
    for attribute, value in attributes.items():
        clean_attribute = attribute.strip().lower()
        if clean_attribute in EXCLUSION_LIST:
            continue

        # 1. Manejo especial de atributos con sub-atributos (el guión bajo '_')
        if '_' in attribute:
            # Divide 'rsrpCandidateA5_timeToTrigger' en ('rsrpCandidateA5', 'timeToTrigger')
            parts = attribute.split('_', 1) 
            if len(parts) == 2:
                # El valor final es 'subatributo=valor' (ej: timeToTrigger=640)
                final_value = f"{parts[1]}={value}"
                # El atributo principal es la primera parte (ej: rsrpCandidateA5)
                principal_attribute = parts[0]
                
                # Agrupamos los sub-atributos bajo el atributo principal
                if principal_attribute not in processed_attributes:
                    processed_attributes[principal_attribute] = []
                processed_attributes[principal_attribute].append(final_value)
                continue # Saltar al siguiente atributo, ya lo procesamos
        
        # 2. Manejo de 'rsrpCriticalEnabled' (Convierte true/false a 1/0 si es necesario, basado en su ejemplo '1')
        if attribute == 'rsrpCriticalEnabled':
            value = '1' if str(value).lower() in ['true', '1'] else '0'
        
        # 3. Atributos simples sin sub-atributos (lowHighFreqPrioClassification, mcpcQuantityList, rsrpCriticalEnabled, rsrpSearchTimeRestriction)
        processed_attributes[attribute] = str(value)

    # --- Generación de Comandos SET ---

    # Generar SETs para atributos simples y atributos con sub-atributos
    for attribute, value in processed_attributes.items():
        if isinstance(value, list):
            # Es un atributo con sub-atributos (ej: rsrpCandidateA5)
            for sub_attribute_value in value:
                # El formato es "set PATH Atributo Subatributo=Valor"
                mml_output.append(f"set {MO_PATH} {attribute} {sub_attribute_value}")
        else:
            # Es un atributo simple (ej: lowHighFreqPrioClassification 7)
            mml_output.append(f"set {MO_PATH} {attribute} {value}")
    
    return "\n".join(mml_output)

# =====================================================================
# GENERACIÓN DE COMANDOS InactivityProfileUeCfg (DINÁMICO)
# =====================================================================

def generate_inactivity_profile_ue_cfg_mml(rnd_data: Dict[str, pd.DataFrame]) -> str:
    """
    Genera la sección de comandos MML para InactivityProfileUeCfg,
    leyendo atributos de la hoja 'Node'.
    """
    mml_output = []
    
    # Obtener atributos de la hoja 'Node' para InactivityProfileUeCfg
    attributes = get_rnd_attributes(rnd_data, 'Node', 'InactivityProfileUeCfg')

    # Path completo
    MO_PATH = "GNBCUCPFunction=1,UeCC=1,InactivityProfile=Default,InactivityProfileUeCfg=Base" 
    
    # --- Header y comandos LD/CR ---
    mml_output.append("\n################################################################")
    mml_output.append("## GNBCUCPFunction -> InactivityProfileUeCfg V2")
    mml_output.append("################################################################")
    
    mml_output.append(f"ld {MO_PATH}")
    mml_output.append(f"cr {MO_PATH}\n")
    
    # --- Comandos SET dinámicos ---
    
    # Atributos a EXCLUIR: El nombre de la MO y el ID
    MO_PATH_PREFIX = "GNBCUCPFunction=1,UeCC=1,InactivityProfile=Default,InactivityProfileUeCfg="
    EXCLUSION_LIST = [
        'inactivityprofileuecfg=', 
        'inactivityprofileuecfgid', 
        MO_PATH_PREFIX.lower() 
    ]
    
    for attribute, value in attributes.items():
        if attribute.strip().lower() in EXCLUSION_LIST:
            continue
            
        mml_output.append(f"set {MO_PATH} {attribute} {value}")
    
    return "\n".join(mml_output)

# =====================================================================
# GENERACIÓN DE COMANDOS UeMC (ESTÁTICO/LD & CR)
# =====================================================================

def generate_ue_mc_mml() -> str:
    """
    Genera la sección MML estática para UeMC (LD y CR).
    """
    mml_output = []
    
    MO_PATH = "GNBCUCPFunction=1,UeMC=1"
    
    mml_output.append("\n################################################################")
    mml_output.append("## GNBCUCPFunction -> UeMC V2")
    mml_output.append("################################################################")
    
    mml_output.append(f"ld {MO_PATH}")
    mml_output.append(f"cr {MO_PATH}")
    
    return "\n".join(mml_output)

# =====================================================================
# GENERACIÓN DE COMANDOS IntraFreqMCCellProfileUeCfg (DINÁMICO CON PARSEO CORREGIDO)
# =====================================================================

def generate_intra_freq_mc_cell_profile_ue_cfg_mml(rnd_data: Dict[str, pd.DataFrame]) -> str:
    """
    Genera la sección de comandos MML para IntraFreqMCCellProfileUeCfg,
    leyendo atributos de la hoja 'Node' y corrigiendo el formato de sub-atributos (añadiendo '=').
    """
    mml_output = []
    
    # 1. Obtener atributos de la hoja 'Node' para IntraFreqMCCellProfileUeCfg
    attributes = get_rnd_attributes(rnd_data, 'Node', 'IntraFreqMCCellProfileUeCfg')

    # Path completo
    MO_PATH = "GNBCUCPFunction=1,IntraFreqMC=1,IntraFreqMCCellProfile=Default,IntraFreqMCCellProfileUeCfg=Base" 
    
    # --- Header ---
    mml_output.append("\n################################################################")
    mml_output.append("## GNBCUCPFunction -> IntraFreqMCCellProfileUeCfg V2")
    mml_output.append("################################################################")
    
    # --- Comandos LD y CR fijos ---
    mml_output.append(f"ld {MO_PATH}")
    mml_output.append(f"cr {MO_PATH}\n") 
    
    # --- Comandos SET dinámicos ---
    
    # Atributos a EXCLUIR
    MO_PATH_PREFIX = "GNBCUCPFunction=1,IntraFreqMC=1,IntraFreqMCCellProfile=Default,IntraFreqMCCellProfileUeCfg="
    EXCLUSION_LIST = [
        'intrafreqmccellprofileuecfg=', 
        'intrafreqmccellprofileuecfgid', 
        MO_PATH_PREFIX.lower() 
    ]
    
    # Reordenamiento y Procesamiento de atributos
    processed_attributes = {}
    for attribute, value in attributes.items():
        clean_attribute = attribute.strip().lower()
        if clean_attribute in EXCLUSION_LIST:
            continue

        # Manejo especial de atributos con sub-atributos (el guión bajo '_')
        if '_' in attribute:
            # Divide 'rsrpBetterSpCell_hysteresis' en ('rsrpBetterSpCell', 'hysteresis')
            parts = attribute.split('_', 1) 
            if len(parts) == 2:
                # CORRECCIÓN: El formato MML deseado es SubAttribute=Value (CON '=')
                sub_attribute = parts[1]
                final_value = f"{sub_attribute}={value}" # Ej: "hysteresis=10"
                     
                principal_attribute = parts[0]
                
                # Agrupamos los sub-atributos bajo el atributo principal
                if principal_attribute not in processed_attributes:
                    processed_attributes[principal_attribute] = []
                processed_attributes[principal_attribute].append(final_value)
                continue 
        
        # Atributos simples sin sub-atributos
        processed_attributes[attribute] = str(value)

    # --- Generación de Comandos SET ---

    for attribute, value in processed_attributes.items():
        if isinstance(value, list):
            # Es un atributo con sub-atributos (ej: rsrpBetterSpCell)
            for sub_attribute_value in value:
                # El formato es "set PATH Atributo Subatributo=Valor"
                mml_output.append(f"set {MO_PATH} {attribute} {sub_attribute_value}")
        else:
            # Es un atributo simple
            mml_output.append(f"set {MO_PATH} {attribute} {value}")
    
    return "\n".join(mml_output)

# =====================================================================
# GENERACIÓN DE COMANDOS CUCP5qiTable (DINÁMICO)
# =====================================================================

def generate_cucp_5qi_table_mml(rnd_data: Dict[str, pd.DataFrame]) -> str:
    """
    Genera la sección de comandos MML para CUCP5qiTable.
    """
    mml_output = []
    attributes = get_rnd_attributes(rnd_data, 'Node', 'CUCP5qiTable')
    MO_PATH = "GNBCUCPFunction=1,CUCP5qiTable=1"
    
    # --- Header y comandos LD/CR ---
    mml_output.append("\n################################################################")
    mml_output.append("## GNBCUCPFunction -> CUCP5qiTable V2")
    mml_output.append("################################################################")
    
    mml_output.append(f"ld {MO_PATH}")
    mml_output.append(f"cr {MO_PATH}\n")
    
    # --- Comandos SET dinámicos ---
    
    MO_PATH_PREFIX = "GNBCUCPFunction=1,CUCP5qiTable="
    EXCLUSION_LIST = [
        'cucp5qitable=', 
        'cucp5qitableid', 
        MO_PATH_PREFIX.lower() 
    ]
    
    for attribute, value in attributes.items():
        if attribute.strip().lower() in EXCLUSION_LIST:
            continue
            
        mml_output.append(f"set {MO_PATH} {attribute} {value}")
    
    return "\n".join(mml_output)

# =====================================================================
# GENERACIÓN DE COMANDOS AnrFunction (DINÁMICO)
# =====================================================================

def generate_anr_function_mml(rnd_data: Dict[str, pd.DataFrame]) -> str:
    """
    Genera la sección de comandos MML para AnrFunction.
    """
    mml_output = []
    attributes = get_rnd_attributes(rnd_data, 'Node', 'AnrFunction')
    MO_PATH = "GNBCUCPFunction=1,AnrFunction=1"
    
    # --- Header y comandos LD/CR ---
    mml_output.append("\n################################################################")
    mml_output.append("## GNBCUCPFunction -> AnrFunction V2")
    mml_output.append("################################################################")
    
    mml_output.append(f"ld {MO_PATH}")
    mml_output.append(f"cr {MO_PATH}\n")
    
    # --- Comandos SET dinámicos ---
    
    MO_PATH_PREFIX = "GNBCUCPFunction=1,AnrFunction="
    EXCLUSION_LIST = [
        'anrfunction=', 
        'anrfunctionid', 
        MO_PATH_PREFIX.lower() 
    ]
    
    for attribute, value in attributes.items():
        if attribute.strip().lower() in EXCLUSION_LIST:
            continue
            
        mml_output.append(f"set {MO_PATH} {attribute} {value}")
    
    return "\n".join(mml_output)

# =====================================================================
# GENERACIÓN DE COMANDOS AnrFunctionNR (DINÁMICO)
# =====================================================================

def generate_anr_function_nr_mml(rnd_data: Dict[str, pd.DataFrame]) -> str:
    """
    Genera la sección de comandos MML para AnrFunctionNR.
    """
    mml_output = []
    attributes = get_rnd_attributes(rnd_data, 'Node', 'AnrFunctionNR')
    MO_PATH = "GNBCUCPFunction=1,AnrFunction=1,AnrFunctionNR=1"
    
    # --- Header y comandos LD/CR ---
    mml_output.append("\n################################################################")
    mml_output.append("## GNBCUCPFunction -> AnrFunctionNR V2")
    mml_output.append("################################################################")
    
    mml_output.append(f"ld {MO_PATH}")
    mml_output.append(f"cr {MO_PATH}\n")
    
    # --- Comandos SET dinámicos ---
    
    MO_PATH_PREFIX = "GNBCUCPFunction=1,AnrFunction=1,AnrFunctionNR="
    EXCLUSION_LIST = [
        'anrfunctionnr=', 
        'anrfunctionnrid', 
        MO_PATH_PREFIX.lower() 
    ]
    
    for attribute, value in attributes.items():
        if attribute.strip().lower() in EXCLUSION_LIST:
            continue
            
        mml_output.append(f"set {MO_PATH} {attribute} {value}")
    
    return "\n".join(mml_output)

# =====================================================================
# GENERACIÓN DE COMANDOS PowerSaving (DINÁMICO)
# =====================================================================

def generate_power_saving_mml(rnd_data: Dict[str, pd.DataFrame]) -> str:
    """
    Genera la sección de comandos MML para PowerSaving.
    """
    mml_output = []
    attributes = get_rnd_attributes(rnd_data, 'Node', 'PowerSaving')
    MO_PATH = "NodeSupport=1,PowerSaving=1"
    
    # --- Header y comandos LD/CR ---
    mml_output.append("\n################################################################")
    mml_output.append("## NodeSupport -> PowerSaving V2")
    mml_output.append("################################################################")
    
    mml_output.append(f"ld {MO_PATH}")
    mml_output.append(f"cr {MO_PATH}\n")
    
    # --- Comandos SET dinámicos ---
    
    MO_PATH_PREFIX = "NodeSupport=1,PowerSaving="
    EXCLUSION_LIST = [
        'powersaving=', 
        'powersavingid', 
        MO_PATH_PREFIX.lower() 
    ]
    
    for attribute, value in attributes.items():
        if attribute.strip().lower() in EXCLUSION_LIST:
            continue
            
        mml_output.append(f"set {MO_PATH} {attribute} {value}")
    
    return "\n".join(mml_output)

# =====================================================================
# FUNCIÓN PRINCIPAL DE GENERACIÓN
# =====================================================================

def generar_node_mos_5g(nemonico: str, wsh_data: Dict[str, Any], rnd_data: Dict[str, pd.DataFrame]) -> str:
    """
    Genera el archivo MOS de nodo (Transport Node) basado en RND y WSH,
    incluyendo la configuración de GNBCUCPFunction.
    """
    nem = nemonico.upper()
    fecha_actual = datetime.now().strftime("%d-%m-%Y")
    hora_actual = datetime.now().strftime("%H:%M:%S")
    
    # 1. Extraer 'TRAMA' del WSH
    trama = wsh_data.get('TRAMA', 'TN_IDL_B')
    
    # 2. Construir el Header (Contenido Estático)
    mos_content = f"""//////////////////////-GENERATED-///////////////////////////////
//
// SCRIPT     : NodeId
// NEMONICO   : {nem}
// CREADOR    : PIERO LEDESMA
// HORA       : {hora_actual}
// FECHA      : {fecha_actual}
//
/////////////////////////////////////////////////////////////

confb+
gs+

set SwM=1,UpgradePackage=CXP2010174/1-R71H14 uri sftp://mm-software@172.25.7.33:22/smrsroot/software/radionode/RadioNode_CXP2010174_1_R71H14_23.Q2
set SystemFunctions=1,SwM=1,UpgradePackage=CXP2010174/1-R71H14 password password=1:yL5YpBepTMnZVwaxiGatn0f6X68Q0ATJ
get . managedElementId > $nodename 

/////////////////////////////////////////////////////////////
# TN/IDL & SYNC FH 
/////////////////////////////////////////////////////////////
crn Transport=1,VlanPort=FH_OAM_B
egressQosClassification
egressQosMarking
egressQosQueueMap
encapsulation EthernetPort={trama}
ingressQosMarking
isTagged true
lowLatencySwitching false
userLabel
vlanId 24
end



crn Equipment=1,FieldReplaceableUnit=BB-1,TnPort=TN_IDL_C
userLabel TN_IDL_C
end

cr Transport=1,EthernetPort=TN_IDL_C
FieldReplaceableUnit=BB-1,TnPort=TN_IDL_C

set Transport=1,EthernetPort=TN_IDL_C autoNegEnable false
set Transport=1,EthernetPort=TN_IDL_C admOperatingMode 9

crn Transport=1,VlanPort=ERAN_E5_CA
egressQosClassification
egressQosMarking
egressQosQueueMap
encapsulation EthernetPort=TN_IDL_C
ingressQosMarking
isTagged true
lowLatencySwitching false
userLabel ERAN_E5_CA
vlanId 3113
end


crn Equipment=1,FieldReplaceableUnit=BB-1,TnPort=TN_IDL_D
userLabel TN_IDL_D
end

cr Transport=1,EthernetPort=TN_IDL_D
FieldReplaceableUnit=BB-1,TnPort=TN_IDL_D

set Transport=1,EthernetPort=TN_IDL_D autoNegEnable false
set Transport=1,EthernetPort=TN_IDL_D admOperatingMode 9

crn Transport=1,VlanPort=ERAN_ULCOMP
egressQosClassification
egressQosMarking
egressQosQueueMap
encapsulation EthernetPort=TN_IDL_D
ingressQosMarking
isTagged true
lowLatencySwitching false
userLabel ERAN_ULCOMP
vlanId 3114
end

deb EthernetPort 


############################################################
# Node_Internal_F1 INTERFACE
############################################################
crn Transport=1,Router=Node_Internal_F1
hopLimit 64
pathMtuExpiresIPv6 86400
routingPolicyLocal
ttl 64
userLabel
end

crn Transport=1,Router=Node_Internal_F1,InterfaceIPv4=NRCUCP
aclEgress
aclIngress
arpTimeout 300
bfdProfile
bfdStaticRoutes 0
egressQosMarking
encapsulation
ingressQosMarking
loopback true
mtu 1500
pcpArp 6
routesHoldDownTimer
routingPolicyIngress
userLabel
end

crn Transport=1,Router=Node_Internal_F1,InterfaceIPv4=NRCUCP,AddressIPv4=1
address 169.254.42.42/32
configurationMode 0
dhcpClientIdentifier
dhcpClientIdentifierType 0
userLabel
end

crn Transport=1,Router=Node_Internal_F1,InterfaceIPv4=NRDU
aclEgress
aclIngress
arpTimeout 300
bfdProfile
bfdStaticRoutes 0
egressQosMarking
encapsulation
ingressQosMarking
loopback true
mtu 1500
pcpArp 6
routesHoldDownTimer
routingPolicyIngress
userLabel
end

crn Transport=1,Router=Node_Internal_F1,InterfaceIPv4=NRDU,AddressIPv4=1
address 169.254.42.43/32
configurationMode 0
dhcpClientIdentifier
dhcpClientIdentifierType 0
userLabel
end
############################################################
# SctpProfile Reference 
############################################################

crn Transport=1,SctpProfile=Node_Internal_F1
alphaIndex 3
assocMaxRtx 20
betaIndex 2
bundlingActivated true
bundlingAdaptiveActivated true
bundlingTimer 0
cookieLife 60
dscp 40
hbMaxBurst 1
heartbeatActivated true
heartbeatInterval 2000
incCookieLife 30
initARWnd 16384
initRto 200
initialHeartbeatInterval 500
maxActivateThr 65535
maxBurst 4
maxInStreams 2
maxInitRt 8
maxOutStreams 2
maxRto 400
maxSctpPduSize 1480
maxShutdownRt 5
minActivateThr 1
minRto 100
noSwitchback true
pathMaxRtx 10
primaryPathAvoidance true
primaryPathMaxRtx 0
sackTimer 10
thrTransmitBuffer 48
thrTransmitBufferCongCeased 85
transmitBufferSize 64
userLabel
end

crn Transport=1,SctpProfile=2
alphaIndex 3
assocMaxRtx 20
betaIndex 2
bundlingActivated true
bundlingAdaptiveActivated true
bundlingTimer 0
cookieLife 60
dscp 40
hbMaxBurst 1
heartbeatActivated true
heartbeatInterval 2000
incCookieLife 30
initARWnd 16384
initRto 200
initialHeartbeatInterval 500
maxActivateThr 65535
maxBurst 4
maxInStreams 2
maxInitRt 8
maxOutStreams 2
maxRto 400
maxSctpPduSize 1480
maxShutdownRt 5
minActivateThr 1
minRto 100
noSwitchback true
pathMaxRtx 10
primaryPathAvoidance true
primaryPathMaxRtx 0
sackTimer 10
thrTransmitBuffer 48
thrTransmitBufferCongCeased 85
transmitBufferSize 64
userLabel
end
############################################################
# SctpEndpoint Reference 
############################################################

crn Transport=1,SctpEndpoint=F1_NRDU
localIpAddress Transport=1,Router=Node_Internal_F1,InterfaceIPv4=NRDU,AddressIPv4=1
portNumber 38472
sctpProfile SctpProfile=Node_Internal_F1
userLabel
end

crn Transport=1,SctpEndpoint=F1_NRCUCP
localIpAddress Transport=1,Router=Node_Internal_F1,InterfaceIPv4=NRCUCP,AddressIPv4=1
portNumber 38472
sctpProfile SctpProfile=Node_Internal_F1
userLabel
end

crn Transport=1,SctpEndpoint=2
localIpAddress Transport=1,Router=NR,InterfaceIPv4=1,AddressIPv4=1
portNumber 36422
sctpProfile SctpProfile=2
userLabel
end
############################################################
# DscpPcpMap Reference 
############################################################

crn Transport=1,QosProfiles=1,DscpPcpMap=1
defaultPcp 0
pcp0 0
pcp1 12,14
pcp2 18,20,22
pcp3 26,28,
pcp4 34,36,38
pcp5 40,42,44,46
pcp6 48
pcp7 56
userLabel DSCP to PCP Mapping
end
############################################################
# RadioEquipmentClock Reference 
############################################################
crn Transport=1,Ptp=1
end

crn Transport=1,Ptp=1,BoundaryOrdinaryClock=1
clockType 2
domainNumber 24
priority1 255
priority2 255
ptpProfile 2
end

crn Transport=1,Ptp=1,BoundaryOrdinaryClock=1,PtpBcOcPort=1
administrativeState 1
announceMessageInterval 1
associatedGrandmaster
asymmetryCompensation 0
dscp 56
durationField 300
localPriority 128
masterOnly false
pBit 1
ptpMulticastAddress 0
ptpPathTimeError 1000
syncMessageInterval -4
transportInterface EthernetPort={trama}
transportVlan
end

crn Transport=1,Synchronization=1,RadioEquipmentClock=1
bfnOffset 0
freqDeviationThreshold 5000
minQualityLevel qualityLevelValueOptionI=2,qualityLevelValueOptionII=2,qualityLevelValueOptionIII=1
selectionProcessMode 1
timeHoldoverAlarmConfig enable=false,filterTime=3
end

crn Transport=1,Synchronization=1,RadioEquipmentClock=1,RadioEquipmentClockReference=PTP
adminQualityLevel qualityLevelValueOptionI=2,qualityLevelValueOptionII=2,qualityLevelValueOptionIII=1
administrativeState 1
encapsulation Ptp=1,BoundaryOrdinaryClock=1
holdOffTime 1000
priority 1
useQLFrom 1
waitToRestoreTime 60
end
cr Synchronization=1,SyncEthInput=1
EthernetPort={trama}
cr Transport=1,Synchronization=1,RadioEquipmentClock=1,RadioEquipmentClockReference=SyncE
Synchronization=1,SyncEthInput=1
2

deb radioequip
set CXC4040008 featurestate 1
set CXC4040011 featurestate 1
############################################################
# Cabinet Reference 
############################################################
cr Equipment=1,Cabinet=1
cr EquipmentSupportFunction=1,Climate=1
set EquipmentSupportFunction=1,Climate=1 climateControlMode 0
set Equipment=1,FieldReplaceableUnit=BB-1 PositionRef Cabinet=1
set MpClusterHandling=1 primaryCoreRef Equipment=1,FieldReplaceableUnit=BB-1

"""
    # 4. AÑADIR BLOQUE DINÁMICO GNBCUCPFunction
    if rnd_data is not None:
        
        # 4a. GNBCUCPFunction
        mos_content += generate_cucp_mml_structure(rnd_data, nem)
        mos_content += "\n" # <--- SEPARADOR

        # 4b. QciProfileEndcConfigExt (NUEVO BLOQUE)
        mos_content += generate_qci_ext_mml(rnd_data)
        mos_content += "\n" # <--- SEPARADOR

        # 4c. GNBCUUPFunction (NUEVO BLOQUE)
        mos_content += generate_cuup_mml_structure(rnd_data, nem)
        mos_content += "\n" # <--- SEPARADOR

        # 4d. GNBDUFunction (NUEVO BLOQUE)
        mos_content += generate_du_mml_structure(rnd_data, nem)
        mos_content += "\n" # <--- SEPARADOR

        # 4e. Rrc (NUEVO BLOQUE)
        mos_content += generate_rrc_mml(rnd_data)
        mos_content += "\n" # <--- SEPARADOR

        # 4f. SignalingRadioBearer (NUEVO BLOQUE)
        mos_content += generate_signaling_radio_bearer_mml(rnd_data)
        mos_content += "\n" # <--- SEPARADOR

        # 4g. DrxProfileUeCfg (NUEVO BLOQUE)
        mos_content += generate_drx_profile_ue_cfg_mml(rnd_data)
        mos_content += "\n" # <--- SEPARADOR    

        # 4h. TermPointToGNBCUCP (NUEVO BLOQUE)
        mos_content += generate_term_point_to_gnbcucp_mml()
        mos_content += "\n" # <--- SEPARADOR

        # 4i. ServiceDiscoveryServer / ServiceDiscovery (NUEVO BLOQUE)
        mos_content += generate_service_discovery_mml()
        mos_content += "\n" # <--- SEPARADOR    

        # 4j. IntraFreqMC (NUEVO BLOQUE)
        mos_content += generate_intra_freq_mc_mml()
        mos_content += "\n" # <--- SEPARADOR

        # 4k. McpcPSCellProfileUeCfg (NUEVO BLOQUE)
        mos_content += generate_mcpc_p_s_cell_profile_mml(rnd_data)
        mos_content += "\n" # <--- SEPARADOR     

        # 4l. InactivityProfileUeCfg (NUEVO BLOQUE)
        mos_content += generate_inactivity_profile_ue_cfg_mml(rnd_data)
        mos_content += "\n" # <--- SEPARADOR

        # 4m. UeMC (NUEVO BLOQUE)
        mos_content += generate_ue_mc_mml()
        mos_content += "\n" # <--- SEPARADOR

        # 4n. IntraFreqMCCellProfileUeCfg (NUEVO BLOQUE)
        mos_content += generate_intra_freq_mc_cell_profile_ue_cfg_mml(rnd_data)
        mos_content += "\n" # <--- SEPARADOR
    
        # 4p. CUCP5qiTable (NUEVO BLOQUE)
        mos_content += generate_cucp_5qi_table_mml(rnd_data)
        mos_content += "\n" # <--- SEPARADOR
    
        # 4q. AnrFunction (NUEVO BLOQUE)
        mos_content += generate_anr_function_mml(rnd_data)
        mos_content += "\n" # <--- SEPARADOR
    
        # 4r. AnrFunctionNR (NUEVO BLOQUE)
        mos_content += generate_anr_function_nr_mml(rnd_data)
        mos_content += "\n" # <--- SEPARADOR
    
        # 4s. PowerSaving (NUEVO BLOQUE)
        mos_content += generate_power_saving_mml(rnd_data)
        mos_content += "\n" # <--- SEPARADOR
    
    else:
        # Si hay error en el RND, lo imprimimos en el MOS para que el usuario lo vea.
        mos_content += f"\n// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        mos_content += f"\n// ! ERROR: No se pudo generar la configuración dinámica."
        mos_content += f"\n// ! MOTIVO: {error_msg}"
        mos_content += f"\n// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
        
    # 5. Cierre estático (cvms y gs-)
    mos_content += """

gs- 
confb- 
cvms PL_NR_Node_$nodename
"""
    return mos_content