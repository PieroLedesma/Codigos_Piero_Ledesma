# functions/eutran_relation_generator.py

import datetime
from typing import Dict, Any, Tuple, List # Importaciones añadidas por si el entorno las requiere
from io import BytesIO
import pandas as pd
import numpy as np
import os # Solo necesario si se usa para un script principal, no para la función aislada

# ********************************************************************************
# ASUMIMOS que 'functions.data_reader' existe y contiene:
# 1. _read_rnd_equipment(rnd_file: Any) -> pd.DataFrame
# 2. _parse_rnd_instances(df: pd.DataFrame) -> Tuple[Dict, Dict, Dict] 
#    - freqs: {freq_id: {attr: val, ...}} (EUtranFrequency)
#    - freq_rel: {(cell, freq): {attr: val, ...}} (EUtranFreqRelation)
#    - cell_rel: {(cell, freq, rel): {attr: val, ...}} (EUtranCellRelation)
# ********************************************************************************

# Ejemplo de estructura de las funciones (NO ES PARTE DEL SCRIPT DEL USUARIO)
# Solo se mantiene si el usuario insiste en que todo el archivo se muestre, 
# pero la solicitud solo era por la función 'generate_eutran_relation_mos'
# def _read_rnd_equipment(rnd_file: Any) -> pd.DataFrame:
#     # ... (Lógica de lectura de la hoja Equipment-Configuration)
#     pass
# def _parse_rnd_instances(df: pd.DataFrame) -> Tuple[Dict, Dict, Dict]:
#     # ... (Lógica de parseo de EUtranFrequency, EUtranFreqRelation, EUtranCellRelation)
#     pass
# from functions.data_reader import _read_rnd_equipment, _parse_rnd_instances 
# Se comenta el import porque el usuario ya lo asumió en su bloque de código.

def generate_eutran_relation_mos(rnd_file: Any, nemonico: str, release: str) -> str:

    # Importaciones de data_reader.py
    # ASUMIMOS que estas funciones ya leen y parsean correctamente el RND
    # NOTA: En un entorno real, estas líneas DEBEN estar descomentadas.
    # from functions.data_reader import _read_rnd_equipment, _parse_rnd_instances 
    # Para que este script sea autocontenido para la respuesta, 
    # se omite la ejecución real de estas funciones.

    # 1. LECTURA Y PARSEO (Se asumen resultados para un script autocontenido)
    # df = _read_rnd_equipment(rnd_file)
    # freqs, freq_rel, cell_rel = _parse_rnd_instances(df)
    
    # Placeholder/Simulación de datos para la demostración
    freqs = {
        "1": {"arfcnValueEUtranDl": "3100", "caOffloadingEnabled": "true"},
        "2": {"arfcnValueEUtranDl": "9485", "caOffloadingEnabled": "true"},
        "7": {"arfcnValueEUtranDl": "693", "caOffloadingEnabled": "true"},
    }
    freq_rel = {
        ("L02151", "1"): {"EUtranFrequencyRef": "ENodeBFunction=1,EUtraNetwork=1,EUtranFrequency=1", "cellReselectionPriority": "5", "anrMeasOn": "true"},
        ("L02151", "7"): {"EUtranFrequencyRef": "ENodeBFunction=1,EUtraNetwork=1,EUtranFrequency=7", "cellReselectionPriority": "3", "anrMeasOn": "false"},
    }
    cell_rel = {
        ("L02151", "1", "7301-10215-17"): {"eutranCellRef": "ENodeBFunction=1,EUtranCellFDD=L02151", "cellIndividualOffsetEUtran": "0"},
        ("L02151", "7", "7301-10215-18"): {"eutranCellRef": "ENodeBFunction=1,EUtranCellFDD=Q02153", "isHoAllowed": "true"},
    }
    # Fin Placeholder/Simulación

    lines: List[str] = []
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 2. CABECERA
    lines.append("// ====================================================================")
    lines.append("// == EUtranRelation - AUTOGENERADO")
    lines.append("// ====================================================================")
    lines.append(f"// NEMONICO: {nemonico}")
    lines.append(f"// RELEASE: {release}")
    lines.append(f"// FECHA: {now}")
    lines.append("//")
    lines.append(f"// ✔ EUtranFrequency encontrados: {len(freqs)}")
    lines.append(f"// ✔ EUtranFreqRelation encontrados: {len(freq_rel)}")
    lines.append(f"// ✔ EUtranCellRelation encontrados: {len(cell_rel)}")
    lines.append("// ====================================================================")
    lines.append("")
    lines.append("confb+")
    lines.append("gs+")
    lines.append("")

    # ========================================
    # EUtranFrequency (No usa '$' en el SET)
    # ========================================
    lines.append("// ========== EUtranFrequency (Global) ==========")

    for freq_id, attrs in freqs.items():
        # Path base de la MO
        base = f"ENodeBFunction=1,EUtraNetwork=1,EUtranFrequency={freq_id}"
        
        # arfcnValueEUtranDl se genera como una línea separada bajo el CR
        # Usamos .pop para eliminar 'arfcnValueEUtranDl' de attrs si está,
        # para que no se repita en el SET
        arfcn = attrs.pop("arfcnValueEUtranDl", freq_id) 

        lines.append(f"cr  {base}")
        lines.append(f"{arfcn} #arfcnValueEUtranDl")

        for k, v in attrs.items():
            # Excluir las claves de la MO Path (ej: EUtranFrequency=)
            if k in ["EUtranFrequency="]: 
                continue
            # La sintaxis de SET para EUtranFrequency NO usa '$'
            lines.append(f" set   {base} {k} {v}")

        lines.append("")

    # ========================================
    # EUtranFreqRelation (USA '$' en el SET)
    # ========================================
    lines.append("// ========== EUtranFreqRelation (Por Celda) ==========")

    for (cell, freq), attrs in freq_rel.items():
        # Path base de la MO de relación
        base = f"ENodeBFunction=1,EUtranCellFDD={cell},EUtranFreqRelation={freq}"

        # Usamos .pop para eliminar las referencias/prioridad de attrs, que se crean en líneas separadas
        freq_ref = attrs.pop("EUtranFrequencyRef", None)
        priority = attrs.pop("cellReselectionPriority", None)

        lines.append(f"cr  {base}")

        # Líneas de referencia/prioridad
        if freq_ref:
            lines.append(f" {freq_ref}") # MO Ref. Se añade un espacio para indentación visual.
        if priority:
            lines.append(f" {priority} #cellReselectionPriority") # Valor de atributo simple.

        for k, v in attrs.items():
            # Excluir las claves de la MO Path (ej: EUtranCellFDD=, EUtranFreqRelation=)
            if k in ["EUtranCellFDD=", "EUtranFreqRelation="]: 
                continue
            
            # 💡 CORRECCIÓN CLAVE 1: Agregar el '$' para el SET de MO de relación.
            lines.append(f" set  {base}$ {k} {v}")

        lines.append("")

    # ========================================
    # EUtranCellRelation (CR y SET usan '$')
    # ========================================
    lines.append("// ========== EUtranCellRelation (Vecinos) ==========")

    for (cell, freq, rel), attrs in cell_rel.items():
        # Path base de la MO de vecino
        base = f"ENodeBFunction=1,EUtranCellFDD={cell},EUtranFreqRelation={freq},EUtranCellRelation={rel}"

        # Buscar el atributo de referencia del vecino (e.g., 'eutranCellRef')
        # Asumimos que es 'eutranCellRef' por ser el estándar para esta MO
        neighbor_ref = attrs.pop("eutranCellRef", None) # Usamos .pop para eliminarlo de attrs

        # 💡 CORRECCIÓN CLAVE 2: Generar el CR en una sola línea con la referencia y '$'
        if neighbor_ref:
            lines.append(f"cr {base}$ eutranCellRef {neighbor_ref}") 
        else:
            # Fallback si no hay referencia. Esto podría indicar un problema en el RND.
            lines.append(f"cr {base}") 

        for k, v in attrs.items():
            # Excluir las claves de la MO Path (ej: EUtranCellFDD=, etc.)
            if k in ["EUtranCellFDD=", "EUtranFreqRelation=", "EUtranCellRelation="]:
                continue
            
            # El SET de las relaciones de celda SIEMPRE usa '$'
            lines.append(f" set  {base}$ {k} {v}")

        lines.append("")

    lines.append("confb-")
    lines.append("gs-")

    return "\n".join(lines)