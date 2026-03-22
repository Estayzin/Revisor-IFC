$lines = Get-Content 'C:\Users\Usuario\Documents\GitHub\Revisor-IFC\explorer.html'
$formaCount = 0
$start = -1
$end = -1
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match 'var FORMA=') {
        $formaCount++
        if ($formaCount -eq 2) { $start = $i }
    }
    if ($start -gt 0 -and $lines[$i] -match 'Centrar') {
        $end = $i
        break
    }
}
Write-Host "start=$start end=$end total=$($lines.Count)"
if ($start -gt 0 -and $end -gt $start) {
    $clean = $lines[0..($start-1)] + $lines[$end..($lines.Count-1)]
    $tmpPath = 'C:\Users\Usuario\Documents\GitHub\Revisor-IFC\explorer_clean.html'
    $clean | Set-Content $tmpPath -Encoding UTF8
    Write-Host "Guardado en $tmpPath con $($clean.Count) lineas"
}
