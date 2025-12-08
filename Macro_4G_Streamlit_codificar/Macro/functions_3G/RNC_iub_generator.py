
# =====================================================================
# RNC_iub_generator.py - Generación de script IUB_RNC para 3G
# =====================================================================

from typing import Tuple, Dict, Any, Optional
from datetime import datetime

# =====================================================================
# FUNCIÓN PRINCIPAL DE GENERACIÓN
# =====================================================================

def generate_rnc_iub_mos(nemonico: str, rnd_data: Optional[Dict[str, Any]] = None, wsh_data: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, str, str]:
    """
    Genera el contenido del archivo MOS para IUB_RNC.
    Retorna: (Success, Content, RNC_Value, Filename)
    """
    mml_output = []
    
    # 1. Obtener Datos
    rnc_value = "UNKNOWN_RNC"
    ip_trafico = "0.0.0.0"
    
    # Datos de WSH (IP_TRAFICO)
    if wsh_data:
        ip_trafico = wsh_data.get('IP_TRAFICO', "0.0.0.0")

    # Datos de RND (Iublink)
    df_iub = None
    if rnd_data:
        for key in rnd_data.keys():
            if key.lower() == 'iublink':
                df_iub = rnd_data[key]
                break
    
    iub_data = {}
    if df_iub is not None and not df_iub.empty:
        # Helper para buscar columna case-insensitive
        def get_val(row, col_name_part):
            for col in df_iub.columns:
                if col_name_part.lower() == col.strip().lower():
                    val = str(row[col]).strip()
                    if val and val.lower() != 'nan':
                        return val
            return ""

        # Usamos la primera fila
        row = df_iub.iloc[0]
        
        rnc_value = get_val(row, 'RNC') or "UNKNOWN_RNC"
        iub_data['Iub'] = get_val(row, 'Iub')
        iub_data['dlHwAdm'] = get_val(row, 'dlHwAdm')
        iub_data['rbsId'] = get_val(row, 'rbsId')
        iub_data['softCongThreshGbrBwDl'] = get_val(row, 'softCongThreshGbrBwDl')
        iub_data['softCongThreshGbrBwUl'] = get_val(row, 'softCongThreshGbrBwUl')
        iub_data['ulHwAdm'] = get_val(row, 'ulHwAdm')
        
        # Convertir floats a ints si es necesario
        for k, v in iub_data.items():
            if v.replace('.','',1).isdigit() and '.' in v:
                try:
                    iub_data[k] = str(int(float(v)))
                except:
                    pass

    # 2. Generar Header
    now = datetime.now()
    hora = now.strftime("%H:%M:%S")
    fecha = now.strftime("%d-%m-%Y")
    
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("//")
    mml_output.append("// SCRIPT     : IUB_RNC")
    mml_output.append(f"// NEMONICO   : {rnc_value}")
    mml_output.append(f"// NEMONICO   : {nemonico}")
    mml_output.append(f"// HORA       : {hora}")
    mml_output.append(f"// FECHA      : {fecha}")
    mml_output.append("//")
    mml_output.append("/////////////////////////////////////////////////////////////")
    mml_output.append("")

    # 3. Comandos Iniciales
    mml_output.append("confb+")
    mml_output.append("gs+")
    mml_output.append("lt all")
    mml_output.append("")

    # 4. Sección IubLink PMER01
    # Valores por defecto si no están en RND
    iub_name = iub_data.get('Iub', f"Iub_{nemonico}")
    dl_hw_adm = iub_data.get('dlHwAdm', "90")
    rbs_id = iub_data.get('rbsId', "13781") # Default del ejemplo
    soft_cong_dl = iub_data.get('softCongThreshGbrBwDl', "100")
    soft_cong_ul = iub_data.get('softCongThreshGbrBwUl', "100")
    ul_hw_adm = iub_data.get('ulHwAdm', "90")
    
    mml_output.append("#############################################################")
    mml_output.append(f"### IubLink {rnc_value}")
    mml_output.append("#############################################################")
    mml_output.append("")
    mml_output.append("lt all")
    mml_output.append("")
    mml_output.append(f"crn RncFunction=1,IubLink={iub_name}")
    mml_output.append("administrativeState 1")
    mml_output.append("controlPlaneTransportOption atm=0,ipv4=1")
    mml_output.append(f"dlHwAdm {dl_hw_adm}")
    mml_output.append("l2EstReqRetryTimeNbapC 5")
    mml_output.append("l2EstReqRetryTimeNbapD 5")
    mml_output.append("linkType 0")
    mml_output.append("poolRedundancy 0")
    mml_output.append("rSiteRef")
    mml_output.append(f"rbsId {rbs_id}")
    mml_output.append(f"remoteCpIpAddress1 {ip_trafico}")
    mml_output.append("remoteCpIpAddress2 000.000.000.000")
    mml_output.append("remoteSctpPortNbapC 5113")
    mml_output.append("remoteSctpPortNbapD 5114")
    mml_output.append("rncModuleAllocWeight 10")
    mml_output.append("rncModulePreferredRef ")
    mml_output.append(f"softCongThreshGbrBwDl {soft_cong_dl}")
    mml_output.append(f"softCongThreshGbrBwUl {soft_cong_ul}")
    mml_output.append("spare 0")
    mml_output.append("spareA 0,0,0,0,0,0,0,0,0,0")
    mml_output.append(f"ulHwAdm {ul_hw_adm}")
    mml_output.append(f"userLabel {iub_name}")
    mml_output.append("userPlaneGbrAdmBandwidthDl 10000")
    mml_output.append("userPlaneGbrAdmBandwidthUl 10000")
    mml_output.append("userPlaneGbrAdmEnabled 0")
    mml_output.append("userPlaneGbrAdmMarginDl 0")
    mml_output.append("userPlaneGbrAdmMarginUl 0")
    mml_output.append("userPlaneIpResourceRef IpAccessHostPool=Iub")
    mml_output.append("userPlaneTransportOption atm=0,ipv4=1")
    mml_output.append("end")
    mml_output.append("")

    # 5. Sección NodeSynch PMER01
    mml_output.append("#############################################################")
    mml_output.append(f"### NodeSynch {rnc_value}")
    mml_output.append("#############################################################")
    mml_output.append("")
    mml_output.append(f"ld RncFunction=1,IubLink={iub_name},NodeSynch=1 #SystemCreated")
    mml_output.append(f"lset RncFunction=1,IubLink={iub_name},NodeSynch=1$ fixedWindowSizeInit 12")
    mml_output.append(f"lset RncFunction=1,IubLink={iub_name},NodeSynch=1$ fixedWindowSizeSup 10")
    mml_output.append(f"lset RncFunction=1,IubLink={iub_name},NodeSynch=1$ maxAllowedIubRtt 500")
    mml_output.append(f"lset RncFunction=1,IubLink={iub_name},NodeSynch=1$ phaseDiffThreshold 50")
    mml_output.append(f"lset RncFunction=1,IubLink={iub_name},NodeSynch=1$ sampleIntervalInit 100")
    mml_output.append(f"lset RncFunction=1,IubLink={iub_name},NodeSynch=1$ sampleIntervalSup 10")
    mml_output.append(f"lset RncFunction=1,IubLink={iub_name},NodeSynch=1$ slidingWindowSize 100")
    mml_output.append(f"lset RncFunction=1,IubLink={iub_name},NodeSynch=1$ transportDelayMeasDiscRatio 0")
    mml_output.append(f"lset RncFunction=1,IubLink={iub_name},NodeSynch=1$ userLabel ")
    mml_output.append("")

    # 6. Sección IubEdch PMER01
    mml_output.append("#############################################################")
    mml_output.append(f"### IubEdch {rnc_value}")
    mml_output.append("#############################################################")
    mml_output.append("")
    mml_output.append(f"crn RncFunction=1,IubLink={iub_name},IubEdch=1")
    mml_output.append("edchDataFrameDelayThreshold 60")
    mml_output.append(f"userLabel IubEdch_{nemonico}")
    mml_output.append("end")
    mml_output.append("")
    mml_output.append(f"GET {iub_name}")
    mml_output.append("")
    mml_output.append("/////////////////////////fin script iub\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")

    content = "\n".join(mml_output)
    
    # Nombre del archivo: 01_{RNC_Value}{Nemonico}_PL_Create_IUB.mos
    filename = f"01_{rnc_value}{nemonico}_PL_Create_IUB.mos"
    
    return True, content, rnc_value, filename
