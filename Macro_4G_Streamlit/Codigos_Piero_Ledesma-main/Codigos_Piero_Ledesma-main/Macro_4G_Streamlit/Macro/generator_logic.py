# generator_logic.py (VERSIÓN FINAL Y ROBUSTA)

import os
import io
import zipfile
import pandas as pd
from typing import Dict, Any, Tuple, Optional

# --- IMPORTACIONES DESDE functions/ ---
from functions.data_reader import leer_datos_wsh_lte 
from functions.terreno_generator import generar_site_basic_xml, generar_site_equipment_xml
from functions.enrollment_generator import generar_create_identity_yml, generar_lte_enm_xml
from functions.remote_generator import generar_hardware_mos
from functions.cell_generator import generate_cell_config_mos 


def generar_archivos_zip(nemonico: str, release: str, trama: str, region: str, wsh_file: Any, rnd_file_xlsx: Any) -> Tuple[Optional[bytes], str, Optional[Dict[str, str]]]:
    nemonico_upper = nemonico.upper()
    
    # 1. Leer datos del WSH
    wsh_data, error_message = leer_datos_wsh_lte(wsh_file, nemonico)
    if not wsh_data:
        return None, error_message, None

    ip_oam = wsh_data.get('IP_OAM_LTE', '0.0.0.0')

    # 2. Leer hojas del RND XLSX 
    try:
        # 2.1 Leemos el RND como objeto ExcelFile para dárselo a Hardware (que lo necesita)
        # Esto soluciona que Hardware no encuentre las RRUs/SCTP, etc.
        rnd_excel_file = pd.ExcelFile(rnd_file_xlsx, engine='openpyxl')
        
        required_sheets = ['Node', 'Cell-Carrier', 'Equipment-Configuration']
        if not all(sheet in rnd_excel_file.sheet_names for sheet in required_sheets):
             return None, f"Error: El RND XLSX debe contener las hojas {', '.join(required_sheets)}.", None

        # 2.2 Leemos las hojas específicas como DataFrames para Celdas
        df_cell_carrier = pd.read_excel(rnd_excel_file, sheet_name='Cell-Carrier')
        
        # 2.3 CORRECCIÓN CRÍTICA: Limpiar nombres de columnas para que Celdas encuentre 'Atributo'
        df_cell_carrier.columns = df_cell_carrier.columns.str.strip()
        
    except Exception as e:
        return None, f"Error al leer hojas del RND XLSX. Asegúrese de que el archivo es un XLSX válido. Error: {e}", None

    # --- Archivos de Terreno y Enrollment (Lógica omitida por brevedad, mantener tu código) ---
    
    folder_name_terreno = f"00-{nemonico_upper}_Terreno"
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

    folder_name_enrollment = f"02-Enrollment_{nemonico_upper}"
    create_identity_yml_content = generar_create_identity_yml(nemonico)
    create_identity_yml_filename = f"00_Create_Identity.xml"
    
    lte_enm_xml_content = generar_lte_enm_xml(nemonico, region, ip_oam)
    lte_enm_xml_filename = f"01_LTE_ENM_{nemonico_upper}.xml"
    
    # --- Generación de Archivos de Remotos (MOS) ---
    folder_name_remotos = f"01-{nemonico_upper}_Script_Remotos" 
    
# 3. Generación de Hardware (¡Pasamos el objeto de archivo original!)
    hardware_mos_content = generar_hardware_mos(
        nemonico, 
        wsh_data, 
        trama, 
        rnd_file_xlsx  # <--- Asegúrate de que este es el archivo de entrada original
    ) 
    hardware_mos_filename = f"00_{nemonico_upper}_Hardware.mos"

    # 4. Generación de Celdas (Pasa el DataFrame Cell-Carrier ya limpio)
    cell_mos_content = generate_cell_config_mos(
        nemonico,
        df_cell_carrier 
    )
    cell_mos_filename = f"01_{nemonico_upper}_EUtranCellFDD.mos" 


    # 5. Empaquetado en ZIP
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
        zip_file.writestr(os.path.join(folder_name_remotos, cell_mos_filename), cell_mos_content.encode('utf-8')) 
        
    zip_buffer.seek(0)
    
    # 6. Devolver el ZIP y los contenidos generados para debug
    all_generated_content = {
        '00_SUMMARY_XML': summary_xml_content,
        '01_SITE_BASIC_XML': site_basic_xml_content,
        '02_SITE_EQUIPMENT_XML': site_equipment_xml_content,
        
        '00_CREATE_IDENTITY_XML': create_identity_yml_content,
        '01_LTE_ENM_XML': lte_enm_xml_content,
        
        '00_HARDWARE_MOS': hardware_mos_content,
        '01_EUtranCellFDD_MOS': cell_mos_content
    }
    return zip_buffer.getvalue(), f"Scripts_{nemonico_upper}.zip", all_generated_content