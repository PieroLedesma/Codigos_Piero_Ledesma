import pandas as pd
from datetime import datetime

def generate_utranrelation_mos(rnd_data, rnc_value, nemonico):
    """
    Genera el archivo 03_{RNC}_{Nemonico}_PL_Create_Relations.mos
    basado en la hoja UtranRelation del RND.
    """
    mml_output = []
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%d-%m-%Y")

    # Header
    mml_output.append("////////////////////////////////////////////////////////////")
    mml_output.append("//")
    mml_output.append("// SCRIPT     : CREATE_Relations")
    mml_output.append(f"// NEMONICO   : {rnc_value}")
    mml_output.append(f"// NEMONICO   : {nemonico}")
    mml_output.append(f"// HORA       : {current_time}")
    mml_output.append(f"// FECHA      : {current_date}")
    mml_output.append("//")
    mml_output.append("////////////////////////////////////////////////////////////")
    mml_output.append("")
    mml_output.append("confb+")
    mml_output.append("gs+")
    mml_output.append("lt all")
    mml_output.append("")

    # 1. Sección UtranRelation
    mml_output.append("#############################################################")
    mml_output.append(f"### UtranRelation {rnc_value}")
    mml_output.append("#############################################################")
    mml_output.append("")

    df_rel = None
    if rnd_data:
        for key in rnd_data.keys():
            if key.lower() == 'utranrelation':
                df_rel = rnd_data[key]
                break
    
    if df_rel is not None and not df_rel.empty:
        for index, row in df_rel.iterrows():
            # Helper para obtener valor de columna
            def get_val(col_name):
                for col in df_rel.columns:
                    if col_name.lower() == col.strip().lower():
                        val = str(row[col]).strip()
                        if val and val.lower() != 'nan':
                            return val
                return ""

            cell = get_val('CELL')
            relation = get_val('Relation')
            cell_r = get_val('CELL_R')
            
            if cell and relation and cell_r:
                # CR Command
                mml_output.append(f"cr RncFunction=1,UtranCell={cell},UtranRelation={relation}")
                mml_output.append(f"UtranCell={cell_r} #UtranCell")
                mml_output.append("0  #mobilityRelationType")
                
                # SET Commands
                # qOffset1sn
                q1 = get_val('qOffset1sn')
                if q1:
                    mml_output.append(f"set RncFunction=1,UtranCell={cell},UtranRelation={relation} qOffset1sn {q1}")
                
                # qOffset2sn
                q2 = get_val('qOffset2sn')
                if q2:
                    mml_output.append(f"set RncFunction=1,UtranCell={cell},UtranRelation={relation} qOffset2sn {q2}")
                
                # selectionPriority
                prio = get_val('selectionPriority')
                if prio:
                    mml_output.append(f"set RncFunction=1,UtranCell={cell},UtranRelation={relation} selectionPriority {prio}")
                
                mml_output.append("")
    else:
        mml_output.append("// ERROR: No se encontraron datos en la hoja UtranRelation")

    # 2. Sección EutranFreqRelation PMER01
    mml_output.append("#############################################################")
    mml_output.append(f"### EutranFreqRelation {rnc_value}")
    mml_output.append("#############################################################")
    mml_output.append("")

    df_eutran = None
    if rnd_data:
        for key in rnd_data.keys():
            if key.lower() == 'eutranfreqrelation':
                df_eutran = rnd_data[key]
                break
    
    if df_eutran is not None and not df_eutran.empty:
        for index, row in df_eutran.iterrows():
            # Helper para obtener valor de columna
            def get_eutran_val(col_name):
                for col in df_eutran.columns:
                    if col_name.lower() == col.strip().lower():
                        val = str(row[col]).strip()
                        if val and val.lower() != 'nan':
                            return val
                return ""

            utran_cell = get_eutran_val('Utrancell')
            eutran_freq = get_eutran_val('eutranFrequency')
            
            if utran_cell and eutran_freq:
                # CR Command
                # cr RncFunction=1,UtranCell=U37811,EutranFreqRelation=LTE3100
                mml_output.append(f"cr RncFunction=1,UtranCell={utran_cell},EutranFreqRelation={eutran_freq}")
                # EutraNetwork=1,EutranFrequency=LTE3100 #eutranFrequencyRef
                mml_output.append(f"EutraNetwork=1,EutranFrequency={eutran_freq} #eutranFrequencyRef")
                
                # Atributos
                attrs = [
                    'qRxLevMin', 'cellReselectionPriority', 'threshHigh',
                    'threshlow', 'redirectionOrder', 'eutranFrequency',
                    'thresh2dRwr', 'coSitedCellAvailable'
                ]
                
                for attr in attrs:
                    val = get_eutran_val(attr)
                    if val:
                        mml_output.append(f"set RncFunction=1,UtranCell={utran_cell},EutranFreqRelation={eutran_freq} {attr} {val}")
                
                mml_output.append("")
    else:
        mml_output.append("// ERROR: No se encontraron datos en la hoja EutranFreqRelation")

    # 3. Sección ExternalEutranCell PMER01
    mml_output.append("#############################################################")
    mml_output.append(f"### ExternalEutranCell {rnc_value}")
    mml_output.append("#############################################################")
    mml_output.append("")

    df_ext_eutran = None
    if rnd_data:
        for key in rnd_data.keys():
            if key.lower() == 'externaleutrancell':
                df_ext_eutran = rnd_data[key]
                break
    
    if df_ext_eutran is not None and not df_ext_eutran.empty:
        for index, row in df_ext_eutran.iterrows():
            # Helper para obtener valor de columna
            def get_ext_val(col_name):
                for col in df_ext_eutran.columns:
                    if col_name.lower() == col.strip().lower():
                        val = str(row[col]).strip()
                        if val and val.lower() != 'nan':
                            return val
                return ""

            eutran_freq = get_ext_val('EutranFrequency')
            ext_cell_id = get_ext_val('ExternalEutranCellId')
            enodeb_id = get_ext_val('eNodeBId')
            cell_id = get_ext_val('cellId')
            tac = get_ext_val('tac')
            pci = get_ext_val('physicalCellIdentity')
            
            if eutran_freq and ext_cell_id and enodeb_id and cell_id and tac:
                # CR Command
                # cr RncFunction=1,EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L37811
                mml_output.append(f"cr RncFunction=1,EutraNetwork=1,EutranFrequency={eutran_freq},ExternalEutranCell={ext_cell_id}")
                mml_output.append(f"{enodeb_id} #eNodeBId")
                mml_output.append(f"{cell_id} #cellId")
                mml_output.append(f"{tac} #tac")
                
                # SET physicalCellIdentity
                if pci:
                    mml_output.append(f"set RncFunction=1,EutraNetwork=1,EutranFrequency={eutran_freq},ExternalEutranCell={ext_cell_id} physicalCellIdentity {pci}")
                
                mml_output.append("")
    else:
        mml_output.append("// ERROR: No se encontraron datos en la hoja ExternalEutranCell")

    # 4. Sección EutranCellRelation PMER01
    mml_output.append("#############################################################")
    mml_output.append(f"### EutranCellRelation {rnc_value}")
    mml_output.append("#############################################################")
    mml_output.append("")

    df_cell_rel = None
    if rnd_data:
        for key in rnd_data.keys():
            if key.lower() == 'eutrancellrelation':
                df_cell_rel = rnd_data[key]
                break
    
    if df_cell_rel is not None and not df_cell_rel.empty:
        for index, row in df_cell_rel.iterrows():
            # Helper para obtener valor de columna
            def get_cell_rel_val(col_name):
                for col in df_cell_rel.columns:
                    if col_name.lower() == col.strip().lower():
                        val = str(row[col]).strip()
                        if val and val.lower() != 'nan':
                            return val
                return ""

            utran_cell = get_cell_rel_val('Utrancell')
            eutran_freq_rel = get_cell_rel_val('EutranFreqRelation')
            eutran_cell_rel = get_cell_rel_val('EutranCellRelation')
            ext_cell_ref = get_cell_rel_val('externalEutranCellRef')
            co_sited = get_cell_rel_val('coSited')
            
            if utran_cell and eutran_freq_rel and eutran_cell_rel and ext_cell_ref:
                # CR Command
                # cr RncFunction=1,UtranCell=U37811,EutranFreqRelation=LTE3100,EutranCellRelation=L37811
                mml_output.append(f"cr RncFunction=1,UtranCell={utran_cell},EutranFreqRelation={eutran_freq_rel},EutranCellRelation={eutran_cell_rel}")
                # EutraNetwork=1,EutranFrequency=LTE3100,ExternalEutranCell=L37811 #externalEutranCellRef
                mml_output.append(f"{ext_cell_ref} #externalEutranCellRef")
                
                # SET coSited
                if co_sited:
                    mml_output.append(f"set RncFunction=1,UtranCell={utran_cell},EutranFreqRelation={eutran_freq_rel},EutranCellRelation={eutran_cell_rel} coSited {co_sited}")
                
                # SET userLabel (empty in the example)
                mml_output.append(f"set RncFunction=1,UtranCell={utran_cell},EutranFreqRelation={eutran_freq_rel},EutranCellRelation={eutran_cell_rel} userLabel ")
                
                mml_output.append("")
    else:
        mml_output.append("// ERROR: No se encontraron datos en la hoja EutranCellRelation")

    # Cierre del script
    mml_output.append("#############################################################")
    mml_output.append(f"############# FIN de SCRIPT EN {rnc_value} #######################")
    mml_output.append("#############################################################")

    content = "\n".join(mml_output)
    filename = f"03_{rnc_value}_{nemonico}_PL_Create_Relations.mos"
    
    return True, content, filename
