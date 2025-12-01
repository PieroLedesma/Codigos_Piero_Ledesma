from typing import Any, List, Dict
from .data_reader import _read_equipment_all_mos
from datetime import datetime

def generate_tilt_mos(nemonico: str, rnd_file_xlsx: Any) -> str:
    """
    Genera el script de TILT (RetSubUnit) basándose en la hoja Equipment-Configuration.
    Busca MOs 'RetSubUnit' y atributos de jerarquía AntennaUnitGroup/AntennaNearUnit.
    """

    # 💡 CORRECCIÓN: Inicialización de 'lines'
    lines: List[str] = []

    # Encabezado
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append("// ====================================================================")
    lines.append("//  ARCHIVO PARA CONFIGURACIÓN DE TILT")
    lines.append("// ====================================================================")
    lines.append("// AUTOR: PIERO LEDESMA")
    lines.append(f"// FECHA: {now}")
    lines.append("// ====================================================================")
    lines.append("")
    lines.append("confb+")
    lines.append("gs+")
    lines.append("")
    lines.append("lt all")
    lines.append("")

    # Leer todos los MOs de Equipment
    all_mos = _read_equipment_all_mos(rnd_file_xlsx)
    
    # Buscamos instancias de 'RetSubUnit'
    candidates = []
    if 'RetSubUnit' in all_mos:
        candidates.extend(all_mos['RetSubUnit'])
        
    parsed_items = []
    
    for inst in candidates:
        # Verificar si tiene el atributo de tilt
        if 'electricalAntennaTilt' in inst:
            tilt = inst['electricalAntennaTilt']
            
            # Buscar los IDs en las llaves del diccionario
            # Las llaves suelen ser el nombre del atributo en el Excel, ej: "Equipment=1,AntennaUnitGroup="
            aug = None
            anu = None
            rsu = None
            
            for k, v in inst.items():
                k_lower = k.lower()
                val_str = str(v).strip()
                
                # Identificar AntennaUnitGroup
                if 'antennaunitgroup' in k_lower and '=' in k_lower:
                    aug = val_str
                
                # Identificar AntennaNearUnit
                elif 'antennanearunit' in k_lower and '=' in k_lower:
                    anu = val_str
                    
                # Identificar RetSubUnit (el ID propio)
                elif 'retsubunit' in k_lower and '=' in k_lower:
                    rsu = val_str
            
            # Si encontramos todos los componentes del ID
            if aug and anu and rsu:
                # Convertir a int para ordenar correctamente
                try:
                    aug_int = int(float(aug))
                except:
                    aug_int = 999
                
                try:
                    anu_int = int(float(anu))
                except:
                    anu_int = 999
                    
                try:
                    rsu_int = int(float(rsu))
                except:
                    rsu_int = 999
                    
                parsed_items.append({
                    'aug_str': aug,
                    'anu_str': anu,
                    'rsu_str': rsu,
                    'aug_int': aug_int,
                    'anu_int': anu_int,
                    'rsu_int': rsu_int,
                    'tilt': tilt
                })

    # Ordenar por Group -> NearUnit -> SubUnit
    parsed_items.sort(key=lambda x: (x['aug_int'], x['anu_int'], x['rsu_int']))

    # Generar lineas
    for item in parsed_items:
        # Formato: set AntennaUnitGroup=1,AntennaNearUnit=1,RetSubUnit=1 electricalAntennaTilt  100
        line = f"set AntennaUnitGroup={item['aug_str']},AntennaNearUnit={item['anu_str']},RetSubUnit={item['rsu_str']} electricalAntennaTilt  {item['tilt']}"
        lines.append(line)

    lines.append("")
    lines.append("")
    lines.    append("confb-")
    lines.append("gs-")
    lines.append("")
    
    return "\n".join(lines)