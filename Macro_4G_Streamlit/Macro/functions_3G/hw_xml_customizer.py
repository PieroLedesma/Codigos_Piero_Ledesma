"""
Generador de XML de configuración HW personalizado para 3G-DUW
Lee el XML template y reemplaza valores con datos del RND
"""

import re
from typing import Dict, Any, Tuple


def customize_hw_xml(
    xml_content: str,
    nemonico: str,
    rnd_data: Dict[str, Any]
) -> Tuple[bool, str, str]:
    """
    Personaliza un archivo XML de configuración HW con datos del RND.
    
    Args:
        xml_content: Contenido del XML template
        nemonico: Némónico del sitio
        rnd_data: Diccionario con datos del RND (hojas como 'Sector', 'AntennaBranch', etc.)
    
    Returns:
        Tuple (success, customized_xml, error_message)
    """
    try:
        # Verificar que tengamos la hoja Sector en rnd_data
        if 'Sector' not in rnd_data or rnd_data['Sector'] is None:
            return False, xml_content, "Hoja 'Sector' no encontrada en RND"
        
        sector_df = rnd_data['Sector']
        
        if sector_df.empty:
            return False, xml_content, "Hoja 'Sector' está vacía"
        
        # 1. Reemplazar logicalName con el némónico
        xml_content = re.sub(
            r'logicalName="[^"]*"',
            f'logicalName="{nemonico}"',
            xml_content,
            count=1
        )
        
        # 2. Reemplazar siteName con nombre personalizado
        site_name = f"{nemonico}_3G_DUW"
        xml_content = re.sub(
            r'siteName="[^"]*"',
            f'siteName="{site_name}"',
            xml_content,
            count=1
        )
        
        # 3. Preparar diccionario con datos por sector
        sector_data_map = {}
        for idx, row in sector_df.iterrows():
            sector_num = int(row.get('Sector', idx + 1))
            if sector_num <= 3:  # Solo primeros 3 sectores
                sector_data_map[sector_num] = {
                    'latitude': int(row.get('latitude', 0)),
                    'longitude': int(row.get('longitude', 0)),
                    'beamDirection': int(row.get('beamDirection', 0)),
                    'height': int(row.get('height', 0)),
                    'latHemisphere': "SOUTH" if row.get('latHemisphere', 1) == 1 else "NORTH"
                }
        
        # 4. Reemplazar datos sector por sector usando un patrón más robusto
        for sector_num in sorted(sector_data_map.keys()):
            data = sector_data_map[sector_num]
            
            # Patrón para encontrar bloque completo de SectorData para este número
            # Buscamos desde <SectorData sectorNumber="X" hasta </SectorData>
            pattern = rf'(<SectorData\s+sectorNumber="{sector_num}"[^>]*>)(.*?)(</SectorData>)'
            
            def replace_sector_block(match):
                opening_tag = match.group(1)
                content = match.group(2)
                closing_tag = match.group(3)
                
                # Reemplazar cada atributo dentro del contenido
                content = re.sub(r'latitude="[^"]*"', f'latitude="{data["latitude"]}"', content)
                content = re.sub(r'latHemisphere="[^"]*"', f'latHemisphere="{data["latHemisphere"]}"', content)
                content = re.sub(r'longitude="[^"]*"', f'longitude="{data["longitude"]}"', content)
                content = re.sub(r'beamDirection="[^"]*"', f'beamDirection="{data["beamDirection"]}"', content)
                content = re.sub(r'height="[^"]*"', f'height="{data["height"]}"', content)
                
                return opening_tag + content + closing_tag
            
            xml_content = re.sub(pattern, replace_sector_block, xml_content, flags=re.DOTALL)
        
        return True, xml_content, ""
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"ERROR in customize_hw_xml: {error_detail}")
        return False, xml_content, f"Error personalizando XML: {str(e)}"
