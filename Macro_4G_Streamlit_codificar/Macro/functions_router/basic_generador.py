from functions_router.data_reader_router import get_master_vlan_data, get_all_client_vlan_data
import os

def generar_script_basic(nemonico, output_dir, df_atnd, vlan_type="ALL_VLAN"):
   
    # -----------------------------------------------------------------
    # NOTA: vlan_type ahora es un parámetro EXPLÍCITO requerido
    # Valores posibles: "MASTER_VLAN" o "ALL_VLAN"
    # Ya no auto-detectamos, el usuario lo seleccionó en el UI
    # -----------------------------------------------------------------
    
    """
    Genera el archivo Script_Basic_{Nemonico}.txt con la firma.
    
    Args:
        nemonico: Némónico del router
        output_dir: Directorio de salida
        df_atnd: Diccionario con todas las hojas del ATND
        vlan_type: Tipo explícito - "MASTER_VLAN" o "ALL_VLAN"
    """
    filename = f"Script_Basic_{nemonico}.txt"
    filepath = os.path.join(output_dir, filename)
    
    from datetime import datetime
    now = datetime.now()
    fecha_str = now.strftime("%d-%m-%Y")
    hora_str = now.strftime("%H:%M:%S")
    
    # El tipo viene del parámetro explícito (seleccionado por el usuario en UI)
    vlan_type_display = "Master VLAN" if vlan_type == "MASTER_VLAN" else "All VLAN"

    mml_output = []
    mml_output.append("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    mml_output.append("!!")
    mml_output.append(f"!! ARCHIVO     : {filename}")
    mml_output.append("!! AUTOR       : Piero Ledesma")
    mml_output.append(f"!! FECHA       : {fecha_str}")
    mml_output.append(f"!! HORA        : {hora_str}")
    mml_output.append(f"!! NEMONICO    : {nemonico}")
    mml_output.append(f"!! TIPO VLAN   : {vlan_type_display}")
    mml_output.append("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    
    # --- LÓGICA DE EXTRACCIÓN DE DATOS ---
    management_ip = "DATA_NOT_FOUND" 
    oss_ip = "DATA_NOT_FOUND" 
    oss_gateway = "DATA_NOT_FOUND"
    
    ntp_servers = []
    link_group_name = "DATA_NOT_FOUND"
    link_group_desc = "DATA_NOT_FOUND"
    port_ethernet_id = "DATA_NOT_FOUND"
    port_speed = "DATA_NOT_FOUND"
    service_instance_3g = "DATA_NOT_FOUND"
    
    # Variables Port BVI
    bvi_name = "DATA_NOT_FOUND"
    bvi_bind_interface = "DATA_NOT_FOUND"
    bvi_context = "DATA_NOT_FOUND"
    bvi_bridge_name = "DATA_NOT_FOUND"

    try:
        if df_atnd: 
             print(f"DEBUG: Keys in df_atnd at start of basic_generador: {list(df_atnd.keys())}")
        
        # 1. Router Layer 3 Configuration
        if df_atnd and 'Router Layer 3 Configuration' in df_atnd:
            df = df_atnd['Router Layer 3 Configuration']
            
            # Convertimos todo a string para buscar mejor
            df_str = df.astype(str)
            
            print(f"DEBUG: 'Router Layer 3 Configuration' columns: {df.columns.tolist()}")
            print(f"DEBUG: 'Router Layer 3 Configuration' head:\n{df.head().to_string()}")

            # --- BUSCAR IP MANAGEMENT (Context local) ---
            # Buscamos la celda que diga "Context local"
            mask_local = df_str.apply(lambda x: x.str.contains('Context local', case=False, na=False))
            rows_local, cols_local = mask_local.values.nonzero()
            
            print(f"DEBUG: Found 'Context local' at rows: {rows_local}")

            if len(rows_local) > 0:
                idx_local = rows_local[0]
                # Buscamos "management" en las filas siguientes
                for i in range(idx_local, min(idx_local + 20, len(df))):
                    # Buscamos en todas las columnas de esa fila
                    row_vals = df_str.iloc[i].values
                    if 'management' in [v.strip() for v in row_vals if isinstance(v, str)]:
                        # Si encontramos 'management', buscamos una IP en esa misma fila (algo que parezca IP)
                        for val in row_vals:
                            val = str(val).strip()
                            # Check simple de IP (x.x.x.x) o CIDR (x.x.x.x/yy)
                            ip_part = val.split('/')[0]
                            if ip_part.count('.') == 3 and ip_part.replace('.', '').isdigit():
                                management_ip = ip_part # Usamos solo la IP sin mascara si es necesario, o val completo?
                                # El script usa "ip address {management_ip}", usualmente sin mascara en este comando si es IOS XR?
                                # Pero si es "ip address 1.2.3.4 255.255.255.0" o "ip address 1.2.3.4/24"
                                # El output esperado es "ip address {management_ip}".
                                # Si el excel tiene CIDR, probablemente queramos la IP y la mascara, o solo la IP.
                                # Asumiremos que pasamos el valor tal cual si tiene / o no, pero validamos la parte IP.
                                management_ip = val 
                                break
                        if management_ip != "DATA_NOT_FOUND": break

            # --- BUSCAR IP MANAGEMENT (Context local) --- (End of block moved down slightly in original file, focusing on Context OSS now)
            
            # --- BUSCAR IP OSS (Context OSS) ---
            mask_oss = df_str.apply(lambda x: x.str.contains('Context OSS', case=False, na=False))
            rows_oss, cols_oss = mask_oss.values.nonzero()
            
            print(f"DEBUG: Found 'Context OSS' at rows: {rows_oss}")

            if len(rows_oss) > 0:
                idx_oss = rows_oss[0]
                # Buscamos "OSS" en las filas siguientes
                for i in range(idx_oss, min(idx_oss + 20, len(df))):
                    row_vals = df_str.iloc[i].values
                    # Buscamos "OSS" exacto o casi exacto en la fila
                    if 'OSS' in [str(v).strip() for v in row_vals]:
                         for val in row_vals:
                            val = str(val).strip()
                            ip_part = val.split('/')[0]
                            if ip_part.count('.') == 3 and ip_part.replace('.', '').isdigit():
                                oss_ip = val
                                break
                    if oss_ip != "DATA_NOT_FOUND": break
                
                # --- BUSCAR GATEWAY OSS (0.0.0.0/0) ---
                # A partir de donde encontramos Context OSS
                for i in range(idx_oss, min(idx_oss + 30, len(df))):
                    row_vals = df_str.iloc[i].values
                    if '0.0.0.0/0' in [str(v).strip() for v in row_vals]:
                        # El gateway suele estar en la columna siguiente o cerca
                        for val in row_vals:
                            val = str(val).strip()
                            if val.count('.') == 3 and val.replace('.', '').isdigit():
                                oss_gateway = val
                                break
                    if oss_gateway != "DATA_NOT_FOUND": break

        # 2. Router Network Management (NTP)
        if df_atnd and 'Router Network Management' in df_atnd:
            df_ntp = df_atnd['Router Network Management']
            try:
                # Buscar header "NTP Server IP"
                mask = df_ntp.astype(str).apply(lambda x: x.str.contains('NTP Server IP', case=False, na=False))
                rows, cols = mask.values.nonzero()
                
                if len(rows) > 0:
                    idx_ntp = rows[0]
                    col_ntp = cols[0]
                    
                    oss_count = 0
                    for i in range(idx_ntp + 1, min(idx_ntp + 15, len(df_ntp))):
                        # Intentamos leer IP, Version, Source de columnas relativas
                        # A veces estan pegadas, a veces no. Asumimos estructura estandar por ahora pero con try
                        try:
                            ip = str(df_ntp.iloc[i, col_ntp]).strip()
                            if ip.lower() == 'nan' or ip == '': continue
                            if 'system clock' in ip.lower(): break 
                            
                            version = str(df_ntp.iloc[i, col_ntp + 1]).strip()
                            source_val = str(df_ntp.iloc[i, col_ntp + 2]).strip()
                            
                            if 'OSS' in source_val:
                                oss_count += 1
                                prefer_str = " prefer" if oss_count == 1 else ""
                                cmd = f"server {ip} version {version} source {source_val}{prefer_str}"
                                ntp_servers.append(cmd)
                        except: continue
            except: pass

        # 3. Port Detail (Link Group & Port Ethernet)
        if df_atnd and 'Port Detail' in df_atnd:
            df_port = df_atnd['Port Detail']
            try:
                # Buscar "link-group"
                mask = df_port.astype(str).apply(lambda x: x.str.contains('link-group', case=False, na=False))
                rows, cols = mask.values.nonzero()
                if len(rows) > 0:
                    r, c = rows[0], cols[0]
                    val = str(df_port.iloc[r, c]).strip()
                    # "link-group WAN_10G_BI919"
                    link_group_name = val.split()[-1]
                    
                    # Descripcion suele estar en otra columna misma fila
                    # Buscamos algo largo o en col 9 como antes
                    if len(df_port.columns) > 9:
                        link_group_desc = str(df_port.iloc[r, 9]).strip()
                    
                    # Port ID y Speed suelen estar cerca
                    # Asumimos que estan en la misma fila o cerca
                    port_ethernet_id = str(df_port.iloc[r, 2]).strip() # Fallback a lo anterior
                    port_speed = str(df_port.iloc[r, 5]).strip()
            except: pass

       # 4. Layer 2 CLIENT (Service Instance 3g_monitor & Port BVI)
        
        # 4.1. Determinar qué hoja de L2 usar basado en el tipo EXPLÍCITO
        # Ya no usamos 'Layer 2 Data' genérico, sino el nombre REAL de la hoja
        if vlan_type == "MASTER_VLAN":
            l2_sheet_name = 'Layer 2 MASTER VLAN'
        else:  # ALL_VLAN
            l2_sheet_name = 'Layer 2 ALL CLIENT'
            
        # 4.2. Intentar leer la hoja correcta
        df_l2 = None
        print(f"DEBUG: Keys in df_atnd: {list(df_atnd.keys()) if df_atnd else 'None'}")
        print(f"DEBUG: Looking for sheet key: {l2_sheet_name}")
        
        # Intentar leer directamente del Excel con el nombre correcto
        if df_atnd and l2_sheet_name in df_atnd:
            df_l2 = df_atnd[l2_sheet_name]
        # Fallback: si usaron la clave genérica 'Layer 2 Data'
        elif df_atnd and 'Layer 2 Data' in df_atnd:
            df_l2 = df_atnd['Layer 2 Data']
            print(f"DEBUG: Using fallback 'Layer 2 Data' key")
        
        # 4.3. Si tenemos la hoja, procedemos a la extracción
        if df_l2 is not None:
            df_l2_str = df_l2.astype(str)
            
            # --- Extracción del service_instance_3g ---
            # Buscamos "3g_monitor"
            mask_3g = df_l2_str.apply(lambda x: x.str.contains('3g_monitor', case=False, na=False))
            rows_3g, cols_3g = mask_3g.values.nonzero()
            
            if len(rows_3g) > 0:
                r, c = rows_3g[0], cols_3g[0]
                # El valor suele estar 2 filas abajo en la misma columna
                if r + 2 < len(df_l2):
                    service_instance_3g = str(df_l2.iloc[r+2, c]).strip()
            
            # --- Extracción de Port BVI ---
            # Buscamos "Port BVI"
            mask_bvi = df_l2_str.apply(lambda x: x.str.contains('Port BVI', case=False, na=False))
            rows_bvi, cols_bvi = mask_bvi.values.nonzero()
            
            if len(rows_bvi) > 0:
                idx_bvi = rows_bvi[0]
                # Buscamos "OSS" debajo de Port BVI
                for i in range(idx_bvi + 1, min(idx_bvi + 20, len(df_l2))):
                    row_vals = df_l2_str.iloc[i].values
                    
                    if 'OSS' in [str(v).strip() for v in row_vals]:
                        # Encontramos la fila OSS
                        # Buscamos valores que parezcan lo que necesitamos
                        # Bind Interface (ej: 100, 200)
                        # Context (ej: OSS)
                        # Bridge Name (ej: BR_OSS)
                        
                        # Estrategia: Iterar columnas y asignar segun contenido o posicion relativa
                        # Asumimos estructura relativa similar a antes pero mas flexible
                        # Col 1: Name (OSS), Col 4: Bind, Col 5: Context, Col 6: Bridge
                        
                        # Intentamos mapear por indices relativos si es posible
                        # Encontramos en que columna esta "OSS"
                        try:
                            col_oss = list(row_vals).index('OSS')
                            bvi_name = 'OSS'
                            # En el excel:
                            # Col 1 (Index 1): Name (OSS) -> col_oss
                            # Col 4 (Index 4): Bind Interface -> col_oss + 3
                            # Col 5 (Index 5): Context -> col_oss + 4
                            # Col 6 (Index 6): Bridge Name -> col_oss + 5
                            
                            if col_oss + 3 < len(row_vals):
                                bvi_bind_interface = str(row_vals[col_oss + 3]).strip()
                            if col_oss + 4 < len(row_vals):
                                bvi_context = str(row_vals[col_oss + 4]).strip()
                            if col_oss + 5 < len(row_vals):
                                bvi_bridge_name = str(row_vals[col_oss + 5]).strip()
                        except: pass
                        break

    except Exception as e:
        print(f"Error extrayendo datos del ATND: {e}")

    mml_output.append("conf")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("service multiple-contexts")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("context local")
    mml_output.append("!")
    mml_output.append("management context OSS")
    mml_output.append("!")
    mml_output.append("context local")
    mml_output.append("!")
    mml_output.append("no ip domain-lookup")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("interface management")
    mml_output.append("description management interface")
    mml_output.append(f"ip address {management_ip}")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("service ftp client")
    mml_output.append("service ssh")
    mml_output.append("service sftp")
    mml_output.append("service scp")
    mml_output.append("service telnet")
    mml_output.append("service snmp server")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("logging console")
    mml_output.append("!")
    mml_output.append("aaa authentication administrator local")
    mml_output.append("!")
    mml_output.append("administrator admin encrypted 2 $1$IjmuzPqE$xOpV86YE487YVkRrXKtfks/OdsYV/YDZURydVSRshIun5LbW4R49FPj9EJPTQBiLFnRcAYXrY.dMfokuAhoAx0")
    mml_output.append("  privilege start 10")
    mml_output.append("  privilege max 15")
    mml_output.append("  no timeout session idle")
    mml_output.append("  role NetconfPlatformAdministrator")
    mml_output.append("  role SudoUser")
    mml_output.append("  role SystemAdministrator")
    mml_output.append("  role SystemSecurityAdministrator")
    mml_output.append("  role TechSupport")
    mml_output.append("  no password-aging")
    mml_output.append("  ")
    mml_output.append("administrator entelum encrypted 2 $1$24/i19sU$Kwz.ucCJmBQa0X7w5edC8l/X0pG6puvpuXNPgf.zgRiUYiztDSVqagNtbTwScOFDbbs8fFjlLbT.VEXKTN5Uq0")
    mml_output.append("  privilege start 10")
    mml_output.append("  privilege max 15")
    mml_output.append("  timeout session idle 5")
    mml_output.append("  role NetconfPlatformAdministrator")
    mml_output.append("  role SystemAdministrator")
    mml_output.append("  role SystemSecurityAdministrator")
    mml_output.append("  no password-aging")
    mml_output.append("  ")
    mml_output.append("administrator COMUser encrypted 2 $6$gc3n/q8a$W10GNxvKPHWwc3hxVCtd.RfzeSmvUFiSIBhWSCuu.fzsBlSgXQQ1nte15VRD3rMAZ8b99Xz0q3/x1Mj7/Qk0cL1")
    mml_output.append("  role NetconfPlatformAdministrator")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("netconf tls server admin-state enabled")
    mml_output.append("default tls cipher-filter")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("global synchronization option 1")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("context OSS")
    mml_output.append("!")
    mml_output.append("no ip domain-lookup")
    mml_output.append("!")
    mml_output.append("interface OSS")
    mml_output.append("description Management Interface OSS")
    mml_output.append(f"ip address {oss_ip}")
    mml_output.append("propagate qos from ip class-map dscp-to-pd")
    mml_output.append("")
    mml_output.append("!")
    mml_output.append(f"ip route 0.0.0.0/0 {oss_gateway} description defaultGateway towards OSS Network")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("service ftp client")
    mml_output.append("service ssh")
    mml_output.append("service sftp")
    mml_output.append("service scp")
    mml_output.append("service telnet")
    mml_output.append("service snmp server")
    mml_output.append("!")
    mml_output.append("ntp-mode")
    mml_output.append("!")
    for ntp_cmd in ntp_servers:
        mml_output.append(ntp_cmd)
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("no logging console")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append(f"link-group {link_group_name}")
    mml_output.append(f"description {link_group_desc}")
    mml_output.append("encapsulation dot1q")
    mml_output.append("qos pwfq scheduling physical-port")
    mml_output.append("maximum-links 1")
    mml_output.append("qos policy queuing")
    mml_output.append(f"service-instance {service_instance_3g}")
    mml_output.append("match")
    mml_output.append(f"dot1q {service_instance_3g}")
    mml_output.append("profile 8021p-on-useip")
    mml_output.append("!")
    mml_output.append("!")
    
    # --- FINAL SECTION ---
    mml_output.append(f"port ethernet {port_ethernet_id} {port_speed}")
    mml_output.append(f"description {link_group_desc}")
    mml_output.append("no shutdown")
    mml_output.append("synchronous-mode")
    mml_output.append("squelch ql-dnu quality-level ql-sec")
    mml_output.append(f"link-group {link_group_name}")
    mml_output.append("lacp priority 100")
    mml_output.append("!")
    mml_output.append(f"port bvi {bvi_name}")
    mml_output.append("no shutdown")
    mml_output.append(f"bridge name {bvi_bridge_name}")
    mml_output.append("encapsulation dot1q")
    mml_output.append(f"dot1q pvc {service_instance_3g}")
    mml_output.append(f"bind interface {bvi_bind_interface} {bvi_context}")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append(f"bridge {bvi_bridge_name}")
    mml_output.append(f"lg {link_group_name} service-instance {service_instance_3g}")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("!")
    mml_output.append("end")
    mml_output.append("save conf")
    mml_output.append("y")

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(mml_output))
        return filepath
    except Exception as e:
        return None
