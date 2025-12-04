# ==============================================================================
# node_generator_3G.py - Generación de scripts de nodo para 3G
# ==============================================================================

def generar_nodeid_mos(nemonico: str) -> str:
    """
    Genera el contenido del archivo 00_{Nemonico}_PL_Nodeid.mos
    basado en el template estático proporcionado.
    """
    nemonico_upper = nemonico.upper()
    
    # Contenido estático con reemplazos mínimos
    mos_content = f"""//
// SCRIPT     : NodeId
// AUTOR      : PIERO LEDESMA
// NEMONICO   : {nemonico_upper}
//
/////////////////////////////////////////////////////////////

confb+
gs+
lt all
get Transport=1,EthernetPort= ethernetPortId > $eth

confb+
gs+

accn Lm=1,IntegrationUnlock=1  activate
set SwM=1,UpgradePackage=CXP9024418/15-R53M22  uri sftp://mm-software@172.25.7.33:22/smrsroot/software/radionode/RadioNode_CXP9024418_15_R53M22_22.Q2
set SystemFunctions=1,SwM=1,UpgradePackage=CXP9024418/15-R53M22 password password=1:yxoOasH4WLb21cr3uJCcJ6vznNB47SI5
#############################################################
### SctpProfile                                              
#############################################################

crn Transport=1,SctpProfile=1
alphaIndex 3
assocMaxRtx 20
betaIndex 2
bundlingActivated true
bundlingAdaptiveActivated true
bundlingTimer 10
cookieLife 60
dscp 40
hbMaxBurst 1
heartbeatActivated true
heartbeatInterval 2000
incCookieLife 30
initARWnd 16384
initRto 200
initialHeartbeatInterval 500
maxActivateThr 65535
maxBurst 4
maxInStreams 17
maxInitRt 8
maxOutStreams 17
maxRto 400
maxSctpPduSize 1480
maxShutdownRt 5
minActivateThr 1
minRto 100
noSwitchback true
pathMaxRtx 4
primaryPathAvoidance true
primaryPathMaxRtx 0
sackTimer 40
thrTransmitBuffer 48
thrTransmitBufferCongCeased 85
transmitBufferSize 256
userLabel 1
end
#############################################################
### SctpEndpoint (Creacin estatica)                           
#############################################################

crn Transport=1,SctpEndpoint=1
localIpAddress Transport=1,Router=WCDMA,InterfaceIPv4=1,AddressIPv4=1
portNumber 36422
sctpProfile Transport=1,sctpProfile=1
userLabel 
end

#############################################################
### Cabinet (Creacin estatica)                           
#############################################################

cr Equipment=1,Cabinet=1
cr EquipmentSupportFunction=1,Climate=1
set EquipmentSupportFunction=1,Climate=1  controlDomainRef Cabinet=1
set EquipmentSupportFunction=1,Climate=1  climateControlMode 0
set Equipment=1,FieldReplaceableUnit=1 PositionRef Cabinet=1
set  NodeSupport=1,MpClusterHandling=1 primaryCoreRef  FieldReplaceableUnit=1 
#############################################################
### TimeSettings (Creacin estatica)                           
#############################################################

ld NodeSupport=1,TimeSettings=1 #SystemCreated
lset NodeSupport=1,TimeSettings=1$ timeOffset +00:00
lset NodeSupport=1,TimeSettings=1$ daylightSavingTimeOffset 1:00
lset NodeSupport=1,TimeSettings=1$ gpsToUtcLeapSeconds 0

#############################################################
### DscpPcpMap                        
#############################################################
crn Transport=1,QosProfiles=1,DscpPcpMap=1
defaultPcp 0
pcp0 0
pcp1 12,14
pcp2 18,20,22
pcp3 26,28,
pcp4 34,36,38
pcp5 40,42,44,46
pcp6 48
pcp7 56
end
#############################################################
### egressQosMarking (Creacin estatica)                           
#############################################################

ld Transport=1,Router=WCDMA,InterfaceIPv4=1
lset Transport=1,Router=WCDMA,InterfaceIPv4=1$ egressQosMarking Transport=1,QosProfiles=1,DscpPcpMap=1
ld Transport=1,Router=WCDMA_OAM,InterfaceIPv4=1
lset Transport=1,Router=WCDMA_OAM,InterfaceIPv4=1$ egressQosMarking Transport=1,QosProfiles=1,DscpPcpMap=1

#############################################################
### RadioEquipmentClock Reference  (Creacin estatica)         
#############################################################
crn Transport=1,Ptp=1
end

crn Transport=1,Ptp=1,BoundaryOrdinaryClock=1
clockType 2
domainNumber 24
priority1 255
priority2 255
ptpProfile 2
end

crn Transport=1,Ptp=1,BoundaryOrdinaryClock=1,PtpBcOcPort=1
administrativeState 1
announceMessageInterval 1
associatedGrandmaster
asymmetryCompensation 0
dscp 56
durationField 300
localPriority 128
masterOnly false
pBit 1
ptpMulticastAddress 0
ptpPathTimeError 1000
syncMessageInterval -4
transportInterface EthernetPort=$eth
transportVlan
end

crn Transport=1,Synchronization=1,RadioEquipmentClock=1
bfnOffset 0
freqDeviationThreshold 5000
minQualityLevel qualityLevelValueOptionI=2,qualityLevelValueOptionII=2,qualityLevelValueOptionIII=1
selectionProcessMode 1
end

crn Transport=1,Synchronization=1,RadioEquipmentClock=1,RadioEquipmentClockReference=PTP_FASE
adminQualityLevel qualityLevelValueOptionI=2,qualityLevelValueOptionII=2,qualityLevelValueOptionIII=1
administrativeState 1
encapsulation Ptp=1,BoundaryOrdinaryClock=1
holdOffTime 1000
priority 1
useQLFrom 1
waitToRestoreTime 60
end
cr Synchronization=1,SyncEthInput=1
EthernetPort=$eth
cr Transport=1,Synchronization=1,RadioEquipmentClock=1,RadioEquipmentClockReference=SyncE
Synchronization=1,SyncEthInput=1
5

deb radioequip
set CXC4040008 featurestate 1
set CXC4040011 featurestate 1
gs-  
confb-  
cvms PL_node_$nodename 
///////////////////////////////////fin script nodeid\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
"""
    return mos_content
