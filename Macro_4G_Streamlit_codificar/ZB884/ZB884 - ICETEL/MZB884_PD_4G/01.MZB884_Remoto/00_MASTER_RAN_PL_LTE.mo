// =====================================================================
// MASTER SCRIPT - Ejecuta todos los archivos .mos generados dinámicamente
// =====================================================================
// Este script ejecuta automáticamente todos los archivos .mos que se
// encuentren en el directorio, sin importar el nemónico utilizado.
// =====================================================================

// Ejecutar scripts en orden secuencial
run 00_*_Hardware.mos
run 01_*_EUtranCellFDD.mos
run 02_*_UtranRelation.mos
run 03_*_EUtranRelation.mos
run 04_*_GUtranRelation.mos
run 05_*_Parametros.mos
run 06_*_Tilt.mos

// Capturar fecha actual
$date = `date +%y%m%d`

// Crear CV (Configuration Version) con el nombre del nodo
cvms CV_$nodename_OK
