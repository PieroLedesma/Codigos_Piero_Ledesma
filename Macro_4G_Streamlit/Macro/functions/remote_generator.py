import datetime
import pandas as pd
from typing import Dict, Any, List
from io import BytesIO

# ====================================================================
# === FUNCIONES INTERNAS DE SOPORTE (SCTP) ===
# ====================================================================

def _extraer_sctp_profile(rnd_node_file: Any) -> List[str]:
    """
    Lee la hoja 'Node' del RND y extrae los comandos MML para configurar el SctpProfile.
    """
    if rnd_node_file is None:
        return ["// RND no cargado. Comandos SCTP omitidos."]

    try:
        # SOLUCIÓN 1: Usamos header=0 para que 'MO' y 'Atributo' sean los nombres de columna
        df_node = pd.read_excel(
            BytesIO(rnd_node_file.getvalue()), 
            sheet_name='Node',
            header=0, 
            dtype=str
        )
    except Exception as e:
        print(f"Error al leer hoja 'Node' o al procesar datos: {e}")
        return ["// Error al leer la hoja 'Node' del RND. Comandos SCTP omitidos."]

    commands = []
    
    try:
        # 1. Filtramos los atributos de SctpProfile (ahora 'MO' existe)
        sctp_attrs = df_node[df_node['MO'] == 'SctpProfile'].copy()
        
        # 2. Encontramos la columna de valores (asumimos que es la siguiente a 'Atributo')
        try:
            atributo_col_index = df_node.columns.get_loc('Atributo')
            value_col_index = atributo_col_index + 1
            value_col_name = df_node.columns[value_col_index]
        except (KeyError, IndexError):
            # Fallback en caso de que la estructura sea inesperada
            return ["// Error Crítico: No se pudo determinar la columna de valores en la hoja 'Node' del RND."]

        # 3. Iteramos sobre las filas y generamos los comandos
        for _, row in sctp_attrs.iterrows():
            attribute_name = row.get('Atributo')
            attribute_value = row.get(value_col_name)
            
            if pd.notna(attribute_name) and pd.notna(attribute_value) and str(attribute_value).strip():
                commands.append(f"set Transport=1,SctpProfile=1 {attribute_name.strip()} {str(attribute_value).strip()}")
        
    except KeyError:
        return ["// Error Crítico: Columna 'MO' no encontrada en RND->Node. Comandos SCTP omitidos."]
    
    # 4. Mensaje de Fallback si no se encontró nada
    if not commands:
        commands.append("// No se encontraron atributos SCTP para 'SctpProfile' en RND->Node.")
        commands.append("// Se usarán los valores por defecto del nodo.")
        
    return commands


# ====================================================================
# === FUNCION PRINCIPAL DE GENERACIÓN (.MOS) ===
# ====================================================================

def generar_hardware_mos(nemonico: str, wsh_data: Dict[str, str], trama: str, rnd_node_file: Any) -> str:
    """
    Genera el contenido MOS (MML) unificado con SCTP dinámico y la activación estática final.
    """
    nemonico_upper = nemonico.upper()
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Obtener comandos SctpProfile dinámicos
    sctp_profile_commands = _extraer_sctp_profile(rnd_node_file)
    
    # --- Variables Dinámicas (Extraídas del WSH Report) ---
    
    # ✅ SOLUCIÓN 2: Usamos claves NORMALIZADAS (MAYÚSCULAS_CON_UNDERSCORES)
    # Su lector de WSH debe normalizar las columnas a este formato.
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
    
    # --- 2. SCRIPT DE TRANSPORTE Y SCTP (CON VALORES DINÁMICOS) ---
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
"""
    
    # --- 3. LINEA FINAL ESTÁTICA Y CIERRE ---
    final_script = f"""
set CXC4040011 featurestate 1

RLOGI: ME={nemonico_upper};

/* --- FIN DE ARCHIVO .MOS --- */
"""
    
    # --- ENSAMBLAJE FINAL ---
    return signature + transport_script + final_script