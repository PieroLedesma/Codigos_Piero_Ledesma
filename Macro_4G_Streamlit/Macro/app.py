# app.py (V5.3 - MixedMode movido al final del formulario)
# Hola Mundo

import streamlit as st
import pandas as pd 
import time

# ====================================================================
# === IMPORTAR LÓGICA DE NEGOCIO (REQUIERE generator_logic.py) ===
# ====================================================================
try:
    from generator_logic import generar_archivos_zip
except ImportError:
    st.error("🚨 Error crítico: No se encuentra el archivo 'generator_logic.py'.")
    st.stop()


# --- LISTAS ESTATICAS REQUERIDAS ---
REGIONES_CHILE = [
    "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI"
]
CONFIGURACIONES = [f"Configuración {i}" for i in range(1, 8)]

if 'generated_data' not in st.session_state:
    st.session_state['generated_data'] = None

# ====================================================================
# === FUNCIÓN CALLBACK PARA EL BOTÓN DE SUBMIT (Mantenida) ===
# ====================================================================
def handle_form_submit(rnd_file, wsh_file):
    """Ejecuta la lógica de generación del script al hacer click."""
    st.session_state['generated_data'] = None 
    
    # Recoger variables del formulario
    nemonico = st.session_state['nemonico_input_v4_4']
    release = st.session_state['release_select_v4_4']
    trama = st.session_state['trama_select_v4_4']
    region = st.session_state['region_select_v4_4']
    
    if not wsh_file:
         st.session_state['generated_data'] = {'error': "Error: Por favor, cargue el archivo WSHReport para obtener la data de red."}
         return
    
    with st.spinner('✨ Generando Terreno, Enrollment y estructura ZIP...'):
        time.sleep(0.5) 
        zip_data, result_name, generated_content = generar_archivos_zip(nemonico, release, trama, region, wsh_file)
        
    if zip_data:
        st.session_state['generated_data'] = {
            'zip_data': zip_data, 
            'zip_filename': result_name, 
            'all_content': generated_content 
        }
    else:
        st.session_state['generated_data'] = {'error': result_name}


# ====================================================================
# === 1. CONFIGURACIÓN INICIAL Y ESTILO (Estilo de píldora mantenido) ===
# ====================================================================

st.set_page_config(
    page_title="Generador de Scripts - Proyecto 4G/5G",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS Personalizado (Mantenido) ---
st.markdown("""
<style>
/* 1. ESTILO DE CABECERA Y FONDO */
.stApp { background-color: #f7f9fc; }
h1 {
    color: #4B0082;
    font-weight: 800;
    padding-bottom: 10px;
    border-bottom: 3px solid #007bff;
}

/* 2. LABELS (Etiquetas) */
div[data-testid="stForm"] label p, 
h3 {
    color: #333333;
    font-weight: 700;
}

/* 3. CONTROLES DE ENTRADA AGRUPADOS */
div[data-testid="stForm"] > div > div:nth-child(1),
div[data-testid="stForm"] > div > div:nth-child(2) {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    background-color: #ffffff;
}

/* 4. SIDEBAR (Mantenido) */
[data-testid="stSidebar"] { background-color: #e6f0ff; color: #0e1117; }

/* 5. ESTILO DE RADIO BUTTONS (Píldora compacta) */
div[data-testid="stRadio"] > label {
    background-color: transparent !important; border: none !important; box-shadow: none !important;
    color: #0e1117 !important; padding: 0px 0px; 
}

/* Etiqueta individual del radio button */
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

/* Estilo al seleccionar */
div[role="radiogroup"] > label:has(input:checked) {
    background-color: #007bff;
    border-color: #007bff; 
    font-weight: bold; 
    color: white !important;
    box-shadow: 0 2px 5px rgba(0, 123, 255, 0.3); 
}

/* 6. BOTÓN DE DESCARGA (Mantenido) */
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
# === 2. BARRA LATERAL (Mantenida) ===
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
# === 3. CONTENIDO PRINCIPAL (MixedMode movido) ===
# ====================================================================
st.header(f"⚙️ Configuración para **{script_selection}**")
st.markdown("---") 

if script_selection == 'Script 4G':
    
    # 3.1 EL FORMULARIO
    with st.form(key='script_4g_form_v4_4', clear_on_submit=False): 
        
        # --- [A] CAMPOS DE ENTRADA (Mantenidos en columnas) ---
        col1, col2 = st.columns(2)
        with col1: 
            st.subheader("Datos Básicos")
            nemonico_input = st.text_input("Némonico", placeholder="Ej: MZB884", key='nemonico_input_v4_4')
            trama_select = st.selectbox("Trama", ("TN_A", "TN_B", "TN_C", "TN_D"), key='trama_select_v4_4')
            release_select = st.selectbox(
                "Release",
                ("RadioNode_CXP9024418_15-R37E15", "RadioNode_CXP2010174_1_R40H08_21.Q4"),
                key='release_select_v4_4'
            )

        with col2: 
            st.subheader("Configuración y Región")
            region_select = st.selectbox("Región", REGIONES_CHILE, key='region_select_v4_4') 
            configuracion_select = st.selectbox("Configuración", CONFIGURACIONES, key='configuracion_select_v4_4')
            
        
        # --- [B] CARGA DE ARCHIVOS REQUERIDOS ---
        st.markdown("<h3 style='margin-top:30px;'>📤 Carga de Archivos Requeridos (CSV/Excel)</h3>", unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        with col3:
            rnd_file = st.file_uploader("Cargar RND (SiteEquipment data)", type=['xlsx', 'csv'], key='rnd_uploader_v4_4')
        with col4:
            wsh_file = st.file_uploader("Cargar WSHReport (SiteBasic data)", type=['xlsx', 'csv'], key='wsh_uploader_v4_4')

        # --- [C] MIXED MODE (Movido al final) ---
        st.markdown("<h3 style='margin-top:30px;'>📡 Modo de Operación</h3>", unsafe_allow_html=True)
        
        mixed_mode_radio = st.radio(
            "MixedMode", 
            ('No', 'Sí'),
            index=0, 
            horizontal=True, 
            key='mixed_mode_radio_v4_4'
        )
        
        if mixed_mode_radio == 'Sí':
            st.warning("🚨 MixedMode Activo. Por favor, cargue el archivo ATND.")
            col_atnd, _, _ = st.columns([1, 2, 2])
            with col_atnd: 
                atnd_file = st.file_uploader("Cargar ATND", type=['xlsx', 'csv'], key='atnd_uploader_v4_4')
        else:
            atnd_file = None 
            
        st.markdown("---") 
        
        # Botón de submit
        st.form_submit_button(
            label='🤖 Generar Script',
            help="Presiona para iniciar la generación del script.",
            type="primary",
            on_click=handle_form_submit,
            args=(rnd_file, wsh_file)
        )


    # 3.2 LÓGICA DE DESCARGA (Mantenida)
    st.markdown("---")
    
    if st.session_state['generated_data'] and 'zip_data' in st.session_state['generated_data']:
        data = st.session_state['generated_data']
        
        st.success(f"✅ ¡Archivos generados con éxito para **{st.session_state['nemonico_input_v4_4']}**!")
        
        col_download, _, _ = st.columns([1, 2, 1])
        with col_download:
            st.download_button(
                label="⬇️ Descargar ZIP Final",
                data=data['zip_data'],
                file_name=data['zip_filename'],
                mime="application/zip",
                type="secondary"
            )
        
        # Mostrar contenidos generados en debug (Mantenido con claves XML)
        with st.expander("Ver Contenido XML/YAML Generado (Debug)"):
            st.subheader("📁 00-NEMONICO_Terreno")
            st.code(data['all_content']['00_SUMMARY_XML'], language='xml')
            st.code(data['all_content']['01_SITE_BASIC_XML'], language='xml')
            st.code(data['all_content']['02_SITE_EQUIPMENT_XML'], language='xml')
            
            st.subheader("📁 02-Enrollment_Nemonico")
            
            # --- LÍNEA CORREGIDA (SE ELIMINA 'label') ---
            st.code(data['all_content']['00_CREATE_IDENTITY_XML'], language='xml') 
            
            # --- LÍNEA CORREGIDA (SE ELIMINA 'label') ---
            st.code(data['all_content']['01_LTE_ENM_XML'], language='text')

            
    elif st.session_state['generated_data'] and 'error' in st.session_state['generated_data']:
        st.error(st.session_state['generated_data']['error'])
        st.session_state['generated_data'] = None 


    # 3.3 BOTÓN DE RECARGA (Mantenido)
    st.markdown("---")
    col_recharge, _, _ = st.columns([1, 2, 1])
    with col_recharge:
        if st.button("Limpiar Formulario (Reiniciar)", help="Reinicia la aplicación para limpiar todos los campos.", key='recharge_button_v4_4'):
            st.session_state['generated_data'] = None
            st.rerun()


# === 4. PLACEHOLDERS (Mantenido) ===
elif script_selection == 'Script 5G':
    st.info("Configuración 5G: Pendiente. Pronto disponible.")
    
elif script_selection == 'Script 3G':
    st.info("Configuración 3G: Pendiente. Pronto disponible.")