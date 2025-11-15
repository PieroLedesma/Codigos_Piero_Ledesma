from oletools.olevba import VBA_Parser
import os
import sys

# ¡MAGIA UTF-8! Soluciona el error de codificación de emojis en la consola de Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    # Esto maneja entornos antiguos o de Python 2, aunque Miniconda3 debería tenerlo.
    pass 

# Rutas a tu archivo Excel con macros (usando 'r' para rutas de Windows más seguras)
archivo_excel = r"C:\Users\pledesma\Documents\Piero Ledesma\Piero Ledesma\Nuevas Macros\Macros VBA\CAMBIO_IPS_Y_C.ELECTRICOS.xlsm"

# Carpeta donde se guardarán los módulos extraídos
carpeta_salida = r"C:\Users\pledesma\Documents\Piero Ledesma\Piero Ledesma\Nuevas Macros\Macros VBA\macros_extraidas"

# Crear carpeta si no existe
os.makedirs(carpeta_salida, exist_ok=True)

print(f"📂 Analizando archivo: {archivo_excel}")

# Analizar el archivo
try:
    vba = VBA_Parser(archivo_excel)

    if vba.detect_vba_macros():
        print(f"🔍 Se detectaron macros en el archivo.\n")
        
        # Extraer los módulos VBA
        for (filename, stream_path, vba_filename, vba_code) in vba.extract_macros():
            if vba_code.strip(): # Si el código no está vacío
                nombre_archivo = os.path.join(carpeta_salida, vba_filename + ".bas")
                
                # 'encoding="utf-8"' aquí ya lo tenías, ¡y es correcto!
                with open(nombre_archivo, "w", encoding="utf-8") as f:
                    f.write(vba_code)
                print(f"✅ Módulo extraído: {vba_filename}.bas")
    else:
        print("⚠ No se encontraron macros en el archivo.")

    # Cerrar el parser
    vba.close()

except FileNotFoundError:
    print(f"❌ ERROR: El archivo no fue encontrado en la ruta: {archivo_excel}")
except Exception as e:
    print(f"❌ Ocurrió un error inesperado durante el análisis: {e}")


print("\n🎉 Proceso completado. Archivos guardados en la carpeta:", carpeta_salida)