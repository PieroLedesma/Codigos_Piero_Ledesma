def generate_create_identity_xml(nemonico):
    """
    Genera el archivo 00_Create_Identity.xml para enrollment.
    """
    xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<Entities xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="EntitiesSchema.xsd">
<Entity>
<PublishCertificatetoTDPS>true</PublishCertificatetoTDPS>
<EntityProfile Name="DUSGen2OAM_CHAIN_EP"/>
<KeyGenerationAlgorithm>
<Name>RSA</Name>
<KeySize>2048</KeySize>
</KeyGenerationAlgorithm>
<Category>
<Modifiable>true</Modifiable>
<Name>NODE-OAM</Name>
</Category>
<EntityInfo>
<Name>{nemonico}-oam</Name>
<Subject>
<SubjectField>
<Type>ORGANIZATION</Type>
<Value>Entel</Value>
</SubjectField>
<SubjectField>
<Type>ORGANIZATION_UNIT</Type>
<Value>Entel</Value>
</SubjectField>
<SubjectField>
<Type>COUNTRY_NAME</Type>
<Value>CL</Value>
</SubjectField>
<SubjectField>
<Type>COMMON_NAME</Type>
<Value>{nemonico}-oam</Value>
</SubjectField>
</Subject>
</EntityInfo>
</Entity>
</Entities>'''
    
    filename = "00_Create_Identity.xml"
    return True, xml_content, filename


def generate_enm_xml(nemonico, rnc_value, ip_oam):
    """
    Genera el archivo 01_ENM_{Nemonico}.xml para enrollment.
    """
    xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
 cmedit create NetworkElement={nemonico} networkElementId={nemonico},neType=RadioNode,ossModelIdentity="22.Q2-R53A03",ossPrefix="SubNetwork=ONRM_ROOT_MO,SubNetwork={rnc_value},MeContext={nemonico}",userlabel="{nemonico}",timeZone="Etc/GMT" -ns=OSS_NE_DEF -v=2.0.0
 cmedit create NetworkElement={nemonico},ComConnectivityInformation=1 ComConnectivityInformationId=1,fileTransferProtocol=SFTP,ftpTlsServerPort=1636,ipAddress="{ip_oam}",port=6513,snmpAgentPort=161,snmpReadCommunity="public",snmpSecurityLevel="NO_AUTH_NO_PRIV",snmpVersion="SNMP_V2C",snmpWriteCommunity="public",transportProtocol="TLS" -ns=COM_MED -version=1.1.0 
 cmedit set NetworkElement={nemonico} controllingRnc="NetworkElement={rnc_value}"
 secadm credentials create --secureusername rbs --secureuserpassword "rbs" --ldapuser disable -n {nemonico}
 cmedit set NetworkElement={nemonico},CmNodeHeartbeatSupervision=1 active=true 
 cmedit set NetworkElement={nemonico},InventorySupervision=1 active=true
 cmedit set NetworkElement={nemonico},PmFunction=1 pmEnabled=true --force
 cmedit set NetworkElement={nemonico},FmFunction=1 subscriptionState=ENABLED
 cmedit action NetworkElement={nemonico},CmFunction=1 sync
 cmedit get {nemonico} CmFunction.syncstatus
 cmedit set NetworkElement={nemonico}, CmNodeHeartbeatSupervision=1 active=true
'''
    
    filename = f"01_ENM_{nemonico}.xml"
    return True, xml_content, filename
