import datetime
import pandas as pd
from typing import Dict, Any, List, Union
from io import BytesIO
import re

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

# Definición de atributos de RetSubUnit que deben extraerse
RETSUBUNIT_ATTRIBUTES = [
    'electricalAntennaTilt',
    'iuantAntennaBearing',
    'iuantSectorId',
    'userLabel'
]

# Definición de atributos de SectorEquipmentFunction que deben extraerse
SEF_ATTRIBUTES = [
    'rfBranchRef', 
    'userLabel', 
    'administrativeState'
]

# Definición de atributos de SectorCarrier que deben extraerse
SC_ATTRIBUTES = [
    'noOfRxAntennas',
    'noOfTxAntennas',
    'prsEnabled',
    'ulForcedTimingAdvanceCommand',
    'txPowerPersistentLock',
    'configuredMaxTxPower',
    'maximumTransmissionPower', 
    'sectorFunctionRef' 
]


# ====================================================================
# === FUNCIONES INTERNAS DE SOPORTE (EXTRACTION) ===
# ====================================================================

def _read_rnd_sheet(rnd_file: Any, sheet_name: str) -> Union[pd.DataFrame, None]:
    """Helper para leer una hoja de Excel del RND."""
    if rnd_file is None:
        return None
    try:
        # Volvemos a usar la opción de leer con header=0
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
        rru_name_row_candidates = rfport_rows[
            rfport_rows['Atributo'].astype(str).str.strip() == 'Equipment=1,FieldReplaceableUnit='
        ]

        if rru_name_row_candidates.empty:
            print("// Error: No se encontró la fila de nombres de RRU ('Equipment=1,FieldReplaceableUnit=')")
            return {}
        
        rru_name_row = rru_name_row_candidates.iloc[0]

        # 2. Mapeo de columnas de RRU (columna de Pandas a nombre de RRU)
        rru_col_to_name_map = {}
        rru_names_set = set() 
        
        for i in range(first_value_col_index, len(df_eq.columns)):
            rru_name_full = str(rru_name_row.iloc[i]).strip()
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
        port_name_rows = rfport_rows[rfport_rows['Atributo'].astype(str).str.strip() == 'RfPort=']
        if port_name_rows.empty: 
            print("// Error: No se encontró la fila de nombres de puerto ('RfPort=')")
            return {}
        port_name_row = port_name_rows.iloc[0]

        for attr in RFPORT_ATTRIBUTES:
            attr_rows = rfport_rows[rfport_rows['Atributo'].str.contains(attr, na=False, regex=False)]
            
            for _, attr_row in attr_rows.iterrows():
                
                for col_index in range(first_value_col_index, len(df_eq.columns)):
                    col_name = df_eq.columns[col_index]
                    rru_name = rru_col_to_name_map.get(col_name)

                    if not rru_name: continue

                    port_id = str(port_name_row.iloc[col_index]).strip()
                    
                    if not port_id or port_id not in ['A', 'B', 'C', 'D', 'R']: continue

                    value = str(attr_row.get(col_name)).strip()

                    if port_id not in rru_config[rru_name]:
                        rru_config[rru_name][port_id] = {}
                        
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

def _extract_antenna_config(rnd_file: Any) -> Dict[str, Any]:
    """
    Extrae la configuración de AntennaUnitGroup, AntennaNearUnit, RetSubUnit,
    AntennaSubunit, AuPort y RfBranch.
    """
    df_eq = _read_rnd_sheet(rnd_file, 'Equipment-Configuration')
    if df_eq is None:
        return {}

    antenna_config = {
        'au_groups': {},
        'antenna_subunits': {},
        'rf_branches': {}
    }
    
    try:
        atributo_index = df_eq.columns.get_loc('Atributo')
        first_value_col_index = atributo_index + 1
        
        # --- 1. Extracción de AntennaUnitGroup, AntennaUnit y Tilts (para AuGroups) ---
        au_group_row = df_eq[
            (df_eq['MO'] == 'AntennaUnit') & 
            (df_eq['Atributo'].astype(str).str.strip() == 'Equipment=1,AntennaUnitGroup=')
        ].iloc[0]
        
        au_tilt_row = df_eq[
            (df_eq['MO'] == 'AntennaUnit') & 
            (df_eq['Atributo'].astype(str).str.strip() == 'mechanicalAntennaTilt')
        ].iloc[0]

        au_unit_row = df_eq[
            (df_eq['MO'] == 'AntennaUnit') & 
            (df_eq['Atributo'].astype(str).str.strip() == 'AntennaUnit=')
        ].iloc[0]

        au_groups = {}
        for i in range(first_value_col_index, len(df_eq.columns)):
            group_id = str(au_group_row.iloc[i]).strip()
            tilt = str(au_tilt_row.iloc[i]).strip()
            unit_id = str(au_unit_row.iloc[i]).strip()
            
            if group_id and group_id.isdigit():
                if group_id not in au_groups:
                    au_groups[group_id] = {
                        'tilt': tilt if tilt else '0',
                        'unit_id': unit_id if unit_id else '1',
                        'near_units': {}
                    }
        antenna_config['au_groups'] = au_groups

        # --- 2. Extracción de RetSubUnit / AntennaNearUnit (para AuGroups) ---
        ret_subunit_rows = df_eq[df_eq['MO'] == 'RetSubUnit'].copy()
        
        ret_group_row = ret_subunit_rows[
            ret_subunit_rows['Atributo'].astype(str).str.strip() == 'Equipment=1,AntennaUnitGroup='
        ].iloc[0]

        ret_near_unit_row = ret_subunit_rows[
            ret_subunit_rows['Atributo'].astype(str).str.strip() == 'AntennaNearUnit='
        ].iloc[0]

        for i in range(first_value_col_index, len(df_eq.columns)):
            current_group = str(ret_group_row.iloc[i]).strip()
            current_near_unit = str(ret_near_unit_row.iloc[i]).strip()
            
            if current_group and current_near_unit and current_group in au_groups and current_near_unit.isdigit():
                
                ret_id_row = ret_subunit_rows[
                    ret_subunit_rows['Atributo'].astype(str).str.strip() == 'RetSubUnit='
                ].iloc[0]
                ret_id = str(ret_id_row.iloc[i]).strip()
                
                near_unit_config = {
                    'ret_subunit_attrs': {},
                    'ret_subunit_id': ret_id if ret_id else '1'
                }

                for attr in RETSUBUNIT_ATTRIBUTES:
                    attr_row = ret_subunit_rows[
                        ret_subunit_rows['Atributo'].astype(str).str.strip() == attr
                    ]
                    if not attr_row.empty:
                        value = str(attr_row.iloc[0].iloc[i]).strip()
                        near_unit_config['ret_subunit_attrs'][attr] = value if value else '0' 

                au_groups[current_group]['near_units'][current_near_unit] = near_unit_config

        # --- 3. Extracción de AntennaSubunit y retSubunitRef (para AuPorts) ---
        
        asub_rows = df_eq[df_eq['MO'] == 'AntennaSubunit'].copy()
        
        asub_group_row = asub_rows[
            asub_rows['Atributo'].astype(str).str.strip() == 'Equipment=1,AntennaUnitGroup='
        ].iloc[0]
        
        asub_id_row = asub_rows[
            asub_rows['Atributo'].astype(str).str.strip() == 'AntennaSubunit='
        ].iloc[0]

        asub_ref_row = asub_rows[
            asub_rows['Atributo'].astype(str).str.strip() == 'retSubunitRef'
        ].iloc[0]

        antenna_subunits = {}
        for i in range(first_value_col_index, len(df_eq.columns)):
            group_id = str(asub_group_row.iloc[i]).strip()
            asub_id = str(asub_id_row.iloc[i]).strip()
            ref_value = str(asub_ref_row.iloc[i]).strip()

            if group_id and group_id.isdigit() and asub_id and asub_id.isdigit():
                
                # Ejemplo de Key: '1-1' (AUG ID - ASUB ID)
                key = f"{group_id}-{asub_id}"
                
                if group_id not in antenna_subunits:
                    antenna_subunits[group_id] = {}
                    
                antenna_subunits[group_id][asub_id] = {
                    'ret_ref': ref_value,
                }
        
        antenna_config['antenna_subunits'] = antenna_subunits

        # --- 4. Extracción de RfBranch (para conexiones) ---
        
        rfbranch_rows = df_eq[df_eq['MO'] == 'RfBranch'].copy()
        
        rfb_group_row = rfbranch_rows[
            rfbranch_rows['Atributo'].astype(str).str.strip() == 'Equipment=1,AntennaUnitGroup='
        ].iloc[0]
        
        rfb_id_row = rfbranch_rows[
            rfbranch_rows['Atributo'].astype(str).str.strip() == 'RfBranch='
        ].iloc[0]

        rfb_auport_ref_row = rfbranch_rows[
            rfbranch_rows['Atributo'].astype(str).str.strip() == 'auPortRef'
        ].iloc[0]
        
        rfb_rfport_ref_row = rfbranch_rows[
            rfbranch_rows['Atributo'].astype(str).str.strip() == 'rfPortRef'
        ].iloc[0]

        rf_branches = {}
        for i in range(first_value_col_index, len(df_eq.columns)):
            group_id = str(rfb_group_row.iloc[i]).strip()
            rfb_id = str(rfb_id_row.iloc[i]).strip()
            auport_ref_full = str(rfb_auport_ref_row.iloc[i]).strip()
            rfport_ref_full = str(rfb_rfport_ref_row.iloc[i]).strip()

            if group_id and group_id.isdigit() and rfb_id and rfb_id.isdigit() and auport_ref_full and rfport_ref_full:
                
                # Extraer AuPort ID: Se asume que siempre es la última parte del ref (AuPort=X)
                auport_id = auport_ref_full # Almacenamos el ID de AuPort (1, 2, 3 o 4)
                
                if group_id not in rf_branches:
                    rf_branches[group_id] = {}
                    
                rf_branches[group_id][rfb_id] = {
                    'au_port_id': auport_id,
                    'rf_port_ref': rfport_ref_full
                }
        
        antenna_config['rf_branches'] = rf_branches


    except (KeyError, IndexError, ValueError) as e:
        print(f"Error crítico al procesar datos de Antenas/Branches: {e}")
        return {}

    return antenna_config

def _extract_sef_config(rnd_file: Any) -> Dict[str, Dict[str, str]]:
    """
    Extrae la configuración de SectorEquipmentFunction de la hoja 'Equipment-Configuration'.
    """
    df_eq = _read_rnd_sheet(rnd_file, 'Equipment-Configuration')
    if df_eq is None:
        return {}
    
    sef_config = {}
    try:
        sef_rows = df_eq[df_eq['MO'] == 'SectorEquipmentFunction'].copy()
        if sef_rows.empty: return {}
        
        atributo_index = df_eq.columns.get_loc('Atributo')
        first_value_col_index = atributo_index + 1
        
        # Fila donde están los IDs de SectorEquipmentFunction (e.g., 1, 2, 3, 7, 8, 9)
        sef_id_row_candidates = sef_rows[
            sef_rows['Atributo'].astype(str).str.strip() == 'NodeSupport=1,SectorEquipmentFunction='
        ]

        if sef_id_row_candidates.empty:
             print("// Error: No se encontró la fila de IDs de SectorEquipmentFunction.")
             return {}
        
        sef_id_row = sef_id_row_candidates.iloc[0]
        
        # Mapear las columnas a los IDs de SEF
        sef_col_to_id_map = {}
        for i in range(first_value_col_index, len(df_eq.columns)):
            sef_id = str(sef_id_row.iloc[i]).strip()
            if sef_id and sef_id.isdigit():
                col_name = df_eq.columns[i]
                sef_col_to_id_map[col_name] = sef_id
                sef_config[sef_id] = {}

        if not sef_col_to_id_map:
            return {}

        # Extraer los atributos para cada SEF
        for attr in SEF_ATTRIBUTES:
            attr_row = sef_rows[sef_rows['Atributo'].astype(str).str.strip() == attr]
            if attr_row.empty: continue
            
            attr_row = attr_row.iloc[0] 
            
            for col_name, sef_id in sef_col_to_id_map.items():
                value = str(attr_row.get(col_name)).strip()
                
                # Asignar valor por defecto si está vacío (ej. administrativeState)
                if not value:
                    if attr == 'administrativeState':
                        value = '1'
                    elif attr == 'rfBranchRef':
                        value = ''
                    elif attr == 'userLabel':
                        value = f'SEF_{sef_id}'
                
                # Manejar el caso especial del RND que termina el userLabel con punto
                if attr == 'userLabel' and value.endswith('.'):
                    value = value[:-1]

                sef_config[sef_id][attr] = value

    except (KeyError, IndexError, ValueError) as e:
        print(f"Error crítico al procesar datos de SectorEquipmentFunction: {e}")
        return {}
        
    return sef_config

def _extract_sector_carrier_config(rnd_file: Any) -> Dict[str, Dict[str, str]]:
    """
    Extrae la configuración de SectorCarrier de la hoja 'Cell-Carrier'.
    """
    df_cc = _read_rnd_sheet(rnd_file, 'Cell-Carrier')
    if df_cc is None:
        return {}

    sc_config = {}
    try:
        sc_rows = df_cc[df_cc['MO'] == 'SectorCarrier'].copy()
        if sc_rows.empty: return {}

        atributo_index = df_cc.columns.get_loc('Atributo')
        first_value_col_index = atributo_index + 1

        # Fila donde están los IDs de SectorCarrier (e.g., 1, 2, 3, 7, 8, 9, 17, 18, 19)
        sc_id_row_candidates = sc_rows[
            sc_rows['Atributo'].astype(str).str.strip() == 'ENodeBFunction=1,SectorCarrier='
        ]

        if sc_id_row_candidates.empty:
            print("// Error: No se encontró la fila de IDs de SectorCarrier.")
            return {}

        sc_id_row = sc_id_row_candidates.iloc[0]

        # Mapear las columnas a los IDs de SectorCarrier
        sc_col_to_id_map = {}
        for i in range(first_value_col_index, len(df_cc.columns)):
            sc_id = str(sc_id_row.iloc[i]).strip()
            if sc_id and sc_id.isdigit():
                col_name = df_cc.columns[i]
                sc_col_to_id_map[col_name] = sc_id
                sc_config[sc_id] = {}

        if not sc_col_to_id_map:
            return {}

        # Extraer los atributos para cada SectorCarrier
        for attr in SC_ATTRIBUTES:
            attr_row = sc_rows[sc_rows['Atributo'].astype(str).str.strip() == attr]
            if attr_row.empty: continue

            attr_row = attr_row.iloc[0] 

            for col_name, sc_id in sc_col_to_id_map.items():
                value = str(attr_row.get(col_name)).strip()

                sc_config[sc_id][attr] = value

    except (KeyError, IndexError, ValueError) as e:
        print(f"Error crítico al procesar datos de SectorCarrier: {e}")
        return {}

    return sc_config

# ====================================================================
# === FUNCION PRINCIPAL DE GENERACIÓN (.MOS) ===
# ====================================================================

def generar_hardware_mos(nemonico: str, wsh_data: Dict[str, str], trama: str, rnd_node_file: Any) -> str:
    """
    Genera el contenido MOS (MML) unificado con SCTP, MMEs, RRU/RfPorts, Antenas, RiPort BB, SEF, SC y RiLinks.
    """
    nemonico_upper = nemonico.upper()
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Obtener la configuración necesaria
    sctp_profile_commands = _extract_sctp_profile(rnd_node_file)
    mme_full_config = _extract_mme_config(rnd_node_file)
    rru_full_config = _extract_rfport_config(rnd_node_file)
    antenna_full_config = _extract_antenna_config(rnd_node_file)
    sef_full_config = _extract_sef_config(rnd_node_file)
    sc_full_config = _extract_sector_carrier_config(rnd_node_file) 
    
    # --- Variables Dinámicas (WSH Report) ---
    ip_address = f"{wsh_data.get('IP_TRAFICO_LTE', '0.0.0.0')}/{wsh_data.get('MASK', '26')}"
    next_hop = wsh_data.get('DGW_TRAFICO_LTE', '0.0.0.0')
    vlan_id = wsh_data.get('VLAN_LTE', '1404')
    trama_port = trama
    
    # --- 1. FIRMA Y COMENTARIO INICIAL ---
    signature = f"""
// ====================================================================
// == ARCHIVO PARA CONFIGURACIÓN DE TRASNPORT Y HW
// ====================================================================
// 
// AUTOR: Piero Ledesma
// FECHA DE SCRIPT: {current_date}
// NEMONICO: {nemonico_upper}
// 
// --------------------------------------------------------------------


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
    
    # --- 3. TERMPOINTTOMME ---
    separator_tpmme = """
// #############################################
// ####        Creación TermPointToMme        ####
// #############################################
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

    
    # --- 4. RRU + RFPORT ---

    separator_rru = """
// #############################################
// ####      Creación de RRUs + Port        ####
// #############################################
"""
    rru_script = ""

    if rru_full_config:
        rru_names_sorted = sorted(rru_full_config.keys())
        
        for rru_name in rru_names_sorted:
            ports_config = rru_full_config[rru_name]
            
            # 4a. Creación y deb de la RRU (FieldReplaceableUnit)
            rru_script += f"""
cr Equipment=1,FieldReplaceableUnit={rru_name}
deb Equipment=1,FieldReplaceableUnit={rru_name}
"""
            
            # 4b. Configuración dinámica de RfPort
            ports_sorted = sorted(ports_config.keys())

            for port_id in ports_sorted:
                attr_data = ports_config[port_id]
                
                rru_script += f"\ncr Equipment=1,FieldReplaceableUnit={rru_name},RfPort={port_id}"

                if port_id != 'R':
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
                else:
                    # El puerto R solo puede tener userLabel
                    user_label = attr_data.get('userLabel', '')
                    if user_label:
                        rru_script += f"\nset FieldReplaceableUnit={rru_name},RfPort={port_id} userLabel {user_label}"
    else:
        rru_script = "\n// No se encontraron RRUs para configurar en la hoja Equipment-Configuration."


    # --- 5. COMANDOS DE ANTENA Y CONEXIÓN (DINAMICO) ---
    
    separator_antenna = """
// #############################################
// ####    Creación de AntennaUnitGroup/RET   ####
// #############################################
"""
    separator_auport = """
// #############################################
// ####        Creación de AuPort/RfBranch  ####
// #############################################
"""
    antenna_script = ""
    auport_script = ""

    if antenna_full_config and 'au_groups' in antenna_full_config:
        au_groups = antenna_full_config['au_groups']
        antenna_subunits = antenna_full_config['antenna_subunits']
        rf_branches = antenna_full_config['rf_branches']
        
        # 5a. Creación de AntennaUnitGroup, AntennaUnit y AntennaNearUnit/RetSubUnit
        sorted_au_group_ids = sorted([k for k in au_groups.keys() if k.isdigit()], key=lambda x: int(x))
        
        for group_id in sorted_au_group_ids:
            group_data = au_groups[group_id]
            unit_id = group_data['unit_id']
            tilt = group_data['tilt']
            near_units = group_data['near_units']

            # CR de AntennaUnitGroup
            antenna_script += f"\ncr Equipment=1,AntennaUnitGroup={group_id}"
            
            # CR y SET de AntennaUnit
            antenna_script += f"""
cr Equipment=1,AntennaUnitGroup={group_id},AntennaUnit={unit_id}
set Equipment=1,AntennaUnitGroup={group_id},AntennaUnit={unit_id} mechanicalAntennaTilt {tilt}
"""

            # CR y SET de AntennaNearUnit + RetSubUnit
            sorted_near_unit_ids = sorted([k for k in near_units.keys() if k.isdigit()], key=lambda x: int(x))

            for near_unit_id in sorted_near_unit_ids:
                nu_data = near_units[near_unit_id]
                ret_attrs = nu_data['ret_subunit_attrs']
                ret_id = nu_data['ret_subunit_id']

                # CR de AntennaNearUnit
                antenna_script += f"""
cr Equipment=1,AntennaUnitGroup={group_id},AntennaNearUnit={near_unit_id}
0
"""
                # CR y SET de RetSubUnit
                antenna_script += f"cr Equipment=1,AntennaUnitGroup={group_id},AntennaNearUnit={near_unit_id},RetSubUnit={ret_id}"

                # Aplicar atributos de RetSubUnit
                if ret_attrs:
                    for attr, value in ret_attrs.items():
                        antenna_script += f"\nset AntennaUnitGroup={group_id},AntennaNearUnit={near_unit_id},RetSubUnit={ret_id} {attr} {value}"
                
                antenna_script += "\n"


            # 5b. Creación de AuPort y RfBranch (Se mantiene dentro del loop de Group ID)
            
            # --- 5b.1 AntennaSubunit y AuPorts ---
            if group_id in antenna_subunits:
                sorted_asub_ids = sorted([k for k in antenna_subunits[group_id].keys() if k.isdigit()], key=lambda x: int(x))
                
                for asub_id in sorted_asub_ids:
                    asub_data = antenna_subunits[group_id][asub_id]
                    ret_ref = asub_data['ret_ref']
                    
                    # CR AntennaSubunit
                    auport_script += f"\ncr Equipment=1,AntennaUnitGroup={group_id},AntennaUnit={unit_id},AntennaSubunit={asub_id}"
                    
                    # Si ASUBID es 1, creamos los 4 AuPorts (asumimos 4 AuPorts solo para el primer AntennaSubunit)
                    if asub_id == '1':
                        for auport_id in ['1', '2', '3', '4']:
                            auport_script += f"\ncr Equipment=1,AntennaUnitGroup={group_id},AntennaUnit={unit_id},AntennaSubunit={asub_id},AuPort={auport_id}"
                    
                    # SET retSubunitRef
                    auport_script += f"\nset Equipment=1,AntennaUnitGroup={group_id},AntennaUnit={unit_id},AntennaSubunit={asub_id} retSubunitRef {ret_ref}"
                    auport_script += "\n" # Espacio entre ASUBs
            
            # --- 5b.2 RfBranch ---
            if group_id in rf_branches:
                # Determinar el nombre de RRU por defecto para este grupo (AUG=N -> RRU-N)
                rru_name_for_group = f"RRU-{group_id}"
                
                sorted_rfb_ids = sorted([k for k in rf_branches[group_id].keys() if k.isdigit()], key=lambda x: int(x))
                
                for rfb_id in sorted_rfb_ids:
                    rfb_data = rf_branches[group_id][rfb_id]
                    au_port_id = rfb_data['au_port_id']
                    rf_port_ref = rfb_data['rf_port_ref']
                    
                    # --- CORRECCIÓN: Asegurar el formato completo para rfPortRef ---
                    final_rf_port_ref = rf_port_ref
                    
                    # 1. Verificar si el valor ya es un MO Reference completo
                    if not re.search(r'(FieldReplaceableUnit|FRU)=', final_rf_port_ref, re.IGNORECASE):
                        # No es una referencia MO completa. Intentar reconstruir.
                        
                        # 1.1 Intentar parsear si hay coma (RRU-X,Y)
                        if ',' in final_rf_port_ref:
                            # Caso: 'RRU-3,D' o '3,D'
                            parts = [p.strip() for p in final_rf_port_ref.split(',', 1)]
                            
                            rru_part = parts[0]
                            port_id = parts[1]
                            
                            # Si la parte RRU es solo el número, usar ese número. Si ya es 'RRU-', usarlo.
                            if rru_part.isdigit():
                                rru_name_to_use = f"RRU-{rru_part}"
                            elif rru_part.upper().startswith('RRU-'):
                                rru_name_to_use = rru_part
                            else:
                                # Fallback al nombre de RRU por grupo
                                rru_name_to_use = rru_name_for_group
                                
                            final_rf_port_ref = f"FieldReplaceableUnit={rru_name_to_use},RfPort={port_id}"
                        
                        # 1.2 Si es solo la letra del Puerto (A, B, C, D) o DATA_1
                        elif final_rf_port_ref.upper() in ['A', 'B', 'C', 'D', 'R', 'DATA_1']:
                            port_id = final_rf_port_ref
                            final_rf_port_ref = f"FieldReplaceableUnit={rru_name_for_group},RfPort={port_id}"
                        
                        # Si no coincide con ningún patrón, se mantiene el valor original (caso de borde)
                        
                    # --- FIN CORRECCIÓN ---


                    # CR RfBranch
                    auport_script += f"\ncr Equipment=1,AntennaUnitGroup={group_id},RfBranch={rfb_id}"
                    
                    auport_value = au_port_id
                    auport_ref = f"Equipment=1,AntennaUnitGroup={group_id},AntennaUnit={unit_id},AntennaSubunit=1,AuPort={auport_value}"
                    
                    # SET auPortRef
                    auport_script += f"\nset Equipment=1,AntennaUnitGroup={group_id},RfBranch={rfb_id} auPortRef {auport_ref}"
                    
                    # SET rfPortRef (USANDO EL VALOR CORREGIDO)
                    auport_script += f"\nset Equipment=1,AntennaUnitGroup={group_id},RfBranch={rfb_id} rfPortRef {final_rf_port_ref}"
                    auport_script += "\n" # Espacio entre Branches

    else:
        antenna_script = "\n// No se encontraron datos de Antenas para configurar en la hoja Equipment-Configuration."
        auport_script = "\n// No se encontraron datos de AuPort/RfBranch para configurar en la hoja Equipment-Configuration."


    # --- 6. RIPORT BASEBAND (ESTÁTICO) ---
    separator_riport = """
// #############################################
// ####        Creación RiPort Baseband         ####
// #############################################
"""
    riport_bb_script = """
cr Equipment=1,FieldReplaceableUnit=BB-1,RiPort=A
cr Equipment=1,FieldReplaceableUnit=BB-1,RiPort=B
cr Equipment=1,FieldReplaceableUnit=BB-1,RiPort=C
cr Equipment=1,FieldReplaceableUnit=BB-1,RiPort=D
cr Equipment=1,FieldReplaceableUnit=BB-1,RiPort=E
cr Equipment=1,FieldReplaceableUnit=BB-1,RiPort=F
"""

    # --- 7. SECTOREQUIPMENTFUNCTION (DINÁMICO) ---
    separator_sef = """
// #############################################
// #### Creación SectorEquipmentFunction  ####
// #############################################
"""
    sef_script = ""
    if sef_full_config:
        # Ordenar por ID numérico (1, 2, 3, 7, 8, 9...)
        sorted_sef_ids = sorted([k for k in sef_full_config.keys() if k.isdigit()], key=lambda x: int(x))
        
        for sef_id in sorted_sef_ids:
            attr_data = sef_full_config[sef_id]
            
            rf_branch_ref = attr_data.get('rfBranchRef', '')
            user_label = attr_data.get('userLabel', f'SEF_{sef_id}')
            admin_state = attr_data.get('administrativeState', '1')

            sef_script += f"""
cr NodeSupport=1,SectorEquipmentFunction={sef_id}
set NodeSupport=1,SectorEquipmentFunction={sef_id} rfBranchRef {rf_branch_ref}
set NodeSupport=1,SectorEquipmentFunction={sef_id} userLabel {user_label}
set NodeSupport=1,SectorEquipmentFunction={sef_id} administrativeState {admin_state}
"""
    else:
        sef_script = "\n// No se encontraron datos de SectorEquipmentFunction para configurar en la hoja Equipment-Configuration."

    
    # --- 8. SECTORCARRIER (DINÁMICO) ---
    separator_sc = """
// #############################################
// ####        Creación SectorCarrier         ####
// #############################################
"""
    sc_script = ""
    if sc_full_config:
        # Ordenar por ID numérico (1, 2, 3, 7, 8, 9, 17, 18, 19...)
        sorted_sc_ids = sorted([k for k in sc_full_config.keys() if k.isdigit()], key=lambda x: int(x))
        
        for sc_id in sorted_sc_ids:
            attr_data = sc_full_config[sc_id]
            
            # Atributo SectorFunctionRef (para el CR)
            sector_function_ref = attr_data.get('sectorFunctionRef', '')
            
            # Atributos para los SETs
            no_rx = attr_data.get('noOfRxAntennas', '4')
            no_tx = attr_data.get('noOfTxAntennas', '4')
            max_tx_power = attr_data.get('configuredMaxTxPower', '100000') 
            ul_ta_cmd = attr_data.get('ulForcedTimingAdvanceCommand', '0')
            tx_persistent_lock = attr_data.get('txPowerPersistentLock', 'false')
            prs_enabled = attr_data.get('prsEnabled', 'true')
            
            sc_script += f"""
cr ENodeBFunction=1,SectorCarrier={sc_id}
SectorEquipmentFunction={sector_function_ref}
set SectorCarrier={sc_id}$ noOfRxAntennas {no_rx}
set SectorCarrier={sc_id}$ noOfTxAntennas {no_tx}
set SectorCarrier={sc_id}$ configuredMaxTxPower {max_tx_power}
set SectorCarrier={sc_id}$ ulForcedTimingAdvanceCommand {ul_ta_cmd}
set SectorCarrier={sc_id}$ txPowerPersistentLock {tx_persistent_lock}
set SectorCarrier={sc_id}$ prsEnabled {prs_enabled}
"""
    else:
        sc_script = "\n// No se encontraron datos de SectorCarrier en la hoja Cell-Carrier para configurar."

    
    # --- 9. CREACIÓN RILINK (ESTÁTICO A-B-C) ---
    separator_rilink = """
// #############################################
// ####          Creación RiLink            ####
// #############################################
"""
    # Esta configuración es la solicitada como "Configuración Basica A-B-C"
    rilink_script = """
crn Equipment=1,RiLink=1
riPortRef1 FieldReplaceableUnit=RRU-1,RiPort=DATA_1
riPortRef2 FieldReplaceableUnit=BB-1,RiPort=A
transportType 0
end

crn Equipment=1,RiLink=2
riPortRef1 FieldReplaceableUnit=RRU-2,RiPort=DATA_1
riPortRef2 FieldReplaceableUnit=BB-1,RiPort=B
transportType 0
end

crn Equipment=1,RiLink=3
riPortRef1 FieldReplaceableUnit=RRU-3,RiPort=DATA_1
riPortRef2 FieldReplaceableUnit=BB-1,RiPort=C
transportType 0
end
"""
    
    # --- 10. ENSAMBLAJE FINAL ---
    final_script = f"""
{signature}
{transport_script}
{separator_tpmme}
{mme_config_script}
{separator_rru}
{rru_script}

{separator_antenna}
{antenna_script}

{separator_auport}
{auport_script}

{separator_riport}
{riport_bb_script}

{separator_sef}
{sef_script}

{separator_sc}
{sc_script}

{separator_rilink}
{rilink_script}

cvms HW_Pledesma

confb-
s-
"""
    
    return final_script