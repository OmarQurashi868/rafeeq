$input | Out-String | Out-Null
git pull origin master 2>&1 | Out-Null
Write-Output '{}'
