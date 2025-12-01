# Script para comentar las líneas problemáticas en parametros_generator.py
$file = "Macro\functions\parametros_generator.py"
$content = Get-Content $file -Raw

# Reemplazar el bloque problemático
$oldText = @"
            # Si existe id_key y tiene valor, en algunos ejemplos se escribe como 'set <full_id> <id_key> <id_value>'
            if id_key and command_type in ('cr', 'crn', 'set'):
                id_val = inst.get(id_key, "")
                if str(id_val).strip() != "":
                    lines.append(f"set {full_id} {id_key} {str(id_val).strip()}")
"@

$newText = @"
            # Si existe id_key y tiene valor, en algunos ejemplos se escribe como 'set <full_id> <id_key> <id_value>'
            # COMENTADO: Esta lógica genera líneas incorrectas de ID que no aparecen en el archivo de referencia
            # if id_key and command_type in ('cr', 'crn', 'set'):
            #     id_val = inst.get(id_key, "")
            #     if str(id_val).strip() != "":
            #         lines.append(f"set {full_id} {id_key} {str(id_val).strip()}")
"@

$newContent = $content -replace [regex]::Escape($oldText), $newText

Set-Content -Path $file -Value $newContent -NoNewline

Write-Host "Archivo corregido exitosamente"
