import pandas as pd
from datetime import datetime

# Diccionario de RNC IDs
RNC_ID_MAP = {
    "SAER02": "1322",
    "SAER03": "1323",
    "SAER04": "1324",
    "SAER05": "1325",
    "SAER06": "1326",
    "SAER08": "1328",
    "ANER01": "203",
    "PMR01": "1001",
    "RAER01": "610",
    "PMER01": "1006",
    "CUR03": "706",
    "TER04": "904",
    "PMR02": "1002",
    "VDR01": "1003",
    "PMR03": "1004",
    "IQR02": "103",
    "PAR01": "1201",
    "SPER01": "1330",
    "ANR01": "201",
    "ANR02": "202",
    "CPR04": "304",
    "QUR02": "507",
    "SNR02": "508",
    "RAR02": "602",
    "RAR03": "603",
    "RAR04": "604",
    "TAR01": "701",
    "CUR01": "702",
    "TAR02": "703",
    "TAR03": "704",
    "TAR04": "707",
    "CUR02": "705",
    "COR03": "804",
    "CHR02": "805",
    "CHR03": "807",
    "COR04": "806",
    "COER01": "811",
    "TER01": "901",
    "TER02": "902",
    "VAER01": "509",
    "CPR03": "303",
    "VDR02": "1005",
    "TER03": "903",
    "LSER01": "405",
    "IQR03": "104",
    "QUR03": "512",
    "PAR02": "1202",
    "CYR02": "1102",
    "IPR01": "510",
    "TEER01": "905",
    "IPR02": "511",
    "TAER01": "708"
}

def generate_cna_import(rnd_data, rnc_value, nemonico):
    """
    Genera el archivo 05_CNA_{RNC}_{Nemonico}_PL.import
    basado en la hoja UtranCell del RND.
    """
    cna_output = []

    # Header
    cna_output.append("..cnai # by CNAI R7F07, user #USUARIO")
    cna_output.append("..capabilities BASIC")
    cna_output.append(".subnetwork UNDEFINED")
    cna_output.append(".domain UTRAN_CELL")

    # Obtener RNCID del diccionario
    rncid = RNC_ID_MAP.get(rnc_value.upper(), "UNKNOWN")

    # Obtener datos de UtranCell
    df_utran = None
    if rnd_data:
        for key in rnd_data.keys():
            if key.lower() == 'utrancell':
                df_utran = rnd_data[key]
                break
    
    if df_utran is not None and not df_utran.empty:
        for index, row in df_utran.iterrows():
            # Helper para obtener valor de columna
            def get_val(col_name):
                for col in df_utran.columns:
                    if col_name.lower() == col.strip().lower():
                        val = str(row[col]).strip()
                        if val and val.lower() != 'nan':
                            return val
                return ""

            # Obtener valores necesarios
            cell_name = get_val('Utrancell')
            if not cell_name:
                cell_name = get_val('UtranCell')
            
            ci = get_val('cId')
            lac = get_val('locationArea')
            if not lac:
                lac = get_val('LAC')
            
            uarfcn_dl = get_val('uarfcnDl')
            primary_cpich = get_val('primaryCpichPower')
            psc = get_val('primaryScramblingCode')
            qrxlevmin = get_val('qRxLevMin')
            qqualmin = get_val('qQualMin')
            
            if cell_name and ci:
                # .set line
                cna_output.append(f".set {rncid}:{cell_name}")
                
                # Atributos
                cna_output.append(f'RNCID="{rncid}"')
                cna_output.append(f'CELL_NAME="{cell_name}"')
                cna_output.append(f'CI="{ci}"')
                cna_output.append('DIVERSITY="NODIV"')
                
                if uarfcn_dl:
                    cna_output.append(f'FDDARFCN={uarfcn_dl}')
                
                if lac:
                    cna_output.append(f'LAC="{lac}"')
                
                cna_output.append('MRSL=22')
                cna_output.append('MCC="730"')
                cna_output.append('MNC="001"')
                
                if qqualmin:
                    cna_output.append(f'QQUALMIN={qqualmin}')
                
                if psc:
                    cna_output.append(f'SCRCODE={psc}')
                
                cna_output.append('SRATSEARCH=0')
                cna_output.append(f'USERLABEL="{cell_name}"')
                cna_output.append('USEDFREQTHRESH2DECNO=-18')
                cna_output.append(f'SOURCENAME="UtranCell={cell_name}"')
                
                if primary_cpich:
                    cna_output.append(f'PRIMARYCPICHPOWER={primary_cpich}')
                
                if qrxlevmin:
                    cna_output.append(f'QRXLEVMIN={qrxlevmin}')
                
                cna_output.append('USEDFREQTHRESH2DRSCP=-109')
                
                # Closing line
                cna_output.append(f".set {rncid}:{cell_name} PG")
    else:
        cna_output.append("// ERROR: No se encontraron datos en la hoja UtranCell")

    # Footer
    cna_output.append("..END")

    content = "\n".join(cna_output)
    filename = f"05_CNA_{rnc_value}_{nemonico}_PL.import"
    
    return True, content, filename
