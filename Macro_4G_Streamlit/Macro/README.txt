
🏗️ Estructura del Directorio

Generador_Macros/
├── app.py                      # 🌐 Interfaz de Usuario (Streamlit UI)
├── generator_logic.py          # 🧠 Lógica Principal: Procesamiento de archivos y orquestación
├── functions/
│   ├── data_processor.py       # 📊 Funciones para leer y extraer datos de WSHReport/RND.
│   ├── file_writer.py          # 💾 Funciones para empaquetar archivos y generar el ZIP.
│   ├── enrollment_generator.py # 📝 Generación del contenido XML de Enrollment (Identidad y Conectividad).
│   └── terreno_generator.py    # 📝 Generación del contenido XML de Terreno (Site Basic/Equipment).
├── data/
│   └── [Aquí van archivos estáticos o plantillas futuras]
├── README.md                   # 📄 Este archivo.
└── requirements.txt            # 📦 Dependencias de Python.

📝 Archivos Clave Generados

[NEMONICO_UPPER]_FullScript.zip
├── 00.[NEMONICO]_Terreno
│   ├── 01_[NEMONICO]_SiteBasic.xml       # Configuración básica (Trama, IP OAM, Equipment=1)
│   └── 02_[NEMONICO]_SiteEquipment.xml   # Configuración de HW (Tarjetas, Radios, Puertos)
└── 02-Enrollment_[NEMONICO]
    ├── 00_Create_Identity.xml            # Creación de identidad y certificado (Contenido XML).
    └── 01_LTE_ENM_[NEMONICO].xml         # Comandos CMEDIT de conectividad (IP OAM, User/Pass, Heartbeat).



 1. Requisitos de Python
Instala las librerías necesarias (asumiendo que usas pandas y streamlit):

Bash

pip install -r requirements.txt
(El archivo requirements.txt debe contener al menos: streamlit, pandas)

2. Ejecución de la Aplicación
Ejecuta el archivo principal app.py usando Streamlit:

Bash

streamlit run app.py
Esto abrirá la aplicación en tu navegador predeterminado (generalmente en http://localhost:8501).

📦 requirements.txt
streamlit
pandas
openpyxl