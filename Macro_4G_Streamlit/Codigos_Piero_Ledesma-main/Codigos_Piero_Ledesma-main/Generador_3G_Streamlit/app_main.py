# Contenido de app_main.py (VERSIÓN FINAL Y COMPLETA)

import streamlit as st
from utils.excel_parser import extraer_parametros, generar_script

# Configuración de página y Título general
st.set_page_config(layout="wide", page_title="Generador de Scripts 3G")

# ==============================================================================
# 0. PLANTILLAS DE CONFIGURACIÓN (Templates) - RECONSTRUIDAS DE VBA
# ==============================================================================

# NOTA: Estas plantillas asumen que excel_parser.py extrae:
# IUB, RBSID, MAXHSRATE, SYNC_1, SYNC_2, NEMONICO, IP_OAM, MASK, 
# IP_TRAFICO, VLAN_OAM, VLAN_IUB, DGW_Iub_IP_OAM, DGW_Iub_IP, PE_VALUE, IP_NTP_1, IP_NTP_2

# 1. DUW_ CAMBIO A OPTICO (3G Estándar)
TEMPLATE_DUW_OPTICO = """
ECHO "Script de Configuración DUW_ CAMBIO A OPTICO generado por Python"

ACTION (
actionName removeSyncRefResource
mo "ManagedElement=1,TransportNetwork=1,Synchronization=1"
exception none
nrOfParameters 1
Reference "ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef={SYNC_1}"
returnValue none
)

ACTION (
actionName removeSyncRefResource
mo "ManagedElement=1,TransportNetwork=1,Synchronization=1"
exception none
nrOfParameters 1
Reference "ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef={SYNC_2}"
returnValue none
)

DELETE (
mo "ManagedElement=1,NodeBFunction=1,Iub={IUB}" 'IUB
exception none
)

DELETE (
mo "ManagedElement=1,TransportNetwork=1,Sctp=1"
exception none
)

DELETE (
mo "ManagedElement=1,IpSystem=1,IpAccessSctp=Iub"
exception none
)

SET (
mo "ManagedElement=1,IpSystem=1,IpAccessHostEt=1"
exception none
nrOfAttributes 15
administrativeState Integer 1
configPbitArp Integer 6
configuredSpeedDuplex Integer 6
dscpPbitMap Array Struct 64
nrOfElements 2
dscp Integer 0
pbit Integer 0
nrOfElements 2
dscp Integer 1
pbit Integer 0
nrOfElements 2
dscp Integer 2
pbit Integer 0
nrOfElements 2
dscp Integer 3
pbit Integer 0
nrOfElements 2
dscp Integer 4
pbit Integer 0
nrOfElements 2
dscp Integer 5
pbit Integer 0
nrOfElements 2
dscp Integer 6
pbit Integer 0
nrOfElements 2
dscp Integer 7
pbit Integer 0
nrOfElements 2
dscp Integer 8
pbit Integer 1
nrOfElements 2
dscp Integer 9
pbit Integer 1
nrOfElements 2
dscp Integer 10
pbit Integer 1
nrOfElements 2
dscp Integer 11
pbit Integer 1
nrOfElements 2
dscp Integer 12
pbit Integer 1
nrOfElements 2
dscp Integer 13
pbit Integer 1
nrOfElements 2
dscp Integer 14
pbit Integer 1
nrOfElements 2
dscp Integer 15
pbit Integer 1
nrOfElements 2
dscp Integer 16
pbit Integer 2
nrOfElements 2
dscp Integer 17
pbit Integer 0
nrOfElements 2
dscp Integer 18
pbit Integer 2
nrOfElements 2
dscp Integer 19
pbit Integer 0
nrOfElements 2
dscp Integer 20
pbit Integer 2
nrOfElements 2
dscp Integer 21
pbit Integer 0
nrOfElements 2
dscp Integer 22
pbit Integer 2
nrOfElements 2
dscp Integer 23
pbit Integer 0
nrOfElements 2
dscp Integer 24
pbit Integer 3
nrOfElements 2
dscp Integer 25
pbit Integer 3
nrOfElements 2
dscp Integer 26
pbit Integer 3
nrOfElements 2
dscp Integer 27
pbit Integer 3
nrOfElements 2
dscp Integer 28
pbit Integer 3
nrOfElements 2
dscp Integer 29
pbit Integer 3
nrOfElements 2
dscp Integer 30
pbit Integer 3
nrOfElements 2
dscp Integer 31
pbit Integer 3
nrOfElements 2
dscp Integer 32
pbit Integer 4
nrOfElements 2
dscp Integer 33
pbit Integer 4
nrOfElements 2
dscp Integer 34
pbit Integer 4
nrOfElements 2
dscp Integer 35
pbit Integer 4
nrOfElements 2
dscp Integer 36
pbit Integer 4
nrOfElements 2
dscp Integer 37
pbit Integer 4
nrOfElements 2
dscp Integer 38
pbit Integer 4
nrOfElements 2
dscp Integer 39
pbit Integer 4
nrOfElements 2
dscp Integer 40
pbit Integer 5
nrOfElements 2
dscp Integer 41
pbit Integer 0
nrOfElements 2
dscp Integer 42
pbit Integer 5
nrOfElements 2
dscp Integer 43
pbit Integer 0
nrOfElements 2
dscp Integer 44
pbit Integer 5
nrOfElements 2
dscp Integer 45
pbit Integer 0
nrOfElements 2
dscp Integer 46
pbit Integer 5
nrOfElements 2
dscp Integer 47
pbit Integer 0
nrOfElements 2
dscp Integer 48
pbit Integer 6
nrOfElements 2
dscp Integer 49
pbit Integer 6
nrOfElements 2
dscp Integer 50
pbit Integer 6
nrOfElements 2
dscp Integer 51
pbit Integer 6
nrOfElements 2
dscp Integer 52
pbit Integer 6
nrOfElements 2
dscp Integer 53
pbit Integer 6
nrOfElements 2
dscp Integer 54
pbit Integer 6
nrOfElements 2
dscp Integer 55
pbit Integer 6
nrOfElements 2
dscp Integer 56
pbit Integer 7
nrOfElements 2
dscp Integer 57
pbit Integer 7
nrOfElements 2
dscp Integer 58
pbit Integer 7
nrOfElements 2
dscp Integer 59
pbit Integer 7
nrOfElements 2
dscp Integer 60
pbit Integer 7
nrOfElements 2
dscp Integer 61
pbit Integer 7
nrOfElements 2
dscp Integer 62
pbit Integer 0
nrOfElements 2
dscp Integer 63
pbit Integer 0
frameFormat Integer 0
masterMode Boolean true
portNo Integer 1
shutDownTimeout Integer 1800
statePropagationDelay Integer 25
)

CREATE (
parent "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"
identity "2"
moType IpInterface
exception none
nrOfAttributes 18
administrativeState Integer 1
dhcpClientIdentifier Struct
nrOfElements 2
clientIdentifier String ""
clientIdentifierType Integer 0
logging Integer 0
maxNoOfFailedPings Integer 2
maxWaitForPingReply Integer 3
mtu Integer 1500
networkPrefixLength Integer {MASK} 'MASK
noOfPingsBeforeOk Integer 2
ownIpAddressActive String "0.0.0.0"
rps Boolean false
switchBackTimer Integer 180
trafficType Integer 0
vLan Boolean true
vid Integer {VLAN_OAM} 'Vlan OAM
)

CREATE (
parent "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"
identity "1"
moType IpInterface
exception none
nrOfAttributes 18
administrativeState Integer 1
dhcpClientIdentifier Struct
nrOfElements 2
clientIdentifier String ""
clientIdentifierType Integer 0
logging Integer 0
maxNoOfFailedPings Integer 2
maxWaitForPingReply Integer 3
mtu Integer 1500
networkPrefixLength Integer {MASK} 'MASK
noOfPingsBeforeOk Integer 2
ownIpAddressActive String "0.0.0.0"
rps Boolean false
switchBackTimer Integer 180
trafficType Integer 0
vLan Boolean true
vid Integer {VLAN_IUB} 'Vlan IUB
)

CREATE (
parent "ManagedElement=1,IpSystem=1"
identity "1"
moType IpAccessHostEt
exception none
nrOfAttributes 4
ipAddress String "{IP_OAM}" 'IP OAM
ipDefaultTtl Integer 64
ntpServerMode Integer 0
ipInterfaceMoRef Reference "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1,IpInterface=2"
)

CREATE (
parent "ManagedElement=1,IpSystem=1"
identity "Iub"
moType IpAccessHostEt
exception none
nrOfAttributes 4
ipAddress String "{IP_TRAFICO}" 'IP IUB CONROL
ipDefaultTtl Integer 64
ntpServerMode Integer 0
ipInterfaceMoRef Reference "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1,IpInterface=1"
)

CREATE (
parent "ManagedElement=1,IpSystem=1"
identity "Iub"
moType IpAccessSctp
exception none
nrOfAttributes 1
ipAccessHostEtRef1 Ref "ManagedElement=1,IpSystem=1,IpAccessHostEt=1"
)

CREATE (
parent "ManagedElement=1,TransportNetwork=1"
identity "1"
moType Sctp
exception none
nrOfAttributes 37
allowedIncrementCookieLife Integer 30
associationMaxRtx Integer 8
bundlingActivated Integer 1
bundlingTimer Integer 10
checksumType Integer 0
cookieLife Integer 3600
delayControl Integer 1
defaultRto Integer 20
defaultTsn Integer 0
hbMaxRtx Integer 5
hbTimer Integer 10
inStream Integer 17
initAckT Integer 3
initMaxRtrAtt Integer 8
keyChangePeriod Integer 4
mBuffer Integer 256
maxBurst Integer 4
maxIncomingStream Integer 17
maxInitialRtrAtt Integer 8
maxOutgoingStream Integer 17
maxShutDownRtrAtt Integer 5
maxUserDataSize Integer 1480
maximumRto Integer 40
minimumRto Integer 10
nPercentage Integer 85
nThreshold Integer 192
numberOfAssociations Integer 2
pathMaxRtx Integer 4
protocolVersion Integer 1
rRtoMin Integer 1
reconfigMaxRtx Integer 3
rtoAlpha Integer 12
rtoBeta Integer 25
rtoMax Integer 40
rtoMin Integer 10
shutdownT Integer 3
tSack Integer 4
validCookieLife Integer 60
)

CREATE (
parent "ManagedElement=1,NodeBFunction=1"
identity "{IUB}" 'IUB
moType Iub
exception none
nrOfAttributes 5
rbsId Integer {RBSID} 'RBSID
userLabel String "{NEMONICO}" 'Nemonico
userPlaneIpResourceRef Ref "ManagedElement=1,IpSystem=1,IpAccessHostEt=1"
controlPlaneTransportOption Struct
nrOfElements 2
atm Boolean false
ipV4 Boolean true
)

SET (
mo "ManagedElement=1,NodeBFunction=1,Iub={IUB},IubDataStreams=1" 'IUB
exception none
hsAqmCongCtrlSpiOnOff Array Integer 16
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
1
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
1
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
1
nrOfElements 1
0
hsDataFrameDelayThreshold Integer 60
)

SET (
mo "ManagedElement=1,NodeBFunction=1,Iub={IUB},IubFpData=1"
exception none
nrOfAttributes 4
adminBlocked State Integer 1
iubDlFpSwitch Integer 1
iubUlFpSwitch Integer 1
maxFramePduSize Integer 1480
)

CREATE (
parent "ManagedElement=1,NodeBFunction=1,Iub={IUB}" 'IUB
identity "1"
moType NbapCommon
exception none
nrOfAttributes 4
auditRetransmissionT Integer 5
l2EstablishReqRetryT Integer 1
l2EstablishSupervisionT Integer 30
l3EstablishSupervisionT Integer 30
)

SET (
mo "ManagedElement=1,IpSystem=1,IpAccessHostEt=1"
exception none
administrativeState Integer 1
)

ECHO "Fin del script. RBSID: {RBSID}"
"""

# 2. CAMBIO_3G_PE (Cambio de PE)
TEMPLATE_CAMBIO_PE = """
ECHO "Script de Configuración CAMBIO_3G_PE generado por Python"

ACTION (
actionName removeSyncRefResource
mo "ManagedElement=1,TransportNetwork=1,Synchronization=1"
exception none
nrOfParameters 1
Reference "ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef={SYNC_1}"
returnValue none
)

ACTION (
actionName removeSyncRefResource
mo "ManagedElement=1,TransportNetwork=1,Synchronization=1"
exception none
nrOfParameters 1
Reference "ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef={SYNC_2}"
returnValue none
)

DELETE (
mo "ManagedElement=1,NodeBFunction=1,Iub={IUB},NbapDedicated=1" 'IUB - DELETE Específico para PE
exception none
)

DELETE (
mo "ManagedElement=1,NodeBFunction=1,Iub={IUB}" 'IUB
exception none
)

DELETE (
mo "ManagedElement=1,TransportNetwork=1,Sctp=1"
exception none
)

DELETE (
mo "ManagedElement=1,IpSystem=1,IpAccessSctp=Iub"
exception none
)

SET (
mo "ManagedElement=1,IpSystem=1,IpAccessHostEt=1"
exception none
nrOfAttributes 15
administrativeState Integer 1
configPbitArp Integer 6
configuredSpeedDuplex Integer 6
dscpPbitMap Array Struct 64
nrOfElements 2
dscp Integer 0
pbit Integer 0
nrOfElements 2
dscp Integer 1
pbit Integer 0
nrOfElements 2
dscp Integer 2
pbit Integer 0
nrOfElements 2
dscp Integer 3
pbit Integer 0
nrOfElements 2
dscp Integer 4
pbit Integer 0
nrOfElements 2
dscp Integer 5
pbit Integer 0
nrOfElements 2
dscp Integer 6
pbit Integer 0
nrOfElements 2
dscp Integer 7
pbit Integer 0
nrOfElements 2
dscp Integer 8
pbit Integer 1
nrOfElements 2
dscp Integer 9
pbit Integer 1
nrOfElements 2
dscp Integer 10
pbit Integer 1
nrOfElements 2
dscp Integer 11
pbit Integer 1
nrOfElements 2
dscp Integer 12
pbit Integer 1
nrOfElements 2
dscp Integer 13
pbit Integer 1
nrOfElements 2
dscp Integer 14
pbit Integer 1
nrOfElements 2
dscp Integer 15
pbit Integer 1
nrOfElements 2
dscp Integer 16
pbit Integer 2
nrOfElements 2
dscp Integer 17
pbit Integer 0
nrOfElements 2
dscp Integer 18
pbit Integer 2
nrOfElements 2
dscp Integer 19
pbit Integer 0
nrOfElements 2
dscp Integer 20
pbit Integer 2
nrOfElements 2
dscp Integer 21
pbit Integer 0
nrOfElements 2
dscp Integer 22
pbit Integer 2
nrOfElements 2
dscp Integer 23
pbit Integer 0
nrOfElements 2
dscp Integer 24
pbit Integer 3
nrOfElements 2
dscp Integer 25
pbit Integer 3
nrOfElements 2
dscp Integer 26
pbit Integer 3
nrOfElements 2
dscp Integer 27
pbit Integer 3
nrOfElements 2
dscp Integer 28
pbit Integer 3
nrOfElements 2
dscp Integer 29
pbit Integer 3
nrOfElements 2
dscp Integer 30
pbit Integer 3
nrOfElements 2
dscp Integer 31
pbit Integer 3
nrOfElements 2
dscp Integer 32
pbit Integer 4
nrOfElements 2
dscp Integer 33
pbit Integer 4
nrOfElements 2
dscp Integer 34
pbit Integer 4
nrOfElements 2
dscp Integer 35
pbit Integer 4
nrOfElements 2
dscp Integer 36
pbit Integer 4
nrOfElements 2
dscp Integer 37
pbit Integer 4
nrOfElements 2
dscp Integer 38
pbit Integer 4
nrOfElements 2
dscp Integer 39
pbit Integer 4
nrOfElements 2
dscp Integer 40
pbit Integer 5
nrOfElements 2
dscp Integer 41
pbit Integer 0
nrOfElements 2
dscp Integer 42
pbit Integer 5
nrOfElements 2
dscp Integer 43
pbit Integer 0
nrOfElements 2
dscp Integer 44
pbit Integer 5
nrOfElements 2
dscp Integer 45
pbit Integer 0
nrOfElements 2
dscp Integer 46
pbit Integer 5
nrOfElements 2
dscp Integer 47
pbit Integer 0
nrOfElements 2
dscp Integer 48
pbit Integer 6
nrOfElements 2
dscp Integer 49
pbit Integer 6
nrOfElements 2
dscp Integer 50
pbit Integer 6
nrOfElements 2
dscp Integer 51
pbit Integer 6
nrOfElements 2
dscp Integer 52
pbit Integer 6
nrOfElements 2
dscp Integer 53
pbit Integer 6
nrOfElements 2
dscp Integer 54
pbit Integer 6
nrOfElements 2
dscp Integer 55
pbit Integer 6
nrOfElements 2
dscp Integer 56
pbit Integer 7
nrOfElements 2
dscp Integer 57
pbit Integer 7
nrOfElements 2
dscp Integer 58
pbit Integer 7
nrOfElements 2
dscp Integer 59
pbit Integer 7
nrOfElements 2
dscp Integer 60
pbit Integer 7
nrOfElements 2
dscp Integer 61
pbit Integer 7
nrOfElements 2
dscp Integer 62
pbit Integer 0
nrOfElements 2
dscp Integer 63
pbit Integer 0
frameFormat Integer 0
masterMode Boolean true
portNo Integer 1
shutDownTimeout Integer 1800
statePropagationDelay Integer 25
)

CREATE (
parent "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"
identity "2"
moType IpInterface
exception none
nrOfAttributes 18
administrativeState Integer 1
dhcpClientIdentifier Struct
nrOfElements 2
clientIdentifier String ""
clientIdentifierType Integer 0
logging Integer 0
maxNoOfFailedPings Integer 2
maxWaitForPingReply Integer 3
mtu Integer 1500
networkPrefixLength Integer {MASK} 'MASK
noOfPingsBeforeOk Integer 2
ownIpAddressActive String "0.0.0.0"
rps Boolean false
switchBackTimer Integer 180
trafficType Integer 0
vLan Boolean true
vid Integer {VLAN_OAM} 'Vlan OAM
)

CREATE (
parent "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"
identity "1"
moType IpInterface
exception none
nrOfAttributes 18
administrativeState Integer 1
dhcpClientIdentifier Struct
nrOfElements 2
clientIdentifier String ""
clientIdentifierType Integer 0
logging Integer 0
maxNoOfFailedPings Integer 2
maxWaitForPingReply Integer 3
mtu Integer 1500
networkPrefixLength Integer {MASK} 'MASK
noOfPingsBeforeOk Integer 2
ownIpAddressActive String "0.0.0.0"
rps Boolean false
switchBackTimer Integer 180
trafficType Integer 0
vLan Boolean true
vid Integer {VLAN_IUB} 'Vlan IUB
)

CREATE (
parent "ManagedElement=1,IpSystem=1"
identity "1"
moType IpAccessHostEt
exception none
nrOfAttributes 4
ipAddress String "{IP_OAM}" 'IP OAM
ipDefaultTtl Integer 64
ntpServerMode Integer 0
ipInterfaceMoRef Reference "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1,IpInterface=2"
)

CREATE (
parent "ManagedElement=1,IpSystem=1"
identity "Iub"
moType IpAccessHostEt
exception none
nrOfAttributes 4
ipAddress String "{IP_TRAFICO}" 'IP IUB CONROL
ipDefaultTtl Integer 64
ntpServerMode Integer 0
ipInterfaceMoRef Reference "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1,IpInterface=1"
)

CREATE (
parent "ManagedElement=1,IpSystem=1"
identity "Iub"
moType IpAccessSctp
exception none
nrOfAttributes 1
ipAccessHostEtRef1 Ref "ManagedElement=1,IpSystem=1,IpAccessHostEt=1"
)

CREATE (
parent "ManagedElement=1,TransportNetwork=1"
identity "1"
moType Sctp
exception none
nrOfAttributes 37
allowedIncrementCookieLife Integer 30
associationMaxRtx Integer 8
bundlingActivated Integer 1
bundlingTimer Integer 10
checksumType Integer 0
cookieLife Integer 3600
delayControl Integer 1
defaultRto Integer 20
defaultTsn Integer 0
hbMaxRtx Integer 5
hbTimer Integer 10
inStream Integer 17
initAckT Integer 3
initMaxRtrAtt Integer 8
keyChangePeriod Integer 4
mBuffer Integer 256
maxBurst Integer 4
maxIncomingStream Integer 17
maxInitialRtrAtt Integer 8
maxOutgoingStream Integer 17
maxShutDownRtrAtt Integer 5
maxUserDataSize Integer 1480
maximumRto Integer 40
minimumRto Integer 10
nPercentage Integer 85
nThreshold Integer 192
numberOfAssociations Integer 2
pathMaxRtx Integer 4
protocolVersion Integer 1
rRtoMin Integer 1
reconfigMaxRtx Integer 3
rtoAlpha Integer 12
rtoBeta Integer 25
rtoMax Integer 40
rtoMin Integer 10
shutdownT Integer 3
tSack Integer 4
validCookieLife Integer 60
)

CREATE (
parent "ManagedElement=1,NodeBFunction=1"
identity "{IUB}" 'IUB
moType Iub
exception none
nrOfAttributes 5
rbsId Integer {RBSID} 'RBSID
userLabel String "{NEMONICO}" 'Nemonico
userPlaneIpResourceRef Ref "ManagedElement=1,IpSystem=1,IpAccessHostEt=1"
controlPlaneTransportOption Struct
nrOfElements 2
atm Boolean false
ipV4 Boolean true
)

SET (
mo "ManagedElement=1,NodeBFunction=1,Iub={IUB},IubDataStreams=1" 'IUB
exception none
hsAqmCongCtrlSpiOnOff Array Integer 16
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
1
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
1
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
1
nrOfElements 1
0
hsDataFrameDelayThreshold Integer 60
)

SET (
mo "ManagedElement=1,NodeBFunction=1,Iub={IUB},IubFpData=1"
exception none
nrOfAttributes 4
adminBlocked State Integer 1
iubDlFpSwitch Integer 1
iubUlFpSwitch Integer 1
maxFramePduSize Integer 1480
)

CREATE (
parent "ManagedElement=1,NodeBFunction=1,Iub={IUB}" 'IUB
identity "1"
moType NbapCommon
exception none
nrOfAttributes 4
auditRetransmissionT Integer 5
l2EstablishReqRetryT Integer 1
l2EstablishSupervisionT Integer 30
l3EstablishSupervisionT Integer 30
)

SET (
mo "ManagedElement=1,IpSystem=1,IpAccessHostEt=1"
exception none
administrativeState Integer 1
)

# --- PARÁMETRO PE ESPECÍFICO DEL FORMULARIO ---
SET (
mo "ManagedElement=1,PE_Site=1"
exception none
PE_Address String "{PE_VALUE}" 
)

ECHO "Fin del script. RBSID: {RBSID}"
"""

# 3. CAMBIO IP 3G (Cambio IP)
TEMPLATE_CAMBIO_IP = """
ECHO "Script de Configuración CAMBIO IP 3G generado por Python"

# --- DELETES INICIALES ---
DELETE (
mo "ManagedElement=1,NodeBFunction=1,Iub={IUB}" 'IUB
exception none
)

DELETE (
mo "ManagedElement=1,TransportNetwork=1,Sctp=1"
exception none
)

DELETE (
mo "ManagedElement=1,IpSystem=1,IpAccessSctp=Iub"
exception none
)
# -------------------------

# --- IP Routing Table Configuration ---
ACTION (
actionName addStaticRoute
mo "ManagedElement=1,IpOam=1,Ip=1,IpRoutingTable=1"
exception none
nrOfParameters 5
String "0.0.0.0"
String "0.0.0.0"
String "{DGW_Iub_IP}" 'DGW IUB IP
Integer 100
Boolean 0
returnValue none
)

ACTION (
actionName addStaticRoute
mo "ManagedElement=1,IpOam=1,Ip=1,IpRoutingTable=1"
exception none
nrOfParameters 5
String "0.0.0.0"
String "0.0.0.0"
String "{DGW_Iub_IP_OAM}" 'DGW IUB OAM IP
Integer 100
Boolean 0
returnValue none
)

# --- IP Interfaces (OAM/IUB) ---
CREATE (
parent "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"
identity "2"
moType IpInterface
exception none
nrOfAttributes 18
administrativeState Integer 1
dhcpClientIdentifier Struct
nrOfElements 2
clientIdentifier String ""
clientIdentifierType Integer 0
logging Integer 0
maxNoOfFailedPings Integer 2
maxWaitForPingReply Integer 3
mtu Integer 1500
networkPrefixLength Integer {MASK} 'MASK
noOfPingsBeforeOk Integer 2
ownIpAddressActive String "0.0.0.0"
rps Boolean false
switchBackTimer Integer 180
trafficType Integer 0
vLan Boolean true
vid Integer {VLAN_OAM} 'Vlan OAM
)

CREATE (
parent "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"
identity "1"
moType IpInterface
exception none
nrOfAttributes 18
administrativeState Integer 1
dhcpClientIdentifier Struct
nrOfElements 2
clientIdentifier String ""
clientIdentifierType Integer 0
logging Integer 0
maxNoOfFailedPings Integer 2
maxWaitForPingReply Integer 3
mtu Integer 1500
networkPrefixLength Integer {MASK} 'MASK
noOfPingsBeforeOk Integer 2
ownIpAddressActive String "0.0.0.0"
rps Boolean false
switchBackTimer Integer 180
trafficType Integer 0
vLan Boolean true
vid Integer {VLAN_IUB} 'Vlan IUB
)

# --- IP Access Hosts (OAM/IUB) ---
CREATE (
parent "ManagedElement=1,IpSystem=1"
identity "1"
moType IpAccessHostEt
exception none
nrOfAttributes 4
ipAddress String "{IP_OAM}" 'IP OAM
ipDefaultTtl Integer 64
ntpServerMode Integer 0
ipInterfaceMoRef Reference "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1,IpInterface=2"
)

CREATE (
parent "ManagedElement=1,IpSystem=1"
identity "Iub"
moType IpAccessHostEt
exception none
nrOfAttributes 4
ipAddress String "{IP_TRAFICO}" 'IP IUB CONROL
ipDefaultTtl Integer 64
ntpServerMode Integer 0
ipInterfaceMoRef Reference "ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1,IpInterface=1"
)

# --- SCTP ---
CREATE (
parent "ManagedElement=1,IpSystem=1"
identity "Iub"
moType IpAccessSctp
exception none
nrOfAttributes 1
ipAccessHostEtRef1 Ref "ManagedElement=1,IpSystem=1,IpAccessHostEt=1"
)

CREATE (
parent "ManagedElement=1,TransportNetwork=1"
identity "1"
moType Sctp
exception none
nrOfAttributes 37
allowedIncrementCookieLife Integer 30
associationMaxRtx Integer 8
bundlingActivated Integer 1
bundlingTimer Integer 10
checksumType Integer 0
cookieLife Integer 3600
delayControl Integer 1
defaultRto Integer 20
defaultTsn Integer 0
hbMaxRtx Integer 5
hbTimer Integer 10
inStream Integer 17
initAckT Integer 3
initMaxRtrAtt Integer 8
keyChangePeriod Integer 4
mBuffer Integer 256
maxBurst Integer 4
maxIncomingStream Integer 17
maxInitialRtrAtt Integer 8
maxOutgoingStream Integer 17
maxShutDownRtrAtt Integer 5
maxUserDataSize Integer 1480
maximumRto Integer 40
minimumRto Integer 10
nPercentage Integer 85
nThreshold Integer 192
numberOfAssociations Integer 2
pathMaxRtx Integer 4
protocolVersion Integer 1
rRtoMin Integer 1
reconfigMaxRtx Integer 3
rtoAlpha Integer 12
rtoBeta Integer 25
rtoMax Integer 40
rtoMin Integer 10
shutdownT Integer 3
tSack Integer 4
validCookieLife Integer 60
)

# --- IUB ---
CREATE (
parent "ManagedElement=1,NodeBFunction=1"
identity "{IUB}" 'IUB
moType Iub
exception none
nrOfAttributes 5
rbsId Integer {RBSID} 'RBSID
userLabel String "{NEMONICO}" 'Nemonico
userPlaneIpResourceRef Ref "ManagedElement=1,IpSystem=1,IpAccessHostEt=1"
controlPlaneTransportOption Struct
nrOfElements 2
atm Boolean false
ipV4 Boolean true
)

SET (
mo "ManagedElement=1,NodeBFunction=1,Iub={IUB},IubDataStreams=1"
exception none
hsAqmCongCtrlSpiOnOff Array Integer 16
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
1
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
1
nrOfElements 1
0
nrOfElements 1
0
nrOfElements 1
1
nrOfElements 1
0
hsDataFrameDelayThreshold Integer 60
)

SET (
mo "ManagedElement=1,NodeBFunction=1,Iub={IUB},IubFpData=1"
exception none
nrOfAttributes 4
adminBlocked State Integer 1
iubDlFpSwitch Integer 1
iubUlFpSwitch Integer 1
maxFramePduSize Integer 1480
)

CREATE (
parent "ManagedElement=1,NodeBFunction=1,Iub={IUB}" 'IUB
identity "1"
moType NbapCommon
exception none
nrOfAttributes 4
auditRetransmissionT Integer 5
l2EstablishReqRetryT Integer 1
l2EstablishSupervisionT Integer 30
l3EstablishSupervisionT Integer 30
)

# --- NTP Configuration (Sync References) ---
# Usa los valores pasados manualmente para IP NTP 1 y 2
CREATE (
parent "ManagedElement=1,IpSystem=1,IpAccessHostEt=1"
identity "7"
moType IpSyncRef
exception none
nrOfAttributes 2
userLabel String "IP NTP Sync Server 1"
ntpServerIpAddress String "{IP_NTP_1}" 'IP_NTP_1
)

CREATE (
parent "ManagedElement=1,IpSystem=1,IpAccessHostEt=1"
identity "8"
moType IpSyncRef
exception none
nrOfAttributes 2
userLabel String "IP NTP Sync Server 2"
ntpServerIpAddress String "{IP_NTP_2}" 'IP_NTP_2
)

# --- Configuration Version Actions ---
ACTION (
actionName create
mo "ManagedElement=1,SwManagement=1,ConfigurationVersion=1"
exception none
nrOfParameters 5
String "CAMBIO_IP"
String "CAMBIO_IP"
Integer 5
String "user"
String "CV Startable"
returnValue none
)
ACTION (
actionName setStartable
mo "ManagedElement=1,SwManagement=1,ConfigurationVersion=1"
exception none
nrOfParameters 1
String "CAMBIO_IP"
returnValue none
)

ECHO "Fin del script. RBSID: {RBSID}"
"""


# ==============================================================================
# 1. FUNCIONES DE RENDERIZADO DE FORMULARIOS (Vistas)
# ==============================================================================

def render_form(form_name, template, extra_inputs=None):
    """Función genérica para renderizar cualquiera de los 3 formularios."""
    
    st.title(f"🛠️ Generador de Scripts - {form_name}")
    st.markdown("---")
    
    STATE_KEY = f'{form_name}_extracted_data'
    if STATE_KEY not in st.session_state:
        st.session_state[STATE_KEY] = None

    # --- 1. SECCIÓN DE CARGA Y PARÁMETROS MANUALES ---
    with st.container(border=True):
        st.header("1. Carga de Excel y Parámetros Clave Manuales")
        
        # 1. Carga de Archivo Excel
        uploaded_file = st.file_uploader(
            "Archivo Excel (Requerido para obtener IPs/VLANs)", 
            type=['xls', 'xlsx'],
            key=f"{form_name}_uploader"
        )
        
        parametros_manuales = {}
        
        # Campos de Texto IUB, RBSID, MAXHSRATE
        st.subheader("Parámetros Clave (Manual)")
        col_manual = st.columns(3)
        with col_manual[0]:
            iub_value = st.text_input("IUB:", value="IUB_SITE_NAME", key=f"{form_name}_iub")
        with col_manual[1]:
            rbsid_value = st.text_input("RBSID:", value="RBSID_NUM", key=f"{form_name}_rbsid")
        with col_manual[2]:
            maxhsrate_value = st.text_input("MAXHSRATE:", value="HSRATE_NUM", key=f"{form_name}_maxhsrate")

        # Se añaden a los parámetros que se pasarán al script
        parametros_manuales['IUB'] = iub_value
        parametros_manuales['RBSID'] = rbsid_value
        parametros_manuales['MAXHSRATE'] = maxhsrate_value 
        
        # 2. Inputs Específicos del Formulario (PE, NTP 1, NTP 2)
        if extra_inputs:
            st.subheader("Parámetros Adicionales")
            cols = st.columns(len(extra_inputs))
            for i, (key, label, default_value) in enumerate(extra_inputs):
                with cols[i]:
                    parametros_manuales[key] = st.text_input(label, value=default_value, key=f"{form_name}_{key}")

        # 3. Inputs para SYNC (ComboBoxes) - Valores 1, 7 y 2, 8 (Corregido)
        st.subheader("Selección SYNC")
        col1, col2 = st.columns(2)
        with col1:
            sync_1 = st.selectbox("SYNC 1:", ["1", "7", "N/A"], index=2, key=f"{form_name}_sync1")
        with col2:
            sync_2 = st.selectbox("SYNC 2:", ["2", "8", "N/A"], index=2, key=f"{form_name}_sync2")
        
        parametros_manuales['SYNC_1'] = sync_1
        parametros_manuales['SYNC_2'] = sync_2


    # --- 2. BOTÓN DE PROCESAMIENTO ---
    st.markdown("---")
    
    if st.button(f"BUSCAR y Generar Script", use_container_width=True, type="primary"):
        
        # 1. Extraer datos (Valida el archivo y devuelve los manuales + datos del Excel)
        parametros = extraer_parametros(uploaded_file, parametros_manuales)
        
        if 'error' in parametros:
            st.session_state[STATE_KEY] = {'error': parametros['error']}
            st.error(parametros['error'])
        else:
            st.session_state[STATE_KEY] = parametros
            st.success("✅ Datos Validados y listos para la generación.")
            st.toast("Script listo para descargar.")


    # --- 3. GENERACIÓN DEL SCRIPT (Botón de Descarga) ---
    st.header("2. Generación y Descarga del Archivo")
    
    if st.session_state[STATE_KEY] and 'error' not in st.session_state[STATE_KEY]:
        data = st.session_state[STATE_KEY]
        
        # 1. Generar Script
        script_content = generar_script(data, template)
        
        # 2. Descarga (¡Lógica que usa NEMONICO!)
        # Intenta obtener el NEMONICO; si falla, usa un marcador.
        nemonico_name = data.get('NEMONICO', 'SIN_NEMONICO')
        
        # Limpia el NEMONICO para que sea un nombre de archivo seguro
        safe_nemonico = nemonico_name.replace(' ', '_').replace('.', '-') 
        
        # Genera el prefijo del formulario limpio
        form_prefix = form_name.replace(' ', '_').replace('__', '_')
        
        # Genera el nombre de archivo final: config_NOMBRE_FORMULARIO_NEMONICO.txt
        file_name = f"config_{form_prefix}_{safe_nemonico}.txt"
        
        st.download_button(
            label="Descargar Script de Configuración (.txt)",
            data=script_content,
            file_name=file_name,
            mime="text/plain",
            key=f"{form_name}_download_btn"
        )
        
        with st.expander("Ver Contenido Generado (Vista Previa)"):
            st.code(script_content, language='text')
            
    elif st.session_state[STATE_KEY] and 'error' in st.session_state[STATE_KEY]:
        st.error(st.session_state[STATE_KEY]['error'])
    else:
        st.info("Presiona 'BUSCAR y Generar Script' después de subir el Excel y rellenar los campos.")


# ==============================================================================
# 3. FUNCIÓN MAIN DE LA APLICACIÓN (Maneja la navegación)
# ==============================================================================

def main():
    if 'page' not in st.session_state:
        st.session_state.page = 'DUW_CAMBIO_A_OPTICO' 

    # --- Sidebar (Menú de Macros) ---
    with st.sidebar:
        st.header("Menú de Macros (Formularios)")
        st.markdown("---")
        
        # 1. DUW_ CAMBIO A OPTICO
        if st.button("DUW_ CAMBIO A OPTICO", use_container_width=True):
            st.session_state.page = 'DUW_CAMBIO_A_OPTICO'
        
        # 2. CAMBIO_3G_PE
        if st.button("CAMBIO_3G_PE", use_container_width=True):
            st.session_state.page = 'CAMBIO_3G_PE'
            
        # 3. CAMBIO IP 3G
        if st.button("CAMBIO IP 3G", use_container_width=True):
            st.session_state.page = 'CAMBIO_IP_3G'
        
        st.markdown("---")
        st.info("Seleccione el formulario para comenzar.")

    # --- Contenido Principal (Renderiza la página seleccionada) ---

    if st.session_state.page == 'DUW_CAMBIO_A_OPTICO':
        render_form("DUW_ CAMBIO A OPTICO", TEMPLATE_DUW_OPTICO)
        
    elif st.session_state.page == 'CAMBIO_3G_PE':
        # PE_VALUE se usa en el template TEMPLATE_CAMBIO_PE
        extra_inputs = [
            ('PE_VALUE', 'Valor de PE:', '10.10.10.1'),
        ]
        render_form("CAMBIO_3G_PE", TEMPLATE_CAMBIO_PE, extra_inputs)
        
    elif st.session_state.page == 'CAMBIO_IP_3G':
        # IP_NTP_1 y IP_NTP_2 se usan en el template TEMPLATE_CAMBIO_IP
        extra_inputs = [
            ('IP_NTP_1', 'IP NTP 1:', '1.1.1.1'),
            ('IP_NTP_2', 'IP NTP 2:', '2.2.2.2'),
        ]
        render_form("CAMBIO IP 3G", TEMPLATE_CAMBIO_IP, extra_inputs)

if __name__ == '__main__':
    main()