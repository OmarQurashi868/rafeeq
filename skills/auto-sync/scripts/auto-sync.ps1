param(
    [int]$DebounceSeconds = 5,
    [string]$Branch = "master"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
Set-Location $repoRoot

function Get-CommitSummary {
    param([string[]]$ChangedFiles)

    if ($ChangedFiles.Count -eq 0) {
        return "Auto-sync repository changes"
    }

    $topLevelNames = $ChangedFiles |
        ForEach-Object { ($_ -split "[/\\]")[0] } |
        Sort-Object -Unique

    if ($topLevelNames.Count -eq 1) {
        return "Update $($topLevelNames[0])"
    }

    if ($topLevelNames.Count -le 3) {
        return "Update $($topLevelNames -join ', ')"
    }

    return "Update project files"
}

function Invoke-AutoSync {
    $status = git status --porcelain
    if (-not $status) {
        return
    }

    git add .

    $staged = @(git diff --cached --name-only)
    if ($staged.Count -eq 0) {
        return
    }

    $summary = Get-CommitSummary -ChangedFiles $staged
    git commit -m $summary
    git push origin $Branch
}

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $repoRoot
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

$ignoredDirectories = @(
    "$([IO.Path]::DirectorySeparatorChar).git$([IO.Path]::DirectorySeparatorChar)",
    "$([IO.Path]::DirectorySeparatorChar)__pycache__$([IO.Path]::DirectorySeparatorChar)"
)

$state = [pscustomobject]@{
    Pending = $false
    LastChange = Get-Date
}

$action = {
    $path = $Event.SourceEventArgs.FullPath
    foreach ($ignored in $Event.MessageData.IgnoredDirectories) {
        if ($path.Contains($ignored)) {
            return
        }
    }

    $Event.MessageData.State.Pending = $true
    $Event.MessageData.State.LastChange = Get-Date
}

$messageData = [pscustomobject]@{
    IgnoredDirectories = $ignoredDirectories
    State = $state
}

$subscriptions = @(
    Register-ObjectEvent -InputObject $watcher -EventName Changed -Action $action -MessageData $messageData
    Register-ObjectEvent -InputObject $watcher -EventName Created -Action $action -MessageData $messageData
    Register-ObjectEvent -InputObject $watcher -EventName Deleted -Action $action -MessageData $messageData
    Register-ObjectEvent -InputObject $watcher -EventName Renamed -Action $action -MessageData $messageData
)

Write-Host "Auto-sync watcher running for $repoRoot. Press Ctrl+C to stop."

try {
    while ($true) {
        Start-Sleep -Seconds 1
        if ($state.Pending -and ((Get-Date) - $state.LastChange).TotalSeconds -ge $DebounceSeconds) {
            $state.Pending = $false
            try {
                Invoke-AutoSync
            }
            catch {
                Write-Error "Auto-sync failed: $_"
            }
        }
    }
}
finally {
    foreach ($subscription in $subscriptions) {
        Unregister-Event -SubscriptionId $subscription.Id -ErrorAction SilentlyContinue
    }
    $watcher.Dispose()
}
