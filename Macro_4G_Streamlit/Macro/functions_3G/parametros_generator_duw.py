"""
Generador de archivo de parámetros MML para modo 3G-DUW
Crea el archivo 02_{Nemonico}_parametros.txt con configuración de parámetros
"""

from datetime import datetime
from typing import Dict, Any, Tuple, List
import pandas as pd


def generate_parametros_duw_txt(
    nemonico: str,
    wsh_data: Dict[str, Any],
    rnd_data: Dict[str, Any]
) -> Tuple[bool, str, str]:
    """
    Genera el archivo .txt de parámetros para modo DUW.
    
    Args:
        nemonico: Némónico del sitio
        wsh_data: Datos extraídos del WSH
        rnd_data: Datos del RND
    
    Returns:
        Tuple (success, txt_content, filename)
    """
    try:
        # Fecha y hora actual
        now = datetime.now()
        fecha_str = now.strftime("%d-%m-%Y")
        hora_str = now.strftime("%H:%M:%S")
        
        # Extraer RNC del RND si existe
        rnc_name = "UNKNOWN"
        if 'Iublink' in rnd_data and not rnd_data['Iublink'].empty:
            rnc_df = rnd_data['Iublink']
            if 'RNC' in rnc_df.columns:
                rnc_name = str(rnc_df['RNC'].iloc[0])
        
        # Lista para construir el contenido MML
        mml_output = []
        
        # Firma personalizada
        mml_output.append("///////////////////////////////////////////////////////////")
        mml_output.append("//")
        mml_output.append(f"// ARCHIVO     : 02_{nemonico}_parametros.txt")
        mml_output.append("// AUTOR       : Piero Ledesma")
        mml_output.append(f"// FECHA       : {fecha_str}")
        mml_output.append(f"// HORA        : {hora_str}")
        mml_output.append(f"// NEMONICO    : {nemonico}")
        mml_output.append(f"// RNC         : {rnc_name}")
        mml_output.append("//")
        mml_output.append("///////////////////////////////////////////////////////////")
        mml_output.append("")
        
        # Comandos iniciales
        mml_output.append("lt all")
        mml_output.append("confb+")
        mml_output.append("gs+")
        
        # ==================================================================
        # SECCIÓN 1: DownlinkBaseBandPool
        # ==================================================================
        mml_output.append("###################################################")
        mml_output.append("# ConfiguracionDUW3001 Hoja DownlinkBaseBandPool  #")
        mml_output.append("###################################################")
        
        # Buscar la hoja con diferentes nombres posibles
        dlbb_df = None
        if 'Downlinkbasebandpool' in rnd_data:
            dlbb_df = rnd_data['Downlinkbasebandpool']
        elif 'DOWNLINKBASEBANDPOOL' in rnd_data:
            dlbb_df = rnd_data['DOWNLINKBASEBANDPOOL']
        elif 'DownlinkBaseBandPool' in rnd_data:
            dlbb_df = rnd_data['DownlinkBaseBandPool']
        
        if dlbb_df is not None and not dlbb_df.empty:
            # Iterar por las filas y generar comandos lset
            for _, row in dlbb_df.iterrows():
                pool_id = row.get('DownlinkBaseBandPool', '')
                max_num_adch = row.get('maxNumADchReservation', '')
                
                if pool_id and max_num_adch:
                    mml_output.append(f"lset DownlinkBaseBandPool={pool_id} maxNumADchReservation {max_num_adch}")
        else:
            mml_output.append("// WARNING: Hoja DownlinkBaseBandPool no encontrada en RND")
        
        mml_output.append("")
        
        # ==================================================================
        # SECCIÓN 2: RbsLocalCell
        # ==================================================================
        mml_output.append("###################################################")
        mml_output.append("# RbsLocalCellId  ------>   Hoja RBSLocalCell     #")
        mml_output.append("###################################################")
        
        # Buscar la hoja con diferentes nombres posibles
        rbs_df = None
        if 'Rbslocalcell' in rnd_data:
            rbs_df = rnd_data['Rbslocalcell']
        elif 'RBSLOCALCELL' in rnd_data:
            rbs_df = rnd_data['RBSLOCALCELL']
        elif 'RBSLocalCell' in rnd_data:
            rbs_df = rnd_data['RBSLocalCell']
        elif 'Nodeblocalcell' in rnd_data:
            rbs_df = rnd_data['Nodeblocalcell']
        elif 'NODEBLOCALCELL' in rnd_data:
            rbs_df = rnd_data['NODEBLOCALCELL']
        
        if rbs_df is not None and not rbs_df.empty:
            # Lista de parámetros a setear (en el orden del ejemplo)
            parametros = [
                'airRateTypeSelector', 'chQualOffset', 'cpcCapability', 'cqiAdjustmentOn',
                'cqiErrors', 'cqiErrorsAbsent', 'defaultCqiHsFach', 'eDch2msTtiCapability',
                'eDchCapability', 'eHichMinCodePower', 'eulFachMaxDcchDtchTime', 'eulFachNumOfDecoders',
                'eulMaxNoSchEDch', 'eulMaxTdUsers', 'eulMcActivationDelayTime', 'eulMcCapability',
                'eulMinMarginCoverage', 'eulNoERgchGroups', 'eulTdSchedulingFactor', 'extraCompEnhUeDrx',
                'extraCompForSigHsFach', 'extraCompHsFach', 'extraHsScchCompEnhUeDrx', 'extraHsScchCompForSigHsFach',
                'extraHsScchCompHsFach', 'extraHsScchPowerForSrbOnHsdpa', 'extraPowerForSrbOnHsdpa', 'fDpchCapability',
                'featureState4wayRxDiversity', 'featureState64QamMimo', 'featureStateCpc', 'featureStateDchEulBalancing',
                'featureStateEnhancedLayer2', 'featureStateEnhUeDrx', 'featureStateEulDynRot', 'featureStateEulFach',
                'featureStateEulMc', 'featureStateEulTdScheduling', 'featureStateFDpchSrbOnHsdpa', 'featureStateHsdpaDbMc',
                'featureStateHsdpaDynamicCodeAllocation', 'featureStateHsdpaIncrementalRedundancy', 'featureStateHsdpaMc',
                'featureStateHsdpaMcInactCtrl', 'featureStateHsdpaMcMimo', 'featureStateHsdpaPowerSharing', 'featureStateHsFach',
                'featureStateHsOlpc', 'featureStateImprovedLayer2', 'featureStateMimo', 'featureStateNbir',
                'hsCodeResourceId', 'hsdpaCapability', 'hsdpaDbMcCapability', 'hsdpaMcActivityBufferThreshold',
                'hsdpaMcCapability', 'hsdpaMcInactivityTimer', 'hsdpaMcMimoCapability', 'hsdpaPowerSharingCapability',
                'hsPowerMargin', 'hsScchMaxCodePower', 'hsScchMinCodePower', 'localCellId',
                'maxDlPowerCapability', 'maxEAgchPowerDl', 'maxEAgchPowerDlTti2', 'maxNumEulUsers',
                'maxNumHsdpaUsers', 'maxNumHsPdschCodes', 'maxUserEHichERgchPowerDl', 'maxUserEHichPowerDlTti2',
                'minBitRate', 'minBitRateMinCqi', 'minDlPowerCapability', 'minSpreadingFactor',
                'ocnsIsActive', 'ocnsIsConfigured', 'powerSharingMaxTransmissionPower', 'qualityCheckPower',
                'qualityCheckPowerEHich', 'queueSelectAlgorithm', 'schCongPeriodGbr', 'schCongThreshGbr',
                'schCongThreshNonGbr', 'schMaxDelay', 'schMinPowerNonGbrHsUsers', 'schNoCongPeriodGbr',
                'schNoCongThreshGbr', 'schPowerDeltaCongGbr', 'schPrioForAbsResSharing', 'schWeight',
                'throughputPqxHsFach', 'featureStateHsAdaptiveBler', 'featureStateHsdpaMixedModePowerSharing'
            ]
            
            # Iterar por cada celda
            for _, row in rbs_df.iterrows():
                cell_id_original = row.get('RbsLocalCellId', '')
                
                if not cell_id_original:
                    continue
                
                # Convertir formato de S1C1 a S.*1.*1
                # Extraer números: S1C1 -> sector=1, cell=1
                import re
                match = re.match(r'S(\d+)C(\d+)', str(cell_id_original))
                if match:
                    sector_num = match.group(1)
                    cell_num = match.group(2)
                    cell_id = f"S.*{sector_num}.*{cell_num}"
                else:
                    cell_id = cell_id_original
                
                # Generar comandos lset para cada parámetro
                for param in parametros:
                    if param in row and pd.notna(row[param]):
                        valor = row[param]
                        
                        # Formatear el valor según el tipo
                        if isinstance(valor, bool):
                            valor_str = str(valor).lower()
                        elif isinstance(valor, (int, float)):
                            # Si es un número flotante sin decimales, convertir a int
                            if isinstance(valor, float) and valor.is_integer():
                                valor_str = str(int(valor))
                            else:
                                valor_str = str(valor)
                        elif isinstance(valor, str):
                            # Si es string vacío, dejar vacío
                            valor_str = valor if valor.strip() else ''
                        else:
                            valor_str = str(valor)
                        
                        # Generar comando lset
                        mml_output.append(f"lset {cell_id} {param} {valor_str}")
                
                # Agregar salto de línea entre celdas
                mml_output.append("")
        else:
            mml_output.append("// WARNING: Hoja RBSLocalCell no encontrada en RND")
        
        mml_output.append("")
        
        # ==================================================================
        # SECCIÓN 3: Carrier
        # ==================================================================
        mml_output.append("###################################################")
        mml_output.append("# Carrier      -----> Hoja Carrier                #")
        mml_output.append("###################################################")
        
        # Buscar la hoja con diferentes nombres posibles
        carrier_df = None
        if 'Carrier' in rnd_data:
            carrier_df = rnd_data['Carrier']
        elif 'CARRIER' in rnd_data:
            carrier_df = rnd_data['CARRIER']
        
        if carrier_df is not None and not carrier_df.empty:
            # Lista de parámetros simples (no combinados)
            parametros_simples = [
                'badBerFramesDtxHsOlpc', 'badBerFramesHsOlpc', 'cellRange', 'dlBandwidth',
                'dlFilterProfile', 'dlPowerOffsetCombinedCell', 'downlinkBaseBandPoolRef',
                'eulLockedOptimalNoiseFloorEstimate', 'eulMaxOwnUuLoad', 'eulMaxRotCoverage',
                'eulSlidingWindowTime', 'eulThermalLevelPrior', 'fccRotMarginHigh', 'fccRotMarginLow',
                'frequencyPlane', 'maxDlPowerCapability', 'minDlPowerCapability', 'numberOfRxBranches',
                'numberOfTxBranches', 'numOfDtxHsOlpc', 'periodDtxHsOlpc', 'sirTargetStepHsOlpc',
                'ulBandwidth', 'ulFilterProfile', 'nbirAlgorithm', 'nbirFixedNotchPosition'
            ]
            
            # Iterar por cada carrier/sector
            for _, row in carrier_df.iterrows():
                sector_num = row.get('Sector', '')
                
                if not sector_num:
                    continue
                
                # Convertir sector a formato S.*X.*1
                cell_id = f"S.*{sector_num}.*1"
                
                # Generar comandos lset para parámetros simples
                for param in parametros_simples:
                    if param in row and pd.notna(row[param]):
                        valor = row[param]
                        
                        # Formatear el valor según el tipo
                        if isinstance(valor, bool):
                            valor_str = str(valor).lower()
                        elif isinstance(valor, (int, float)):
                            if isinstance(valor, float) and valor.is_integer():
                                valor_str = str(int(valor))
                            else:
                                valor_str = str(valor)
                        elif isinstance(valor, str):
                            valor_str = valor if valor.strip() else ''
                        else:
                            valor_str = str(valor)
                        
                        mml_output.append(f"lset {cell_id} {param} {valor_str}")
                
                # Parámetro especial: eulOptimalNoiseFloorLock (combinación de dos columnas)
                col_lock = 'eulOptimalNoiseFloorLock_eulNoiseFloorLock'
                col_estimate = 'eulOptimalNoiseFloorLock_eulOptimalNoiseFloorEstimate'
                
                if col_lock in row and col_estimate in row:
                    lock_val = row[col_lock]
                    estimate_val = row[col_estimate]
                    
                    # Formatear valores
                    if pd.notna(lock_val):
                        if isinstance(lock_val, bool):
                            lock_str = str(lock_val).lower()
                        else:
                            lock_str = str(lock_val).lower()
                    else:
                        lock_str = "false"
                    
                    if pd.notna(estimate_val):
                        if isinstance(estimate_val, float) and estimate_val.is_integer():
                            estimate_str = str(int(estimate_val))
                        else:
                            estimate_str = str(estimate_val)
                    else:
                        estimate_str = "-1040"
                    
                    # Combinar en formato: eulNoiseFloorLock=false,eulOptimalNoiseFloorEstimate=-1040
                    combined_value = f"eulNoiseFloorLock={lock_str},eulOptimalNoiseFloorEstimate={estimate_str}"
                    mml_output.append(f"lset {cell_id} eulOptimalNoiseFloorLock {combined_value}")
                
                # Agregar salto de línea entre carriers
                mml_output.append("")
        else:
            mml_output.append("// WARNING: Hoja Carrier no encontrada en RND")
        
        mml_output.append("")
        
        # ==================================================================
        # SECCIÓN 4: NodeBFunction
        # ==================================================================
        mml_output.append("###################################################")
        mml_output.append("# NodeBFunction   ----> Hoja NodeBFunction        #")
        mml_output.append("###################################################")
        
        # Buscar la hoja con diferentes nombres posibles
        nbf_df = None
        if 'Nodebfunction' in rnd_data:
            nbf_df = rnd_data['Nodebfunction']
        elif 'NODEBFUNCTION' in rnd_data:
            nbf_df = rnd_data['NODEBFUNCTION']
        elif 'NodeBFunction' in rnd_data:
            nbf_df = rnd_data['NodeBFunction']
        
        if nbf_df is not None and not nbf_df.empty:
            # Tomar la primera fila (configuración global)
            row = nbf_df.iloc[0]
            
            # Lista de parámetros en el orden especificado
            parametros = [
                'analogUlAlignIsActive', 'dlLicFractBbPool', 'eul2msFirstSchedStep', 'eulDchMaxAllowedSchRate',
                'eulFachInitialRate', 'eulFachMinAllocation', 'eulInactivityHighRateTime', 'eulInactivityLowRateTime',
                'eulLowRate', 'eulLowUsageTime', 'eulMaxAllowedSchRate', 'eulMaxShoRate',
                'eulMaxTotalProtectedRate', 'eulNonServHwRate', 'eulNoReschUsers', 'eulSchedulingWeight',
                'eulTargetRate', 'featureState16Qam', 'featureState64Qam', 'featureStateAbsoluteTimeSynch',
                'featureStateCeCapEul', 'featureStateCeEfficiencyEul', 'featureStateCeExtForEul', 'featureStateCombinedCell',
                'featureStateDlPowerControlEul', 'featureStateDualStackIub', 'featureStateDualTmaSupport', 'featureStateEul2msTti',
                'featureStateEulForLargeRbsConfig', 'featureStateGrake', 'featureStateHsAqmCongCtrl', 'featureStateHsdpaFlexibleScheduler',
                'featureStateHsdpaImprovedLinkAdaptation', 'featureStateHsdpaMcInterDuSched', 'featureStateHsdpaMinBitRate', 'featureStateHsdpaRbrQosProfiling',
                'featureStateImprovedDAgc', 'featureStateIncreasedCellCarrierSupport', 'featureStateIncreasedHsCodeCap', 'featureStateIncrNumHsCodes',
                'featureStateInterferenceSuppression', 'featureStateIntSuppAllBearers', 'featureStateIntSuppEul10ms', 'featureStateMbmsIubEfficiency',
                'featureStateMixedMode', 'featureStatePerHarqProcessGrant', 'featureStatePsiCoverage', 'featureStateRbsMpLoadSharing',
                'featureStateRetCascading', 'featureStateStandardizedRet', 'featureStateStandardizedTma', 'featureStateUlFcc',
                'hsdpaMcInterDuSchedCapability', 'licenseCapacityChannelElementDl', 'licenseCapacityChannelElementUl', 'licenseCapacityRbsChannelElementsDownlink',
                'licenseCapacityRbsChannelElementsUplink', 'licenseStateCeCapEul', 'licenseStateCombinedCell', 'licenseStateEulMc',
                'licenseStateHsdpaPowerSharing', 'licenseStateHsOlpc', 'licenseStateIncreasedCellCarrierSupport', 'licenseStateNbir',
                'licenseStateRbsMpLoadSharing', 'toaeCch', 'toaeDch', 'ulLicFractBbPool',
                'featureStateUlCoMpReception', 'licenseStateUlCoMpReception', 'featureStateEulLowLatencyPresched', 'licenseStateEulLowLatencyPresched',
                'featureStateMultiSectorPerRadio', 'featureStateUlSpectrumAnalyzer', 'licenseStateHsAdaptiveBler', 'licenseStateHsdpaMixedModePowerSharing',
                'licenseStateMultiSectorPerRadio', 'licenseStateUlSpectrumAnalyzer', 'nonEqPwrCommonPrecoderState', 'nbapDscp'
            ]
            
            # Generar comandos Set para cada parámetro
            for param in parametros:
                if param in row:
                    valor = row[param]
                    
                    # Formatear el valor según el tipo
                    if pd.notna(valor):
                        if isinstance(valor, bool):
                            valor_str = str(int(valor))  # Convertir bool a 0/1
                        elif isinstance(valor, (int, float)):
                            if isinstance(valor, float) and valor.is_integer():
                                valor_str = str(int(valor))
                            else:
                                valor_str = str(valor)
                        elif isinstance(valor, str):
                            # Verificar si es un string que representa múltiples valores
                            valor_str = valor.strip()
                        else:
                            valor_str = str(valor)
                    else:
                        # Si es NaN/None, dejar vacío
                        valor_str = ''
                    
                    # Generar comando Set (con punto después de Set y espacio antes del parámetro)
                    mml_output.append(f"Set . {param} {valor_str}")
        else:
            mml_output.append("// WARNING: Hoja NodeBFunction no encontrada en RND")
        

        # ==================================================================
        # SECCIÓN 5: IubDataStreams & SiteConfiguration
        # ==================================================================
        mml_output.append("###################################################################")
        mml_output.append("# IubDataStreams ---> Hojas IubDataStreams y SiteConfiguration    #")
        mml_output.append("###################################################################")
        
        # Función auxiliar para buscar columnas sin distinguir mayúsculas/minúsculas
        def get_value_case_insensitive(row, col_name):
            # Normalizar nombres de columnas del row
            col_map = {c.lower(): c for c in row.index}
            actual_col = col_map.get(col_name.lower())
            if actual_col:
                return row[actual_col]
            return None

        # --- IubDataStreams ---
        iub_df = None
        if 'Iubdatastreams' in rnd_data:
            iub_df = rnd_data['Iubdatastreams']
        elif 'IUBDATASTREAMS' in rnd_data:
            iub_df = rnd_data['IUBDATASTREAMS']
        elif 'IubDataStreams' in rnd_data:
            iub_df = rnd_data['IubDataStreams']
            
        if iub_df is not None and not iub_df.empty:
            # Tomar la primera fila
            row = iub_df.iloc[0]
            
            # Parámetros Iub
            params_iub = [
                'hsDataFrameDelayThreshold', 'maxHSRate', 
                'schHsFlowControlOnOff', 'hsRbrDiscardProbability', 'hsRbrWeight'
            ]
            
            for param in params_iub:
                valor = get_value_case_insensitive(row, param)
                
                # Formatear valor
                if pd.notna(valor):
                    if isinstance(valor, bool):
                        valor_str = str(int(valor)) # 0/1 para bools en este contexto
                    elif isinstance(valor, (int, float)):
                        if isinstance(valor, float) and valor.is_integer():
                            valor_str = str(int(valor))
                        else:
                            valor_str = str(valor)
                    else:
                        valor_str = str(valor).strip()
                else:
                    valor_str = ''
                
                # Si el valor no está vacío, agregarlo
                if valor_str:
                    mml_output.append(f"lset Iub=. {param} {valor_str}")
        else:
             mml_output.append("// WARNING: Hoja IubDataStreams no encontrada en RND")

        mml_output.append("")

        # --- SiteConfiguration ---
        site_conf_df = None
        if 'Siteconfiguration' in rnd_data:
            site_conf_df = rnd_data['Siteconfiguration']
        elif 'SITECONFIGURATION' in rnd_data:
            site_conf_df = rnd_data['SITECONFIGURATION']
        elif 'SiteConfiguration' in rnd_data:
            site_conf_df = rnd_data['SiteConfiguration']
            
        if site_conf_df is not None and not site_conf_df.empty:
            row = site_conf_df.iloc[0]
            
            # logicalName -> Columna 'Site'
            val = get_value_case_insensitive(row, 'Site')
            if pd.notna(val):
                mml_output.append(f"set ManagedElement=1 logicalName {val}  // Site")
            
            # site -> Columna 'Name'
            val = get_value_case_insensitive(row, 'Name')
            if pd.notna(val):
                mml_output.append(f"set ManagedElement=1 site {val}   // Name")
                
            # userLabel -> Columna 'Site'
            val = get_value_case_insensitive(row, 'Site')
            if pd.notna(val):
                mml_output.append(f"set ManagedElement=1 userLabel {val}   //Site")
        else:
             mml_output.append("// WARNING: Hoja SiteConfiguration no encontrada en RND")
             
        mml_output.append("")

        # ==================================================================
        # SECCIÓN 6: TpaDevice AIR32
        # ==================================================================
        # Verificar si la antena es AIR32 desde SiteConfiguration
        is_air32 = False
        if site_conf_df is not None and not site_conf_df.empty:
            row_site = site_conf_df.iloc[0]
            antenna_val = get_value_case_insensitive(row_site, 'Antenna')
            if antenna_val and 'AIR32' in str(antenna_val).upper():
                is_air32 = True
        
        # Cargar hoja TpaDevice_RruDeviceGroup de forma robusta
        tpa_df = None
        # Buscar en las keys del diccionario alguna que contenga 'TPADEVICE' y 'RRUDEVICEGROUP'
        for key in rnd_data.keys():
            if 'TPADEVICE' in key.upper() and 'RRUDEVICEGROUP' in key.upper():
                tpa_df = rnd_data[key]
                break
            
        if is_air32 and tpa_df is not None and not tpa_df.empty:
            mml_output.append("###################################################")
            mml_output.append("# maxTotalOutputPower                             #")
            mml_output.append("###################################################")
            mml_output.append("acc sector unInitSector")
            mml_output.append("")
            mml_output.append("###################################################")
            mml_output.append("# TpaDevice  AIR32                                #")
            mml_output.append("###################################################")
            mml_output.append("###################################################")
            mml_output.append("# maxTotalOutputPower                             #")
            mml_output.append("###################################################")
            mml_output.append("acc sector unInitSector")
            mml_output.append("")
            
            for _, row in tpa_df.iterrows():
                tpa_device = get_value_case_insensitive(row, 'TpaDevice')
                max_pwr = get_value_case_insensitive(row, 'maxTotalOutputPower')
                max_pwr_low = get_value_case_insensitive(row, 'maxTotalOutputPowerLow')
                
                # AuxPlugInUnit dinámico
                aux_unit = get_value_case_insensitive(row, 'AuxPlugInUnit')
                if not aux_unit:
                    aux_unit = 'RRUW-1'
                
                if pd.notna(tpa_device):
                    # Convertir a int si es float
                    if isinstance(tpa_device, float) and tpa_device.is_integer():
                        tpa_device = int(tpa_device)
                        
                    if pd.notna(max_pwr):
                        if isinstance(max_pwr, float) and max_pwr.is_integer():
                            max_pwr_str = str(int(max_pwr))
                        else:
                            max_pwr_str = str(max_pwr)
                        mml_output.append(f"set Equipment=1,AuxPlugInUnit={aux_unit},.*TpaDevice={tpa_device} maxTotalOutputPower {max_pwr_str}")
                        
                    if pd.notna(max_pwr_low):
                        if isinstance(max_pwr_low, float) and max_pwr_low.is_integer():
                            max_pwr_low_str = str(int(max_pwr_low))
                        else:
                            max_pwr_low_str = str(max_pwr_low)
                        mml_output.append(f"set Equipment=1,AuxPlugInUnit={aux_unit},.*TpaDevice={tpa_device} maxTotalOutputPowerLow {max_pwr_low_str}")
            
            mml_output.append("")

        # ==================================================================
        # SECCIÓN 7: TpaDevice RRU
        # ==================================================================
        if tpa_df is not None and not tpa_df.empty:
            mml_output.append("###################################################")
            mml_output.append("# TpaDevice  RRU                                     #")
            mml_output.append("###################################################")
            
            for _, row in tpa_df.iterrows():
                sector_antenna = get_value_case_insensitive(row, 'SectorAntenna')
                tpa_device = get_value_case_insensitive(row, 'TpaDevice')
                max_pwr = get_value_case_insensitive(row, 'maxTotalOutputPower')
                
                # AuxPlugInUnit dinámico
                aux_unit = get_value_case_insensitive(row, 'AuxPlugInUnit')
                if not aux_unit:
                    aux_unit = 'RRUW-1'
                
                if pd.notna(sector_antenna) and pd.notna(tpa_device) and pd.notna(max_pwr):
                     # Formatear valores
                    if isinstance(tpa_device, float) and tpa_device.is_integer():
                        tpa_device = int(tpa_device)
                        
                    if isinstance(max_pwr, float) and max_pwr.is_integer():
                        max_pwr_str = str(int(max_pwr))
                    else:
                        max_pwr_str = str(max_pwr)
                        
                    mml_output.append("wait 1s")
                    mml_output.append(f"Set SectorAntenna={sector_antenna},AuxPlugInUnit={aux_unit},RruDeviceGroup=1,TpaDeviceSet=1,TpaDevice={tpa_device} maxTotalOutputPower {max_pwr_str}")
            
            mml_output.append("")
        
        # ==================================================================
        # SECCIÓN 8: AntennaBranch (Aditional)
        # ==================================================================
        # Cargar hoja AntennaBranch
        ant_branch_df = None
        if 'AntennaBranch' in rnd_data:
            ant_branch_df = rnd_data['AntennaBranch']
        elif 'ANTENNABRANCH' in rnd_data:
            ant_branch_df = rnd_data['ANTENNABRANCH']
            
        if ant_branch_df is not None and not ant_branch_df.empty:
            mml_output.append("###################################################")
            mml_output.append("# Aditional                                       #")
            mml_output.append("###################################################")
            mml_output.append("acc sector unInitSector")
            mml_output.append("wait 2s")
            mml_output.append("")
            
            for _, row in ant_branch_df.iterrows():
                sector_ant = get_value_case_insensitive(row, 'SectorAntenna')
                ant_branch = get_value_case_insensitive(row, 'AntennaBranch')
                ant_sup_th = get_value_case_insensitive(row, 'antennaSupervisionThreshold')
                low_curr_sup = get_value_case_insensitive(row, 'lowCurrentSupervision')
                mech_tilt = get_value_case_insensitive(row, 'mechanicalAntennaTilt')
                
                if pd.notna(sector_ant) and pd.notna(ant_branch):
                    # Formatear valores
                    if pd.notna(ant_sup_th):
                        if isinstance(ant_sup_th, float) and ant_sup_th.is_integer():
                            ant_sup_th = str(int(ant_sup_th))
                        mml_output.append(f"set SectorAntenna={sector_ant},AntennaBranch={ant_branch} antennaSupervisionThreshold {ant_sup_th}")
                        
                    if pd.notna(low_curr_sup):
                        if isinstance(low_curr_sup, float) and low_curr_sup.is_integer():
                            low_curr_sup = str(int(low_curr_sup))
                        mml_output.append(f"set SectorAntenna={sector_ant},AntennaBranch={ant_branch} lowCurrentSupervision {low_curr_sup}")
                        
                    if pd.notna(mech_tilt):
                        if isinstance(mech_tilt, float) and mech_tilt.is_integer():
                            mech_tilt = str(int(mech_tilt))
                        mml_output.append(f"set SectorAntenna={sector_ant},AntennaBranch={ant_branch} mechanicalAntennaTilt {mech_tilt}")
                    
                    mml_output.append("")
            
            mml_output.append("")
        
        # ==================================================================
        # SECCIÓN 9: Sector
        # ==================================================================
        # Cargar hoja Sector
        sector_df = None
        if 'Sector' in rnd_data:
            sector_df = rnd_data['Sector']
        elif 'SECTOR' in rnd_data:
            sector_df = rnd_data['SECTOR']
            
        if sector_df is not None and not sector_df.empty:
            mml_output.append("###################################################")
            mml_output.append("# SET Sector ----> Hoja Sector                    #")
            mml_output.append("###################################################")
            mml_output.append("")
            
            for _, row in sector_df.iterrows():
                sector_id = get_value_case_insensitive(row, 'Sector')
                beam_dir = get_value_case_insensitive(row, 'beamDirection')
                height = get_value_case_insensitive(row, 'height')
                lat = get_value_case_insensitive(row, 'latitude')
                lon = get_value_case_insensitive(row, 'longitude')
                
                if pd.notna(sector_id):
                    # Formatear sector_id
                    if isinstance(sector_id, float) and sector_id.is_integer():
                        sector_id = int(sector_id)
                        
                    if pd.notna(beam_dir):
                        if isinstance(beam_dir, float) and beam_dir.is_integer():
                            beam_dir = str(int(beam_dir))
                        mml_output.append(f"set Sector={sector_id} beamDirection {beam_dir}")
                        
                    if pd.notna(height):
                        if isinstance(height, float) and height.is_integer():
                            height = str(int(height))
                        mml_output.append(f"set Sector={sector_id} height {height}")
                        
                    if pd.notna(lat):
                        try:
                            lat = str(int(float(lat)))
                        except ValueError:
                            pass # Mantener valor original si falla conversión
                        mml_output.append(f"set Sector={sector_id} latitude {lat}")
                        
                    if pd.notna(lon):
                        try:
                            lon = str(int(float(lon)))
                        except ValueError:
                            pass # Mantener valor original si falla conversión
                        mml_output.append(f"set Sector={sector_id} longitude {lon}")
                    
                    mml_output.append("")
            
            mml_output.append("")

        # ==================================================================
        # SECCIÓN 10: TxDeviceGroup
        # ==================================================================
        # Cargar hoja TxDeviceGroup de forma robusta
        tx_dev_df = None
        # Buscar key que contenga 'TXDEVICEGROUP'
        for key in rnd_data.keys():
            if 'TXDEVICEGROUP' in key.upper():
                tx_dev_df = rnd_data[key]
                break
            
        if tx_dev_df is not None and not tx_dev_df.empty:
            mml_output.append("###################################################")
            mml_output.append("# SET TxDeviceGroup ----> Hoja TxDeviceGroup      #")
            mml_output.append("###################################################")
            mml_output.append("")
            
            for _, row in tx_dev_df.iterrows():
                # Leer columnas disponibles
                subrack = get_value_case_insensitive(row, 'Subrack')
                slot = get_value_case_insensitive(row, 'Slot')
                plugin = get_value_case_insensitive(row, 'PlugInUnit')
                piu_dev = get_value_case_insensitive(row, 'PiuDevice')
                tx_dev = get_value_case_insensitive(row, 'TxDeviceGroup')
                num_hs = get_value_case_insensitive(row, 'numHsCodeResources')
                num_eul = get_value_case_insensitive(row, 'numEulResources')
                
                # Valores por defecto si no existen en la hoja
                if not subrack: subrack = '1'
                if not slot: slot = '1'
                if not plugin: plugin = '1'
                if not piu_dev: piu_dev = '2'
                if not tx_dev: tx_dev = '1'
                
                # Formatear valores enteros
                vals = [subrack, slot, plugin, piu_dev, tx_dev, num_hs, num_eul]
                formatted_vals = []
                for v in vals:
                    if pd.notna(v) and isinstance(v, float) and v.is_integer():
                        formatted_vals.append(str(int(v)))
                    else:
                        formatted_vals.append(str(v) if pd.notna(v) else "")
                
                s_sub, s_slot, s_plug, s_piu, s_tx, s_hs, s_eul = formatted_vals
                
                # Generar comandos si hay valores de recursos
                if s_hs:
                    mml_output.append(f"set Subrack={s_sub},Slot={s_slot},PlugInUnit={s_plug},PiuDevice={s_piu},TxDeviceGroup={s_tx} numHsCodeResources {s_hs}")
                if s_eul:
                    mml_output.append(f"set Subrack={s_sub},Slot={s_slot},PlugInUnit={s_plug},PiuDevice={s_piu},TxDeviceGroup={s_tx} numEulResources {s_eul}")
            
            mml_output.append("")

        # ==================================================================
        # SECCIÓN 11: NtpServer
        # ==================================================================
        mml_output.append("###################################################")
        mml_output.append("# SET NtpServer ----> Valor estatico              #")
        mml_output.append("###################################################")
        mml_output.append("")
        mml_output.append("crn SystemFunctions=1,TimeSetting=1,NtpServer=2")
        mml_output.append("serverAddress 172.16.50.42")
        mml_output.append("serviceActive true")
        mml_output.append("userLabel NTP2")
        mml_output.append("end")
        mml_output.append("")
        mml_output.append("crn SystemFunctions=1,TimeSetting=1,NtpServer=1")
        mml_output.append("serverAddress 172.16.50.41")
        mml_output.append("serviceActive true")
        mml_output.append("userLabel NTP1")
        mml_output.append("end")
        mml_output.append("")

        # ==================================================================
        # SECCIÓN 12: Other
        # ==================================================================
        # Usamos IubDataStreams (ya cargado como iub_ds_df) y Iub (ya cargado como iub_df)
        # Pero necesitamos rbsid de Iub y maxHSRate de IubDataStreams
        
        # Recargar Iub si es necesario (ya debería estar en iub_df al inicio, pero por seguridad)
        iub_df_local = None
        if 'Iub' in rnd_data:
            iub_df_local = rnd_data['Iub']
        elif 'IUB' in rnd_data:
            iub_df_local = rnd_data['IUB']
            
        # Recargar IubDataStreams si es necesario
        iub_ds_df_local = None
        if 'IubDataStreams' in rnd_data:
            iub_ds_df_local = rnd_data['IubDataStreams']
        elif 'IUBDATASTREAMS' in rnd_data:
            iub_ds_df_local = rnd_data['IUBDATASTREAMS']
            
        mml_output.append("###################################################")
        mml_output.append("# SET Other ----> Hoja iub y IubDataStreams       #")
        mml_output.append("###################################################")
        mml_output.append("")
        
        # rbsid desde Iub
        if iub_df_local is not None and not iub_df_local.empty:
            rbsid_val = get_value_case_insensitive(iub_df_local.iloc[0], 'rbsId')
            if pd.notna(rbsid_val):
                if isinstance(rbsid_val, float) and rbsid_val.is_integer():
                    rbsid_val = str(int(rbsid_val))
                mml_output.append(f"set . rbsid {rbsid_val}")
                
        # maxhsrate desde IubDataStreams
        if iub_ds_df_local is not None and not iub_ds_df_local.empty:
            max_hs_val = get_value_case_insensitive(iub_ds_df_local.iloc[0], 'maxHSRate')
            if pd.notna(max_hs_val):
                if isinstance(max_hs_val, float) and max_hs_val.is_integer():
                    max_hs_val = str(int(max_hs_val))
                mml_output.append(f"set . maxhsrate {max_hs_val}")
        
        mml_output.append("")

        # ==================================================================
        # SECCIÓN 13: AntFeederCable
        # ==================================================================
        # Cargar hoja AntFeederCable
        ant_feed_df = None
        if 'AntFeederCable' in rnd_data:
            ant_feed_df = rnd_data['AntFeederCable']
        elif 'ANTFEEDERCABLE' in rnd_data:
            ant_feed_df = rnd_data['ANTFEEDERCABLE']
            
        if ant_feed_df is not None and not ant_feed_df.empty:
            mml_output.append("###################################################")
            mml_output.append("# SET AntFeederCable ----> Hoja AntFeederCable    #")
            mml_output.append("###################################################")
            mml_output.append("acc sector unInitSector")
            mml_output.append("wait 2s")
            
            for _, row in ant_feed_df.iterrows():
                ant_cable = get_value_case_insensitive(row, 'AntFeederCable')
                dl_att = get_value_case_insensitive(row, 'dlAttenuation')
                elec_dl = get_value_case_insensitive(row, 'electricalDlDelay')
                elec_ul = get_value_case_insensitive(row, 'electricalUlDelay')
                ul_att = get_value_case_insensitive(row, 'ulAttenuation')
                
                if pd.notna(ant_cable):
                    mml_output.append(f"rset AntFeederCable={ant_cable} dlAttenuation {dl_att}")
                    mml_output.append(f"rset AntFeederCable={ant_cable} electricalDlDelay {elec_dl}")
                    mml_output.append(f"rset AntFeederCable={ant_cable} electricalUlDelay {elec_ul}")
                    mml_output.append(f"rset AntFeederCable={ant_cable} ulAttenuation {ul_att}")
                    mml_output.append("")
            
            mml_output.append("")

        # ==================================================================
        # SECCIÓN 14: Other Sector
        # ==================================================================
        # Cargar hoja SectorAntenna
        sec_ant_df = None
        if 'SectorAntenna' in rnd_data:
            sec_ant_df = rnd_data['SectorAntenna']
        elif 'SECTORANTENNA' in rnd_data:
            sec_ant_df = rnd_data['SECTORANTENNA']
            
        # Reutilizar hoja Sector (ya cargada como sector_df en SECCIÓN 9)
        # Si no está cargada, intentamos cargarla de nuevo
        if 'sector_df' not in locals() or sector_df is None:
            if 'Sector' in rnd_data:
                sector_df = rnd_data['Sector']
            elif 'SECTOR' in rnd_data:
                sector_df = rnd_data['SECTOR']

        if (sec_ant_df is not None and not sec_ant_df.empty) or (sector_df is not None and not sector_df.empty):
            mml_output.append("#########################################################")
            mml_output.append("# SET Other Sector ----> Hoja SectorAntenna y Sector    #")
            mml_output.append("#########################################################")
            mml_output.append("")
            
            # Parte 1: SectorAntenna
            if sec_ant_df is not None and not sec_ant_df.empty:
                for _, row in sec_ant_df.iterrows():
                    sa_id = get_value_case_insensitive(row, 'SectorAntenna')
                    ant_type = get_value_case_insensitive(row, 'antennaType')
                    
                    if pd.notna(sa_id) and pd.notna(ant_type):
                        if isinstance(ant_type, float) and ant_type.is_integer():
                            ant_type = str(int(ant_type))
                        
                        mml_output.append(f"get sectorAntenna={sa_id} antennatype > $AntSite")
                        mml_output.append(f"if $AntSite != {ant_type}")
                        mml_output.append(f"set SectorAntenna={sa_id} antennaType {ant_type}")
                        mml_output.append("fi")
                        mml_output.append("")
            
            # Parte 2: Sector (InitSector)
            if sector_df is not None and not sector_df.empty:
                for _, row in sector_df.iterrows():
                    sector_id = get_value_case_insensitive(row, 'Sector')
                    tx_branches = get_value_case_insensitive(row, 'numberOfTxBranches')
                    band_val = get_value_case_insensitive(row, 'band')
                    
                    if pd.notna(sector_id):
                        if isinstance(sector_id, float) and sector_id.is_integer():
                            sector_id = int(sector_id)
                            
                        # Mapeo de banda
                        band_id = band_val
                        if pd.notna(band_val):
                            s_band = str(band_val).strip()
                            if s_band == '1900':
                                band_id = '2'
                            elif s_band == '900':
                                band_id = '8'
                            elif s_band == '850':
                                band_id = '5' # Asumiendo 5 para 850, ajustar si es necesario
                            elif s_band == '2100':
                                band_id = '1'
                            # Si ya es un número (ej: 2, 8), se mantiene
                            elif isinstance(band_val, float) and band_val.is_integer():
                                band_id = str(int(band_val))
                        
                        if pd.notna(tx_branches):
                            if isinstance(tx_branches, float) and tx_branches.is_integer():
                                tx_branches = str(int(tx_branches))
                                
                        if pd.notna(tx_branches) and pd.notna(band_id):
                            mml_output.append(f"accn Sector={sector_id} InitSector {tx_branches} {band_id}")
            
            mml_output.append("")
            mml_output.append("wait 2s")
            mml_output.append("")

        # ==================================================================
        # SECCIÓN 15: Set dscp
        # ==================================================================
        # Cargar hojas Ip, IpAccessHostEt, RncFunction
        # Cargar hojas Ip, IpAccessHostEt, RncFunction de forma robusta
        ip_df = None
        ip_acc_df = None
        rnc_func_df = None
        
        # Buscar keys
        for key in rnd_data.keys():
            k_upper = key.upper()
            if 'IP' == k_upper or 'IP ' in k_upper: # Exact match or with space
                 # Cuidado con IPACCESSHOSTE que contiene IP
                 if 'IPACCESS' not in k_upper:
                     ip_df = rnd_data[key]
            
            if 'IPACCESS' in k_upper:
                ip_acc_df = rnd_data[key]
                
            if 'RNCFUNCTION' in k_upper or 'NODEBFUNCTION' in k_upper:
                rnc_func_df = rnd_data[key]

        # DEBUG
        print(f"DEBUG: Keys available: {list(rnd_data.keys())}")
        if ip_acc_df is not None:
            print(f"DEBUG: IpAccessHostEt columns: {ip_acc_df.columns.tolist()}")
        else:
            print("DEBUG: IpAccessHostEt NOT FOUND - Using Dummy Fallback")
            # Crear dummy DF para forzar la generación con default
            ip_acc_df = pd.DataFrame({'dummy': [1]})

        mml_output.append("#############################################################")
        mml_output.append("# Set dscp   ----> Hojas Ip - IpAccessHostEt - RncFunction ##")
        mml_output.append("#############################################################")
        mml_output.append("")
        
        # 1. Ip
        if ip_df is not None and not ip_df.empty:
            dscp_val = get_value_case_insensitive(ip_df.iloc[0], 'dscp')
            if pd.notna(dscp_val):
                if isinstance(dscp_val, float) and dscp_val.is_integer():
                    dscp_val = str(int(dscp_val))
                mml_output.append(f"set Ip=1 dscp {dscp_val}")
        
        # 2. IpAccessHostEt
        if ip_acc_df is not None and not ip_acc_df.empty:
            # Intentar leer ntpDscp, luego dscp, sino default 46
            ntp_dscp = get_value_case_insensitive(ip_acc_df.iloc[0], 'ntpDscp')
            if pd.isna(ntp_dscp):
                ntp_dscp = get_value_case_insensitive(ip_acc_df.iloc[0], 'dscp')
            
            # Valor por defecto si no se encuentra
            if pd.isna(ntp_dscp):
                ntp_dscp = '46'
                
            if pd.notna(ntp_dscp):
                if isinstance(ntp_dscp, float) and ntp_dscp.is_integer():
                    ntp_dscp = str(int(ntp_dscp))
                mml_output.append(f"set IpAccessHostEt=1 ntpDscp {ntp_dscp}")
                
        # 3. NodeBFunction (nbapDscp)
        if rnc_func_df is not None and not rnc_func_df.empty:
            nbap_dscp = get_value_case_insensitive(rnc_func_df.iloc[0], 'nbapDscp')
            if pd.notna(nbap_dscp):
                if isinstance(nbap_dscp, float) and nbap_dscp.is_integer():
                    nbap_dscp = str(int(nbap_dscp))
                mml_output.append(f"set NodeBFunction=1 nbapDscp {nbap_dscp}")
        
        mml_output.append("")
        mml_output.append("deb IpSystem=1,IpAccessHostEt=1")
        mml_output.append("")

        # ==================================================================
        # SECCIÓN 16: GigaBitEthernet
        # ==================================================================
        # Cargar hoja GigaBitEthernet de forma robusta
        gbe_df = None
        for key in rnd_data.keys():
            if 'GIGABITETHERNET' in key.upper():
                gbe_df = rnd_data[key]
                break
        
        if gbe_df is not None and not gbe_df.empty:
            mml_output.append("#############################################################")
            mml_output.append("# Set GigaBitEthernet   ----> Hoja GigaBitEthernet         ##")
            mml_output.append("#############################################################")
            mml_output.append("")
            
            dscp_map_str = get_value_case_insensitive(gbe_df.iloc[0], 'dscpPbitMap')
            
            if pd.notna(dscp_map_str):
                # Limpiar y dividir por espacios
                # Convertir a string primero por si acaso es interpretado como otro tipo
                dscp_map_str = str(dscp_map_str).strip()
                # Reemplazar múltiples espacios por uno solo
                import re
                dscp_map_str = re.sub(r'\s+', ' ', dscp_map_str)
                values = dscp_map_str.split(' ')
                
                for idx, val in enumerate(values):
                    if val: # Asegurar que no sea string vacío
                        mml_output.append("acc Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1   setDscpPbit")
                        mml_output.append(f"{idx}")
                        mml_output.append(f"{val}")
                        mml_output.append("")

                        mml_output.append(f"{val}")
                        mml_output.append("")

        # ==================================================================
        # SECCIÓN 17: Final Static
        # ==================================================================
        mml_output.append("#############################################################")
        mml_output.append("#            FIN de SCRIPT de PARAMETROS                   ##")
        mml_output.append("#############################################################")
        mml_output.append("")
        mml_output.append("bl IpSyncRef")
        mml_output.append("acc Synchronization removeSyncRefResource")
        mml_output.append("IpSystem=1,IpAccessHostEt=1,IpSyncRef=7")
        mml_output.append("acc Synchronization removeSyncRefResource")
        mml_output.append("IpSystem=1,IpAccessHostEt=1,IpSyncRef=8")
        mml_output.append("")
        mml_output.append("set Synchronization telecomStandard 0")
        mml_output.append("set Synchronization selectionProcessMode 1")
        mml_output.append("")
        mml_output.append("acc Synchronization addSyncRefResourceQl")
        mml_output.append("Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1")
        mml_output.append("1")
        mml_output.append("1")
        mml_output.append("1")
        mml_output.append("")
        mml_output.append("set . featureStateSyncEth 1")
        mml_output.append("")
        mml_output.append("")
        mml_output.append("confb-")
        mml_output.append("gs-")
        mml_output.append("")
        mml_output.append(f"cvms {nemonico}_PL_parametros")
        mml_output.append(f"cv rbset {nemonico}_PL_parametros")
        mml_output.append("rbs")
        mml_output.append("")

        # Convertir lista a string
        txt_content = "\n".join(mml_output)
        
        filename = f"02_{nemonico}_parametros.txt"
        
        return True, txt_content, filename
        
    except Exception as e:
        error_msg = f"Error generating parametros TXT: {str(e)}"
        print(f"ERROR: {error_msg}")
        return False, "", ""
