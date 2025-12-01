from typing import Dict, Any

# functions_5G/enrollment_generator_5G.py
# =====================================================================
# Generador de archivos de Enrollment para 5G NR
# =====================================================================
# AUTOR: PIERO LEDESMA
# =====================================================================

def generar_create_identity_xml_5g(nemonico: str) -> str:
    """
    Genera el contenido XML para 00_Create_Identity.xml para 5G NR.
    
    Args:
        nemonico: Nemónico del sitio (ej: GLA781)
        
    Returns:
        str: Contenido XML del archivo de identidad
    """
    nemonico_upper = nemonico.upper()
    
    # Contenido XML con la declaración XML incluida (Usando la versión actualizada que proporcionaste)
    content_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Entities xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="EntitiesSchema.xsd">
<Entity>
    <PublishCertificatetoTDPS>true</PublishCertificatetoTDPS>
 <EntityProfile Name="DUSGen2OAM_CHAIN_EP" />
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
</Entities>
"""
    return content_xml


def generar_cmedit_enrollment_5g(nemonico: str, region: str, wsh_data: Dict[str, Any]) -> str:
    """
    Genera el contenido del script CMEDIT para Enrollment. (MML Script - NO XML)
    
    Args:
        nemonico: Nemónico del sitio
        region: Región (ej: X)
        wsh_data: Diccionario con datos del WSH (contiene IP_OAM)
        
    Returns:
        str: Contenido del script CMEDIT (texto plano)
    """
    nemonico_upper = nemonico.upper()
    region_upper = region.upper()
    
    # Extraer la IP OAM del diccionario de datos (o usar 0.0.0.0 si falla)
    ip_oam = wsh_data.get('IP_OAM', '0.0.0.0')
    
    # Contenido del script CMEDIT para 5G NR (TEXTO PLANO MML)
    content_cmedit = f"""cmedit create NetworkElement={nemonico_upper} networkElementId={nemonico_upper}, neType="RadioNode",ossPrefix="SubNetwork=ONRM_ROOT_MO,SubNetwork=NR_Region_{region_upper},MeContext={nemonico_upper}",userlabel="{nemonico_upper}", ossModelIdentity="22.Q2-R53A03", timeZone="UTC" -ns=OSS_NE_DEF -v=2.0.0 
cmedit create NetworkElement={nemonico_upper},ComConnectivityInformation=1 ComConnectivityInformationId=1,fileTransferProtocol=SFTP,ftpTlsServerPort=1636,ipAddress="{ip_oam}",port=6513,snmpAgentPort=161,snmpReadCommunity="public",snmpSecurityLevel="NO_AUTH_NO_PRIV",snmpVersion="SNMP_V2C",snmpWriteCommunity="public",transportProtocol="TLS" -ns=COM_MED -version=1.1.0 
secadm credentials create --secureusername rbs --secureuserpassword "rbs" --ldapuser disable -n {nemonico_upper}
cmedit set NetworkElement={nemonico_upper} saUserLabel="{nemonico_upper}"
cmedit set NetworkElement={nemonico_upper},CmNodeHeartbeatSupervision=1 active=true 
cmedit set NetworkElement={nemonico_upper},InventorySupervision=1 active=true
cmedit set NetworkElement={nemonico_upper},PmFunction=1 pmEnabled=true --force
cmedit set NetworkElement={nemonico_upper},FmFunction=1 subscriptionState=ENABLED
cmedit action NetworkElement={nemonico_upper},CmFunction=1 sync
cmedit set NetworkElement={nemonico_upper},CmNodeHeartbeatSupervision=1 active=true
"""
    return content_cmedit