# Read stdin for context
$inputJson = $input | Out-String | ConvertFrom-Json

$title = "Rafeeq"
$message = "Task complete or waiting for input."

if ($inputJson.event -eq "AfterAgent") {
    $message = "Agent is done responding."
} elseif ($inputJson.event -eq "Notification") {
    if ($inputJson.data -and $inputJson.data.message) {
        $message = $inputJson.data.message
    } else {
        $message = "User input required."
    }
}

# Load Assemblies
try {
    [void][Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime]
    [void][Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime]

    # Toast Notification XML
    $xml = @"
<toast>
    <visual>
        <binding template="ToastGeneric">
            <text>$title</text>
            <text>$message</text>
        </binding>
    </visual>
</toast>
"@

    $xmlDoc = New-Object Windows.Data.Xml.Dom.XmlDocument
    $xmlDoc.LoadXml($xml)

    $AppId = "{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe"
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($AppId).Show($xmlDoc)
} catch {
    # Fallback to a simpler method if WinRT fails (e.g. older Windows or restricted environment)
    Add-Type -AssemblyName System.Windows.Forms
    $global:balloon = New-Object System.Windows.Forms.NotifyIcon
    $global:balloon.Icon = [System.Drawing.SystemIcons]::Information
    $global:balloon.Visible = $true
    $global:balloon.ShowBalloonTip(5000, $title, $message, "Info")
}

# Mandatory JSON output for Gemini CLI
"{}"
