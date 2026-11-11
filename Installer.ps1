param([string]$GameRoot='G:\Jeux\World_of_Tanks_EU')
$ErrorActionPreference='Stop'
$game=[IO.Path]::GetFullPath($GameRoot)
$versionText=Get-Content -LiteralPath (Join-Path $game 'version.xml') -Raw
if($versionText -notmatch 'v\.2\.4\.1\.1\s') { throw 'Cette version alpha est prévue pour WoT EU 2.4.1.1 uniquement.' }
if(Get-Process -Name WorldOfTanks -ErrorAction SilentlyContinue) { throw 'Fermez World of Tanks avant installation.' }
$modDir=Join-Path $game 'mods\2.4.1.1'
if(-not (Get-ChildItem -LiteralPath $modDir -Filter 'aslain.modmenu_*.wotmod')) { throw 'Mod Menu Aslain requis.' }
if(-not (Get-ChildItem -LiteralPath $modDir -Recurse -Filter 'net.openwg.gameface_*.wotmod')) { throw 'OpenWG Gameface requis.' }
$source=Join-Path $PSScriptRoot 'dist\matisse.commander_friend_0.2.5.wotmod'
if(-not (Test-Path -LiteralPath $source)) { throw 'Le paquet compilé est absent.' }
$nativeSource=Join-Path $PSScriptRoot 'dist\native_0.1.1\commander_friend_audio.pyd'
if(-not (Test-Path -LiteralPath $nativeSource)) { throw 'Le lecteur audio est absent.' }
$dest=Join-Path $modDir 'matisse.commander_friend_0.2.5.wotmod'
$knownVersions=@{
 'matisse.commander_friend_0.2.4.wotmod'='C329B977A6FF13FB85DEC9554419EEB7B58B36B4D0848496D3F5E256D26C7739'
 'matisse.commander_friend_0.2.3.wotmod'='F378C9F600BC7C5FAA6C37F2D0F9E56DF03E8F380E7B721355FB54AAD94DD77A'
 'matisse.commander_friend_0.2.2.wotmod'='19911DC9FC3001F308BEE66E2ACD7759881D4E2378CD14D57A754A91CE74F926'
 'matisse.commander_friend_0.2.1.wotmod'='C0FF191EC01E7B7026A68E06308A039BA9C09D1826D039FB5FCCA1F19C7DFE53'
 'matisse.commander_friend_0.1.0.wotmod'='019BE86ACBDDC7A9DEFAAE742A2800712C7DE09C7B9058B300C92CCA0185842C'
 'matisse.commander_friend_0.1.1.wotmod'='6044CBD7D6A050D536A7BE5282E31C71FDAE1DF68EA9DBA4D44A9A5F58B1A15E'
 'matisse.commander_friend_0.2.0.wotmod'='4BEB4E42BB4CE864B709621D157EE6E0A50384EADD837BA74B1C2529CDD9A51C'
}
$old=Get-ChildItem -LiteralPath $modDir -Filter 'matisse.commander_friend_*.wotmod'
foreach($file in $old) {
 if($knownVersions.ContainsKey($file.Name) -and (Get-FileHash -LiteralPath $file.FullName).Hash -eq $knownVersions[$file.Name]) { continue }
 if($file.FullName -ne $dest -or (Get-FileHash -LiteralPath $file.FullName).Hash -ne (Get-FileHash -LiteralPath $source).Hash) {
  throw "Une autre version existe déjà : $($file.FullName). Conservez-la hors du dossier mods avant de continuer."
 }
}
$config=Join-Path $game 'mods\configs\matisse.commander_friend'
New-Item -ItemType Directory -Force -Path $config,(Join-Path $config 'voice'),(Join-Path $config 'demo_voice') | Out-Null
$nativeDir=Join-Path $config 'native_0.1.1'
New-Item -ItemType Directory -Force -Path $nativeDir | Out-Null
$nativeDest=Join-Path $nativeDir 'commander_friend_audio.pyd'
if((Test-Path -LiteralPath $nativeDest) -and (Get-FileHash -LiteralPath $nativeDest).Hash -ne (Get-FileHash -LiteralPath $nativeSource).Hash) { throw 'Un autre lecteur audio existe déjà. Installation annulée.' }
Copy-Item -LiteralPath $nativeSource -Destination $nativeDest
if((Get-FileHash -LiteralPath $nativeDest).Hash -ne (Get-FileHash -LiteralPath $nativeSource).Hash) { throw 'La copie du lecteur audio est incorrecte.' }
foreach($file in Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'assets\demo_voice') -Filter '*.wav') {
 $target=Join-Path $config ('demo_voice\'+$file.Name)
 if(-not(Test-Path -LiteralPath $target)){ Copy-Item -LiteralPath $file.FullName -Destination $target }
}
foreach($name in @('Catalogue-des-enregistrements.html','catalogue-enregistrements.json','fichiers-a-enregistrer.txt')) {
 Copy-Item -LiteralPath (Join-Path $PSScriptRoot ('dist\'+$name)) -Destination (Join-Path $config $name)
}
$profileSource=Join-Path $PSScriptRoot 'assets\profiles\papacito'
$profileDest=Join-Path $config 'profiles\papacito'
$backupDir=Join-Path $config ('backups\'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
foreach($file in Get-ChildItem -LiteralPath $profileSource -Recurse -File){
 $relative=$file.FullName.Substring($profileSource.Length+1)
 $target=Join-Path $profileDest $relative
 if((Test-Path -LiteralPath $target) -and (Get-FileHash -LiteralPath $target).Hash -ne (Get-FileHash -LiteralPath $file.FullName).Hash){
  $savedProfile=Join-Path $backupDir ('papacito\'+$relative)
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $savedProfile) | Out-Null
  Copy-Item -LiteralPath $target -Destination $savedProfile
 }
}
foreach($file in Get-ChildItem -LiteralPath $profileSource -Recurse -File){
 $relative=$file.FullName.Substring($profileSource.Length+1)
 $target=Join-Path $profileDest $relative
 New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
 Copy-Item -LiteralPath $file.FullName -Destination $target
 if((Get-FileHash -LiteralPath $target).Hash -ne (Get-FileHash -LiteralPath $file.FullName).Hash){throw 'La copie du profil Papacito est incorrecte.'}
}
$moved=@()
try {
 foreach($file in $old | Where-Object { $_.FullName -ne $dest }){
  New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
  $selection=Join-Path $config 'selection.json'
  if(Test-Path -LiteralPath $selection){Copy-Item -LiteralPath $selection -Destination (Join-Path $backupDir 'selection-before-update.json')}
  $saved=Join-Path $backupDir ($file.Name+'.disabled')
  Move-Item -LiteralPath $file.FullName -Destination $saved
  $moved+=@{Saved=$saved;Original=$file.FullName}
 }
 Copy-Item -LiteralPath $source -Destination $dest
}
catch {
 if(Test-Path -LiteralPath $dest){Remove-Item -LiteralPath $dest}
 foreach($entry in $moved){ Copy-Item -LiteralPath $entry.Saved -Destination $entry.Original }
 throw
}
$hash=(Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash
if($hash -ne (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash){throw 'La copie du paquet est incorrecte.'}
[pscustomobject]@{Path=$dest;SHA256=$hash;Game='2.4.1.1';InstalledAt=(Get-Date).ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'dist\installation.json') -Encoding UTF8
Write-Output 'Alpha installée. Aucun chef de char sélectionné automatiquement. Validation dans le garage encore nécessaire.'
