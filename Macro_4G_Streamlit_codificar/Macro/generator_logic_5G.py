# =====================================================================
# generator_logic_5G.py - Lógica de generación para scripts 5G NR (CORREGIDO)
# =====================================================================

import io
import zipfile
from typing import Dict, Any, Tuple, Optional

# --- IMPORTACIONES DESDE functions_5G/ ---
from functions_5G.data_reader_5G import leer_datos_wsh_5g, leer_rnd_sheets_5g 
from functions_5G.terreno_generator_5G import generar_site_basic_xml_5g, generar_site_equipment_xml_5g
from functions_5G.node_generator import generar_node_mos_5g
from functions_5G.carrier_cell_generator import generar_carrier_cell_mos_5g
from functions_5G.NR_Relation_Parametros import generar_nr_relation_parametros_5g
from functions_5G.generator_master_5G import generate_master_script_5g
# CORRECCIÓN AQUÍ: Importar la función correcta
from functions_5G.enrollment_generator_5G import generar_create_identity_xml_5g, generar_cmedit_enrollment_5g 

# =====================================================================
# FUNCIÓN PRINCIPAL DE GENERACIÓN DEL ZIP PARA 5G
# =====================================================================
def generar_archivos_zip_5g(
    nemonico: str,
    release: str,
    trama: str,
    region: str,
    wsh_file: Any,
    rnd_file: Any = None,
    ip_oam: str = "" # Se mantiene por compatibilidad con app.py, pero usamos wsh_data
) -> Tuple[Optional[bytes], str, Optional[Dict[str, str]]]:
    """
    Genera el paquete ZIP con archivos de terreno, remotos y enrollment para 5G NR.
    """
    
    nem = nemonico.upper()

    # 1) LEER ARCHIVO WSH
    wsh_data, error_message = leer_datos_wsh_5g(wsh_file, nemonico)
    if not wsh_data:
        return None, error_message, None

    # 2) GENERACIÓN DE ARCHIVOS TERRENO
    folder_terreno = f"00.{nem}_Terreno"
    folder_remoto = f"01.{nem}_Remoto"
    folder_enrollment = f"02.{nem}_Enrollment"  # Nombre de carpeta corregido
    release_path = release + ("/" if not release.endswith("/") else "")
    
    summary_xml = f"""<summary:AutoIntegrationRbsSummaryFile
    xmlns:summary="http://www.ericsson.se/RbsSummaryFileSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.ericsson.se/RbsSummaryFileSchemaSummaryFile.xsd">
<Format revision="F"/>
<ConfigurationFiles
    siteBasicFilePath="01_{nem}_SiteBasic.xml"
    siteEquipmentFilePath="02_{nem}_SiteEquipment.xml"
    upgradePackageFilePath="{release_path}"/>
</summary:AutoIntegrationRbsSummaryFile>"""

    site_basic_xml = generar_site_basic_xml_5g(nemonico, trama, wsh_data)
    site_equipment_xml = generar_site_equipment_xml_5g(trama)
    
    # ======================================================
    # 3) GENERACIÓN DE ARCHIVOS DE ENROLLMENT
    # ======================================================
    create_identity_xml = generar_create_identity_xml_5g(nemonico)
    
    # CORRECCIÓN: Usamos la función correcta y pasamos wsh_data
    cmedit_enrollment_content = generar_cmedit_enrollment_5g(nemonico, region, wsh_data)
    
    # ======================================================
    # 4) GENERACIÓN DE ARCHIVOS REMOTOS (MOS) & LECTURA RND
    # ======================================================
    node_mos_content = ""
    carrier_cell_mos_content = ""
    nr_relation_param_mos_content = ""
    master_script_content = ""
    rnd_data = None 

    if rnd_file:
        # LECTURA CENTRALIZADA DE HOJAS DEL RND
        rnd_data, error_message = leer_rnd_sheets_5g(rnd_file)
        if not rnd_data:
            return None, error_message, None

        # 01_NODE_MOS
        node_mos_content = generar_node_mos_5g(nemonico, wsh_data, rnd_data) 
        
        # 02_CARRIER_CELL_MOS
        carrier_cell_mos_content = generar_carrier_cell_mos_5g(nemonico, wsh_data, rnd_data) 

        # 03_NR_RELATION_PARAM_MOS
        nr_relation_param_mos_content = generar_nr_relation_parametros_5g(nemonico, wsh_data, rnd_data) 
        
        # 00_MASTER_SCRIPT
        master_script_content = generate_master_script_5g(nemonico)

    # ======================================================
    # 5) GENERAR ZIP
    # ======================================================
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        # ---- TERRENO ----
        zip_file.writestr(f"{folder_terreno}/00_{nem}_RbsSummaryFile.xml", summary_xml)
        zip_file.writestr(f"{folder_terreno}/01_{nem}_SiteBasic.xml", site_basic_xml)
        zip_file.writestr(f"{folder_terreno}/02_{nem}_SiteEquipment.xml", site_equipment_xml)
        
        # ---- REMOTO ----
        if master_script_content:
            zip_file.writestr(f"{folder_remoto}/00_MASTER_RAN_PL_NR.mo", master_script_content)
        
        if node_mos_content:
            zip_file.writestr(f"{folder_remoto}/01_{nem}_NR_Transport_Node.mos", node_mos_content)
        
        if carrier_cell_mos_content:
            zip_file.writestr(f"{folder_remoto}/02_{nem}_NR_HW_CELL.mos", carrier_cell_mos_content) 

        if nr_relation_param_mos_content:
            zip_file.writestr(f"{folder_remoto}/03_{nem}_NR_RELATION_PARAM.mos", nr_relation_param_mos_content) 
        
        # ---- ENROLLMENT ----
        zip_file.writestr(f"{folder_enrollment}/00_Create_Identity.xml", create_identity_xml)
        # Nota: Guardamos como .mo o .txt porque es un script cmedit, no XML puro
        zip_file.writestr(f"{folder_enrollment}/01_ENM_{nem}.xml", cmedit_enrollment_content)

    zip_buffer.seek(0)

    # 6) Generación del diccionario de contenido (Para visualización en App)
    generated_content = {
        '00_SUMMARY_XML': summary_xml,
        '01_SITE_BASIC_XML': site_basic_xml,
        '02_SITE_EQUIPMENT_XML': site_equipment_xml,
        '00_CREATE_IDENTITY': create_identity_xml,
        '01_ENM_XML': cmedit_enrollment_content,
    }
    
    if master_script_content:
        generated_content['00_MASTER_SCRIPT'] = master_script_content
    
    if node_mos_content:
        generated_content['01_NODE_MOS'] = node_mos_content
    
    if carrier_cell_mos_content:
        generated_content['02_CARRIER_CELL_MOS'] = carrier_cell_mos_content

    if nr_relation_param_mos_content:
        generated_content['03_NR_RELATION_PARAM_MOS'] = nr_relation_param_mos_content

    return zip_buffer.getvalue(), f"Script_5G_{nem}.zip", generated_content