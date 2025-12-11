# ===========================================================================
# functions_Relation/relation_generator.py (SECCIÓN EutranCellRelation implementada)
# ===========================================================================

from typing import Dict, Any
from datetime import datetime
import pandas as pd
import numpy as np

def bool_to_mml(value):
    """Convierte valores booleanos (True/False o 1/0) a formato MML (1/0)."""
    if pd.isna(value):
        return None 
    
    value_str = str(value).upper().strip()

    if value_str in ['TRUE', '1', 'T']:
        return '1'
    elif value_str in ['FALSE', '0', 'F']:
        return '0'
    # Retorna el valor como string si es numérico
    try:
        return str(int(value))
    except ValueError:
        return str(value)


def generate_relation_script(nemonico: str, all_data: Dict[str, pd.DataFrame]) -> str:
    """
    Genera el script MML para la creación de Relaciones LTE->3G.
    """
    
    if "error" in all_data:
        return f"# ERROR AL LEER DATOS: {all_data['error']}"

    mml_output = []
    fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener RNC para el Amos
    rnc_value = "RNC_DESCONOCIDO" 
    for df in all_data.values():
        if 'RNC' in df.columns:
            rnc_value = df['RNC'].dropna().iloc[0] if not df['RNC'].dropna().empty else rnc_value
            break

    # 4. AÑADIR LA FIRMA (HEADER)
    mml_output.append("#############################################################")
    mml_output.append("#                                                           ")
    mml_output.append("#     ARCHIVO PARA CREACION DE RELACIONES LTE-> 3G EN RNC     ")
    mml_output.append(f"#     GENERADO POR : Piero Ledesma                          ")
    mml_output.append(f"#     FECHA: {fecha_hoy:<40}") 
    mml_output.append(f"#     NEMONICO: {nemonico:<40}") 
    mml_output.append("#                                                           ")
    mml_output.append("#############################################################")
    mml_output.append("")
    mml_output.append(f"amos {rnc_value}") 
    mml_output.append("lt all")
    mml_output.append("confb+")
    mml_output.append("gs+")
    mml_output.append("") 

    # ===========================================================================
    # === 5. SECCIÓN UtranCell (MML) ===
    # ===========================================================================
    if 'UtranCell' in all_data:
        utran_df = all_data['UtranCell']
        mml_output.append("####################################################")
        mml_output.append("#     UtranCell                                    #")
        mml_output.append("####################################################")
        for _, row in utran_df.iterrows():
            try:
                utrancell_name = str(row['Utrancell']).strip()
                if not utrancell_name: continue
                
                lte_meas_val = bool_to_mml(row.get('lteMeasEnabled'))
                if lte_meas_val in ['0', '1']:
                    mml_output.append(f"set UtranCell={utrancell_name} lteMeasEnabled {lte_meas_val}")
                
                ps_ho_val = bool_to_mml(row.get('psHoToLteEnabled'))
                if ps_ho_val in ['0', '1']:
                    mml_output.append(f"set UtranCell={utrancell_name} psHoToLteEnabled {ps_ho_val}")

            except KeyError as e:
                mml_output.append(f"# ERROR: Columna faltante en la hoja UtranCell: {e}")
        mml_output.append("") 
    
    # ===========================================================================
    # === 6. SECCIÓN EutranFreqRelation (MML) ===
    # ===========================================================================
    if 'EutranFreqRelation' in all_data:
        freq_rel_df = all_data['EutranFreqRelation']
        set_params = [
            'cellReselectionPriority', 'qRxLevMin', 'threshHigh', 'threshlow', 
            'redirectionOrder', 'thresh2dRwr', 'coSitedCellAvailable'
        ]
        
        mml_output.append("#############################################################")
        mml_output.append("#     EutranFreqRelation                                    #")
        mml_output.append("#############################################################")
        
        for _, row in freq_rel_df.iterrows():
            try:
                utrancell_name = str(row['UtranCell']).strip()
                # Asegura que la columna de frecuencia exista, si no, usa el alias
                eutran_freq = str(row.get('eutranFrequency', row.get('EutranFreqRelation', ''))).strip()
                
                if not utrancell_name or not eutran_freq: continue
                
                # Comando CR (Creation)
                mml_output.append(f"cr UtranCell={utrancell_name},EutranFreqRelation={eutran_freq}")
                mml_output.append(f"EutraNetwork=1,EutranFrequency={eutran_freq}")
                
                # Comandos SET
                for param in set_params:
                    value = row.get(param)
                    if param == 'coSitedCellAvailable':
                        mml_value = bool_to_mml(value)
                    else:
                        mml_value = str(value).strip() if pd.notna(value) else None
                        
                    if mml_value is not None:
                        mml_output.append(f"set UtranCell={utrancell_name},EutranFreqRelation={eutran_freq} {param} {mml_value}")
                
                mml_output.append("") 
            except KeyError as e:
                mml_output.append(f"# ERROR: Columna faltante en la hoja EutranFreqRelation: {e}")
        mml_output.append("")
    
    # ===========================================================================
    # === 7. SECCIÓN ExternalEutranCell (MML) ===
    # ===========================================================================
    if 'ExternalEutranCell' in all_data:
        external_df = all_data['ExternalEutranCell']
        cr_body_params = ['eNodeBId', 'cellId', 'tac']
        
        mml_output.append("#############################################################")
        mml_output.append("#     ExternalEutranCell                                    #")
        mml_output.append("#############################################################")
        
        for _, row in external_df.iterrows():
            try:
                eutran_freq = str(row['EutranFrequency']).strip()
                external_cell_id = str(row['ExternalEutranCellId']).strip()
                
                if not eutran_freq or not external_cell_id: continue
                
                # Comando CR (Creation) MoId
                mml_output.append(f"cr EutraNetwork=1,EutranFrequency={eutran_freq},ExternalEutranCell={external_cell_id}")
                
                # Parámetros en el cuerpo del CR (Líneas 2, 3, 4)
                for param in cr_body_params:
                    value = row.get(param)
                    # Intentar convertir a entero/string (necesario para el formato de MML con salto de línea)
                    mml_value = str(int(value)) if pd.notna(value) and str(value).strip().isdigit() else str(value).strip() if pd.notna(value) else None
                    
                    if mml_value is not None:
                        mml_output.append(mml_value)
                
                # Comando SET (physicalCellIdentity)
                pci_value = row.get('physicalCellIdentity')
                pci_mml_value = str(int(pci_value)) if pd.notna(pci_value) and str(pci_value).strip().isdigit() else None
                
                if pci_mml_value is not None:
                    mml_output.append(f"set EutraNetwork=1,EutranFrequency={eutran_freq},ExternalEutranCell={external_cell_id} physicalCellIdentity {pci_mml_value}")
                
                mml_output.append("") # Separador
                
            except KeyError as e:
                mml_output.append(f"# ERROR: Columna faltante en la hoja ExternalEutranCell: {e}")
            except ValueError as e:
                 mml_output.append(f"# ERROR: Valor inválido (no numérico) en columna de ExternalEutranCell: {e}")

        mml_output.append("") 


    # ===========================================================================
    # === 8. GENERACIÓN DE COMANDOS MML: SECCIÓN EutranCellRelation (NUEVA) ===
    # ===========================================================================
    
    if 'EutranCellRelation' in all_data:
        cell_rel_df = all_data['EutranCellRelation']
        
        mml_output.append("#############################################################")
        mml_output.append("#     EutranCellRelation                                    #")
        mml_output.append("#############################################################")
        
        # Las columnas necesarias son: UtranCell, EutranFreqRelation, EutranCellRelation, externalEutranCellRef
        
        for _, row in cell_rel_df.iterrows():
            try:
                utrancell_name = str(row['UtranCell']).strip()
                eutran_freq = str(row['EutranFreqRelation']).strip()
                eutran_cell_rel_id = str(row['EutranCellRelation']).strip()
                # La columna 'externalEutranCellRef' contiene toda la MoId de destino (EutraNetwork=1,...)
                external_ref = str(row['externalEutranCellRef']).strip()
                
                if not utrancell_name or not eutran_freq or not eutran_cell_rel_id or not external_ref: 
                    mml_output.append(f"# ADVERTENCIA: Fila saltada por datos faltantes: UtranCell={utrancell_name}, Freq={eutran_freq}, CellRel={eutran_cell_rel_id}")
                    continue
                
                # Comando CR (Creation) MoId
                # cr RncFunction=1,UtranCell=U35971,EutranFreqRelation=LTE3100,EutranCellRelation=L24664
                cr_mo_id = (
                    f"cr RncFunction=1,UtranCell={utrancell_name},"
                    f"EutranFreqRelation={eutran_freq},"
                    f"EutranCellRelation={eutran_cell_rel_id}"
                )
                mml_output.append(cr_mo_id)
                
                # Segunda línea del CR (Referencia al ExternalEutranCell)
                # EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L24664
                mml_output.append(external_ref)
                
                mml_output.append("") # Separador
                
            except KeyError as e:
                mml_output.append(f"# ERROR: Columna faltante en la hoja EutranCellRelation: {e}")
        
        mml_output.append("") # Separador final
    else:
        mml_output.append("# ADVERTENCIA: La hoja 'EutranCellRelation' no se encontró en el archivo.")
        mml_output.append("") 


    # 9. Finalización MML
    mml_output.append("confb-")
    mml_output.append("gs-")
    
    return "\n".join(mml_output)

# ===========================================================================