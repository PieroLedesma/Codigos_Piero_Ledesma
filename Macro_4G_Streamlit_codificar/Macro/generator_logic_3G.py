# ===========================================================================
# generator_logic_3G.py - Orquestación de generación de scripts 3G WCDMA
# ===========================================================================

import io
import zipfile
from typing import Dict, Tuple, Optional, Any

# Importar funciones de lectura y generación
from functions_3G.data_reader_3G import leer_datos_wsh_3g,leer_rnd_sheets_3g
from functions_3G.terreno_generator_3G import (
    generar_rbssummary,
    generar_sitebasic,
    generar_siteequipment
)
from functions_3G.node_generator_3G import generar_nodeid_mos
from functions_3G.Sector_generator import generate_sector_mos

# ===========================================================================
# FUNCIÓN PRINCIPAL: Generar archivos ZIP para 3G
# ===========================================================================

def generar_archivos_zip_3g(
    nemonico: str,
    trama: str,
    release: str,
    region: str,
    wsh_file: Any,
    rnd_file: Any,
    configuracion: str = "Configuración Básica 3G"
) -> Tuple[Optional[bytes], str, Optional[Dict[str, str]]]:
    """
    Genera el ZIP con archivos de terreno 3G WCDMA.
    
    Returns:
        Tuple con (zip_bytes, nombre_zip, dict_contenidos) o (None, "", None) en caso de error.
    """
    try:
        print(f"DEBUG: generar_archivos_zip_3g START for {nemonico}")
        # ===== 1. LECTURA DE DATOS =====
        # Leer WSH
        print("DEBUG: Reading WSH...")
        wsh_data, error_wsh = leer_datos_wsh_3g(wsh_file, nemonico)
        if not wsh_data:
            print(f"DEBUG: Error reading WSH: {error_wsh}")
            return None, "", {'error': error_wsh}
        
        if not wsh_data:
            print("DEBUG: No WSH data found")
            return None, "", {'error': 'No se pudieron extraer datos del WSH.'}
        
        print(f"DEBUG: WSH data extracted: {wsh_data}")
        
        # Leer RND (Opcional para terreno, solo warning si falla)
        print("DEBUG: Reading RND (Optional)...")
        rnd_data, error_rnd = leer_rnd_sheets_3g(rnd_file)
        if error_rnd:
            print(f"DEBUG: Warning reading RND: {error_rnd} - Proceeding anyway for Terrain scripts")
            # No retornamos error, solo logueamos y seguimos
            # return None, "", {'error': error_rnd} 
        
        nemonico_upper = nemonico.upper()
        
        # ===== 2. GENERAR CONTENIDOS XML Y MOS =====
        print("DEBUG: Generating XMLs and MOS...")
        xml_rbssummary = generar_rbssummary(nemonico_upper, release)
        xml_sitebasic = generar_sitebasic(nemonico_upper, wsh_data, trama)
        xml_siteequipment = generar_siteequipment(nemonico_upper)
        mos_nodeid = generar_nodeid_mos(nemonico_upper)
        
        # Generar Sector MOS
        print("DEBUG: Generating Sector MOS...")
        # Crear directorio temporal para Sector_generator
        import tempfile
        import os
        temp_dir = tempfile.mkdtemp()
        success_sector, msg_sector, sector_file_path = generate_sector_mos(
            nemonico=nemonico_upper,
            output_base_path=temp_dir,
            rnd_data=rnd_data,
            configuracion=configuracion
        )
        
        # Leer contenido del archivo generado
        mos_sector = ""
        if success_sector and os.path.exists(sector_file_path):
            with open(sector_file_path, 'r', encoding='utf-8') as f:
                mos_sector = f.read()
            print(f"DEBUG: Sector MOS generated successfully")
        else:
            print(f"DEBUG: Warning - Sector MOS generation failed: {msg_sector}")
            # Continuar sin Sector si falla
            mos_sector = f"// ERROR: No se pudo generar Sector MOS\n// {msg_sector}"
        print("DEBUG: XMLs and MOS generated successfully")
        
        # ===== 3. CREAR ESTRUCTURA ZIP =====
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Carpeta de terreno
            carpeta_terreno = f"00_Terreno_{nemonico_upper}/"
            
            # Agregar los 3 archivos XML
            zip_file.writestr(
                f"{carpeta_terreno}00_{nemonico_upper}_RbsSummaryFile.xml",
                xml_rbssummary.encode('utf-8')
            )
            zip_file.writestr(
                f"{carpeta_terreno}01_{nemonico_upper}_SiteBasic.xml",
                xml_sitebasic.encode('utf-8')
            )
            zip_file.writestr(
                f"{carpeta_terreno}02_{nemonico_upper}_SiteEquipment.xml",
                xml_siteequipment.encode('utf-8')
            )
            
            # Carpeta de Nodo (01_nodo_nemonico)
            carpeta_nodo = f"01_nodo_nemonico/"
            zip_file.writestr(
                f"{carpeta_nodo}00_{nemonico_upper}_PL_Nodeid.mos",
                mos_nodeid.encode('utf-8')
            )
            
            # Agregar Sector MOS
            if mos_sector and "ERROR" not in mos_sector:
                zip_file.writestr(
                    f"{carpeta_nodo}01_Nemonico_PL_Sector.mos",
                    mos_sector.encode('utf-8')
                )
        
        zip_buffer.seek(0)
        zip_bytes = zip_buffer.read()
        
        # Nombre del archivo ZIP
        zip_filename = f"{nemonico_upper}_3G_Scripts.zip"
        
        # Contenidos para mostrar en Streamlit
        all_content = {
            '00_RbsSummaryFile': xml_rbssummary,
            '01_SiteBasic': xml_sitebasic,
            '02_SiteEquipment': xml_siteequipment,
            '00_NodeId': mos_nodeid,
            '01_Sector': mos_sector
        }
        
        return zip_bytes, zip_filename, all_content
        
    except Exception as e:
        return None, "", {'error': f'Error inesperado durante la generación: {str(e)}'}
