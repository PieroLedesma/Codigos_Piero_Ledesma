# ===========================================================================
# Autor: PIERO LEDESMA
# Fecha: 23/12/2025
# Proyecto: Generador Site Equipment XML - VERSIÓN RESTAURADA COMPLETA
# ===========================================================================

import os
import re
import traceback
from datetime import datetime
from typing import Tuple, Dict, Any

def generar_site_equipment_auto(nemonico: str, wsh_data: Dict[str, Any], rnd_data: Dict[str, Any]) -> Tuple[bool, str, str]:
    filename = f"00_site_equipment_{nemonico}.xml"

    try:
        # --- HELPERS ---
        def clean_key(text):
            return str(text).upper().replace(' ','').replace('_','').replace('-','').strip()

        def find_sheet(names):
            for name in names:
                target = clean_key(name)
                key = next((k for k in rnd_data.keys() if clean_key(k) == target), None)
                if key: return rnd_data[key]
            return None

        def find_col(df, aliases):
            if df is None: return None
            cols_map = {clean_key(c): c for c in df.columns}
            for alias in aliases:
                target = clean_key(alias)
                if target in cols_map: return cols_map[target]
            return None

        def safe_str(val, default="0"):
            if val is None or str(val).lower() in ('nan', 'none', ''): return default
            try:
                # Evita el .0 en números
                f_val = float(str(val).replace(',', '.'))
                return str(int(f_val))
            except:
                return str(val).strip()

        def format_coord_with_sign(val):
            if val is None or str(val).lower() in ('nan', ''): return "0"
            s_val = str(val).replace(',', '.')
            return s_val.split('.')[0].strip()

        # --- 1. CARGA DE HOJAS ---
        df_sector = find_sheet(['Sector', 'Sectors'])
        df_carrier = find_sheet(['Carrier', 'Carriers'])
        df_ret_prof = find_sheet(['RetProfile'])
        df_sec_ant = find_sheet(['SectorAntenna'])
        df_tx_dev = find_sheet(['TxDeviceGroup', 'TX_DEVICE_GROUP'])
        df_site_cfg = find_sheet(['SiteConfiguration'])
        df_ant_feeder = find_sheet(['AntFeederCable', 'ANTFEEDERCABLE'])

        if df_sector is None: return False, "Error: Hoja Sector no encontrada", filename

        # --- 2. siteName DINÁMICO (SiteConfiguration) ---
        site_name_val = nemonico
        if df_site_cfg is not None:
            c_site_cfg_site = find_col(df_site_cfg, ['SITE'])
            c_name = find_col(df_site_cfg, ['NAME'])
            if c_site_cfg_site and c_name:
                row_cfg = df_site_cfg[df_site_cfg[c_site_cfg_site].astype(str).str.strip().str.upper() == nemonico.upper()]
                if not row_cfg.empty:
                    site_name_val = str(row_cfg.iloc[0].get(c_name, nemonico)).strip()

        c_site_main = find_col(df_sector, ['SITE'])
        df_rows_sector = df_sector[df_sector[c_site_main].astype(str).str.strip().str.upper() == nemonico.upper()].copy()
        if df_rows_sector.empty: return False, f"No hay datos para {nemonico}", filename

        # --- 3. RET, HSDPA & ALARMAS ---
        rets_xml = []
        type_of_ret_val = "NONE"
        if df_ret_prof is not None:
            c_site_ret = find_col(df_ret_prof, ['SITE'])
            df_ret_rows = df_ret_prof[df_ret_prof[c_site_ret].astype(str).str.strip().str.upper() == nemonico.upper()]
            c_t_retu = find_col(df_ret_prof, ['TypeOfRetu'])
            if not df_ret_rows.empty and c_t_retu:
                type_of_ret_val = str(df_ret_rows.iloc[0].get(c_t_retu, "NONE")).strip()
            
            for _, r in df_ret_rows.iterrows():
                rets_xml.append(f'<RetProfile antennaType="{safe_str(r.get("antennaType"))}" retType="{safe_str(r.get("retType", "1"))}" minTilt="{safe_str(r.get("minTilt"))}" maxTilt="{safe_str(r.get("maxTilt"))}" retParam1="0" retParam2="0" retParam3="0" retParam4="0" retParam5="0" retParam6="0" retParam7="0" retParam8="0" checkSum="{safe_str(r.get("checkSum"))}"/>')

        hsdpa_xml, eul_xml = [], []
        if df_tx_dev is not None:
            c_site_tx = find_col(df_tx_dev, ['SITE'])
            df_tx_rows = df_tx_dev[df_tx_dev[c_site_tx].astype(str).str.strip().str.upper() == nemonico.upper()]
            for _, r in df_tx_rows.iterrows():
                slot_v = safe_str(r.get('slot'), "1")
                hs_res = safe_str(r.get('numHsCodeResources'))
                eul_res = safe_str(r.get('numEulResources'))
                hsdpa_xml.append(f'    <HsdpaSlot slot="{slot_v}" numHsCodeResources="{hs_res}"/>')
                eul_xml.append(f'    <EulSlot slot="{slot_v}" numEulResources="{eul_res}"/>')

        alarms_xml = [f'    <Alarm externalAlarmUnit="Sup" portId="{p}" alarmSlogan="" normallyOpen="YES" severity="Minor" probableCause="550"/>' for p in range(1, 9)]

        # --- 4. PROCESAMIENTO SECTORES (Jerarquía y Tabulaciones Fix) ---
        sectors_xml, caps_xml, tma_xml, ant_xml, init_xml, cells_xml = [], [], [], [], [], []
        pos_ant_xml, pos_radio_xml = [], []
        
        for i, (_, row) in enumerate(df_rows_sector.iterrows(), 1):
            s_num = str(i)
            lat_v = format_coord_with_sign(row.get(find_col(df_sector, ['LATITUDE'])))
            lon_v = format_coord_with_sign(row.get(find_col(df_sector, ['LONGITUDE'])))
            beam_v = safe_str(row.get(find_col(df_sector, ['BEAMDIRECTION', 'ENDBEAMDIRECTION'])), "000").zfill(3)
            band_v = safe_str(row.get(find_col(df_sector, ['BAND'])))
            
            # Lógica RBB
            rv = int(float(str(row.get(find_col(df_sector, ['RADIOBUILDINGBLOCK']), 1)).replace(',','.')))
            tv_sec = int(float(str(row.get(find_col(df_sector, ['NUMBEROFTXBRANCHES']), 1)).replace(',','.')))
            rbb_map = {(40, 4): "RBB44_1A", (44, 4): "RBB44_1D", (20, 4): "RBB24_1A", (1, 1): "RBB12_1A"}
            r_final = rbb_map.get((rv, tv_sec), "RBB12_1A")
            cpri_v = "X4" if "RBB44" in r_final else "X2"

            # AntennaType Dinámico
            ant_type_val = "99"
            if df_sec_ant is not None:
                c_site_sa = find_col(df_sec_ant, ['SITE'])
                c_sec_sa = find_col(df_sec_ant, ['SECTORANTENNA'])
                m_sa = df_sec_ant[(df_sec_ant[c_site_sa].astype(str).str.strip().str.upper() == nemonico.upper()) & 
                                  (df_sec_ant[c_sec_sa].astype(str).str.strip() == f"{s_num}-1")]
                if not m_sa.empty:
                    ant_type_val = safe_str(m_sa.iloc[0].get('antennaType', '99'))

            def finalize_16(def_val):
                parts = [str(def_val)] * 12 + ["-1"] * 4
                return ", ".join(parts)

            def format_ericsson_list(raw_val, def_val):
                if raw_val is None or str(raw_val).lower() in ('nan', 'none', ''):
                    return finalize_16(def_val)
                parts = str(raw_val).strip().replace(',', ' ').split()
                while len(parts) < 16:
                    parts.append("-1")
                return ", ".join(parts[:16])

            def get_feeder_data(sector_num, branch_letter):
                if df_ant_feeder is None: return None
                target = f"{sector_num}{branch_letter}"
                c_site = find_col(df_ant_feeder, ['SITE'])
                c_cable = find_col(df_ant_feeder, ['ANTFEEDERCABLE'])
                if not c_site or not c_cable: return None
                row_f = df_ant_feeder[(df_ant_feeder[c_site].astype(str).str.strip().str.upper() == nemonico.upper()) & 
                                      (df_ant_feeder[c_cable].astype(str).str.strip().str.upper() == target.upper())]
                return row_f.iloc[0] if not row_f.empty else None

            def get_branch_xml_attrs(branch_letter, default_att, default_delay):
                row_f = get_feeder_data(s_num, branch_letter)
                if row_f is not None:
                    dl_att = format_ericsson_list(row_f.get('dlAttenuation'), default_att)
                    ul_att = format_ericsson_list(row_f.get('ulAttenuation'), default_att)
                    dl_del = format_ericsson_list(row_f.get('electricalDlDelay'), default_delay)
                    ul_del = format_ericsson_list(row_f.get('electricalUlDelay'), default_delay)
                else:
                    dl_att = finalize_16(default_att)
                    ul_att = finalize_16(default_att)
                    dl_del = str(default_delay)
                    ul_del = str(default_delay)
                return (f'dlFeederAttenuationBranch{branch_letter}="{dl_att}" '
                        f'ulFeederAttenuationBranch{branch_letter}="{ul_att}" '
                        f'dlFeederDelayBranch{branch_letter}="{dl_del}" '
                        f'ulFeederDelayBranch{branch_letter}="{ul_del}"')

            # Valores por defecto basados en RBB
            def_att = "5" if rv >= 20 else "20"
            def_delay = "15"

            branch_a_attrs = get_branch_xml_attrs("A", def_att, def_delay)
            branch_b_attrs = get_branch_xml_attrs("B", def_att, def_delay)
            
            # Opcionales C y D si existen en RND
            branch_c_attrs = ""
            if get_feeder_data(s_num, "C") is not None:
                branch_c_attrs = " " + get_branch_xml_attrs("C", def_att, def_delay)
            
            branch_d_attrs = ""
            if get_feeder_data(s_num, "D") is not None:
                branch_d_attrs = " " + get_branch_xml_attrs("D", def_att, def_delay)

            # LocalCell
            if df_carrier is not None:
                c_site_car = find_col(df_carrier, ['SITE'])
                c_sec_car = find_col(df_carrier, ['SECTOR'])
                df_site_car = df_carrier[df_carrier[c_site_car].astype(str).str.strip().str.upper() == nemonico.upper()]
                row_car = df_site_car[df_site_car[c_sec_car].astype(str).str.strip() == s_num]
                if not row_car.empty:
                    rc = row_car.iloc[0]
                    c_id = "".join(filter(str.isdigit, str(rc.get(find_col(df_carrier, ['UTRANCELL']), ''))))
                    c_range = safe_str(rc.get(find_col(df_carrier, ['CELLRANGE']), '35000'))
                    tx_b = safe_str(rc.get(find_col(df_carrier, ['NUMBEROFTXBRANCHES']), '1'))
                    rx_b = safe_str(rc.get(find_col(df_carrier, ['NUMBEROFRXBRANCHES']), '2'))
                    cells_xml.append(f'        <Sector sectorNumber="{s_num}">\n            <Cell cellNumber="1" cellCreated="YES" cellIdentity="{c_id}" cellRange="{c_range}" baseBandPoolId="1" numberOfTxBranches="{tx_b}" numberOfRxBranches="{rx_b}" operatingBand="{band_v}"/>\n        </Sector>')

            sectors_xml.append(f'    <SectorData sectorNumber="{s_num}" latitude="{lat_v}" latHemisphere="SOUTH" longitude="{lon_v}" geoDatum="WGS84" beamDirection="{beam_v}" height="1500" noiseFigure="-1" sectorGroup="-1" mixedModeRadio="FALSE">\n        <RadioUnit radioUnitNumber="1" isSharedWithExternalMe="FALSE"/>\n    </SectorData>')
            caps_xml.append(f'    <SectorCapability sectorNumber="{s_num}" cpriLineRate="{cpri_v}" radioBuildingBlock="{r_final}" primaryPortId="BU1_{chr(65+(i-1)%26)}" sectorSequenceNumber="1" auUnitType="RRUWRRUS"/>')
            
            tma_xml.append(f'        <TmaSector sectorNumber="{s_num}" tmaType="NONE" typeOfRet="{type_of_ret_val}" riuInstalled="NO" currentLowSupervision_C="ON" currentLowSupervision_D="ON"/>')
            
            f_high = "19400" if rv >= 20 else "9571"
            f_low = "19300" if rv >= 20 else "9471"
            ant_xml.append(f'        <AntennaSector sectorNumber="{s_num}" antennaType="{ant_type_val}" mechanicalTilt="0" fqBandHighEdgeBranchA="{f_high}" fqBandLowEdgeBranchA="{f_low}" {branch_a_attrs} {branch_b_attrs}{branch_c_attrs}{branch_d_attrs} sectorOutputPower="40" beamDirection="{beam_v}" beamDirection2="000" beamDirection3="000"/>')
            
            init_xml.append(f'        <InitiatedSector sectorNumber="{s_num}" antennaSupervisionBranchA="0" antennaSupervisionBranchB="0" antennaSupervisionBranchC="0" antennaSupervisionBranchD="0" antennaSupervisionBranchE="0" antennaSupervisionBranchF="0"/>')
            
            pos_ant_xml.append(f'<PositionConfiguration sectorNumber="{s_num}" unitType="Antenna" unitNumber="1" positionInformation=""/>')
            pos_radio_xml.append(f'<PositionConfiguration sectorNumber="{s_num}" unitType="RadioUnit" unitNumber="1" positionInformation=""/>')

        # --- 5. ENSAMBLAJE FINAL ---
        nl = "\n"
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Site Equipment Configuration -->
<!-- Created {timestamp} -->
<!-- Created by Piero Ledesma -->
<Site>
<Format revision="BK1"/>
<TimingUnitConfig gpsOutEnabled="FALSE"/>
<OptionalEquipmentConfiguration cabinetNumber="1" noOfPdu="2" configureSau="NO" configureClimate="YES" configurePowerSupply="NO" configureBatteryBackup="NO" smokeDetector="FALSE" fanSpeedSupervision="0"> </OptionalEquipmentConfiguration>
<SiteLocationConfiguration siteName="{site_name_val}" logicalName="{nemonico}" lmtPorts="UNLOCKED">
{nl.join(sectors_xml)}
</SiteLocationConfiguration>
<SectorCapabilitySettings>
{nl.join(caps_xml)}
</SectorCapabilitySettings>
<SectorEquipmentConfiguration>
    <TmaConfiguration>
{nl.join(tma_xml)}
    </TmaConfiguration>
    <AntennaConfiguration>
{nl.join(ant_xml)}
    </AntennaConfiguration>
{f"    <RetConfiguration>{nl}{nl.join(['        '+r for r in rets_xml])}{nl}    </RetConfiguration>" if rets_xml else ""}
    <InitiateSectorsConfiguration>
{nl.join(init_xml)}
    </InitiateSectorsConfiguration>
    <LocalCellConfiguration carrierAllocationMode="Flexible">
{nl.join(cells_xml)}
    </LocalCellConfiguration>
</SectorEquipmentConfiguration>
<HsdpaSettings steeredHsAllocation="FALSE">
{nl.join(hsdpa_xml)}
</HsdpaSettings>
<EulSettings>
{nl.join(eul_xml)}
</EulSettings>
<ExternalAlarmConfiguration cabinetNumber="1">
{nl.join(alarms_xml)}
</ExternalAlarmConfiguration>
<Cabinet cabinetNumber="1" sharedCabinetIdentifier="" alarmInExternalMe="FALSE" equipmentSupportFunctionId="1">
    <ClimateSystem climateSystem="Standard"/>
    <ClimateRegulationSystem climateRegulationSystem="NotApplicable"/>
</Cabinet>
<SupportSystemControl supportSystemControl="TRUE"/>
<WantedPosition latitude="" longitude="" altitude="" tolerance="50"/>
{nl.join(pos_ant_xml)}
{nl.join(pos_radio_xml)}
</Site>"""
        return True, content, filename

    except Exception as e:
        return False, f"Error: {str(e)}", filename