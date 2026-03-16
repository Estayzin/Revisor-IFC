$text = 'admin:12345678'
$bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
$sha256 = [System.Security.Cryptography.SHA256]::Create()
$hash = $sha256.ComputeHash($bytes)
$hex = ($hash | ForEach-Object { $_.ToString('x2') }) -join ''
Write-Host $hex
