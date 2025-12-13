# ===========================================================================
# oam_generator_3G.py - Generador de archivo OAM para 3G-DUW
# ===========================================================================

from typing import Dict, Any, Tuple
from datetime import datetime

def cidr_to_netmask(cidr: str) -> str:
    """
    Convierte una máscara en formato CIDR (ej: '26') a formato decimal (ej: '255.255.255.192').
    
    Args:
        cidr: Máscara en formato CIDR como string (ej: '26', '24', '30')
    
    Returns:
        Máscara en formato decimal (ej: '255.255.255.192')
    """
    try:
        cidr_int = int(cidr)
        # Crear la máscara binaria
        mask = (0xffffffff >> (32 - cidr_int)) << (32 - cidr_int)
        # Convertir a formato decimal
        return f"{(mask >> 24) & 0xff}.{(mask >> 16) & 0xff}.{(mask >> 8) & 0xff}.{mask & 0xff}"
    except (ValueError, TypeError):
        # Si falla la conversión, retornar máscara por defecto /26
        return "255.255.255.192"


def convert_trama_to_port(trama: str) -> str:
    """
    Convierte el valor de Trama removiendo el guión bajo.
    
    Args:
        trama: Valor de trama (ej: 'TN_A', 'TN_B', 'TN_IDL_A')
    
    Returns:
        Valor sin guión bajo (ej: 'TNA', 'TNB', 'TNIDLA')
    """
    return trama.replace('_', '')


def generate_oam_xml(
    nemonico: str,
    wsh_data: Dict[str, Any],
    trama: str
) -> Tuple[bool, str, str]:
    """
    Genera el archivo XML de configuración OAM para 3G-DUW.
    
    Args:
        nemonico: Némónico del sitio (ej: 'UZC109')
        wsh_data: Diccionario con datos del WSH que contiene:
            - IP_TRAFICO: IP de sincronización
            - IP_OAM: IP de OAM
            - MASK_TRAFICO: Máscara de tráfico en CIDR
            - MASK_OAM: Máscara de OAM en CIDR
            - GATEWAY_TRAFICO: Gateway de tráfico
            - GATEWAY_OAM: Gateway de OAM
            - VLAN_TRAFICO: VLAN de tráfico
            - VLAN_OAM: VLAN de OAM
        trama: Valor de trama (ej: 'TN_A', 'TN_B')
    
    Returns:
        Tupla (success, xml_content, filename)
    """
    try:
        # Extraer datos del WSH
        sync_ip = wsh_data.get('IP_TRAFICO', '0.0.0.0')
        oam_ip = wsh_data.get('IP_OAM', '0.0.0.0')
        
        # Convertir máscaras de CIDR a formato decimal
        sync_mask = cidr_to_netmask(wsh_data.get('MASK_TRAFICO', '26'))
        oam_mask = cidr_to_netmask(wsh_data.get('MASK_OAM', '26'))
        
        # Gateways
        sync_gateway = wsh_data.get('GATEWAY_TRAFICO', '0.0.0.0')
        oam_gateway = wsh_data.get('GATEWAY_OAM', '0.0.0.0')
        
        # VLANs
        sync_vlan = wsh_data.get('VLAN_TRAFICO', '1300')
        oam_vlan = wsh_data.get('VLAN_OAM', '1301')
        
        # Convertir trama a gigaBitEthernetPort
        gb_port = convert_trama_to_port(trama)
        
        # Fecha y hora actual
        now = datetime.now()
        fecha_creacion = now.strftime("%d-%m-%Y %H:%M:%S")
        
        # Valores fijos según especificación
        ethernet_ip = "169.254.1.1"
        ethernet_mask = "255.255.0.0"
        et_ip_synch_slot = "1"
        use_received_ql = "FALSE"
        admin_quality = "QL_SSU_A"
        
        # Servidores DNS y NTP
        dns_server = "172.29.79.50"
        primary_ntp = "172.16.50.41"
        secondary_ntp = "172.16.50.42"
        
        # Sincronización de red
        synch_slot = "1"
        synch_port = "10"
        synch_priority = "1"
        
        # Generar contenido XML
        xml_content = f"""<!-- OAM Access Configuration -->
<!--  Created {fecha_creacion}  -->
<!--  Created by Piero Ledesma  -->
<SiteBasic>
<Format revision="E"/>
<ConfigureOAMAccess>
<IPoverEthernet ethernetIpAddress="{ethernet_ip}" ethernetSubnetMask="{ethernet_mask}"/>
<IPoverGigabitEthernet etIPSynchSlot="{et_ip_synch_slot}" syncIpAddress="{sync_ip}" syncSubnetMask="{sync_mask}" defaultRouter0="{sync_gateway}" syncVid="{sync_vlan}">
<OamIpHost oamSubnetMask="{oam_mask}" oamDefaultRouter0="{oam_gateway}" oamIpAddress="{oam_ip}" oamVid="{oam_vlan}"/>
<GigaBitEthernet gigaBitEthernetPort="{gb_port}" useReceivedQl="{use_received_ql}" adminQuality="{admin_quality}"/>
</IPoverGigabitEthernet>
<Servers isDefaultDomainName="NO" dnsServerIpAddress="{dns_server}" primaryNtpServerIpAddress="{primary_ntp}" primaryNtpServiceActive="YES" secondaryNtpServerIpAddress="{secondary_ntp}" secondaryNtpServiceActive="YES" localTimeZone="UTC" daylightSavingTime="YES" singleLogonServer=""/>
<StaticRouting>
<Route routeIpAddress="0.0.0.0" routeSubnetMask="0.0.0.0" hopIpAddress="{sync_gateway}" routeMetric="100" redistribute="NO"/>
<Route routeIpAddress="0.0.0.0" routeSubnetMask="0.0.0.0" hopIpAddress="{oam_gateway}" routeMetric="100" redistribute="NO"/>
<Route routeIpAddress="10.0.0.0" routeSubnetMask="255.255.0.0" hopIpAddress="169.254.1.2" routeMetric="100" redistribute="NO"/>
</StaticRouting>
<NetworkSynch synchSlot="{synch_slot}" synchPort="{synch_port}" synchPriority="{synch_priority}"/>
</ConfigureOAMAccess>
</SiteBasic>"""
        
        # Nombre del archivo
        filename = f"00_Create_Oam_{nemonico}.xml"
        
        return True, xml_content, filename
        
    except Exception as e:
        error_msg = f"<!-- ERROR generating OAM XML: {str(e)} -->"
        return False, error_msg, f"ERROR_OAM_{nemonico}.xml"
