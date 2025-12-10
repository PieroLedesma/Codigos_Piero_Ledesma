# =====================================================================
# queue_generator.py - Generación de script Queue (01)
# =====================================================================

from datetime import datetime
from typing import Optional, Any, Dict, List
import pandas as pd
import numpy as np 
import re
import math
# Importaciones necesarias para acceder a las hojas del Excel
# Se asume que 'get_shaper_data' existe en data_reader_ATND.py
from .data_reader_ATND import get_dscp_to_pcp_map_data, get_ethernet_port_data, get_shaper_data, get_scheduler_dwrr_data, get_pcp_to_queue_map_data


# =====================================================================
# FUNCIÓN HELPER 
# =====================================================================
def get_val(row: pd.Series, col_name: str) -> Optional[str]:
    """
    Obtiene y formatea un valor de forma segura de una fila de DataFrame.
    """
    if col_name in row.index:
        val = row[col_name]
        
        # Si es un valor nulo o None, retorna None
        if pd.isna(val):
            return None
            
        # Si es un string y está vacío después de limpiar espacios, retorna None
        if isinstance(val, str) and not val.strip():
            return None

        # Convertir a string y manejar floats sin decimales
        if isinstance(val, (float, int)):
            # Usar np.isinf para la verificación de valores infinitos
            if not np.isinf(val) and val == int(val):
                return str(int(val))
            return str(val)
            
        return str(val).strip()
    return None


# =====================================================================
# FUNCIÓN DE SECCIÓN: DscpToPCPMap (Lógica de userLabel.1 para mapeo)
# =====================================================================

def generate_dscp_to_pcp_map_section(atnd_data: Dict[str, Any]) -> List[str]:
    """
    Genera la sección DscpToPCPMap del script MML, de forma dinámica.
    """
    mml_output = []
    
    # Obtener DataFrames
    df_dscp = get_dscp_to_pcp_map_data(atnd_data)
    df_eth_port = get_ethernet_port_data(atnd_data)
    
    # Nombres de columnas clave
    ID_COL = 'dscpSetToPCPId'
    DSCP_SET_COL = 'dscpSet'
    PCP_COL = 'pcp'
    
    # ESTRATEGIA: Usar nombres que Pandas asigna a las columnas duplicadas
    USER_LABEL_DEFAULT_COL = 'userLabel'
    USER_LABEL_MAPEO_COL = 'userLabel.1' 

    # --- 1. Validaciones Iniciales y Puerto Ethernet ---
    if df_dscp is None or df_dscp.empty:
        mml_output.append(f"// WARNING: Hoja DscpToPCPMap no encontrada o vacía. Saltando sección.")
        return mml_output
        
    df_temp = df_dscp.copy()

    # Si la columna que asumimos que Pandas creó no existe, volvemos al nombre por defecto
    if USER_LABEL_MAPEO_COL not in df_temp.columns:
        mml_output.append(f"// WARNING: Columna de mapeo '{USER_LABEL_MAPEO_COL}' no encontrada. Usando '{USER_LABEL_DEFAULT_COL}'.")
        USER_LABEL_MAPEO_COL = USER_LABEL_DEFAULT_COL 


    df_eth_port = df_eth_port.dropna(subset=['ethernetPortId']) if df_eth_port is not None else pd.DataFrame()
    if df_eth_port.empty:
        mml_output.append(f"// ERROR: Hoja Ethernet_Port vacía o 'ethernetPortId' nulo. No se puede determinar el puerto.")
        return mml_output

    ethernet_port_id = get_val(df_eth_port.iloc[0], 'ethernetPortId') 
    if not ethernet_port_id:
        mml_output.append(f"// ERROR: 'ethernetPortId' es nulo o vacío. Saltando sección.")
        return mml_output

    # --- 2. Header y Mapeo por defecto ---
    mml_output.append("")
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("// DscpToPCPMap ")
    mml_output.append("/////////////////////////////////////////////////////////////")
    
    resource_key = f"Transport=1,EthernetPort={ethernet_port_id},QueueSystem=1"
    map_key = f"{resource_key},QoSClassifier=1,DscpToPCPMap=1"
    
    mml_output.append(f"cr {resource_key}")
    mml_output.append(f"cr {resource_key},QoSClassifier=1")
    mml_output.append(f"cr {map_key}")
    
    # Extracción de defaultPCP y userLabel DEFAULT 
    try:
        default_row = df_temp.iloc[0] 
        default_pcp_val = get_val(default_row, 'defaultPCP') or '0'
        # Usando el nombre de columna del primer 'userLabel'
        default_label = get_val(default_row, USER_LABEL_DEFAULT_COL) 
    except Exception:
        default_pcp_val = '0'
        default_label = 'DEFAULT'

    mml_output.append(f"{default_pcp_val} #defaultPCP")
    mml_output.append(f"lset {map_key}$ userLabel {default_label or 'DEFAULT'}")
    mml_output.append("") 
    
    # --- 3. Preprocesamiento de datos para mapeos dinámicos ---
    
    try:
        if ID_COL not in df_temp.columns:
            raise KeyError(ID_COL)
        
        df_temp[ID_COL] = pd.to_numeric(df_temp[ID_COL], errors='coerce')
        
        # Validar las columnas requeridas (usando USER_LABEL_MAPEO_COL)
        validation_cols = [col for col in [ID_COL, DSCP_SET_COL, PCP_COL, USER_LABEL_MAPEO_COL] if col in df_temp.columns]

        df_temp.dropna(subset=validation_cols, inplace=True)
        df_temp[ID_COL] = df_temp[ID_COL].astype(int)
        
    except KeyError as e:
        mml_output.append(f"// ERROR: Falló la limpieza de datos de DscpToPCPMap. Detalle: Columna requerida {str(e)} no encontrada.")
        return mml_output
    except Exception as e:
        mml_output.append(f"// ERROR: Falló la limpieza de datos de DscpToPCPMap. Detalle: {str(e)}")
        return mml_output
        
    # Filtrar ID=0 y ordenar
    df_final = df_temp[df_temp[ID_COL] != 0].sort_values(by=ID_COL)
    
    # --- 4. Generación de DscpSetToPCP dinámica ---
    for index, row in df_final.iterrows():
        try:
            dscp_id = get_val(row, ID_COL)
            dscp_set = get_val(row, DSCP_SET_COL)
            pcp_val = get_val(row, PCP_COL)
            
            # EXTRACCIÓN CORREGIDA: Usamos el nombre 'userLabel.1'
            user_label = get_val(row, USER_LABEL_MAPEO_COL)
            
            # Fallback (solo si el valor es realmente nulo)
            user_label = user_label or f"DSCP_MAP_{dscp_id}"

            if dscp_id and dscp_set and pcp_val: 
                dscp_to_pcp_key = f"{map_key},DscpSetToPCP={dscp_id}"
                
                mml_output.append(f"cr {dscp_to_pcp_key}")
                mml_output.append(f"{dscp_set} #dscpSet")
                mml_output.append(f"{pcp_val} #pcp")
                mml_output.append(f"lset {dscp_to_pcp_key}$ userLabel {user_label}")
                mml_output.append("") 

        except Exception as e:
            mml_output.append(f"// ERROR: Falló al procesar fila dinámica {index}: {str(e)}")
            continue

    return mml_output


# =====================================================================
# FUNCIÓN DE SECCIÓN: Shaper (Nueva)
# =====================================================================

def generate_shaper_section(atnd_data: Dict[str, Any]) -> List[str]:
    """
    Genera la sección Shaper del script MML.
    """
    mml_output = []
    
    df_shaper = get_shaper_data(atnd_data)
    df_eth_port = get_ethernet_port_data(atnd_data)
    
    # --- 1. Validaciones Iniciales y Puerto Ethernet ---
    if df_shaper is None or df_shaper.empty:
        mml_output.append(f"// WARNING: Hoja Shaper no encontrada o vacía. Saltando sección.")
        return mml_output
        
    df_temp = df_shaper.copy()

    df_eth_port = df_eth_port.dropna(subset=['ethernetPortId']) if df_eth_port is not None else pd.DataFrame()
    if df_eth_port.empty:
        mml_output.append(f"// ERROR: Hoja Ethernet_Port vacía o 'ethernetPortId' nulo. No se puede determinar el puerto para Shaper.")
        return mml_output

    ethernet_port_id = get_val(df_eth_port.iloc[0], 'ethernetPortId') 
    if not ethernet_port_id:
        mml_output.append(f"// ERROR: 'ethernetPortId' es nulo o vacío. Saltando sección Shaper.")
        return mml_output

    # Claves MML estáticas y base
    RESOURCE_KEY_BASE = f"Transport=1,EthernetPort={ethernet_port_id},QueueSystem=1"
    SHAPER_KEY_ROOT = f"{RESOURCE_KEY_BASE},Shaper=1"
    SCHEDULER_KEY = f"{SHAPER_KEY_ROOT},SchedulerSp=1"
    
    # --- 2. Header de la sección ---
    mml_output.append("")
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("// Shaper ")
    mml_output.append("/////////////////////////////////////////////////////////////")
    
    # --- 3. Shaper Principal (Nivel 1: Fila 0) ---
    try:
        root_row = df_temp.iloc[0]
        
        cbs_root = get_val(root_row, 'committedBurstSize') # Columna B
        cir_root = get_val(root_row, 'committedInformationRate_kbps') # Columna C (El primero)

        if cbs_root and cir_root:
            mml_output.append(f"cr {SHAPER_KEY_ROOT}")
            mml_output.append(f"bytes={cbs_root} #committedBurstSize")
            mml_output.append(f"kbps={cir_root} #committedInformationRate")
            mml_output.append(f"lset {SHAPER_KEY_ROOT}$ order 0")
            # userLabel para el Shaper principal no está en la hoja
            mml_output.append(f"lset {SHAPER_KEY_ROOT}$ userLabel") 
        else:
            mml_output.append("// WARNING: Valores de Shaper Principal (CBS/CIR) nulos. Saltando Shaper=1.")
            return mml_output

    except Exception as e:
        mml_output.append(f"// ERROR: Falló al procesar Shaper Principal: {str(e)}")
        return mml_output


    # --- 4. SchedulerSp (Nivel 2: Fijo SchedulerSp=1) ---
    mml_output.append(f"cr {SCHEDULER_KEY}")
    mml_output.append(f"lset {SCHEDULER_KEY}$ order 0")
    mml_output.append(f"lset {SCHEDULER_KEY}$ userLabel") # userLabel para SchedulerSp no está en la hoja


    # --- 5. Shapers Anidados y QueueTailDrop (Nivel 3) ---
    
    # Nombres de columnas mapeados por Pandas (basados en la duplicidad)
    CBS_BYTES_COL = 'committedBurstSize_bytes' 
    CIR_ANIDADO_COL = 'committedInformationRate_kbps.1' # Asumimos el .1
    ORDER_SHAPER_COL = 'order.1' # Asumimos el .1
    SHAPER_ID_COL = 'shaperid'
    USER_LABEL_SHAPER_COL = 'userlabel.1' # Asumimos el .1
    
    # Columnas QueueTailDrop
    QUEUE_SIZE_BYTES_COL = 'queuesize_bytes' 
    QUEUETD_ID_COL = 'queueTailDropId' 
    ORDER_QTD_COL = 'order' # El primer 'order' de la fila (Columna M)
    
    # Filtrar las filas que definen los mapeos (tienen shaperid y QueueTailDropId)
    df_mapped = df_temp.dropna(subset=[SHAPER_ID_COL, QUEUETD_ID_COL]).copy()
    
    if df_mapped.empty:
         mml_output.append("// WARNING: No se encontraron mapeos Shaper/QueueTailDrop válidos.")
         return mml_output

    for index, row in df_mapped.iterrows():
        try:
            shaper_id = get_val(row, SHAPER_ID_COL)
            queue_td_id = get_val(row, QUEUETD_ID_COL)
            
            # Shaper Anidado: Extracción de valores
            cbs_anidado = get_val(row, CBS_BYTES_COL)
            # Usar los nombres de columna supuestos por Pandas
            cir_anidado = get_val(row, CIR_ANIDADO_COL) 
            order_shaper = get_val(row, ORDER_SHAPER_COL) 
            user_label_shaper = get_val(row, USER_LABEL_SHAPER_COL) 
            
            # QueueTailDrop: Extracción de valores
            queue_size = get_val(row, QUEUE_SIZE_BYTES_COL)
            # Usamos el primer 'order' para el QTD (Columna M en el esquema)
            order_qtd = get_val(row, ORDER_QTD_COL) 

            if shaper_id and queue_td_id and cbs_anidado and cir_anidado:
                SHAPER_ANIDADO_KEY = f"{SCHEDULER_KEY},Shaper={shaper_id}"
                QTD_ANIDADO_KEY = f"{SHAPER_ANIDADO_KEY},QueueTailDrop={queue_td_id}"
                
                # Comando Shaper Anidado
                mml_output.append(f"cr {SHAPER_ANIDADO_KEY}")
                mml_output.append(f"bytes={cbs_anidado} #committedBurstSize")
                mml_output.append(f"kbps={cir_anidado} #committedInformationRate")
                mml_output.append(f"set {SHAPER_ANIDADO_KEY}$ order {order_shaper or shaper_id}")
                mml_output.append(f"set {SHAPER_ANIDADO_KEY}$ userlabel {user_label_shaper or ''}")
                
                # Comando QueueTailDrop Anidado
                if queue_size:
                    mml_output.append(f"cr {QTD_ANIDADO_KEY}")
                    mml_output.append(f"bytes={queue_size} #queueSize")
                    mml_output.append(f"set {QTD_ANIDADO_KEY}$ order {order_qtd or '0'}")
                    mml_output.append(f"set {QTD_ANIDADO_KEY}$ userlabel")
                else:
                    mml_output.append(f"// WARNING: queueSize para Shaper={shaper_id} es nulo. Omitiendo QueueTailDrop={queue_td_id}")
                
                mml_output.append("")

        except Exception as e:
            mml_output.append(f"// ERROR: Falló al procesar fila Shaper dinámica {index}: {str(e)}")
            continue

    return mml_output

# =====================================================================
# FUNCIÓN DE SECCIÓN: SchedulerDwrr (Corregida)
# =====================================================================

def generate_scheduler_dwrr_section(atnd_data: Dict[str, Any]) -> List[str]:
    """
    Genera la sección SchedulerDwrr del script MML.
    """
    mml_output = []
    
    # Asegúrate de que get_scheduler_dwrr_data está importado correctamente
    # from .data_reader_ATND import get_scheduler_dwrr_data 
    df_dwrr = get_scheduler_dwrr_data(atnd_data) 
    df_eth_port = get_ethernet_port_data(atnd_data)
    
    # --- 1. Validaciones Iniciales y Puerto Ethernet ---
    if df_dwrr is None or df_dwrr.empty:
        mml_output.append(f"// WARNING: Hoja SchedulerDwrr no encontrada o vacía. Saltando sección.")
        return mml_output
        
    df_temp = df_dwrr.copy()

    df_eth_port = df_eth_port.dropna(subset=['ethernetPortId']) if df_eth_port is not None else pd.DataFrame()
    if df_eth_port.empty:
        mml_output.append(f"// ERROR: Hoja Ethernet_Port vacía o 'ethernetPortId' nulo. No se puede determinar el puerto para SchedulerDwrr.")
        return mml_output

    ethernet_port_id = get_val(df_eth_port.iloc[0], 'ethernetPortId') 
    if not ethernet_port_id:
        mml_output.append(f"// ERROR: 'ethernetPortId' es nulo o vacío. Saltando sección SchedulerDwrr.")
        return mml_output

    # Claves MML estáticas y base
    RESOURCE_KEY_BASE = f"Transport=1,EthernetPort={ethernet_port_id},QueueSystem=1,Shaper=1,SchedulerSp=1"
    DWRR_KEY = f"{RESOURCE_KEY_BASE},SchedulerDwrr=1"
    
    # Columnas de Root SchedulerDwrr
    SCHEDULING_WEIGHT_COL = 'schedulingWeight'
    ORDER_ROOT_COL = 'order' # El primer 'order' de la fila
    USER_LABEL_ROOT_COL = 'userLabel' # El primer 'userLabel' de la fila

    # --- 2. Header de la sección ---
    mml_output.append("")
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("// SchedulerDwrr ")
    mml_output.append("/////////////////////////////////////////////////////////////")
    
    # --- 3. SchedulerDwrr Principal (Nivel 1: Fila 0) ---
    try:
        root_row = df_temp.iloc[0]
        
        # Parámetros Root
        weight_val = get_val(root_row, SCHEDULING_WEIGHT_COL) 
        order_val = get_val(root_row, ORDER_ROOT_COL)
        user_label_root = get_val(root_row, USER_LABEL_ROOT_COL)

        if weight_val:
            mml_output.append(f"cr {DWRR_KEY}")
            mml_output.append(f"set {DWRR_KEY}$ order {order_val or '0'}")
            mml_output.append(f"set {DWRR_KEY}$ schedulingWeight {weight_val}")
            mml_output.append(f"set {DWRR_KEY}$ userLabel {user_label_root or ''}")
        else:
            mml_output.append("// WARNING: Valor de schedulingWeight nulo. Saltando SchedulerDwrr=1.")
            return mml_output

    except Exception as e:
        mml_output.append(f"// ERROR: Falló al procesar SchedulerDwrr Principal: {str(e)}")
        # Continuamos para intentar procesar los mapeos anidados si el error fue solo en la primera fila.
        pass 

    # --- 4. Shapers Anidados y QueueTailDrop (Nivel 2) ---
    
    # Nombres de columnas mapeados por Pandas (basados en la duplicidad)
    CBS_BYTES_COL = 'committedBurstSize_bytes'
    CIR_KBPS_COL = 'committedInformationRate_kbps' # <--- CORREGIDO: Usamos nombre explícito (Columna J)
    ORDER_SHAPER_COL = 'order.1' # Segundo 'order' (Columna K)
    SHAPER_ID_COL = 'shaperid'
    USER_LABEL_SHAPER_COL = 'userlabel.1' # <--- CORREGIDO: Minúscula 'l' y asumiendo sufijo (Columna M)
    
    # Columnas QueueTailDrop
    QUEUE_SIZE_BYTES_COL = 'queueSize_bytes' 
    QUEUETD_ID_COL = 'queueTailDropId' 
    ORDER_QTD_COL = 'order.2' # Tercer 'order' (Columna O)
    
    # Validamos que al menos los IDs existan
    df_mapped = df_temp.dropna(subset=[SHAPER_ID_COL, QUEUETD_ID_COL]).copy()
    
    if df_mapped.empty:
         mml_output.append("// WARNING: No se encontraron mapeos Shaper/QueueTailDrop anidados en SchedulerDwrr.")
         # Evitar retornar si la cabecera ya se escribió
         return mml_output

    for index, row in df_mapped.iterrows():
        try:
            shaper_id = get_val(row, SHAPER_ID_COL)
            queue_td_id = get_val(row, QUEUETD_ID_COL)
            
            # Shaper Anidado: Extracción de valores
            cbs_anidado = get_val(row, CBS_BYTES_COL) # committedBurstSize_bytes
            cir_anidado = get_val(row, CIR_KBPS_COL) # committedInformationRate_kbps
            order_shaper = get_val(row, ORDER_SHAPER_COL) # order.1
            user_label_shaper = get_val(row, USER_LABEL_SHAPER_COL) # userlabel.1
            
            # QueueTailDrop: Extracción de valores
            queue_size = get_val(row, QUEUE_SIZE_BYTES_COL) # queueSize_bytes
            order_qtd = get_val(row, ORDER_QTD_COL) # order.2

            # Verificamos que los valores críticos no sean nulos
            if shaper_id and queue_td_id and cbs_anidado and cir_anidado:
                SHAPER_ANIDADO_KEY = f"{DWRR_KEY},Shaper={shaper_id}"
                QTD_ANIDADO_KEY = f"{SHAPER_ANIDADO_KEY},QueueTailDrop={queue_td_id}"
                
                # Comando Shaper Anidado
                mml_output.append(f"cr {SHAPER_ANIDADO_KEY}")
                mml_output.append(f"bytes={cbs_anidado} #committedBurstSize")
                mml_output.append(f"kbps={cir_anidado} #committedInformationRate")
                mml_output.append(f"set {SHAPER_ANIDADO_KEY}$ order {order_shaper or shaper_id}")
                mml_output.append(f"set {SHAPER_ANIDADO_KEY}$ userLabel {user_label_shaper or ''}")
                
                # Comando QueueTailDrop Anidado
                if queue_size:
                    mml_output.append(f"cr {QTD_ANIDADO_KEY}")
                    mml_output.append(f"bytes={queue_size} #queueSize")
                    mml_output.append(f"set {QTD_ANIDADO_KEY}$ order {order_qtd or '0'}")
                    mml_output.append(f"set {QTD_ANIDADO_KEY}$ userLabel")
                else:
                    mml_output.append(f"// WARNING: queueSize para Shaper={shaper_id} en SchedulerDwrr es nulo. Omitiendo QueueTailDrop={queue_td_id}")
                
                mml_output.append("")

        except Exception as e:
            mml_output.append(f"// ERROR: Falló al procesar fila SchedulerDwrr dinámica {index}: {str(e)}")
            continue

    return mml_output

def generate_pcp_to_queue_map_section(atnd_data: Dict[str, Any]) -> List[str]:
    """
    Genera la sección PcpToQueueMap replicando el formato exacto solicitado:
    - cr por cada PcpSetToQueue.
    - Propiedades en líneas separadas (#pcpSet, #queue).
    - Usa la columna 'userLabel.1' o la última columna para la referencia de cola.
    """
    mml_output = []
    ethernet_port_id = None 

    # --- 1. Obtención de Datos y Validaciones ---
    df_pcp_map = atnd_data.get('PcpToQueueMap', pd.DataFrame()) 
    df_eth_port = atnd_data.get('Ethernet_Port', pd.DataFrame()) 

    if df_pcp_map is None or df_pcp_map.empty:
        mml_output.append(f"// WARNING: Hoja PcpToQueueMap no encontrada o vacía.")
        return mml_output
        
    df_temp = df_pcp_map.copy()

    # Obtener puerto Ethernet
    df_eth_port = df_eth_port.dropna(subset=['ethernetPortId']) if df_eth_port is not None else pd.DataFrame()
    if df_eth_port.empty:
        mml_output.append(f"// ERROR: Hoja Ethernet_Port vacía. No se puede determinar puerto.")
        return mml_output 
        
    ethernet_port_id = df_eth_port.iloc[0]['ethernetPortId'] 
    if not ethernet_port_id:
        mml_output.append(f"// ERROR: 'ethernetPortId' es nulo.")
        return mml_output
    
    # -----------------------------------------------------------------
    # Configuración
    # -----------------------------------------------------------------
    PCP_MAP_KEY = f"Transport=1,EthernetPort={ethernet_port_id},QueueSystem=1,QoSClassifier=1,PcpToQueueMap=1"
    QUEUE_BASE_KEY = f"EthernetPort={ethernet_port_id},QueueSystem=1,Shaper=1,SchedulerSp=1,SchedulerDwrr=1"
    
    # Nombres de columnas
    DEFAULT_QUEUE_COL = 'defaultQueue'
    PCP_SET_TO_QUEUE_ID_COL = 'PcpSetToQueue' # El ID numérico (1, 2, 3...)
    PCP_SET_COL = 'pcpSet'                    # El valor PCP (7, 6, 5...)
    
    # Columna objetivo para la referencia de cola (la duplicada)
    TARGET_QUEUE_COL = 'userLabel.1' 
    # -----------------------------------------------------------------
    
    # --- 2. Header ---
    mml_output.append("")
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("// PcpToQueueMap ")
    mml_output.append("/////////////////////////////////////////////////////////////")

    # --- 3. PcpToQueueMap Principal (Formato específico solicitado) ---
    try:
        root_row = df_temp.iloc[0]
        default_queue_raw = root_row[DEFAULT_QUEUE_COL]
        
        # Construir ruta de defaultQueue
        if pd.notna(default_queue_raw):
            match_suffix = re.search(r'(Shaper=\d+,QueueTailDrop=\d+)', str(default_queue_raw))
            if match_suffix:
                default_queue_val = f"{QUEUE_BASE_KEY},{match_suffix.group(1)}"
            else:
                default_queue_val = f"{QUEUE_BASE_KEY},Shaper=4,QueueTailDrop=4"
        else:
            default_queue_val = f"{QUEUE_BASE_KEY},Shaper=4,QueueTailDrop=4"

        # Generar bloque EXACTO como el ejemplo
        mml_output.append(f"cr {PCP_MAP_KEY}")
        mml_output.append(f"{default_queue_val} #defaultQueue")
        # El usuario pidió: lset ...$ userLabel
        mml_output.append(f"lset {PCP_MAP_KEY}$ userLabel") 
        mml_output.append("")
        
    except Exception as e:
        mml_output.append(f"// ERROR: Falló al procesar PcpToQueueMap Principal: {str(e)}")

    # --- 4. PcpSetToQueue Anidados (Iteración individual) ---
    df_mapped = df_temp.dropna(subset=[PCP_SET_TO_QUEUE_ID_COL]).copy()
    
    for index, row in df_mapped.iterrows():
        try:
            # Obtener ID (1, 2, 3...)
            item_id = row[PCP_SET_TO_QUEUE_ID_COL]
            
            # Obtener valor PCP (7, 6, 5...)
            pcp_set_val = row[PCP_SET_COL]
            
            # --- Lógica de selección de columna de Cola (CORREGIDA) ---
            queue_ref_raw = None
            if TARGET_QUEUE_COL in df_mapped.columns:
                queue_ref_raw = row[TARGET_QUEUE_COL]
            
            # Si falla, usar la última columna (fallback seguro)
            if pd.isna(queue_ref_raw) or queue_ref_raw == "":
                queue_ref_raw = row.iloc[-1]

            # Generar bloque si los datos son válidos
            if pd.notna(item_id) and pd.notna(pcp_set_val) and pd.notna(queue_ref_raw):
                
                final_queue_ref = str(queue_ref_raw).strip()
                
                # Validar que parece una referencia de cola válida
                if "EthernetPort=" in final_queue_ref:
                    # Bloque individual
                    mml_output.append(f"cr {PCP_MAP_KEY},PcpSetToQueue={int(item_id)}")
                    mml_output.append(f"{int(pcp_set_val)} #pcpSet")
                    mml_output.append(f"{final_queue_ref} #queue")
                    mml_output.append("")
                else:
                    mml_output.append(f"// WARNING: Fila {index} ignorada. Referencia no válida: {final_queue_ref}")

        except Exception as e:
            mml_output.append(f"// ERROR: Falló fila {index}: {str(e)}")
            continue

    # 5. Finalización
    mml_output.append("gs-")
    mml_output.append("confb-")
    
    return mml_output

# =====================================================================
# FUNCIÓN PRINCIPAL 
# =====================================================================

def generate_queue_script(nemonico: str, atnd_data: Any = None) -> str:
    """
    Genera el contenido del archivo 01.-Nemonico_QUEUE_BB.txt.
    """
    
    now = datetime.now()
    fecha_str = now.strftime("%d-%m-%Y")
    hora_str = now.strftime("%H:%M:%S")
    
    queue_output = []
    
    # -----------------------------------------------------------
    # 1. GENERACIÓN DEL ENCABEZADO (FIRMA)
    # -----------------------------------------------------------
    queue_output.append("/////////////////////////////////////////////////////////////")
    queue_output.append("//")
    queue_output.append("// SCRIPT     : QUEUE ATND LTE -> EJECUTAR CON RUN 1")
    queue_output.append("// AUTOR      : PIERO LEDESMA")
    queue_output.append(f"// NEMONICO   : {nemonico}")
    queue_output.append(f"// HORA       : {hora_str}")
    queue_output.append(f"// FECHA      : {fecha_str}")
    queue_output.append("//")
    queue_output.append("/////////////////////////////////////////////////////////////")
    queue_output.append("") 
    
    # -----------------------------------------------------------
    # 2. GENERACIÓN DE SECCIONES MML
    # -----------------------------------------------------------
    
    if atnd_data:
        # 1. DscpToPCPMap
        queue_output.extend(generate_dscp_to_pcp_map_section(atnd_data))
        
        # 2. Shaper
        queue_output.extend(generate_shaper_section(atnd_data))

        # 3. SchedulerDwrr
        queue_output.extend(generate_scheduler_dwrr_section(atnd_data))

    # 4. PcpToQueueMap (Nueva Sección)
        queue_output.extend(generate_pcp_to_queue_map_section(atnd_data))
        
    else:
        queue_output.append("// ERROR: No se pasaron datos del ATND para generar la lógica de Queue.")
    
    return "\n".join(queue_output)