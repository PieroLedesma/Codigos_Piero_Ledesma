import pandas as pd
import datetime
from typing import Dict, Any, List, Union, Tuple
import re

# ====================================================================
# === 1. FUNCIONES DE AYUDA (INDEXACIÓN Y EXTRACCIÓN SEGURA) ===
# ====================================================================

def safe_get_value(df: pd.DataFrame, mo_name: str, attribute: str, cell_column: str) -> Any:
    """
    Extrae un valor de la celda específica usando MO y Atributo, 
    retornando None si no se encuentra o está vacío/NaN.
    """
    try:
        # Se asume que el DataFrame está limpio y listo para buscar
        cell_row = df[
            (df['MO'].str.strip() == mo_name.strip()) & 
            (df['Atributo'].str.strip() == attribute.strip())
        ]
        
        if not cell_row.empty and cell_column in cell_row.columns:
            value = cell_row.iloc[0][cell_column]
            
            # Limpiar y validar
            if pd.isna(value) or (isinstance(value, str) and value.strip() == ''):
                return None
            
            # Limpiar espacios alrededor del valor si es string
            if isinstance(value, str):
                return value.strip()
            return value
            
    except Exception:
        return None
    return None

# ====================================================================
# === 2. FORMATTERS PARA ATRIBUTOS ESTRUCTURADOS CONSOLIDABLES ===
# ====================================================================

def generate_consolidated_set_struct_commands(df: pd.DataFrame, cell_column: str, struct_prefix: str, include_type_char: bool = True) -> str:
    """
    Genera comandos SET para atributos estructurados CONSOLIDABLES (ej: LoadBasedCaMsrThr, changeNotification, mappingInfo)
    donde todos los sub-atributos van en una sola línea separados por comas.
    """
    
    mo_name = 'EUtranCellFDD'
    
    # 1. Filtrar filas donde el Atributo comienza con el prefijo de la estructura
    struct_rows = df[
        (df['MO'] == mo_name) & 
        (df['Atributo'].str.contains(f"^{re.escape(struct_prefix)}_", regex=True, na=False))
    ]
    
    # Lista de tuplas para almacenar (orden_key, sub_attr_name, formatted_part)
    parts_to_sort = []
    
    # Definición de orden fijo especial para LoadBasedCaMsrThr
    # Orden deseado: cceUtilThresh, dlSeUtilThresh, ulPrbUtilThresh, ulSeUtilThresh, dlPrbUtilThresh
    ORDER_MAP = {
        'cceUtilThresh': 1,
        'dlSeUtilThresh': 2,
        'dlPrbUtilThresh': 3,
        'ulPrbUtilThresh': 4,
        'ulSeUtilThresh': 5,
    }

    
    for _, row in struct_rows.iterrows():
        full_attr_name = str(row['Atributo']).strip()
        sub_attr_name = full_attr_name.split('_', 1)[1] 
        value = row[cell_column]
        
        if pd.notna(value) and str(value).strip() != '':
            value_str = str(value).strip()
            value_str_lower = value_str.lower()
            
            # --- Lógica de Formato ---
            if include_type_char:
                type_char = 'b' if value_str_lower in ('true', 'false') else 'i' 
                formatted_part = f"{sub_attr_name}:{type_char}={value_str_lower}"
            else:
                formatted_part = f"{sub_attr_name}={value_str}"
            
            # --- Lógica de Ordenamiento ---
            order_key = float('inf') 
            
            if struct_prefix == 'LoadBasedCaMsrThr':
                # Buscamos el prefijo (ej: 'cceUtilThresh', 'dlPrbUtilThresh', etc.)
                prefix_match = re.match(r'(cceUtilThresh|dlSeUtilThresh|dlPrbUtilThresh|ulPrbUtilThresh|ulSeUtilThresh)', sub_attr_name)
                
                if prefix_match:
                    prefix = prefix_match.group(0)
                    order_key = ORDER_MAP.get(prefix, 99) # Usar 99 como fallback
                    # Añadir una orden secundaria para high/low: Low (0) va antes que High (1)
                    secondary_order = 0 if 'Low' in sub_attr_name else 1
                    parts_to_sort.append(((order_key, secondary_order), sub_attr_name, formatted_part))
                    continue # Saltar a la siguiente iteración
            
            # Ordenamiento por defecto (para SIBs, mappingInfo y otros)
            sib_match = re.search(r'SIB(\d+|10|11|12|15|16)', sub_attr_name)
            map_match = re.search(r'\d+$', sub_attr_name)
            
            if sib_match:
                order_key = int(sib_match.group(1)) 
            elif map_match:
                order_key = int(map_match.group(0))
            else:
                order_key = sub_attr_name # Usar el nombre completo para ordenar alfabéticamente

            parts_to_sort.append((order_key, sub_attr_name, formatted_part))

    # 2. Ordenar las partes: por la clave de ordenamiento, luego por el nombre alfabético
    # La clave de ordenamiento puede ser una tupla (LoadBasedCaMsrThr) o un valor simple.
    parts_to_sort.sort(key=lambda x: (x[0] if isinstance(x[0], (int, float, tuple)) else x[1], x[1]))
    
    # 3. Ensamblar el comando final
    parts = [p[2] for p in parts_to_sort]
    
    if parts:
        combined_value = ",".join(parts)
        cell_mo_name = safe_get_value(df, mo_name, 'ENodeBFunction=1,EUtranCellFDD=', cell_column)
        if cell_mo_name:
            # Estos comandos siempre van consolidados y separados por coma
            return f"set ENodeBFunction=1,EUtranCellFDD={cell_mo_name} {struct_prefix} {combined_value}\n"
    return ""

# ====================================================================
# === 3. FORMATTERS PARA ATRIBUTOS ESTRUCTURADOS INDIVIDUALES (SIB3) ===
# ====================================================================

def generate_individual_set_struct_commands(df: pd.DataFrame, cell_column: str, struct_prefix: str) -> str:
    """
    Genera comandos SET INDIVIDUALES para atributos estructurados (ej: SIB3),
    donde cada sub-atributo tiene su propia línea de comando.
    """
    mo_name = 'EUtranCellFDD'
    cell_mo_name = safe_get_value(df, mo_name, 'ENodeBFunction=1,EUtranCellFDD=', cell_column)
    if not cell_mo_name:
        return ""
        
    struct_rows = df[
        (df['MO'] == mo_name) & 
        (df['Atributo'].str.contains(f"^{re.escape(struct_prefix)}_", regex=True, na=False))
    ]
    
    parts_to_sort = []
    
    for _, row in struct_rows.iterrows():
        full_attr_name = str(row['Atributo']).strip()
        # Extrae el nombre del sub-atributo (ej: sIntraSearch)
        sub_attr_name = full_attr_name.split('_', 1)[1] 
        value = row[cell_column]
        
        if pd.notna(value) and str(value).strip() != '':
            value_str = str(value).strip()
            
            # --- Lógica de Ordenamiento ---
            order_key = float('inf') 
            sib_match = re.search(r'SIB(\d+|10|11|12|15|16)', sub_attr_name)
            
            if sib_match:
                order_key = int(sib_match.group(1)) 
            else:
                order_key = sub_attr_name # Ordenar alfabéticamente si no hay número
            
            # Almacenar la tupla: (orden_key, sub_attr_name, value_str)
            parts_to_sort.append((order_key, sub_attr_name, value_str))

    # 2. Ordenar las partes: por la clave de ordenamiento, luego por el nombre alfabético
    parts_to_sort.sort(key=lambda x: (x[0] if isinstance(x[0], (int, float)) else x[1], x[1]))
    
    # 3. Ensamblar comandos individuales
    commands = []
    for _, sub_attr_name, value_str in parts_to_sort:
        # Asegurar el uso de true/false en minúsculas para booleanos
        if value_str.lower() in ('true', 'false'):
            final_value = value_str.lower()
        else:
            final_value = value_str

        # set ENodeBFunction=1,EUtranCellFDD=L02152 systemInformationBlock3 sIntraSearch=46
        commands.append(f"set ENodeBFunction=1,EUtranCellFDD={cell_mo_name} {struct_prefix} {sub_attr_name}={final_value}")
        
    return "\n".join(commands) + "\n" if commands else ""

# ====================================================================
# === 4. LÓGICA DE CRN (3 VERSIONES) Y SETS SIMPLES/ESPECIALES ===
# ====================================================================

def generate_creation_and_simple_sets(df: pd.DataFrame, cell_column: str) -> Tuple[str, str, str]:
    """Genera los comandos CRN (3 versiones) y SET simples/especiales para una celda."""
    
    mo_name = 'EUtranCellFDD'
    cell_mo_name = safe_get_value(df, mo_name, 'ENodeBFunction=1,EUtranCellFDD=', cell_column)
    
    if not cell_mo_name:
        return "", "", ""
        
    # --- 0. EXTRACCIÓN DE ATRIBUTOS CLAVE (Para CR/CRN) ---
    
    crn_attrs_data = {
        'cellId': safe_get_value(df, mo_name, 'cellId', cell_column),
        'dlChannelBandwidth': safe_get_value(df, mo_name, 'dlChannelBandwidth', cell_column),
        'earfcndl': safe_get_value(df, mo_name, 'earfcndl', cell_column),
        'earfcnul': safe_get_value(df, mo_name, 'earfcnul', cell_column),
        'physicalLayerCellIdGroup': safe_get_value(df, mo_name, 'physicalLayerCellIdGroup', cell_column),
        'physicalLayerSubCellId': safe_get_value(df, mo_name, 'physicalLayerSubCellId', cell_column),
        'rachRootSequence': safe_get_value(df, mo_name, 'rachRootSequence', cell_column),
        'tac': safe_get_value(df, mo_name, 'tac', cell_column),
        'ulChannelBandwidth': safe_get_value(df, mo_name, 'ulChannelBandwidth', cell_column),
        'prsPeriod': safe_get_value(df, mo_name, 'prsPeriod', cell_column),
        'noConsecutiveSubframes': safe_get_value(df, mo_name, 'noConsecutiveSubframes', cell_column),
        'transmissionMode': safe_get_value(df, mo_name, 'transmissionMode', cell_column),
        'additionalPlmnList': "mcc=1,mnc=1,mncLength=2;mcc=1,mnc=1,mncLength=2;mcc=1,mnc=1,mncLength=2;mcc=1,mnc=1,mncLength=2;mcc=1,mnc=1,mncLength=2", 
        'additionalPlmnReservedList': "false,false,false,false,false"
    }
    
    try:
        match = re.search(r'S(\d+)', cell_column)
        sc_ref = f"ENodeBFunction=1,SectorCarrier={match.group(1)}" if match else "ENodeBFunction=1,SectorCarrier=UNKNOWN"
    except:
        sc_ref = "ENodeBFunction=1,SectorCarrier=UNKNOWN"
        
    cell_defined_primary_plmn_id = safe_get_value(df, mo_name, 'cellDefinedPrimaryPlmnId', cell_column) or ''

    # --- 1. BLOQUE DE CREACIÓN CRN (Con atributos - ORDEN FIJO) ---
    
    CRN_FIXED_ORDER = [
        'additionalPlmnList', 
        'additionalPlmnReservedList',
        'cellId',
        'dlChannelBandwidth',
        'earfcndl',
        'earfcnul',
        'physicalLayerCellIdGroup',
        'physicalLayerSubCellId',
        'rachRootSequence',
        'sectorCarrierRef', 
        'tac',
        'ulChannelBandwidth',
        'cellDefinedPrimaryPlmnId', 
        'prsPeriod',
        'noConsecutiveSubframes',
        'transmissionMode',
    ]

    crn_parts = []
    
    for attr_key in CRN_FIXED_ORDER:
        if attr_key == 'sectorCarrierRef':
            crn_parts.append(f"sectorCarrierRef {sc_ref}")
        elif attr_key == 'cellDefinedPrimaryPlmnId':
            crn_parts.append(f"cellDefinedPrimaryPlmnId {cell_defined_primary_plmn_id}")
        elif attr_key in crn_attrs_data:
             value = crn_attrs_data[attr_key]
             if value is not None and str(value).strip() != '':
                 crn_parts.append(f"{attr_key} {value}")
            
    crn_content = (
        f"crn ENodeBFunction=1,EUtranCellFDD={cell_mo_name}\n\n"
        + "\n".join(crn_parts)
        + "\n\nend\n"
    )

    # --- 2. BLOQUE DE CREACIÓN CR (Posicional - Versión 13 y 14 se mantienen iguales) ---
    
    cr_v13_params = [
        crn_attrs_data['earfcndl'],
        crn_attrs_data['earfcnul'],
        crn_attrs_data['cellId'],
        crn_attrs_data['physicalLayerCellIdGroup'],
        crn_attrs_data['physicalLayerSubCellId'],
        crn_attrs_data['tac'],
        sc_ref,
        crn_attrs_data['dlChannelBandwidth'],
        crn_attrs_data['ulChannelBandwidth'],
        crn_attrs_data['additionalPlmnList'], 
        crn_attrs_data['additionalPlmnReservedList']
    ]
    
    cr_v13_content = (
        f"cr ENodeBFunction=1,EUtranCellFDD={cell_mo_name}\n"
        + "\n".join(str(p) for p in cr_v13_params if p is not None)
        + "\n\n" 
    )
    
    cr_v14_params = [
        crn_attrs_data['earfcndl'],
        crn_attrs_data['earfcnul'],
        crn_attrs_data['cellId'],
        crn_attrs_data['physicalLayerCellIdGroup'],
        crn_attrs_data['physicalLayerSubCellId'],
        crn_attrs_data['tac'],
        'd', # Placeholder
        sc_ref,
        crn_attrs_data['dlChannelBandwidth'],
        crn_attrs_data['ulChannelBandwidth'],
        crn_attrs_data['additionalPlmnList'], 
        crn_attrs_data['additionalPlmnReservedList']
    ]
    
    cr_v14_content = (
        f"cr ENodeBFunction=1,EUtranCellFDD={cell_mo_name}\n"
        + "\n".join(str(p) for p in cr_v14_params if p is not None)
        + "\n\n"
    )
    
    creation_block = (
        f"// === 1. CRN (CON ATRIBUTOS - ORDEN FIJO) ===\n" 
        + crn_content 
        + f"// === 2. CR POSICIONAL (VERSIÓN 13 ARGS) ===\n" 
        + cr_v13_content
        + f"// === 3. CR POSICIONAL (VERSIÓN 14 ARGS CON 'd') ===\n" 
        + cr_v14_content
    )
    
    # --- 4. SET: Atributos simples de SET ---
    
    set_simple_attributes = [
        'noOfPucchCqiUsers', 'userLabel', 'altitude', 'latitude', 'longitude', 
        'pMaxServingCell', 'pZeroNominalPucch', 'qRxLevMin', 'qRxLevMinOffset', 
        'rachRootSequence', 'covTriggerdBlindHoAllowed', 'crsGain', 
        'maxSentCrsAssistCells', 'cellCapMaxCellSubCap', 'cellCapMinCellSubCap', 
        'cellSubscriptionCapacity', 'dlInterferenceManagementActive', 'drxActive', 
        'mobCtrlAtPoorCovActive', 'qciTableRef', 
        'pdschTypeBGain', 'outOfCoverageThreshold', 'pciConflict', 
        'pdcchCfiMode', 'emergencyAreaId', 'primaryPlmnReserved', 
        'pdcchOuterLoopInitialAdj', 'pdcchOuterLoopUpStep', 
        'qQualMin', 'threshServingLow', 'ulSrsEnable', 'zzzTemporary14', 
        'servOrPrioTriggeredErabAction', 'zzzTemporary26', 'zzzTemporary27', 
        'zzzTemporary38', 'cellCapMinMaxWriProt', 'zzzTemporary36', 
        'zzzTemporary37', 'noOfPucchSrUsers', 
        'pdcchPowerBoostMax', 'tTimeAlignmentTimer', 'cioLowerLimitAdjBySon', 
        'cioUpperLimitAdjBySon', 'puschPwrOffset64qam', 'pdcchTargetBler', 
        'pdcchTargetBlerPCell', 'ulBlerTargetEnabled', 'dynUeAdmCtrlEnabled', 
        'ttiBundlingAfterReest', 'ttiBundlingSwitchThres', 'ttiBundlingSwitchThresHyst', 
        'dynUlResourceAllocEnabled', 'enableServiceSpecificHARQ', 'srvccDelayTimer', 
        'sCellHandlingAtVolteCall', 'loadBasedCaEnabled', 'optimizedPdcchCongestThres', 
        'optimizedPdcchDlPrbThres', 'optimizedPdcchUlPrbThres', 'pdcchFlexibleBlerEnabled', 
        'maxNoClusteredPuschAlloc', 'minInterfUlRegionSize', 'minInterfSchedEnabled', 
        'cfraEnable', 'blerTargetConfigEnabled', 'dlBlerTargetEnabled', 
        'lastSchedLinkAdaptEnabled', 'endcAllowedPlmnList', 'diffPdcchMaxTargetBlerEnabled', 
        'pdcchCongCtrlParamEnabled', 'upperLayerIndR15Usage', 'diffPdcchMaxTargetBlerThres', 
        'pdcchMaxTargetBlerHigh', 'pdcchOutLoopInitAdjCong', 'pdcchOutLoopInitAdjPCellCong', 
        'primaryUpperLayerInd', 'endcB1MeasGapConfig', 'lbTpNonQualFraction', 
        'lbTpRankThreshMin', # Los atributos 'noConsecutiveSubframes', 'prsPeriod', 'transmissionMode' se omiten aquí pues ya van en el CRN.
    ]
    
    set_simple_commands = []
    
    for attr_rnd in set_simple_attributes:
        value = safe_get_value(df, mo_name, attr_rnd, cell_column)
        if value is not None and str(value).strip() != '':
            if isinstance(value, str) and value.lower() in ('true', 'false'):
                value = value.lower()
            
            set_simple_commands.append(f"set ENodeBFunction=1,EUtranCellFDD={cell_mo_name} {attr_rnd} {value}")
            
    # --- Casos especiales de SET que requieren comandos separados ---
    
    # 1. eutranCellCoverage: TRES SETs separados (posCellBearing, posCellOpeningAngle, posCellRadius)
    # Se genera un comando SET por cada sub-atributo para imitar el formato del ejemplo
    for sub_attr in ['posCellBearing', 'posCellOpeningAngle', 'posCellRadius']:
        rnd_attr = f'eutranCellCoverage_{sub_attr}' 
        value = safe_get_value(df, mo_name, rnd_attr, cell_column)
        if value is not None and str(value).strip() != '':
             set_simple_commands.append(f"set ENodeBFunction=1,EUtranCellFDD={cell_mo_name} eutranCellCoverage {sub_attr}={value}")

    # 2. eutranCellPolygon: CONSOLIDACIÓN DE FILAS SEPARADAS DE RND
    
    # Obtener valores de latitud (L) y longitud (G) de las filas separadas
    lat_values_str = safe_get_value(df, mo_name, 'eutranCellPolygon_cornerLatitude', cell_column)
    long_values_str = safe_get_value(df, mo_name, 'eutranCellPolygon_cornerLongitude', cell_column)

    # --- Lógica de Fallback y Consolidación ---
    
    DEFAULT_POLYGON_VALUE = "cornerLatitude=0,cornerLongitude=0;cornerLatitude=0,cornerLongitude=0;cornerLatitude=0,cornerLongitude=0;cornerLatitude=0,cornerLongitude=0;cornerLatitude=0,cornerLongitude=0;cornerLatitude=0,cornerLongitude=0;cornerLatitude=0,cornerLongitude=0;cornerLatitude=0,cornerLongitude=0;cornerLatitude=0,cornerLongitude=0;cornerLatitude=0,cornerLongitude=0;cornerLatitude=0,cornerLongitude=0;cornerLatitude=0,cornerLongitude=0;cornerLatitude=0,cornerLongitude=0;cornerLatitude=0,cornerLongitude=0;cornerLatitude=0,cornerLongitude=0"
    
    eutran_poly_value = None
    
    if lat_values_str and long_values_str:
        # Limpiar y dividir los valores (asumiendo que están separados por espacios)
        lat_list = lat_values_str.split()
        long_list = long_values_str.split()
        
        # Combinar en el formato requerido: Lat=X,Long=Y;...
        if len(lat_list) == len(long_list):
            polygon_parts = [
                f"cornerLatitude={lat},cornerLongitude={long}"
                for lat, long in zip(lat_list, long_list)
            ]
            eutran_poly_value = ";".join(polygon_parts)
            
    # Usar el valor consolidado o el valor por defecto si la extracción falló
    final_eutran_poly_value = eutran_poly_value if eutran_poly_value else DEFAULT_POLYGON_VALUE
    
    if final_eutran_poly_value:
        set_simple_commands.append(f"set ENodeBFunction=1,EUtranCellFDD={cell_mo_name} eutranCellPolygon {final_eutran_poly_value}")
    
    set_simple_content = "\n".join(set_simple_commands) + "\n"
    
    return creation_block, set_simple_content, cell_mo_name


# ====================================================================
# === 5. FUNCIÓN PRINCIPAL ===
# ====================================================================

def generate_cell_config_mos(nemonico: str, df_cell_carrier: pd.DataFrame) -> str:
    """
    Genera el contenido MOS (MML) para la configuración de las celdas EUtranCellFDD,
    incluyendo los comandos de cierre al final.
    """
    nemonico_upper = nemonico.upper()
    current_date = datetime.datetime.now().strftime("%Y-%m-%d") # Usar solo fecha para el encabezado

    cell_columns = [col for col in df_cell_carrier.columns if col not in ['MO', 'Atributo']]
    
    # --- Encabezado Solicitado ---
    full_script = (
        f"// ====================================================================\n"
        f"// == ARCHIVO PARA CREACIÓN DE CELDAS\n"
        f"// ====================================================================\n"
        f"// \n"
        f"// AUTOR: Piero Ledesma\n"
        f"// FECHA DE SCRIPT: {current_date}\n"
        f"// NEMONICO: {nemonico_upper}\n"
        f"// \n"
        f"// --------------------------------------------------------------------\n\n"
    )

    for cell_column in cell_columns:
        creation_block, set_simple_content, cell_mo_name = generate_creation_and_simple_sets(
            df_cell_carrier, cell_column
        )
        
        if cell_mo_name:
            full_script += f"\n\n// #################################################\n"
            full_script += f"// #### Comandos para {cell_mo_name} ({cell_column}) ####\n"
            full_script += f"// #################################################\n\n"
            
            # --- 1. COMANDOS DE CREACIÓN (3 VERSIONES) ---
            full_script += creation_block
            
            # --- 2. SETS SIMPLES Y CASOS ESPECIALES (Coverage/Polygon) ---
            full_script += set_simple_content
            
            # --- 3. SETS ESTRUCTURADOS CONSOLIDABLES CON TIPO (changeNotification, mappingInfo) ---
            
            # changeNotification 
            full_script += generate_consolidated_set_struct_commands(
                df_cell_carrier, cell_column, 'changeNotification', True
            )
            
            # mappingInfo 
            full_script += generate_consolidated_set_struct_commands(
                df_cell_carrier, cell_column, 'mappingInfo', True
            )

            # --- 4. SETS ESTRUCTURADOS CONSOLIDABLES SIN TIPO (LoadBasedCaMsrThr) ---

            # LoadBasedCaMsrThr (Utiliza ordenamiento especial)
            full_script += generate_consolidated_set_struct_commands(
                df_cell_carrier, cell_column, 'LoadBasedCaMsrThr', False
            )
            
            # --- 5. SETS ESTRUCTURADOS INDIVIDUALES SIN TIPO (SIB3) ---
            
            # systemInformationBlock3 (Requiere comandos individuales)
            full_script += generate_individual_set_struct_commands(
                df_cell_carrier, cell_column, 'systemInformationBlock3'
            )
            
            full_script += "\n\n"
    
    # --- Comandos de Cierre Solicitados ---
    full_script += f"cvms EUtranCellFDD_Pledesma\n"
    full_script += f"confb-\n"
    full_script += f"s-\n"
    
    return full_script