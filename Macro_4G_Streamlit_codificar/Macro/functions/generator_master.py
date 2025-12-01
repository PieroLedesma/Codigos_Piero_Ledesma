from datetime import datetime

def generate_master_script_mo(nemonico: str) -> str:
    """
    Genera el script maestro (00_MASTER_RAN_PL_LTE.mo) que ejecuta todos los archivos .mos
    generados por la aplicación en orden secuencial.
    
    Args:
        nemonico: Nemónico del sitio (ej: MZB884)
        
    Returns:
        str: Contenido del archivo .mo maestro
    """
    
    nem = nemonico.upper()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = []
    
    # Encabezado
    lines.append("// ====================================================================")
    lines.append("//  MASTER SCRIPT - EJECUCIÓN SECUENCIAL DE SCRIPTS REMOTOS")
    lines.append("// ====================================================================")
    lines.append("// AUTOR: PIERO LEDESMA")
    lines.append(f"// FECHA: {now}")
    lines.append(f"// NEMÓNICO: {nem}")
    lines.append("// ====================================================================")
    lines.append("// Este script ejecuta automáticamente todos los archivos .mos")
    lines.append("// generados para la configuración del nodo LTE.")
    lines.append("// ====================================================================")
    lines.append("")
    
    # Ejecución de scripts en orden
    lines.append("// Ejecutar scripts en orden secuencial")
    lines.append(f"run 00_{nem}_Hardware.mos")
    lines.append(f"run 01_{nem}_EUtranCellFDD.mos")
    lines.append(f"run 02_{nem}_UtranRelation.mos")
    lines.append(f"run 03_{nem}_EUtranRelation.mos")
    lines.append(f"run 04_{nem}_GUtranRelation.mos")
    lines.append(f"run 05_{nem}_Parametros.mos")
    lines.append(f"run 06_{nem}_Tilt.mos")
    lines.append("")
    
    # Captura de fecha y creación de CV
    lines.append("// Capturar fecha actual")
    lines.append("$date = `date +%y%m%d`")
    lines.append("")
    lines.append("// Crear CV (Configuration Version) con el nombre del nodo")
    lines.append("cvms CV_$nodename_OK")
    lines.append("")
    
    return "\n".join(lines)
