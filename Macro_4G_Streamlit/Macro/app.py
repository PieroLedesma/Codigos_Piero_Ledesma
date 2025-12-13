# app.py (V5.4 - Final con RND Único)
# Hola Mundo

import streamlit as st
import pandas as pd
import time
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# ====================================================================
# === IMPORTAR LÓGICA DE NEGOCIO (REQUIERE generator_logic.py) ===
# ====================================================================
try:
    from generator_logic import generar_archivos_zip
    from generator_logic_5G import generar_archivos_zip_5g
    from generator_logic_relation import generar_archivos_relation
except ImportError as e:
    st.error(f"🚨 Error crítico: No se encuentra el archivo de lógica de generación: {e}")
    st.stop()


# --- LISTAS ESTATICAS REQUERIDAS ---
REGIONES_CHILE = [
    "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI"
]
# MODIFICACIÓN CLAVE: Se reemplaza la lista de opciones por la única opción fija
CONFIGURACIONES = ["Configuración Básica A-B-C (Fija)"] 
CONFIGURACIONES_3G = ["Configuración Básica 3G"]

# Configuraciones 3G-DUW (archivos de la carpeta HW_DUW/SITE_2022)
CONFIGURACIONES_3G_DUW = [
    "00.SITE_1X1_RRU_3G900.xml",
    "00.SITE_2X1_RRU_3G900.xml",
    "00.SITE_2x1_4415_CON_RETU_RHHT_BUENO.xml",
    "00.SITE_2x1_4415_MMR.xml",
    "00.SITE_2x1_4415_Sin_RETU.xml",
    "00.SITE_2x1_RRU_3G900_CON_RETU.xml",
    "00.SITE_3G900_TMF_3Sectores_CON_RRU.xml",
    "00.SITE_3X1_4415_RHHT.xml",
    "00.SITE_3X1_900_6102.xml",
    "00.SITE_3X1_900_6102_ARETU.xml",
    "00.SITE_3X2_4415_CON_RHHT.xml",
    "00.SITE_3X2_4415_SIN_RETU_SIN_MMR.xml",
    "00.SITE_3x1_4415_MMR.xml",
    "00.SITE_3x1_4415_MMR_v2_SINSUP.xml",
    "00.SITE_3x1_4415_SIN_MMR.xml",
    "00.SITE_3x1_6601_RRUS_900.xml",
    "00.SITE_3x1_6601_RRUS_dualduw_1900.xml",
    "00.SITE_3x1_AIR21.xml",
    "00.SITE_3x1_RBS6201V2W.xml",
    "00.SITE_3x1_RBS6201V2W_ARETU.xml",
    "00.SITE_3x1_RRU4415_MMR_22Q2.xml",
    "00.SITE_3x1_RRU_3G1900_CON_RETU.xml",
    "00.SITE_3x1_RRU_3G1900_SIN_RETU.xml",
    "00.SITE_3x1_RRU_3G900_CON_RETU.xml",
    "00.SITE_3x1_RRU_3G900_SIN_RETU.xml",
    "00.SITE_3x1_RRU_RETU_BANDA_A.xml",
    "00.SITE_3x2_6601_RRUS_900.xml",
    "00.SITE_3x2_RRU4415_MMR.xml",
    "00.SITE_PSI_3SECTORES_1TMF_FQBAND_9521_9471.xml",
    "00.SITE_PSI_3SECTORES_1TMF_FQBAND_9571_9471.xml",
    "00.Site3x2_RRUW_CON_ARETU.xml",
    "00.Site3x2_RRUW_CON_RETU_W16_DELAY_OK.xml",
    "00.Site_3x1_bandaA_AIR21_1DUW.xml",
    "00.site_3x2_RRU_RETU_BANDA_A_SRETU.xml",
    "00.CAB_6601_900_3x2_w18.xml",
    "00.CAB_6601_dual.xml",
    "00.CAB_900.xml",
    "00.CAB_RBS6201V2W.xml",
    "16.Create_Site_Equipment_URM355_B2conARETU.xml",
    "16.Create_Site_Equipment_URM355_in_SAER06.xml",
    "UGE643_cabinet.xml",
    "URM643_cabinet.xml",
    "URM643_site_2Tx.xml"
]

if 'generated_data' not in st.session_state:
    st.session_state['generated_data'] = None

if 'generated_data_5g' not in st.session_state:
    st.session_state['generated_data_5g'] = None

if 'generated_data_3g' not in st.session_state:
    st.session_state['generated_data_3g'] = None

if 'generated_data_atnd' not in st.session_state:
    st.session_state['generated_data_atnd'] = None

if 'generated_data_relation' not in st.session_state:
    st.session_state['generated_data_relation'] = None

# ====================================================================
# === FUNCIÓN CALLBACK PARA EL BOTÓN DE SUBMIT (CORREGIDA - RND ÚNICO) ===
# ====================================================================
# Acepta DOS ARCHIVOS: RND (usado para SiteEquipment/Node) y WSH
def handle_form_submit(rnd_file_global, wsh_file):
    """Ejecuta la lógica de generación del script al hacer click."""
    st.session_state['generated_data'] = None

    # Recoger variables del formulario
    nemonico = st.session_state['nemonico_input_v4_4']
    release = st.session_state['release_select_v4_4']
    trama = st.session_state['trama_select_v4_4']
    region = st.session_state['region_select_v4_4']
    tipo_sitio = st.session_state['tipo_sitio_radio_v4_4']  # Nuevo: capturar tipo de sitio

    if not wsh_file:
        st.session_state['generated_data'] = {'error': "Error: Por favor, cargue el archivo WSHReport para obtener la data de red."}
        return
    
    if not rnd_file_global:
        st.session_state['generated_data'] = {'error': "Error: Por favor, cargue el archivo RND (Excel) completo."}
        return

    with st.spinner('✨ Generando Terreno, Enrollment y estructura ZIP...'):
        time.sleep(0.5)
        
        # LLAMADA CON TIPO_SITIO
        zip_data, result_name, generated_content = generar_archivos_zip(
            nemonico, 
            release, 
            trama, 
            region, 
            wsh_file, 
            rnd_file_global,
            tipo_sitio  # Nuevo parámetro
        )

    if zip_data:
        st.session_state['generated_data'] = {
            'zip_data': zip_data,
            'zip_filename': result_name,
            'all_content': generated_content
        }
    else:
        st.session_state['generated_data'] = {'error': result_name}


# ====================================================================
# === FUNCIÓN CALLBACK PARA EL BOTÓN DE SUBMIT 5G ===
# ====================================================================
def handle_form_submit_5g(wsh_file_5g, rnd_file_5g):
    """Ejecuta la lógica de generación del script 5G (TERRENO) al hacer click."""
    st.session_state['generated_data_5g'] = None

    # Recoger variables del formulario 5G
    nemonico = st.session_state['nemonico_input_5g_v1']
    release = st.session_state['release_select_5g_v1']
    trama = st.session_state['trama_select_5g_v1']
    region = st.session_state['region_select_5g_v1']

    if not wsh_file_5g:
        st.session_state['generated_data_5g'] = {'error': "Error: Por favor, cargue el archivo WSHReport para 5G."}
        return
        
    if not rnd_file_5g:
        st.session_state['generated_data_5g'] = {'error': "Error: Por favor, cargue el archivo RND para 5G."}
        return

    with st.spinner('✨ Generando archivos de terreno y remotos 5G NR...'):
        time.sleep(0.5)
        
        # LLAMADA A GENERADOR 5G
        zip_data, result_name, generated_content = generar_archivos_zip_5g(
            nemonico, 
            release, 
            trama, 
            region, 
            wsh_file_5g,
            rnd_file_5g
        )

    if zip_data:
        st.session_state['generated_data_5g'] = {
            'zip_data': zip_data,
            'zip_filename': result_name,
            'all_content': generated_content
        }
    else:
        st.session_state['generated_data_5g'] = {'error': result_name}


# ====================================================================
# === FUNCIÓN CALLBACK PARA SUBMIT 3G ===
# ====================================================================
def handle_form_submit_3g(wsh_file_3g, rnd_file_3g):
    """Ejecuta la lógica de generación de scripts 3G al hacer click."""
    print("DEBUG: handle_form_submit_3g CALLED")
    from generator_logic_3G import generar_archivos_zip_3g
    
    st.session_state['generated_data_3g'] = None
    
    # Recoger variables del formulario
    nemonico = st.session_state['nemonico_input_3g_v1']
    trama = st.session_state['trama_select_3g_v1']
    tipo_3g = st.session_state.get('tipo_3g_radio_v1', '3G-BB')  # Nuevo: capturar tipo 3G
    
    # Solo leer release, region, configuracion si es modo BB
    if tipo_3g == '3G-BB':
        release = st.session_state['release_select_3g_v1']
        region = st.session_state['region_select_3g_v1']
        configuracion = st.session_state['configuracion_select_3g_v1']
    else:
        # Para DUW, usar configuración seleccionada del selector
        release = "RadioNode_CXP9024418_15_R53M22_22.Q2"
        region = "XIII"
        configuracion = st.session_state.get('configuracion_duw_select_3g_v1', CONFIGURACIONES_3G_DUW[0])
    
    print(f"DEBUG: Inputs - Nemonico: {nemonico}, Trama: {trama}, Tipo: {tipo_3g}, Release: {release}, Configuracion: {configuracion}")
    
    if not wsh_file_3g:
        print("DEBUG: No WSH file provided")
        st.session_state['generated_data_3g'] = {'error': "Falta archivo WSH"}
        return

    # Generar archivos
    print("DEBUG: Calling generar_archivos_zip_3g...")
    
    # Convertir tipo_3g a formato esperado por generador: "BB" o "DUW"
    tipo_param = "DUW" if tipo_3g == "3G-DUW" else "BB"
    
    zip_data, result_name, generated_content = generar_archivos_zip_3g(
        nemonico=nemonico,
        trama=trama,
        release=release,
        region=region,
        wsh_file=wsh_file_3g,
        rnd_file=rnd_file_3g,
        configuracion=configuracion,
        tipo_3g=tipo_param  # Nuevo parámetro
    )
    print(f"DEBUG: Result - Zip: {bool(zip_data)}, Name: {result_name}")
    
    if zip_data:
        st.session_state['generated_data_3g'] = {
            'zip_data': zip_data,
            'zip_filename': result_name,
            'all_content': generated_content
        }
    else:
        st.session_state['generated_data_3g'] = {'error': result_name}


# ====================================================================
# === FUNCIÓN CALLBACK PARA SUBMIT ATND BB ===
# ====================================================================
def handle_form_submit_atnd(atnd_file):
    """Ejecuta la lógica de generación de scripts ATND BB al hacer click."""
    print("DEBUG: handle_form_submit_atnd CALLED")
    from generator_logic_atnd import generar_archivos_atnd
    
    st.session_state['generated_data_atnd'] = None
    
    # Recoger variables del formulario
    nemonico = st.session_state['nemonico_input_atnd_v1']
    
    print(f"DEBUG: Inputs - Nemonico: {nemonico}")
    
    if not atnd_file:
        print("DEBUG: No ATND file provided")
        st.session_state['generated_data_atnd'] = {'error': "Falta archivo ATND"}
        return
    
    if not nemonico:
        print("DEBUG: No nemonico provided")
        st.session_state['generated_data_atnd'] = {'error': "Falta némónico"}
        return
    
    # Generar archivos ATND
    print("DEBUG: Calling generar_archivos_atnd...")
    with st.spinner('✨ Procesando archivo ATND y generando ZIP...'):
        zip_data, zip_filename, generated_content = generar_archivos_atnd(
            nemonico=nemonico.upper(),
            atnd_file=atnd_file
        )
    
    print(f"DEBUG: Result - ZIP: {bool(zip_data)}, Name: {zip_filename}")
    
    if zip_data:
        st.session_state['generated_data_atnd'] = {
            'zip_data': zip_data,
            'zip_filename': zip_filename,
            'all_content': generated_content
        }
    else:
        error_msg = generated_content.get('error', 'Error desconocido') if generated_content else 'Error al generar archivo'
        st.session_state['generated_data_atnd'] = {'error': error_msg}

# ====================================================================
# === FUNCIÓN CALLBACK PARA SUBMIT RELATION LTE->3G (CORREGIDA) ===
# ====================================================================
def handle_form_submit_relation(relation_file):
    """Ejecuta la lógica de generación de scripts de Relaciones LTE->3G."""
    
    print("DEBUG: handle_form_submit_relation CALLED")
    
    st.session_state['generated_data_relation'] = None
    
    # 1. Recoger variables del formulario (se lee nemonico DENTRO del callback)
    # ESTA LÍNEA ES CLAVE: Funciona porque el widget ya se renderizó.
    try:
        nemonico = st.session_state['nemonico_input_relation_v1']
    except KeyError:
        st.session_state['generated_data_relation'] = {'error': "Error: No se encontró el Némónico. Intente recargar la página."}
        return

    if not nemonico:
        st.session_state['generated_data_relation'] = {'error': "Falta el némónico"}
        return # Detiene la ejecución

    if not relation_file:
        st.session_state['generated_data_relation'] = {'error': "Falta el archivo de Excel de Relaciones"}
        return # Detiene la ejecución

    # 2. LLAMADA A GENERADOR DE RELACIONES
    print("DEBUG: Calling generar_archivos_relation...")
    with st.spinner('✨ Procesando archivo de Relaciones y generando script MOS...'):
        zip_data, zip_filename, generated_content = generar_archivos_relation(
            nemonico=nemonico.upper(),
            relation_file=relation_file # Usamos el argumento de la función
        )

    # 3. Guardar Resultados
    if zip_data:
        st.session_state['generated_data_relation'] = {
            'zip_data': zip_data,
            'zip_filename': zip_filename,
            'all_content': generated_content
        }
    else:
        error_msg = generated_content.get('error', 'Error desconocido') if generated_content else 'Error al generar archivo'
        st.session_state['generated_data_relation'] = {'error': error_msg}


# ====================================================================
# === 1. CONFIGURACIÓN INICIAL Y ESTILO (Estilo de píldora mantenido) ===
# ====================================================================

st.set_page_config(
    page_title="Generador de Scripts - Proyecto 4G/5G",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ====================================================================
# === AUTHENTICATION SETUP ===
# ====================================================================

# Initialize authenticator with correct API for v0.3+
try:
    authenticator = stauth.Authenticate(
        st.secrets["credentials"].to_dict(),
        st.secrets["cookie"]["name"],
        st.secrets["cookie"]["key"],
        st.secrets["cookie"]["expiry_days"]
    )
except Exception as e:
    st.error(f"Error loading authentication configuration: {e}")
    st.stop()

# Login widget
try:
    authenticator.login(location='main')
except Exception as e:
    st.error(f"Login error: {e}")
    st.stop()

# Check authentication status
if st.session_state.get("authentication_status") == False:
    st.error('Usuario/Contraseña incorrectos')
    st.stop()
elif st.session_state.get("authentication_status") is None:
    st.warning('Por favor ingrese su usuario y contraseña')
    st.stop()

# If authenticated, show logout button in sidebar
if st.session_state.get("authentication_status"):
    with st.sidebar:
        st.write(f'Bienvenido *{st.session_state.get("name")}*')
        authenticator.logout(location='sidebar')

# --- CSS Personalizado ---
st.markdown("""
<style>
.stApp { background-color: #f7f9fc; }
h1 {
    color: #4B0082;
    font-weight: 800;
    padding-bottom: 10px;
    border-bottom: 3px solid #007bff;
}
div[data-testid="stForm"] label p,
h3 {
    color: #333333;
    font-weight: 700;
}
div[data-testid="stForm"] > div > div:nth-child(1),
div[data-testid="stForm"] > div > div:nth-child(2) {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    background-color: #ffffff;
}
[data-testid="stSidebar"] { background-color: #e6f0ff; color: #0e1117; }
div[data-testid="stRadio"] > label {
    background-color: transparent !important; border: none !important; box-shadow: none !important;
    color: #0e1117 !important; padding: 0px 0px;
}
div[role="radiogroup"] > label {
    input[type="radio"] { visibility: hidden; width: 0px; height: 0px; margin: 0; }
    background-color: #f0f2f6;
    color: #333333;
    padding: 8px 15px;
    margin: 5px;
    border-radius: 20px;
    border: 1px solid #c0c0c0;
    width: auto;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    transition: all 0.2s;
    font-weight: 500;
    cursor: pointer;
}
div[role="radiogroup"] > label:has(input:checked) {
    background-color: #007bff;
    border-color: #007bff;
    font-weight: bold;
    color: white !important;
    box-shadow: 0 2px 5px rgba(0, 123, 255, 0.3);
}
.stDownloadButton button {
    background-color: #28a745;
    color: white;
    font-weight: bold;
    border-radius: 25px;
    padding: 10px 30px;
    transition: all 0.3s;
}
.stDownloadButton button:hover {
    background-color: #218838;
}
.stMarkdown { margin-top: 0px; margin-bottom: 0px; }
</style>
""", unsafe_allow_html=True)



# ====================================================================
# === 2. BARRA LATERAL ===
# ====================================================================
with st.sidebar:
    st.markdown("<h3 style='text-align: center; color: #007bff;'>🚀 Tipo de Script</h3>", unsafe_allow_html=True)
    script_selection = st.radio(
        "Elige la tecnología:",
        ('Script 4G', 'Script 5G', 'Script 3G', 'ATND BB', 'Relation LTE->3G'),
        index=0,
        key='sidebar_selection_v4_4'
    )

# ====================================================================
# === 3. CONTENIDO PRINCIPAL ===
# ====================================================================
st.header(f"⚙️ Configuración para **{script_selection}**")
st.markdown("---")

if script_selection == 'Script 4G':

    # 3.1 FORMULARIO
    with st.form(key='script_4g_form_v4_4', clear_on_submit=False):

        col1, col2, _ = st.columns([2, 2, 1])
        with col1:
            st.subheader("Datos Básicos")
            nemonico_input = st.text_input("Némonico", placeholder="Ej: MXXXXX - GXXXXX - PXXXXX", key='nemonico_input_v4_4')
            trama_select = st.selectbox("Trama", ("TN_A", "TN_B", "TN_C", "TN_D","TN_IDL_B","TN_IDL_A"), key='trama_select_v4_4')
            release_select = st.selectbox(
                "Release",
                ("RadioNode_CXP9024418_15-R37E15", "RadioNode_CXP2010174_1_R40H08_21.Q4"),
                key='release_select_v4_4'
            )

        with col2:
            st.subheader("Configuración y Región")
            region_select = st.selectbox("Región", REGIONES_CHILE, key='region_select_v4_4')
            configuracion_select = st.selectbox("Configuración", CONFIGURACIONES, key='configuracion_select_v4_4')

        # CARGA DE ARCHIVOS
        st.markdown("<h3 style='margin-top:30px;'>📤 Carga de Archivos Requeridos (Excel)</h3>", unsafe_allow_html=True)
        col3, col4, _ = st.columns([2, 2, 1])
        with col3:
            rnd_file_global = st.file_uploader(
                "1. Cargar RND Completo (Archivo único .xlsx)", 
                type=['xlsx'], 
                key='rnd_uploader_v4_4_global'
            )
        with col4:
            wsh_file = st.file_uploader(
                "2. Cargar WSHReport (Archivo único .xlsx)", 
                type=['xlsx'], 
                key='wsh_uploader_v4_4'
            )

        # MIXED MODE
        st.markdown("<h3 style='margin-top:30px;'>📡 Modo de Operación</h3>", unsafe_allow_html=True)

        col_mixed, col_tipo_sitio, _ = st.columns([2, 2, 1])
        
        with col_mixed:
            mixed_mode_radio = st.radio(
                "MixedMode",
                ('No', 'Sí'),
                index=0,
                horizontal=True,
                key='mixed_mode_radio_v4_4'
            )
        
        with col_tipo_sitio:
            tipo_sitio_radio = st.radio(
                "Tipo de Sitio",
                ('Normal (Macro)', 'P (MM/AS)'),
                index=0,
                horizontal=True,
                key='tipo_sitio_radio_v4_4',
                help="Selecciona 'P' para sitios con Active Antenna Systems (AAS)"
            )

        if mixed_mode_radio == 'Sí':
            st.warning("🚨 MixedMode Activo. Por favor, cargue el archivo ATND.")
            col_atnd, _, _ = st.columns([1, 2, 2])
            with col_atnd:
                atnd_file = st.file_uploader("Cargar ATND", type=['xlsx', 'csv'], key='atnd_uploader_v4_4')
        else:
            atnd_file = None

        st.markdown("---")

        # BOTÓN SUBMIT
        st.form_submit_button(
            label='🤖 Generar Script',
            help="Presiona para iniciar la generación del script.",
            type="primary",
            on_click=handle_form_submit,
            args=(rnd_file_global, wsh_file)
        )

    # 3.2 DESCARGA
    st.markdown("---")

    if st.session_state['generated_data'] and 'zip_data' in st.session_state['generated_data']:
        data = st.session_state['generated_data']
        nemonico_display = st.session_state['nemonico_input_v4_4'].upper()

        st.success(f"✅ ¡Archivos generados con éxito para **{nemonico_display}**!")

        col_download, _, _ = st.columns([1, 2, 1])
        with col_download:
            st.download_button(
                label="⬇️ Descargar ZIP Final",
                data=data['zip_data'],
                file_name=data['zip_filename'],
                mime="application/zip",
                type="secondary"
            )

        # DEBUG EXPANDER
        with st.expander("Ver Contenido XML/YAML/MOS Generado (Debug)"):

            # TERRENO
            st.subheader(f"📁 00-{nemonico_display}_Terreno")
            st.markdown(f"**00_{nemonico_display}_RbsSummaryFile.xml**")
            st.code(data['all_content']['00_SUMMARY_XML'], language='xml')

            st.markdown(f"**01_{nemonico_display}_SiteBasic.xml**")
            st.code(data['all_content']['01_SITE_BASIC_XML'], language='xml')

            st.markdown(f"**02_{nemonico_display}_SiteEquipment.xml**")
            st.code(data['all_content']['02_SITE_EQUIPMENT_XML'], language='xml')

            # ENROLLMENT
            st.subheader(f"📁 02-Enrollment_{nemonico_display}")
            st.markdown("**00_Create_Identity.xml**")
            st.code(data['all_content']['00_CREATE_IDENTITY_XML'], language='xml')

            st.markdown(f"**01_LTE_ENM_{nemonico_display}.xml**")
            st.code(data['all_content']['01_LTE_ENM_XML'], language='xml')

            # REMOTOS
            st.subheader(f"📁 01-{nemonico_display}_Script_Remotos")
            
            # Master script (solo si existe en el contenido generado)
            if '00_MASTER_MO' in data['all_content']:
                st.markdown(f"**00_MASTER_RAN_PL_LTE.mo**")
                st.code(data['all_content']['00_MASTER_MO'], language='text')

            st.markdown(f"**00_{nemonico_display}_Hardware.mos**")
            st.code(data['all_content']['00_HARDWARE_MOS'], language='text')

            st.markdown(f"**01_{nemonico_display}_EUtranCellFDD.mos**")
            st.code(data['all_content']['01_EUtranCellFDD_MOS'], language='text')

            st.markdown(f"**02_{nemonico_display}_UtranRelation.mos**")
            st.code(data['all_content']['02_UtranRelation_MOS'], language='text')

            st.markdown(f"**03_{nemonico_display}_EUtranRelation.mos**")
            st.code(data['all_content']['03_EUtranRelation_MOS'], language='text')

            st.markdown(f"**04_{nemonico_display}_GUtranRelation.mos**")
            st.code(data['all_content']['04_GUtranRelation_MOS'], language='text')

            st.markdown(f"**05_{nemonico_display}_Parametros.mos**")
            st.code(data['all_content']['05_Parametros_MOS'], language='text')

            st.markdown(f"**06_{nemonico_display}_Tilt.mos**")
            st.code(data['all_content']['06_Tilt_MOS'], language='text')

    # ERRORES
    elif st.session_state['generated_data'] and 'error' in st.session_state['generated_data']:
        st.error(st.session_state['generated_data']['error'])
        st.session_state['generated_data'] = None

    # LIMPIAR
    st.markdown("---")
    col_recharge, _, _ = st.columns([1, 2, 1])
    with col_recharge:
        if st.button("Limpiar Formulario (Reiniciar)", help="Reinicia la aplicación para limpiar todos los campos.", key='recharge_button_v4_4'):
            st.session_state['generated_data'] = None
            st.rerun()


# PLACEHOLDERS
elif script_selection == 'Script 5G':
    
    # 3.1 FORMULARIO 5G
    with st.form(key='script_5g_form_v1', clear_on_submit=False):

        col1, col2, _ = st.columns([2, 2, 1])
        with col1:
            st.subheader("Datos Básicos")
            nemonico_input_5g = st.text_input("Nemonico", placeholder="Ej: NXXXXX", key='nemonico_input_5g_v1')
            trama_select_5g = st.selectbox("Trama", ("TN_IDL_A", "TN_IDL_B", "TN_IDL_C"), key='trama_select_5g_v1')
            release_select_5g = st.selectbox(
                "Release",
                ("RadioNode_CXP2010174_1_R40H08_21.Q4",),
                key='release_select_5g_v1'
            )

        with col2:
            st.subheader("Región")
            region_select_5g = st.selectbox("Región", REGIONES_CHILE, key='region_select_5g_v1')

        # CARGA DE ARCHIVOS
        st.markdown("<h3 style='margin-top:30px;'>📤 Carga de Archivos Requeridos</h3>", unsafe_allow_html=True)
        col3_5g, col4_5g, _ = st.columns([2, 2, 1])
        with col3_5g:
            wsh_file_5g = st.file_uploader(
                "1. Cargar WSHReport (Archivo .xlsx con hoja '5G')", 
                type=['xlsx'], 
                key='wsh_uploader_5g_v1'
            )
        with col4_5g:
            rnd_file_5g = st.file_uploader(
                "2. Cargar RND (Archivo .xlsx)", 
                type=['xlsx'], 
                key='rnd_uploader_5g_v1'
            )

        st.markdown("---")

        # BOTÓN SUBMIT - CONECTADO AL CALLBACK
        st.form_submit_button(
            label='🤖 Generar Script 5G',
            help="Presiona para iniciar la generación de archivos de terreno y remotos 5G.",
            type="primary",
            on_click=handle_form_submit_5g,
            args=(wsh_file_5g, rnd_file_5g)
        )

    # 3.2 DESCARGA
    st.markdown("---")

    if st.session_state['generated_data_5g'] and 'zip_data' in st.session_state['generated_data_5g']:
        data = st.session_state['generated_data_5g']
        nemonico_display = st.session_state['nemonico_input_5g_v1'].upper()

        st.success(f"✅ ¡Archivos 5G NR generados con éxito para **{nemonico_display}**!")

        col_download, _, _ = st.columns([1, 2, 1])
        with col_download:
            st.download_button(
                label="⬇️ Descargar ZIP Final 5G",
                data=data['zip_data'],
                file_name=data['zip_filename'],
                mime="application/zip",
                type="secondary"
            )

        # DEBUG EXPANDER
        with st.expander("Ver Contenido XML Generado 5G (Debug)"):

            # TERRENO
            st.subheader(f"📁 00.{nemonico_display}_Terreno")
            st.markdown(f"**00_{nemonico_display}_RbsSummaryFile.xml**")
            st.code(data['all_content']['00_SUMMARY_XML'], language='xml')

            st.markdown(f"**01_{nemonico_display}_SiteBasic.xml**")
            st.code(data['all_content']['01_SITE_BASIC_XML'], language='xml')

            st.markdown(f"**02_{nemonico_display}_SiteEquipment.xml**")
            st.code(data['all_content']['02_SITE_EQUIPMENT_XML'], language='xml')
            
# 01_NODE_MOS
            st.markdown(f"**01_{nemonico_display}_NR_Transport_Node.mos**")
            st.code(data['all_content']['01_NODE_MOS'], language='text')

            # 02_CARRIER_CELL_MOS (NUEVO ARCHIVO)
            # Verificamos específicamente este segundo archivo antes de acceder a la clave
            if '02_CARRIER_CELL_MOS' in data['all_content']: 
                st.markdown(f"**02_{nemonico_display}_NR_HW_CELL.mos**")
                st.code(data['all_content']['02_CARRIER_CELL_MOS'], language='text')

            # 03_NR_RELATION_PARAM_MOS (NUEVO ARCHIVO)
            # Verificamos específicamente este tercer archivo antes de acceder a la clave
            if '03_NR_RELATION_PARAM_MOS' in data['all_content']: 
                st.markdown(f"**03_{nemonico_display}_NR_RELATION_PARAM.mos**")
                st.code(data['all_content']['03_NR_RELATION_PARAM_MOS'], language='text')

    # ERRORES
    elif st.session_state['generated_data_5g'] and 'error' in st.session_state['generated_data_5g']:
        st.error(st.session_state['generated_data_5g']['error'])
        st.session_state['generated_data_5g'] = None

    # LIMPIAR
    st.markdown("---")
    col_recharge_5g, _, _ = st.columns([1, 2, 1])
    with col_recharge_5g:
        if st.button("Limpiar Formulario (Reiniciar)", help="Reinicia la aplicación para limpiar todos los campos.", key='recharge_button_5g_v1'):
            st.session_state['generated_data_5g'] = None
            st.rerun()


elif script_selection == 'Script 3G':
    
    # SELECTOR DE TIPO 3G (FUERA DEL FORMULARIO para permitir condicionales dinámicos)
    st.markdown("<h3 style='margin-bottom:20px;'>🔧 Tipo de Configuración 3G</h3>", unsafe_allow_html=True)
    tipo_3g_selected = st.radio(
        "Selecciona el tipo de configuración:",
        ('3G-BB', '3G-DUW'),
        index=0,
        horizontal=True,
        key='tipo_3g_radio_v1',
        help="3G-BB: BaseStation (configuración estándar), 3G-DUW: DualUnitWCDMA (sin terreno)"
    )
    
    st.markdown("---")
    
    # 3.1 FORMULARIO 3G
    with st.form(key='script_3g_form_v1', clear_on_submit=False):

        col1, col2, _ = st.columns([2, 2, 1])
        with col1:
            st.subheader("Datos Básicos")
            nemonico_input_3g = st.text_input("Nemonico", placeholder="Ej: NXXXXX", key='nemonico_input_3g_v1')
            trama_select_3g = st.selectbox("Trama", ("TN_A", "TN_B", "TN_C", "TN_IDL_A", "TN_IDL_B", "TN_IDL_C"), key='trama_select_3g_v1')
            
            # Mostrar Release solo si es BB
            if tipo_3g_selected == '3G-BB':
                release_select_3g = st.selectbox(
                    "Release",
                    ("RadioNode_CXP9024418_15_R53M22_22.Q2",),
                    key='release_select_3g_v1'
                )

        with col2:
            # Mostrar Configuración y Región solo si es BB
            if tipo_3g_selected == '3G-BB':
                st.subheader("Configuración y Región")
                region_select_3g = st.selectbox("Región", REGIONES_CHILE, key='region_select_3g_v1')
                configuracion_select_3g = st.selectbox("Configuración", CONFIGURACIONES_3G, key='configuracion_select_3g_v1')
            else:
                st.subheader("Configuración DUW")
                configuracion_duw_select = st.selectbox(
                    "Selecciona configuración HW",
                    CONFIGURACIONES_3G_DUW,
                    key='configuracion_duw_select_3g_v1',
                    help="Archivos de configuración de hardware de la carpeta HW_DUW/SITE_2022"
                )

        # CARGA DE ARCHIVOS
        st.markdown("<h3 style='margin-top:30px;'>📤 Carga de Archivos Requeridos</h3>", unsafe_allow_html=True)
        col3_3g, col4_3g, _ = st.columns([2, 2, 1])
        with col3_3g:
            wsh_file_3g = st.file_uploader(
                "1. Cargar WSHReport (Archivo .xlsx con hoja '3G')", 
                type=['xlsx'], 
                key='wsh_uploader_3g_v1'
            )
        with col4_3g:
            # RND es opcional para DUW
            label_rnd = "2. Cargar RND (Archivo .xlsx)" if tipo_3g_selected == '3G-BB' else "2. Cargar RND (Opcional para DUW)"
            rnd_file_3g = st.file_uploader(
                label_rnd, 
                type=['xlsx'], 
                key='rnd_uploader_3g_v1'
            )

        st.markdown("---")

        # BOTÓN SUBMIT - CONECTADO AL CALLBACK
        st.form_submit_button(
            label='🤖 Generar Script 3G',
            help="Presiona para iniciar la generación de archivos de terreno 3G.",
            type="primary",
            on_click=handle_form_submit_3g,
            args=(wsh_file_3g, rnd_file_3g)
        )

    # 3.2 DESCARGA Y VISUALIZACIÓN
    st.markdown("---")

    if st.session_state['generated_data_3g'] and 'zip_data' in st.session_state['generated_data_3g']:
        data = st.session_state['generated_data_3g']
        nemonico_display = st.session_state['nemonico_input_3g_v1'].upper()

        st.success(f"✅ ¡Archivos 3G generados con éxito para **{nemonico_display}**!")

        col_download, _, _ = st.columns([1, 2, 1])
        with col_download:
            st.download_button(
                label="⬇️ Descargar ZIP Final 3G",
                data=data['zip_data'],
                file_name=data['zip_filename'],
                mime="application/zip",
                type="secondary"
            )

        #DEBUG EXPANDER
        with st.expander("🔍 Ver contenido de los archivos generados"):
            # Obten el tipo seleccionado
            tipo_3g_display = st.session_state.get('tipo_3g_radio_v1', '3G-BB')
            
            # Terreno (Solo BB)
            if tipo_3g_display == '3G-BB':
                st.subheader(f"📁 00_Terreno_{nemonico_display}")
                
                st.markdown(f"**00_{nemonico_display}_RbsSummaryFile.xml**")
                st.code(data['all_content']['00_RbsSummaryFile'], language='xml')

                st.markdown(f"**01_{nemonico_display}_SiteBasic.xml**")
                st.code(data['all_content']['01_SiteBasic'], language='xml')

                st.markdown(f"**02_{nemonico_display}_SiteEquipment.xml**")
                st.code(data['all_content']['02_SiteEquipment'], language='xml')

                st.subheader(f"📁 01_Nodo_{nemonico_display}")
                st.markdown(f"**00_{nemonico_display}_PL_Nodeid.mos**")
                st.code(data['all_content']['00_NodeId'], language='text')

                if '01_Sector' in data['all_content'] and data['all_content']['01_Sector']:
                    st.markdown(f"**01_{nemonico_display}_PL_Sector.mos**")
                    st.code(data['all_content']['01_Sector'], language='text')

                if '02_Parametros' in data['all_content'] and data['all_content']['02_Parametros']:
                    st.markdown(f"**02_{nemonico_display}_PL_Parametros.mos**")
                    st.code(data['all_content']['02_Parametros'], language='text')
            
            # Nodo DUW (Solo DUW)
            else:  # 3G-DUW
                st.subheader(f"📁 01_Nodo_{nemonico_display}")
                if '10_OAM_XML' in data['all_content'] and data['all_content']['10_OAM_XML']:
                    st.markdown(f"**00_Create_Oam_{nemonico_display}.xml**")
                    st.code(data['all_content']['10_OAM_XML'], language='xml')
                
                if '12_IUB_MO' in data['all_content'] and data['all_content']['12_IUB_MO']:
                    st.markdown(f"**01_{nemonico_display}_iub.mo**")
                    st.code(data['all_content']['12_IUB_MO'], language='text')
                
                if '13_PARAMETROS_TXT' in data['all_content'] and data['all_content']['13_PARAMETROS_TXT']:
                    st.markdown(f"**02_{nemonico_display}_parametros.txt**")
                    st.code(data['all_content']['13_PARAMETROS_TXT'], language='text')
                
                if '11_HW_Config' in data['all_content'] and data['all_content']['11_HW_Config']:
                    hw_config_name = data['all_content']['11_HW_Config']
                    st.markdown(f"**03_{hw_config_name}**")
                    st.info(f"Archivo de configuración HW: {hw_config_name}")

            # RNC (Siempre se muestra)
            if '03_RNC_IUB' in data['all_content'] and data['all_content']['03_RNC_IUB']:
                st.subheader(f"📁 02_RNC_..._{nemonico_display}")
                st.markdown(f"**01_..._PL_Create_IUB.mos**")
                st.code(data['all_content']['03_RNC_IUB'], language='text')

            if '04_UtranCell' in data['all_content'] and data['all_content']['04_UtranCell']:
                st.markdown(f"**02_..._PL_UtranCell.mos**")
                st.code(data['all_content']['04_UtranCell'], language='text')

            if '05_UtranRelation' in data['all_content'] and data['all_content']['05_UtranRelation']:
                st.markdown(f"**03_..._PL_Create_Relations.mos**")
                st.code(data['all_content']['05_UtranRelation'], language='text')

            if '06_MSC' in data['all_content'] and data['all_content']['06_MSC']:
                st.markdown(f"**04_MSC_..._PL_Delete_Create_Cells.mos**")
                st.code(data['all_content']['06_MSC'], language='text')

            if '07_CNA' in data['all_content'] and data['all_content']['07_CNA']:
                st.markdown(f"**05_CNA_..._PL.import**")
                st.code(data['all_content']['07_CNA'], language='text')

            # Enrollment (Solo BB)
            if tipo_3g_display == '3G-BB':
                if '08_Enrollment_Identity' in data['all_content'] and data['all_content']['08_Enrollment_Identity']:
                    st.subheader(f"📁 03_Enrroll_{nemonico_display}")
                    st.markdown(f"**00_Create_Identity.xml**")
                    st.code(data['all_content']['08_Enrollment_Identity'], language='xml')

                if '09_Enrollment_ENM' in data['all_content'] and data['all_content']['09_Enrollment_ENM']:
                    st.markdown(f"**01_ENM_{nemonico_display}.xml**")
                    st.code(data['all_content']['09_Enrollment_ENM'], language='xml')

    # ERRORES
    elif st.session_state['generated_data_3g'] and 'error' in st.session_state['generated_data_3g']:
        st.error(st.session_state['generated_data_3g']['error'])
        st.session_state['generated_data_3g'] = None

    # LIMPIAR
    st.markdown("---")
    col_recharge_3g, _, _ = st.columns([1, 2, 1])
    with col_recharge_3g:
        if st.button("Limpiar Formulario (Reiniciar)", help="Reinicia la aplicación para limpiar todos los campos.", key='recharge_button_3g_v1'):
            st.session_state['generated_data_3g'] = None
            st.rerun()


elif script_selection == 'ATND BB':
    
    # 3.1 FORMULARIO ATND BB
    with st.form(key='script_atnd_form_v1', clear_on_submit=False):

        st.subheader("📋 Datos Básicos")
        col1, col2 = st.columns(2)
        
        with col1:
            nemonico_input_atnd = st.text_input(
                "Némónico", 
                placeholder="Ej: MXXXXX", 
                key='nemonico_input_atnd_v1',
                help="Ingrese el némónico del sitio"
            )
        
        with col2:
            st.write("")  # Espaciador

        # CARGA DE ARCHIVO ATND
        st.markdown("<h3 style='margin-top:30px;'>📤 Carga de Archivo ATND</h3>", unsafe_allow_html=True)
        col_atnd, _, _ = st.columns([2, 1, 1])
        with col_atnd:
            atnd_file_upload = st.file_uploader(
                "Cargar archivo ATND (Excel)", 
                type=['xlsx', 'xls'], 
                key='atnd_uploader_v1',
                help="Seleccione el archivo ATND en formato Excel"
            )

        st.markdown("---")

        # BOTÓN SUBMIT
        st.form_submit_button(
            label='🤖 Procesar ATND',
            help="Presiona para procesar el archivo ATND.",
            type="primary",
            on_click=handle_form_submit_atnd,
            args=(atnd_file_upload,)
        )

    # 3.2 RESULTADOS
    st.markdown("---")

    if st.session_state['generated_data_atnd'] and 'zip_data' in st.session_state['generated_data_atnd']:
        data = st.session_state['generated_data_atnd']
        nemonico_display = st.session_state['nemonico_input_atnd_v1'].upper()

        st.success(f"✅ ¡Archivos ATND generados con éxito para **{nemonico_display}**!")
        
        col_download, _, _ = st.columns([1, 2, 1])
        with col_download:
            st.download_button(
                label="⬇️ Descargar ZIP ATND",
                data=data['zip_data'],
                file_name=data['zip_filename'],
                mime="application/zip",
                type="secondary"
            )
        
        # DEBUG EXPANDER - Mostrar contenido generado
        with st.expander("🔍 Ver contenido del archivo generado"):
            st.markdown(f"**00.-{nemonico_display}_ATND_BB.txt**")
            st.code(data['all_content']['atnd_txt'], language='text')

            st.markdown("---") # Separador visual
    
            st.markdown(f"**📄 01.-{nemonico_display}_QUEUE_BB.txt**")
            st.code(data['all_content']['queue_txt'], language='text')

    # ERRORES
    elif st.session_state['generated_data_atnd'] and 'error' in st.session_state['generated_data_atnd']:
        st.error(st.session_state['generated_data_atnd']['error'])
        st.session_state['generated_data_atnd'] = None

    # LIMPIAR
    st.markdown("---")
    col_recharge_atnd, _, _ = st.columns([1, 2, 1])
    with col_recharge_atnd:
        if st.button("Limpiar Formulario (Reiniciar)", help="Reinicia la aplicación para limpiar todos los campos.", key='recharge_button_atnd_v1'):
            st.session_state['generated_data_atnd'] = None
            st.rerun()


elif script_selection == 'Relation LTE->3G':
    
    # 🚨 Importación de Lógica (Debe estar al inicio, pero la incluimos aquí por referencia)
    # from generator_logic_relation import generar_archivos_relation 
    
    # === 1. FORMULARIO RELATIONS LTE->3G ===
    with st.form(key='script_relation_form_v1', clear_on_submit=False):

        st.subheader("📋 Generación de Script de Relaciones LTE -> 3G")
        
        # PRIMERA FILA: NÉMÓNICO (Usando el ratio [2, 2, 1])
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            nemonico_input_relation = st.text_input(
                "Némónico del Sitio (LTE)", 
                placeholder="Ej: MXXXXX", 
                key='nemonico_input_relation_v1',
                help="Ingrese el némónico del sitio Macro/LTE"
            )
            # col2 y col3 quedan como espaciadores para el némónico.
            
        # SEGUNDA FILA: CARGA DE ARCHIVO (También usando el ratio [2, 2, 1])
        st.markdown("<h4 style='margin-top:20px;'>📤 Archivo de Relaciones (Excel)</h4>", unsafe_allow_html=True)
        
        col_file1, col_file2, col_file3 = st.columns([2, 2, 1])
        
        with col_file1:
            relation_file_upload = st.file_uploader(
                "Cargar Excel de Relaciones", 
                type=['xlsx', 'xls'], 
                key='relation_uploader_v1',
                help="Seleccione el archivo Excel que contiene la data de red y relaciones"
            )
        # col_file2 y col_file3 quedan como espaciadores para la carga de archivo.
        
        st.markdown("---")

        # BOTÓN SUBMIT
        st.form_submit_button(
            label='🤖 Generar Script de Relaciones',
            help="Presiona para generar el archivo .mos de relaciones LTE->3G.",
            type="primary",
            on_click=handle_form_submit_relation,
            args=(relation_file_upload,)
        )

    # === 2. RESULTADOS ===
    st.markdown("---") # <-- AQUI COMIENZA EL BLOQUE DE RESULTADOS
    
    if st.session_state['generated_data_relation'] and 'zip_data' in st.session_state['generated_data_relation']:
        data = st.session_state['generated_data_relation']
        try:
            nemonico_display = st.session_state['nemonico_input_relation_v1'].upper()
        except KeyError:
            nemonico_display = "SITIO"

        st.success(f"✅ ¡Script de Relaciones LTE->3G generado con éxito para **{nemonico_display}**!")
        
        # 1. BOTÓN DE DESCARGA: Mantenemos las columnas para centrar el botón
        col_download, _, _ = st.columns([1, 2, 1])
        with col_download:
            st.download_button(
                label="⬇️ Descargar ZIP Relaciones",
                data=data['zip_data'],
                file_name=data['zip_filename'],
                mime="application/zip",
                type="secondary"
            )
        
        # 2. DEBUG EXPANDER: Saca este bloque fuera de las columnas
        with st.expander("🔍 Ver contenido del archivo generado (Ancho Máximo)"):
            st.markdown(f"**00_PL_Relaciones_{nemonico_display}.mos**") 
            if 'relation_mos' in data['all_content']:
                st.code(data['all_content']['relation_mos'], language='text') 

    # ERRORES
    elif st.session_state['generated_data_relation'] and 'error' in st.session_state['generated_data_relation']:
        st.error(st.session_state['generated_data_relation']['error'])

    # LIMPIAR
    st.markdown("---")
    col_recharge_relation, _, _ = st.columns([1, 2, 1])
    with col_recharge_relation:
        if st.button("Limpiar Formulario (Reiniciar)", help="Reinicia la aplicación para limpiar todos los campos.", key='recharge_button_relation_v1'):
            st.rerun()