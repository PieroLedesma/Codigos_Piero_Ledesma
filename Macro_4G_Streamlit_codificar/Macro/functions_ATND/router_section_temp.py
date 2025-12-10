# Continuación de atnd_generator.py - Función Router

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
