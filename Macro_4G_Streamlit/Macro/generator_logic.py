# generator_logic.py

import os
import io
import zipfile
from typing import Dict, Any, Tuple, Optional

# --- IMPORTACIONES NECESARIAS ---
from functions.data_reader import leer_datos_wsh_lte 
from functions.terreno_generator import generar_site_basic_xml, generar_site_equipment_xml
from functions.enrollment_generator import generar_create_identity_yml, generar_lte_enm_xml
from functions.remote_generator import generar_hardware_mos 


def generar_archivos_zip(nemonico: str, release: str, trama: str, region: str, wsh_file: Any, rnd_node_file: Any) -> Tuple[Optional[bytes], str, Optional[Dict[str, str]]]:
    """
    Coordina la generación de todos los archivos (Terreno, Enrollment, Remotos)
    utilizando la data del WSH y del RND (hoja Node), y los comprime en un ZIP.
    
    Argumentos:
        nemonico (str): Nombre del sitio.
        release (str): Release de software.
        trama (str): Puerto físico de la trama.
        region (str): Región de la célula.
        wsh_file (Any): Archivo subido del WSHReport (LTE.csv).
        rnd_node_file (Any): Archivo subido del RND (Hoja Node.xlsx).
        
    Retorna:
        Contenido ZIP, nombre del archivo, y diccionario de contenido para debug.
    """
    nemonico_upper = nemonico.upper()
    
    # 1. Leer datos del WSH
    wsh_data, error_message = leer_datos_wsh_lte(wsh_file, nemonico)
    if not wsh_data:
        return None, error_message, None

    ip_oam = wsh_data.get('IP_OAM_LTE', '0.0.0.0')

    # --- Generación de Archivos de Terreno ---
    folder_name_terreno = f"00.{nemonico_upper}_Terreno"
    
    release_path = release + ("/" if not release.endswith("/") else "")
    summary_xml_filename = f"00_{nemonico_upper}_RbsSummaryFile.xml"
    summary_xml_content = f"""<summary:AutoIntegrationRbsSummaryFile
xmlns:summary="http://www.ericsson.se/RbsSummaryFileSchema"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://www.ericsson.se/RbsSummaryFileSchemaSummaryFile.xsd">
<Format revision="F"/>
<ConfigurationFiles
    siteBasicFilePath="01_{nemonico_upper}_SiteBasic.xml"
    siteEquipmentFilePath="02_{nemonico_upper}_SiteEquipment.xml"
    upgradePackageFilePath="{release_path}"/>
</summary:AutoIntegrationRbsSummaryFile>"""

    site_basic_xml_content = generar_site_basic_xml(nemonico, trama, wsh_data)
    site_basic_xml_filename = f"01_{nemonico_upper}_SiteBasic.xml"
    
    site_equipment_xml_content = generar_site_equipment_xml(trama)
    site_equipment_xml_filename = f"02_{nemonico_upper}_SiteEquipment.xml"


    # --- Generación de Archivos de Enrollment ---
    folder_name_enrollment = f"02-Enrollment_{nemonico_upper}"
    
    create_identity_yml_content = generar_create_identity_yml(nemonico)
    create_identity_yml_filename = f"00_Create_Identity.xml"
    
    lte_enm_xml_content = generar_lte_enm_xml(nemonico, region, ip_oam)
    lte_enm_xml_filename = f"01_LTE_ENM_{nemonico_upper}.xml"

    
    # --- Generación de Archivos de Remotos (MOS) ---
    folder_name_remotos = f"{nemonico_upper}_Script_Remotos" 
    
    # La macro unificada
    hardware_mos_content = generar_hardware_mos(
        nemonico, 
        wsh_data, 
        trama, 
        rnd_node_file   # Pasa la data del RND (Excel, Hoja Node)
    ) 
    hardware_mos_filename = f"00_{nemonico_upper}_Hardware.mos" 


    # 2. Empaquetado en ZIP
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        # Archivos de Terreno
        zip_file.writestr(os.path.join(folder_name_terreno, summary_xml_filename), summary_xml_content.encode('utf-8'))
        zip_file.writestr(os.path.join(folder_name_terreno, site_basic_xml_filename), site_basic_xml_content.encode('utf-8'))
        zip_file.writestr(os.path.join(folder_name_terreno, site_equipment_xml_filename), site_equipment_xml_content.encode('utf-8'))
        
        # Archivos de Enrollment
        zip_file.writestr(os.path.join(folder_name_enrollment, create_identity_yml_filename), create_identity_yml_content.encode('utf-8'))
        zip_file.writestr(os.path.join(folder_name_enrollment, lte_enm_xml_filename), lte_enm_xml_content.encode('utf-8'))
        
        # Archivos de Remotos (MOS)
        zip_file.writestr(os.path.join(folder_name_remotos, hardware_mos_filename), hardware_mos_content.encode('utf-8'))
        
    zip_buffer.seek(0)
    
    # 3. Devolver el ZIP y los contenidos generados para debug
    all_generated_content = {
        '00_SUMMARY_XML': summary_xml_content,
        '01_SITE_BASIC_XML': site_basic_xml_content,
        '02_SITE_EQUIPMENT_XML': site_equipment_xml_content,
        
        '00_CREATE_IDENTITY_XML': create_identity_yml_content,
        '01_LTE_ENM_XML': lte_enm_xml_content,
        
        '00_HARDWARE_MOS': hardware_mos_content 
    }
    return zip_buffer.getvalue(), f"Scripts_{nemonico_upper}.zip", all_generated_content