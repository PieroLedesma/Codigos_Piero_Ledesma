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
from functions_3G.oam_generator_3G import generate_oam_xml
from functions_3G.hw_xml_customizer import customize_hw_xml
from functions_3G.iub_generator_duw import generate_iub_duw_mo
from functions_3G.parametros_generator_duw import generate_parametros_duw_txt
from functions_3G.generador_Siteeqm import generar_site_equipment_auto


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
    configuracion: str = "Configuración Básica 3G",
    tipo_3g: str = "BB"
) -> Tuple[Optional[bytes], str, Optional[Dict[str, str]]]:
    """
    Genera el ZIP con archivos de terreno 3G WCDMA.
    
    Args:
        tipo_3g: Tipo de generación '3G-BB' (BaseStation) o '3G-DUW' (DualUnitWCDMA)
    
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
        
        # Leer RND (Requerido para RNC en DUW, opcional solo para terreno en BB)
        print("DEBUG: Reading RND...")
        rnd_data, error_rnd = leer_rnd_sheets_3g(rnd_file)
        
        # En modo DUW, si hay RND file pero falla la lectura, es un problema
        if tipo_3g == "DUW" and rnd_file and error_rnd:
            print(f"ERROR: Failed to read RND in DUW mode: {error_rnd}")
            return None, "", {'error': f'Error reading RND file (required for DUW mode): {error_rnd}'}
        
        # En modo BB, solo warning si falla RND
        if tipo_3g == "BB" and error_rnd:
            print(f"DEBUG: Warning reading RND: {error_rnd} - Proceeding anyway for Terrain scripts")
        
        # Verificar que rnd_data no sea None
        if rnd_data is None:
            print("WARNING: rnd_data is None, initializing as empty dict")
            rnd_data = {}
        
        print(f"DEBUG: RND data loaded: {len(rnd_data)} sheets") 
        
        nemonico_upper = nemonico.upper()
        
        # Inicializar xml_oam (puede ser sobreescrito en modo DUW)
        xml_oam = ""
        mo_iub = ""  # Inicializar IUB MO (solo para DUW)
        txt_parametros = ""  # Inicializar parámetros TXT (solo para DUW)
        
        # Inicializar variables de contenido opcional
        xml_site_equipment_auto = ""
        hw_template_content = ""
        
        # ===== 2. GENERAR CONTENIDOS XML Y MOS =====
        # SOLO para modo BB - En modo DUW solo se genera OAM
        if tipo_3g == "BB":
            print("DEBUG: Generating XMLs and MOS for BB mode...")
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
                print(f"DEBUG: UtranCell result - Success: {success_utran}, Filename:{filename_utran}")
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
        else:
            # Modo DUW: Generar archivos RNC, pero NO terreno ni nodo básico
            print("DEBUG: DUW mode - Generating RNC files, skipping terreno and basic node files")
            
            # No generar archivos de terreno y nodo básico
            xml_rbssummary = ""
            xml_sitebasic = ""
            xml_siteequipment = ""
            mos_nodeid = ""
            mos_sector = ""
            mos_parametros = ""
            
            # No generar enrollment
            success_enroll = False
            xml_identity = ""
            filename_identity = ""
            success_enm = False
            xml_enm = ""
            filename_enm = ""
            
            # SÍ GENERAR ARCHIVOS RNC
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

            print("DEBUG: Generating UtranCell MOS...")
            try:
                success_utran, mos_utran, filename_utran = generate_utrancell_mos(
                    nemonico=nemonico_upper,
                    rnd_data=rnd_data
                )
                print(f"DEBUG: UtranCell result - Success: {success_utran}, Filename:{filename_utran}")
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

        # ===== 3. CREAR ESTRUCTURA ZIP =====
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            
            # ===== MODO 3G-BB: Generar carpetas de terreno y nodo completo =====
            if tipo_3g == "BB":
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
            
            # ===== MODO 3G-DUW: Solo generar carpeta de nodo con OAM y configuración HW =====
            else:  # tipo_3g == "DUW"
                print("DEBUG: Generando estructura para modo 3G-DUW")
                
                # Generar archivo OAM
                success_oam, xml_oam, filename_oam = generate_oam_xml(
                    nemonico=nemonico_upper,
                    wsh_data=wsh_data,
                    trama=trama
                )
                
                if not success_oam:
                    print(f"WARNING: Error generando OAM: {xml_oam}")
                
                # Carpeta de Nodo DUW (01_nodo_{nemonico})
                carpeta_nodo_duw = f"01_nodo_{nemonico_upper}/"
                
                # Agregar archivo OAM como primer archivo
                if success_oam and xml_oam:
                    zip_file.writestr(
                        f"{carpeta_nodo_duw}{filename_oam}",
                        xml_oam.encode('utf-8')
                    )
                
                # Generar archivo IUB para DUW
                print("DEBUG: Generating IUB MO for DUW...")
                success_iub, mo_iub, filename_iub = generate_iub_duw_mo(
                    nemonico=nemonico_upper,
                    wsh_data=wsh_data,
                    rnd_data=rnd_data
                )
                
                if success_iub and mo_iub:
                    zip_file.writestr(
                        f"{carpeta_nodo_duw}{filename_iub}",
                        mo_iub.encode('utf-8')
                    )
                    print(f"DEBUG: IUB MO generated successfully: {filename_iub}")
                else:
                    print(f"WARNING: Could not generate IUB MO")
                
                # Generar archivo de parámetros para DUW
                print("DEBUG: Generating parametros TXT for DUW...")
                success_param, txt_param, filename_param = generate_parametros_duw_txt(
                    nemonico=nemonico_upper,
                    wsh_data=wsh_data,
                    rnd_data=rnd_data
                )
                
                if success_param and txt_param:
                    txt_parametros = txt_param  # Guardar para all_content
                    zip_file.writestr(
                        f"{carpeta_nodo_duw}{filename_param}",
                        txt_param.encode('utf-8')
                    )
                    print(f"DEBUG: Parametros TXT generated successfully: {filename_param}")
                else:
                    print(f"WARNING: Could not generate parametros TXT")
                
                # Agregar archivo de configuración HW_DUW seleccionado o generar automático
                import os
                
                xml_site_equipment_auto = "" # Reiniciar para DUW
                
                if configuracion == "Automático":
                    print("DEBUG: Generating automatic Site Equipment...")
                    success_seqm, xml_seqm, filename_seqm = generar_site_equipment_auto(
                        nemonico=nemonico_upper,
                        wsh_data=wsh_data,
                        rnd_data=rnd_data
                    )
                    if success_seqm:
                        xml_site_equipment_auto = xml_seqm
                        # Usar el nombre retornado (ya incluye el 00_) y sin prefijo adicional
                        zip_file.writestr(
                            f"{carpeta_nodo_duw}{filename_seqm}",
                            xml_seqm.encode('utf-8')
                        )
                        print(f"DEBUG: Added automatic Site Equipment file: {filename_seqm}")
                    else:
                        print(f"WARNING: Could not generate automatic Site Equipment")
                else:
                    # Lógica existente para archivos estáticos
                    hw_duw_path = os.path.join(
                        os.path.dirname(os.path.dirname(__file__)),  # Retroceder a la raíz del proyecto
                        "HW_DUW",
                        "SITE_2022",
                        configuracion  # configuracion contiene el nombre del archivo (ej: "00.SITE_3x1_RRU_3G900_CON_RETU.xml")
                    )
                    
                    print(f"DEBUG: Reading HW configuration from: {hw_duw_path}")
                    
                    if os.path.exists(hw_duw_path):
                        with open(hw_duw_path, 'r', encoding='utf-8') as f:
                            hw_template_content = f.read()
                        
                        # Agregar al ZIP usando contenido original del template
                        zip_file.writestr(
                            f"{carpeta_nodo_duw}01_{configuracion}",
                            hw_template_content.encode('utf-8')
                        )
                        print(f"DEBUG: Added HW configuration file: {configuracion}")
                    else:
                        print(f"WARNING: HW configuration file not found: {hw_duw_path}")

                
                # Agregar carpeta de RNC en modo DUW también
                if success_rnc:
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
            '09_Enrollment_ENM': xml_enm,
            '10_OAM_XML': xml_oam if tipo_3g == "DUW" else "",  # Solo para DUW
            '11_HW_Config': configuracion if tipo_3g == "DUW" else "",  # Solo para DUW
            '12_IUB_MO': mo_iub if tipo_3g == "DUW" and 'mo_iub' in locals() else "",  # Solo para DUW
            '13_PARAMETROS_TXT': txt_parametros if tipo_3g == "DUW" else "",  # Solo para DUW
            '14_SITE_EQUIPMENT_AUTO_XML': xml_site_equipment_auto if tipo_3g == "DUW" and configuracion == "Automático" else "",
            '15_HW_TEMPLATE_CONTENT': hw_template_content if tipo_3g == "DUW" and configuracion != "Automático" else ""
        }
        
        return zip_bytes, zip_filename, all_content
        
    except Exception as e:
        error_msg = f"Error inesperado durante la generación: {str(e)}"
        print(f"ERROR: {error_msg}")
        return None, error_msg, {'error': error_msg}
