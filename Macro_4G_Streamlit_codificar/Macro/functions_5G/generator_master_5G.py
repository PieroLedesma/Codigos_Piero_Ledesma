from datetime import datetime

def generate_master_script_5g(nemonico: str) -> str:
    """
    Genera el script maestro (00_MASTER_RAN_PL_NR.mo) que ejecuta todos los archivos .mos
    generados por la aplicación 5G en orden secuencial.
    
    Args:
        nemonico: Nemónico del sitio (ej: GLA781)
        
    Returns:
        str: Contenido del archivo .mo maestro para 5G NR
    """
    
    nem = nemonico.upper()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = []
    
    # Encabezado
    lines.append("// ====================================================================")
    lines.append("//  MASTER SCRIPT 5G NR - EJECUCIÓN SECUENCIAL DE SCRIPTS REMOTOS")
    lines.append("// ====================================================================")
    lines.append("// AUTOR: PIERO LEDESMA")
    lines.append(f"// FECHA: {now}")
    lines.append(f"// NEMÓNICO: {nem}")
    lines.append("// ====================================================================")
    lines.append("// Este script ejecuta automáticamente todos los archivos .mos")
    lines.append("// generados para la configuración del nodo 5G NR.")
    lines.append("// ====================================================================")
    lines.append("")
    
    # Ejecución de scripts en orden
    lines.append("// Ejecutar scripts en orden secuencial")
    lines.append(f"run 01_{nem}_NR_Transport_Node.mos")
    lines.append(f"run 02_{nem}_NR_HW_CELL.mos")
    lines.append(f"run 03_{nem}_NR_RELATION_PARAM.mos")
    lines.append(f"run 02_{nem}_NR_HW_CELL.mos")
    lines.append(f"run 03_{nem}_NR_RELATION_PARAM.mos")
    lines.append("")
    
    # Captura de fecha y creación de CV
    lines.append("// Capturar fecha actual")
    lines.append("$date = `date +%y%m%d`")
    lines.append("")
    lines.append("// Crear CV (Configuration Version) con el nombre del nodo")
    lines.append("cvms CV_NR_$nodename_OK")
    lines.append("")
    
    return "\n".join(lines)
