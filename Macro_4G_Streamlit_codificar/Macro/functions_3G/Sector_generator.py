# =====================================================================
# Sector_generator.py - Generación de script Sector MOS para 3G WCDMA
# =====================================================================

import pandas as pd
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import os

# =====================================================================
# CONSTANTES DE CONFIGURACIÓN
# =====================================================================

OUTPUT_FILENAME = "01_Nemonico_PL_Sector.mos"
OUTPUT_FOLDER = "01_nodo_nemonico"

# =====================================================================
# FUNCIÓN PRINCIPAL DE GENERACIÓN
# =====================================================================

def generate_sector_mos(
    nemonico: str,
    output_base_path: str,
    rnd_data: Optional[Dict[str, pd.DataFrame]] = None,
    configuracion: str = "Configuración Básica 3G"
) -> Tuple[bool, str, str]:
    """
    Genera el archivo MOS de Sector para 3G WCDMA.
    """
    try:
        # Crear carpeta de salida si no existe
        output_dir = os.path.join(output_base_path, OUTPUT_FOLDER)
        os.makedirs(output_dir, exist_ok=True)
        
        # Ruta completa del archivo
        output_file = os.path.join(output_dir, OUTPUT_FILENAME)
        
        # Generar contenido del MOS
        mos_content = generate_sector_mml(nemonico, rnd_data, configuracion)
        
        # Escribir archivo
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(mos_content)
        
        return True, f"Archivo generado exitosamente: {output_file}", output_file
        
    except Exception as e:
        return False, f"Error al generar archivo Sector: {str(e)}", ""


def generate_sector_mml(nemonico: str, rnd_data: Optional[Dict[str, pd.DataFrame]] = None, configuracion: str = "Configuración Básica 3G") -> str:
    """
    Genera el contenido MML completo del script Sector.
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
    # SECCIÓN DINÁMICA: HW - RRU
    # ============================================================
    if rnd_data and 'RfPort' in rnd_data:
        mml_output.append(generate_rru_section(rnd_data['RfPort'], nemonico))
    else:
        mml_output.append("// ADVERTENCIA: No se encontraron datos de RfPort para generar sección RRU")
        
    # ============================================================
    # SECCIÓN DINÁMICA: HW - RFPORT
    # ============================================================
    if rnd_data and 'RfPort' in rnd_data:
        mml_output.append(generate_rfport_section(rnd_data['RfPort'], nemonico))
    else:
        mml_output.append("// ADVERTENCIA: No se encontraron datos de RfPort para generar sección RfPort")
    
    # ============================================================
    # NUEVA SECCIÓN DINÁMICA: HW - AntennaUnitGroup
    # ============================================================
    if rnd_data and 'RfBranch' in rnd_data:
        mml_output.append(generate_antennaunitgroup(rnd_data))
    else:
        mml_output.append("// ADVERTENCIA: No se encontraron datos de RfBranch para generar AntennaUnitGroup")

    # ============================================================
    # NUEVA SECCIÓN DINÁMICA: HW - AuPort
    # ============================================================
    if rnd_data and 'RfBranch' in rnd_data:
        mml_output.append(generate_auport_section(rnd_data['RfBranch'], nemonico))
    else:
        mml_output.append("// ADVERTENCIA: No se encontraron datos de RfBranch para generar sección AuPort")

    # ============================================================
    # NUEVA SECCIÓN DINÁMICA: HW - RfBranch
    # ============================================================
    if rnd_data and 'RfBranch' in rnd_data:
        mml_output.append(generate_rfbranch_section(rnd_data['RfBranch'], nemonico))
    else:
        mml_output.append("// ADVERTENCIA: No se encontraron datos de RfBranch para generar sección RfBranch")



    # ============================================================
    # NUEVA SECCIÓN DINÁMICA: SectorEquipmentFunction
    # ============================================================
    if rnd_data and 'RfBranch' in rnd_data:
        mml_output.append(generate_sector_equipment_function_section(rnd_data['RfBranch'], nemonico))
    else:
        mml_output.append("// ADVERTENCIA: No se encontraron datos de RfBranch para generar sección SectorEquipmentFunction")

    # ============================================================
    # NUEVA SECCIÓN: RiPort (Estática)
    # ============================================================
    mml_output.append(generate_riport_section())

    # ============================================================
    # NUEVA SECCIÓN: Rilink (Dinámica según Configuración)
    # ============================================================
    if rnd_data and 'RfBranch' in rnd_data:
        mml_output.append(generate_rilink_section(configuracion, rnd_data['RfBranch'], nemonico))
    else:
        mml_output.append(generate_rilink_section(configuracion, None, nemonico))

    # ============================================================
    # COMANDOS FINALES
    # ============================================================
    mml_output.append("\n################################\n")
    mml_output.append("gs-")
    mml_output.append("confb-")
    mml_output.append("cvms PL_sector_$nodename")
    mml_output.append("\nST RRU|SECTOR|CELL")
    mml_output.append("/////////////////////////fin script Sector\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")

    return "\n".join(mml_output)


# =====================================================================
# GENERACIÓN DE ENCABEZADO
# =====================================================================

def generate_header(nemonico: str) -> str:
    now = datetime.now()
    hora = now.strftime("%H:%M:%S")
    fecha = now.strftime("%d-%m-%Y")
    
    header = f"""//
// SCRIPT     : Sector
// NEMONICO   : {nemonico}
// HORA       : {hora}
// FECHA      : {fecha}
//
/////////////////////////////////////////////////////////////
"""
    return header


def generate_initial_commands() -> str:
    commands = """
confb+
gs+
set NodeSupport=1,MpClusterHandling=1 primaryCoreRef FieldReplaceableUnit=BB-1
"""
    return commands.strip()


# =====================================================================
# GENERACIÓN DE SECCIÓN RRU (DINÁMICA)
# =====================================================================

def generate_rru_section(df_rfport: pd.DataFrame, nemonico: str) -> str:
    """
    Genera la sección de comandos MML para RRUs basada en la hoja RfPort.
    Filtra por el nemónico del sitio.
    """
    mml_output = []
    
    mml_output.append("\n#############################################################")
    mml_output.append("### HW - RRU                                  ")
    mml_output.append("#############################################################\n")
    
    # 1. LIMPIEZA DE COLUMNAS (Para evitar errores por espacios o saltos de línea en Excel)
    df_rfport.columns = df_rfport.columns.str.strip().str.replace('\n', '')
    
    # 2. VALIDACIÓN DE COLUMNAS REQUERIDAS
    col_rru = 'FieldReplaceableUnit'
    col_site = 'Site'
    
    if col_rru not in df_rfport.columns:
        return f"// ERROR: Columna '{col_rru}' no encontrada en RfPort. Columnas detectadas: {list(df_rfport.columns)}"
    
    if col_site not in df_rfport.columns:
        # Intentamos buscar variaciones comunes si 'Site' no existe
        found_site = False
        for col in df_rfport.columns:
            if 'SITE' in col.upper() or 'NEMONICO' in col.upper():
                col_site = col
                found_site = True
                break
        if not found_site:
            return "// ERROR CRITICO: No se encuentra columna 'Site' o similar para filtrar."

    # 3. FILTRADO POR SITIO (CRUCIAL)
    # Convertimos a string y mayúsculas para asegurar coincidencia (ULA781 vs ula781)
    df_filtered = df_rfport[df_rfport[col_site].astype(str).str.upper() == nemonico.upper()].copy()
    
    if df_filtered.empty:
        return f"// ADVERTENCIA: No se encontraron registros en RfPort para el sitio {nemonico}"

    # 4. OBTENCIÓN DE RRUs ÚNICAS
    rrus = df_filtered[col_rru].dropna().astype(str).unique()
    rrus_sorted = sorted(rrus)
    
    if len(rrus_sorted) == 0:
          return f"// ADVERTENCIA: El sitio {nemonico} existe pero no tiene RRUs definidas en la columna {col_rru}"

    # 5. GENERACIÓN DE COMANDOS
    for rru in rrus_sorted:
        rru = rru.strip()
        if not rru:
            continue
            
        mml_output.append(f"cr Equipment=1,FieldReplaceableUnit={rru}")
        mml_output.append(f"cr Equipment=1,FieldReplaceableUnit={rru},Riport=DATA_1")
        mml_output.append(f"cr Equipment=1,FieldReplaceableUnit={rru},Riport=DATA_2\n")
    
    return "\n".join(mml_output)


# =====================================================================
# GENERACIÓN DE SECCIÓN RFPORT (DINÁMICA)
# =====================================================================

def generate_rfport_section(df_rfport: pd.DataFrame, nemonico: str) -> str:
    """
    Genera el bloque de comandos MML para la configuración de RfPort 
    basado en los datos de la hoja RfPort.
    """
    mml_output = []
    
    # Encabezado de la sección
    mml_output.append("\n#############################################################")
    mml_output.append("### HW - RfPort                               ")
    mml_output.append("#############################################################\n")
    
    # 1. LIMPIEZA DE COLUMNAS Y FILTRADO (reutilizamos la lógica del RRU)
    df_rfport.columns = df_rfport.columns.str.strip().str.replace('\n', '')
    col_site = 'Site' 
    
    if col_site not in df_rfport.columns:
        # Intentamos buscar variaciones comunes si 'Site' no existe
        found_site = False
        for col in df_rfport.columns:
            if 'SITE' in col.upper() or 'NEMONICO' in col.upper():
                col_site = col
                found_site = True
                break
        if not found_site:
            return "// ERROR CRITICO: No se encuentra columna 'Site' o similar para filtrar en RfPort."
            
    # Filtrar por sitio
    df_filtered = df_rfport[df_rfport[col_site].astype(str).str.upper() == nemonico.upper()].copy()

    if df_filtered.empty:
        return f"### ADVERTENCIA: No se encontraron registros en RfPort para el sitio {nemonico}. No se generó la configuración de RfPort.\n"

    # 2. Iterar sobre las filas (cada fila es un RfPort)
    for index, row in df_filtered.iterrows():
        try:
            rru = str(row["FieldReplaceableUnit"]).strip()
            rf_port = str(row["RfPort"]).strip()
            admin_state = str(row["administrativeState"]).strip()
            user_label = str(row["userLabel"]).strip()
            # Convertir a minúsculas para 'true'/'false' según el estándar de MML
            vswr_active = str(row["vswrSupervisionActive"]).strip().lower() 
            vswr_sens = str(row["vswrSupervisionSensitivity"]).strip()
            
            # Referencia completa del objeto RfPort
            rru_port_ref = f"Equipment=1,FieldReplaceableUnit={rru},RfPort={rf_port}"
            
            # Comandos MML de Creación y Configuración
            mml_output.append(f"cr {rru_port_ref}")
            mml_output.append(f"set {rru_port_ref} userLabel {user_label}")
            mml_output.append(f"set {rru_port_ref} vswrSupervisionActive {vswr_active}")
            mml_output.append(f"set {rru_port_ref} vswrSupervisionSensitivity {vswr_sens}")
            mml_output.append(f"set {rru_port_ref} administrativeState {admin_state}\n") # Añadir salto de línea para separar bloques
            
        except KeyError as e:
            mml_output.append(f"### ERROR DE CAMPO: Columna '{e.args[0]}' no encontrada en RfPort para la fila {index}. Se omite este RfPort.")
            continue
        except Exception as e:
            mml_output.append(f"### ERROR DESCONOCIDO: Error al procesar fila {index} del RfPort: {str(e)}. Se omite este RfPort.")
            continue
    
    # Si no se generó ningún comando (a pesar de tener el dataframe filtrado), emitir una advertencia.
    if len(mml_output) <= 3: # 3 es la cantidad de líneas del encabezado de la sección
        mml_output.append(f"### ADVERTENCIA: El DataFrame de RfPort para {nemonico} estaba vacío o no pudo procesarse correctamente.\n")
        
    return "\n".join(mml_output)


# =====================================================================
# GENERACIÓN DE SECCIÓN AntennaUnitGroup (DINÁMICA)
# =====================================================================

def generate_antennaunitgroup(rnd_data: Dict[str, pd.DataFrame]) -> str:
    """
    Genera los comandos MML para crear y configurar AntennaUnitGroup, AntennaUnit y AntennaSubunit.
    
    Args:
        rnd_data: Diccionario de DataFrames del RND, debe contener la hoja 'RfBranch'.
        
    Returns:
        str: Comandos MML en formato de texto.
    """
    
    mml_output = ["\n#############################################################"]
    mml_output.append("### HW - AntennaUnitGroup")
    mml_output.append("#############################################################\n")

    # Obtener el DataFrame de RfBranch
    try:
        df_rfbranch = rnd_data['RfBranch']
    except KeyError:
        return "ERROR: Hoja 'RfBranch' no encontrada en los datos del RND."

    # Obtener los valores únicos y ordenados de AntennaUnitGroup
    # El valor debe ser un entero para que el MML sea válido (ej: AntennaUnitGroup=1)
    try:
        # Limpieza de columnas
        df_rfbranch.columns = df_rfbranch.columns.str.strip().str.replace('\n', '')
        
        # Validación de columna
        if 'AntennaUnitGroup' not in df_rfbranch.columns:
             return "ERROR: Columna 'AntennaUnitGroup' no encontrada en RfBranch."

        # Conversión y obtención de únicos
        antennagroups = df_rfbranch['AntennaUnitGroup'].dropna().astype(int).unique()
        antennagroups.sort()
        
    except Exception as e:
        return f"ERROR: No se pudo obtener/procesar 'AntennaUnitGroup' de RfBranch. Error: {e}"
    
    if len(antennagroups) == 0:
        return "ADVERTENCIA: No se encontraron AntennaUnitGroup válidos en RfBranch."


    for group_id in antennagroups:
        # Comando para AntennaUnitGroup
        mml_output.append(f"crn Equipment=1,AntennaUnitGroup={group_id}")
        mml_output.append("end")
        
        # Comando para AntennaUnit (siempre '1' según el patrón)
        mml_output.append(f"crn Equipment=1,AntennaUnitGroup={group_id},AntennaUnit=1")
        mml_output.append("end")
        
        # Comando para AntennaSubunit (siempre '1' según el patrón y con valores fijos)
        mml_output.append(f"crn Equipment=1,AntennaUnitGroup={group_id},AntennaUnit=1,AntennaSubunit=1")
        mml_output.append("azimuthHalfPowerBeamwidth 65")
        mml_output.append("commonChBeamfrmPortMap 0")
        mml_output.append("customComChBeamfrmWtsAmplitude 0,0,0,0,0,0,0,0")
        mml_output.append("customComChBeamfrmWtsPhase 0,0,0,0,0,0,0,0")
        mml_output.append("end\n") # Salto de línea para separar bloques

    mml_output.append("sale de la hoja AntennaUnitGroup")
    
    return "\n".join(mml_output)


# =====================================================================
# GENERACIÓN DE SECCIÓN AuPort (NUEVA)
# =====================================================================

def generate_auport_section(df_rfbranch: pd.DataFrame, nemonico: str) -> str:
    """
    Genera la sección AuPort basada en la columna 'AuPortRef' de la hoja RfBranch.
    Construye el path completo del MO usando AntennaUnitGroup.
    """
    mml_output = []
    
    mml_output.append("\n#############################################################")
    mml_output.append("### AuPort                       ")
    mml_output.append("#############################################################\n")
    
    # 1. LIMPIEZA DE COLUMNAS
    df_rfbranch.columns = df_rfbranch.columns.str.strip().str.replace('\n', '')
    print(f"DEBUG: Columns in RfBranch for AuPort generation: {list(df_rfbranch.columns)}")
    
    # 2. VALIDACIÓN DE COLUMNAS
    # Buscamos 'AuPortRef' (case insensitive, ignorando espacios)
    col_auport = None
    for col in df_rfbranch.columns:
        clean_col = col.upper().replace(' ', '').strip()
        if clean_col == 'AUPORTREF' or clean_col == 'AUPORT':
            col_auport = col
            break
            
    if not col_auport:
        return f"// ADVERTENCIA: No se encontró la columna 'AuPortRef' (o 'AuPort') en RfBranch. Columnas disponibles: {list(df_rfbranch.columns)}"

    # Validar AntennaUnitGroup
    if 'AntennaUnitGroup' not in df_rfbranch.columns:
        return f"// ADVERTENCIA: No se encontró la columna 'AntennaUnitGroup' en RfBranch. Columnas disponibles: {list(df_rfbranch.columns)}"

    col_site = 'Site'
    # Re-validar site (aunque ya se validó antes, por seguridad)
    if col_site not in df_rfbranch.columns:
         for col in df_rfbranch.columns:
            if 'SITE' in col.upper() or 'NEMONICO' in col.upper():
                col_site = col
                break
    
    # 3. FILTRADO POR SITIO
    df_filtered = df_rfbranch[df_rfbranch[col_site].astype(str).str.upper() == nemonico.upper()].copy()
    
    if df_filtered.empty:
        return f"// ADVERTENCIA: No hay datos para {nemonico} en RfBranch."

    # 4. GENERACIÓN DE COMANDOS (EVITANDO DUPLICADOS)
    # Usamos tupla (AntennaUnitGroup, AuPort) como clave para evitar duplicados
    processed_auports = set()
    
    for index, row in df_filtered.iterrows():
        auport_ref = str(row[col_auport]).strip()
        antenna_group = str(row['AntennaUnitGroup']).strip()
        user_label = str(row.get('userLabel', '')).strip()
        
        if not auport_ref or auport_ref.upper() == 'NAN':
            continue
        
        if not antenna_group or antenna_group.upper() == 'NAN':
            continue
            
        # Normalizar para evitar duplicados
        auport_key = (antenna_group.upper(), auport_ref.upper())
        
        if auport_key not in processed_auports:
            # Construir el path completo del MO
            mo_path = f"Equipment=1,AntennaUnitGroup={antenna_group},AntennaUnit=1,AntennaSubunit=1,AuPort={auport_ref}"
            
            mml_output.append(f"crn {mo_path}")
            if user_label:
                mml_output.append(f"userlabel {user_label}")
            mml_output.append("end\n")
            
            processed_auports.add(auport_key)
            
    return "\n".join(mml_output)


# =====================================================================
# GENERACIÓN DE SECCIÓN RfBranch (NUEVA)
# =====================================================================

def generate_rfbranch_section(df_rfbranch: pd.DataFrame, nemonico: str) -> str:
    """
    Genera la sección RfBranch basada en la hoja RfBranch.
    Construye paths completos para RfBranch, auPortRef y rfPortRef.
    """
    mml_output = []
    
    mml_output.append("\n#############################################################")
    mml_output.append("### RfBranch v2                     ")
    mml_output.append("#############################################################\n")
    
    # 1. LIMPIEZA DE COLUMNAS
    df_rfbranch.columns = df_rfbranch.columns.str.strip().str.replace('\n', '')
    print(f"DEBUG: Columns in RfBranch for RfBranch generation: {list(df_rfbranch.columns)}")
    
    # 2. VALIDACIÓN DE COLUMNAS REQUERIDAS
    required_cols = {
        'AntennaUnitGroup': None,
        'RfBranch': None,
        'dlAttenuation': None,
        'dlTrafficDelay': None,
        'ulAttenuation': None,
        'ulTrafficDelay': None,
        'userLabel': None
    }
    
    # Validar columnas base
    for col_name in required_cols.keys():
        if col_name not in df_rfbranch.columns:
            return f"// ADVERTENCIA: Columna '{col_name}' no encontrada en RfBranch. Columnas disponibles: {list(df_rfbranch.columns)}"
    
    # Buscar auPortRef (case insensitive)
    col_auportref = None
    for col in df_rfbranch.columns:
        clean_col = col.upper().replace(' ', '').strip()
        if clean_col == 'AUPORTREF' or clean_col == 'AUPORT':
            col_auportref = col
            break
    
    if not col_auportref:
        return f"// ADVERTENCIA: Columna 'auPortRef' no encontrada en RfBranch. Columnas disponibles: {list(df_rfbranch.columns)}"
    
    # Buscar rfPortRef (case insensitive)
    col_rfportref = None
    for col in df_rfbranch.columns:
        clean_col = col.upper().replace(' ', '').strip()
        if clean_col == 'RFPORTREF':
            col_rfportref = col
            break
    
    if not col_rfportref:
        return f"// ADVERTENCIA: Columna 'rfPortRef' no encontrada en RfBranch. Columnas disponibles: {list(df_rfbranch.columns)}"
    
    # Buscar site
    col_site = 'Site'
    if col_site not in df_rfbranch.columns:
        for col in df_rfbranch.columns:
            if 'SITE' in col.upper() or 'NEMONICO' in col.upper():
                col_site = col
                break
    
    # 3. FILTRADO POR SITIO
    df_filtered = df_rfbranch[df_rfbranch[col_site].astype(str).str.upper() == nemonico.upper()].copy()
    
    if df_filtered.empty:
        return f"// ADVERTENCIA: No hay datos para {nemonico} en RfBranch."

    # 4. GENERACIÓN DE COMANDOS
    for index, row in df_filtered.iterrows():
        try:
            antenna_group = str(row['AntennaUnitGroup']).strip()
            rfbranch = str(row['RfBranch']).strip()
            auport_ref = str(row[col_auportref]).strip()
            rfport_ref = str(row[col_rfportref]).strip()
            dl_attenuation = str(row['dlAttenuation']).strip()
            dl_traffic_delay = str(row['dlTrafficDelay']).strip()
            ul_attenuation = str(row['ulAttenuation']).strip()
            ul_traffic_delay = str(row['ulTrafficDelay']).strip()
            user_label = str(row['userLabel']).strip()
            
            # Validar valores obligatorios
            if not antenna_group or antenna_group.upper() == 'NAN':
                continue
            if not rfbranch or rfbranch.upper() == 'NAN':
                continue
            
            # Construir el path del RfBranch
            rfbranch_path = f"Equipment=1,AntennaUnitGroup={antenna_group},RfBranch={rfbranch}"
            
            # Comando crn
            mml_output.append(f"crn {rfbranch_path}")
            
            # auPortRef path completo
            if auport_ref and auport_ref.upper() != 'NAN':
                auport_path = f"Equipment=1,AntennaUnitGroup={antenna_group},AntennaUnit=1,AntennaSubunit=1,AuPort={auport_ref}"
                mml_output.append(f"auPortRef {auport_path}")
            
            # dlAttenuation - convertir espacios a comas
            if dl_attenuation and dl_attenuation.upper() != 'NAN':
                dl_attenuation_formatted = dl_attenuation.replace(' ', ',')
                mml_output.append(f"dlAttenuation {dl_attenuation_formatted}")
            
            # dlTrafficDelay - convertir espacios a comas
            if dl_traffic_delay and dl_traffic_delay.upper() != 'NAN':
                dl_traffic_delay_formatted = dl_traffic_delay.replace(' ', ',')
                mml_output.append(f"dlTrafficDelay {dl_traffic_delay_formatted}")
            
            # rfPortRef path completo - usar AntennaUnitGroup para construir RRU-X
            if rfport_ref and rfport_ref.upper() != 'NAN':
                # Construir FRU como RRU-{AntennaUnitGroup}
                rru_name = f"RRU-{antenna_group}"
                rfport_full_path = f"Equipment=1,FieldReplaceableUnit={rru_name},RfPort={rfport_ref}"
                mml_output.append(f"rfPortRef {rfport_full_path}")
            
            # ulAttenuation - convertir espacios a comas
            if ul_attenuation and ul_attenuation.upper() != 'NAN':
                ul_attenuation_formatted = ul_attenuation.replace(' ', ',')
                mml_output.append(f"ulAttenuation {ul_attenuation_formatted}")
            
            # ulTrafficDelay - convertir espacios a comas
            if ul_traffic_delay and ul_traffic_delay.upper() != 'NAN':
                ul_traffic_delay_formatted = ul_traffic_delay.replace(' ', ',')
                mml_output.append(f"ulTrafficDelay {ul_traffic_delay_formatted}")
            
            # userLabel
            if user_label and user_label.upper() != 'NAN':
                mml_output.append(f"userLabel {user_label}")
            
            mml_output.append("end\n")
            
        except KeyError as e:
            mml_output.append(f"// ERROR: Columna '{e.args[0]}' no encontrada en fila {index}")
            continue
        except Exception as e:
            mml_output.append(f"// ERROR: Error al procesar fila {index}: {str(e)}")
            continue
    
    return "\n".join(mml_output)


# =====================================================================
# GENERACIÓN DE SECCIÓN SectorEquipmentFunction (NUEVA)
# =====================================================================

def generate_sector_equipment_function_section(df_rfbranch: pd.DataFrame, nemonico: str) -> str:
    """
    Genera la sección SectorEquipmentFunction basada en AntennaUnitGroup de la hoja RfBranch.
    La idea es que sea dinamica dependiendo de la cantidad de antennaunitgroup.
    """
    mml_output = []
    
    mml_output.append("\n#############################################################")
    mml_output.append("### Sector     V2                  ")
    mml_output.append("#############################################################\n")
    
    # 1. LIMPIEZA DE COLUMNAS
    df_rfbranch.columns = df_rfbranch.columns.str.strip().str.replace('\n', '')
    
    # Helper para buscar columnas case-insensitive
    def find_col(df, keywords):
        for col in df.columns:
            for kw in keywords:
                if kw.upper() == col.upper().strip():
                    return col
        return None

    # 2. VALIDACIÓN DE COLUMNAS
    col_site = find_col(df_rfbranch, ['Site', 'Nemonico', 'NodeId'])
    col_aug = find_col(df_rfbranch, ['AntennaUnitGroup'])
    col_rfbranch = find_col(df_rfbranch, ['RfBranch'])
    col_userlabel = find_col(df_rfbranch, ['userLabel', 'User Label'])

    if not col_site:
        return "// ERROR CRITICO: No se encuentra columna 'Site' o similar para filtrar en RfBranch."
    
    if not col_aug:
        return "// ADVERTENCIA: No se encontró columna 'AntennaUnitGroup' para generar SectorEquipmentFunction"

    if not col_rfbranch:
        return "// ADVERTENCIA: No se encontró columna 'RfBranch' para generar SectorEquipmentFunction"

    # 3. FILTRADO POR SITIO
    df_filtered = df_rfbranch[df_rfbranch[col_site].astype(str).str.upper() == nemonico.upper()].copy()
    
    if df_filtered.empty:
        return f"// ADVERTENCIA: No hay datos para {nemonico} en RfBranch para SectorEquipmentFunction."

    # 4. AGRUPAMIENTO POR AntennaUnitGroup
    try:
        # Normalizar AntennaUnitGroup a entero para asegurar consistencia
        # Primero convertimos a numérico, coercing errores a NaN, luego eliminamos NaNs
        df_filtered['AUG_Clean'] = pd.to_numeric(df_filtered[col_aug], errors='coerce')
        df_filtered = df_filtered.dropna(subset=['AUG_Clean'])
        df_filtered['AUG_Clean'] = df_filtered['AUG_Clean'].astype(int)
        
        # Obtenemos grupos únicos
        unique_groups = sorted(df_filtered['AUG_Clean'].unique())
        
        for group_id in unique_groups:
            # Filtrar filas para este grupo usando la columna limpia
            group_rows = df_filtered[df_filtered['AUG_Clean'] == group_id]
            
            # Obtener userLabel
            user_label = "Sector_Default"
            if col_userlabel:
                labels = group_rows[col_userlabel].dropna().astype(str)
                # Filtrar 'nan' string y vacíos
                valid_labels = labels[~labels.str.lower().isin(['nan', ''])]
                if not valid_labels.empty:
                    user_label = valid_labels.iloc[0]
            
            # Obtener RfBranches para este grupo
            # Convertir a string y limpiar decimales si es necesario (ej: 1.0 -> 1)
            raw_branches = group_rows[col_rfbranch].dropna()
            clean_branches = []
            for val in raw_branches:
                try:
                    # Si es float, convertir a int primero para quitar .0
                    val_float = float(val)
                    if val_float.is_integer():
                        clean_branches.append(str(int(val_float)))
                    else:
                        clean_branches.append(str(val))
                except:
                    clean_branches.append(str(val))
            
            rf_branches = sorted(list(set(clean_branches)), key=lambda x: int(x) if x.isdigit() else x)
                
            # Construir la lista de referencias
            # Formato: AntennaUnitGroup=X,RfBranch=Y
            refs = []
            for branch in rf_branches:
                if branch: # Evitar vacíos
                    refs.append(f"AntennaUnitGroup={group_id},RfBranch={branch}")
                
            refs_str = " ".join(refs)
            
            # Generar bloque MML
            mml_output.append(f"crn NodeSupport=1,SectorEquipmentFunction={group_id}")
            mml_output.append(f"userLabel {user_label}")
            mml_output.append("administrativeState 0")
            mml_output.append(f"rfBranchRef {refs_str}")
            mml_output.append("end\n")
            
    except Exception as e:
        return f"// ERROR: Fallo al generar SectorEquipmentFunction: {str(e)}"
        
    return "\n".join(mml_output)


# =====================================================================
# GENERACIÓN DE SECCIÓN RiPort (ESTÁTICA)
# =====================================================================

def generate_riport_section() -> str:
    """
    Genera la sección RiPort estática con 6 puertos (A-F) para BB-1.
    """
    mml_output = []
    
    mml_output.append("\n#############################################################")
    mml_output.append("### RiPort (Estática)               ")
    mml_output.append("#############################################################\n")
    
    # Generar 6 RiPorts estáticos
    for port in ['A', 'B', 'C', 'D', 'E', 'F']:
        mml_output.append(f"cr Equipment=1,FieldReplaceableUnit=BB-1,RiPort={port}")
    
    return "\n".join(mml_output)


# =====================================================================
# GENERACIÓN DE SECCIÓN Rilink (DINÁMICA)
# =====================================================================

def generate_rilink_section(
    configuracion: str,
    df_rfbranch: Optional[pd.DataFrame] = None,
    nemonico: str = ""
) -> str:
    """
    Genera la sección Rilink basada en la configuración seleccionada.
    
    Si configuracion == "Configuración Básica 3G":
      - Genera rilinks 3GB2_S1, 3GB2_S2, 3GB2_S3, etc.
      - Conecta BB-1 RiPort (A, B, C, ...) con RRU-X DATA_1
      - Dinámico según AntennaUnitGroups en RND
    """
    mml_output = []
    
    mml_output.append("\n#############################################################")
    mml_output.append("### Rilink (Dinámica)            ")
    mml_output.append("#############################################################\n")
    
    # Helper para buscar columnas case-insensitive
    def find_col(df, keywords):
        for col in df.columns:
            for kw in keywords:
                if kw.upper() == col.upper().strip():
                    return col
        return None
    
    if configuracion == "Configuración Básica 3G":
        # Obtener grupos únicos de AntennaUnitGroup del RND
        if df_rfbranch is not None and 'AntennaUnitGroup' in df_rfbranch.columns:
            # Limpiar nombres de columnas
            df_rfbranch.columns = df_rfbranch.columns.str.strip().str.replace('\n', '')
            
            # Filtrar por sitio
            col_site = find_col(df_rfbranch, ['Site', 'Nemonico', 'NodeId'])
            if col_site and nemonico:
                df_filtered = df_rfbranch[df_rfbranch[col_site].astype(str).str.upper() == nemonico.upper()].copy()
                
                # Obtener grupos únicos
                try:
                    groups = df_filtered['AntennaUnitGroup'].dropna().astype(int).unique()
                    groups = sorted(groups)
                    
                    # Generar rilink para cada grupo
                    riports = ['A', 'B', 'C', 'D', 'E', 'F']
                    for idx, group_id in enumerate(groups):
                        if idx < len(riports):
                            riport = riports[idx]
                            mml_output.append(f"cr equipment=1,rilink=3GB2_S{group_id}")
                            mml_output.append(f"Equipment=1,FieldReplaceableUnit=BB-1,RiPort={riport}")
                            mml_output.append(f"Equipment=1,FieldReplaceableUnit=RRU-{group_id},RiPort=DATA_1\n")
                except Exception as e:
                    mml_output.append(f"// ADVERTENCIA: Error procesando AntennaUnitGroup: {str(e)}")
                    # Fallback a 3 sectores
                    for i in range(1, 4):
                        riport = ['A', 'B', 'C'][i-1]
                        mml_output.append(f"cr equipment=1,rilink=3GB2_S{i}")
                        mml_output.append(f"Equipment=1,FieldReplaceableUnit=BB-1,RiPort={riport}")
                        mml_output.append(f"Equipment=1,FieldReplaceableUnit=RRU-{i},RiPort=DATA_1\n")
            else:
                mml_output.append("// ADVERTENCIA: No se encontró columna 'Site' para filtrar Rilink")
                # Fallback a 3 sectores
                for i in range(1, 4):
                    riport = ['A', 'B', 'C'][i-1]
                    mml_output.append(f"cr equipment=1,rilink=3GB2_S{i}")
                    mml_output.append(f"Equipment=1,FieldReplaceableUnit=BB-1,RiPort={riport}")
                    mml_output.append(f"Equipment=1,FieldReplaceableUnit=RRU-{i},RiPort=DATA_1\n")
        else:
            # Fallback: Si no hay RND, generar estático para 3 sectores
            for i in range(1, 4):
                riport = ['A', 'B', 'C'][i-1]
                mml_output.append(f"cr equipment=1,rilink=3GB2_S{i}")
                mml_output.append(f"Equipment=1,FieldReplaceableUnit=BB-1,RiPort={riport}")
                mml_output.append(f"Equipment=1,FieldReplaceableUnit=RRU-{i},RiPort=DATA_1\n")
    else:
        mml_output.append(f"// No se generan Rilinks para configuración: {configuracion}")
    
    return "\n".join(mml_output)


if __name__ == "__main__":
    print("Corre este archivo importándolo desde app.py o generator_logic_3G.py")
