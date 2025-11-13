import datetime
import pandas as pd
from typing import Dict, Any, List, Union
from io import BytesIO

# ====================================================================
# === DATOS ESTATICOS DE MME (IPs) ===
MME_IP_DATA = {
    "vSASG13": {"ipAddress1": "172.25.197.6", "ipAddress2": "172.25.197.7"},
    "SASG09": {"ipAddress1": "172.18.231.144", "ipAddress2": "172.18.231.145"},
    "SASG10": {"ipAddress1": "172.18.231.134", "ipAddress2": "172.18.231.135"},
    "SASG11": {"ipAddress1": "172.18.180.142", "ipAddress2": "172.18.180.143"},
    "SASG12": {"ipAddress1": "172.18.180.144", "ipAddress2": "172.18.180.145"},
    "CDLV3C_AMF01": {"ipAddress1": "172.16.212.33", "ipAddress2": "172.16.212.34"},
    "INDC_AMF01": {"ipAddress1": "172.30.88.37", "ipAddress2": "172.30.88.38"},
    "CHSG01": {"ipAddress1": "172.25.17.15", "ipAddress2": "172.25.17.16"},
    "COSG01": {"ipAddress1": "172.25.17.143", "ipAddress2": "172.25.17.144"},
    "IND_USN01": {"ipAddress1": "172.25.237.103", "ipAddress2": "172.25.237.104"},
    "CDLV_USN01": {"ipAddress1": "172.25.236.174", "ipAddress2": "172.25.236.175"},
    "SASG08": {"ipAddress1": "172.18.231.138", "ipAddress2": "172.18.231.139"},
    "CNTC_AMF01": {"ipAddress1": "172.24.220.213", "ipAddress2": "172.24.220.214"},
    "vSASG14": {"ipAddress1": "172.23.127.7", "ipAddress2": "172.23.127.8"},
    "DURPCCMM1": {"ipAddress1": "10.9.9.201", "ipAddress2": "10.9.9.202"},
    "LONPCCMM1": {"ipAddress1": "172.24.235.7", "ipAddress2": "172.24.235.8"},
}

# Definición de atributos de RfPort que deben extraerse
RFPORT_ATTRIBUTES = [
    'vswrSupervisionActive', 
    'vswrSupervisionSensitivity', 
    'administrativeState', 
    'userLabel'
]

# ====================================================================
# === FUNCIONES INTERNAS DE SOPORTE (EXTRACTION) ===
# ====================================================================

def _read_rnd_sheet(rnd_file: Any, sheet_name: str) -> Union[pd.DataFrame, None]:
    """Helper para leer una hoja de Excel del RND."""
    if rnd_file is None:
        return None
    try:
        return pd.read_excel(
            BytesIO(rnd_file.getvalue()), 
            sheet_name=sheet_name,
            header=0, 
            dtype=str
        )
    except Exception as e:
        print(f"Error al leer hoja '{sheet_name}': {e}")
        return None

def _extract_sctp_profile(rnd_node_file: Any) -> List[str]:
    """Extrae comandos SCTP de la hoja 'Node'."""
    df_node = _read_rnd_sheet(rnd_node_file, 'Node')
    if df_node is None:
        return ["// RND no cargado o error al leer hoja 'Node'. Comandos SCTP omitidos."]

    commands = []
    try:
        sctp_attrs = df_node[df_node['MO'] == 'SctpProfile'].copy()
        atributo_col_index = df_node.columns.get_loc('Atributo')
        value_col_index = atributo_col_index + 1
        value_col_name = df_node.columns[value_col_index]

        for _, row in sctp_attrs.iterrows():
            attribute_name = row.get('Atributo')
            attribute_value = row.get(value_col_name)
            
            if pd.notna(attribute_name) and pd.notna(attribute_value) and str(attribute_value).strip():
                commands.append(f"set Transport=1,SctpProfile=1 {attribute_name.strip()} {str(attribute_value).strip()}")
        
    except KeyError:
        return ["// Error Crítico: Columna 'MO' o 'Atributo' no encontrada en RND->Node. Comandos SCTP omitidos."]
    except IndexError:
        return ["// Error Crítico: No se pudo determinar la columna de valores en la hoja 'Node' del RND."]
    
    if not commands:
        commands.append("// No se encontraron atributos SCTP para 'SctpProfile' en RND->Node.")
        
    return commands


def _extract_mme_config(rnd_file: Any) -> Dict[str, Dict[str, str]]:
    """Extrae la configuración de TermPointToMme."""
    df_eq = _read_rnd_sheet(rnd_file, 'Equipment-Configuration')
    if df_eq is None:
        return {}

    mme_data = {}
    try:
        tptmme_rows = df_eq[df_eq['MO'] == 'TermPointToMme'].copy()
        if tptmme_rows.empty: return {}

        atributo_index = df_eq.columns.get_loc('Atributo')
        mme_column_map = {}
        mme_name_row = tptmme_rows.iloc[0] # Asumimos la primera fila de TermPointToMme tiene los nombres MME
        
        for i in range(atributo_index + 1, len(df_eq.columns)):
            mme_name = str(mme_name_row.iloc[i]).strip()
            col_name = df_eq.columns[i]
            
            if mme_name in MME_IP_DATA:
                mme_column_map[mme_name] = col_name
                mme_data[mme_name] = {}

        attributes_to_extract = ['administrativeState', 'mmeSupportNbIoT', 'mmeSupportLegacyLte']
        
        for attr in attributes_to_extract:
            attr_row = tptmme_rows[tptmme_rows['Atributo'] == attr]
            if attr_row.empty: continue
            
            attr_row = attr_row.iloc[0] 
            
            for mme_name, col_name in mme_column_map.items():
                value = str(attr_row.get(col_name)).strip()
                
                if not value:
                    if attr == 'administrativeState':
                        value = '1'
                    elif attr in ['mmeSupportNbIoT', 'mmeSupportLegacyLte']:
                        value = 'true'
                
                mme_data[mme_name][attr] = value

    except (KeyError, IndexError) as e:
        print(f"Error al buscar columnas en la hoja Equipment-Configuration para MME: {e}")
        return {}
    return mme_data


def _extract_rfport_config(rnd_file: Any) -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Extrae la configuración de FieldReplaceableUnit (RRU) y RfPort.
    Busca la fila de nombres de RRU en la columna 'Atributo' con el valor
    'Equipment=1,FieldReplaceableUnit='.
    """
    df_eq = _read_rnd_sheet(rnd_file, 'Equipment-Configuration')
    if df_eq is None:
        return {}

    rru_config = {}
    
    try:
        # Fila donde están los atributos y los valores de los RfPort
        rfport_rows = df_eq[df_eq['MO'] == 'RfPort'].copy()
        
        if rfport_rows.empty: 
            return {}

        atributo_index = df_eq.columns.get_loc('Atributo')
        first_value_col_index = atributo_index + 1
        
        # 1. Búsqueda CRÍTICA de la fila de nombres de RRUs: 
        # Busca la fila donde MO='RfPort' Y Atributo='Equipment=1,FieldReplaceableUnit='
        rru_name_row_candidates = rfport_rows[
            rfport_rows['Atributo'].astype(str).str.strip() == 'Equipment=1,FieldReplaceableUnit='
        ]

        if rru_name_row_candidates.empty:
            print("// Error: No se encontró la fila de nombres de RRU ('Equipment=1,FieldReplaceableUnit=')")
            return {}
        
        rru_name_row = rru_name_row_candidates.iloc[0]

        # 2. Mapeo de columnas de RRU (columna de Pandas a nombre de RRU)
        rru_col_to_name_map = {}
        rru_names_set = set() # Usamos un set para solo agregar cada RRU (RRU-1, RRU-2) una vez
        
        for i in range(first_value_col_index, len(df_eq.columns)):
            rru_name_full = str(rru_name_row.iloc[i]).strip()
            # Aseguramos el formato RRU-X (por si viene RRU-1-1 o algo similar, aunque en el ejemplo era RRU-1)
            rru_parts = rru_name_full.split('-')
            if len(rru_parts) >= 2 and rru_parts[0].upper() == 'RRU':
                 rru_name = f"RRU-{rru_parts[1]}"
            else:
                 rru_name = rru_name_full

            col_name = df_eq.columns[i]
            
            if rru_name.upper().startswith('RRU'):
                rru_col_to_name_map[col_name] = rru_name
                rru_names_set.add(rru_name)
        
        for name in rru_names_set:
             rru_config[name] = {}
        
        if not rru_col_to_name_map:
            return {}

        # 3. Extracción de atributos de RfPort para cada RRU
        # Buscamos la fila de nombres de puertos ('RfPort=') que está justo debajo de 'Equipment=1,FieldReplaceableUnit='
        port_name_rows = rfport_rows[rfport_rows['Atributo'].astype(str).str.strip() == 'RfPort=']
        if port_name_rows.empty: 
            print("// Error: No se encontró la fila de nombres de puerto ('RfPort=')")
            return {}
        port_name_row = port_name_rows.iloc[0]

        for attr in RFPORT_ATTRIBUTES:
            attr_rows = rfport_rows[rfport_rows['Atributo'].str.contains(attr, na=False, regex=False)]
            
            for _, attr_row in attr_rows.iterrows():
                
                # Iteramos sobre las columnas (Puertos A, B, C...)
                for col_index in range(first_value_col_index, len(df_eq.columns)):
                    col_name = df_eq.columns[col_index]
                    rru_name = rru_col_to_name_map.get(col_name)

                    if not rru_name: continue

                    port_id = str(port_name_row.iloc[col_index]).strip()
                    
                    if not port_id or port_id not in ['A', 'B', 'C', 'D', 'R']: continue

                    # Extraemos el valor del atributo para esa columna
                    value = str(attr_row.get(col_name)).strip()

                    if port_id not in rru_config[rru_name]:
                        rru_config[rru_name][port_id] = {}
                        
                    # Aplicar valores por defecto si están vacíos
                    if not value:
                        if attr == 'administrativeState':
                            value = '1'
                        elif attr == 'vswrSupervisionActive':
                            value = 'true'
                        elif attr == 'vswrSupervisionSensitivity':
                            value = '100'
                        else:
                            value = 'LTE'
                            
                    rru_config[rru_name][port_id][attr] = value

    except (KeyError, IndexError, ValueError) as e:
        print(f"Error crítico al buscar columnas o procesar datos en Equipment-Configuration para RRU: {e}")
        return {}

    return rru_config

# ====================================================================
# === FUNCION PRINCIPAL DE GENERACIÓN (.MOS) ===
# ====================================================================

def generar_hardware_mos(nemonico: str, wsh_data: Dict[str, str], trama: str, rnd_node_file: Any) -> str:
    """
    Genera el contenido MOS (MML) unificado con SCTP, MMEs y RRU/RfPorts.
    """
    nemonico_upper = nemonico.upper()
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Obtener la configuración necesaria
    sctp_profile_commands = _extract_sctp_profile(rnd_node_file)
    mme_full_config = _extract_mme_config(rnd_node_file)
    rru_full_config = _extract_rfport_config(rnd_node_file)
    
    # --- Variables Dinámicas (WSH Report) ---
    ip_address = f"{wsh_data.get('IP_TRAFICO_LTE', '0.0.0.0')}/{wsh_data.get('MASK', '26')}"
    next_hop = wsh_data.get('DGW_TRAFICO_LTE', '0.0.0.0')
    vlan_id = wsh_data.get('VLAN_LTE', '1404')
    trama_port = trama
    
    # --- 1. FIRMA Y COMENTARIO INICIAL ---
    signature = f"""
/*
    ====================================================================
    == ARCHIVO DE CONFIGURACIÓN REMOTA
    ====================================================================
    
    AUTOR: Piero Ledesma
    FECHA DE SCRIPT: {current_date}
    NEMONICO: {nemonico_upper}
    
    --------------------------------------------------------------------
    == CONFIGURACIÓN DE TRANSPORTE Y SCTP (WSH + RND Node)
    == IP DE TRÁFICO USADA: {ip_address}
    --------------------------------------------------------------------
*/

confb+
s+
"""
    
    # --- 2. SCRIPT DE TRANSPORTE, SCTP Y ACTIVACIÓN DE FEATURE ---
    transport_script = f"""
crn Transport=1,VlanPort=LTE
egressQosClassification
egressQosMarking 
egressQosQueueMap 
encapsulation EthernetPort={trama_port}
ingressQosMarking 
isTagged true
userLabel LTE
vlanId {vlan_id}
end

crn Transport=1,Router=LTE
hopLimit 64
pathMtuExpiresIPv6 86400
routingPolicyLocal 
ttl 64
userLabel
end

crn Transport=1,Router=LTE,InterfaceIPv4=1
aclEgress 
aclIngress 
arpTimeout 300
bfdProfile 
bfdStaticRoutes 0
egressQosMarking QosProfiles=1,DscpPcpMap=1
encapsulation VlanPort=LTE
ingressQosMarking 
loopback false
mtu 1500
pcpArp 6
routesHoldDownTimer 
routingPolicyIngress
userLabel LTE
end

crn Transport=1,Router=LTE,InterfaceIPv4=1,AddressIPv4=1
address {ip_address} 
configurationMode 0
dhcpClientIdentifier 
dhcpClientIdentifierType 0
primaryAddress true
userLabel LTE
end

crn Transport=1,Router=LTE,RouteTableIPv4Static=1
end

crn Transport=1,Router=LTE,RouteTableIPv4Static=1,Dst=1
dst 0.0.0.0/0
end

crn Transport=1,Router=LTE,RouteTableIPv4Static=1,Dst=1,NextHop=1
address {next_hop}
adminDistance 1
bfdMonitoring true
discard false
reference 
end

cr ENodeBFunction=1
mcc=730,mnc=01,mncLength=2

cr Transport=1,SctpProfile=1

// --- ATRIBUTOS SCTP EXTRAÍDOS DEL RND (HOJA NODE) ---
{chr(10).join(sctp_profile_commands)}

cr Transport=1,SctpEndpoint=1
Transport=1,Router=LTE,InterfaceIPv4=1,AddressIPv4=1
36422
SctpProfile=1
set ENodeBFunction=1 sctpRef SctpEndpoint=1
set ENodeBFunction=1 upIpAddressRef Router=LTE,InterfaceIPv4=1,AddressIPv4=1
cr Transport=1,QosProfiles=1,DscpPcpMap=1
cr Transport=1,Synchronization=1,RadioEquipmentClock=1
cr Transport=1,Synchronization=1,SyncEthInput=1
EthernetPort=TN_A
cr Transport=1,Synchronization=1,SyncEthInput=1
EthernetPort=TN_B
cr Transport=1,Synchronization=1,SyncEthInput=1
EthernetPort=TN_C
cr Transport=1,Synchronization=1,SyncEthInput=1
EthernetPort={trama_port}
cr Transport=1,Synchronization=1,RadioEquipmentClock=1,RadioEquipmentClockReference=SyncE
Synchronization=1,SyncEthInput=1
1
deb Transport=1,Synchronization=1,RadioEquipmentClock=1,RadioEquipmentClockReference=SyncE

set CXC4040011 featurestate 1 

"""
    
    # --- 3. SEPARADOR Y COMANDOS TERMPOINTTOMME (DINAMICO) ---
    
    separator_tpmme = """
/*
#############################################
####        Creación TermPointToMme        ####
#############################################
*/
"""

    mme_config_script = ""
    if mme_full_config:
        for mme_name, attr_data in mme_full_config.items():
            ip_data = MME_IP_DATA.get(mme_name, {'ipAddress1': '0.0.0.0', 'ipAddress2': '0.0.0.0'})
            
            admin_state = attr_data.get('administrativeState', '1')
            nbiot_support = attr_data.get('mmeSupportNbIoT', 'true')
            legacy_lte_support = attr_data.get('mmeSupportLegacyLte', 'true')
            
            mme_config_script += f"""
crn ENodeBFunction=1,TermPointToMme={mme_name}
administrativeState {admin_state}
mmeSupportNbIoT {nbiot_support}
mmeSupportLegacyLte {legacy_lte_support}
domainName 
ipAddress1 {ip_data['ipAddress1']}
ipAddress2 {ip_data['ipAddress2']}
end
"""
    else:
        mme_config_script = "\n// No se encontraron TermPointToMme en la hoja Equipment-Configuration para configurar."

    
    # --- 4. SEPARADOR Y COMANDOS RRU + RFPORT + RIPORT (DINAMICO) ---

    separator_rru = """
/*
#############################################
####      Creación de RRUs + Port        ####
#############################################
*/
"""
    rru_script = ""

    if rru_full_config:
        # **CORRECCIÓN DE ORDENAMIENTO:** Ordenamos las claves de RRU alfabéticamente
        rru_names_sorted = sorted(rru_full_config.keys())
        
        for rru_name in rru_names_sorted:
            ports_config = rru_full_config[rru_name]
            
            # 4a. Creación y deb de la RRU (FieldReplaceableUnit)
            rru_script += f"""
cr Equipment=1,FieldReplaceableUnit={rru_name}
deb Equipment=1,FieldReplaceableUnit={rru_name}
"""
            
            # 4b. Configuración dinámica de RfPort (A, B, C, D...)
            # También ordenamos los puertos (A, B, C, D, R) para consistencia
            ports_sorted = sorted(ports_config.keys())

            for port_id in ports_sorted:
                attr_data = ports_config[port_id]
                
                # Para asegurar la creación
                rru_script += f"\ncr Equipment=1,FieldReplaceableUnit={rru_name},RfPort={port_id}"

                if port_id != 'R':
                    # Configuración de atributos (extraídos del RND)
                    vswr_active = attr_data.get('vswrSupervisionActive', 'true')
                    vswr_sens = attr_data.get('vswrSupervisionSensitivity', '100')
                    admin_state = attr_data.get('administrativeState', '1')
                    user_label = attr_data.get('userLabel', 'LTE')

                    rru_script += f"""
set FieldReplaceableUnit={rru_name},RfPort={port_id} vswrSupervisionActive {vswr_active}
set FieldReplaceableUnit={rru_name},RfPort={port_id} vswrSupervisionSensitivity {vswr_sens}
set FieldReplaceableUnit={rru_name},RfPort={port_id} administrativeState {admin_state}
set FieldReplaceableUnit={rru_name},RfPort={port_id} userLabel {user_label}
"""

            # 4c. RiPort=DATA_1 y DATA_2 estático
            rru_script += f"""
cr Equipment=1,FieldReplaceableUnit={rru_name},RiPort=DATA_1
cr Equipment=1,FieldReplaceableUnit={rru_name},RiPort=DATA_2
"""
    else:
        rru_script = "\n// No se encontraron RRUs para configurar en la hoja Equipment-Configuration."


    # --- 5. ENSAMBLAJE FINAL ---
    final_script = f"""
{signature}
{transport_script}
{separator_tpmme}
{mme_config_script}

{separator_rru}
{rru_script}

/* --- FIN DE ARCHIVO .MOS --- */
"""
    
    return final_script