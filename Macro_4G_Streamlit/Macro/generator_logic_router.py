import os
import tempfile
import shutil
import streamlit as st
from functions_router.data_reader_router import leer_atnd_router
from functions_router.data_reader_router import extract_router_info
from functions_router.basic_generador import generar_script_basic
from functions_router.advanced_generador import generar_script_advanced

def analizar_atnd_router(atnd_file):
    """
    PASO 1: Analiza el archivo ATND y extrae información del router.
    
    Esta función se ejecuta cuando el usuario hace clic en "Analizar ATND".
    
    Args:
        atnd_file: Archivo ATND cargado por el usuario
        
    Returns:
        Tuple[Dict, str]: (info_dict, error_message)
        info_dict contiene:
            - 'nemonico': Némónico del router
            - 'router_name': Nombre del router
            - 'vlan_type': 'MASTER_VLAN' o 'ALL_VLAN'
            - 'vlan_type_display': Versión legible para UI
    """
    return extract_router_info(atnd_file)

def generar_archivos_r6k(nemonico, atnd_file, vlan_type):
    """
    PASO 2: Orquesta la generación de archivos para Script R6K.
    
    Args:
        nemonico: Némónico del router (del input del usuario)
        atnd_file: Archivo ATND ya analizado
        vlan_type: Tipo de VLAN explícito ('MASTER_VLAN' o 'ALL_VLAN')
        
    Returns:
        Tuple[bytes, str, dict]: (zip_data, zip_filename, scripts_content)
    """
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Crear carpeta principal Script_R6K_{Nemonico}_{VLAN_TYPE}
        vlan_suffix = "MASTER" if vlan_type == "MASTER_VLAN" else "ALL"
        folder_name = f"Script_R6K_{nemonico}_{vlan_suffix}"
        output_dir = os.path.join(temp_dir, folder_name)
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Leer archivo ATND
        df_atnd, error = leer_atnd_router(atnd_file)
        if df_atnd is None:
            return None, f"Error al leer archivo ATND: {error}", None
        
        # 2. Verificar que el tipo de VLAN detectado coincida (opcional pero útil)
        detected_type = df_atnd.get('VLAN_TYPE', {})
        if not detected_type.empty:
            detected = detected_type.iloc[0]['TIPO']
            if detected != vlan_type:
                st.warning(f"⚠️ Tipo detectado ({detected}) difiere del seleccionado ({vlan_type})")
            
        # 3. Generar Script Basic (pasando tipo explícito)
        script_path_basic = generar_script_basic(nemonico, output_dir, df_atnd, vlan_type=vlan_type)
        if not script_path_basic:
            return None, "Error al generar Script Basic", None
            
        # 4. Generar Script Advanced (pasando tipo explícito)
        script_path_advanced = generar_script_advanced(nemonico, output_dir, df_atnd, vlan_type=vlan_type)
        
        # 5. Comprimir resultado
        shutil.make_archive(output_dir, 'zip', output_dir)
        zip_path = output_dir + '.zip'
        
        with open(zip_path, "rb") as f:
            zip_data = f.read()
            
        # Retornamos el contenido de los scripts para mostrar en pantalla
        scripts_content = {}
        if script_path_basic:
            try:
                scripts_content["basic_script"] = open(script_path_basic, 'r', encoding='utf-8').read()
            except: pass
            
        if script_path_advanced:
            try:
                scripts_content["advanced_script"] = open(script_path_advanced, 'r', encoding='utf-8').read()
            except: pass

        return zip_data, f"{folder_name}.zip", scripts_content
        
    except Exception as e:
        return None, f"Error inesperado: {str(e)}", None
    finally:
        # Limpieza
        shutil.rmtree(temp_dir, ignore_errors=True)

