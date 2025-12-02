# =====================================================================
# generator_logic.py (VERSIÓN FINAL + GUtranRelation)
# =====================================================================

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
from functions.utran_relation_generator import generar_utran_relation_mos
from functions.eutran_relation_generator import generate_eutran_relation_mos
from functions.Gutran_relation_generator import generate_gutran_relation_mos
from functions.parametros_generator import generate_parametros_mos
from functions.tilt_generator import generate_tilt_mos   # <--- NUEVO TILT
from functions.generator_master import generate_master_script_mo  # <--- NUEVO MASTER



# =====================================================================
# FUNCIÓN PRINCIPAL DE GENERACIÓN DEL ZIP
# =====================================================================
def generar_archivos_zip(
    nemonico: str,
    release: str,
    trama: str,
    region: str,
    wsh_file: Any,
    rnd_file_xlsx: Any,
    tipo_sitio: str = "Normal (MM/Macro)"  # Nuevo parámetro
) -> Tuple[Optional[bytes], str, Optional[Dict[str, str]]]:

    nem = nemonico.upper()

    # ======================================================
    # 1) LEER ARCHIVO WSH
    # ======================================================
    wsh_data, error_message = leer_datos_wsh_lte(wsh_file, nemonico)
    if not wsh_data:
        return None, error_message, None

    ip_oam = wsh_data.get('IP_OAM_LTE', '0.0.0.0')

    # ======================================================
    # 2) LEER EXCEL RND
    # ======================================================
    try:
        df_cell = pd.read_excel(
            rnd_file_xlsx,
            sheet_name='Cell-Carrier',
            engine='openpyxl'
        )
        df_cell.columns = df_cell.columns.str.strip()

    except Exception as e:
        return None, f"Error al leer hoja 'Cell-Carrier' del RND XLSX: {e}", None

    # ======================================================
    # 3) GENERACIÓN DE ARCHIVOS TERRENO Y ENROLLMENT
    # ======================================================
    folder_terreno = f"00-{nem}_Terreno"
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

    site_basic_xml = generar_site_basic_xml(nemonico, trama, wsh_data)
    site_equipment_xml = generar_site_equipment_xml(trama)

    folder_enroll = f"02-Enrollment_{nem}"
    identity_xml = generar_create_identity_yml(nemonico)
    lte_enm_xml = generar_lte_enm_xml(nemonico, region, ip_oam)

    # ======================================================
    # 4) GENERACIÓN DE ARCHIVOS REMOTOS (MOS)
    # ======================================================
    folder_remotos = f"01-{nem}_Script_Remotos"

    # 00. Hardware (RRUS / AAS)
    hardware_mos = generar_hardware_mos(nemonico, wsh_data, trama, rnd_file_xlsx, tipo_sitio)

    # 01. Celdas LTE
    cell_mos = generate_cell_config_mos(nemonico, df_cell)

    # 02. UTRAN RELATIONS
    utran_mos = generar_utran_relation_mos(nemonico, rnd_file_xlsx)
    utran_filename = f"02_{nem}_UtranRelation.mos"

    # 03. EUTRAN RELATIONS
    try:
        eutran_mos = generate_eutran_relation_mos(rnd_file_xlsx, nemonico, release)
    except Exception as e:
        eutran_mos = f"// ERROR AL GENERAR EUTRAN RELATION: {e}"

    eutran_filename = f"03_{nem}_EUtranRelation.mos"

    # 04. GUTRAN RELATIONS (NUEVO)
    try:
        gutran_mos = generate_gutran_relation_mos(rnd_file_xlsx, nemonico, release)
        gutran_filename = f"04_{nem}_GUtranRelation.mos"
    except Exception as e:
        gutran_mos = f"// ERROR AL GENERAR GUtranRelation: {e}"
        gutran_filename = f"04_{nem}_GUtranRelation.mos"

    # 05. PARAMETROS (NUEVO)
    try:
        parametros_mos = generate_parametros_mos(nemonico, rnd_file_xlsx)
        parametros_filename = f"05_{nem}_Parametros.mos"
    except Exception as e:
        parametros_mos = f"// ERROR AL GENERAR PARAMETROS: {e}"
        parametros_filename = f"05_{nem}_Parametros.mos"

    # 06. TILT (NUEVO)
    try:
        tilt_mos = generate_tilt_mos(nemonico, rnd_file_xlsx)
        tilt_filename = f"06_{nem}_Tilt.mos"
    except Exception as e:
        tilt_mos = f"// ERROR AL GENERAR TILT: {e}"
        tilt_filename = f"06_{nem}_Tilt.mos"

    # 07. MASTER SCRIPT (NUEVO)
    try:
        master_mo = generate_master_script_mo(nemonico)
        master_filename = f"00_MASTER_RAN_PL_LTE.mo"
    except Exception as e:
        master_mo = f"// ERROR AL GENERAR MASTER SCRIPT: {e}"
        master_filename = f"00_MASTER_RAN_PL_LTE.mo"

    # ======================================================
    # 5) GENERAR ZIP
    # ======================================================
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:

        # ---- TERRENO ----
        zip_file.writestr(f"{folder_terreno}/00_{nem}_RbsSummaryFile.xml", summary_xml)
        zip_file.writestr(f"{folder_terreno}/01_{nem}_SiteBasic.xml", site_basic_xml)
        zip_file.writestr(f"{folder_terreno}/02_{nem}_SiteEquipment.xml", site_equipment_xml)

        # ---- ENROLLMENT ----
        zip_file.writestr(f"{folder_enroll}/00_Create_Identity.xml", identity_xml)
        zip_file.writestr(f"{folder_enroll}/01_LTE_ENM_{nem}.xml", lte_enm_xml)

        # ---- REMOTOS ----
        zip_file.writestr(f"{folder_remotos}/{master_filename}", master_mo)   # <--- NUEVO MASTER
        zip_file.writestr(f"{folder_remotos}/00_{nem}_Hardware.mos", hardware_mos)
        zip_file.writestr(f"{folder_remotos}/01_{nem}_EUtranCellFDD.mos", cell_mos)
        zip_file.writestr(f"{folder_remotos}/{utran_filename}", utran_mos)
        zip_file.writestr(f"{folder_remotos}/{eutran_filename}", eutran_mos)
        zip_file.writestr(f"{folder_remotos}/{gutran_filename}", gutran_mos)
        zip_file.writestr(f"{folder_remotos}/{parametros_filename}", parametros_mos)
        zip_file.writestr(f"{folder_remotos}/{tilt_filename}", tilt_mos)   # <--- NUEVO TILT

    zip_buffer.seek(0)

    generated_content = {
        '00_SUMMARY_XML': summary_xml,
        '01_SITE_BASIC_XML': site_basic_xml,
        '02_SITE_EQUIPMENT_XML': site_equipment_xml,
        '00_CREATE_IDENTITY_XML': identity_xml,
        '01_LTE_ENM_XML': lte_enm_xml,
        '00_MASTER_MO': master_mo,   # <--- NUEVO MASTER
        '00_HARDWARE_MOS': hardware_mos,
        '01_EUtranCellFDD_MOS': cell_mos,
        '02_UtranRelation_MOS': utran_mos,
        '03_EUtranRelation_MOS': eutran_mos,
        '04_GUtranRelation_MOS': gutran_mos,
        '05_Parametros_MOS': parametros_mos,
        '06_Tilt_MOS': tilt_mos   # <--- NUEVO TILT
    }

    return zip_buffer.getvalue(), f"Scripts_4G_{nem}.zip", generated_content
