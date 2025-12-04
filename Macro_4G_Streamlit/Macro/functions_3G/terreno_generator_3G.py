# ==============================================================================
# terreno_generator_3G.py - Generación de archivos XML de terreno para 3G WCDMA
# ==============================================================================

from typing import Dict

# ==============================================================================
# FUNCIÓN 1: Generar RbsSummaryFile
# ==============================================================================

def generar_rbssummary(nemonico: str, release: str) -> str:
    """
    Genera el archivo 00_{NEMONICO}_RbsSummaryFile.xml
    """
    nemonico_upper = nemonico.upper()
    
    xml_content = f"""<summary:AutoIntegrationRbsSummaryFile
xmlns:summary="http://www.ericsson.se/RbsSummaryFileSchema"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://www.ericsson.se/RbsSummaryFileSchemaSummaryFile.xsd">
<Format revision="F"/>
<ConfigurationFiles
    siteBasicFilePath="01_{nemonico_upper}_SiteBasic.xml"
    siteEquipmentFilePath="02_{nemonico_upper}_SiteEquipment.xml"
    upgradePackageFilePath="{release}/"/>
</summary:AutoIntegrationRbsSummaryFile>
"""
    return xml_content

# ==============================================================================
# FUNCIÓN 2: Generar SiteBasic
# ==============================================================================

def generar_sitebasic(nemonico: str, wsh_data: Dict[str, str], trama: str) -> str:
    """
    Genera el archivo 01_{NEMONICO}_SiteBasic.xml con configuración de red WCDMA
    """
    nemonico_upper = nemonico.upper()
    
    # Extraer datos del WSH (estilo 4G - separado IP y mask)
    ip_oam = wsh_data.get('IP_OAM', '0.0.0.0')
    ip_trafico = wsh_data.get('IP_TRAFICO', '0.0.0.0')
    mask_oam = wsh_data.get('MASK_OAM', '26')
    mask_trafico = wsh_data.get('MASK_TRAFICO', '26')
    gateway_oam = wsh_data.get('GATEWAY_OAM', '0.0.0.0')
    gateway_trafico = wsh_data.get('GATEWAY_TRAFICO', '0.0.0.0')
    vlan_oam = wsh_data.get('VLAN_OAM', '1301')
    vlan_trafico = wsh_data.get('VLAN_TRAFICO', '1300')
    dns = wsh_data.get('DNS', '10.170.15.20')
    ntp1 = wsh_data.get('NTP1', '172.16.50.41')
    ntp2 = wsh_data.get('NTP2', '172.16.50.42')
    
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <capabilities>
    <capability>urn:ietf:params:netconf:base:1.0</capability>
  </capabilities>
</hello>
]]>]]>
<rpc message-id="1" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <edit-config>
    <target>
      <running />
    </target>
    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
      <ManagedElement xmlns="urn:com:ericsson:ecim:ComTop">
        <managedElementId>1</managedElementId>
        <SystemFunctions>
          <systemFunctionsId>1</systemFunctionsId>
          <Lm xmlns="urn:com:ericsson:ecim:RcsLM">
            <lmId>1</lmId>
            <fingerprint>{nemonico_upper}</fingerprint>
          </Lm>
        </SystemFunctions>
      </ManagedElement>
    </config>
  </edit-config>
</rpc>
]]>]]>
<rpc message-id="Closing" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <close-session></close-session>
</rpc>
]]>]]>
<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <capabilities>
    <capability>urn:ietf:params:netconf:base:1.0</capability>
  </capabilities>
</hello>
]]>]]>
<rpc message-id="2" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <edit-config>
    <target>
      <running />
    </target>
    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
      <ManagedElement xmlns="urn:com:ericsson:ecim:ComTop">
        <managedElementId>1</managedElementId>
        <SystemFunctions>
          <systemFunctionsId>1</systemFunctionsId>
          <Lm xmlns="urn:com:ericsson:ecim:RcsLM">
            <lmId>1</lmId>
            <FeatureState>
              <featureStateId>CXC4011823</featureStateId>
              <featureState>ACTIVATED</featureState>
            </FeatureState>
          </Lm>
        </SystemFunctions>
      </ManagedElement>
    </config>
  </edit-config>
</rpc>
]]>]]>
<rpc message-id="Closing" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <close-session></close-session>
</rpc>
]]>]]>
<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <capabilities>
    <capability>urn:ietf:params:netconf:base:1.0</capability>
  </capabilities>
</hello>
]]>]]>
<rpc message-id="3" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <edit-config>
    <target>
      <running />
    </target>
    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
      <ManagedElement xmlns="urn:com:ericsson:ecim:ComTop">
        <managedElementId>1</managedElementId>
        <SystemFunctions>
          <systemFunctionsId>1</systemFunctionsId>
          <SecM xmlns="urn:com:ericsson:ecim:ComSecM">
            <secMId>1</secMId>
            <UserManagement>
              <userManagementId>1</userManagementId>
              <LocalAuthorizationMethod xmlns="urn:com:ericsson:ecim:ComLocalAuthorization">
                <localAuthorizationMethodId>1</localAuthorizationMethodId>
                <administrativeState>UNLOCKED</administrativeState>
              </LocalAuthorizationMethod>
              <UserIdentity xmlns="urn:com:ericsson:ecim:RcsUser">
                <userIdentityId>1</userIdentityId>
                <MaintenanceUser>
                  <maintenanceUserId>1</maintenanceUserId>
                  <userName>rbs</userName>
                  <password>
                    <cleartext />
                    <password>rbs</password>
                  </password>
                </MaintenanceUser>
              </UserIdentity>
            </UserManagement>
          </SecM>
          <SysM xmlns="urn:com:ericsson:ecim:RcsSysM">
            <sysMId>1</sysMId>
            <CliSsh>
              <cliSshId>1</cliSshId>
              <administrativeState>UNLOCKED</administrativeState>
              <port>2023</port>
            </CliSsh>
            <NetconfSsh>
              <netconfSshId>1</netconfSshId>
              <administrativeState>UNLOCKED</administrativeState>
              <port>830</port>
            </NetconfSsh>
            <NtpServer>
              <ntpServerId>1</ntpServerId>
              <serverAddress>{ntp1}</serverAddress>
              <administrativeState>UNLOCKED</administrativeState>
            </NtpServer>
            <NtpServer>
              <ntpServerId>2</ntpServerId>
              <serverAddress>{ntp2}</serverAddress>
              <administrativeState>UNLOCKED</administrativeState>
            </NtpServer>
          </SysM>
        </SystemFunctions>
        <Transport>
          <transportId>1</transportId>
          <Router xmlns="urn:com:ericsson:ecim:RtnL3Router">
            <routerId>WCDMA_OAM</routerId>
          </Router>
          <EthernetPort xmlns="urn:com:ericsson:ecim:RtnL2EthernetPort">
            <ethernetPortId>{trama}</ethernetPortId>
            <administrativeState>UNLOCKED</administrativeState>
            <admOperatingMode>1G_FULL</admOperatingMode>
            <autoNegEnable>true</autoNegEnable>
            <encapsulation>ManagedElement=1,Equipment=1,FieldReplaceableUnit=BB-1,TnPort={trama}</encapsulation>
            <userLabel>{trama}</userLabel>
          </EthernetPort>
          <VlanPort xmlns="urn:com:ericsson:ecim:RtnL2VlanPort">
            <vlanPortId>WCDMA_OAM</vlanPortId>
            <encapsulation>ManagedElement=1,Transport=1,EthernetPort={trama}</encapsulation>
            <vlanId>{vlan_oam}</vlanId>
          </VlanPort>
          <Router xmlns="urn:com:ericsson:ecim:RtnL3Router">
            <routerId>WCDMA_OAM</routerId>
            <InterfaceIPv4 xmlns="urn:com:ericsson:ecim:RtnL3InterfaceIPv4">
              <interfaceIPv4Id>1</interfaceIPv4Id>
              <encapsulation>ManagedElement=1,Transport=1,VlanPort=WCDMA_OAM</encapsulation>
              <userLabel>WCDMA_OAM</userLabel>
              <AddressIPv4>
                <addressIPv4Id>1</addressIPv4Id>
                <address>{ip_oam}/{mask_oam}</address>
              </AddressIPv4>
            </InterfaceIPv4>
          </Router>
        </Transport>
        <SystemFunctions>
          <systemFunctionsId>1</systemFunctionsId>
          <SysM xmlns="urn:com:ericsson:ecim:RcsSysM">
            <sysMId>1</sysMId>
            <OamAccessPoint>
              <oamAccessPointId>1</oamAccessPointId>
              <accessPoint>ManagedElement=1,Transport=1,Router=WCDMA_OAM,InterfaceIPv4=1,AddressIPv4=1</accessPoint>
            </OamAccessPoint>
          </SysM>
        </SystemFunctions>
        <Transport>
          <transportId>1</transportId>
          <Ntp xmlns="urn:com:ericsson:ecim:RsyncNtp">
            <ntpId>1</ntpId>
          </Ntp>
          <Router xmlns="urn:com:ericsson:ecim:RtnL3Router">
            <routerId>WCDMA</routerId>
          </Router>
          <VlanPort xmlns="urn:com:ericsson:ecim:RtnL2VlanPort">
            <vlanPortId>WCDMA</vlanPortId>
            <encapsulation>ManagedElement=1,Transport=1,EthernetPort={trama}</encapsulation>
            <vlanId>{vlan_trafico}</vlanId>
          </VlanPort>
          <Router xmlns="urn:com:ericsson:ecim:RtnL3Router">
            <routerId>WCDMA</routerId>
            <InterfaceIPv4 xmlns="urn:com:ericsson:ecim:RtnL3InterfaceIPv4">
              <interfaceIPv4Id>1</interfaceIPv4Id>
              <encapsulation>ManagedElement=1,Transport=1,VlanPort=WCDMA</encapsulation>
              <userLabel>WCDMA</userLabel>
              <AddressIPv4>
                <addressIPv4Id>1</addressIPv4Id>
                <address>{ip_trafico}/{mask_trafico}</address>
              </AddressIPv4>
            </InterfaceIPv4>
          </Router>
          <Router xmlns="urn:com:ericsson:ecim:RtnL3Router">
            <routerId>WCDMA_OAM</routerId>
            <DnsClient xmlns="urn:com:ericsson:ecim:RtnDnsClient">
              <dnsClientId>1</dnsClientId>
              <configurationMode>MANUAL</configurationMode>
              <serverAddress>{dns}</serverAddress>
            </DnsClient>
            <RouteTableIPv4Static xmlns="urn:com:ericsson:ecim:RtnRoutesStaticRouteIPv4">
              <routeTableIPv4StaticId>1</routeTableIPv4StaticId>
              <Dst>
                <dstId>1</dstId>
                <dst>0.0.0.0/0</dst>
                <NextHop>
                  <nextHopId>1</nextHopId>
                  <address>{gateway_oam}</address>
                  <adminDistance>1</adminDistance>
                </NextHop>
              </Dst>
            </RouteTableIPv4Static>
          </Router>
          <Router xmlns="urn:com:ericsson:ecim:RtnL3Router">
            <routerId>WCDMA</routerId>
            <RouteTableIPv4Static xmlns="urn:com:ericsson:ecim:RtnRoutesStaticRouteIPv4">
              <routeTableIPv4StaticId>1</routeTableIPv4StaticId>
              <Dst>
                <dstId>1</dstId>
                <dst>0.0.0.0/0</dst>
                <NextHop>
                  <nextHopId>1</nextHopId>
                  <address>{gateway_trafico}</address>
                  <adminDistance>1</adminDistance>
                </NextHop>
              </Dst>
            </RouteTableIPv4Static>
          </Router>
        </Transport>
        <Equipment xmlns="urn:com:ericsson:ecim:ReqEquipment">
          <equipmentId>1</equipmentId>
          <FieldReplaceableUnit xmlns="urn:com:ericsson:ecim:ReqFieldReplaceableUnit">
            <fieldReplaceableUnitId>BB-1</fieldReplaceableUnitId>
            <TnPort xmlns="urn:com:ericsson:ecim:ReqTnPort">
              <tnPortId>{trama}</tnPortId>
            </TnPort>
          </FieldReplaceableUnit>
        </Equipment>
      </ManagedElement>
    </config>
  </edit-config>
</rpc>
]]>]]>
<rpc message-id="Closing" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <close-session></close-session>
</rpc>
]]>]]>
<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <capabilities>
    <capability>urn:ietf:params:netconf:base:1.0</capability>
  </capabilities>
</hello>
]]>]]>
<rpc message-id="4" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <edit-config>
    <target>
      <running />
    </target>
    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
      <ManagedElement xmlns="urn:com:ericsson:ecim:ComTop">
        <managedElementId>1</managedElementId>
        <networkManagedElementId>{nemonico_upper}</networkManagedElementId>
      </ManagedElement>
    </config>
  </edit-config>
</rpc>
]]>]]>
<rpc message-id="Closing" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <close-session></close-session>
</rpc>
]]>]]>

"""
    return xml_content

# ==============================================================================
# FUNCIÓN 3: Generar SiteEquipment
# ==============================================================================

def generar_siteequipment(nemonico: str) -> str:
    """
    Genera el archivo 02_{NEMONICO}_SiteEquipment.xml con configuración de hardware
    """
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
       <capabilities>
               <capability>urn:ietf:params:netconf:base:1.0</capability>
               <capability>urn:com:ericsson:ebase:0.1.0</capability>
               <capability>urn:com:ericsson:ebase:1.1.0</capability>
        </capabilities>
</hello>
]]>]]>
<rpc message-id="Create primary FieldReplaceableUnit with ports in the first rpc" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<edit-config>
       <config>
               <ManagedElement>
                       <managedElementId>1</managedElementId>
                       <Equipment>
                               <equipmentId>1</equipmentId>
                               <FieldReplaceableUnit>
                                       <fieldReplaceableUnitId>BB-1</fieldReplaceableUnitId>
                                       <administrativeState>UNLOCKED</administrativeState>
                                       <RiPort>
                                               <riPortId>A</riPortId>
                                       </RiPort>
                                       <RiPort>
                                               <riPortId>B</riPortId>
                                       </RiPort>
                                       <RiPort>
                                               <riPortId>C</riPortId>
                                       </RiPort>
                                       <TnPort>
                                               <tnPortId></tnPortId>
                                       </TnPort>
                                       <EcPort>
                                               <ecPortId>1</ecPortId>
                                               <hubPosition>X</hubPosition>
                                       </EcPort>
                                       <SyncPort>
                                               <syncPortId>1</syncPortId>
                                       </SyncPort>
                               </FieldReplaceableUnit>
                       </Equipment>
                       <NodeSupport>
                               <nodeSupportId>1</nodeSupportId>
                               <MpClusterHandling>
                                       <mpClusterHandlingId>1</mpClusterHandlingId>
                                       <primaryCoreRef>ManagedElement=1,Equipment=1,FieldReplaceableUnit=BB-1</primaryCoreRef>
                               </MpClusterHandling>
                       </NodeSupport>
               </ManagedElement>
       </config>
</edit-config>
</rpc>
]]>]]>
<rpc message-id="Common Support System hardware configuration" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <edit-config>
                <config>
                       <ManagedElement xmlns="urn:com:ericsson:ecim:ComTop">
                                <managedElementId>1</managedElementId>
                                <Equipment>
                                        <equipmentId>1</equipmentId>
                                        <EcBus>
                                                <ecBusId>1</ecBusId>
                                                <ecBusConnectorRef>ManagedElement=1,Equipment=1,FieldReplaceableUnit=BB-1</ecBusConnectorRef>
                                        </EcBus>
                                        <FieldReplaceableUnit>
                                                <fieldReplaceableUnitId>BB-1</fieldReplaceableUnitId>
                                                <positionRef>ManagedElement=1,Equipment=1,Cabinet=1</positionRef>
                                                <EcPort>
                                                        <ecPortId>1</ecPortId>
                                                        <hubPosition>X</hubPosition>
                                                        <ecBusRef>ManagedElement=1,Equipment=1,EcBus=1</ecBusRef>
                                                </EcPort>
                                        </FieldReplaceableUnit>
                                        <FieldReplaceableUnit>
                                                <fieldReplaceableUnitId>SUP</fieldReplaceableUnitId>
                                                <administrativeState>UNLOCKED</administrativeState>
                                                <positionRef>ManagedElement=1,Equipment=1,Cabinet=1</positionRef>
                                                <EcPort>
                                                        <ecPortId>1</ecPortId>
                                                        <cascadingOrder>0</cascadingOrder>
                                                        <hubPosition>NA</hubPosition>
                                                        <ecBusRef>ManagedElement=1,Equipment=1,EcBus=1</ecBusRef>
                                                </EcPort>
                                                <AlarmPort>
                                                        <alarmPortId>1</alarmPortId>
                                                        <administrativeState>UNLOCKED</administrativeState>
                                                        <alarmSlogan>ExternalAlarmSAUAlarmPort1</alarmSlogan>
                                                </AlarmPort>
                                        </FieldReplaceableUnit>
                                        <Cabinet>
                                                <cabinetId>1</cabinetId>
                                                <productData>
                                                        <productionDate>20160229</productionDate>
                                                        <productName>DUS 52 01</productName>
                                                        <productNumber>KDU 137 925/31</productNumber>
                                                        <productRevision>R1E</productRevision>
                                                        <serialNumber>D16S393592</serialNumber>
                                                </productData>
                                        </Cabinet>
                                </Equipment>
                        </ManagedElement>
                </config>
        </edit-config>
</rpc>
]]>]]>

<rpc message-id="Common Support System functional configuration" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
       <edit-config>
                <config>
                        <ManagedElement>
                                <managedElementId>1</managedElementId>
                                <EquipmentSupportFunction>
                                        <equipmentSupportFunctionId>1</equipmentSupportFunctionId>
                                        <supportSystemControl>true</supportSystemControl>
                                        <Climate>
                                                <climateId>1</climateId>
                                                <climateControlMode>NORMAL</climateControlMode>
                                                <controlDomainRef>ManagedElement=1,Equipment=1,Cabinet=1</controlDomainRef>
                                        </Climate>
                                </EquipmentSupportFunction>
                        </ManagedElement>
                </config>
        </edit-config>
</rpc>
]]>]]>
<rpc message-id="Close session" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <close-session />
</rpc>
]]>]]>

"""
    return xml_content
