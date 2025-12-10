# ===========================================================================
# generator_logic_atnd.py - Orquestación de generación de scripts ATND
# ===========================================================================

import io
import zipfile
from typing import Dict, Tuple, Optional, Any

# Importar funciones de lectura y generación
from functions_ATND.data_reader_ATND import leer_atnd_completo, validar_atnd_data, get_summary_data
from functions_ATND.atnd_generator import generate_atnd_script
# [IMPORTANTE] Importamos la nueva función
from functions_ATND.queue_generator import generate_queue_script

# ===========================================================================
# FUNCIÓN PRINCIPAL: Generar archivos para ATND
# ===========================================================================

def generar_archivos_atnd(
    nemonico: str,
    atnd_file: Any
) -> Tuple[Optional[bytes], str, Optional[Dict[str, str]]]:
    """
    Genera el ZIP con carpeta y archivos para ATND.
    """
    try:
        print(f"DEBUG: generar_archivos_atnd START for {nemonico}")
        
        # ===== 1. VALIDAR ARCHIVO ATND =====
        if not atnd_file:
            print("DEBUG: No ATND file provided")
            return None, "", {'error': 'No se proporcionó archivo ATND'}
        
        # ===== 2. LEER Y VALIDAR DATOS =====
        print("DEBUG: Reading ATND file...")
        atnd_data, error = leer_atnd_completo(atnd_file)
        
        if error or not atnd_data:
            error_msg = error or "No se pudieron leer datos del ATND"
            print(f"DEBUG: Error reading ATND: {error_msg}")
            return None, "", {'error': error_msg}
        
        es_valido, msg_validacion = validar_atnd_data(atnd_data)
        if not es_valido:
            print(f"DEBUG: Validation failed: {msg_validacion}")
            return None, "", {'error': msg_validacion}
        
        # Obtener datos del summary para usar el nombre real del sitio
        summary = get_summary_data(atnd_data)
        site_name = summary.get('Site', nemonico) if summary else nemonico
        
        # ===== 3. GENERAR SCRIPTS =====
        
        # A) Generar Script 00 (ATND)
        print("DEBUG: Generating ATND script (00)...")
        success, script_atnd_content, _ = generate_atnd_script(site_name, atnd_file)
        
        if not success:
            print(f"DEBUG: Script generation failed")
            return None, "", {'error': 'Error al generar script ATND'}

        # B) [NUEVO] Generar Script 01 (QUEUE)
        print("DEBUG: Generating Queue script (01)...")
        # Aquí llamamos a la función que creamos en el paso 1
        script_queue_content = generate_queue_script(site_name, atnd_data)
        
        print(f"DEBUG: Scripts generated successfully")
        
        # ===== 4. CREAR ESTRUCTURA ZIP =====
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Nombre de la carpeta: Nemonico_ATND_BB
            carpeta_atnd = f"{site_name}_ATND_BB/"
            
            # --- Guardar archivo 00 (ATND) ---
            nombre_archivo_00 = f"00.-{site_name}_ATND_BB.txt"
            zip_file.writestr(
                f"{carpeta_atnd}{nombre_archivo_00}",
                script_atnd_content.encode('utf-8')
            )
            
            # --- [NUEVO] Guardar archivo 01 (QUEUE) ---
            nombre_archivo_01 = f"01.-{site_name}_QUEUE_BB.txt"
            zip_file.writestr(
                f"{carpeta_atnd}{nombre_archivo_01}",
                script_queue_content.encode('utf-8')
            )
            
            print(f"DEBUG: Added files to ZIP: {nombre_archivo_00}, {nombre_archivo_01}")
        
        zip_buffer.seek(0)
        zip_bytes = zip_buffer.read()
        
        # Nombre del archivo ZIP
        zip_filename = f"{site_name}_ATND_BB.zip"
        
        # Contenido para mostrar en Streamlit (Frontend)
        contenido = {
            'atnd_txt': script_atnd_content,
            'queue_txt': script_queue_content # Ahora esta variable sí existe
        }
        
        print(f"DEBUG: ZIP generated successfully: {zip_filename}")
        
        return zip_bytes, zip_filename, contenido
        
    except Exception as e:
        error_msg = f'Error inesperado durante la generación: {str(e)}'
        print(f"DEBUG: Exception - {error_msg}")
        import traceback
        traceback.print_exc()
        return None, "", {'error': error_msg}