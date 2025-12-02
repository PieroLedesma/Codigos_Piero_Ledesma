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
except ImportError as e:
    st.error(f"🚨 Error crítico: No se encuentra el archivo de lógica de generación: {e}")
    st.stop()


# --- LISTAS ESTATICAS REQUERIDAS ---
REGIONES_CHILE = [
    "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI"
]
# MODIFICACIÓN CLAVE: Se reemplaza la lista de opciones por la única opción fija
CONFIGURACIONES = ["Configuración Básica A-B-C (Fija)"] 

if 'generated_data' not in st.session_state:
    st.session_state['generated_data'] = None

if 'generated_data_5g' not in st.session_state:
    st.session_state['generated_data_5g'] = None

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
        ('Script 4G', 'Script 5G', 'Script 3G'),
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

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Datos Básicos")
            nemonico_input = st.text_input("Némonico", placeholder="Ej: MZB884", key='nemonico_input_v4_4')
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
        col3, col4 = st.columns(2)
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

        col_mixed, col_tipo_sitio = st.columns(2)
        
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

        col1, col2 = st.columns(2)
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
        col3_5g, col4_5g = st.columns(2)
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

        st.success(f"✅ ¡Archivos de terreno 5G NR generados con éxito para **{nemonico_display}**!")

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
    st.info("Configuración 3G: Pendiente. Pronto disponible.")
