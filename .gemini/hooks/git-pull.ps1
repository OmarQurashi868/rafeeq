$input | Out-String | Out-Null
git pull origin main 2>&1 | Out-Null
Write-Output '{}'
