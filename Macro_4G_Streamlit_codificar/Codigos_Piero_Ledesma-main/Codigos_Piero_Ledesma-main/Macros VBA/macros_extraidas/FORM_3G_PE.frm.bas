Attribute VB_Name = "FORM_3G_PE"
Attribute VB_Base = "0{4FA46C58-6255-4559-BF3B-3D9C14F9F4BD}{837B6BA8-E086-4864-AA29-F2E6FF976C0D}"
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
    
    rutaArchivo_S1 = Ruta_Archivo & "00.TRUN1_GESTION_IP_" & NEMONICO & ".mo"
    rutaArchivo_S2 = Ruta_Archivo & "01.TRUNI_CREATE_IUB_" & NEMONICO & ".mo"

    archivoS1 = FreeFile
    Open rutaArchivo_S1 For Output As archivoS1
    
    Print #archivoS1,
    Print #archivoS1, "ACTION"
    Print #archivoS1, "("
    Print #archivoS1, "actionName removeSyncRefResource"
    Print #archivoS1, "mo ""ManagedElement=1,TransportNetwork=1,Synchronization=1"""
    Print #archivoS1, "exception none"
    Print #archivoS1, "nrOfParameters 1"
    Print #archivoS1, "Reference ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef=" & SYNC_1; """"  'SYNCREF 1
    Print #archivoS1, "returnValue none"
    Print #archivoS1, ")"
    Print #archivoS1, ""
    Print #archivoS1, "ACTION"
    Print #archivoS1, "("
    Print #archivoS1, "actionName removeSyncRefResource"
    Print #archivoS1, "mo ""ManagedElement=1,TransportNetwork=1,Synchronization=1"""
    Print #archivoS1, "exception none"
    Print #archivoS1, "nrOfParameters 1"
    Print #archivoS1, "Reference ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef=" & SYNC_2; """"  'SYNCREF 2
    Print #archivoS1, "returnValue none"
    Print #archivoS1, ")"
    Print #archivoS1, ""
    Print #archivoS1, "DELETE"
    Print #archivoS1, "("
    Print #archivoS1, "mo ""ManagedElement=1,NodeBFunction=1,Iub=" & IUB; ",NbapDedicated=1""" 'IUB
    Print #archivoS1, "exception none"
    Print #archivoS1, ")"
    Print #archivoS1, ""
    Print #archivoS1, "DELETE"
    Print #archivoS1, "("
    Print #archivoS1, "mo ""ManagedElement=1,NodeBFunction=1,Iub=" & IUB; ",NbapCommon=1"""  'IUB
    Print #archivoS1, "exception none"
    Print #archivoS1, ")"
    Print #archivoS1, ""
    Print #archivoS1, "DELETE"
    Print #archivoS1, "("
    Print #archivoS1, "mo ""ManagedElement=1,NodeBFunction=1,Iub=" & IUB; """" 'IUB
    Print #archivoS1, "exception none"
    Print #archivoS1, ")"
    Print #archivoS1, ""
    Print #archivoS1, "DELETE"
    Print #archivoS1, "("
    Print #archivoS1, "mo ""ManagedElement=1,TransportNetwork=1,Sctp=1"""
    Print #archivoS1, "exception none"
    Print #archivoS1, ")"
    Print #archivoS1, ""
    Print #archivoS1, "DELETE"
    Print #archivoS1, "("
    Print #archivoS1, "mo ""ManagedElement=1,IpSystem=1,IpAccessSctp=Iub"""
    Print #archivoS1, "exception none"
    Print #archivoS1, ")"
    Print #archivoS1, ""
    Print #archivoS1, "SET"
    Print #archivoS1, "("
    Print #archivoS1, "mo ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1"""
    Print #archivoS1, "exception none"
    Print #archivoS1, "administrativeState Integer 0"
    Print #archivoS1, ")"
    Print #archivoS1, ""
    Print #archivoS1, "SET"
    Print #archivoS1, "("
    Print #archivoS1, "mo ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef=" & SYNC_1; """"       'SYNCREF 1
    Print #archivoS1, "exception none"
    Print #archivoS1, "administrativeState Integer 0"
    Print #archivoS1, ")"
    Print #archivoS1, ""
    Print #archivoS1, "SET"
    Print #archivoS1, "("
    Print #archivoS1, "mo ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef=" & SYNC_2; """"       'SYNCREF 2
    Print #archivoS1, "exception none"
    Print #archivoS1, "administrativeState Integer 0"
    Print #archivoS1, ")"
    Print #archivoS1, ""
    Print #archivoS1, "DELETE"
    Print #archivoS1, "("
    Print #archivoS1, "mo ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef=" & SYNC_2; """"    'SYNCREF 2
    Print #archivoS1, "exception none"
    Print #archivoS1, ")"
    Print #archivoS1, ""
    Print #archivoS1, "DELETE"
    Print #archivoS1, "("
    Print #archivoS1, "   mo ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1,IpSyncRef=" & SYNC_1; """"   'SYNCREF 1
    Print #archivoS1, "   exception none"
    Print #archivoS1, ")"
    Print #archivoS1, ""
    Print #archivoS1, "DELETE"
    Print #archivoS1, "("
    Print #archivoS1, "mo ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1"""
    Print #archivoS1, "exception none"
    Print #archivoS1, ")"
    Print #archivoS1, ""
    Print #archivoS1, "DELETE"
    Print #archivoS1, "("
    Print #archivoS1, "mo ""ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1,IpInterface=1"""
    Print #archivoS1, "exception none"
    Print #archivoS1, ")"
    Print #archivoS1, ""
    Print #archivoS1, "SET"
    Print #archivoS1, "("
    Print #archivoS1, "mo ""ManagedElement=1,IpOam=1,Ip=1"""
    Print #archivoS1, "exception none"
    Print #archivoS1, "nodeInterfaceName String ""le0"""
    Print #archivoS1, ")"
    Print #archivoS1, ""
    Print #archivoS1, "DELETE"
    Print #archivoS1, "("
    Print #archivoS1, "mo ""ManagedElement=1,IpOam=1,Ip=1,IpHostLink=1"""
    Print #archivoS1, "exception none"
    Print #archivoS1, ")"
    Print #archivoS1, "DELETE"
    Print #archivoS1, "("
    Print #archivoS1, "mo ""ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1,IpInterface=2"""
    Print #archivoS1, "exception none"
    Print #archivoS1, ")"
    Print #archivoS1, ""
    Print #archivoS1, "DELETE"
    Print #archivoS1, "("
    Print #archivoS1, "mo ""ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"""
    Print #archivoS1, "exception none"
    Print #archivoS1, ")"
    Print #archivoS1, "CREATE"
    Print #archivoS1, "("
    Print #archivoS1, "   parent ""ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1"""
    Print #archivoS1, "   identity ""1"""
    Print #archivoS1, "   moType GigaBitEthernet"
    Print #archivoS1, "   exception none"
    Print #archivoS1, "   nrOfAttributes 10"
    Print #archivoS1, "   administrativeState Integer 1"
    Print #archivoS1, "   autoNegotiation Boolean true"
    Print #archivoS1, "   configPbitArp Integer 6"
    Print #archivoS1, "   configuredSpeedDuplex Integer 6"
    Print #archivoS1, "   dscpPbitMap Array Struct 64"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 0"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 1"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 2"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 3"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 4"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 5"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 6"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 7"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 8"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 9"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 10"
    Print #archivoS1, "         pbit Integer 1"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 11"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 12"
    Print #archivoS1, "         pbit Integer 1"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 13"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 14"
    Print #archivoS1, "         pbit Integer 1"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 15"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 16"
    Print #archivoS1, "         pbit Integer 2"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 17"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 18"
    Print #archivoS1, "         pbit Integer 2"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 19"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 20"
    Print #archivoS1, "         pbit Integer 2"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 21"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 22"
    Print #archivoS1, "         pbit Integer 2"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 23"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 24"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 25"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 26"
    Print #archivoS1, "         pbit Integer 3"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 27"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 28"
    Print #archivoS1, "         pbit Integer 3"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 29"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 30"
    Print #archivoS1, "         pbit Integer 4"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 31"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 32"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 33"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 34"
    Print #archivoS1, "         pbit Integer 4"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 35"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 36"
    Print #archivoS1, "         pbit Integer 4"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 37"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 38"
    Print #archivoS1, "         pbit Integer 4"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 39"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 40"
    Print #archivoS1, "         pbit Integer 5"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 41"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 42"
    Print #archivoS1, "         pbit Integer 5"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 43"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 44"
    Print #archivoS1, "         pbit Integer 5"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 45"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 46"
    Print #archivoS1, "         pbit Integer 5"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 47"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 48"
    Print #archivoS1, "         pbit Integer 6"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 49"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 50"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 51"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 52"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 53"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 54"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 55"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 56"
    Print #archivoS1, "         pbit Integer 7"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 57"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 58"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 59"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 60"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 61"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 62"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         dscp Integer 63"
    Print #archivoS1, "         pbit Integer 0"
    Print #archivoS1, "   frameFormat Integer 0"
    Print #archivoS1, "   masterMode Boolean true"
    Print #archivoS1, "   portNo Integer 1"
    Print #archivoS1, "   shutDownTimeout Integer 1800"
    Print #archivoS1, "   statePropagationDelay Integer 25"
    Print #archivoS1, ")"
    Print #archivoS1, "CREATE"
    Print #archivoS1, "("
    Print #archivoS1, "   parent ""ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"""
    Print #archivoS1, "   identity ""2"""
    Print #archivoS1, "   moType IpInterface"
    Print #archivoS1, "   exception none"
    Print #archivoS1, "   nrOfAttributes 18"
    Print #archivoS1, "   configurationMode Integer 0"
    Print #archivoS1, "   defaultRouter0 String """ & DGW_Iub_IP_OAM; """"   'DGW IUB OAM IP
    Print #archivoS1, "   defaultRouter1 String ""0.0.0.0"""
    Print #archivoS1, "   defaultRouter2 String ""0.0.0.0"""
    Print #archivoS1, "   defaultRouterPingInterval Integer 4"
    Print #archivoS1, "   dhcpClientIdentifier Struct"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         clientIdentifier String """""
    Print #archivoS1, "         clientIdentifierType Integer 0"
    Print #archivoS1, "   logging Integer 0"
    Print #archivoS1, "   maxNoOfFailedPings Integer 2"
    Print #archivoS1, "   maxWaitForPingReply Integer 3"
    Print #archivoS1, "   mtu Integer 1500"
    Print #archivoS1, "   networkPrefixLength Integer " & MASK; ""             'MASK
    Print #archivoS1, "   noOfPingsBeforeOk Integer 2"
    Print #archivoS1, "   ownIpAddressActive String ""0.0.0.0"""
    Print #archivoS1, "   rps Boolean false"
    Print #archivoS1, "   switchBackTimer Integer 180"
    Print #archivoS1, "   trafficType Integer 0"
    Print #archivoS1, "   vLan Boolean true"
    Print #archivoS1, "   vid Integer " & VLAN_OAM; ""                           'VLAN IUB OAM
    Print #archivoS1, ")"
    Print #archivoS1, "CREATE"
    Print #archivoS1, "("
    Print #archivoS1, "   parent ""ManagedElement=1,IpOam=1,Ip=1"""
    Print #archivoS1, "   identity ""1"""
    Print #archivoS1, "   moType IpHostLink"
    Print #archivoS1, "   exception none"
    Print #archivoS1, "   nrOfAttributes 2"
    Print #archivoS1, "   ipInterfaceMoRef Ref ""ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1,IpInterface=2"""
    Print #archivoS1, "   ipv4Addresses Array String 1"
    Print #archivoS1, "      """ & IP_OAM; """"           'IP OAM
    Print #archivoS1, ")"
    Print #archivoS1, "CREATE"
    Print #archivoS1, "("
    Print #archivoS1, "   parent ""ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1"""
    Print #archivoS1, "   identity ""1"""
    Print #archivoS1, "   moType IpInterface"
    Print #archivoS1, "   exception none"
    Print #archivoS1, "   nrOfAttributes 18"
    Print #archivoS1, "   configurationMode Integer 0"
    Print #archivoS1, "   defaultRouter0 String """ & DGW_Iub_IP; """"           'DGW IUB IP
    Print #archivoS1, "   defaultRouter1 String ""0.0.0.0"""
    Print #archivoS1, "   defaultRouter2 String ""0.0.0.0"""
    Print #archivoS1, "   defaultRouterPingInterval Integer 4"
    Print #archivoS1, "   dhcpClientIdentifier Struct"
    Print #archivoS1, "      nrOfElements 2"
    Print #archivoS1, "         clientIdentifier String """""
    Print #archivoS1, "         clientIdentifierType Integer 0"
    Print #archivoS1, "   logging Integer 0"
    Print #archivoS1, "   maxNoOfFailedPings Integer 2"
    Print #archivoS1, "   maxWaitForPingReply Integer 3"
    Print #archivoS1, "   mtu Integer 1500"
    Print #archivoS1, "   networkPrefixLength Integer " & MASK; ""                   'MASK
    Print #archivoS1, "   noOfPingsBeforeOk Integer 2"
    Print #archivoS1, "   ownIpAddressActive String ""0.0.0.0"""
    Print #archivoS1, "   rps Boolean false"
    Print #archivoS1, "   switchBackTimer Integer 180"
    Print #archivoS1, "   trafficType Integer 0"
    Print #archivoS1, "   vLan Boolean true"
    Print #archivoS1, "   vid Integer " & VLAN_IUB; ""                                'Vlan IUB
    Print #archivoS1, ")"
    Print #archivoS1, "CREATE"
    Print #archivoS1, "("
    Print #archivoS1, "   parent ""ManagedElement=1,IpSystem=1"""
    Print #archivoS1, "   identity ""1"""
    Print #archivoS1, "   moType IpAccessHostEt"
    Print #archivoS1, "   exception none"
    Print #archivoS1, "   nrOfAttributes 6"
    Print #archivoS1, "   administrativeState Integer 1"
    Print #archivoS1, "   ipAddress String """ & IP_TRAFICO; """"              'IP IUB CONROL
    Print #archivoS1, "   ipDefaultTtl Integer 64"
    Print #archivoS1, "   ipInterfaceMoRef Ref ""ManagedElement=1,Equipment=1,Subrack=1,Slot=1,PlugInUnit=1,ExchangeTerminalIp=1,GigaBitEthernet=1,IpInterface=1"""
    Print #archivoS1, "   networkPrefixLength Integer 0"
    Print #archivoS1, "   ntpDscp Integer 46"
    Print #archivoS1, ")"
    Print #archivoS1, "ACTION"
    Print #archivoS1, "("
    Print #archivoS1, "  actionName addStaticRoute"
    Print #archivoS1, "  mo ""ManagedElement=1,IpOam=1,Ip=1,IpRoutingTable=1"""
    Print #archivoS1, "  exception none"
    Print #archivoS1, "  nrOfParameters 5"
    Print #archivoS1, "  String ""0.0.0.0"""
    Print #archivoS1, "  String ""0.0.0.0"""
    Print #archivoS1, "  String """ & DGW_Iub_IP_OAM; """"   'DGW IUB OAM IP
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
    Print #archivoS1, "  String """ & DGW_Iub_IP; """"           'DGW IUB IP
    Print #archivoS1, "  Integer 100"
    Print #archivoS1, "  Boolean 0"
    Print #archivoS1, "    returnValue none"
    Print #archivoS1, ")"
    Print #archivoS1, "SET"
    Print #archivoS1, "("
    Print #archivoS1, "mo ""ManagedElement=1,IpOam=1,Ip=1"""
    Print #archivoS1, "exception none"
    Print #archivoS1, "nodeInterfaceName String ""lh1"""
    Print #archivoS1, ")"
    Close archivoS1
    
        archivoS2 = FreeFile
    Open rutaArchivo_S2 For Output As archivoS2
    
    Print #archivoS2, ""
    Print #archivoS2, "CREATE"
    Print #archivoS2, "("
    Print #archivoS2, "   parent ""ManagedElement=1,IpSystem=1"""
    Print #archivoS2, "   identity ""Iub"""
    Print #archivoS2, "   moType IpAccessSctp"
    Print #archivoS2, "   exception none"
    Print #archivoS2, "   nrOfAttributes 1"
    Print #archivoS2, "   ipAccessHostEtRef1 Ref ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1"""
    Print #archivoS2, ")"
    Print #archivoS2, "CREATE"
    Print #archivoS2, "("
    Print #archivoS2, "   parent ""ManagedElement=1,TransportNetwork=1"""
    Print #archivoS2, "   identity ""1"""
    Print #archivoS2, "   moType Sctp"
    Print #archivoS2, "   exception none"
    Print #archivoS2, "   nrOfAttributes 37"
    Print #archivoS2, "   allowedIncrementCookieLife Integer 30"
    Print #archivoS2, "   associationMaxRtx Integer 8"
    Print #archivoS2, "   bundlingActivated Integer 1"
    Print #archivoS2, "   bundlingTimer Integer 10"
    Print #archivoS2, "   heartbeatInterval Integer 30"
    Print #archivoS2, "   heartbeatMaxBurst Integer 0"
    Print #archivoS2, "   heartbeatPathProbingInterval Integer 500"
    Print #archivoS2, "   heartbeatStatus Boolean true"
    Print #archivoS2, "   initialAdRecWin Integer 32768"
    Print #archivoS2, "   initialRto Integer 20"
    Print #archivoS2, "   intervalOobPkts Integer 3600"
    Print #archivoS2, "   ipAccessSctpRef Ref ""ManagedElement=1,IpSystem=1,IpAccessSctp=Iub"""
    Print #archivoS2, "   keyChangePeriod Integer 4"
    Print #archivoS2, "   mBuffer Integer 256"
    Print #archivoS2, "   maxBurst Integer 4"
    Print #archivoS2, "   maxIncomingStream Integer 17"
    Print #archivoS2, "   maxInitialRtrAtt Integer 8"
    Print #archivoS2, "   maxOutgoingStream Integer 17"
    Print #archivoS2, "   maxShutDownRtrAtt Integer 5"
    Print #archivoS2, "   maxUserDataSize Integer 1480"
    Print #archivoS2, "   maximumRto Integer 40"
    Print #archivoS2, "   minimumRto Integer 10"
    Print #archivoS2, "   nPercentage Integer 85"
    Print #archivoS2, "   nThreshold Integer 192"
    Print #archivoS2, "   numberOfAssociations Integer 2"
    Print #archivoS2, "   pathMaxRtx Integer 4"
    Print #archivoS2, "   pathSelection Integer 0"
    Print #archivoS2, "   potentiallyFailedMaxRtx Integer 4"
    Print #archivoS2, "   rpuId Ref ""ManagedElement=1,SwManagement=1,ReliableProgramUniter=sctp_host"""
    Print #archivoS2, "   rtoAlphaIndex Integer 3"
    Print #archivoS2, "   rtoBetaIndex Integer 2"
    Print #archivoS2, "   sctpAssocDeleteTimeout Integer 168"
    Print #archivoS2, "   switchbackMaxThreshold Integer 65535"
    Print #archivoS2, "   switchbackMinThreshold Integer 1"
    Print #archivoS2, "   switchbackMode Integer 1"
    Print #archivoS2, "   tSack Integer 4"
    Print #archivoS2, "   validCookieLife Integer 60"
    Print #archivoS2, ")"
    Print #archivoS2, ""
    Print #archivoS2, ""
    Print #archivoS2, "CREATE"
    Print #archivoS2, "("
    Print #archivoS2, "   parent ""ManagedElement=1,NodeBFunction=1"""
    Print #archivoS2, "   identity """ & IUB; """"              'IUB
    Print #archivoS2, "   moType Iub"
    Print #archivoS2, "   exception none"
    Print #archivoS2, "   nrOfAttributes 5"
    Print #archivoS2, "   controlPlaneTransportOption Struct"
    Print #archivoS2, "      nrOfElements 2"
    Print #archivoS2, "         atm Boolean false"
    Print #archivoS2, "         ipV4 Boolean true"
    Print #archivoS2, "   rbsId Integer " & RBSID; ""            'RBSID
    Print #archivoS2, "   userLabel String """ & NEMONICO; """"       'Nemonico
    Print #archivoS2, "   userPlaneIpResourceRef Ref ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1"""
    Print #archivoS2, "   userPlaneTransportOption Struct"
    Print #archivoS2, "      nrOfElements 2"
    Print #archivoS2, "         atm Boolean false"
    Print #archivoS2, "         ipV4 Boolean true"
    Print #archivoS2, ")"
    Print #archivoS2, "SET"
    Print #archivoS2, "("
    Print #archivoS2, "   mo ""ManagedElement=1,NodeBFunction=1,Iub=" & IUB; ",IubDataStreams=1"""
    Print #archivoS2, "   exception none"
    Print #archivoS2, "   hsAqmCongCtrlSpiOnOff Array Integer 16"
    Print #archivoS2, "      0"
    Print #archivoS2, "      1"
    Print #archivoS2, "      1"
    Print #archivoS2, "      1"
    Print #archivoS2, "      1"
    Print #archivoS2, "      0"
    Print #archivoS2, "      0"
    Print #archivoS2, "      1"
    Print #archivoS2, "      0"
    Print #archivoS2, "      0"
    Print #archivoS2, "      0"
    Print #archivoS2, "      0"
    Print #archivoS2, "      0"
    Print #archivoS2, "      0"
    Print #archivoS2, "      0"
    Print #archivoS2, "      0"
    Print #archivoS2, ")"
    Print #archivoS2, "SET"
    Print #archivoS2, "("
    Print #archivoS2, "   mo ""ManagedElement=1,NodeBFunction=1,Iub=" & IUB; ",IubDataStreams=1"""          'IUB
    Print #archivoS2, "   exception none"
    Print #archivoS2, "   hsDataFrameDelayThreshold Integer 60"
    Print #archivoS2, ")"
    Print #archivoS2, "SET"
    Print #archivoS2, "("
    Print #archivoS2, "   mo ""ManagedElement=1,NodeBFunction=1,Iub=" & IUB; ",IubDataStreams=1"""            'IUB
    Print #archivoS2, "   exception none"
    Print #archivoS2, "   hsRbrDiscardProbability Integer 0"
    Print #archivoS2, ")"
    Print #archivoS2, "SET"
    Print #archivoS2, "("
    Print #archivoS2, "   mo ""ManagedElement=1,NodeBFunction=1,Iub=" & IUB; ",IubDataStreams=1"""           'IUB
    Print #archivoS2, "   exception none"
    Print #archivoS2, "   hsRbrWeight Array Integer 16"
    Print #archivoS2, "      100"
    Print #archivoS2, "      100"
    Print #archivoS2, "      50"
    Print #archivoS2, "      100"
    Print #archivoS2, "      200"
    Print #archivoS2, "      100"
    Print #archivoS2, "      100"
    Print #archivoS2, "      100"
    Print #archivoS2, "      100"
    Print #archivoS2, "      100"
    Print #archivoS2, "      100"
    Print #archivoS2, "      100"
    Print #archivoS2, "      100"
    Print #archivoS2, "      100"
    Print #archivoS2, "      100"
    Print #archivoS2, "      100"
    Print #archivoS2, ")"
    Print #archivoS2, "SET"
    Print #archivoS2, "("
    Print #archivoS2, "   mo ""ManagedElement=1,NodeBFunction=1,Iub=" & IUB; ",IubDataStreams=1"""          'IUB
    Print #archivoS2, "   exception none"
    Print #archivoS2, "   maxHsRate Integer " & MAXHRATE; ""            'MaxHrate
    Print #archivoS2, ")"
    Print #archivoS2, "SET"
    Print #archivoS2, "("
    Print #archivoS2, "   mo ""ManagedElement=1,NodeBFunction=1,Iub=" & IUB; ",IubDataStreams=1"""            'IUB
    Print #archivoS2, "   exception none"
    Print #archivoS2, "   schHsFlowControlOnOff Array Integer 16"
    Print #archivoS2, "      0"
    Print #archivoS2, "      1"
    Print #archivoS2, "      1"
    Print #archivoS2, "      1"
    Print #archivoS2, "      1"
    Print #archivoS2, "      0"
    Print #archivoS2, "      0"
    Print #archivoS2, "      1"
    Print #archivoS2, "      0"
    Print #archivoS2, "      0"
    Print #archivoS2, "      0"
    Print #archivoS2, "      0"
    Print #archivoS2, "      0"
    Print #archivoS2, "      0"
    Print #archivoS2, "      0"
    Print #archivoS2, "      0"
    Print #archivoS2, ")"
    Print #archivoS2, "CREATE"
    Print #archivoS2, "("
    Print #archivoS2, "   parent ""ManagedElement=1,NodeBFunction=1,Iub=" & IUB; """"            'IUB
    Print #archivoS2, "   identity ""1"""
    Print #archivoS2, "   moType NbapDedicated"
    Print #archivoS2, "   exception none"
    Print #archivoS2, "   nrOfAttributes 2"
    Print #archivoS2, "   l2EstablishReqRetryT Integer 1"
    Print #archivoS2, "   l2EstablishSupervisionT Integer 30"
    Print #archivoS2, ")"
    Print #archivoS2, "CREATE"
    Print #archivoS2, "("
    Print #archivoS2, "   parent ""ManagedElement=1,NodeBFunction=1,Iub=" & IUB; """"                'IUB
    Print #archivoS2, "   identity ""1"""
    Print #archivoS2, "   moType NbapCommon"
    Print #archivoS2, "   exception none"
    Print #archivoS2, "   nrOfAttributes 4"
    Print #archivoS2, "   auditRetransmissionT Integer 5"
    Print #archivoS2, "   l2EstablishReqRetryT Integer 1"
    Print #archivoS2, "   l2EstablishSupervisionT Integer 30"
    Print #archivoS2, "   l3EstablishSupervisionT Integer 30"
    Print #archivoS2, ")"
    Print #archivoS2, "SET"
    Print #archivoS2, "("
    Print #archivoS2, "mo ""ManagedElement=1,IpSystem=1,IpAccessHostEt=1"""
    Print #archivoS2, "exception none"
    Print #archivoS2, "administrativeState Integer 1"
    Print #archivoS2, ")"

    
    Close archivoS2
    
    
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



