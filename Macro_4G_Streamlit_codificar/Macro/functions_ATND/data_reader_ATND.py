
# =====================================================================
# data_reader_ATND.py - Lectura de archivos ATND Excel
# =====================================================================

import pandas as pd
from typing import Dict, Tuple, Optional, Any

# =====================================================================
# FUNCIÓN PRINCIPAL DE LECTURA
# =====================================================================

def leer_atnd_completo(atnd_file: Any) -> Tuple[Optional[Dict[str, pd.DataFrame]], Optional[str]]:
    """
    Lee todas las hojas del archivo ATND Excel y retorna un diccionario.
    
    Args:
        atnd_file: Archivo Excel ATND cargado (puede ser file-like object o path)
    
    Returns:
        Tuple[Dict, str]: (Diccionario con DataFrames por hoja, mensaje de error)
        - Si tiene éxito: (dict_data, None)
        - Si falla: (None, mensaje_error)
    """
    try:
        # Leer el archivo Excel
        xls = pd.ExcelFile(atnd_file)
        
        # Diccionario para almacenar todas las hojas
        atnd_data = {}
        
        # Lista de hojas esperadas en un ATND
        hojas_esperadas = [
            'Summary',
            'ATND Transport Licensing',
            'ATND Transport Features',
            'DscpDscpMap',
            'DscpPcpMap',
            'PcpPcpMap',
            'NtpFrequencySync',
            'BoundaryOrdinaryClock',
            'PtpBcOcPort',
            'Synchronization',
            'RadioEquipmentClockReference',
            'SfpModule',
            'Ethernet_Port',
            'Router',
            'VlanPort',
            'TwampREsponder',
            'Shaper',
            'SchedulerDwrr',
            'PcpToQueueMap',
            'DscpToPCPMap'
        ]
        
        # Leer todas las hojas disponibles
        for sheet_name in xls.sheet_names:
            try:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                
                # Limpiar nombres de columnas (eliminar espacios extra)
                df.columns = df.columns.str.strip()
                
                # Guardar en el diccionario con el nombre de la hoja
                atnd_data[sheet_name] = df
                
                print(f"✓ Hoja '{sheet_name}' leída correctamente: {len(df)} filas, {len(df.columns)} columnas")
                
            except Exception as e:
                print(f"⚠ Advertencia al leer hoja '{sheet_name}': {e}")
                # Continuar con las demás hojas
                continue
        
        if not atnd_data:
            return None, "No se pudieron leer hojas del archivo ATND"
        
        print(f"\n✓ Total de hojas leídas: {len(atnd_data)}")
        return atnd_data, None
        
    except Exception as e:
        error_msg = f"Error al leer archivo ATND: {str(e)}"
        print(f"✗ {error_msg}")
        return None, error_msg


# =====================================================================
# FUNCIONES AUXILIARES PARA EXTRAER DATOS ESPECÍFICOS
# =====================================================================

def get_summary_data(atnd_data: Dict[str, pd.DataFrame]) -> Optional[Dict[str, Any]]:
    """
    Extrae datos de la hoja Summary.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        Diccionario con datos del summary o None
    """
    if 'Summary' not in atnd_data:
        return None
    
    df = atnd_data['Summary']
    if df.empty:
        return None
    
    # Obtener la primera fila (asumiendo que hay un solo sitio)
    row = df.iloc[0]
    
    summary = {
        'Site': str(row.get('Site', '')),
        'Nombre': str(row.get('Nombre', '')),
        'ATND_Version': str(row.get('ATND Version', '')),
        'SW_Version': str(row.get('SW Version', '')),
        'MixMode': str(row.get('MixMode', '')),
        'Arquitectura': str(row.get('Arquitectura', '')),
        'Hardware': str(row.get('Hardware', '')),
        'PE_3G': str(row.get('PE_3G', '')),
        'SFP_RED': str(row.get('SFP RED', '')),
        'SFP_BBU': str(row.get('SFP BBU', '')),
        'PROYECTO': str(row.get('PROYECTO', '')),
        'CUENTA': str(row.get('CUENTA', '')),
        'FECHA': str(row.get('FECHA', ''))
    }
    
    return summary


def get_router_data(atnd_data: Dict[str, pd.DataFrame]) -> Optional[pd.DataFrame]:
    """
    Extrae datos de la hoja Router.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        DataFrame con datos de Router o None
    """
    return atnd_data.get('Router', None)


def get_vlanport_data(atnd_data: Dict[str, pd.DataFrame]) -> Optional[pd.DataFrame]:
    """
    Extrae datos de la hoja VlanPort.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        DataFrame con datos de VlanPort o None
    """
    return atnd_data.get('VlanPort', None)


def get_ethernet_port_data(atnd_data: Dict[str, pd.DataFrame]) -> Optional[pd.DataFrame]:
    """
    Extrae datos de la hoja Ethernet_Port.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        DataFrame con datos de Ethernet_Port o None
    """
    return atnd_data.get('Ethernet_Port', None)


def get_synchronization_data(atnd_data: Dict[str, pd.DataFrame]) -> Optional[pd.DataFrame]:
    """
    Extrae datos de la hoja Synchronization.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        DataFrame con datos de Synchronization o None
    """
    return atnd_data.get('Synchronization', None)


def get_shaper_data(atnd_data: Dict[str, pd.DataFrame]) -> Optional[pd.DataFrame]:
    """
    Extrae datos de la hoja Shaper.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        DataFrame con datos de Shaper o None
    """
    return atnd_data.get('Shaper', None)

def get_scheduler_dwrr_data(atnd_data: Dict[str, pd.DataFrame]) -> Optional[pd.DataFrame]:
    """
    Extrae datos de la hoja SchedulerDwrr.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        DataFrame con datos de SchedulerDwrr o None
    """
    return atnd_data.get('SchedulerDwrr', None)

# ... después de get_scheduler_dwrr_data ...

def get_pcp_to_queue_map_data(atnd_data: Dict[str, pd.DataFrame]) -> Optional[pd.DataFrame]:
    """
    Extrae datos de la hoja PcpToQueueMap.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        DataFrame con datos de PcpToQueueMap o None
    """
    return atnd_data.get('PcpToQueueMap', None)

# En data_reader_ATND.py, después de get_shaper_data:

def get_dscp_to_pcp_map_data(atnd_data: Dict[str, pd.DataFrame]) -> Optional[pd.DataFrame]:
    """
    Extrae datos de la hoja DscpToPCPMap.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        DataFrame con datos de DscpToPCPMap o None
    """
    return atnd_data.get('DscpToPCPMap', None)


# =====================================================================
# FUNCIÓN DE VALIDACIÓN
# =====================================================================

def validar_atnd_data(atnd_data: Dict[str, pd.DataFrame]) -> Tuple[bool, str]:
    """
    Valida que el archivo ATND tenga las hojas mínimas requeridas.
    
    Args:
        atnd_data: Diccionario con todas las hojas del ATND
    
    Returns:
        Tuple[bool, str]: (es_valido, mensaje)
    """
    hojas_requeridas = ['Summary', 'Router', 'VlanPort', 'Ethernet_Port']
    
    hojas_faltantes = []
    for hoja in hojas_requeridas:
        if hoja not in atnd_data:
            hojas_faltantes.append(hoja)
    
    if hojas_faltantes:
        return False, f"Faltan hojas requeridas: {', '.join(hojas_faltantes)}"
    
    return True, "Archivo ATND válido"
