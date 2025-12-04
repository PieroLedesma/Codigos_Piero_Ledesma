"""
Ejemplo de extracción de datos de RND 3G WCDMA para uso en generator_logic_3G.py

Este script muestra cómo leer y procesar el archivo RND Excel para extraer
información clave de celdas 3G, relaciones, y configuraciones HSPA.
"""

import pandas as pd
from typing import Dict, List


class RND3GReader:
    """Lector de archivos RND 3G WCDMA"""
    
    def __init__(self, rnd_file_path: str):
        """
        Inicializa el lector con la ruta del archivo RND
        
        Args:
            rnd_file_path: Ruta completa al archivo Excel RND
        """
        self.rnd_file = rnd_file_path
        self.excel_file = pd.ExcelFile(rnd_file_path)
        
    def get_site_info(self) -> Dict:
        """Extrae información general del sitio"""
        df_utran = pd.read_excel(self.excel_file, sheet_name='UtranCell')
        
        if len(df_utran) == 0:
            return {}
            
        return {
            'site': df_utran['Site'].iloc[0],
            'rnc': df_utran['RNC'].iloc[0],
            'num_celdas': len(df_utran),
            'celdas_ids': df_utran['Utrancell'].tolist()
        }
    
    def get_celdas_3g(self) -> List[Dict]:
        """
        Extrae información de todas las celdas 3G
        
        Returns:
            Lista de diccionarios con datos de cada celda
        """
        df = pd.read_excel(self.excel_file, sheet_name='UtranCell')
        
        # Columnas clave para celdas 3G
        columnas_importantes = [
            'RNC', 'Site', 'Utrancell', 'cId', 'lac',
            'primaryScramblingCode', 'uarfcnDl', 'uarfcnUl',
            'maximumTransmissionPower', 'primaryCpichPower',
            'qQualMin', 'qRxLevMin', 'administrativeState'
        ]
        
        # Filtrar solo columnas que existen
        columnas_disponibles = [col for col in columnas_importantes if col in df.columns]
        
        celdas = []
        for idx, row in df.iterrows():
            celda = {col: row[col] for col in columnas_disponibles}
            # Agregar coordenadas si están disponibles
            if 'antennaPosition_latitude' in df.columns:
                celda['latitude'] = row['antennaPosition_latitude']
            if 'antennaPosition_longitude' in df.columns:
                celda['longitude'] = row['antennaPosition_longitude']
            celdas.append(celda)
        
        return celdas
    
    def get_relaciones_3g(self) -> List[Dict]:
        """
        Extrae relaciones 3G->3G (UtranRelation)
        
        Returns:
            Lista de diccionarios con relaciones entre celdas WCDMA
        """
        df = pd.read_excel(self.excel_file, sheet_name='UtranRelation')
        
        relaciones = []
        for idx, row in df.iterrows():
            relacion = {
                'celda_origen': row['CELL'],
                'celda_destino': row['Relation'],
                'rnc_origen': row['RNC'],
                'rnc_destino': row.get('RNC_R', row['RNC']),
                'qOffset1sn': row.get('qOffset1sn', 0),
                'qOffset2sn': row.get('qOffset2sn', 0),
                'priority': row.get('selectionPriority', 1)
            }
            relaciones.append(relacion)
        
        return relaciones
    
    def get_relaciones_lte(self) -> List[Dict]:
        """
        Extrae relaciones 3G->4G LTE
        
        Returns:
            Lista de relaciones hacia celdas LTE
        """
        df = pd.read_excel(self.excel_file, sheet_name='EutranCellRelation')
        
        relaciones_lte = []
        for idx, row in df.iterrows():
            relacion = {
                'celda_3g': row.get('Utrancell', ''),
                'celda_lte': row.get('EutranCellRelation', ''),
                'rnc': row.get('RNC', ''),
                'freq_relation': row.get('EutranFreqRelation', ''),
                'co_sited': row.get('coSited', 0),
                'external_cell_ref': row.get('externalEutranCellRef', '')
            }
            relaciones_lte.append(relacion)
        
        return relaciones_lte
    
    def get_frecuencias_lte(self) -> List[Dict]:
        """
        Extrae configuración de frecuencias LTE
        
        Returns:
            Lista de frecuencias LTE configuradas
        """
        df = pd.read_excel(self.excel_file, sheet_name='EutranFreqRelation')
        
        frecuencias = []
        for idx, row in df.iterrows():
            freq = {
                'celda_3g': row.get('Utrancell', ''),
                'rnc': row.get('RNC', ''),
                'freq_relation': row.get('EutranFreqRelation', ''),
                'earfcn': row.get('earfcnDl', row.get('earfcn', 0)),
                'priority': row.get('cellReselectionPriority', 0),
                'qoffset': row.get('qOffsetFreq', 0),
                'qqualmin': row.get('qQualMin', 0),
                'qrxlevmin': row.get('qRxLevMin', 0)
            }
            frecuencias.append(freq)
        
        return frecuencias
    
    def get_configuracion_hspa(self) -> Dict[str, List[Dict]]:
        """
        Extrae configuración HSPA (HSDPA + HSUPA)
        
        Returns:
            Diccionario con configuraciones EUL y HSDSCH por celda
        """
        # EUL (Enhanced Uplink / HSUPA)
        df_eul = pd.read_excel(self.excel_file, sheet_name='EUL')
        eul_configs = []
        for idx, row in df_eul.iterrows():
            config = {
                'celda': row.get('Utrancell', ''),
                'site': row.get('Site', ''),
                'max_slots': row.get('eulMaxSlotsByUe', 0),
                'max_rate': row.get('maxEulPhysChRate', 0),
                'scheduling_grant': row.get('eulSchedulingGrant', '')
            }
            eul_configs.append(config)
        
        # HSDSCH (High Speed Downlink / HSDPA)
        df_hsdsch = pd.read_excel(self.excel_file, sheet_name='Hsdsch')
        hsdsch_configs = []
        for idx, row in df_hsdsch.iterrows():
            config = {
                'celda': row.get('Utrancell', ''),
                'site': row.get('Site', ''),
                'max_codes': row.get('hsdschMaxCode', 0),
                'max_ue': row.get('hsdschMaxUe', 0),
                'max_retrans': row.get('hsPdschCodeMaxRetrans', 0)
            }
            hsdsch_configs.append(config)
        
        return {
            'eul': eul_configs,
            'hsdsch': hsdsch_configs
        }
    
    def get_carriers(self) -> List[Dict]:
        """
        Extrae información de portadoras (carriers)
        
        Returns:
            Lista de configuraciones de portadoras por sector
        """
        df = pd.read_excel(self.excel_file, sheet_name='NodeBSectorCarrier')
        
        carriers = []
        for idx, row in df.iterrows():
            carrier = {
                'site': row.get('Site', ''),
                'carrier_id': row.get('Carrier', ''),
                'uarfcn_dl': row.get('uarfcnDl', 0),
                'uarfcn_ul': row.get('uarfcnUl', 0),
                'psc': row.get('primaryScramblingCode', 0),
                'max_power': row.get('maximumTransmissionPower', 0),
                'frame_offset': row.get('frameStartOffset', 0)
            }
            carriers.append(carrier)
        
        return carriers
    
    def get_rf_branches(self) -> List[Dict]:
        """
        Extrae configuración de ramas RF (antenas)
        
        Returns:
            Lista de ramas RF configuradas
        """
        df = pd.read_excel(self.excel_file, sheet_name='RfBranch')
        
        branches = []
        for idx, row in df.iterrows():
            branch = {
                'site': row.get('Site', ''),
                'carrier': row.get('Carrier', ''),
                'rf_branch': row.get('RfBranch', ''),
                'dl_attenuation': row.get('dlAttenuation', 0),
                'ul_attenuation': row.get('ulAttenuation', 0),
                'rf_port_ref': row.get('rfPortRef', '')
            }
            branches.append(branch)
        
        return branches
    
    def generar_resumen_completo(self) -> Dict:
        """
        Genera un resumen completo del RND
        
        Returns:
            Diccionario con toda la información del sitio
        """
        return {
            'info_sitio': self.get_site_info(),
            'celdas_3g': self.get_celdas_3g(),
            'relaciones_3g': self.get_relaciones_3g(),
            'relaciones_lte': self.get_relaciones_lte(),
            'frecuencias_lte': self.get_frecuencias_lte(),
            'hspa': self.get_configuracion_hspa(),
            'carriers': self.get_carriers(),
            'rf_branches': self.get_rf_branches()
        }


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Ruta al archivo RND
    RND_FILE = r"LA781 - TEKNICA\LA781 - TEKNICA\RND_ULA781_WCDMA1900_900_20251104-141953.xlsx"
    
    # Crear lector
    reader = RND3GReader(RND_FILE)
    
    # Obtener información del sitio
    print("=" * 80)
    print("INFORMACIÓN DEL SITIO")
    print("=" * 80)
    site_info = reader.get_site_info()
    print(f"Sitio: {site_info.get('site', 'N/A')}")
    print(f"RNC: {site_info.get('rnc', 'N/A')}")
    print(f"Número de celdas: {site_info.get('num_celdas', 0)}")
    print(f"IDs de celdas: {', '.join(site_info.get('celdas_ids', []))}")
    
    # Obtener celdas 3G
    print("\n" + "=" * 80)
    print("CELDAS 3G")
    print("=" * 80)
    celdas = reader.get_celdas_3g()
    for celda in celdas:
        print(f"\nCelda: {celda.get('Utrancell', 'N/A')}")
        print(f"  - Cell ID: {celda.get('cId', 'N/A')}")
        print(f"  - LAC: {celda.get('lac', 'N/A')}")
        print(f"  - PSC: {celda.get('primaryScramblingCode', 'N/A')}")
        print(f"  - Max Power: {celda.get('maximumTransmissionPower', 'N/A')} dBm")
    
    # Obtener relaciones 3G
    print("\n" + "=" * 80)
    print("RELACIONES 3G->3G")
    print("=" * 80)
    relaciones = reader.get_relaciones_3g()
    print(f"Total de relaciones: {len(relaciones)}")
    print("\nPrimeras 5 relaciones:")
    for rel in relaciones[:5]:
        print(f"  {rel['celda_origen']} -> {rel['celda_destino']} "
              f"(Priority: {rel['priority']}, qOffset1: {rel['qOffset1sn']} dB)")
    
    # Obtener relaciones LTE
    print("\n" + "=" * 80)
    print("RELACIONES 3G->4G LTE")
    print("=" * 80)
    relaciones_lte = reader.get_relaciones_lte()
    print(f"Total de relaciones LTE: {len(relaciones_lte)}")
    if relaciones_lte:
        print("\nPrimeras 5 relaciones LTE:")
        for rel in relaciones_lte[:5]:
            print(f"  {rel['celda_3g']} -> {rel['celda_lte']}")
    
    # Obtener configuración HSPA
    print("\n" + "=" * 80)
    print("CONFIGURACIÓN HSPA")
    print("=" * 80)
    hspa = reader.get_configuracion_hspa()
    print(f"Configuraciones HSUPA (EUL): {len(hspa['eul'])}")
    print(f"Configuraciones HSDPA: {len(hspa['hsdsch'])}")
    
    # Obtener carriers
    print("\n" + "=" * 80)
    print("PORTADORAS (CARRIERS)")
    print("=" * 80)
    carriers = reader.get_carriers()
    print(f"Total de carriers: {len(carriers)}")
    for carrier in carriers:
        print(f"\nCarrier: {carrier.get('carrier_id', 'N/A')}")
        print(f"  - UARFCN DL: {carrier.get('uarfcn_dl', 'N/A')}")
        print(f"  - UARFCN UL: {carrier.get('uarfcn_ul', 'N/A')}")
        print(f"  - PSC: {carrier.get('psc', 'N/A')}")
    
    print("\n" + "=" * 80)
    print("ANÁLISIS COMPLETADO")
    print("=" * 80)
