Attribute VB_Name = "FORM_3G_IP"
Attribute VB_Base = "0{C92E03DB-BC77-4A22-BE56-25C461DA53B6}{9E41751E-9441-4991-8CDA-BF967ACDC0DF}"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Attribute VB_TemplateDerived = False
Attribute VB_Customizable = False
Sub LeerArchivoExcel()

    Dim rutaArchivo As String
    Dim libro As Workbook
    Dim hoja As Worksheet
    Dim carpeta As String
    
    Dim IUB As String
    Dim RBSID As String
    Dim Release As String
    Dim SYNC_1 As String
    Dim SYNC_2 As String
    Dim IP_NTP_1 As String
    Dim IP_NTP_2 As String
        
    Dim columna_IP_OAM As Range
    Dim columna_MASK As Range
    Dim columna_Nemonico As Range
    Dim columna_VLAN_OAM As Range
    Dim columna_DGW_Iub_IP As Range
    Dim columna_VLAN_IUB As Range
    Dim columna_DGW_Iub_IP_OAM As Range
    
    Dim encabezado_IP_OAM As String
    Dim encabezado_MASK As String
    Dim encabezado_Nemonico As String
    Dim encabezado_IP_IUB As String
    Dim encabezado_Vlan_OAM As String
    Dim encabezado_DGW_Iub_IP As String
    Dim encabezado_VLAN_IUB As String
    Dim encabezado_DGW_Iub_IP_OAM As String
    Dim encabezado_Proyecto As String
    Dim encabezado_PE As String
        
    
    Dim IP_OAM As Variant
    Dim MASK As Variant
    Dim NEMONICO As Variant
    Dim IP_TRAFICO As Variant
    Dim VLAN_OAM As Variant
    Dim VLAN_IUB As Variant
    Dim DGW_OAM_LTE As Variant
    Dim DGW_TRAFICO_LTE As Variant
    
    

    IUB = TextBox_IUB.Text
    RBSID = TextBox_RBSID.Text
    MAXHRATE = TextBox_MAXHRATE.Text
    SYNC_1 = ComboBox_SYNC_1.Value
    SYNC_2 = ComboBox_SYNC_2.Value
    IP_NTP_1 = TextBox_IP_1.Text
    IP_NTP_2 = TextBox_IP_1.Text
    
    
    
    ' Establecer la ruta del archivo Excel que deseas leer
    rutaArchivo = Application.GetOpenFilename("Archivos de Excel (*.xls;*.xlsx), *.xls;*.xlsx")
    
    ' Abrir el archivo Excel
    Set libro = Workbooks.Open(rutaArchivo)
    
    ' Especificar la hoja que contiene los datos (cambiar "2G_3G" si es necesario)
    Set hoja = libro.Worksheets("2G-3G")
    
    ' Especificar el encabezado a buscar
    encabezado_IP_OAM = "IP OAM"
    encabezado_MASK = "Mask"
    encabezado_Nemonico = "Nemonico"
    encabezado_IP_IUB = "IP Iub_IP Control"
    encabezado_Vlan_OAM = "Vlan OAM"
    encabezado_DGW_Iub_IP = "DGW Iub_IP"
    encabezado_VLAN_IUB = "Vlan Iub"
    encabezado_DGW_Iub_IP_OAM = "DGW Iub_IP_OAM"
    encabezado_Proyecto = "Proyecto"
    encabezado_PE = "Pto Agregación Definitiva"
    
    ' Buscar el encabezado en la primera fila (fila 1) de la hoja
    Set columna_IP_OAM = hoja.Rows(1).Find(encabezado_IP_OAM, LookIn:=xlValues, LookAt:=xlWhole)
    Set columna_MASK = hoja.Rows(1).Find(encabezado_MASK, LookIn:=xlValues, LookAt:=xlWhole)
    Set columna_Nemonico = hoja.Rows(1).Find(encabezado_Nemonico, LookIn:=xlValues, LookAt:=xlWhole)
    Set columna_IP_IUB = hoja.Rows(1).Find(encabezado_IP_IUB, LookIn:=xlValues, LookAt:=xlWhole)
    Set columna_VLAN_OAM = hoja.Rows(1).Find(encabezado_Vlan_OAM, LookIn:=xlValues, LookAt:=xlWhole)
    Set columna_DGW_Iub_IP = hoja.Rows(1).Find(encabezado_DGW_Iub_IP, LookIn:=xlValues, LookAt:=xlWhole)
    Set columna_VLAN_IUB = hoja.Rows(1).Find(encabezado_VLAN_IUB, LookIn:=xlValues, LookAt:=xlWhole)
    Set columna_DGW_Iub_IP_OAM = hoja.Rows(1).Find(encabezado_DGW_Iub_IP_OAM, LookIn:=xlValues, LookAt:=xlWhole)
    Set columna_Proyecto = hoja.Rows(1).Find(encabezado_Proyecto, LookIn:=xlValues, LookAt:=xlWhole)
    Set columna_PE = hoja.Rows(1).Find(encabezado_PE, LookIn:=xlValues, LookAt:=xlWhole)
    
    
    ' Si se encontró el encabezado, obtener el valor de la celda en la fila 2 (fila de datos)
    IP_OAM = hoja.Cells(2, columna_IP_OAM.Column).Value
    MASK = hoja.Cells(2, columna_MASK.Column).Value
    NEMONICO = hoja.Cells(2, columna_Nemonico.Column).Value
    IP_TRAFICO = hoja.Cells(2, columna_IP_IUB.Column).Value
    VLAN_OAM = hoja.Cells(2, columna_VLAN_OAM.Column).Value
    VLAN_IUB = hoja.Cells(2, columna_VLAN_IUB.Column).Value
    DGW_Iub_IP_OAM = hoja.Cells(2, columna_DGW_Iub_IP_OAM.Column).Value
    DGW_Iub_IP = hoja.Cells(2, columna_DGW_Iub_IP.Column).Value

    
    
    ' Mostrar Mensaje
    cantidadColumnas = ActiveSheet.UsedRange.Columns.Count
    cantidadFilas = ActiveSheet.UsedRange.Rows.Count
    MsgBox "NEMONICO :" & NEMONICO & vbCrLf & "IUB :" & IUB & vbCrLf & "RBSID :" & RBSID & vbCrLf & "MAXHRATE :" & MAXHRATE & vbCrLf & "SYNC_REF 1 :" & SYNC_1 & vbCrLf & "SYNC_REF 2 :" & SYNC_2 & vbCrLf & "IP_OAM :" & IP_OAM & vbCrLf & "Mascara :" & MASK & vbCrLf & "DGW_Iub_IP_OAM :" & DGW_Iub_IP_OAM & vbCrLf & "IP_IUB_CONTROL :" & IP_TRAFICO & vbCrLf & "DGW_Iub_IP :" & DGW_Iub_IP & vbCrLf & "VLAN_OAM :" & VLAN_OAM & vbCrLf & "VLAN_IUB :" & VLAN_IUB & vbCrLf & "CAntidad de columnas :" & cantidadColumnas & "cantidad de filas:" & cantidadFilas
    
    For i = 2 To cantidadFilas
    
    NEM = hoja.Cells(i, columna_Nemonico.Column).Value
    IP = hoja.Cells(i, columna_IP_OAM.Column).Value
    PROYECTO = hoja.Cells(i, columna_Proyecto.Column).Value
    PE = hoja.Cells(i, columna_PE.Column).Value
    
    MsgBox (NEM & vbCrLf & IP & vbCrLf & PROYECTO & vbCrLf & PE)
    Next i

    
    ' Cerrar el archivo Excel
    libro.Close SaveChanges:=False

    ' Liberar recursos
    Set hoja = Nothing
    Set libro = Nothing
    
    ' Crea carpeta
    Ruta = "C:\Generador_2\" & NEMONICO
       
    If Dir(Ruta, vbDirectory) = "" Then
    MkDir Ruta
    End If
    
    Ruta_Archivo = Ruta & "\"
    
    rutaArchivo_S1 = Ruta_Archivo & "00.TRUN1_GESTION_OPTICA_" & NEMONICO & ".mo"
    rutaArchivo_S2 = Ruta_Archivo & "01.RUN_DELETE_IUB_" & NEMONICO & ".mo"
    rutaArchivo_S3 = Ruta_Archivo & "02.TRUNI_CREATE_IUB_" & NEMONICO & ".mo"

    archivoS1 = FreeFile
    Open rutaArchivo_S1 For Output As archivoS1
    
    Print #archivoS1, "ACTION"
    Print #archivoS1, "("
    Print #archivoS1, "  actionName assignIpAddress"
    Print #archivoS1, "  mo ""ManagedElement=1,IpOam=1,Ip=1,IpHostLink=1"""
    Print #archivoS1, "  exception none"
    Print #archivoS1, "  nrOfParameters 6"
    Print #archivoS1, "  String """ & IP_OAM; """"                             'IP OAM
    Print #archivoS1, "  Integer 26"
    Print #archivoS1, "  String """ & DGW_Iub_IP_OAM; """"                     'DGW IUB OAM IP
    Print #archivoS1, "  String ""0.0.0.0"""
    Print #archivoS1, "  String ""0.0.0.0"""
    Print #archivoS1, "  String ""0.0.0.0"""
    Print #archivoS1, "    returnValue none"
    Print #archivoS1, ")"
    Print #archivoS1, "ACTION"
    Print #archivoS1, "("
    Print #archivoS1, "  actionName addStaticRoute"
    Print #archivoS1, "  mo ""ManagedElement=1,IpOam=1,Ip=1,IpRoutingTable=1"""
    Print #archivoS1, "  exception none"
    Print #archivoS1, "  nrOfParameters 5"
    Print #archivoS1, "  String ""0.0.0.0"""
    Print #archivoS1, "  String ""0.0.0.0"""
    Print #archivoS1, "  String """ & DGW_Iub_IP; """"                         'DGW IUB IP
    Print #archivoS1, "  Integer 100"
    Print #archivoS1, "  Boolean 0"
    Print #archivoS1, "    returnValue none"
    Print #archivoS1, ")"
    Print #archivoS1, "ACTION"
    Print #archivoS1, "("
    Print #archivoS1, "  actionName addStaticRoute"
    Print #archivoS1, "  mo ""ManagedElement=1,IpOam=1,Ip=1,IpRoutingTable=1"""
    Print #archivoS1, "  exception none"
    Print #archivoS1, "  nrOfParameters 5"
    Print #archivoS1, "  String ""0.0.0.0"""
    Print #archivoS1, "  String ""0.0.0.0"""
    Print #archivoS1, "  String """ & DGW_Iub_IP_OAM; """"                      'DGW IUB OAM IP
    Print #archivoS1, "  Integer 100"
    Print #archivoS1, "  Boolean 0"
    Print #archivoS1, "    returnValue none"
    Print #archivoS1, ")"
    Print #archivoS1, "SET"
    Print #archivoS1, "("
    Print #archivoS1, "   mo ""ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1,IpInterface=2"""
    Print #archivoS1, "   exception none"
    Print #archivoS1, "   vid Integer " & VLAN_OAM; ""                           'VLAN IUB OAM
    Print #archivoS1, ")"
    Print #archivoS1, "SET"
    Print #archivoS1, "("
    Print #archivoS1, "   mo ""ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1,IpInterface=1"""
    Print #archivoS1, "   exception none"
    Print #archivoS1, "   vid Integer " & VLAN_IUB; ""                                'Vlan IUB
    Print #archivoS1, ")"
    Close archivoS1

    archivoS2 = FreeFile
    Open rutaArchivo_S2 For Output As archivoS2
    
    Print #archivoS2, ""
    Print #archivoS2, "lt all"
    Print #archivoS2, "confb+"
    Print #archivoS2, "confd+"
    Print #archivoS2, "gs+"
    Print #archivoS2, "rdel Nbap"
    Print #archivoS2, "del NodeBFunction=1,IUB=IUB"
    Print #archivoS2, "bl IpAccessHostEt"
    Print #archivoS2, "bl IpSyncRef"
    Print #archivoS2, "rdel Sctp=1"
    Print #archivoS2, "actc Synchronization removeSyncRefResource"
    Print #archivoS2, "IpSystem=1,IpAccessHostEt=1,IpSyncRef=" & SYNC_1; ""
    Print #archivoS2, "actc Synchronization removeSyncRefResource"
    Print #archivoS2, "IpSystem=1,IpAccessHostEt=1,IpSyncRef=" & SYNC_2; ""
    Print #archivoS2, "del IpSystem=1,IpAccessSctp=IUB"
    Print #archivoS2, "rdel IpSyncRef"
    Print #archivoS2, "del IpSystem=1,IpAccessHostEt=1"
    Print #archivoS2, "del IpInterface=1"
    Print #archivoS2, "confb-"
    Print #archivoS2, "confd+"
    Print #archivoS2, "gs-"
    Close archivoS2
    
    archivoS3 = FreeFile
    Open rutaArchivo_S3 For Output As archivoS2
    

Print #archivoS3, ""
Print #archivoS3, ""
Print #archivoS3, "CREATE"
Print #archivoS3, "("
Print #archivoS3, " parent ""ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"""
Print #archivoS3, " identity ""1"""
Print #archivoS3, " moType IpInterface"
Print #archivoS3, " exception none"
Print #archivoS3, " nrOfAttributes 10"
Print #archivoS3, " networkPrefixLength Integer 26"
Print #archivoS3, " defaultRouter0 String """ & DGW_Iub_IP; """"           'DGW IUB IP
Print #archivoS3, " defaultRouter1 String ""0.0.0.0"""
Print #archivoS3, " defaultRouter2 String ""0.0.0.0"""
Print #archivoS3, " ownIpAddressActive String ""0.0.0.0"""
Print #archivoS3, " mtu Integer 1500"
Print #archivoS3, " rps Boolean false"
Print #archivoS3, " TrafficType Integer 7"
Print #archivoS3, " vLan Boolean true"
Print #archivoS3, " vid Integer " & VLAN_IUB; ""                                'Vlan IUB
Print #archivoS3, ")"
Print #archivoS3, "CREATE"
Print #archivoS3, "("
Print #archivoS3, "   parent ""ManagedElement=1,IpSystem=1"""
Print #archivoS3, "  identity ""1"""
Print #archivoS3, "  moType IpAccessHostEt"
Print #archivoS3, "  exception none"
Print #archivoS3, "  nrOfAttributes 4"
Print #archivoS3, "  ipAddress String """ & IP_TRAFICO; """"              'IP IUB CONROL
Print #archivoS3, "  ipDefaultTtl Integer 64"
Print #archivoS3, "  ntpServerMode Integer 0"
Print #archivoS3, "  ipInterfaceMoRef Reference ""ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1,IpInterface=1"""
Print #archivoS3, ")"
Print #archivoS3, "CREATE"
Print #archivoS3, "("
Print #archivoS3, "   parent ""ManagedElement=1,IpSystem=1"""
Print #archivoS3, "  identity ""Iub"""
Print #archivoS3, "  moType IpAccessSctp"
Print #archivoS3, "  exception none"
Print #archivoS3, "  nrOfAttributes 1"
Print #archivoS3, "      ipAccessHostEtRef1 Reference ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1"""
Print #archivoS3, ")"
Print #archivoS3, "CREATE"
Print #archivoS3, "("
Print #archivoS3, "   parent ""ManagedElement=1,TransportNetwork=1"""
Print #archivoS3, "   identity ""1"""
Print #archivoS3, "   moType Sctp"
Print #archivoS3, "   exception none"
Print #archivoS3, "   nrOfAttributes 37"
Print #archivoS3, "   allowedIncrementCookieLife Integer 30"
Print #archivoS3, "   associationMaxRtx Integer 8"
Print #archivoS3, "   bundlingActivated Integer 1"
Print #archivoS3, "   bundlingTimer Integer 10"
Print #archivoS3, "   heartbeatInterval Integer 30"
Print #archivoS3, "   heartbeatMaxBurst Integer 0"
Print #archivoS3, "   heartbeatPathProbingInterval Integer 500"
Print #archivoS3, "   heartbeatStatus Boolean true"
Print #archivoS3, "   initialAdRecWin Integer 32768"
Print #archivoS3, "   initialRto Integer 20"
Print #archivoS3, "   intervalOobPkts Integer 3600"
Print #archivoS3, "   ipAccessSctpRef Ref ""ManagedElement=1,IpSystem=1,IpAccessSctp=Iub"""
Print #archivoS3, "   keyChangePeriod Integer 4"
Print #archivoS3, "   mBuffer Integer 256"
Print #archivoS3, "   maxBurst Integer 4"
Print #archivoS3, "   maxIncomingStream Integer 17"
Print #archivoS3, "   maxInitialRtrAtt Integer 8"
Print #archivoS3, "   maxOutgoingStream Integer 17"
Print #archivoS3, "   maxShutDownRtrAtt Integer 5"
Print #archivoS3, "   maxUserDataSize Integer 1480"
Print #archivoS3, "   maximumRto Integer 40"
Print #archivoS3, "   minimumRto Integer 10"
Print #archivoS3, "   nPercentage Integer 85"
Print #archivoS3, "   nThreshold Integer 192"
Print #archivoS3, "   numberOfAssociations Integer 2"
Print #archivoS3, "   pathMaxRtx Integer 4"
Print #archivoS3, "   pathSelection Integer 0"
Print #archivoS3, "   potentiallyFailedMaxRtx Integer 4"
Print #archivoS3, "   rpuId Ref ""ManagedElement=1,SwManagement=1,ReliableProgramUniter=sctp_host"""
Print #archivoS3, "   rtoAlphaIndex Integer 3"
Print #archivoS3, "   rtoBetaIndex Integer 2"
Print #archivoS3, "   sctpAssocDeleteTimeout Integer 168"
Print #archivoS3, "   switchbackMaxThreshold Integer 65535"
Print #archivoS3, "   switchbackMinThreshold Integer 1"
Print #archivoS3, "   switchbackMode Integer 1"
Print #archivoS3, "   tSack Integer 4"
Print #archivoS3, "   validCookieLife Integer 60"
Print #archivoS3, ")"
Print #archivoS3, "CREATE"
Print #archivoS3, "("
Print #archivoS3, "   parent ""ManagedElement=1,NodeBFunction=1"""
Print #archivoS3, "   identity """ & IUB; """"                                         'IUB
Print #archivoS3, "   moType Iub"
Print #archivoS3, "   exception none"
Print #archivoS3, "   nrOfAttributes 5"
Print #archivoS3, "        rbsId Integer " & RBSID; ""                               'RBSID
Print #archivoS3, "        userLabel String """ & NEMONICO; """"                     'Nemonico
Print #archivoS3, "        userPlaneIpResourceRef Ref ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1"""
Print #archivoS3, "        controlPlaneTransportOption Struct"
Print #archivoS3, "          nrOfElements 2"
Print #archivoS3, "            atm Boolean false "
Print #archivoS3, "            ipV4 Boolean true"
Print #archivoS3, "        userPlaneTransportOption Struct"
Print #archivoS3, "          nrOfElements 2"
Print #archivoS3, "            atm Boolean false "
Print #archivoS3, "            ipV4 Boolean true"
Print #archivoS3, ")"
Print #archivoS3, "CREATE"
Print #archivoS3, "("
Print #archivoS3, "   parent ""ManagedElement=1,NodeBFunction=1,Iub=" & IUB; """"            'IUB
Print #archivoS3, "   identity ""1"""
Print #archivoS3, "   moType NbapDedicated"
Print #archivoS3, "   exception none"
Print #archivoS3, "   nrOfAttributes 2"
Print #archivoS3, "   l2EstablishReqRetryT Integer 1"
Print #archivoS3, "   l2EstablishSupervisionT Integer 30"
Print #archivoS3, ")"
Print #archivoS3, "CREATE"
Print #archivoS3, "("
Print #archivoS3, "   parent ""ManagedElement=1,NodeBFunction=1,Iub=" & IUB; """"                'IUB
Print #archivoS3, "   identity ""1"""
Print #archivoS3, "   moType NbapCommon"
Print #archivoS3, "   exception none"
Print #archivoS3, "   nrOfAttributes 4"
Print #archivoS3, "   auditRetransmissionT Integer 5"
Print #archivoS3, "   l2EstablishReqRetryT Integer 1"
Print #archivoS3, "   l2EstablishSupervisionT Integer 30"
Print #archivoS3, "   l3EstablishSupervisionT Integer 30"
Print #archivoS3, ")"
Print #archivoS3, "SET"
Print #archivoS3, "("
Print #archivoS3, "   mo ""ManagedElement=1,NodeBFunction=1,Iub=" & IUB; ",IubDataStreams=1"""          'IUB
Print #archivoS3, "   exception none"
Print #archivoS3, "   hsDataFrameDelayThreshold Integer 60"
Print #archivoS3, ")"
Print #archivoS3, "SET"
Print #archivoS3, "("
Print #archivoS3, "   mo ""ManagedElement=1,NodeBFunction=1,Iub=" & IUB; ",IubDataStreams=1"""          'IUB
Print #archivoS3, "   exception none"
Print #archivoS3, "   maxHsRate Integer " & MAXHRATE; ""            'MaxHrate
Print #archivoS3, ")"
Print #archivoS3, "SET"
Print #archivoS3, "("
Print #archivoS3, "   mo ""ManagedElement=1,NodeBFunction=1,Iub=" & IUB; ",IubDataStreams=1"""          'IUB
Print #archivoS3, "   exception none"
Print #archivoS3, "   schHsFlowControlOnOff Array Integer 160"
Print #archivoS3, "1"
Print #archivoS3, "1"
Print #archivoS3, "1"
Print #archivoS3, "1"
Print #archivoS3, "0"
Print #archivoS3, "0"
Print #archivoS3, "1"
Print #archivoS3, "0"
Print #archivoS3, "0"
Print #archivoS3, "0"
Print #archivoS3, "0"
Print #archivoS3, "0"
Print #archivoS3, "0"
Print #archivoS3, "0"
Print #archivoS3, "0"
Print #archivoS3, ")"
Print #archivoS3, "CREATE"
Print #archivoS3, "("
Print #archivoS3, "   parent ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1"""
Print #archivoS3, "   identity ""7"""
Print #archivoS3, "   moType IpSyncRef"
Print #archivoS3, "   exception none"
Print #archivoS3, "   nrOfAttributes 2"
Print #archivoS3, "    userLabel String ""IP NTP Sync Server 1"""
Print #archivoS3, "    ntpServerIpAddress String """ & IP_NTP_1; """"         'IP_NTP_1
Print #archivoS3, ")"
Print #archivoS3, "CREATE"
Print #archivoS3, "("
Print #archivoS3, "   parent ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1"""
Print #archivoS3, "   identity ""8"""
Print #archivoS3, "   moType IpSyncRef"
Print #archivoS3, "   exception none"
Print #archivoS3, "   nrOfAttributes 2"
Print #archivoS3, "    userLabel String ""IP NTP Sync Server 2"""
Print #archivoS3, "    ntpServerIpAddress String """ & IP_NTP_2; """"       'IP_NTP_2
Print #archivoS3, ")"
Print #archivoS3, "ACTION"
Print #archivoS3, "("
Print #archivoS3, "   actionName addSyncRefResource"
Print #archivoS3, "   mo ""ManagedElement=1,TransportNetwork=1,Synchronization=1"""
Print #archivoS3, "   exception none"
Print #archivoS3, "   nrOfParameters 2 "
Print #archivoS3, "    Reference ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef=" & SYNC_1; """"  'SYNCREF
Print #archivoS3, "    Integer 1"
Print #archivoS3, "     returnValue none"
Print #archivoS3, ")"
Print #archivoS3, "ACTION"
Print #archivoS3, "("
Print #archivoS3, "   actionName addSyncRefResource"
Print #archivoS3, "   mo ""ManagedElement=1,TransportNetwork=1,Synchronization=1"""
Print #archivoS3, "   exception none"
Print #archivoS3, "   nrOfParameters 2 "
Print #archivoS3, "    Reference ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef=" & SYNC_2; """"  'SYNCREF
Print #archivoS3, "    Integer 2"
Print #archivoS3, ")     returnValue none"
Print #archivoS3, ")"
Print #archivoS3, "SET"
Print #archivoS3, "("
Print #archivoS3, "  mo ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef=" & SYNC_1; """"  'SYNCREF
Print #archivoS3, "   exception none"
Print #archivoS3, "   administrativeState Integer 1"
Print #archivoS3, ")"
Print #archivoS3, "SET"
Print #archivoS3, "("
Print #archivoS3, "  mo ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef=" & SYNC_2; """"  'SYNCREF
Print #archivoS3, "   exception none"
Print #archivoS3, "   administrativeState Integer 1"
Print #archivoS3, ")"
Print #archivoS3, "SET"
Print #archivoS3, "("
Print #archivoS3, "  mo ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1"""
Print #archivoS3, "   exception none"
Print #archivoS3, "   administrativeState Integer 1"
Print #archivoS3, ")"
Print #archivoS3, ""
Print #archivoS3, ""
Print #archivoS3, "/////////////////////////////////////"
Print #archivoS3, "// Definition NodeBFeature"
Print #archivoS3, "/////////////////////////////////////"
Print #archivoS3, ""
Print #archivoS3, "SET"
Print #archivoS3, "("
Print #archivoS3, "mo ""ManagedElement=1,NodeBFunction=1"""
Print #archivoS3, "exception none"
Print #archivoS3, "nbapDscp Integer 40"
Print #archivoS3, ")"
Print #archivoS3, "SET"
Print #archivoS3, "("
Print #archivoS3, "mo ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1"""
Print #archivoS3, "exception none"
Print #archivoS3, "ntpDscp Integer 46"
Print #archivoS3, ")"
Print #archivoS3, "///////////////////////"
Print #archivoS3, "// Queue Q0 ( 0,22 )"
Print #archivoS3, "///////////////////////"
Print #archivoS3, "ACTION"
Print #archivoS3, "("
Print #archivoS3, "actionName setDscpPbit"
Print #archivoS3, "mo ""ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"""
Print #archivoS3, "exception none"
Print #archivoS3, "nrOfParameters 2"
Print #archivoS3, "   Integer ""22"" //dscp"
Print #archivoS3, "   Integer ""1""  //pbit"
Print #archivoS3, "returnValue none"
Print #archivoS3, ")"
Print #archivoS3, "/////////////////////////"
Print #archivoS3, "// Queue Q1 ( 16,18,20,26,28 )"
Print #archivoS3, "/////////////////////////"
Print #archivoS3, "ACTION"
Print #archivoS3, "("
Print #archivoS3, "actionName setDscpPbit"
Print #archivoS3, "mo ""ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"""
Print #archivoS3, "exception none"
Print #archivoS3, "nrOfParameters 2"
Print #archivoS3, "   Integer ""16"" //dscp"
Print #archivoS3, "   Integer ""3""  //pbit"
Print #archivoS3, "returnValue none"
Print #archivoS3, ")"
Print #archivoS3, "ACTION"
Print #archivoS3, "("
Print #archivoS3, "actionName setDscpPbit"
Print #archivoS3, "mo ""ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"""
Print #archivoS3, "exception none"
Print #archivoS3, "nrOfParameters 2"
Print #archivoS3, "   Integer ""18"" //dscp"
Print #archivoS3, "   Integer ""3""  //pbit"
Print #archivoS3, "returnValue none"
Print #archivoS3, ")"
Print #archivoS3, "ECHO ""ACTION - ConfigurationVersion Creation"""
Print #archivoS3, "ACTION"
Print #archivoS3, "("
Print #archivoS3, "actionName create"
Print #archivoS3, "mo ""ManagedElement=1,SwManagement=1,ConfigurationVersion=1"""
Print #archivoS3, "exception none"
Print #archivoS3, "nrOfParameters 5"
Print #archivoS3, "String ""CAMBIO_IP"""
Print #archivoS3, "String ""CAMBIO_IP"""
Print #archivoS3, "Integer 5"
Print #archivoS3, "String ""user"""
Print #archivoS3, "String ""CV Startable"""
Print #archivoS3, "returnValue none"
Print #archivoS3, ")"
Print #archivoS3, "ECHO ""Action - setStartable ConfigurationVersion"""
Print #archivoS3, "ACTION"
Print #archivoS3, "("
Print #archivoS3, "actionName setStartable"
Print #archivoS3, "mo ""ManagedElement=1,SwManagement=1,ConfigurationVersion=1"""
Print #archivoS3, "exception none"
Print #archivoS3, "nrOfParameters 1"
Print #archivoS3, "String ""CAMBIO_IP"""
Print #archivoS3, "returnValue none"
Print #archivoS3, ")"

    Close archivoS3
    
End Sub
    
Private Sub ComboBox_SYNC_Change()

End Sub


Private Sub BUSCAR_Click()

    LeerArchivoExcel

End Sub


Private Sub ComboBox_SYNC_1_Change()

End Sub


Private Sub IUB_TEXT_Click()

End Sub


Private Sub TextBox_IUB_Change()

End Sub

Private Sub TextBox_MAXHRATE_Change()

End Sub

Private Sub UserForm_Initialize()

With Me.ComboBox_SYNC_1
    .ShowDropButtonWhen = fmShowDropButtonWhenAlways
    .AddItem "1"
    .AddItem "7"
End With

With Me.ComboBox_SYNC_2
    .ShowDropButtonWhen = fmShowDropButtonWhenAlways
    .AddItem "2"
    .AddItem "8"
End With

End Sub



