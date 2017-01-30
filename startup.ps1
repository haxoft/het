start-process powershell.exe -argument '-nologo -noprofile -executionpolicy bypass -command cd $PSScriptRoot; ngrok http 8000 '
Start-Sleep -m 5000
$wc = New-Object system.Net.WebClient
$result = $wc.downloadString('http://localhost:4040/status')
$result -match 'https://[a-f0-9]+\.ngrok\.io' > $null
$ngrokUrl = $Matches[0]
if(!$ngrokUrl) { throw [System.InvalidOperationException] "Could not retrieve ngrok URL" }
Write-Output $ngrokUrl
(Get-Content ./hetaddon/static/addon/atlassian-connect.json) | ForEach-Object { $_ -replace '(?<="baseUrl": ").*?(?=")', $ngrokUrl } | Set-Content ./hetaddon/static/addon/atlassian-connect.json
$ngrokUrlWithoutProtocol = $ngrokUrl -replace 'https://', ''
(Get-Content ./HET/settings.py) | ForEach-Object { $_ -replace '(?<=ALLOWED_HOSTS = \[").*?(?="\])', $ngrokUrlWithoutProtocol } | Set-Content ./HET/settings.py
Set-Clipboard -Value "$ngrokUrl/static/addon/atlassian-connect.json"
start-process powershell.exe -argument '-nologo -noprofile -executionpolicy bypass -command cd $PSScriptRoot; python manage.py runserver 8000'
Read-Host -Prompt "Press Enter to exit"