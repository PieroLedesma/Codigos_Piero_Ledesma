import os
import pandas as pd

def extract_qos_dscp_to_pd(df_atnd):
    """
    Extrae el mapeo de DSCP to PD desde la hoja QoS R6672_BB.
    Retorna lista de tuplas (ip_number, qos_value) para ip 0 to 63.
    """
    qos_mappings = []
    
    try:
        if 'QoS R667_2_BB' not in df_atnd and 'QoS R6672_BB' not in df_atnd:
            print("WARNING: No se encontró hoja QoS R6672_BB, usando valores por defecto")
            return generate_default_dscp_mappings()
        
        # Intentar ambas variantes del nombre
        df_qos = df_atnd.get('QoS R6672_BB') or df_atnd.get('QoS R667_2_BB')
        
        if df_qos is None or (isinstance(df_qos, pd.DataFrame) and df_qos.empty):
            return generate_default_dscp_mappings()
        
        # Convertir a string para búsqueda
        df_str = df_qos.astype(str)
        
        # Buscar la sección "ip X to qos Y" en el dataframe
        # Buscar líneas que contengan "ip" y "to qos" o "to ipprec"
        for idx, row in df_str.iterrows():
            for col_idx, cell_value in enumerate(row):
                cell_str = str(cell_value).strip()
                # Buscar patrones como "ip 0 to qos 0" o "ip 18 to qos 8"
                if 'ip' in cell_str.lower() and 'to' in cell_str.lower() and 'qos' in cell_str.lower():
                    parts = cell_str.split()
                    try:
                        # Formato esperado: "ip X to qos Y"
                        if len(parts) >= 5 and parts[0].lower() == 'ip':
                            ip_num = int(parts[1])
                            qos_val = int(parts[4])
                            if 0 <= ip_num <= 63:
                                qos_mappings.append((ip_num, qos_val))
                    except (ValueError, IndexError):
                        continue
        
        # Si encontramos mapeos, ordenar y completar los que falten
        if qos_mappings:
            # Ordenar por ip number
            qos_mappings.sort(key=lambda x: x[0])
            # Llenar los gaps con valor 0
            complete_mappings = []
            mapped_ips = {ip_num for ip_num, _ in qos_mappings}
            
            for i in range(64):
                if i in mapped_ips:
                    # Buscar el valor correspondiente
                    for ip_num, qos_val in qos_mappings:
                        if ip_num == i:
                            complete_mappings.append((i, qos_val))
                            break
                else:
                    complete_mappings.append((i, 0))
            
            return complete_mappings
        
    except Exception as e:
        print(f"Error extrayendo QoS DSCP mappings: {e}")
    
    # Fallback: valores por defecto
    return generate_default_dscp_mappings()


def generate_default_dscp_mappings():
    """Genera los mapeos por defecto basados en el ejemplo del usuario."""
    mappings = []
    for i in range(64):
        if i in [18, 20, 22]:
            mappings.append((i, 8))
        elif i in [26, 28]:
            mappings.append((i, 16))
        elif i in [34, 36, 38]:
            mappings.append((i, 24))
        elif i in [40, 42, 44, 46]:
            mappings.append((i, 40))
        elif i == 48:
            mappings.append((i, 48))
        elif i == 56:
            mappings.append((i, 56))
        else:
            mappings.append((i, 0))
    return mappings


def extract_ethernet_pbit_mappings(df_atnd):
    """
    Extrae el mapeo de ethernet pbit desde QoS R6672_BB.
    Retorna lista de tuplas (ethernet_number, qos_value) para ethernet 0 to 7.
    """
    # Valores por defecto del ejemplo del usuario
    default_mappings = [
        (0, 0),
        (1, 0),
        (2, 8),
        (3, 16),
        (4, 24),
        (5, 40),
        (6, 48),
        (7, 56)
    ]
    
    try:
        if 'QoS R667_2_BB' not in df_atnd and 'QoS R6672_BB' not in df_atnd:
            return default_mappings
        
        df_qos = df_atnd.get('QoS R6672_BB') or df_atnd.get('QoS R667_2_BB')
        
        if df_qos is None or (isinstance(df_qos, pd.DataFrame) and df_qos.empty):
            return default_mappings
        
        df_str = df_qos.astype(str)
        ethernet_mappings = []
        
        # Buscar patrones como "ethernet 0 to qos 0"
        for idx, row in df_str.iterrows():
            for col_idx, cell_value in enumerate(row):
                cell_str = str(cell_value).strip()
                if 'ethernet' in cell_str.lower() and 'to' in cell_str.lower() and 'qos' in cell_str.lower():
                    parts = cell_str.split()
                    try:
                        if len(parts) >= 5 and parts[0].lower() == 'ethernet':
                            eth_num = int(parts[1])
                            qos_val = int(parts[4])
                            if 0 <= eth_num <= 7:
                                ethernet_mappings.append((eth_num, qos_val))
                    except (ValueError, IndexError):
                        continue
        
        if ethernet_mappings:
            ethernet_mappings.sort(key=lambda x: x[0])
            # Completar si faltan valores
            complete = []
            mapped = {num for num, _ in ethernet_mappings}
            for i in range(8):
                if i in mapped:
                    for num, val in ethernet_mappings:
                        if num == i:
                            complete.append((num, val))
                            break
                else:
                    # Usar valor por defecto
                    for num, val in default_mappings:
                        if num == i:
                            complete.append((num, val))
                            break
            return complete
        
    except Exception as e:
        print(f"Error extrayendo ethernet pbit mappings: {e}")
    
    return default_mappings


def extract_contexts_from_l3_config(df_atnd):
    """
    Extrae los contexts desde Router Layer 3 Configuration.
    
    Retorna lista de diccionarios con la información de cada context:
    {
        'name': 'NOC',
        'interface_name': 'NOC',
        'interface_description': 'Management Interface NOC',
        'ip_address': '10.73.191.108/27',
        'route_nexthop': '10.73.191.97',
        'route_description': 'defaultGateway towards NOC Network',
        'ntp_servers': ['server 10.250.221.25 version 3 source SAFE']
    }
    """
    contexts = []
    
    # SOLO generar estos 3 contexts específicos
    ALLOWED_CONTEXTS = ['NOC', 'SAFE', 'SYNC']
    
    try:
        if 'Router Layer 3 Configuration' not in df_atnd:
            print("WARNING: No se encontró hoja Router Layer 3 Configuration")
            return contexts
        
        df = df_atnd['Router Layer 3 Configuration']
        if df.empty:
            return contexts
        
        df_str = df.astype(str)
        
        # Buscar todas las filas que contengan "Context" en alguna columna
        context_rows = []
        for idx, row in df_str.iterrows():
            for col_idx, cell in enumerate(row):
                if 'context' in str(cell).lower() and 'local' not in str(cell).lower():
                    # Buscar el nombre del context
                    cell_parts = str(cell).split()
                    if len(cell_parts) >= 2 and cell_parts[0].lower() == 'context':
                        context_name = cell_parts[1].upper()
                        # FILTRO: Solo procesar contexts permitidos
                        if context_name in ALLOWED_CONTEXTS:
                            context_rows.append((idx, context_name))
        
        # Para cada context encontrado, extraer su información
        for row_idx, context_name in context_rows:
            context_data = {
                'name': context_name,
                'interface_name': context_name,
                'interface_description': f'Management Interface {context_name}',
                'ip_address': None,
                'route_nexthop': None,
                'route_description': f'defaultGateway towards {context_name} Network',
                'ntp_servers': []
            }
            
            # Buscar información en las filas siguientes (buscar hasta 20 filas después)
            for i in range(row_idx, min(row_idx + 20, len(df))):
                row = df.iloc[i]
                row_str = str(row.values).lower()
                
                # Buscar IP Address (en columna IPv4 Address)
                for col_idx, cell in enumerate(row):
                    cell_str = str(cell).strip()
                    
                    # Detectar IP address (formato x.x.x.x/yy)
                    if '.' in cell_str and '/' in cell_str and 'nan' not in cell_str.lower():
                        # Verificar que sea una IP válida
                        ip_part = cell_str.split('/')[0]
                        if ip_part.count('.') == 3:
                            try:
                                octets = [int(x) for x in ip_part.split('.')]
                                if all(0 <= x <= 255 for x in octets):
                                    if not context_data['ip_address']:
                                        context_data['ip_address'] = cell_str
                                        print(f"DEBUG: {context_name} - IP encontrada: {cell_str}")
                            except ValueError:
                                pass
                    
                    # Buscar Next-Hop (buscar en filas que contengan "Route/Netmask" o "0.0.0.0/0")
                    # El next-hop está en la columna siguiente cuando encuentra "0.0.0.0/0" o "Next-Hop"
                    if ('0.0.0.0' in cell_str or 'route' in cell_str.lower() or 'next-hop' in cell_str.lower()) and not context_data['route_nexthop']:
                        # Buscar en las columnas siguientes de esta fila
                        for next_col_idx in range(col_idx + 1, min(col_idx + 3, len(row))):
                            next_cell = str(row.iloc[next_col_idx]).strip()
                            # Verificar si es una IP válida (sin /)
                            if '.' in next_cell and '/' not in next_cell and 'nan' not in next_cell.lower():
                                if next_cell.count('.') == 3:
                                    try:
                                        octets = [int(x) for x in next_cell.split('.')]
                                        if all(0 <= x <= 255 for x in octets):
                                            context_data['route_nexthop'] = next_cell
                                            print(f"DEBUG: {context_name} - Next-hop encontrado: {next_cell}")
                                            break
                                    except ValueError:
                                        pass
            
            # Ajustes específicos por context
            if context_name == 'SYNC':
                context_data['interface_name'] = 'SYNC_8275.2'
                context_data['interface_description'] = 'Sync 8275.2 APTS'
                # SYNC no tiene IP ni route
                context_data['ip_address'] = None
                context_data['route_nexthop'] = None
            
            # NTP servers solo para SAFE
            if context_name == 'SAFE':
                context_data['ntp_servers'] = ['server 10.250.221.25 version 3 source SAFE']
                # SAFE tiene descripción especial para el route
                context_data['route_description'] = 'defaultGateway towards SOEM Network'
            
            contexts.append(context_data)
        
        # ORDENAR contexts en el orden específico: NOC, SAFE, SYNC
        context_order = {'NOC': 0, 'SAFE': 1, 'SYNC': 2}
        contexts.sort(key=lambda x: context_order.get(x['name'], 99))
        
        print(f"DEBUG: Encontrados {len(contexts)} contexts: {[c['name'] for c in contexts]}")
        
    except Exception as e:
        print(f"Error extrayendo contexts: {e}")
    
    return contexts


def generate_context_section(context_data):
    """
    Genera las líneas MML para un context específico.
    """
    lines = []
    
    ctx_name = context_data['name']
    
    lines.append(f"context {ctx_name}")
    lines.append("!")
    lines.append("no ip domain-lookup")
    lines.append("!")
    lines.append("!")
    lines.append("!")
    
    # Interface
    lines.append(f"interface {context_data['interface_name']}")
    lines.append(f"description {context_data['interface_description']}")
    
    # IP address (si existe)
    if context_data['ip_address']:
        lines.append(f"ip address {context_data['ip_address']}")
    
    lines.append("propagate qos from ip class-map dscp-to-pd")
    lines.append("!")
    lines.append("!")
    
    # Static route (si existe next-hop)
    if context_data['route_nexthop']:
        lines.append(f"ip route 0.0.0.0/0 {context_data['route_nexthop']} description {context_data['route_description']}")
    
    lines.append("!")
    lines.append("!")
    lines.append("!")
    
    # Services
    lines.append("service ftp client")
    lines.append("service ssh")
    lines.append("service sftp")
    lines.append("service scp")
    lines.append("service telnet")
    lines.append("service snmp server")
    lines.append("!")
    
    # NTP (si existe)
    if context_data.get('ntp_servers'):
        lines.append("ntp-mode")
        lines.append("!")
        for ntp_line in context_data['ntp_servers']:
            lines.append(ntp_line)
        lines.append("!")
        lines.append("!")
    
    lines.append("!")
    lines.append("!")
    lines.append("no logging console")
    lines.append("!")
    lines.append("!")
    lines.append("!")
    
    return lines


def extract_qos_policies(df_atnd):
    """
    Extrae las políticas QoS R6K_1GE desde la hoja QoS R6672_BB.
    
    Retorna lista de diccionarios con las políticas en el orden correcto:
    [
        {
            'name': 'R6K_1GE',
            'type': 'pwfq',
            'rate_pir': 10000000,
            'rate_cir': 10000000,
            'queues': {...}
        },
        ...
    ]
    """
    # Políticas por defecto basadas en el ejemplo (10Mbps y 1Mbps)
    default_policies = [
        {
            'name': 'R6K_1GE',
            'type': 'pwfq',
            'rate_pir': 10000000,
            'rate_cir': 10000000,
            'queues': {
                0: {'priority': 0, 'strict_priority': 0, 'rate_maximum': 800000},
                1: {'priority': 0, 'strict_priority': 1, 'rate_maximum': 200000},
                2: {'priority': 0, 'strict_priority': 2, 'rate_maximum': 3000000},
                3: {'priority': 0, 'strict_priority': 3, 'rate_maximum': 500000},
                4: {'priority': 4, 'weight': 10},
                5: {'priority': 4, 'weight': 20},
                6: {'priority': 4, 'weight': 10},
                7: {'priority': 4, 'weight': 20}
            }
        },
        {
            'name': 'R6K_1GE',
            'type': 'pwfq',
            'rate_pir': 1000000,
            'rate_cir': 1000000,
            'queues': {
                0: {'priority': 0, 'strict_priority': 0, 'rate_maximum': 80000},
                1: {'priority': 0, 'strict_priority': 1, 'rate_maximum': 20000},
                2: {'priority': 0, 'strict_priority': 2, 'rate_maximum': 300000},
                3: {'priority': 0, 'strict_priority': 3, 'rate_maximum': 50000},
                4: {'priority': 4, 'weight': 10},
                5: {'priority': 4, 'weight': 20},
                6: {'priority': 4, 'weight': 10},
                7: {'priority': 4, 'weight': 20}
            }
        }
    ]
    
    try:
        if 'QoS R667_2_BB' not in df_atnd and 'QoS R6672_BB' not in df_atnd:
            print("WARNING: No se encontró hoja QoS R6672_BB, usando políticas por defecto")
            return default_policies
        
        df_qos = df_atnd.get('QoS R6672_BB') or df_atnd.get('QoS R667_2_BB')
        
        if df_qos is None or (isinstance(df_qos, pd.DataFrame) and df_qos.empty):
            return default_policies
        
        # TODO: Aquí se podría implementar la extracción dinámica desde el Excel
        # Por ahora usamos los valores por defecto que son estándar
        
        print(f"DEBUG: Usando políticas QoS por defecto (2 políticas R6K_1GE)")
        
    except Exception as e:
        print(f"Error extrayendo QoS policies: {e}")
    
    return default_policies


def generate_qos_policies_section(df_atnd):
    """
    Genera la sección completa de QoS policies (dot1q, queue-map, policies).
    """
    lines = []
    
    # === PARTE ESTÁTICA ===
    lines.append("!")
    lines.append("dot1q profile 8021p-on-useip")
    lines.append("propagate qos from ethernet class-map ip-pbit-to-pd")
    lines.append("!")
    lines.append("ipv4 enable-fragment")
    lines.append("!")
    lines.append("qos queue-map 8-queues")
    lines.append("num-queues 8")
    lines.append("queue 0 priority 0")
    lines.append("queue 1 priority 1")
    lines.append("queue 2 priority 2")
    lines.append("queue 3 priority 3")
    lines.append("queue 4 priority 4")
    lines.append("queue 5 priority 5")
    lines.append("queue 6 priority 6")
    lines.append("queue 7 priority 7")
    lines.append("!")
    lines.append("!")
    lines.append("!")
    
    # === PARTE DINÁMICA: QoS Policies ===
    policies = extract_qos_policies(df_atnd)
    
    for policy in policies:
        lines.append(f"qos policy {policy['name']} {policy['type']}")
        lines.append(f"rate pir {policy['rate_pir']}")
        lines.append(f"rate cir {policy['rate_cir']}")
        lines.append("num-queues 8")
        
        # Generar configuración de cada queue
        for queue_num in range(8):
            queue_config = policy['queues'].get(queue_num, {})
            
            # Queue con strict-priority y rate maximum (queues 0-3)
            if 'strict_priority' in queue_config:
                priority = queue_config['priority']
                strict_prio = queue_config['strict_priority']
                rate_max = queue_config.get('rate_maximum', 0)
                
                lines.append(f"queue {queue_num} priority {priority} strict-priority {strict_prio}")
                if rate_max > 0:
                    lines.append(f"queue {queue_num} rate maximum {rate_max}")
            
            # Queue con weight (queues 4-7)
            elif 'weight' in queue_config:
                priority = queue_config['priority']
                weight = queue_config['weight']
                lines.append(f"queue {queue_num} priority {priority} weight {weight}")
        
        lines.append("!")
    
    return lines


def extract_system_clock_timezone(df_atnd):
    """
    Extrae el timezone del system clock desde Router Network Management.
    
    Retorna string como "UTC 0 0 local" o None si no se encuentra.
    """
    try:
        if 'Router Network Management' not in df_atnd:
            print("WARNING: No se encontró hoja Router Network Management")
            return None
        
        df = df_atnd['Router Network Management']
        if df.empty:
            return None
        
        df_str = df.astype(str)
        
        # Buscar la celda que contenga "system clock"
        for idx, row in df_str.iterrows():
            for col_idx, cell in enumerate(row):
                if 'system clock' in str(cell).lower():
                    # Buscar el valor del timezone en las columnas siguientes
                    for next_col in range(col_idx + 1, min(col_idx + 4, len(row))):
                        timezone_val = str(row.iloc[next_col]).strip()
                        if timezone_val and 'nan' not in timezone_val.lower() and len(timezone_val) > 3:
                            # Limpiar el valor (puede venir como "timezone UTC 0 0 local")
                            if 'timezone' in timezone_val.lower():
                                timezone_val = timezone_val.replace('timezone', '').strip()
                            print(f"DEBUG: System clock timezone encontrado: {timezone_val}")
                            return timezone_val
        
        print(f"WARNING: System clock timezone no encontrado en Router Network Management")
        
    except Exception as e:
        print(f"Error extrayendo system clock: {e}")
    
    return None


def generate_system_card_section(df_atnd):
    """
    Genera la sección de system clock y card configuration.
    """
    lines = []
    
    # Extraer timezone
    timezone = extract_system_clock_timezone(df_atnd)
    
    # System clock (dinámico - solo si se encuentra)
    if timezone:
        lines.append(f"system clock timezone {timezone}")
        lines.append("!")
    
    # Card configuration (estático)
    lines.append("card lc-1-10ge-24-100ge-4-port 1")
    lines.append("!")
    lines.append("!")
    
    return lines


def extract_link_group_port(df_atnd):
    """
    Extrae el puerto específico que se usa para el link-group (el que se crea en Basic).
    Retorna el port ID (ej: '1/20') o None.
    """
    try:
        if 'Port Detail' not in df_atnd:
            return None
        
        df = df_atnd['Port Detail']
        df_str = df.astype(str)
        
        # Buscar "link-group"
        for idx, row in df_str.iterrows():
            for col_idx, cell in enumerate(row):
                if 'link-group' in str(cell).lower():
                    # El puerto suele estar en columna 2
                    port_val = str(df.iloc[idx, 2]).strip()
                    if '/' in port_val and 'nan' not in port_val.lower():
                        print(f"DEBUG: Found link-group port: {port_val} (will be excluded from Advanced)")
                        return port_val
    except Exception as e:
        print(f"Error extracting link-group port: {e}")
    
    return None


def extract_ports_from_port_detail(df_atnd, vlan_type="ALL_VLAN"):
    """
    Extrae información de puertos desde Port Detail.
    
    Retorna lista de diccionarios:
    [
        {
            'port': '1/4',
            'speed': '1ge',
            'description': 'DUW FDD BI919 1900',
            'type': 'FDD',  # FDD, TDD, o SAFE
            'qos_policy': 'R6K_1GE'
        },
        ...
    ]
    """
    ports = []
    
    # Extraer el puerto del link-group para excluirlo
    lg_port = extract_link_group_port(df_atnd)
    
    try:
        if 'Port Detail' not in df_atnd:
            print("WARNING: No se encontró hoja Port Detail")
            return ports
        
        df = df_atnd['Port Detail']
        if df.empty:
            return ports
        
        df_str = df.astype(str)
        
        # Buscar columnas importantes
        port_col = None
        desc_col = None
        
        # Buscar headers
        for idx, row in df_str.iterrows():
            for col_idx, cell in enumerate(row):
                cell_lower = str(cell).lower()
                if 'port' in cell_lower and not port_col:
                    port_col = col_idx
                if 'description' in cell_lower and not desc_col:
                    desc_col = col_idx
            
            # Si ya encontramos las columnas, las filas siguientes son datos
            if port_col is not None and desc_col is not None:
                # Procesar filas de datos
                for data_idx in range(idx + 1, len(df)):
                    data_row = df.iloc[data_idx]
                    
                    port_val = str(data_row.iloc[port_col]).strip()
                    desc_val = str(data_row.iloc[desc_col]).strip() if desc_col < len(data_row) else ""
                    
                    # Validar que sea un puerto válido (formato X/Y)
                    if '/' in port_val and 'nan' not in port_val.lower():
                        # FILTRAR: Ignorar puertos con description "nan" o vacía
                        if not desc_val or desc_val.lower() == 'nan' or len(desc_val) < 2:
                            continue
                        
                        # FILTRAR: Excluir puerto 1/24
                        if port_val == '1/24' or port_val.endswith('/24'):
                            continue
                        
                        # FILTRAR: Excluir el puerto específico del link-group (el que se crea en Basic)
                        if lg_port and port_val == lg_port:
                            print(f"DEBUG: Skipping link-group port {port_val} (created in Basic script)")
                            continue
                        
                        # Determinar tipo de puerto
                        port_type = 'OTHER'
                        if 'SAFE' in desc_val.upper():
                            port_type = 'SAFE'
                        elif 'FDD' in desc_val.upper():
                            port_type = 'FDD'
                        elif 'TDD' in desc_val.upper():
                            port_type = 'TDD'
                        
                        # Determinar velocidad (1ge o 10ge)
                        # TDD suele ser 10ge, pero verificar en el port number o descripción
                        speed = '1ge'
                        if 'TDD' in desc_val.upper():
                            speed = '10ge'  # TDD son 10ge por defecto
                        elif '10' in port_val or 'ten' in desc_val.lower() or '10ge' in desc_val.lower():
                            speed = '10ge'
                        
                        # Determinar QoS policy
                        qos_policy = 'R6K_10GE' if speed == '10ge' else 'R6K_1GE'
                        
                        port_info = {
                            'port': port_val,
                            'speed': speed,
                            'description': desc_val,
                            'type': port_type,
                            'qos_policy': qos_policy,
                            'service_instances': []
                        }
                        
                        ports.append(port_info)
                
                break
        
        print(f"DEBUG: Encontrados {len(ports)} puertos en Port Detail")
        
    except Exception as e:
        print(f"Error extrayendo puertos: {e}")
    
    return ports


def extract_service_instances(df_atnd, vlan_type="ALL_VLAN"):
    """
    Extrae service instances desde Layer 2 ALL CLIENT (para All VLAN).
    
    Retorna diccionario: {port: [vlan1, vlan2, ...]}
    """
    service_instances = {}
    
    try:
        # Determinar nombre de hoja según tipo - intentar múltiples variantes
        possible_sheet_names = [
            'Layer 2 ALL CLIENT',
            'Layer 2 Data',  # Nombre común en ATNDs
            'Layer 2 MASTER VLAN'
        ]
        
        sheet_name = None
        for name in possible_sheet_names:
            if name in df_atnd:
                sheet_name = name
                print(f"DEBUG: Using sheet '{sheet_name}' for service instances")
                break
        
        if sheet_name is None:
            print(f"WARNING: No se encontró hoja Layer 2. Hojas disponibles: {list(df_atnd.keys())}")
            # Intentar fallback inmediatamente
            return extract_service_instances_from_port_detail(df_atnd)
        
        df = df_atnd[sheet_name]
        if df.empty:
            return service_instances
        
        df_str = df.astype(str)
        
        # ESTRATEGIA: Buscar todos los números que parezcan VLANs (1000-9999)
        # y asociarlos con el puerto más cercano mencionado arriba
        
        current_port = None
        
        for idx, row in df_str.iterrows():
            row_text = ' '.join([str(cell) for cell in row if str(cell) != 'nan']).upper()
            
            # Buscar menciones de puertos (1/1, 1/2, etc.)
            for col_idx, cell in enumerate(row):
                cell_str = str(cell).strip()
                
                # Detectar puerto (formato 1/X)
                if '1/' in cell_str and len(cell_str) < 10:
                    # Extraer número de puerto
                    try:
                        port_match = cell_str.split('1/')[-1].split()[0]
                        if port_match.isdigit():
                            current_port = port_match
                            print(f"DEBUG: Found port reference: 1/{current_port}")
                    except:
                        pass
                
                # Detectar VLANs (números de 70-9999)
                if cell_str.isdigit():
                    vlan_num = int(cell_str)
                    # Las VLANs suelen estar en el rango 70-9999
                    if 70 <= vlan_num <= 9999:
                        # Si tenemos un puerto actual, asignar la VLAN
                        if current_port:
                            if current_port not in service_instances:
                                service_instances[current_port] = []
                            if vlan_num not in service_instances[current_port]:
                                service_instances[current_port].append(vlan_num)
                                print(f"DEBUG: Added VLAN {vlan_num} to port 1/{current_port}")
        
        # FALLBACK: Si no encontró nada, usar Port Detail
        if not service_instances:
            print("DEBUG: No VLANs found in Layer 2 sheet, trying Port Detail fallback")
            service_instances = extract_service_instances_from_port_detail(df_atnd)
        
        print(f"DEBUG: Total service instances found for {len(service_instances)} ports")
        for port, vlans in service_instances.items():
            print(f"  Port 1/{port}: VLANs {sorted(vlans)}")
        
    except Exception as e:
        print(f"Error extrayendo service instances: {e}")
        import traceback
        traceback.print_exc()
    
    return service_instances


def extract_service_instances_from_port_detail(df_atnd):
    """
    Fallback: Extrae service instances desde Port Detail usando columna MTU.
    """
    service_instances = {}
    
    try:
        if 'Port Detail' not in df_atnd:
            return service_instances
        
        print("DEBUG: Extracting service instances from Port Detail")
        df_port = df_atnd['Port Detail']
        df_port_str = df_port.astype(str)
        
        port_col = None
        mtu_col = None
        
        for idx, row in df_port_str.iterrows():
            for col_idx, cell in enumerate(row):
                cell_lower = str(cell).lower()
                if ('router port' in cell_lower or cell_lower.strip() == 'port') and not port_col:
                    port_col = col_idx
                if 'mtu' in cell_lower and not mtu_col:
                    mtu_col = col_idx
            
            if port_col is not None and mtu_col is not None:
                print(f"DEBUG: Found Port column at {port_col}, MTU column at {mtu_col}")
                # Extraer datos
                for data_idx in range(idx + 1, len(df_port)):
                    data_row = df_port.iloc[data_idx]
                    port_val = str(data_row.iloc[port_col]).strip()
                    mtu_val = str(data_row.iloc[mtu_col]).strip()
                    
                    if '/' in port_val and mtu_val.isdigit():
                        port_num = port_val.split('/')[-1]
                        vlan = int(mtu_val)
                        
                        if 70 <= vlan <= 9999:
                            if port_num not in service_instances:
                                service_instances[port_num] = []
                            if vlan not in service_instances[port_num]:
                                service_instances[port_num].append(vlan)
                                print(f"DEBUG: Port Detail - Added VLAN {vlan} to port 1/{port_num}")
                break
    
    except Exception as e:
        print(f"Error in Port Detail fallback: {e}")
    
    return service_instances



def extract_link_group_info(df_atnd):
    """
    Extrae información del link-group desde Port Detail.
    
    Retorna diccionario:
    {
        'name': 'WAN_10G_BI919',
        'description': 'TO_ACSR-950D-A1-LAL-ESQ-CORONEL-BI740',
        'qos_policy': 'R6K_1GE'
    }
    """
    link_group_info = None
    
    try:
        if 'Port Detail' not in df_atnd:
            return None
        
        df = df_atnd['Port Detail']
        df_str = df.astype(str)
        
        # Buscar "link-group" en toda la hoja
        for idx, row in df_str.iterrows():
            for col_idx, cell in enumerate(row):
                cell_str = str(cell).strip()
                
                if 'link-group' in cell_str.lower():
                    # Extraer nombre del link-group
                    # Formato: "link-group WAN_10G_BI919"
                    parts = cell_str.split()
                    if len(parts) >= 2:
                        lg_name = parts[-1]  # Último token es el nombre
                        
                        # Priorizar descripciones que empiecen con "TO"
                        description = ""
                        candidates = []
                        for next_col in range(col_idx + 1, min(col_idx + 15, len(row))):
                            desc_val = str(row.iloc[next_col]).strip()
                            if desc_val and 'nan' not in desc_val.lower() and len(desc_val) > 3:
                                candidates.append(desc_val)
                                if desc_val.upper().startswith('TO') or desc_val.upper().startswith('TO_'):
                                    description = desc_val
                                    break
                        
                        # Si no encontramos una con "TO", usar la primera candidata larga
                        if not description and candidates:
                            # Preferir la que tenga guiones o sea más larga
                            best_candidate = max(candidates, key=len)
                            if len(best_candidate) > 10:
                                description = best_candidate
                            else:
                                description = candidates[0]

                        # Determinar QoS policy (generalmente R6K_1GE para link-groups)
                        qos_policy = 'R6K_1GE'
                        if '10' in lg_name.upper() or '10GE' in lg_name.upper():
                            qos_policy = 'R6K_10GE'
                        
                        link_group_info = {
                            'name': lg_name,
                            'description': description if description else f"Link Group {lg_name}",
                            'qos_policy': qos_policy
                        }
                        
                        print(f"DEBUG: Found link-group '{lg_name}' with description '{description}'")
                        break
            
            if link_group_info:
                break
    
    except Exception as e:
        print(f"Error extracting link-group info: {e}")
    
    return link_group_info


def extract_link_group_vlans(df_atnd, lg_name):
    """
    Extrae las VLANs asociadas al Link Group desde Layer 2 ALL CLIENT.
    Busca la fila con el nombre del Link Group y captura las VLANs siguientes.
    """
    vlans = set()
    
    try:
        # Buscar en las hojas posibles - Layer 2 Data es la más común
        sheet_name = None
        for name in ['Layer 2 ALL CLIENT', 'Layer 2 Data', 'Layer 2 MASTER VLAN']:
            if name in df_atnd:
                sheet_name = name
                print(f"DEBUG: Link Group VLAN search using sheet: {sheet_name}")
                break
        
        if not sheet_name:
            return vlans
            
        df = df_atnd[sheet_name]
        df_str = df.astype(str)
        
        # Buscar la columna que contiene el nombre del Link Group
        target_row_idx = None
        lg_col_idx = None
        
        # Terminos de búsqueda más flexibles
        search_terms = [lg_name.lower(), f"lg {lg_name}".lower()]
        # Agregar búsqueda por partes del nombre (ej: BI919) para ser más robusto
        if '_' in lg_name:
            search_terms.append(lg_name.split('_')[-1].lower())
            
        print(f"DEBUG: Search terms for Link Group: {search_terms}")
            
        for idx, row in df_str.iterrows():
            if target_row_idx is not None:
                break
                
            for col_idx, cell in enumerate(row):
                cell_str = str(cell).lower().strip()
                # Verificar si alguna celda contiene parte del nombre del Link Group
                # Y también contiene "lg" o "link" para evitar falsos positivos
                if ('lg' in cell_str or 'link' in cell_str) and any(term in cell_str for term in search_terms):
                    target_row_idx = idx
                    lg_col_idx = col_idx
                    print(f"DEBUG: Found Link Group row at {idx}, col {col_idx}: {cell_str}")
                    break
        
        # Si no lo encontramos así, buscar solo el nombre exacto
        if target_row_idx is None:
             for idx, row in df_str.iterrows():
                if target_row_idx is not None:
                    break
                for col_idx, cell in enumerate(row):
                    cell_str = str(cell).lower().strip()
                    if lg_name.lower() in cell_str:
                        target_row_idx = idx
                        lg_col_idx = col_idx
                        print(f"DEBUG: Found Link Group row (exact match) at {idx}, col {col_idx}: {cell_str}")
                        break

        if target_row_idx is not None:
            # Recorrer filas hacia abajo desde la fila encontrada
            for i in range(target_row_idx, len(df)):
                row = df.iloc[i]
                
                # Verificar si empezamos un nuevo bloque (si la celda del LG cambia de contenido drásticamente)
                # Pero cuidado, a veces las celdas de abajo están vacías (merged) o repiten info
                
                # Buscar números (VLANs) en TODO el ancho de la fila (o cerca)
                # Generalmente las VLANs están a la derecha del nombre del puerto/LG
                start_col = lg_col_idx + 1
                end_col = min(lg_col_idx + 10, len(row))
                
                for col in range(start_col, end_col):
                    val = str(row.iloc[col]).strip()
                    if val.isdigit():
                        vlan = int(val)
                        if 1 <= vlan <= 4096:
                            vlans.add(vlan)
        
        if vlans:
            print(f"DEBUG: Extracted {len(vlans)} VLANs for Link Group: {sorted(list(vlans))}")
        else:
            print("DEBUG: No VLANs found for Link Group in Layer 2 sheet")

    except Exception as e:
        print(f"Error extracting LG VLANs: {e}")
    
    return vlans


def generate_link_group_section(df_atnd, port_vlans):
    """
    Genera la sección de link-group con service instances.
    Prioriza las VLANs extraídas explícitamente para el LG, si no usa las de los puertos.
    """
    lines = []
    
    # Extraer info del link-group
    lg_info = extract_link_group_info(df_atnd)
    
    if not lg_info:
        print("WARNING: No se encontró link-group en Port Detail")
        return lines
        
    # Extraer VLANs específicas del Link Group (desde Layer 2)
    lg_vlans = extract_link_group_vlans(df_atnd, lg_info['name'])
    
    # Combinar con VLANs de puertos si es necesario, o usar solo LG si se encontraron
    if lg_vlans:
        print(f"DEBUG: Using explicit Link Group VLANs: {lg_vlans}")
        # Unimos por si acaso falta alguna de los puertos, pero las del LG deberían ser la fuente de verdad
        final_vlans = lg_vlans.union(port_vlans)
    else:
        print("DEBUG: Using aggregated Port VLANs for Link Group")
        final_vlans = port_vlans
    
    # Configuración del link-group
    lines.append("!")
    lines.append(f"link-group {lg_info['name']}")
    lines.append(f" description {lg_info['description']}")
    lines.append(" no shutdown")
    lines.append(" encapsulation dot1q")
    lines.append(" qos pwfq scheduling physical-port")
    lines.append(" maximum-links 1")
    lines.append(f" qos policy queuing {lg_info['qos_policy']}")
    
    # Service instances - agregar todas las VLANs únicas ordenadas
    for vlan in sorted(final_vlans):
        lines.append(f" service-instance {vlan}")
        lines.append("  match")
        lines.append(f"   dot1q {vlan}")
        lines.append("  profile 8021p-on-useip")
    
    lines.append("!")
    
    return lines


def generate_port_configuration(port_info):
    """
    Genera las líneas de configuración para un puerto específico.
    """
    lines = []
    
    port = port_info['port']
    speed = port_info['speed']
    description = port_info['description']
    port_type = port_info['type']
    qos_policy = port_info['qos_policy']
    service_instances = port_info.get('service_instances', [])
    is_tdd = port_info.get('is_tdd', False)
    vlan_type = port_info.get('vlan_type', 'ALL_VLAN')
    
    # Header del puerto
    lines.append("!")
    lines.append(f"port ethernet {port} {speed}")
    lines.append(f"description {description}")
    
    # CASO ESPECIAL: FDD + MASTER_VLAN
    if port_type == 'FDD' and vlan_type == 'MASTER_VLAN':
        lines.append("no auto-negotiate")
        lines.append("synchronous-mode")
        lines.append("squelch ql-dnu quality-level ql-sec")
        lines.append("no shutdown")
        lines.append("encapsulation dot1q")
        lines.append(f"qos policy queuing {qos_policy}")
        
        # Service instances con estructura especial (QinQ push)
        for vlan in sorted(service_instances):
            lines.append(f"service-instance {vlan}")
            lines.append("match")
            lines.append("dot1q *")
            lines.append("vlan-rewrite")
            lines.append(f"ingress seq 1 push outer dot1q {vlan}")
            lines.append("egress seq 1 pop outer")
            lines.append("profile 8021p-on-useip")
            
        return lines

    # Configuración Standard
    if port_type == 'FDD':
        # FDD tiene synchronous-mode
        lines.append("synchronous-mode")
        lines.append(" squelch ql-dnu quality-level ql-sec")
    elif port_type == 'SAFE':
        # SAFE tiene no auto-negotiate
        lines.append("no auto-negotiate")
    
    # Configuración común
    lines.append("no shutdown")
    lines.append("encapsulation dot1q")
    lines.append(f"qos policy queuing {qos_policy}")
    
    # Service instances con indentación correcta
    if is_tdd:
        # TDD: service-instance usa un número, dot1q usa otro
        for si_num, dot1q_num in service_instances:
            lines.append(f"service-instance {si_num}")
            lines.append(" match")
            lines.append(f"  dot1q {dot1q_num}")
            lines.append(" profile 8021p-on-useip")
    else:
        # FDD y SAFE: service-instance y dot1q usan el mismo número
        for vlan in sorted(service_instances):
            lines.append(f"service-instance {vlan}")
            lines.append(" match")
            lines.append(f"  dot1q {vlan}")
            lines.append(" profile 8021p-on-useip")
    
    return lines


def generate_ports_section(df_atnd, vlan_type="ALL_VLAN"):
    """
    Genera la sección completa de puertos.
    """
    lines = []
    
    # Extraer puertos
    ports = extract_ports_from_port_detail(df_atnd, vlan_type)
    
    # Extraer service instances
    si_map = extract_service_instances(df_atnd, vlan_type)
    
    # Asignar service instances a cada puerto
    for port_info in ports:
        port_full = port_info['port']  # ej: "1/4"
        port_num = port_full.split('/')[-1] if '/' in port_full else port_full  # ej: "4"
        port_type = port_info['type']
        port_info['vlan_type'] = vlan_type
        
        # Intentar múltiples claves de búsqueda
        keys_to_try = [port_num, port_full, f"1/{port_num}"]
        
        found = False
        for key in keys_to_try:
            if key in si_map:
                raw_vlans = si_map[key]
                
                # Aplicar filtros según tipo de puerto
                if port_type == 'SAFE':
                    # SAFE: solo la VLAN más pequeña (generalmente 70)
                    port_info['service_instances'] = [min(raw_vlans)] if raw_vlans else []
                    print(f"DEBUG: Port {port_full} (SAFE) - Using only VLAN {min(raw_vlans)}")
                elif port_type == 'TDD':
                    # TDD: caso especial - service-instance usa primer VLAN, dot1q usa la siguiente
                    # Si solo hay una VLAN, usar VLAN y VLAN+1
                    if len(raw_vlans) == 1:
                        base_vlan = raw_vlans[0]
                        port_info['service_instances'] = [(base_vlan, base_vlan + 1)]  # Tupla especial
                    else:
                        # Si hay múltiples, usar las dos primeras
                        sorted_vlans = sorted(raw_vlans)
                        port_info['service_instances'] = [(sorted_vlans[0], sorted_vlans[1])]
                    port_info['is_tdd'] = True  # Flag para procesamiento especial
                    print(f"DEBUG: Port {port_full} (TDD) - service-instance {port_info['service_instances'][0][0]}, dot1q {port_info['service_instances'][0][1]}")
                else:
                    # FDD y otros: todas las VLANs
                    port_info['service_instances'] = raw_vlans
                    print(f"DEBUG: Port {port_full} matched with key '{key}', VLANs: {raw_vlans}")
                
                found = True
                break
        
        if not found:
            print(f"WARNING: No service instances found for port {port_full}")
    
    # Ordenar puertos por número
    def get_port_sort_key(p):
        try:
            parts = p['port'].split('/')
            return (int(parts[0]), int(parts[1]))
        except:
            return (99, 99)
    
    ports.sort(key=get_port_sort_key)
    
    # Recolectar todas las VLANs de todos los puertos para el link-group
    all_vlans = set()
    
    # Generar configuración de cada puerto
    for port_info in ports:
        port_lines = generate_port_configuration(port_info)
        lines.extend(port_lines)
        
        # Recolectar VLANs
        service_instances = port_info.get('service_instances', [])
        is_tdd = port_info.get('is_tdd', False)
        
        if is_tdd:
            # TDD: extraer VLANs de las tuplas
            for si_num, dot1q_num in service_instances:
                all_vlans.add(si_num)
                all_vlans.add(dot1q_num)
        else:
            # FDD y SAFE: VLANs directas
            for vlan in service_instances:
                all_vlans.add(vlan)
    
    # === GENERAR LINK-GROUP con todas las VLANs ===
    link_group_lines = generate_link_group_section(df_atnd, all_vlans)
    lines.extend(link_group_lines)
    
    # Línea final de separación
    lines.append("!")
    
    return lines


def extract_port_bvi_info(df_atnd):
    """
    Extrae información de la tabla 'Port BVI' desde Layer 2 ALL CLIENT.
    Retorna lista de diccionarios con la configuración de cada BVI.
    """
    bvi_list = []
    
    try:
        # Buscar en las hojas posibles
        # Nota: Data Reader estandariza a "Layer 2 Data" usualmente
        sheet_name = None
        for name in ['Layer 2 Data', 'Layer 2 ALL CLIENT', 'Layer 2 MASTER VLAN']:
            if name in df_atnd:
                sheet_name = name
                break
        
        if not sheet_name:
            print("ERROR: No se encontró hoja Layer 2 para Port BVI")
            return bvi_list
            
        df = df_atnd[sheet_name]
        df_str = df.astype(str)
        
        print(f"DEBUG: Analyzing sheet '{sheet_name}' for Port BVI. Shape: {df.shape}")
        
        # Estrategia: Buscar la celda que diga "Port BVI" (Titulo)
        # y luego buscar los headers debajo
        title_row_idx = None
        
        # 1. Buscar titulo "Port BVI"
        for idx, row in df_str.iterrows():
            row_str = " ".join([str(c) for c in row]).lower()
            if 'port bvi' in row_str:
                title_row_idx = idx
                print(f"DEBUG: Found 'Port BVI' title at row {idx}")
                # Imprimir la fila para ver qué hay
                print(f"DEBUG: Row content: {row.tolist()[:5]}...")
                break
        
        # Si no encontramos titulo, buscar headers directamente (Estrategia anterior mejorada)
        start_search_row = title_row_idx if title_row_idx is not None else 0
        
        header_row_idx = None
        cols_map = {}
        
        column_mappings = {
            'name': ['name', 'nombre'],
            'encapsulation': ['encapsulation', 'encap'],
            'pvc': ['pvc', 'dot1qpvc', 'vlan'],
            'bind_interface': ['bind interface', 'bind_interface', 'bind'],
            'context': ['context', 'vrf'],
            'bridge_name': ['bridge name', 'bridgename', 'bridge']
        }
        
        # Buscar headers en las siguientes 10 filas desde el titulo (o todo si no hay titulo)
        end_search_row = min(start_search_row + 20, len(df)) if title_row_idx is not None else len(df)
        
        for idx in range(start_search_row, end_search_row):
            row = df_str.iloc[idx]
            temp_map = {}
            
            # Debug: Mostrar filas cercanas al titulo para ver donde estan los headers
            if title_row_idx is not None and idx < title_row_idx + 5:
                print(f"DEBUG: Scanning row {idx} for headers: {row.tolist()[:5]}...")

            for col_idx, cell in enumerate(row):
                cell_str = str(cell).strip().lower()
                
                for field, variants in column_mappings.items():
                    if any(v in cell_str for v in variants):
                        if field not in temp_map:
                            temp_map[field] = col_idx
            
            # Criterio estricto: Necesitamos Name, PVC y (Bridge Name OR Bind Interface)
            if 'name' in temp_map and 'pvc' in temp_map and ('bridge_name' in temp_map or 'bind_interface' in temp_map):
                header_row_idx = idx
                cols_map = temp_map
                print(f"DEBUG: Found HEADERS at row {idx}. Map: {cols_map}")
                break
        
        if header_row_idx is not None:
            # Iterar datos
            for i in range(header_row_idx + 1, len(df)):
                row = df.iloc[i]
                
                # Validar columna Name
                if 'name' in cols_map:
                    name_val = str(row.iloc[cols_map['name']]).strip()
                    bridge_val = str(row.iloc[cols_map.get('bridge_name', -1)] if 'bridge_name' in cols_map else "").strip()
                    
                    # Criterio fin: Name vacio Y Bridge vacio (o headers repetidos)
                    if (not name_val or name_val.lower() == 'nan') and (not bridge_val or bridge_val.lower() == 'nan'):
                        continue # Skip empty rows
                    
                    # Si encontramos otro header o 'Port BVI' de nuevo, parar
                    if 'port bvi' in name_val.lower() or 'bridge' == name_val.lower():
                        print(f"DEBUG: Stopped extraction at row {i} due to new section header: {name_val}")
                        break

                    # Extraer
                    if name_val and name_val.lower() != 'nan' and name_val.lower() != 'name':
                        bvi_data = {
                            'name': name_val,
                            'encapsulation': 'dot1q',
                            'pvc': '',
                            'bind_interface': '',
                            'context': '',
                            'bridge_name': ''
                        }
                        
                        if 'encapsulation' in cols_map:
                            val = str(row.iloc[cols_map['encapsulation']]).strip()
                            if val and val.lower() != 'nan': bvi_data['encapsulation'] = val
                        
                        if 'pvc' in cols_map:
                            val = str(row.iloc[cols_map['pvc']]).strip()
                            if val.endswith('.0'): val = val[:-2]
                            if val and val.lower() != 'nan': bvi_data['pvc'] = val
                            
                        if 'bind_interface' in cols_map:
                            val = str(row.iloc[cols_map['bind_interface']]).strip()
                            if val and val.lower() != 'nan': bvi_data['bind_interface'] = val
                            
                        if 'context' in cols_map:
                            val = str(row.iloc[cols_map['context']]).strip()
                            if val and val.lower() != 'nan': bvi_data['context'] = val
                        
                        if 'bridge_name' in cols_map:
                            val = str(row.iloc[cols_map['bridge_name']]).strip()
                            if val and val.lower() != 'nan': bvi_data['bridge_name'] = val
                            
                        bvi_list.append(bvi_data)
        else:
            print("WARNING: Could not identify Port BVI header row after Title Search")
            # Imprimir columnas raw para debug
            print(f"DEBUG: Sheet columns: {df.columns.tolist()}")

    except Exception as e:
        print(f"Error extracting Port BVI info: {e}")
        import traceback
        traceback.print_exc()
        
    return bvi_list


def generate_port_bvi_section(df_atnd):
    """
    Genera la sección de Port Ethernet Management y Port BVI.
    """
    lines = []
    
    # === PARTE ESTÁTICA ===
    lines.append("port ethernet management")
    lines.append(" shutdown")
    lines.append(" bind interface management local")
    lines.append("!")
    
    # === PARTE DINÁMICA (Port BVI) ===
    bvis = extract_port_bvi_info(df_atnd)
    
    if not bvis:
        lines.append("! WARNING: No se encontraron datos para Port BVI. Revise logs de debug.")
    
    for bvi in bvis:
        lines.append(f"port bvi {bvi['name']}")
        lines.append(" no shutdown")
        if bvi['bridge_name']:
            lines.append(f" bridge name {bvi['bridge_name']}")
        
        lines.append(f" encapsulation {bvi['encapsulation']}")
        
        if bvi['pvc']:
            lines.append(f" dot1q pvc {bvi['pvc']}")
            
        if bvi['bind_interface']:
            context = bvi['context']
            if context and context.lower() != 'nan':
                 if context != bvi['bind_interface']:
                    lines.append(f" bind interface {bvi['bind_interface']} {context}")
                 else:
                    lines.append(f" bind interface {bvi['bind_interface']} {context}")
            else:
                lines.append(f" bind interface {bvi['bind_interface']}")
        
        lines.append("!")
        lines.append("!")
    
    return lines


def extract_system_info(df_atnd):
    """
    Extrae información del sistema desde 'RAN IP Addressing'.
    Retorna diccionario con router_name, site_name, site_id.
    """
    info = {
        'router_name': 'ROUTER_NAME_NOT_FOUND',
        'site_name': 'SITE_NAME_NOT_FOUND',
        'site_id': 'SITE_ID_NOT_FOUND'
    }
    
    try:
        if 'RAN IP Addressing' not in df_atnd:
            print("ERROR: 'RAN IP Addressing' sheet not found in df_atnd keys:", df_atnd.keys())
            return info
            
        df = df_atnd['RAN IP Addressing']
        df_str = df.astype(str)
        
        print(f"DEBUG: 'RAN IP Addressing' shape: {df.shape}")
        print(f"DEBUG: First 10 rows of 'RAN IP Addressing':")
        for i in range(min(10, len(df))):
            print(f"DEBUG Row {i}: {df_str.iloc[i].tolist()}")
        
        # Buscar headers: SITE NAME, SITE ID, ROUTER NAME
        header_row_idx = None
        cols_map = {}
        
        keywords = {
            'SITE NAME': 'site_name',
            'SITE ID': 'site_id',
            'ROUTER NAME': 'router_name'
        }
        
        for idx, row in df_str.iterrows():
            row_map = {}
            for col_idx, cell in enumerate(row):
                cell_str = str(cell).strip().upper()
                # Check weak match
                for key in keywords:
                    if key in cell_str:
                         row_map[keywords[key]] = col_idx
            
            # Si encontramos al menos 2 de las 3 columnas importantes
            if len(row_map) >= 2:
                header_row_idx = idx
                cols_map = row_map
                print(f"DEBUG: Found RAN IP headers at row {idx}: {cols_map}")
                break
        
        if header_row_idx is not None:
            # Buscar la fila de datos (puede no ser inmeditamente la siguiente por celdas vacias/ocultas)
            # Escanear hasta 5 filas abajo
            for offset in range(1, 6):
                data_row_idx = header_row_idx + offset
                if data_row_idx >= len(df):
                    break
                    
                row = df.iloc[data_row_idx]
                temp_info = {}
                found_valid_data = False
                
                for field, col_idx in cols_map.items():
                    val = str(row.iloc[col_idx]).strip()
                    if val and val.lower() != 'nan':
                        temp_info[field] = val
                        found_valid_data = True
                
                # Si encontramos al menos un dato válido (ej: SITE ID), asumimos que es la fila correcta
                if found_valid_data:
                    info.update(temp_info)
                    print(f"DEBUG: Data found at row {data_row_idx}")
                    print(f"DEBUG: Extracted System Info: {info}")
                    break
                else:
                    print(f"DEBUG: Skipping empty row {data_row_idx}")
                
    except Exception as e:
        print(f"Error extracting System Info: {e}")
        import traceback
        traceback.print_exc()
        
    return info


def generate_system_basic_section(df_atnd):
    """
    Genera la sección básica de sistema (iag, ipv6, hostname, dnprefix, tcp).
    """
    lines = []
    info = extract_system_info(df_atnd)
    
    lines.append("iag pod level 2")
    lines.append("!")
    lines.append("ipv6 path-mtu-discovery discovery-interval 600")
    lines.append("!")
    lines.append("system contact Entel Chile")
    lines.append(f"system hostname {info['router_name']}")
    lines.append("system location Entel Chile")
    lines.append(f"system description Site Router {info['site_name']}")
    lines.append(f"system dnprefix SubNetwork=ONRM_ROOT_MO_R,SubNetwork=Router,MeContext=Router_{info['site_id']}")
    lines.append("!")
    lines.append("tcp Path-mtu-discovery")
    lines.append("timeout session idle 5")
    lines.append("!")
    lines.append("!")
    
    return lines


    return lines


    return lines


def extract_network_management_info(df_atnd):
    """
    Extrae información de 'Router Network Management'.
    Recupera:
    - Trap Server (IP, version, community, view)
    - NTP Servers
    """
    info = {
        'enm_ip': '0.0.0.0',
        'enm_version': '2c',
        'enm_security': 'public', 
        'enm_view': 'ENM-View',
        'snmp_views': []
    }
    
    try:
        sheet_name = 'Router Network Management'
        if sheet_name not in df_atnd:
            return info
            
        df = df_atnd[sheet_name]
        df_str = df.astype(str)
        
        # === 1. BUSCAR TRAP SERVER (ENM_public_v2c) ===
        # Header suele ser: VRF | IP address | Version | security-name | view
        # O buscamos directamente por la celda "ENM_public_v2c" y mapeamos por posición relativa
        # En la imagen: ENM_public_v2c está en la columna que dice "VRF" o "Trap server" (header arriba)
        
        trap_found = False
        for idx, row in df_str.iterrows():
            row_list = [str(c).strip() for c in row]
            
            # Buscar la fila de datos que contiene "ENM_public_v2c"
            # Asumiremos la estructura visual: 
            # Col 0: Name, Col 1: IP, Col 2: Version, Col 3: SecName, Col 4: View (aprox)
            # Pero mejor buscamos la celda y miramos a la derecha
            
            if 'ENM_public_v2c' in row_list:
                col_idx = row_list.index('ENM_public_v2c')
                # La IP suele estar a la derecha
                # Buscamos en las siguientes 5 columnas algo que parezca IP
                for offset in range(1, 6):
                    if col_idx + offset < len(row_list):
                        val = row_list[col_idx + offset]
                        # Check IP format
                        if '.' in val and len(val.split('.')) == 4:
                            info['enm_ip'] = val
                            # Asumimos orden relativo según imagen: IP, Version, SecName, View
                            # Version esta justo despues de IP?
                            if col_idx + offset + 1 < len(row_list):
                                info['enm_version'] = row_list[col_idx + offset + 1]
                            if col_idx + offset + 2 < len(row_list):
                                info['enm_security'] = row_list[col_idx + offset + 2]
                            if col_idx + offset + 3 < len(row_list):
                                info['enm_view'] = row_list[col_idx + offset + 3]
                            
                            trap_found = True
                            print(f"DEBUG: Found Trap Server info: {info}")
                            break
            if trap_found: break
            
        # === 2. BUSCAR SNMP VIEWS ===
        # Header "snmp view"
        
        view_col_idx = None
        header_row = None
        
        for idx, row in df_str.iterrows():
            row_lower = [str(c).lower().strip() for c in row]
            for c_idx, val in enumerate(row_lower):
                if 'snmp view' in val:
                    view_col_idx = c_idx
                    header_row = idx
                    break
            if header_row is not None: break
            
        if header_row is not None:
            for i in range(header_row + 1, min(header_row + 10, len(df))):
                val = str(df_str.iloc[i, view_col_idx]).strip()
                # A veces esta en la misma celda o a la derecha?
                # Si el valor dice 'snmp view', buscamos a la derecha
                if val.lower() == 'snmp view':
                    if view_col_idx + 1 < df.shape[1]:
                         val_right = str(df_str.iloc[i, view_col_idx + 1]).strip()
                         if val_right and val_right.lower() != 'nan':
                             info['snmp_views'].append(val_right)
                else:
                    if val and val.lower() != 'nan' and 'included' in val.lower():
                        info['snmp_views'].append(val)
        
        print(f"DEBUG: Extracted SNMP Views: {info['snmp_views']}")

    except Exception as e:
        print(f"Error extracting Network Management info: {e}")
        
    return info


def generate_network_management_section(df_atnd):
    """
    Genera la sección 'management context OSS' y configuración SNMP.
    """
    lines = []
    info = extract_network_management_info(df_atnd)
    
    # === SNMP SECTION ===
    lines.append("management context OSS")
    lines.append(" conf")
    lines.append(" netconf tls server admin-state enable")
    lines.append(" default tls cipher-filter")
    lines.append(" snmp server")
    lines.append(" traps ifmib encaps")
    lines.append(" traps ifmib ip")
    
    # === DYNAMIC SNMP VIEWS ===
    if info['snmp_views']:
        for view_def in info['snmp_views']:
            lines.append(f" snmp view {view_def}")
    else:
        # Fallback a estáticos típicos
        lines.append(" snmp view all internet included")
        lines.append(" snmp view ENM-View mib_2 included")
        
    lines.append(" snmp view ENM-View snmpModules included")
    lines.append(" snmp view ENM-View ericssonAlarmMIB included")
    lines.append(" snmp view Inet-View internet included")
    lines.append(" snmp view restricted system included")
    lines.append(" snmp view restricted snmp included")
    lines.append(" snmp view restricted snmpEngine included")
    lines.append(" snmp view restricted snmpMPDStats included")
    lines.append(" snmp view restricted usmStats included")
    lines.append(" snmp community EISUP context SAFE")
    lines.append(" snmp community public view Inet-View")
    lines.append(" snmp group group1 security-model usm noauth all-contexts read Inet-View write Inet-View notify Inet-View")
    lines.append(" snmp group group1 security-model usm priv all-contexts read Inet-View write Inet-View notify Inet-View")
    
    # Dynamic Target line
    t_ip = info['enm_ip']
    t_sec = info['enm_security']
    t_ver = info['enm_version']
    t_view = info['enm_view']
    
    # Limpieza básica de strings 'nan'
    if t_sec == 'nan': t_sec = 'public'
    if t_ver == 'nan': t_ver = '2c'
    if t_view == 'nan': t_view = 'ENM-View'
    
    lines.append(f" snmp target ENM_public_v2c {t_ip} security-name {t_sec} version {t_ver} view {t_view}")
    lines.append("!")
    lines.append("!")
    
    return lines


    return lines


def extract_bridge_domains(df_atnd):
    """
    Extrae la configuración de Bridge Domains desde 'Layer 2 ALL CLIENT' (o Layer 2 Data).
    Busca bloques que comienzan con "Bridge" y su nombre, seguidos de una lista de puertos/LGs.
    """
    bridges = []
    
    try:
        # Determinar hoja correcta. 
        # Si vlan_type="ALL_VLAN", suele ser 'Layer 2 Data' mapeada o 'Layer 2 ALL CLIENT'
        # El df_atnd ya trae las hojas con nombres clave.
        target_sheet = None
        if 'Layer 2 ALL CLIENT' in df_atnd:
            target_sheet = df_atnd['Layer 2 ALL CLIENT']
        elif 'Layer 2 Data' in df_atnd:
            target_sheet = df_atnd['Layer 2 Data']
            
        if target_sheet is None or target_sheet.empty:
            print("WARNING: No Layer 2 sheet found for Bridge Domains")
            return bridges
            
        df = target_sheet.astype(str)
        
        # Estrategia de barrido:
        # Buscar "Bridge" en alguna columna (usualmente la primera o segunda).
        # Una vez encontrado, el nombre está en la misma fila (columna siguiente o más allá).
        # Debajo viene header "Port" | "Service-instance"
        # Luego N filas de datos.
        
        current_bridge = None
        capturing = False
        port_col_idx = None
        si_col_idx = None
        
        # Iteramos filas
        for idx, row in df.iterrows():
            row_list = [str(c).strip() for c in row]
            row_lower = [c.lower() for c in row_list]
            
            # 1. Detectar Comienzo de Bloque Bridge
            # Buscamos celda exacta "Bridge" o "Bridge:"
            if 'bridge' in row_lower:
                # Verificar si es el header del título del bridge
                # En la imagen: [Bridge] ... [NOMBRE]
                try:
                    # Buscamos el índice donde dice 'bridge'
                    indices = [i for i, x in enumerate(row_lower) if x == 'bridge']
                    if indices:
                        # Asumimos que es un titulo de tabla nueva
                        b_idx = indices[0]
                        
                        # Buscar nombre del bridge en esa fila (celda no vacía y no 'bridge')
                        # A veces esta justo al lado, o varias celdas a la derecha
                        bridge_name = None
                        for k in range(b_idx + 1, len(row_list)):
                            val = row_list[k]
                            if val and val.lower() != 'nan':
                                bridge_name = val
                                break
                        
                        if bridge_name:
                            # Guardamos el bridge anterior si existía
                            if current_bridge:
                                bridges.append(current_bridge)
                            
                            current_bridge = {
                                'name': bridge_name,
                                'items': []
                            }
                            # Reseteamos columnas para este nuevo bloque
                            capturing = False # Esperamos a encontrar header "Port"
                            print(f"DEBUG: Found Bridge Header: {bridge_name} at row {idx}")
                            continue
                except:
                    pass

            # 2. Detectar Headers de Columnas (Port, Service-instance)
            # Solo si tenemos un current_bridge detectado
            if current_bridge and not capturing:
                if 'port' in row_lower and ('service-instance' in row_lower or 'service instance' in row_lower):
                    # Identificar columnas
                    for i, val in enumerate(row_lower):
                        if 'port' == val: port_col_idx = i
                        elif 'service-instance' in val or 'service instance' in val: si_col_idx = i
                    
                    if port_col_idx is not None:
                        capturing = True
                        print(f"DEBUG: Found Bridge Columns at row {idx}: Port={port_col_idx}, SI={si_col_idx}")
                        continue

            # 3. Capturar Datos
            if current_bridge and capturing:
                # Criterio de parada: Fila vacía en Port, o palabra clave 'Bridge' (ya manejado arriba en paso 1)
                
                # Chequear si encontramos un nuevo 'Bridge' en esta fila -> Se maneja en el paso 1 del siguiente loop,
                # PERO el paso 1 usa 'continue', así que saltaría aquí.
                # Sin embargo, necesitamos cerrar el bridge actual si aparece uno nuevo.
                # La lógica del paso 1 ya hace append(current_bridge) si encuentra uno nuevo.
                # El riesgo es procesar la fila de título como dato.
                # Agregamos check rápido:
                if 'bridge' in row_lower:
                    continue 

                port_val = row_list[port_col_idx] if port_col_idx < len(row_list) else ''
                si_val = row_list[si_col_idx] if si_col_idx is not None and si_col_idx < len(row_list) else ''
                
                # Validar contenido
                if not port_val or port_val.lower() == 'nan':
                    continue
                
                # Ignorar headers repetidos por error
                if port_val.lower() == 'port': continue
                
                # Procesar Service Instance: manejar múltiples valores (newlines, x000D)
                raw_si = str(si_val).replace('_x000D_', '\n')
                si_parts = [p.strip() for p in raw_si.split('\n')]
                
                for part in si_parts:
                    if not part: continue # Skip empty parts
                    if part.lower() == 'nan': continue
                    
                    final_si = part
                    if final_si.endswith('.0'): final_si = final_si[:-2]
                    
                    # Regla estricta: Si no hay SI, no se agrega el puerto/LG
                    if final_si:
                        item = {
                            'interface': port_val,
                            'service_instance': final_si
                        }
                        current_bridge['items'].append(item)

        # Al final, agregar el último bridge
        if current_bridge:
            bridges.append(current_bridge)
            
    except Exception as e:
        print(f"Error extracting Bridge Domains: {e}")
        import traceback
        traceback.print_exc()
        
    return bridges


def generate_bridge_domains_section(df_atnd):
    """
    Genera la configuración de Bridges.
    """
    lines = []
    bridges = extract_bridge_domains(df_atnd)
    
    for br in bridges:
        if not br['items']: 
             # Si no hay items (porque se filtraron todos por falta de SI),
             # el usuario quiere que aparezca el bridge igual?
             # User example: "bridge 5G_N1_N3" (sin ports)
             # Entonces seguimos.
             pass
        
        lines.append(f"bridge {br['name']}")
        for item in br['items']:
            raw_int = item['interface']
            si = item['service_instance']
            
            line_str = " " 
            
            if raw_int.lower().startswith('lg') or raw_int.lower().startswith('link-group'):
                line_str += raw_int
            else:
                if '/' in raw_int or raw_int[0].isdigit():
                    line_str += f"port {raw_int}"
                else:
                    line_str += raw_int
            
            if si:
                line_str += f" service-instance {si}"
                
            lines.append(line_str)
        lines.append("!")
        
    return lines


    return lines


def generate_synchronization_section(df_atnd):
    """
    Genera la sección de Sincronización desde la hoja 'Synchronization'.
    Extrae comandos de la Columna A o donde se detecten palabras clave,
    filtrando encabezados conocidos y evitando falsos positivos.
    """
    lines = []
    
    if 'Synchronization' not in df_atnd:
        print("WARNING: Hoja 'Synchronization' no encontrada en df_atnd.")
        return lines
        
    df = df_atnd['Synchronization']
    df_str = df.astype(str)
    
    # 1. Detectar columna de comandos
    # Se añaden palabras clave que aparecen en escenarios Master VLAN (ptp-clock, input-source)
    cmd_col_idx = 0
    found_col = False
    keywords_search = [
        "cable-delay", 
        "tod input", 
        "protocol ericsson", 
        "ptp-clock", 
        "acquiring-state", 
        "input-source",
        "ptp-port"
    ]
    
    for c_idx in range(len(df.columns)):
        # Pasamos a minúsculas y manejamos posibles NaN
        col_values = df_str.iloc[:, c_idx].str.lower().fillna('')
        for kw in keywords_search:
            if col_values.str.contains(kw, regex=False).any():
                cmd_col_idx = c_idx
                found_col = True
                print(f"DEBUG: Found Sync Command Column at index {c_idx} (keyword: {kw})")
                break
        if found_col: break
        
    print(f"DEBUG: Using column index {cmd_col_idx} for Sync commands")

    lines.append("!")
    lines.append("!conf")
    lines.append("!synchronization")
    lines.append("!no ptp-clock g8275-1 t-bc")
    lines.append("!")
    
    # Headers/Títulos a ignorar (se eliminó "synchronization" de aquí para evitar conflictos)
    blacklist = [
        "router synchronization",
        "global synchronization",
        "1 pps + tod",
        "ptp bc oc port",
        "radio equipment clock",
        "sync ports",
        "synce ports",
        "port ethernet",         # Comandos SyncE que se suelen omitir
        "gps delay",
        "comments",
        "table",
        "cable or unit",
        "product number",
        "delay",
        "minimum bending",
        "outdoor classified",
        "baseband synchronization",
        "source configuration",
        "port towards",
        "source selection",
        "clocktype",
        "boundary ordinary clock"
    ]
    
    for idx, row in df_str.iterrows():
        cell = str(row.iloc[cmd_col_idx]).strip()
        cell = cell.replace('_x000D_', '').strip() # Limpiar basura excel
        
        # Filtros básicos: celdas vacías o nulas
        if not cell or cell.lower() == 'nan' or cell == 'None':
            continue
            
        cell_lower = cell.lower()
        
        # Lógica de Blacklist mejorada
        is_header = False
        # Si la celda es exactamente "synchronization", es el primer comando de configuración.
        # NO debemos marcarlo como header aunque la palabra "synchronization" esté en la blacklist.
        if cell_lower == "synchronization":
            is_header = False
        else:
            for bl in blacklist:
                if bl in cell_lower:
                    is_header = True
                    break
        
        if is_header:
            continue

        # Ignorar celdas que son solo números cortos (posibles índices de filas en Excel)
        if cell.isdigit() and len(cell) < 3:
            continue
            
        # Filtro de seguridad adicional para comandos específicos de SyncE si el usuario pidió omitirlos
        # (Ajustar según necesidad)
        if any(x in cell_lower for x in ["synchronous-mode", "squelch"]):
            continue

        lines.append(cell)

    # Cierre de la sección
    lines.append("!")
    lines.append("commit")
    lines.append("end")
    lines.append("save config")
    lines.append("y")
    
    return lines
    
def generar_script_advanced(nemonico, output_dir, df_atnd, vlan_type="ALL_VLAN"):
    """
    Genera el archivo SCRIPT_ADVANCED_{TIPO}_{NEMONICO}.txt.
    
    Args:
        nemonico: Némónico del router
        output_dir: Directorio de salida
        df_atnd: Diccionario con todas las hojas del ATND
        vlan_type: Tipo explícito - "MASTER_VLAN" o "ALL_VLAN"
    """
    # El tipo viene del parámetro explícito
    vlan_type_display = "MASTER" if vlan_type == "MASTER_VLAN" else "ALL"
    
    # Definir Nombre de Archivo
    filename = f"SCRIPT_ADVANCED_{vlan_type_display}_{nemonico}.txt"
    filepath = os.path.join(output_dir, filename)
    
    from datetime import datetime
    now = datetime.now()
    fecha_str = now.strftime("%d-%m-%Y")
    hora_str = now.strftime("%H:%M:%S")

    # Generar Contenido
    mml_output = []
    mml_output.append("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    mml_output.append("!!")
    mml_output.append(f"!! ARCHIVO     : {filename}")
    mml_output.append("!! AUTOR       : Piero Ledesma")
    mml_output.append(f"!! FECHA       : {fecha_str}")
    mml_output.append(f"!! HORA        : {hora_str}")
    mml_output.append(f"!! NEMONICO    : {nemonico}!!")
    mml_output.append("!! TIPO VLAN   : All VLAN" if vlan_type == "ALL_VLAN" else "!! TIPO VLAN   : Master VLAN")
    mml_output.append("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    mml_output.append("")
    mml_output.append("conf")
    mml_output.append("!")
    mml_output.append("")
    mml_output.append("!")
    mml_output.append("!")
    
    # === SECCIÓN 1: L2 ACCESS-LIST FILTRO-CORE-ERS (ESTÁTICA) ===
    mml_output.append("l2 access-list FILTRO-CORE-ERS")
    mml_output.append("description FILTRO-CORE-ERS")
    mml_output.append("seq 10 deny any 01:80:c2:00:00:00 mask ff:ff:ff:ff:ff:f0")
    mml_output.append("seq 20 deny any 01:80:c2:00:00:10 mask ff:ff:ff:ff:ff:f0")
    mml_output.append("seq 30 deny any 01:80:c2:00:00:20 mask ff:ff:ff:ff:ff:f0")
    mml_output.append("seq 40 deny any 01:80:c2:00:00:10 mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 50 deny any 01:00:0c:00:00:00 mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 60 deny any 01:00:0c:cc:cc:cc mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 70 deny any 01:00:0c:cc:cc:cd mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 80 deny any 01:00:0c:cd:cd:ce mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 90 deny any 01:00:0c:cd:cd:d0 mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 110 deny any 00:0f:e2:07:82:17 mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 120 deny any 00:0f:e2:07:82:97 mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 130 deny any 00:0f:e2:07:82:57 mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 150 deny any 00:0f:e2:07:82:d7 mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 160 deny any 00:0f:e2:07:82:d8 mask ff:ff:ff:ff:ff:f8")
    mml_output.append("seq 170 deny any 00:0f:e2:07:82:e0 mask ff:ff:ff:ff:ff:f0")
    mml_output.append("seq 180 deny any 00:0f:e2:07:82:f0 mask ff:ff:ff:ff:ff:f0")
    mml_output.append("seq 190 deny any 00:0f:e2:07:83:00 mask ff:ff:ff:ff:ff:f0")
    mml_output.append("seq 200 deny any 00:0f:e2:07:83:10 mask ff:ff:ff:ff:ff:f8")
    mml_output.append("seq 210 deny any 01:0f:e2:00:00:04 mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 220 deny any 20:0b:c7:94:0b:f5 mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 250 deny any 01:00:0c:dd:dd:dd mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 300 deny any 20:0b:c7:94:0b:f3 mask ff:ff:ff:ff:ff:ff")
    mml_output.append("!")
    


    # === SECCIÓN 2: L2 ACCESS-LIST MAC-SAFE (ESTÁTICA) ===
    mml_output.append("l2 access-list MAC-SAFE")
    mml_output.append("description MAC-SAFE")
    mml_output.append("seq 10 deny any 01:80:c2:00:00:00 mask ff:ff:ff:ff:ff:f0")
    mml_output.append("seq 20 deny any 01:80:c2:00:00:10 mask ff:ff:ff:ff:ff:f0")
    mml_output.append("seq 30 deny any 01:80:c2:00:00:20 mask ff:ff:ff:ff:ff:f0")
    mml_output.append("seq 40 deny any 01:80:c2:00:00:10 mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 50 deny any 01:00:0c:00:00:00 mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 60 deny any 01:00:0c:cc:cc:cc mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 70 deny any 01:00:0c:cc:cc:cd mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 80 deny any 01:00:0c:cd:cd:ce mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 90 deny any 01:00:0c:cd:cd:d0 mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 110 deny any 00:0f:e2:07:82:17 mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 120 deny any 00:0f:e2:07:82:97 mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 130 deny any 00:0f:e2:07:82:57 mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 150 deny any 00:0f:e2:07:82:d7 mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 160 deny any 00:0f:e2:07:82:d8 mask ff:ff:ff:ff:ff:f8")
    mml_output.append("seq 170 deny any 00:0f:e2:07:82:e0 mask ff:ff:ff:ff:ff:f0")
    mml_output.append("seq 180 deny any 00:0f:e2:07:82:f0 mask ff:ff:ff:ff:ff:f0")
    mml_output.append("seq 190 deny any 00:0f:e2:07:83:00 mask ff:ff:ff:ff:ff:f0")
    mml_output.append("seq 200 deny any 00:0f:e2:07:83:10 mask ff:ff:ff:ff:ff:f8")
    mml_output.append("seq 210 deny any 01:0f:e2:00:00:04 mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 220 deny any 20:0b:c7:94:0b:f5 mask ff:ff:ff:ff:ff:ff")
    mml_output.append("seq 250 deny any 01:00:0c:dd:dd:dd mask ff:ff:ff:ff:ff:ff")
    mml_output.append("!")
    
    # === SECCIÓN 3: SERVICE MULTIPLE-CONTEXTS (ESTÁTICA) ===
    mml_output.append("service multiple-contexts")
    mml_output.append("!")
    
    # === SECCIÓN 4: QOS CLASS-MAP DSCP-TO-PD (DINÁMICA) ===
    mml_output.append("qos class-map dscp-to-pd ip in")
    
    # Extraer mapeos dinámicos desde QoS sheet
    dscp_mappings = extract_qos_dscp_to_pd(df_atnd)
    for ip_num, qos_val in dscp_mappings:
        mml_output.append(f"ip {ip_num} to qos {qos_val}")
    
    mml_output.append("!")
    
    # === SECCIÓN 5: QOS CLASS-MAP IP-PBIT-TO-PD ETHERNET (DINÁMICA) ===
    mml_output.append("qos class-map ip-pbit-to-pd ethernet in")
    mml_output.append("use-ip dscp-to-pd")
    
    # Extraer mapeos de ethernet
    ethernet_mappings = extract_ethernet_pbit_mappings(df_atnd)
    for eth_num, qos_val in ethernet_mappings:
        mml_output.append(f"ethernet {eth_num} to qos {qos_val}")
    
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("security profile admin-eal3-compliance")
    mml_output.append("lockout-duration 5")
    mml_output.append("failed-login-attempts 6")
    mml_output.append("global synchronization option 1")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("no release description")
    mml_output.append("!")
    mml_output.append("!release ID 2")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("alarm-port 1 input 1 active low")
    mml_output.append("alarm-port 1 input 1 admin-state disabled")
    mml_output.append("alarm-port 1 input 1 severity critical")
    mml_output.append("no alarm-port 1 input 1 description")
    mml_output.append("!")
    mml_output.append("!release ID 2")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("alarm-port 1 input 1 active low")
    mml_output.append("alarm-port 1 input 1 admin-state disabled")
    mml_output.append("alarm-port 1 input 1 severity critical")
    mml_output.append("no alarm-port 1 input 1 description")
    mml_output.append("alarm-port 1 input 2 active low")
    mml_output.append("alarm-port 1 input 2 admin-state disabled")
    mml_output.append("alarm-port 1 input 2 severity critical")
    mml_output.append("no alarm-port 1 input 2 description")
    mml_output.append("alarm-port 1 input 3 active low")
    mml_output.append("alarm-port 1 input 3 admin-state disabled")
    mml_output.append("alarm-port 1 input 3 severity critical")
    mml_output.append("no alarm-port 1 input 3 description")
    mml_output.append("!")
    mml_output.append("alarm-port 1 output 1 admin-state disabled")
    mml_output.append("no alarm-port 1 output 1 description")
    mml_output.append("!")
    
    # === SECCIÓN 6: CONTEXTS DINÁMICOS ===
    # Extraer contexts desde Router Layer 3 Configuration
    contexts = extract_contexts_from_l3_config(df_atnd)
    
    for context_data in contexts:
        # Generar sección para cada context
        context_lines = generate_context_section(context_data)
        mml_output.extend(context_lines)
    
    # End Context marker
    if contexts:
        mml_output.append("! ** End Context **")
        mml_output.append("!")
    
    # === SECCIÓN 7: QoS POLICIES (DOT1Q, QUEUE-MAP, R6K POLICIES) ===
    qos_policy_lines = generate_qos_policies_section(df_atnd)
    mml_output.extend(qos_policy_lines)
    
    # === SECCIÓN 8: SYSTEM CLOCK Y CARD ===
    system_card_lines = generate_system_card_section(df_atnd)
    mml_output.extend(system_card_lines)
    
    # === SECCIÓN 9: PUERTOS (PORTS) ===
    ports_lines = generate_ports_section(df_atnd, vlan_type)
    mml_output.extend(ports_lines)
    
    # === SECCIÓN 11: PORT BVI & MANAGEMENT ===
    try:
        lines_bvi = generate_port_bvi_section(df_atnd)
        mml_output.extend(lines_bvi)
    except Exception as e:
        print(f"ERROR: Falló generate_port_bvi_section: {e}")
        import traceback
        traceback.print_exc()
    
    mml_output.append("!")
    mml_output.append("!")

    # === SECCIÓN 11: SYSTEM BASIC (MOVIDO AL FINAL) ===
    try:
        sys_lines = generate_system_basic_section(df_atnd)
        mml_output.extend(sys_lines)
    except Exception as e:
        print(f"Error generando System Basic section: {e}")
        import traceback
        traceback.print_exc()

    
    # === SECCIÓN 12: NETWORK MANAGEMENT (AL FINAL) ===
    try:
        net_mgmt_lines = generate_network_management_section(df_atnd)
        mml_output.extend(net_mgmt_lines)
    except Exception as e:
        print(f"Error generando Network Management section: {e}")
        import traceback
        traceback.print_exc()

    # === SECCIÓN 13: BRIDGES (FINAL-FINAL) ===
    # User pidió que fuera la última parte
    try:
        bridge_lines = generate_bridge_domains_section(df_atnd)
        mml_output.extend(bridge_lines)
    except Exception as e:
        print(f"ERROR: Falló generate_bridge_domains_section: {e}")
        import traceback
        traceback.print_exc()

    # === SECCIÓN 14: SYNCHRONIZATION (REQV 6675) ===
    # Extract from 'Synchronization' sheet
    try:
        sync_lines = generate_synchronization_section(df_atnd)
        mml_output.extend(sync_lines)
    except Exception as e:
        print(f"ERROR: Falló generate_synchronization_section: {e}")
        import traceback
        traceback.print_exc()

    # Escribir archivo
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(mml_output))
        print(f"SUCCESS: Advanced script generado: {filename}")
        return filepath
    except Exception as e:
        print(f"ERROR: No se pudo generar advanced script: {e}")
        import traceback
        traceback.print_exc()
        return None
