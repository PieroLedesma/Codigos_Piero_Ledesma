import pandas as pd
import streamlit as st

# ==============================================================================
# 1. FUNCIÓN DE EXTRACCIÓN Y VALIDACIÓN DEL EXCEL
# ==============================================================================

def extraer_parametros(uploaded_file, parametros_manuales):
    """
    Lee un archivo Excel (Hoja '2G-3G') y extrae los parámetros de red 
    necesarios, combinándolos con los parámetros manuales del formulario.
    """
    
    # 1. Validación de Archivo Subido
    if uploaded_file is None:
        return {'error': "❌ Error: Por favor, sube el archivo Excel para continuar."}

    try:
        # 2. Lectura del Excel
        # Intentamos leer la hoja '2G-3G', que es la que se usa en el VBA
        df = pd.read_excel(uploaded_file, sheet_name='2G-3G', engine='openpyxl') 
        
        # 3. Normalización de Encabezados (¡LA SOLUCIÓN A TU PROBLEMA!)
        # Elimina espacios, convierte a mayúsculas y reemplaza guiones bajos por espacios.
        # Esto nos asegura que 'Mask', ' Mask ', 'mask', o 'M A S K' sean tratados como 'MASK'.
        df.columns = df.columns.str.strip().str.upper().str.replace('_', ' ')
        
        # 4. Extraer Fila de Datos
        # Asumimos que los datos de la celda que importan están en la segunda fila (índice 1)
        if df.shape[0] < 2:
            return {'error': "❌ Error: La hoja '2G-3G' debe tener al menos una fila de encabezados (Fila 1) y una fila de datos (Fila 2)."}
            
        data_row = df.iloc[1] # Fila 2 de Excel = índice 1 de Pandas
        
        # 5. Extracción de los 11 Parámetros de Red
        
        # Diccionario de búsqueda: El valor debe ser el encabezado LIMPIO en MAYÚSCULAS
        campos_requeridos = {
            'IP_OAM': 'IP OAM',
            'MASK': 'MASK',
            'NEMONICO': 'NEMONICO',
            'IP_TRAFICO': 'IP IUB IP CONTROL', # Ajustado basado en un nombre común de VBA
            'VLAN_OAM': 'VLAN OAM',
            'VLAN_IUB': 'VLAN IUB',
            'DGW_Iub_IP_OAM': 'DGW IUB IP OAM',
            'DGW_Iub_IP': 'DGW IUB IP',
            # Los campos NTP y PE se pasan desde parametros_manuales
        }
        
        parametros_excel = {}
        missing_fields = []

        for key_python, header_excel in campos_requeridos.items():
            try:
                # Intenta extraer el valor (Convertimos el valor a string para evitar problemas de formato)
                valor = str(data_row[header_excel])
                
                # Validación simple: No debe ser 'nan' (vacío)
                if valor.lower() in ('nan', 'none', ''):
                    missing_fields.append(header_excel)
                
                parametros_excel[key_python] = valor
            except KeyError:
                # Esto atrapará si la columna no existe o tiene un nombre inesperado
                missing_fields.append(header_excel)

        if missing_fields:
            return {'error': f"❌ Error: Faltan las siguientes columnas en la Fila 1 del Excel o están vacías en la Fila 2: {', '.join(missing_fields)}. Revisa mayúsculas, minúsculas y espacios."}

        # 6. Combinar Parámetros Manuales y de Excel
        parametros_finales = {**parametros_manuales, **parametros_excel}
        return parametros_finales
        
    except FileNotFoundError:
        return {'error': "❌ Error: Archivo no encontrado. Vuelve a subir el Excel."}
    except ValueError:
         return {'error': "❌ Error: No se pudo leer la hoja '2G-3G'. Verifica el nombre de la hoja."}
    except Exception as e:
        return {'error': f"❌ Error general al leer el Excel: {e}. Revisa el formato y contenido de la hoja '2G-3G'."}


# ==============================================================================
# 2. FUNCIÓN DE GENERACIÓN DEL SCRIPT
# ==============================================================================

def generar_script(data, template):
    """
    Rellena la plantilla de script con los datos proporcionados.
    """
    
    # 1. Ajuste de variables SYNC (para que el template solo use 1 y 2 si no es 'N/A')
    # Nota: Las plantillas se construyeron para usar {SYNC_1} y {SYNC_2} sin 'N/A', 
    # por lo que esto asegura que se usen si son valores válidos (1, 7, 2, 8).
    
    # Esta parte asume que el reemplazo solo necesita hacerse si el valor NO es N/A.
    # Dado que los comandos DELETE/ACTION usan {SYNC_1} y {SYNC_2} directamente como parte de una MO
    # la mejor práctica es pasar los valores tal como están.
    
    # Rellenar la plantilla con todos los datos
    try:
        # Usa el método format para rellenar todas las llaves {CLAVE} en la plantilla
        script_content = template.format(**data)
        return script_content
    except KeyError as e:
        # Captura si falta una llave en los datos (ej: {IP_OAM} no se encontró)
        return f"ERROR DE GENERACIÓN: Falta el parámetro {e} necesario para la plantilla. Vuelva a subir el Excel y verifique que todos los campos requeridos existen."
    except Exception as e:
        return f"ERROR FATAL al generar el script: {e}"