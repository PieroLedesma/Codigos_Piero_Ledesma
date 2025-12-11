# ===========================================================================
# functions_Relation/data_reader_relation.py
# ===========================================================================

import pandas as pd
from typing import Dict, Any

def leer_datos_relacion(uploaded_file: Any) -> Dict[str, pd.DataFrame]:
    """
    Lee todas las hojas de un archivo Excel cargado por Streamlit de forma dinámica.

    Args:
        uploaded_file: Objeto de archivo cargado por st.file_uploader.

    Returns:
        Un diccionario donde las claves son los nombres de las hojas y los valores
        son DataFrames de pandas.
    """
    if uploaded_file is None:
        return {"error": "No se proporcionó archivo para la lectura."}

    # Usamos io.BytesIO para leer el archivo cargado directamente en pandas
    try:
        # sheet_name=None indica a pandas que lea todas las hojas
        all_sheets_data = pd.read_excel(
            uploaded_file, 
            sheet_name=None, 
            engine='openpyxl'
        )
        
        # Opcional: Limpieza o normalización básica (ej. nombres de columna en minúsculas)
        processed_data = {}
        for sheet_name, df in all_sheets_data.items():
            # Aquí podrías añadir lógica de validación/limpieza
            processed_data[sheet_name] = df.copy() 
            
        print(f"DEBUG: Hojas leídas con éxito: {list(processed_data.keys())}")
        return processed_data

    except Exception as e:
        print(f"ERROR: Falló la lectura del archivo Excel: {e}")
        return {"error": f"Falló la lectura del archivo Excel. Asegúrate de que es un .xlsx válido. Detalle: {e}"}

# ===========================================================================