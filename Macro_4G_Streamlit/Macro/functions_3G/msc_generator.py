import pandas as pd
from datetime import datetime

def generate_msc_mos(rnd_data, rnc_value, nemonico):
    """
    Genera el archivo 04_MSC_{RNC}_{Nemonico}_PL_Delete_Create_Cells.mos
    basado en la hoja MscParameter del RND.
    """
    mml_output = []

    # Header
    mml_output.append("###########################################################")
    mml_output.append("### MscParameter")
    mml_output.append("#############################################################")
    mml_output.append("@COMMENT +---------------------------------------------------------------+ ##")
    mml_output.append(f"@COMMENT |    CREACION DE CELDAS EN MSC CHMBC01         | ##")
    mml_output.append("@COMMENT +---------------------------------------------------------------+ ##")
    mml_output.append("")
    mml_output.append("ssh -l (#USUARIO ENM#) 172.18.250.69")
    mml_output.append("(#PSWD ENM#)")
    mml_output.append("mml")
    mml_output.append("@T 2")
    mml_output.append("")

    # 1. Sección MscParameter
    df_msc = None
    if rnd_data:
        for key in rnd_data.keys():
            if key.lower() == 'mscparameter':
                df_msc = rnd_data[key]
                break
    
    if df_msc is not None and not df_msc.empty:
        for index, row in df_msc.iterrows():
            # Helper para obtener valor de columna
            def get_val(col_name):
                for col in df_msc.columns:
                    if col_name.lower() == col.strip().lower():
                        val = str(row[col]).strip()
                        if val and val.lower() != 'nan':
                            return val
                return ""

            utran_cell = get_val('Utrancell')
            locno = get_val('LOCNO')
            ro = get_val('RO')
            ea = get_val('EA')
            zc = get_val('ZC')
            
            if utran_cell and locno:
                # Comandos básicos
                mml_output.append(f"MGRCE:AREA={utran_cell};")
                mml_output.append(f"MGLCE:AREA={utran_cell};")
                mml_output.append(f"MGLNE:LOCNO={locno};")
                mml_output.append(f"MGAAE:AREA={utran_cell};")
                mml_output.append("")
                
                # MGAAI - SAI (formato: 730-01-10513-37811)
                # Construir SAI desde los datos disponibles
                site = get_val('Site')
                if site:
                    # Extraer últimos dígitos del site para construir SAI
                    sai = f"730-01-10513-{site}"
                    mml_output.append(f"MGAAI:AREA={utran_cell},SAI={sai};")
                
                # MGAAC
                if ro and ea:
                    mml_output.append(f"MGAAC:AREA={utran_cell},RO={ro},EA={ea};")
                
                mml_output.append(f"MGAAP:AREA={utran_cell};")
                mml_output.append(f"MGLNI:LOCNO={locno};")
                mml_output.append(f"MGLCI:LOCNO={locno},AREA={utran_cell};")
                mml_output.append(f"MGLNP:LOCNO={locno};")
                
                # MGZCI
                if zc:
                    mml_output.append(f"MGZCI:ZC={zc},LOCNO={locno};")
                
                mml_output.append(f"MGZCP:LOCNO={locno};")
                mml_output.append(f"MGLCP:AREA={utran_cell};")
                
                # MGRCI - EC codes (ERIND 1-12)
                for i in range(1, 13):
                    ec_col = f'ERIND={i}'
                    ec_val = get_val(ec_col)
                    if ec_val:
                        mml_output.append(f"MGRCI:AREA={utran_cell},EC={ec_val},ERIND={i};")
                
                mml_output.append(f"MGRCP:AREA={utran_cell};")
                mml_output.append("")
    else:
        mml_output.append("// ERROR: No se encontraron datos en la hoja MscParameter")

    # Comandos de salida para el primer MSC
    mml_output.append("exit;")
    mml_output.append("exit")
    mml_output.append("")

    # Definir los MSCs adicionales con sus IPs
    additional_mscs = [
        {"name": "SAMBC01", "ip": "172.18.211.5"},
        {"name": "SAMBC02", "ip": "172.18.250.37"},
        {"name": "IQMBC01", "ip": "172.16.51.85"}
    ]

    # Replicar comandos para cada MSC adicional
    for msc in additional_mscs:
        mml_output.append("@COMMENT +---------------------------------------------------------------+ ##")
        mml_output.append(f"@COMMENT |    CREACION DE CELDAS EN MSC {msc['name']}         | ##")
        mml_output.append("@COMMENT +---------------------------------------------------------------+ ##")
        mml_output.append("")
        mml_output.append(f"ssh -l (#USUARIO ENM#) {msc['ip']}")
        mml_output.append("(#PSWD ENM#)")
        mml_output.append("mml")
        mml_output.append("@T 2")
        mml_output.append("")

        # Replicar los mismos comandos MML para este MSC
        if df_msc is not None and not df_msc.empty:
            for index, row in df_msc.iterrows():
                def get_val(col_name):
                    for col in df_msc.columns:
                        if col_name.lower() == col.strip().lower():
                            val = str(row[col]).strip()
                            if val and val.lower() != 'nan':
                                return val
                    return ""

                utran_cell = get_val('Utrancell')
                locno = get_val('LOCNO')
                ro = get_val('RO')
                ea = get_val('EA')
                zc = get_val('ZC')
                
                if utran_cell and locno:
                    mml_output.append(f"MGRCE:AREA={utran_cell};")
                    mml_output.append(f"MGLCE:AREA={utran_cell};")
                    mml_output.append(f"MGLNE:LOCNO={locno};")
                    mml_output.append(f"MGAAE:AREA={utran_cell};")
                    mml_output.append("")
                    
                    site = get_val('Site')
                    if site:
                        sai = f"730-01-10513-{site}"
                        mml_output.append(f"MGAAI:AREA={utran_cell},SAI={sai};")
                    
                    if ro and ea:
                        mml_output.append(f"MGAAC:AREA={utran_cell},RO={ro},EA={ea};")
                    
                    mml_output.append(f"MGAAP:AREA={utran_cell};")
                    mml_output.append(f"MGLNI:LOCNO={locno};")
                    mml_output.append(f"MGLCI:LOCNO={locno},AREA={utran_cell};")
                    mml_output.append(f"MGLNP:LOCNO={locno};")
                    
                    if zc:
                        mml_output.append(f"MGZCI:ZC={zc},LOCNO={locno};")
                    
                    mml_output.append(f"MGZCP:LOCNO={locno};")
                    mml_output.append(f"MGLCP:AREA={utran_cell};")
                    
                    for i in range(1, 13):
                        ec_col = f'ERIND={i}'
                        ec_val = get_val(ec_col)
                        if ec_val:
                            mml_output.append(f"MGRCI:AREA={utran_cell},EC={ec_val},ERIND={i};")
                    
                    mml_output.append(f"MGRCP:AREA={utran_cell};")
                    mml_output.append("")

        # Comandos de salida para este MSC
        mml_output.append("exit;")
        mml_output.append("exit")
        mml_output.append("")

    content = "\n".join(mml_output)
    filename = f"04_MSC_{rnc_value}_{nemonico}_PL_Delete_Create_Cells.mos"
    
    return True, content, filename
