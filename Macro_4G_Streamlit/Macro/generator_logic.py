# generator_logic.py (Coordinador Principal - V5.1)

import os
import io
import zipfile
from typing import Dict, Any, Tuple, Optional

# Importar las funciones de los nuevos módulos
from functions.data_reader import leer_datos_wsh_lte
from functions.terreno_generator import generar_site_basic_xml, generar_site_equipment_xml
from functions.enrollment_generator import generar_create_identity_yml, generar_lte_enm_xml


def generar_archivos_zip(nemonico: str, release: str, trama: str, region: str, wsh_file: Any) -> Tuple[Optional[bytes], str, Optional[Dict[str, str]]]:
    """
    Coordina la generación de todos los archivos y los comprime en un ZIP,
    incluyendo las carpetas de Terreno y Enrollment.
    """
    nemonico_upper = nemonico.upper()
    
    # 1. Leer datos del WSH (Delegado a data_reader.py)
    wsh_data, error_message = leer_datos_wsh_lte(wsh_file, nemonico)
    if not wsh_data:
        return None, error_message, None

    # Datos extraídos
    ip_oam = wsh_data.get('IP_OAM_LTE', '0.0.0.0')

    # --- Generación de Archivos de Terreno (Delegado a terreno_generator.py) ---
    folder_name_terreno = f"00.{nemonico_upper}_Terreno"
    
    # Summary File Content (Se queda aquí porque usa las rutas de ambos archivos)
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


    # --- Generación de Archivos de Enrollment (Delegado a enrollment_generator.py) ---
    folder_name_enrollment = f"02-Enrollment_{nemonico_upper}"
    
    create_identity_yml_content = generar_create_identity_yml(nemonico)
    create_identity_yml_filename = f"00_Create_Identity.xml"
    
    lte_enm_xml_content = generar_lte_enm_xml(nemonico, region, ip_oam)
    lte_enm_xml_filename = f"01_LTE_ENM_{nemonico_upper}.xml"


    # 2. Crear el buffer de memoria y el ZIP
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        # Archivos de Terreno
        zip_file.writestr(os.path.join(folder_name_terreno, summary_xml_filename), summary_xml_content.encode('utf-8'))
        zip_file.writestr(os.path.join(folder_name_terreno, site_basic_xml_filename), site_basic_xml_content.encode('utf-8'))
        zip_file.writestr(os.path.join(folder_name_terreno, site_equipment_xml_filename), site_equipment_xml_content.encode('utf-8'))
        
        # Archivos de Enrollment
        zip_file.writestr(os.path.join(folder_name_enrollment, create_identity_yml_filename), create_identity_yml_content.encode('utf-8'))
        zip_file.writestr(os.path.join(folder_name_enrollment, lte_enm_xml_filename), lte_enm_xml_content.encode('utf-8'))
        
    zip_buffer.seek(0)
    
    # 3. Devolver el ZIP y los contenidos generados para debug
    all_generated_content = {
        '00_SUMMARY_XML': summary_xml_content,
        '01_SITE_BASIC_XML': site_basic_xml_content,
        '02_SITE_EQUIPMENT_XML': site_equipment_xml_content,
        '00_CREATE_IDENTITY_XML': create_identity_yml_content,
        '01_LTE_ENM_XML': lte_enm_xml_content
    }
    return zip_buffer.getvalue(), f"Scripts_{nemonico_upper}.zip", all_generated_content