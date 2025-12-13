"""
Generador de archivo IUB MO para modo 3G-DUW
Crea el archivo 01_{Nemonico}_iub.mo con configuración IUB
"""

from datetime import datetime
from typing import Dict, Any, Tuple


def generate_iub_duw_mo(
    nemonico: str,
    wsh_data: Dict[str, Any],
    rnd_data: Dict[str, Any]
) -> Tuple[bool, str, str]:
    """
    Genera el archivo .mo de configuración IUB para modo DUW.
    
    Args:
        nemonico: Némónico del sitio
        wsh_data: Datos extraídos del WSH (IPs, VLANs, máscaras, gateways)
        rnd_data: Datos del RND (rbsId, maxHsRate, etc.)
    
    Returns:
        Tuple (success, mo_content, filename)
    """
    try:
        # Fecha y hora actual
        now = datetime.now()
        fecha_str = now.strftime("%d-%m-%Y")
        hora_str = now.strftime("%H:%M:%S")
        
        # Extraer datos del WSH
        ip_iub = wsh_data.get('IP_TRAFICO', '0.0.0.0')  # IP de tráfico IUB
        dgw_iub = wsh_data.get('GATEWAY_TRAFICO', '0.0.0.0')  # Gateway de tráfico
        vlan_iub = wsh_data.get('VLAN_TRAFICO', '0')  # VLAN de tráfico
        mask_iub = wsh_data.get('MASK_TRAFICO', '0')  # Máscara CIDR de tráfico
        
        # Extraer RNC del RND si existe
        rnc_name = "UNKNOWN"
        if 'Iublink' in rnd_data and not rnd_data['Iublink'].empty:
            rnc_df = rnd_data['Iublink']
            if 'RNC' in rnc_df.columns:
                rnc_name = str(rnc_df['RNC'].iloc[0])
        
        # Extraer rbsId del RND (hoja Iub)
        rbs_id = "0"
        if 'Iub' in rnd_data and not rnd_data['Iub'].empty:
            iub_df = rnd_data['Iub']
            if 'rbsId' in iub_df.columns:
                rbs_id = str(iub_df['rbsId'].iloc[0])
        
        # Extraer maxHsRate del RND
        max_hs_rate = "825"  # Valor por defecto
        if 'IubDataStreams' in rnd_data and not rnd_data['IubDataStreams'].empty:
            iub_ds_df = rnd_data['IubDataStreams']
            if 'maxHsRate' in iub_ds_df.columns:
                max_hs_rate = str(iub_ds_df['maxHsRate'].iloc[0])
        
        # Identity del Iub
        iub_identity = f"Iub_{nemonico}"
        
        # Generar contenido del archivo MO
        mo_content = f"""///////////////////////////////////////////////////////////
//
// ARCHIVO     : 01_{nemonico}_iub.mo
// AUTOR       : Piero Ledesma
// FECHA       : {fecha_str}
// HORA        : {hora_str}
// NEMONICO    : {nemonico}
// RNC         : {rnc_name}
//
///////////////////////////////////////////////////////////

SET
(
   mo "ManagedElement=1,IpSystem=1,IpAccessHostEt=1"
   exception none
   administrativeState Integer 0
)
SET
(
   mo "ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef=8"
   exception none
   administrativeState Integer 0
)
SET
(
   mo "ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef=7"
   exception none
   administrativeState Integer 0
)
ACTION
(
   actionName removeSyncRefResource
   mo "ManagedElement=1,TransportNetwork=1,Synchronization=1"
   exception none
   nrOfParameters 1
      Ref "ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef=8"
   returnValue ignore
)
ACTION
(
   actionName removeSyncRefResource
   mo "ManagedElement=1,TransportNetwork=1,Synchronization=1"
   exception none
   nrOfParameters 1
      Ref "ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef=7"
   returnValue ignore
)
DELETE
(
   mo "ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef=8"
   exception none
)

DELETE
(
   mo "ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef=7"
   exception none
)

DELETE
(
   mo "ManagedElement=1,IpSystem=1,IpAccessHostEt=1"
   exception none
)

DELETE
(
   mo "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1,IpInterface=1"
   exception none
)
CREATE
(
   parent "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"
   identity "1"
   moType IpInterface
   exception none
   nrOfAttributes 18
   configurationMode Integer 0
   defaultRouter0 String "{dgw_iub}"
   defaultRouter1 String "0.0.0.0"
   defaultRouter2 String "0.0.0.0"
   defaultRouterPingInterval Integer 4
   dhcpClientIdentifier Struct
      nrOfElements 2
         clientIdentifier String "&"
         clientIdentifierType Integer 0
   logging Integer 0
   maxNoOfFailedPings Integer 2
   maxWaitForPingReply Integer 3
   mtu Integer 1500
   networkPrefixLength Integer {mask_iub}
   noOfPingsBeforeOk Integer 2
   ownIpAddressActive String "0.0.0.0"
   rps Boolean false
   switchBackTimer Integer 180
   trafficType Integer 0
   vLan Boolean true
   vid Integer {vlan_iub}
)
CREATE
(
   parent "ManagedElement=1,IpSystem=1"
   identity "1"
   moType IpAccessHostEt
   exception none
   nrOfAttributes 6
   administrativeState Integer 1
   ipAddress String "{ip_iub}"
   ipDefaultTtl Integer 64
   ipInterfaceMoRef Ref "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1,IpInterface=1"
   networkPrefixLength Integer 0
   ntpDscp Integer 46
)
CREATE
(
   parent "ManagedElement=1,IpSystem=1,IpAccessHostEt=1"
   identity "7"
   moType IpSyncRef
   exception none
   nrOfAttributes 2
   administrativeState Integer 0
   ntpServerIpAddress String "10.170.73.253"
)
CREATE
(
   parent "ManagedElement=1,IpSystem=1,IpAccessHostEt=1"
   identity "8"
   moType IpSyncRef
   exception none
   nrOfAttributes 2
   administrativeState Integer 0
   ntpServerIpAddress String "10.170.73.254"
)
ACTION
(
   actionName addSyncRefResource
   mo "ManagedElement=1,TransportNetwork=1,Synchronization=1"
   exception none
   nrOfParameters 2
      Ref "ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef=8"
      Integer "2"
   returnValue ignore
)

ACTION
(
   actionName addSyncRefResource
   mo "ManagedElement=1,TransportNetwork=1,Synchronization=1"
   exception none
   nrOfParameters 2
      Ref "ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef=7"
      Integer "1"
   returnValue ignore
)
ECHO "CREATE - ManagedElement=1,IpSystem=1,IpAccessSctp=Iub"
CREATE
(
parent "ManagedElement=1,IpSystem=1"
identity "Iub"
moType IpAccessSctp
exception none
nrOfAttributes 1
ipAccessHostEtRef1 Reference "ManagedElement=1,IpSystem=1,IpAccessHostEt=1"
)


// ------------- 3) Create Sctp MO
ECHO "------------- 3) Create Sctp MO"
CREATE
(
parent "ManagedElement=1,TransportNetwork=1"
identity 1
moType Sctp
exception none
nrOfAttributes 3
ipAccessSctpRef Reference "ManagedElement=1,IpSystem=1,IpAccessSctp=Iub"
numberOfAssociations Integer 2
rpuId Ref "ManagedElement=1,SwManagement=1,ReliableProgramUniter=sctp_host"
)

CREATE
(
parent "ManagedElement=1,NodeBFunction=1"
identity {iub_identity}
moType Iub
exception none
nrOfAttributes 5
rbsId  Integer {rbs_id}
userLabel String "{nemonico}"
userPlaneIpResourceRef Ref "ManagedElement=1,IpSystem=1,IpAccessHostEt=1"
controlPlaneTransportOption Struct
nrOfElements 2
atm Boolean false
ipV4 Boolean true
userPlaneTransportOption Struct
nrOfElements 2
atm Boolean false
ipV4 Boolean true
)


ECHO "NbapCommon (id 1)"
CREATE
(
parent "ManagedElement=1,NodeBFunction=1,Iub={iub_identity}"
identity 1
moType NbapCommon
exception none
nrOfAttributes 0
)

ECHO "NbapDedicated (id 1)"
CREATE
(
parent "ManagedElement=1,NodeBFunction=1,Iub={iub_identity}"
identity 1
moType NbapDedicated
exception none
nrOfAttributes 0
)

SET
(
mo "ManagedElement=1,NodeBFunction=1,Iub={iub_identity},IubDataStreams=1"
exception none
maxHsRate Integer {max_hs_rate}
)

SET
(
mo "ManagedElement=1,NodeBFunction=1"
exception none
userLabel String "RoRoc_Disabled"
)

SET
(
mo "ManagedElement=1,NodeBFunction=1"
exception none
nbapDscp Integer 40
)
SET
(
mo "ManagedElement=1,IpSystem=1,IpAccessHostEt=1"
exception none
ntpDscp Integer 46
)

///////////////////////
// Queue Q0 ( 0,22 )
///////////////////////
ACTION
(
actionName setDscpPbit
mo "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"
exception none
nrOfParameters 2
Integer "22"
Integer "1"
returnValue none
)
/////////////////////////
// Queue Q1 ( 16,18,20,26,28 )
/////////////////////////
ACTION
(
actionName setDscpPbit
mo "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"
exception none
nrOfParameters 2
Integer "16"
Integer "3"
returnValue none
)
ACTION
(
actionName setDscpPbit
mo "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"
exception none
nrOfParameters 2
Integer "18"
Integer "3"
returnValue none
)
ACTION
(
actionName setDscpPbit
mo "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"
exception none
nrOfParameters 2
Integer "20"
Integer "3"
returnValue none
)
ACTION
(
actionName setDscpPbit
mo "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"
exception none
nrOfParameters 2
Integer "26"
Integer "3"
returnValue none
)
ACTION
(
actionName setDscpPbit
mo "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"
exception none
nrOfParameters 2
Integer "28"
Integer "3"
returnValue none
)
/////////////////////////
// Queue Q2 ( 38 )
/////////////////////////
ACTION
(
actionName setDscpPbit
mo "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"
exception none
nrOfParameters 2
Integer "38"
Integer "4"
returnValue none
)
/////////////////////////
// Queue Q3 ( 40,42,44,46 )
/////////////////////////
ACTION
(
actionName setDscpPbit
mo "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"
exception none
nrOfParameters 2
Integer "40"
Integer "5"
returnValue none
)
ACTION
(
actionName setDscpPbit
mo "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"
exception none
nrOfParameters 2
Integer "42"
Integer "5"
returnValue none
)
ACTION
(
actionName setDscpPbit
mo "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"
exception none
nrOfParameters 2
Integer "44"
Integer "5"
returnValue none
)
ACTION
(
actionName setDscpPbit
mo "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"
exception none
nrOfParameters 2
Integer "46"
Integer "5"
returnValue none
)

SET
(
mo "ManagedElement=1,IpSystem=1,IpAccessHostEt=1"
   exception none
   administrativeState Integer 1
)

"""
        
        filename = f"01_{nemonico}_iub.mo"
        
        return True, mo_content, filename
        
    except Exception as e:
        error_msg = f"Error generating IUB MO: {str(e)}"
        print(f"ERROR: {error_msg}")
        return False, "", ""
