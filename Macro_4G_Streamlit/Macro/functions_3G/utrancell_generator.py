
# =====================================================================
# utrancell_generator.py - Generación de script UtranCell para 3G
# =====================================================================

from typing import Tuple, Dict, Any, Optional
from datetime import datetime

# =====================================================================
# FUNCIÓN PRINCIPAL DE GENERACIÓN
# =====================================================================

def generate_utrancell_mos(nemonico: str, rnd_data: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, str]:
    """
    Genera el contenido del archivo MOS para UtranCell.
    Retorna: (Success, Content, Filename)
    """
    mml_output = []
    
    # 1. Obtener Datos
    # Necesitamos iterar sobre la hoja UtranCell
    df_utran = None
    if rnd_data:
        for key in rnd_data.keys():
            if key.lower() == 'utrancell':
                df_utran = rnd_data[key]
                break
    
    # 2. Generar Header
    now = datetime.now()
    hora = now.strftime("%H:%M:%S")
    fecha = now.strftime("%d-%m-%Y")
    
    # El usuario pidió "PMER01" como ejemplo, pero usaremos el nemonico real
    # Si hay un valor RNC disponible en otro lado, podríamos usarlo, pero aquí usaremos el nemonico
    # OJO: El ejemplo del usuario muestra dos lineas de NEMONICO, una con PMER01 y otra con ULA781
    # Asumiremos que la primera es el RNC y la segunda el Sitio.
    # Intentaremos sacar el RNC de Iublink si está disponible en rnd_data, igual que en el otro generador
    
    rnc_value = "UNKNOWN_RNC"
    if rnd_data:
        for key in rnd_data.keys():
            if key.lower() == 'iublink':
                df_iub = rnd_data[key]
                if df_iub is not None and not df_iub.empty:
                    for col in df_iub.columns:
                        if col.strip().lower() == 'rnc':
                            val = str(df_iub.iloc[0][col]).strip()
                            if val and val.lower() != 'nan':
                                rnc_value = val
                            break
                break

    mml_output.append("//////////////////////-PDUARTE-///////////////////////////////")
    mml_output.append("//")
    mml_output.append("// SCRIPT     : CREATE_CELLS")
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

    # 4. Sección ServiceAreas
    mml_output.append("#############################################################")
    mml_output.append(f"### ServiceAreas {rnc_value}")
    mml_output.append("#############################################################")
    mml_output.append("")

    if df_utran is not None and not df_utran.empty:
        # Helper para buscar columna case-insensitive
        def get_val(row, col_name_part):
            for col in df_utran.columns:
                if col_name_part.lower() == col.strip().lower():
                    val = str(row[col]).strip()
                    if val and val.lower() != 'nan':
                        return val
            return ""

        for index, row in df_utran.iterrows():
            lac = get_val(row, 'lac')
            local_cell_id = get_val(row, 'localCellId') # ServiceArea
            sac = get_val(row, 'sac')
            
            # Convertir floats a ints
            if lac.replace('.','',1).isdigit() and '.' in lac: lac = str(int(float(lac)))
            if local_cell_id.replace('.','',1).isdigit() and '.' in local_cell_id: local_cell_id = str(int(float(local_cell_id)))
            if sac.replace('.','',1).isdigit() and '.' in sac: sac = str(int(float(sac)))

            if lac and local_cell_id and sac:
                mml_output.append(f"crn RncFunction=1,LocationArea={lac},ServiceArea={sac}")
                mml_output.append(f"sac {sac}")
                mml_output.append(f"userLabel SAC_{sac}")
                mml_output.append("end")
                mml_output.append("")

    # 5. Sección Cells PMER01
    mml_output.append("#############################################################")
    mml_output.append(f"### Cells {rnc_value}")
    mml_output.append("#############################################################")
    mml_output.append("")

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
            
            # Identificadores principales
            cid = get_val('cId')
            local_cell_id = get_val('localCellId')
            if not cid: cid = local_cell_id # Fallback
            
            if cid:
                # --- CR Command ---
                mml_output.append(f"cr RncFunction=1,UtranCell=U{cid}")
                
                # Argumentos del CR (orden importa según ejemplo)
                mml_output.append(f"{local_cell_id} #localCellId")
                mml_output.append(f"{cid} #cId")
                mml_output.append(f"{get_val('tCell')} #tCell")
                mml_output.append(f"{get_val('uarfcnUl')} #uarfcnUl")
                mml_output.append(f"{get_val('uarfcnDl')} #uarfcnDl")
                mml_output.append(f"{get_val('primaryScramblingCode')} #primaryScramblingCode")
                mml_output.append(f"{get_val('sib1PlmnScopeValueTag')} #sib1PlmnScopeValueTag")
                
                lac = get_val('lac')
                if not lac: lac = get_val('LocationArea') # Try alternative name
                mml_output.append(f"LocationArea={lac} #locationAreaRef")
                
                sac = get_val('sac')
                mml_output.append(f"LocationArea={lac},ServiceArea={sac} #serviceAreaRef")
                
                iub_link = get_val('iubLinkRef')
                if not iub_link: iub_link = f"Iub_{nemonico}" # Fallback default
                
                # Fix double prefix
                if not iub_link.lower().startswith("iublink="):
                    mml_output.append(f"IubLink={iub_link} #iubLinkRef")
                else:
                    mml_output.append(f"{iub_link} #iubLinkRef")
                
                mocn = get_val('mocnCellProfileRef')
                if mocn:
                    if not mocn.lower().startswith("mocncellprofile="):
                         mml_output.append(f"MocnCellProfile={mocn} #mocnCellProfileRef")
                    else:
                         mml_output.append(f"{mocn} #mocnCellProfileRef")
                mml_output.append("")
                
                # --- SET Commands ---
                # Lista de atributos simples a setear
                simple_attrs = [
                    'administrativeState', 'agpsEnabled', 'amrNbSelector', 'amrWbRateDlMax', 'amrWbRateUlMax',
                    'anrBlackList', 'aseDlAdm', 'aseUlAdm', 'bchPower', 'cbsSchedulePeriodLength',
                    'cellBroadcastSac', 'cellReserved', 'codeLoadThresholdDlSf128', 'compModeAdm',
                    'cpcSupport', 'ctchAdmMargin', 'ctchOccasionPeriod', 'dchIflsMarginCode',
                    'dchIflsMarginPower', 'dchIflsThreshCode', 'dchIflsThreshPower', 'dlCodeAdm',
                    'dlCodeOffloadLimit', 'dlPowerOffloadLimit', 'dmcrEnabled', 'dnclEnabled',
                    'downswitchTimer', 'eulNonServingCellUsersAdm', 'eulServingCellUsersAdm',
                    'eulServingCellUsersAdmTti2', 'fachMeasOccaCycLenCoeff', 'fdpchSupport',
                    'ganHoEnabled', 'hardIfhoCorr', 'hoType', 'hsdpaUsersAdm', 'hsdpaUsersOffloadLimit',
                    'hsdschInactivityTimer', 'hsdschInactivityTimerCpc', 'hsIflsHighLoadThresh',
                    'hsIflsMarginUsers', 'hsIflsPowerLoadThresh', 'hsIflsRedirectLoadLimit',
                    'hsIflsSpeechMultiRabTrigg', 'hsIflsThreshUsers', 'iFCong', 'iFHyst',
                    'iflsCpichEcnoThresh', 'iflsMode', 'iflsRedirectUarfcn', 'inactivityTimeMultiPsInteractive',
                    'inactivityTimer', 'inactivityTimerEnhUeDrx', 'inactivityTimerPch', 'individualOffset',
                    'interFreqFddMeasIndicator', 'interPwrMax', 'interRate', 'loadBasedHoSupport',
                    'loadBasedHoType', 'loadSharingGsmFraction', 'loadSharingGsmThreshold', 'loadSharingMargin',
                    'localCellId', 'maximumTransmissionPower', 'maxPwrMax', 'maxRate', 'maxTxPowerUl',
                    'minimumRate', 'minPwrMax', 'minPwrRl', 'nOutSyncInd', 'pathlossThreshold',
                    'primaryCpichPower', 'primarySchPower', 'primaryScramblingCode', 'pwrAdm',
                    'qHyst1', 'qHyst2', 'qQualMin', 'qRxLevMin', 'qualMeasQuantity', 'rac',
                    'redirectUarfcn', 'releaseRedirect', 'releaseRedirectHsIfls', 'reportingRange1a',
                    'reportingRange1b', 'rlFailureT', 'rrcLcEnabled', 'sac', 'secondaryCpichPower',
                    'secondarySchPower', 'servDiffRrcAdmHighPrioProfile', 'sf128Adm', 'sf16Adm',
                    'sf16AdmUl', 'sf16gAdm', 'sf32Adm', 'sf4AdmUl', 'sf64AdmUl', 'sf8Adm',
                    'sf8AdmUl', 'sf8gAdmUl', 'sHcsRat', 'sib1PlmnScopeValueTag', 'sInterSearch',
                    'sIntraSearch', 'spare', 'sRatSearch', 'srbAdmExempt', 'standAloneSrbSelector',
                    'tCell', 'timeToTrigger1a', 'timeToTrigger1b', 'transmissionScheme', 'treSelection',
                    'uarfcnDl', 'uarfcnUl', 'usedFreqThresh2dEcno', 'usedFreqThresh2dRscp',
                    'dlCodePowerCmEnabled', 'eulMcServingCellUsersAdmTti2', 'primaryTpsCell',
                    'rwrEutraCc', 'rachOverloadProtect', 'ifIratHoPsIntHsEnabled',
                    'cellUpdateConfirmCsInitRepeat', 'cellUpdateConfirmPsInitRepeat', 'lteMeasEnabled',
                    'psHoToLteEnabled'
                ]
                
                for attr in simple_attrs:
                    val = get_val(attr)
                    if val:
                        mml_output.append(f"set RncFunction=1,UtranCell=U{cid} {attr} {val}")
                
                # Atributos complejos / especiales
                
                # accessClassesBarredCs/Ps/NBarred
                acb_cs = get_val('accessClassesBarredCs')
                if acb_cs:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} accessClassesBarredCs {acb_cs}")
                
                acb_ps = get_val('accessClassesBarredPs')
                if acb_ps:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} accessClassesBarredPs {acb_ps}")
                
                acb_n = get_val('accessClassNBarred')
                if acb_n:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} accessClassNBarred {acb_n}")
                
                # spareA
                sparea = get_val('spareA')
                if sparea:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} spareA {sparea}")
                
                # userLabel
                user_label = get_val('userLabel')
                if user_label:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} userLabel {user_label}")
                
                # mocnCellProfileRef
                if mocn:
                    if not mocn.lower().startswith("mocncellprofile="):
                        mml_output.append(f"set RncFunction=1,UtranCell=U{cid} mocnCellProfileRef MocnCellProfile={mocn}")
                    else:
                        mml_output.append(f"set RncFunction=1,UtranCell=U{cid} mocnCellProfileRef {mocn}")
                
                # absPrioCellRes
                abs_prio = get_val('absPrioCellRes')
                if not abs_prio:
                    # Try to construct with prefixed columns
                    prio = get_val('absPrioCellRes_cellReselectionPriority')
                    s1 = get_val('absPrioCellRes_sPrioritySearch1')
                    s2 = get_val('absPrioCellRes_sPrioritySearch2')
                    low = get_val('absPrioCellRes_threshServingLow')
                    fach = get_val('absPrioCellRes_measIndFach')
                    if prio and s1 and s2 and low and fach:
                        abs_prio = f"cellReselectionPriority={prio},sPrioritySearch1={s1},sPrioritySearch2={s2},threshServingLow={low},measIndFach={fach}"
                if abs_prio:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} absPrioCellRes {abs_prio}")
                
                # admBlockRedirection
                adm_block = get_val('admBlockRedirection')
                if not adm_block:
                    gsm = get_val('admBlockRedirection_gsmRrc')
                    rrc = get_val('admBlockRedirection_rrc')
                    speech = get_val('admBlockRedirection_speech')
                    if gsm and rrc and speech:
                        adm_block = f"gsmRrc={gsm},rrc={rrc},speech={speech}"
                if adm_block:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} admBlockRedirection {adm_block}")
                
                # anrIafUtranCellConfig
                anr_conf = get_val('anrIafUtranCellConfig')
                if not anr_conf:
                    anr_en = get_val('anrIafUtranCellConfig_anrEnabled')
                    rel_add = get_val('anrIafUtranCellConfig_relationAddEnabled')
                    if anr_en and rel_add:
                        anr_conf = f"anrEnabled={anr_en},relationAddEnabled={rel_add}"
                if anr_conf:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} anrIafUtranCellConfig {anr_conf}")
                
                # antennaPosition
                lat = get_val('antennaPosition_latitude')
                sign = get_val('antennaPosition_latitudeSign')
                lon = get_val('antennaPosition_longitude')
                if lat and sign and lon:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} antennaPosition latitude={lat},latitudeSign={sign},longitude={lon}")
                
                # aseLoadThresholdUlSpeech
                ase_load = get_val('aseLoadThresholdUlSpeech')
                if not ase_load:
                    amr12 = get_val('aseLoadThresholdUlSpeech_amr12200')
                    amr59 = get_val('aseLoadThresholdUlSpeech_amr5900')
                    amr79 = get_val('aseLoadThresholdUlSpeech_amr7950')
                    amrWb12 = get_val('aseLoadThresholdUlSpeech_amrWb12650')
                    amrWb88 = get_val('aseLoadThresholdUlSpeech_amrWb8850')
                    if amr12 and amr59 and amr79 and amrWb12 and amrWb88:
                        ase_load = f",amr12200={amr12},amr5900={amr59},amr7950={amr79},amrWb12650={amrWb12},amrWb8850={amrWb88}"
                if ase_load:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} aseLoadThresholdUlSpeech {ase_load}")
                
                # cyclicAcb
                cyc = get_val('cyclicAcb')
                if not cyc:
                    acb_en = get_val('cyclicAcb_acbEnabled')
                    rot_size = get_val('cyclicAcb_rotationGroupSize')
                    if acb_en and rot_size:
                        cyc = f"acbEnabled={acb_en},rotationGroupSize={rot_size}"
                if cyc:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} cyclicAcb {cyc}")
                
                # hcsSib3Config
                hcs = get_val('hcsSib3Config')
                if not hcs:
                    hcs_prio = get_val('hcsSib3Config_hcsPrio')
                    q_hcs = get_val('hcsSib3Config_qHcs')
                    s_search = get_val('hcsSib3Config_sSearchHcs')
                    if hcs_prio and q_hcs and s_search:
                        hcs = f"hcsPrio={hcs_prio},qHcs={q_hcs},sSearchHcs={s_search}"
                if hcs:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} hcsSib3Config {hcs}")
                
                # hcsUsage
                hcs_use = get_val('hcsUsage')
                if not hcs_use:
                    conn = get_val('hcsUsage_connectedMode')
                    idle = get_val('hcsUsage_idleMode')
                    if conn and idle:
                        hcs_use = f"connectedMode={conn},idleMode={idle}"
                if hcs_use:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} hcsUsage {hcs_use}")
                
                # hsIflsDownswitchTrigg
                hs_down = get_val('hsIflsDownswitchTrigg')
                if not hs_down:
                    fast = get_val('hsIflsDownswitchTrigg_fastDormancy')
                    to_fach = get_val('hsIflsDownswitchTrigg_toFach')
                    to_ura = get_val('hsIflsDownswitchTrigg_toUra')
                    if fast and to_fach and to_ura:
                        hs_down = f"fastDormancy={fast},toFach={to_fach},toUra={to_ura}"
                if hs_down:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} hsIflsDownswitchTrigg {hs_down}")
                
                # hsIflsTrigger
                hs_trig = get_val('hsIflsTrigger')
                if not hs_trig:
                    from_fach = get_val('hsIflsTrigger_fromFach')
                    from_ura = get_val('hsIflsTrigger_fromUra')
                    if from_fach and from_ura:
                        hs_trig = f"fromFach={from_fach},fromUra={from_ura}"
                if hs_trig:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} hsIflsTrigger {hs_trig}")
                
                # pagingPermAccessCtrl
                pag = get_val('pagingPermAccessCtrl')
                if not pag:
                    loc_acb = get_val('pagingPermAccessCtrl_locRegAcb')
                    loc_restr = get_val('pagingPermAccessCtrl_locRegRestr')
                    pag_restr = get_val('pagingPermAccessCtrl_pagingRespRestr')
                    if loc_acb and loc_restr and pag_restr:
                        pag = f"locRegAcb={loc_acb},locRegRestr={loc_restr},pagingRespRestr={pag_restr}"
                if pag:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} pagingPermAccessCtrl {pag}")
                
                # pwrLoadThresholdDlSpeech
                pwr_load = get_val('pwrLoadThresholdDlSpeech')
                if not pwr_load:
                    amr12 = get_val('pwrLoadThresholdDlSpeech_amr12200')
                    amr59 = get_val('pwrLoadThresholdDlSpeech_amr5900')
                    amr79 = get_val('pwrLoadThresholdDlSpeech_amr7950')
                    amrWb12 = get_val('pwrLoadThresholdDlSpeech_amrWb12650')
                    amrWb88 = get_val('pwrLoadThresholdDlSpeech_amrWb8850')
                    if amr12 and amr59 and amr79 and amrWb12 and amrWb88:
                        pwr_load = f"amr12200={amr12},amr5900={amr59},amr7950={amr79},amrWb12650={amrWb12},amrWb8850={amrWb88}"
                if pwr_load:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} pwrLoadThresholdDlSpeech {pwr_load}")
                
                # rateSelectionPsInteractive
                rate_sel = get_val('rateSelectionPsInteractive')
                if not rate_sel:
                    chan = get_val('rateSelectionPsInteractive_channelType')
                    dl = get_val('rateSelectionPsInteractive_dlPrefRate')
                    ul = get_val('rateSelectionPsInteractive_ulPrefRate')
                    if chan and dl and ul:
                        rate_sel = f"channelType={chan},dlPrefRate={dl},ulPrefRate={ul}"
                if rate_sel:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} rateSelectionPsInteractive {rate_sel}")
                
                # releaseRedirectEutraTriggers
                rel_red = get_val('releaseRedirectEutraTriggers')
                if not rel_red:
                    cs_rel = get_val('releaseRedirectEutraTriggers_csFallbackCsRelease')
                    cs_dch = get_val('releaseRedirectEutraTriggers_csFallbackDchToFach')
                    dch_fach = get_val('releaseRedirectEutraTriggers_dchToFach')
                    fach_ura = get_val('releaseRedirectEutraTriggers_fachToUra')
                    fast = get_val('releaseRedirectEutraTriggers_fastDormancy')
                    norm = get_val('releaseRedirectEutraTriggers_normalRelease')
                    if cs_rel and cs_dch and dch_fach and fach_ura and fast and norm:
                        rel_red = f"csFallbackCsRelease={cs_rel},csFallbackDchToFach={cs_dch},dchToFach={dch_fach},fachToUra={fach_ura},fastDormancy={fast},normalRelease={norm}"
                if rel_red:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} releaseRedirectEutraTriggers {rel_red}")
                
                # serviceRestrictions
                srv_res = get_val('serviceRestrictions')
                if not srv_res:
                    vid = get_val('serviceRestrictions_csVideoCalls')
                    if vid:
                        srv_res = f"csVideoCalls={vid}"
                if srv_res:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} serviceRestrictions {srv_res}")
                
                # tpsCellThresholds
                tps = get_val('tpsCellThresholds')
                if not tps:
                    en = get_val('tpsCellThresholds_tpsCellThreshEnabled')
                    lock = get_val('tpsCellThresholds_tpsLockThreshold')
                    unlock = get_val('tpsCellThresholds_tpsUnlockThreshold')
                    if en and lock and unlock:
                        tps = f"tpsCellThreshEnabled={en},tpsLockThreshold={lock},tpsUnlockThreshold={unlock}"
                if tps:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} tpsCellThresholds {tps}")
                
                # routingAreaRef
                rac_val = get_val('rac')
                if lac and rac_val:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} routingAreaRef LocationArea={lac},RoutingArea={rac_val}")
                
                # uraref
                ura_val = get_val('uraList')
                if ura_val:
                    mml_output.append(f"set RncFunction=1,UtranCell=U{cid} uraref ura={ura_val}")
                
                mml_output.append("")
    else:
        mml_output.append("// ERROR: No se encontraron datos en la hoja UtranCell")

    # 6. Sección Rach PMER01
    mml_output.append("#############################################################")
    mml_output.append(f"### Rach {rnc_value}")
    mml_output.append("#############################################################")
    mml_output.append("")
    
    df_rach = None
    if rnd_data:
        for key in rnd_data.keys():
            if key.lower() == 'rach':
                df_rach = rnd_data[key]
                break
    
    if df_rach is not None and not df_rach.empty:
        for index, row in df_rach.iterrows():
            # Helper para obtener valor de columna (Rach specific)
            def get_rach_val(col_name):
                for col in df_rach.columns:
                    if col_name.lower() == col.strip().lower():
                        val = str(row[col]).strip()
                        if val and val.lower() != 'nan':
                            return val
                return ""

            utran_cell = get_rach_val('Utrancell')
            if utran_cell:
                # CRN Command
                # Asumimos Rach=1 fijo ya que no hay columna de ID de Rach, y el ejemplo usa Rach=1
                mml_output.append(f"crn RncFunction=1,UtranCell={utran_cell},Rach=1")
                
                # Atributos
                attrs = [
                    'administrativeState', 'aichPower', 'aichTransmissionTiming',
                    'constantValueCprach', 'increasedRachCoverageEnabled', 'maxPreambleCycle',
                    'nb01Max', 'nb01Min', 'powerOffsetP0', 'powerOffsetPpm',
                    'preambleRetransMax', 'preambleSignatures', 'scramblingCodeWordNo',
                    'spreadingFactor', 'subChannelNo'
                ]
                
                for attr in attrs:
                    val = get_rach_val(attr)
                    if val:
                        mml_output.append(f"{attr} {val}")
                
                # userLabel (Solo si existe en RND, para cumplir "no defaults")
                user_label = get_rach_val('userLabel')
                if user_label:
                    mml_output.append(f"userLabel {user_label}")
                
                mml_output.append("end")
                mml_output.append("")
    else:
        mml_output.append("// ERROR: No se encontraron datos en la hoja Rach")

    # 7. Sección PCH PMER01
    mml_output.append("#############################################################")
    mml_output.append(f"### PCH {rnc_value}")
    mml_output.append("#############################################################")
    mml_output.append("")
    
    df_pch = None
    if rnd_data:
        for key in rnd_data.keys():
            if key.lower() == 'pch':
                df_pch = rnd_data[key]
                break
    
    if df_pch is not None and not df_pch.empty:
        for index, row in df_pch.iterrows():
            # Helper para obtener valor de columna (Pch specific)
            def get_pch_val(col_name):
                for col in df_pch.columns:
                    if col_name.lower() == col.strip().lower():
                        val = str(row[col]).strip()
                        if val and val.lower() != 'nan':
                            return val
                return ""

            utran_cell = get_pch_val('Utrancell')
            if utran_cell:
                # CRN Command
                # Asumimos Pch=1 fijo
                mml_output.append(f"crn RncFunction=1,UtranCell={utran_cell},Pch=1")
                
                # Atributos
                attrs = [
                    'administrativeState', 'pchPower', 'pichPower', 'sccpchOffset'
                ]
                
                for attr in attrs:
                    val = get_pch_val(attr)
                    if val:
                        mml_output.append(f"{attr} {val}")
                
                # userLabel
                user_label = get_pch_val('userLabel')
                if user_label:
                    mml_output.append(f"userLabel {user_label}")
                
                mml_output.append("end")
                mml_output.append("")
    else:
        mml_output.append("// ERROR: No se encontraron datos en la hoja Pch")

    # 8. Sección HSDSCH PMER01
    mml_output.append("#############################################################")
    mml_output.append(f"### Hsdsch {rnc_value}")
    mml_output.append("#############################################################")
    mml_output.append("")
    
    df_hsd = None
    if rnd_data:
        for key in rnd_data.keys():
            if key.lower() == 'hsdsch':
                df_hsd = rnd_data[key]
                break
    
    if df_hsd is not None and not df_hsd.empty:
        for index, row in df_hsd.iterrows():
            # Helper para obtener valor de columna (Hsdsch specific)
            def get_hsd_val(col_name):
                for col in df_hsd.columns:
                    if col_name.lower() == col.strip().lower():
                        val = str(row[col]).strip()
                        if val and val.lower() != 'nan':
                            return val
                return ""

            utran_cell = get_hsd_val('Utrancell')
            if utran_cell:
                # CRN Command
                # Asumimos Hsdsch=1 fijo
                mml_output.append(f"crn RncFunction=1,UtranCell={utran_cell},Hsdsch=1")
                
                # Atributos
                attrs = [
                    'administrativeState', 'codeThresholdPdu656', 'cqiFeedbackCycle',
                    'deltaAck1', 'deltaAck2', 'deltaCqi1', 'deltaCqi2',
                    'deltaNack1', 'deltaNack2', 'hsMeasurementPowerOffset',
                    'initialAckNackRepetitionFactor', 'initialCqiRepetitionFactor',
                    'numHsPdschCodes', 'numHsScchCodes'
                ]
                
                for attr in attrs:
                    val = get_hsd_val(attr)
                    if val:
                        mml_output.append(f"{attr} {val}")
                
                # userLabel
                # User instruction: Default to "Hsdsch 1"
                user_label = get_hsd_val('userLabel')
                if not user_label:
                    user_label = "Hsdsch 1"
                
                mml_output.append(f"userLabel {user_label}")
                
                mml_output.append("end")
                mml_output.append("")
    else:
        mml_output.append("// ERROR: No se encontraron datos en la hoja Hsdsch")

    # 9. Sección FACH PMER01
    mml_output.append("#############################################################")
    mml_output.append(f"### Fach {rnc_value}")
    mml_output.append("#############################################################")
    mml_output.append("")
    
    df_fach = None
    if rnd_data:
        for key in rnd_data.keys():
            if key.lower() == 'fach':
                df_fach = rnd_data[key]
                break
    
    if df_fach is not None and not df_fach.empty:
        for index, row in df_fach.iterrows():
            # Helper para obtener valor de columna (Fach specific)
            def get_fach_val(col_name):
                for col in df_fach.columns:
                    if col_name.lower() == col.strip().lower():
                        val = str(row[col]).strip()
                        if val and val.lower() != 'nan':
                            return val
                return ""

            utran_cell = get_fach_val('Utrancell')
            if utran_cell:
                # CRN Command
                # Asumimos Fach=1 fijo
                mml_output.append(f"crn RncFunction=1,UtranCell={utran_cell},Fach=1")
                
                # Atributos
                attrs = [
                    'administrativeState', 'maxFach1Power', 'maxFach2Power',
                    'pOffset1Fach', 'pOffset3Fach', 'sccpchOffset'
                ]
                
                for attr in attrs:
                    val = get_fach_val(attr)
                    if val:
                        mml_output.append(f"{attr} {val}")
                
                # userLabel
                # User instruction: Default to "Fach 1"
                user_label = get_fach_val('userLabel')
                if not user_label:
                    user_label = "Fach 1"
                
                mml_output.append(f"userLabel {user_label}")
                
                mml_output.append("end")
                mml_output.append("")
    else:
        mml_output.append("// ERROR: No se encontraron datos en la hoja Fach")

    # 10. Sección EUL PMER01
    mml_output.append("#############################################################")
    mml_output.append(f"### Eul {rnc_value}")
    mml_output.append("#############################################################")
    mml_output.append("")
    
    df_eul = None
    if rnd_data:
        for key in rnd_data.keys():
            if key.lower() == 'eul':
                df_eul = rnd_data[key]
                break
    
    if df_eul is not None and not df_eul.empty:
        for index, row in df_eul.iterrows():
            # Helper para obtener valor de columna (Eul specific)
            def get_eul_val(col_name):
                for col in df_eul.columns:
                    if col_name.lower() == col.strip().lower():
                        val = str(row[col]).strip()
                        if val and val.lower() != 'nan':
                            return val
                return ""

            utran_cell = get_eul_val('Utrancell')
            if utran_cell:
                # CRN Command
                # Asumimos Hsdsch=1, Eul=1 fijo
                mml_output.append(f"crn RncFunction=1,UtranCell={utran_cell},Hsdsch=1,Eul=1")
                
                # Atributos
                attrs = [
                    'administrativeState', 'eulDchBalancingEnabled', 'eulDchBalancingLoad',
                    'eulDchBalancingOverload', 'eulDchBalancingReportPeriod',
                    'eulDchBalancingSuspendDownSw', 'eulDchBalancingTimerNg',
                    'eulLoadTriggeredSoftCong', 'eulMaxTargetRtwp', 'numEagchCodes',
                    'numEhichErgchCodes', 'pathlossThresholdEulTti2', 'releaseAseUlNg',
                    'threshEulTti2Ecno'
                ]
                
                for attr in attrs:
                    val = get_eul_val(attr)
                    if val:
                        mml_output.append(f"{attr} {val}")
                
                # userLabel
                # User instruction: Default to "Eul 1"
                user_label = get_eul_val('userLabel')
                if not user_label:
                    user_label = "Eul 1"
                
                mml_output.append(f"userLabel {user_label}")
                
                mml_output.append("end")
                # Extra command requested by user
                mml_output.append(f"ld RncFunction=1,UtranCell={utran_cell},Hsdsch=1,Eul=1,MultiCarrier=1 #SystemCreated")
                mml_output.append("")
    else:
        mml_output.append("// ERROR: No se encontraron datos en la hoja Eul")

    # 11. Sección EULFACH PMER01
    mml_output.append("#############################################################")
    mml_output.append(f"### EulFach {rnc_value}")
    mml_output.append("#############################################################")
    mml_output.append("")
    
    df_efach = None
    if rnd_data:
        for key in rnd_data.keys():
            # El nombre de la hoja puede venir como 'E-Fach' o 'EFach' dependiendo del mapeo
            # En data_reader se guarda como 'EFach' (TitleCase sin guiones) o con la llave original
            if key.lower() == 'efach' or key.lower() == 'e-fach':
                df_efach = rnd_data[key]
                break
    
    if df_efach is not None and not df_efach.empty:
        for index, row in df_efach.iterrows():
            # Helper para obtener valor de columna (EulFach specific)
            def get_efach_val(col_name):
                for col in df_efach.columns:
                    if col_name.lower() == col.strip().lower():
                        val = str(row[col]).strip()
                        if val and val.lower() != 'nan':
                            return val
                return ""

            utran_cell = get_efach_val('Utrancell')
            if utran_cell:
                # CRN Command
                # Asumimos Hsdsch=1, Eul=1, EulFach=1 fijo
                mml_output.append(f"crn RncFunction=1,UtranCell={utran_cell},Hsdsch=1,Eul=1,EulFach=1")
                
                # Atributos
                attrs = [
                    'administrativeState', 'cEdchResourcesEai', 'deltaCqi',
                    'initDpcchPower', 'initFdpchPower', 'initInterferenceUl',
                    'maxCcchTime', 'maxCollisionResTime', 'numPreambleSignatures',
                    'ulSirTarget'
                ]
                
                for attr in attrs:
                    val = get_efach_val(attr)
                    if val:
                        mml_output.append(f"{attr} {val}")
                
                # userLabel
                # User instruction: Default to "EulFach 1"
                user_label = get_efach_val('userLabel')
                if not user_label:
                    user_label = "EulFach 1"
                
                mml_output.append(f"userLabel {user_label}")
                
                mml_output.append("end")
                mml_output.append("")
    else:
        mml_output.append("// ERROR: No se encontraron datos en la hoja E-Fach")

    mml_output.append("#############################################################")
    mml_output.append(f"#######################FIN del SCRIPT#######################")
    mml_output.append("#############################################################")
    content = "\n".join(mml_output)
    
    # Nombre del archivo: 02_valor de RND_Nemonico_PL_UtranCell.mos
    # "valor de RND" asumimos que es el RNC value como en el otro archivo
    filename = f"02_{rnc_value}_{nemonico}_PL_UtranCell.mos"
    
    return True, content, filename
