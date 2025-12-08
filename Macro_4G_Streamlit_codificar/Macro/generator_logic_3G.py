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
from functions_3G.generator_parametros_3G import generate_parametros_mos
from functions_3G.RNC_iub_generator import generate_rnc_iub_mos
from functions_3G.utrancell_generator import generate_utrancell_mos
from functions_3G.utranrelation_generator import generate_utranrelation_mos
from functions_3G.msc_generator import generate_msc_mos
from functions_3G.cna_generator import generate_cna_import
from functions_3G.enrollment_generator_3G import generate_create_identity_xml, generate_enm_xml

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
        
        # Generar Parámetros MOS
        print("DEBUG: Generating Parametros MOS...")
        success_parametros, mos_parametros, msg_parametros = generate_parametros_mos(
            nemonico=nemonico_upper,
            wsh_data=wsh_data,
            rnd_data=rnd_data
        )
        
        if success_parametros:
            print(f"DEBUG: Parametros MOS generated successfully")
        else:
            print(f"DEBUG: Warning - Parametros MOS generation failed: {msg_parametros}")
            mos_parametros = f"// ERROR: No se pudo generar Parametros MOS\n// {msg_parametros}"
            
        # Generar RNC IUB MOS
        print("DEBUG: Generating RNC IUB MOS...")
        success_rnc, mos_rnc, rnc_val, filename_rnc = generate_rnc_iub_mos(
            nemonico=nemonico_upper,
            rnd_data=rnd_data,
            wsh_data=wsh_data
        )
        
        if success_rnc:
             print(f"DEBUG: RNC IUB MOS generated successfully")
        else:
             print(f"DEBUG: Warning - RNC IUB MOS generation failed")
             mos_rnc = "// ERROR: No se pudo generar RNC IUB MOS"
             rnc_val = "UNKNOWN_RNC"

        # Generar UtranCell MOS
        print("DEBUG: Generating UtranCell MOS...")
        try:
            success_utran, mos_utran, filename_utran = generate_utrancell_mos(
                nemonico=nemonico_upper,
                rnd_data=rnd_data
            )
            print(f"DEBUG: UtranCell result - Success: {success_utran}, Filename: {filename_utran}")
        except Exception as e:
            print(f"DEBUG: Exception in generate_utrancell_mos: {e}")
            success_utran = False
            mos_utran = f"// ERROR: Exception in UtranCell: {e}"
            filename_utran = "ERROR_UTRANCELL.mos"
        
        if success_utran:
             print(f"DEBUG: UtranCell MOS generated successfully")
        else:
             print(f"DEBUG: Warning - UtranCell MOS generation failed")
             mos_utran = "// ERROR: No se pudo generar UtranCell MOS"

        # Generar UtranRelation MOS
        print("DEBUG: Generating UtranRelation MOS...")
        success_rel, mos_rel, filename_rel = generate_utranrelation_mos(
            rnd_data=rnd_data,
            rnc_value=rnc_val,
            nemonico=nemonico_upper
        )

        if success_rel:
             print(f"DEBUG: UtranRelation MOS generated successfully")
        else:
             print(f"DEBUG: Warning - UtranRelation MOS generation failed")
             mos_rel = "// ERROR: No se pudo generar UtranRelation MOS"

        # Generar MSC MOS
        print("DEBUG: Generating MSC MOS...")
        try:
            success_msc, mos_msc, filename_msc = generate_msc_mos(
                rnd_data=rnd_data,
                rnc_value=rnc_val,
                nemonico=nemonico_upper
            )
            print(f"DEBUG: MSC result - Success: {success_msc}, Filename: {filename_msc}")
        except Exception as e:
            print(f"DEBUG: Exception in generate_msc_mos: {e}")
            success_msc = False
            mos_msc = f"// ERROR: Exception in MSC: {e}"
            filename_msc = "ERROR_MSC.mos"
        
        if success_msc:
             print(f"DEBUG: MSC MOS generated successfully")
        else:
             print(f"DEBUG: Warning - MSC MOS generation failed")
             mos_msc = "// ERROR: No se pudo generar MSC MOS"

        # Generar CNA Import
        print("DEBUG: Generating CNA Import...")
        try:
            success_cna, cna_content, filename_cna = generate_cna_import(
                rnd_data=rnd_data,
                rnc_value=rnc_val,
                nemonico=nemonico_upper
            )
            print(f"DEBUG: CNA result - Success: {success_cna}, Filename: {filename_cna}")
        except Exception as e:
            print(f"DEBUG: Exception in generate_cna_import: {e}")
            success_cna = False
            cna_content = f"// ERROR: Exception in CNA: {e}"
            filename_cna = "ERROR_CNA.import"
        
        if success_cna:
             print(f"DEBUG: CNA Import generated successfully")
        else:
             print(f"DEBUG: Warning - CNA Import generation failed")
             cna_content = "// ERROR: No se pudo generar CNA Import"

        # Generar Enrollment XML
        print("DEBUG: Generating Enrollment XML...")
        try:
            success_enroll, xml_identity, filename_identity = generate_create_identity_xml(
                nemonico=nemonico_upper
            )
            print(f"DEBUG: Enrollment result - Success: {success_enroll}, Filename: {filename_identity}")
        except Exception as e:
            print(f"DEBUG: Exception in generate_create_identity_xml: {e}")
            success_enroll = False
            xml_identity = f"<!-- ERROR: Exception in Enrollment: {e} -->"
            filename_identity = "ERROR_Identity.xml"
        
        if success_enroll:
             print(f"DEBUG: Enrollment XML generated successfully")
        else:
             print(f"DEBUG: Warning - Enrollment XML generation failed")
             xml_identity = "<!-- ERROR: No se pudo generar Enrollment XML -->"

        # Generar ENM XML
        print("DEBUG: Generating ENM XML...")
        try:
            ip_oam = wsh_data.get('IP_OAM', 'UNKNOWN_IP')
            success_enm, xml_enm, filename_enm = generate_enm_xml(
                nemonico=nemonico_upper,
                rnc_value=rnc_val,
                ip_oam=ip_oam
            )
            print(f"DEBUG: ENM result - Success: {success_enm}, Filename: {filename_enm}")
        except Exception as e:
            print(f"DEBUG: Exception in generate_enm_xml: {e}")
            success_enm = False
            xml_enm = f"<!-- ERROR: Exception in ENM: {e} -->"
            filename_enm = "ERROR_ENM.xml"
        
        if success_enm:
             print(f"DEBUG: ENM XML generated successfully")
        else:
             print(f"DEBUG: Warning - ENM XML generation failed")
             xml_enm = "<!-- ERROR: No se pudo generar ENM XML -->"

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
            
            # Carpeta de Nodo (01_nodo_{nemonico})
            carpeta_nodo = f"01_nodo_{nemonico_upper}/"
            zip_file.writestr(
                f"{carpeta_nodo}00_{nemonico_upper}_PL_Nodeid.mos",
                mos_nodeid.encode('utf-8')
            )
            
            # Agregar Sector MOS
            if mos_sector and "ERROR" not in mos_sector:
                zip_file.writestr(
                    f"{carpeta_nodo}01_{nemonico_upper}_PL_Sector.mos",
                    mos_sector.encode('utf-8')
                )
            
            # Agregar Parametros MOS
            if mos_parametros and "ERROR" not in mos_parametros:
                zip_file.writestr(
                    f"{carpeta_nodo}02_{nemonico_upper}_PL_Parametros.mos",
                    mos_parametros.encode('utf-8')
                )
                
            # Agregar RNC IUB MOS y UtranCell MOS
            # Carpeta: 02_RNC_{RNC_Value}_{Nemonico}
            if success_rnc: # Usamos rnc_val obtenido aquí para la carpeta
                folder_rnc = f"02_RNC_{rnc_val}_{nemonico_upper}"
                
                if mos_rnc:
                    zip_file.writestr(
                        f"{folder_rnc}/{filename_rnc}",
                        mos_rnc.encode('utf-8')
                    )
                
                if success_utran and mos_utran:
                    zip_file.writestr(
                        f"{folder_rnc}/{filename_utran}",
                        mos_utran.encode('utf-8')
                    )
                
                if success_rel and mos_rel:
                    zip_file.writestr(
                        f"{folder_rnc}/{filename_rel}",
                        mos_rel.encode('utf-8')
                    )
                
                if success_msc and mos_msc:
                    zip_file.writestr(
                        f"{folder_rnc}/{filename_msc}",
                        mos_msc.encode('utf-8')
                    )
                
                if success_cna and cna_content:
                    zip_file.writestr(
                        f"{folder_rnc}/{filename_cna}",
                        cna_content.encode('utf-8')
                    )
            
            # Carpeta de Enrollment (03_Enrroll_Nemonico)
            carpeta_enroll = f"03_Enrroll_{nemonico_upper}/"
            if success_enroll and xml_identity:
                zip_file.writestr(
                    f"{carpeta_enroll}{filename_identity}",
                    xml_identity.encode('utf-8')
                )
                
                if success_enm and xml_enm:
                    zip_file.writestr(
                        f"{carpeta_enroll}{filename_enm}",
                        xml_enm.encode('utf-8')
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
            '01_Sector': mos_sector,
            '02_Parametros': mos_parametros,
            '03_RNC_IUB': mos_rnc,
            '04_UtranCell': mos_utran,
            '05_UtranRelation': mos_rel,
            '06_MSC': mos_msc,
            '07_CNA': cna_content,
            '08_Enrollment_Identity': xml_identity,
            '09_Enrollment_ENM': xml_enm
        }
        
        return zip_bytes, zip_filename, all_content
        
    except Exception as e:
        return None, "", {'error': f'Error inesperado durante la generación: {str(e)}'}
