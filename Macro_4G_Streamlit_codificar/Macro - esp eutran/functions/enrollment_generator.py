# functions/enrollment_generator.py

def generar_create_identity_yml(nemonico: str) -> str:
    """
    Genera el contenido XML para 00_Create_Identity.yml.
    (Aunque la extensión es .yml, el contenido interno es Ericsson XML).
    """
    nemonico_upper = nemonico.upper()
    
    # Contenido XML para el archivo .yml
    content_xml = f"""<Entities xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="EntitiesSchema.xsd">
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
<Name>{nemonico_upper}-oam</Name>
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
<Value>{nemonico_upper}-oam</Value>
</SubjectField>
</Subject>
</EntityInfo>
</Entity>
</Entities>"""
    return content_xml


def generar_lte_enm_xml(nemonico: str, region: str, ip_oam: str) -> str:
    """
    Genera el contenido de comandos CMEDIT para 01_LTE_ENM_Nemonico.xml, 
    reemplazando Nemonico, Region e IP_OAM.
    """
    nemonico_upper = nemonico.upper()
    region_upper = region.upper()
    
    # Contenido del script CMEDIT (texto plano)
    content_cmedit = f"""cmedit create NetworkElement={nemonico_upper} networkElementId={nemonico_upper}, neType="RadioNode",ossPrefix="SubNetwork=ONRM_ROOT_MO,SubNetwork=LTE_Region_{region_upper},MeContext={nemonico_upper}",userlabel="{nemonico_upper}", ossModelIdentity="22.Q2-R53A03", timeZone="UTC" -ns=OSS_NE_DEF -v=2.0.0
cmedit create NetworkElement={nemonico_upper},ComConnectivityInformation=1 ComConnectivityInformationId=1,fileTransferProtocol=SFTP,ftpTlsServerPort=1636,ipAddress="{ip_oam}",port=6513,snmpAgentPort=161,snmpReadCommunity="public",snmpSecurityLevel="NO_AUTH_NO_PRIV",snmpVersion="SNMP_V2C",snmpWriteCommunity="public",transportProtocol="TLS" -ns=COM_MED -version=1.1.0
secadm credentials create --secureusername rbs --secureuserpassword "rbs" --ldapuser disable -n {nemonico_upper}
cmedit set NetworkElement={nemonico_upper},CmNodeHeartbeatSupervision=1 active=true
cmedit set NetworkElement={nemonico_upper},InventorySupervision=1 active=true
cmedit set NetworkElement={nemonico_upper},PmFunction=1 pmEnabled=true --force
cmedit set NetworkElement={nemonico_upper},FmFunction=1 subscriptionState=ENABLED
cmedit action NetworkElement={nemonico_upper},CmFunction=1 sync
cmedit set NetworkElement={nemonico_upper},CmNodeHeartbeatSupervision=1 active=true"""
    return content_cmedit