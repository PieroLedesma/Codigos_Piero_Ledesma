
# =====================================================================
# atnd_generator.py - Generación de script ATND en formato MML
# =====================================================================

from typing import Tuple, Optional, Any, Dict
from datetime import datetime
import pandas as pd
from .data_reader_ATND import leer_atnd_completo, get_summary_data, validar_atnd_data

# =====================================================================
# FUNCIÓN PRINCIPAL DE GENERACIÓN
# =====================================================================

def generate_atnd_script(nemonico: str, atnd_file: Any) -> Tuple[bool, str, str]:
    """
    Genera el contenido del archivo MML para ATND.
    
    Args:
        nemonico: Némónico del sitio
        atnd_file: Archivo Excel ATND cargado
    
    Returns:
        Tuple[bool, str, str]: (Success, Content, Filename)
    """
    mml_output = []
    
    # 1. Leer datos del ATND
    print(f"DEBUG: Leyendo archivo ATND para {nemonico}...")
    atnd_data, error = leer_atnd_completo(atnd_file)
    
    if error or not atnd_data:
        error_msg = error or "No se pudieron leer datos del ATND"
        print(f"DEBUG: Error - {error_msg}")
        return False, f"// ERROR: {error_msg}", f"{nemonico}_ATND_ERROR.mos"
    
    # 2. Validar datos
    es_valido, msg_validacion = validar_atnd_data(atnd_data)
    if not es_valido:
        print(f"DEBUG: Validación fallida - {msg_validacion}")
        return False, f"// ERROR: {msg_validacion}", f"{nemonico}_ATND_ERROR.mos"
    
    # 3. Obtener datos del Summary
    summary = get_summary_data(atnd_data)
    site_name = summary.get('Site', nemonico) if summary else nemonico
    
    # 4. Generar Header con firma
    now = datetime.now()
    hora = now.strftime("%H:%M:%S")
    fecha = now.strftime("%d-%m-%Y")
    
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("//")
    mml_output.append("// SCRIPT     : ATND LTE Baseband")
    mml_output.append("// AUTOR      : PIERO LEDESMA")
    mml_output.append(f"// NEMONICO   : {site_name}")
    mml_output.append(f"// HORA       : {hora}")
    mml_output.append(f"// FECHA      : {fecha}")
    mml_output.append("//")
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("")
    
    # 5. Información del ATND (comentarios)
    if summary:
        mml_output.append("// ========== INFORMACIÓN DEL ATND ==========")
        mml_output.append(f"// Nombre: {summary.get('Nombre', 'N/A')}")
        mml_output.append(f"// Hardware: {summary.get('Hardware', 'N/A')}")
        mml_output.append(f"// SW Version: {summary.get('SW_Version', 'N/A')}")
        mml_output.append(f"// Arquitectura: {summary.get('Arquitectura', 'N/A')}")
        mml_output.append(f"// Proyecto: {summary.get('PROYECTO', 'N/A')}")
        mml_output.append("// ==========================================")
        mml_output.append("")
    
    # 6. Comandos iniciales
    mml_output.append("confb+")
    mml_output.append("gs+")
    mml_output.append("")
    
    # 7. Sección DscpDscpMap
    dscp_section = generate_dscp_dscp_map_section(atnd_data)
    if dscp_section:
        mml_output.extend(dscp_section)
    
    # 8. Sección DscpPcpMap
    dscp_pcp_section = generate_dscp_pcp_map_section(atnd_data)
    if dscp_pcp_section:
        mml_output.extend(dscp_pcp_section)
    
    # 9. Sección PcpPcpMap
    pcp_pcp_section = generate_pcp_pcp_map_section(atnd_data)
    if pcp_pcp_section:
        mml_output.extend(pcp_pcp_section)
    
    # 10. Sección Ethernet Port
    ethernet_port_section = generate_ethernet_port_section(atnd_data)
    if ethernet_port_section:
        mml_output.extend(ethernet_port_section)
    
    # 11. Sección VlanPort
    vlan_port_section = generate_vlan_port_section(atnd_data)
    if vlan_port_section:
        mml_output.extend(vlan_port_section)
    
    # 12. Sección Router
    router_section = generate_router_section(atnd_data)
    if router_section:
        mml_output.extend(router_section)
    
    # 13. Sección TwampResponder
    twamp_section = generate_twamp_responder_section(atnd_data)
    if twamp_section:
        mml_output.extend(twamp_section)
    
    # 14. Sección NtpFrequencySync
    ntp_section = generate_ntp_frequency_sync_section(atnd_data)
    if ntp_section:
        mml_output.extend(ntp_section)
    
    # 15. Sección BoundaryOrdinaryClock
    boundary_clock_section = generate_boundary_ordinary_clock_section(atnd_data)
    if boundary_clock_section:
        mml_output.extend(boundary_clock_section)
    
    # 16. Sección PtpBcOcPort
    ptp_port_section = generate_ptp_bc_oc_port_section(atnd_data)
    if ptp_port_section:
        mml_output.extend(ptp_port_section)
    
    # 17. Sección Synchronization
    sync_section = generate_synchronization_section(atnd_data)
    if sync_section:
        mml_output.extend(sync_section)
    
    # 18. Sección RadioEquipmentClockReference
    radio_clock_ref_section = generate_radio_equipment_clock_reference_section(atnd_data)
    if radio_clock_ref_section:
        mml_output.extend(radio_clock_ref_section)
    
    # 19. Sección Features
    features_section = generate_features_section(atnd_data, site_name)
    if features_section:
        mml_output.extend(features_section)
    
    # 20. Comandos finales
    mml_output.append(f"cvms CV_ATND-{site_name}")
    mml_output.append("gs-")
    mml_output.append("confb-")
    mml_output.append("")
    
    print(f"DEBUG: Script ATND generado exitosamente para {site_name}")
    
    # 9. Generar contenido final
    content = "\n".join(mml_output)
    
    # 10. Nombre del archivo
    filename = f"{site_name}_ATND_Parametros.mos"
    
    return True, content, filename


# =====================================================================
# FUNCIONES DE GENERACIÓN DE SECCIONES
# =====================================================================

def generate_dscp_dscp_map_section(atnd_data: Dict[str, Any]) -> Optional[list]:
    """
    Genera la sección DscpDscpMap del script MML.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        Lista de líneas MML para la sección DscpDscpMap o None
    """
    if 'DscpDscpMap' not in atnd_data:
        print("DEBUG: Hoja DscpDscpMap no encontrada")
        return None
    
    df = atnd_data['DscpDscpMap']
    if df.empty:
        print("DEBUG: Hoja DscpDscpMap está vacía")
        return None
    
    mml_output = []
    
    # Header de la sección
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("/////// DscpDscpMap ")
    mml_output.append("/////////////////////////////////////////////////////////////")
    
    # Obtener la primera fila (asumiendo un solo sitio)
    row = df.iloc[0]
    
    # Comando CREATE
    mml_output.append("cr Transport=1,QosProfiles=1,DscpDscpMap=1")
    
    # Helper para obtener valor de columna
    def get_val(col_name):
        if col_name in df.columns:
            val = row[col_name]
            # Convertir a int si es float
            if isinstance(val, float) and not pd.isna(val):
                return str(int(val))
            elif pd.isna(val):
                return None
            return str(val)
        return None
    
    # SET para defaultDscp
    default_dscp = get_val('defaultDscp')
    if default_dscp is not None:
        mml_output.append(f"set Transport=1,QosProfiles=1,DscpDscpMap=1$ defaultDscp {default_dscp}")
    
    # SET para dscp0 a dscp63
    for i in range(64):
        dscp_val = get_val(f'dscp{i}')
        if dscp_val is not None:
            mml_output.append(f"set Transport=1,QosProfiles=1,DscpDscpMap=1$ dscp{i} {dscp_val}")
    
    # SET para userLabel
    user_label = get_val('userLabel')
    if user_label:
        mml_output.append(f"set Transport=1,QosProfiles=1,DscpDscpMap=1$ userLabel {user_label}")
    
    mml_output.append("")
    
    print("DEBUG: Sección DscpDscpMap generada exitosamente")
    return mml_output


def generate_dscp_pcp_map_section(atnd_data: Dict[str, Any]) -> Optional[list]:
    """
    Genera la sección DscpPcpMap del script MML.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        Lista de líneas MML para la sección DscpPcpMap o None
    """
    if 'DscpPcpMap' not in atnd_data:
        print("DEBUG: Hoja DscpPcpMap no encontrada")
        return None
    
    df = atnd_data['DscpPcpMap']
    if df.empty:
        print("DEBUG: Hoja DscpPcpMap está vacía")
        return None
    
    mml_output = []
    
    # Header de la sección
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("/////// DscpPcpMap ")
    mml_output.append("/////////////////////////////////////////////////////////////")
    
    # Obtener la primera fila (asumiendo un solo sitio)
    row = df.iloc[0]
    
    # Comando CREATE
    mml_output.append("cr Transport=1,QosProfiles=1,DscpPcpMap=1")
    
    # Helper para obtener valor de columna
    def get_val(col_name):
        if col_name in df.columns:
            val = row[col_name]
            # Convertir a int si es float
            if isinstance(val, float) and not pd.isna(val):
                return str(int(val))
            elif pd.isna(val):
                return None
            return str(val).strip()
        return None
    
    # SET para defaultPcp
    default_pcp = get_val('defaultPcp')
    if default_pcp is not None:
        mml_output.append(f"set Transport=1,QosProfiles=1,DscpPcpMap=1$ defaultPcp {default_pcp}")
    
    # SET para pcp0 a pcp7
    for i in range(8):
        pcp_val = get_val(f'pcp{i}')
        if pcp_val is not None:
            # El valor puede contener múltiples números separados por espacios
            mml_output.append(f"set Transport=1,QosProfiles=1,DscpPcpMap=1$ pcp{i} {pcp_val}")
    
    # SET para userLabel
    user_label = get_val('userLabel')
    if user_label:
        mml_output.append(f"set Transport=1,QosProfiles=1,DscpPcpMap=1$ userLabel {user_label}")
    
    mml_output.append("")
    
    print("DEBUG: Sección DscpPcpMap generada exitosamente")
    return mml_output


def generate_pcp_pcp_map_section(atnd_data: Dict[str, Any]) -> Optional[list]:
    """
    Genera la sección PcpPcpMap del script MML.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        Lista de líneas MML para la sección PcpPcpMap o None
    """
    if 'PcpPcpMap' not in atnd_data:
        print("DEBUG: Hoja PcpPcpMap no encontrada")
        return None
    
    df = atnd_data['PcpPcpMap']
    if df.empty:
        print("DEBUG: Hoja PcpPcpMap está vacía")
        return None
    
    mml_output = []
    
    # Header de la sección
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("// PcpPcpMap ")
    mml_output.append("/////////////////////////////////////////////////////////////")
    
    # Obtener la primera fila (asumiendo un solo sitio)
    row = df.iloc[0]
    
    # Comando CREATE
    mml_output.append("cr Transport=1,QosProfiles=1,PcpPcpMap=1")
    
    # Helper para obtener valor de columna
    def get_val(col_name):
        if col_name in df.columns:
            val = row[col_name]
            # Convertir a int si es float
            if isinstance(val, float) and not pd.isna(val):
                return str(int(val))
            elif pd.isna(val):
                return None
            return str(val).strip()
        return None
    
    # SET para defaultPcp
    default_pcp = get_val('defaultPcp')
    if default_pcp is not None:
        mml_output.append(f"set Transport=1,QosProfiles=1,PcpPcpMap=1$ defaultPcp {default_pcp}")
    
    # SET para pcp0 a pcp7
    for i in range(8):
        pcp_val = get_val(f'pcp{i}')
        if pcp_val is not None:
            mml_output.append(f"set Transport=1,QosProfiles=1,PcpPcpMap=1$ pcp{i} {pcp_val}")
    
    # SET para userLabel
    user_label = get_val('userLabel')
    if user_label:
        mml_output.append(f"set Transport=1,QosProfiles=1,PcpPcpMap=1$ userLabel {user_label}")
    
    mml_output.append("")
    
    print("DEBUG: Sección PcpPcpMap generada exitosamente")
    return mml_output


def generate_ethernet_port_section(atnd_data: Dict[str, Any]) -> Optional[list]:
    """
    Genera la sección Ethernet Port del script MML.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        Lista de líneas MML para la sección Ethernet Port o None
    """
    if 'Ethernet_Port' not in atnd_data:
        print("DEBUG: Hoja Ethernet_Port no encontrada")
        return None
    
    df = atnd_data['Ethernet_Port']
    if df.empty:
        print("DEBUG: Hoja Ethernet_Port está vacía")
        return None
    
    mml_output = []
    
    # Header de la sección
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("// Ethernet Port ")
    mml_output.append("/////////////////////////////////////////////////////////////")
    
    # Helper para obtener valor de columna
    def get_val(row, col_name):
        if col_name in df.columns:
            val = row[col_name]
            # Convertir a int si es float
            if isinstance(val, float) and not pd.isna(val):
                return str(int(val))
            elif pd.isna(val):
                return None
            # Convertir booleanos
            if isinstance(val, bool):
                return str(val).lower()
            return str(val).strip()
        return None
    
    # Iterar sobre cada fila (puede haber múltiples puertos Ethernet)
    for index, row in df.iterrows():
        ethernet_port_id = get_val(row, 'ethernetPortId')
        
        if not ethernet_port_id:
            continue
        
        # SET para admOperatingMode
        adm_operating_mode = get_val(row, 'admOperatingMode')
        if adm_operating_mode is not None:
            mml_output.append(f"set Transport=1,EthernetPort={ethernet_port_id}$ admOperatingMode {adm_operating_mode}")
        
        # SET para administrativeState
        administrative_state = get_val(row, 'administrativeState')
        if administrative_state is not None:
            mml_output.append(f"set Transport=1,EthernetPort={ethernet_port_id}$ administrativeState {administrative_state}")
        
        # SET para autoNegEnable
        auto_neg_enable = get_val(row, 'autoNegEnable')
        if auto_neg_enable is not None:
            mml_output.append(f"set Transport=1,EthernetPort={ethernet_port_id}$ autoNegEnable {auto_neg_enable}")
        
        # SET para userLabel
        user_label = get_val(row, 'userLabel')
        if user_label:
            mml_output.append(f"set Transport=1,EthernetPort={ethernet_port_id}$ userLabel {user_label}")
    
    mml_output.append("")
    
    print("DEBUG: Sección Ethernet Port generada exitosamente")
    return mml_output


def generate_vlan_port_section(atnd_data: Dict[str, Any]) -> Optional[list]:
    """
    Genera la sección VlanPort del script MML.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        Lista de líneas MML para la sección VlanPort o None
    """
    if 'VlanPort' not in atnd_data:
        print("DEBUG: Hoja VlanPort no encontrada")
        return None
    
    df = atnd_data['VlanPort']
    if df.empty:
        print("DEBUG: Hoja VlanPort está vacía")
        return None
    
    mml_output = []
    
    # Header de la sección
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("// VlanPort ")
    mml_output.append("/////////////////////////////////////////////////////////////")
    
    # Helper para obtener valor de columna
    def get_val(row, col_name):
        if col_name in df.columns:
            val = row[col_name]
            # Convertir a int si es float
            if isinstance(val, float) and not pd.isna(val):
                return str(int(val))
            elif pd.isna(val):
                return None
            # Convertir booleanos
            if isinstance(val, bool):
                return str(val).lower()
            return str(val).strip()
        return None
    
    # Iterar sobre cada fila (puede haber múltiples VLANs)
    for index, row in df.iterrows():
        vlan_port_id = get_val(row, 'vlanPortId')
        
        if not vlan_port_id:
            continue
        
        # Comando CREATE
        mml_output.append(f"cr Transport=1,VlanPort={vlan_port_id}")
        
        # Parámetro encapsulation (en la línea siguiente del cr)
        encapsulation = get_val(row, 'encapsulation')
        if encapsulation:
            mml_output.append(f"{encapsulation} #encapsulation")
        
        # Parámetro vlanId (en la línea siguiente)
        vlan_id = get_val(row, 'vlanId')
        if vlan_id:
            mml_output.append(f"{vlan_id} #vlanId")
        
        # SET para isTagged
        is_tagged = get_val(row, 'isTagged')
        if is_tagged is not None:
            mml_output.append(f"set Transport=1,VlanPort={vlan_port_id}$ isTagged {is_tagged}")
        
        # SET para userLabel
        user_label = get_val(row, 'userLabel')
        if user_label:
            mml_output.append(f"set Transport=1,VlanPort={vlan_port_id}$ userLabel {user_label}")
        
        # Línea en blanco entre VLANs
        mml_output.append("")
    
    print("DEBUG: Sección VlanPort generada exitosamente")
    return mml_output


def generate_router_section(atnd_data: Dict[str, Any]) -> Optional[list]:
    """
    Genera la sección Router del script MML.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        Lista de líneas MML para la sección Router o None
    """
    if 'Router' not in atnd_data:
        print("DEBUG: Hoja Router no encontrada")
        return None
    
    df = atnd_data['Router']
    if df.empty:
        print("DEBUG: Hoja Router está vacía")
        return None
    
    mml_output = []
    
    # Header de la sección
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("// Router ")
    mml_output.append("/////////////////////////////////////////////////////////////")
    
    # Helper para obtener valor de columna
    def get_val(row, col_name):
        # Buscar columna con espacios o sin espacios
        for col in df.columns:
            if col.strip().lower() == col_name.lower():
                val = row[col]
                # Si val es una Serie (columnas duplicadas), tomar el primer valor
                if isinstance(val, pd.Series):
                    val = val.iloc[0] if not val.empty else None
                # Convertir a int si es float
                if isinstance(val, float) and not pd.isna(val):
                    return str(int(val))
                elif pd.isna(val) if not isinstance(val, pd.Series) else val is None:
                    return None
                # Convertir booleanos
                if isinstance(val, bool):
                    return str(val).lower()
                return str(val).strip() if val is not None else None
        return None
    
    # Iterar sobre cada fila (cada router)
    for index, row in df.iterrows():
        router_id = get_val(row, 'routerId')
        
        if not router_id:
            continue
        
        # 1. CREATE Router
        mml_output.append(f"cr Transport=1,Router={router_id}")
        user_label_router = get_val(row, 'userLabel')
        if user_label_router:
            mml_output.append(f"set Transport=1,Router={router_id}$ userLabel {user_label_router}")
        mml_output.append("")
        
        # 2. DnsClient (solo si tiene dnsClientId)
        dns_client_id = get_val(row, 'dnsClientId')
        if dns_client_id:
            mml_output.append(f"cr Transport=1,Router={router_id},DnsClient={dns_client_id}")
            
            dscp = get_val(row, 'dscp')
            if dscp:
                mml_output.append(f"set Transport=1,Router={router_id},DnsClient={dns_client_id}$ dscp {dscp}")
            
            server_address = get_val(row, 'serverAddress')
            if server_address:
                mml_output.append(f"set Transport=1,Router={router_id},DnsClient={dns_client_id}$ serverAddress {server_address}")
            
            used_server_address = get_val(row, 'usedServerAddress')
            if used_server_address:
                mml_output.append(f"set Transport=1,Router={router_id},DnsClient={dns_client_id}$ usedServerAddress {used_server_address}")
            
            mml_output.append("")
        
        # 3. InterfaceIPv4
        mml_output.append(f"cr Transport=1,Router={router_id},InterfaceIPv4=1")
        
        encapsulation = get_val(row, 'encapsulation')
        if encapsulation:
            mml_output.append(f"{encapsulation} #encapsulation")
        
        # loopback siempre false
        mml_output.append("false #loopback")
        
        egress_qos = get_val(row, 'egressQosMarking')
        if egress_qos:
            mml_output.append(f"set Transport=1,Router={router_id},InterfaceIPv4=1$ egressQosMarking {egress_qos}")
        
        user_label_interface = get_val(row, 'userLabel.1')
        if user_label_interface:
            mml_output.append(f"set Transport=1,Router={router_id},InterfaceIPv4=1$ userLabel {user_label_interface}")
        
        mml_output.append("")
        
        # 4. AddressIPv4
        address = get_val(row, 'address')
        address_ipv4_id = get_val(row, 'addressIPv4Id')
        if not address_ipv4_id:
            address_ipv4_id = "1"
        
        if address:
            mml_output.append(f"cr Transport=1,Router={router_id},InterfaceIPv4=1,AddressIPv4={address_ipv4_id}")
            mml_output.append(f"{address} #address")
            mml_output.append("0 #configurationMode")
            
            used_address = get_val(row, 'usedAddress')
            if used_address:
                mml_output.append(f"set Transport=1,Router={router_id},InterfaceIPv4=1,AddressIPv4={address_ipv4_id}$ usedAddress {used_address}")
            
            user_label_address = get_val(row, 'userLabel.2')
            if user_label_address:
                mml_output.append(f"set Transport=1,Router={router_id},InterfaceIPv4=1,AddressIPv4={address_ipv4_id}$ userLabel {user_label_address}")
            
            mml_output.append("")
        
        # 5. RouteTableIPv4Static
        route_table_id = get_val(row, 'routeTableIPv4StaticId')
        if not route_table_id:
            route_table_id = "1"
        
        mml_output.append(f"cr Transport=1,Router={router_id},RouteTableIPv4Static={route_table_id}")
        
        # 6. Dst
        dst = get_val(row, 'dst')
        dst_id = get_val(row, 'dstId')
        if not dst_id:
            dst_id = "1"
        
        if dst:
            mml_output.append(f"cr Transport=1,Router={router_id},RouteTableIPv4Static={route_table_id},Dst={dst_id}")
            mml_output.append(f"{dst} #dst")
            
            # 7. NextHop
            next_hop_address = get_val(row, 'address')  # Reutiliza la columna address
            next_hop_id = get_val(row, 'nextHopId')
            if not next_hop_id:
                next_hop_id = "1"
            
            if next_hop_address:
                # Extraer solo la IP (sin /26)
                next_hop_ip = next_hop_address.split('/')[0]
                # Cambiar el último octeto a .1 para el gateway
                parts = next_hop_ip.split('.')
                if len(parts) == 4:
                    parts[3] = '1'
                    gateway_ip = '.'.join(parts)
                    
                    mml_output.append(f"cr Transport=1,Router={router_id},RouteTableIPv4Static={route_table_id},Dst={dst_id},NextHop={next_hop_id}")
                    mml_output.append(f"{gateway_ip} #address")
                    mml_output.append("false #discard")
                    mml_output.append("d #reference")
                    
                    admin_distance = get_val(row, 'adminDistance')
                    if admin_distance:
                        mml_output.append(f"{admin_distance} #adminDistance")
        
        mml_output.append("")
    
    print("DEBUG: Sección Router generada exitosamente")
    return mml_output


def generate_twamp_responder_section(atnd_data: Dict[str, Any]) -> Optional[list]:
    """
    Genera la sección TwampResponder del script MML.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        Lista de líneas MML para la sección TwampResponder o None
    """
    if 'TwampREsponder' not in atnd_data:
        print("DEBUG: Hoja TwampREsponder no encontrada")
        return None
    
    df = atnd_data['TwampREsponder']
    if df.empty:
        print("DEBUG: Hoja TwampREsponder está vacía")
        return None
    
    mml_output = []
    
    # Header de la sección
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("// TWAMP_RESPONDER")
    mml_output.append("/////////////////////////////////////////////////////////////")
    
    # Helper para obtener valor de columna
    def get_val(row, col_name):
        if col_name in df.columns:
            val = row[col_name]
            # Convertir a int si es float
            if isinstance(val, float) and not pd.isna(val):
                return str(int(val))
            elif pd.isna(val):
                return None
            return str(val).strip()
        return None
    
    # Iterar sobre cada fila (cada TwampResponder)
    for index, row in df.iterrows():
        twamp_responder_id = get_val(row, 'twampResponderId')
        ip_address = get_val(row, 'ipAddress')
        
        if not twamp_responder_id or not ip_address:
            continue
        
        # Extraer el routerId del ipAddress
        # Ejemplo: "Router=LTE,InterfaceIPv4=1,AddressIPv4=1" -> "LTE"
        router_id = None
        if 'Router=' in ip_address:
            parts = ip_address.split(',')
            for part in parts:
                if part.startswith('Router='):
                    router_id = part.replace('Router=', '')
                    break
        
        if not router_id:
            continue
        
        # Comando CREATE
        mml_output.append(f"cr Transport=1,Router={router_id},TwampResponder={twamp_responder_id}")
        mml_output.append(f"{ip_address} #ipAddress")
        
        # udpPort
        udp_port = get_val(row, 'udpPort')
        if udp_port:
            mml_output.append(f"{udp_port} #udpPort")
        
        # SET para responderType
        responder_type = get_val(row, 'responderType')
        if responder_type:
            mml_output.append(f"set Transport=1,Router={router_id},TwampResponder={twamp_responder_id} responderType {responder_type}")
        
        # SET para userLabel
        user_label = get_val(row, 'userLabel')
        if user_label:
            mml_output.append(f"set Transport=1,Router={router_id},TwampResponder={twamp_responder_id} userLabel {user_label}")
        
        mml_output.append("")
    
    print("DEBUG: Sección TwampResponder generada exitosamente")
    return mml_output


def generate_ntp_frequency_sync_section(atnd_data: Dict[str, Any]) -> Optional[list]:
    """
    Genera la sección NtpFrequencySync del script MML.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        Lista de líneas MML para la sección NtpFrequencySync o None
    """
    if 'NtpFrequencySync' not in atnd_data:
        print("DEBUG: Hoja NtpFrequencySync no encontrada")
        return None
    
    df = atnd_data['NtpFrequencySync']
    if df.empty:
        print("DEBUG: Hoja NtpFrequencySync está vacía")
        return None
    
    mml_output = []
    
    # Header de la sección
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("// NtpFrequencySync")
    mml_output.append("/////////////////////////////////////////////////////////////")
    
    # Helper para obtener valor de columna
    def get_val(row, col_name):
        if col_name in df.columns:
            val = row[col_name]
            # Convertir a int si es float
            if isinstance(val, float) and not pd.isna(val):
                return str(int(val))
            elif pd.isna(val):
                return None
            return str(val).strip()
        return None
    
    # Iterar sobre cada fila (cada servidor NTP)
    for index, row in df.iterrows():
        ntp_id = get_val(row, 'ntpFrequencySyncId')
        
        if not ntp_id:
            continue
        
        # Comando CREATE
        mml_output.append(f"cr Transport=1,Ntp=1,NtpFrequencySync={ntp_id}")
        
        # addressIPv4Reference
        address_ref = get_val(row, 'addressIPv4Reference')
        if address_ref:
            mml_output.append(f"{address_ref} #addressIPv4Reference")
        
        # syncServerNtpIpAddress
        sync_server_ip = get_val(row, 'syncServerNtpIpAddress')
        if sync_server_ip:
            mml_output.append(f"{sync_server_ip} #syncServerNtpIpAddress")
        
        # SET para dscp
        dscp = get_val(row, 'dscp')
        if dscp:
            mml_output.append(f"set Transport=1,Ntp=1,NtpFrequencySync={ntp_id} dscp {dscp}")
        
        mml_output.append("")
    
    print("DEBUG: Sección NtpFrequencySync generada exitosamente")
    return mml_output


def generate_boundary_ordinary_clock_section(atnd_data: Dict[str, Any]) -> Optional[list]:
    """
    Genera la sección BoundaryOrdinaryClock del script MML.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        Lista de líneas MML para la sección BoundaryOrdinaryClock o None
    """
    if 'BoundaryOrdinaryClock' not in atnd_data:
        print("DEBUG: Hoja BoundaryOrdinaryClock no encontrada")
        return None
    
    df = atnd_data['BoundaryOrdinaryClock']
    if df.empty:
        print("DEBUG: Hoja BoundaryOrdinaryClock está vacía")
        return None
    
    mml_output = []
    
    # Header de la sección
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("// BoundaryOrdinaryClock")
    mml_output.append("/////////////////////////////////////////////////////////////")
    
    # Crear Transport=1,Ptp=1 primero
    mml_output.append("cr Transport=1,Ptp=1")
    
    # Mapeo de valores de texto a números
    clock_type_map = {
        'SLAVE_ONLY_ORDINARY_CLOCK': '2',
        'BOUNDARY_CLOCK': '1',
        'ORDINARY_CLOCK': '0'
    }
    
    ptp_profile_map = {
        'G_8275_1': '2',
        'G_8275_2': '3',
        'DEFAULT': '0'
    }
    
    # Helper para obtener valor de columna
    def get_val(row, col_name):
        # Buscar columna con espacios o sin espacios
        for col in df.columns:
            if col.strip().lower() == col_name.lower():
                val = row[col]
                # Convertir a int si es float
                if isinstance(val, float) and not pd.isna(val):
                    return str(int(val))
                elif pd.isna(val):
                    return None
                return str(val).strip()
        return None
    
    # Iterar sobre cada fila (normalmente solo una)
    for index, row in df.iterrows():
        boundary_clock_id = get_val(row, 'boundaryOrdinaryClockId')
        
        if boundary_clock_id is None:
            continue
        
        # Comando CREATE
        mml_output.append(f"cr Transport=1,Ptp=1,BoundaryOrdinaryClock={boundary_clock_id}")
        
        # clockType (mapear de texto a número)
        clock_type = get_val(row, 'clockType')
        if clock_type:
            clock_type_num = clock_type_map.get(clock_type, clock_type)
            mml_output.append(f"{clock_type_num} #clockType")
        
        # domainNumber
        domain_number = get_val(row, 'domainNumber')
        if domain_number:
            mml_output.append(f"{domain_number} #domainNumber")
        
        # ptpProfile (mapear de texto a número)
        ptp_profile = get_val(row, 'ptpProfile')
        if ptp_profile:
            ptp_profile_num = ptp_profile_map.get(ptp_profile, ptp_profile)
            mml_output.append(f"{ptp_profile_num} #ptpProfile")
    
    mml_output.append("")
    
    print("DEBUG: Sección BoundaryOrdinaryClock generada exitosamente")
    return mml_output


def generate_ptp_bc_oc_port_section(atnd_data: Dict[str, Any]) -> Optional[list]:
    """
    Genera la sección PtpBcOcPort del script MML.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        Lista de líneas MML para la sección PtpBcOcPort o None
    """
    if 'PtpBcOcPort' not in atnd_data:
        print("DEBUG: Hoja PtpBcOcPort no encontrada")
        return None
    
    df = atnd_data['PtpBcOcPort']
    if df.empty:
        print("DEBUG: Hoja PtpBcOcPort está vacía")
        return None
    
    mml_output = []
    
    # Header de la sección
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("// ptpBcOcPort")
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("")
    
    # Mapeo de valores de texto a números
    multicast_address_map = {
        'NON_FORWARDABLE': '1',
        'FORWARDABLE': '0'
    }
    
    # Helper para obtener valor de columna
    def get_val(row, col_name):
        if col_name in df.columns:
            val = row[col_name]
            # Convertir a int si es float
            if isinstance(val, float) and not pd.isna(val):
                return str(int(val))
            elif pd.isna(val):
                return None
            return str(val).strip()
        return None
    
    # Iterar sobre cada fila (puede haber múltiples puertos)
    for index, row in df.iterrows():
        ptp_port_id = get_val(row, 'ptpBcOcPortId')
        
        if ptp_port_id is None:
            continue
        
        # Comando CREATE
        mml_output.append(f"cr Transport=1,Ptp=1,BoundaryOrdinaryClock=0,ptpBcOcPort={ptp_port_id}")
        
        # transportInterface
        transport_interface = get_val(row, 'transportInterface')
        if transport_interface:
            mml_output.append(f"{transport_interface} #transportInterface")
        
        mml_output.append("")
        
        # SET para administrativeState
        admin_state = get_val(row, 'administrativeState')
        if admin_state:
            mml_output.append(f"set Transport=1,Ptp=1,BoundaryOrdinaryClock=0,ptpBcOcPort={ptp_port_id}$ administrativeState {admin_state}")
        
        # SET para associatedGrandmaster (puede estar vacío)
        associated_gm = get_val(row, 'associatedGrandmaster')
        # Siempre incluir la línea, aunque esté vacía
        mml_output.append(f"set Transport=1,Ptp=1,BoundaryOrdinaryClock=0,ptpBcOcPort={ptp_port_id}$ associatedGrandmaster {associated_gm if associated_gm else ''}")
        
        # SET para dscp
        dscp = get_val(row, 'dscp')
        if dscp:
            mml_output.append(f"set Transport=1,Ptp=1,BoundaryOrdinaryClock=0,ptpBcOcPort={ptp_port_id}$ dscp {dscp}")
        
        # SET para Pbit
        pbit = get_val(row, 'Pbit')
        if pbit:
            mml_output.append(f"set Transport=1,Ptp=1,BoundaryOrdinaryClock=0,ptpBcOcPort={ptp_port_id}$ Pbit {pbit}")
        
        # SET para ptpMulticastAddress (mapear de texto a número)
        multicast_addr = get_val(row, 'ptpMulticastAddress')
        if multicast_addr:
            multicast_num = multicast_address_map.get(multicast_addr, multicast_addr)
            mml_output.append(f"set Transport=1,Ptp=1,BoundaryOrdinaryClock=0,ptpBcOcPort={ptp_port_id}$ ptpMulticastAddress {multicast_num}")
        
        mml_output.append("")
    
    print("DEBUG: Sección PtpBcOcPort generada exitosamente")
    return mml_output


def generate_synchronization_section(atnd_data: Dict[str, Any]) -> Optional[list]:
    """
    Genera la sección Synchronization del script MML.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        Lista de líneas MML para la sección Synchronization o None
    """
    if 'Synchronization' not in atnd_data:
        print("DEBUG: Hoja Synchronization no encontrada")
        return None
    
    df_sync = atnd_data['Synchronization']
    if df_sync.empty:
        print("DEBUG: Hoja Synchronization está vacía")
        return None
    
    mml_output = []
    
    # Header de la sección
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("// Synchronization")
    mml_output.append("/////////////////////////////////////////////////////////////")
    
    # Mapeo de telecomStandard
    telecom_standard_map = {
        'OPTION_I': '1',
        'OPTION_II': '2',
        'OPTION_III': '3'
    }
    
    # Helper para obtener valor de columna
    def get_val(row, col_name, df):
        # Buscar columna con espacios o sin espacios
        for col in df.columns:
            if col.strip().lower() == col_name.lower():
                val = row[col]
                if isinstance(val, float) and not pd.isna(val):
                    return str(int(val))
                elif pd.isna(val):
                    return None
                if isinstance(val, bool):
                    return str(val).lower()
                return str(val).strip()
        return None
    
    # Obtener datos de Synchronization
    row_sync = df_sync.iloc[0]
    
    # SET para fixedPosition
    fixed_position = get_val(row_sync, 'fixedPosition', df_sync)
    if fixed_position:
        mml_output.append(f"set Transport=1,Synchronization=1 fixedPosition {fixed_position}")
    
    # SET para telecomStandard (mapear de texto a número)
    telecom_std = get_val(row_sync, 'telecomStandard', df_sync)
    if telecom_std:
        telecom_num = telecom_standard_map.get(telecom_std, telecom_std)
        mml_output.append(f"set Transport=1,Synchronization=1 telecomStandard {telecom_num}")
    
    # CREATE SyncEthInput - Obtener encapsulation dinámicamente
    # Buscar en SfpModule o Ethernet_Port
    encapsulation_value = "EthernetPort=TN_B"  # Valor por defecto
    
    if 'SfpModule' in atnd_data and not atnd_data['SfpModule'].empty:
        df_sfp = atnd_data['SfpModule']
        if 'SfpModule' in df_sfp.columns:
            sfp_module = df_sfp.iloc[0]['SfpModule']
            if not pd.isna(sfp_module):
                encapsulation_value = f"EthernetPort={sfp_module}"
    elif 'Ethernet_Port' in atnd_data and not atnd_data['Ethernet_Port'].empty:
        df_eth = atnd_data['Ethernet_Port']
        if 'ethernetPortId' in df_eth.columns:
            eth_port_id = df_eth.iloc[0]['ethernetPortId']
            if not pd.isna(eth_port_id):
                encapsulation_value = f"EthernetPort={eth_port_id}"
    
    mml_output.append("cr Transport=1,Synchronization=1,SyncEthInput=1")
    mml_output.append(f"{encapsulation_value} #encapsulation")
    
    # CREATE RadioEquipmentClock
    mml_output.append("cr Transport=1,Synchronization=1,RadioEquipmentClock=1")
    mml_output.append("set Transport=1,Synchronization=1,RadioEquipmentClock=1$ minQualityLevel qualityLevelValueOptionI=1,qualityLevelValueOptionII=2,qualityLevelValueOptionIII=1")
    mml_output.append("set Transport=1,Synchronization=1,RadioEquipmentClock=1$ selectionProcessMode 2")
    
    # DELETE RadioEquipmentClockReference=SyncE
    mml_output.append("del Transport=1,Synchronization=1,RadioEquipmentClock=1,RadioEquipmentClockReference=SyncE")
    mml_output.append("y")
    
    mml_output.append("")
    
    print("DEBUG: Sección Synchronization generada exitosamente")
    return mml_output


def generate_radio_equipment_clock_reference_section(atnd_data: Dict[str, Any]) -> Optional[list]:
    """
    Genera la sección RadioEquipmentClockReference del script MML.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        Lista de líneas MML para la sección RadioEquipmentClockReference o None
    """
    if 'RadioEquipmentClockReference' not in atnd_data:
        print("DEBUG: Hoja RadioEquipmentClockReference no encontrada")
        return None
    
    df = atnd_data['RadioEquipmentClockReference']
    if df.empty:
        print("DEBUG: Hoja RadioEquipmentClockReference está vacía")
        return None
    
    mml_output = []
    
    # Header de la sección
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("// RadioEquipmentClockReference")
    mml_output.append("/////////////////////////////////////////////////////////////")
    
    # Helper para obtener valor de columna
    def get_val(row, col_name):
        if col_name in df.columns:
            val = row[col_name]
            # Convertir a int si es float
            if isinstance(val, float) and not pd.isna(val):
                return str(int(val))
            elif pd.isna(val):
                return None
            return str(val).strip()
        return None
    
    # Iterar sobre cada fila (cada referencia de reloj)
    for index, row in df.iterrows():
        ref_id = get_val(row, 'radioEquipmentClockReferenceId')
        
        if not ref_id:
            continue
        
        # Comando CREATE
        mml_output.append(f"cr Transport=1,Synchronization=1,RadioEquipmentClock=1,RadioEquipmentClockReference={ref_id}")
        
        # encapsulation
        encapsulation = get_val(row, 'encapsulation')
        if encapsulation:
            mml_output.append(f"{encapsulation} #encapsulation")
        
        # priority
        priority = get_val(row, 'priority')
        if priority:
            mml_output.append(f"{priority} #Priority")
        
        # SET para administrativeState
        admin_state = get_val(row, 'administrativeState')
        if admin_state is not None:
            mml_output.append(f"set Transport=1,Synchronization=1,RadioEquipmentClock=1,RadioEquipmentClockReference={ref_id} administrativestate {admin_state}")
        
        mml_output.append("")
    
    print("DEBUG: Sección RadioEquipmentClockReference generada exitosamente")
    return mml_output


def generate_features_section(atnd_data: Dict[str, Any], site_name: str) -> Optional[list]:
    """
    Genera la sección Features del script MML.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
        site_name: Nombre del sitio
    
    Returns:
        Lista de líneas MML para la sección Features o None
    """
    if 'ATND Transport Features' not in atnd_data:
        print("DEBUG: Hoja ATND Transport Features no encontrada")
        return None
    
    df = atnd_data['ATND Transport Features']
    if df.empty:
        print("DEBUG: Hoja ATND Transport Features está vacía")
        return None
    
    mml_output = []
    
    # Header de la sección
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("// Features")
    mml_output.append("/////////////////////////////////////////////////////////////")
    
    # Importar el mapeo de features desde functions_3G
    try:
        from functions_3G.feature_mapping import FEATURE_MAPPING
    except ImportError:
        print("DEBUG: No se pudo importar FEATURE_MAPPING")
        FEATURE_MAPPING = {}
    
    # Obtener la primera fila (datos del sitio)
    row = df.iloc[0]
    
    # Iterar sobre las columnas (cada columna es un feature)
    for col in df.columns:
        if col == 'Site':
            continue
        
        # Obtener el valor del feature (0 o 1)
        feature_value = row[col]
        
        # Convertir a int si es float
        if isinstance(feature_value, float) and not pd.isna(feature_value):
            feature_value = int(feature_value)
        elif pd.isna(feature_value):
            continue
        
        # Buscar el código CXC en el mapeo
        cxc_code = FEATURE_MAPPING.get(col, None)
        
        if cxc_code:
            # Generar comando SET
            mml_output.append(f"set SystemFunctions=1,Lm=1,FeatureState={cxc_code} featureState {feature_value}")
        else:
            print(f"DEBUG: Feature '{col}' no encontrado en FEATURE_MAPPING")
    
    mml_output.append("")
    
    print("DEBUG: Sección Features generada exitosamente")
    return mml_output
