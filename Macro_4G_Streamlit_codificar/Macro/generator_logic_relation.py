# ===========================================================================
# generator_logic_relation.py - Orquestación FINAL de Relaciones
# ===========================================================================

import io
import zipfile
from typing import Dict, Tuple, Optional, Any
from functions_Relation.data_reader_relation import leer_datos_relacion # <-- IMPORTACIÓN CLAVE
from functions_Relation.relation_generator import generate_relation_script # <-- IMPORTACIÓN CLAVE

# ===========================================================================
# FUNCIÓN PRINCIPAL: Generar archivos de Relaciones
# ===========================================================================

def generar_archivos_relation(
    nemonico: str,
    relation_file: Any 
) -> Tuple[Optional[bytes], str, Optional[Dict[str, str]]]:
    """
    Genera el ZIP con el script de Relaciones LTE->3G.
    """
    try:
        print(f"DEBUG: generar_archivos_relation START for {nemonico}")
        
        if not relation_file:
            return None, "", {'error': 'Archivo de relaciones no cargado.'}
            
        # 1. Leer todas las hojas del archivo Excel
        print("DEBUG: Calling leer_datos_relacion...")
        all_data = leer_datos_relacion(relation_file)
        
        if "error" in all_data:
            return None, "", {'error': all_data['error']}

        # 2. Generar Script MOS de Relaciones
        print("DEBUG: Calling generate_relation_script...")
        script_mos_content = generate_relation_script(nemonico, all_data)
        
        if "ERROR AL LEER DATOS" in script_mos_content:
             return None, "", {'error': script_mos_content}

        # 3. CREAR ESTRUCTURA ZIP
        zip_buffer = io.BytesIO()
        
        # Nombre de la carpeta y archivo según tu solicitud
        carpeta_name = f"Relaciones_{nemonico.upper()}/"
        nombre_archivo_00 = f"00_PL_Relaciones_{nemonico.upper()}.mos"
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(
                f"{carpeta_name}{nombre_archivo_00}",
                script_mos_content.encode('utf-8')
            )
            
            print(f"DEBUG: Added file to ZIP: {nombre_archivo_00}")
        
        zip_buffer.seek(0)
        zip_bytes = zip_buffer.read()
        
        # Nombre del archivo ZIP
        zip_filename = f"Relaciones_{nemonico.upper()}.zip"
        
        # Contenido para mostrar en Streamlit (Frontend)
        contenido = {
            'relation_mos': script_mos_content, # Clave usada en app.py para debug
        }
        
        print(f"DEBUG: ZIP generated successfully: {zip_filename}")
        
        return zip_bytes, zip_filename, contenido
        
    except Exception as e:
        error_msg = f'Error inesperado durante la generación: {str(e)}'
        import traceback
        traceback.print_exc()
        return None, "", {'error': error_msg}

# ===========================================================================