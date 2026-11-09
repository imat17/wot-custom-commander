param([string]$GameRoot='G:\Jeux\World_of_Tanks_EU')
$ErrorActionPreference='Stop'
$game=[IO.Path]::GetFullPath($GameRoot)
$versionText=Get-Content -LiteralPath (Join-Path $game 'version.xml') -Raw
if($versionText -notmatch 'v\.2\.4\.1\.1\s') { throw 'Cette version alpha est prévue pour WoT EU 2.4.1.1 uniquement.' }
if(Get-Process -Name WorldOfTanks -ErrorAction SilentlyContinue) { throw 'Fermez World of Tanks avant installation.' }
$modDir=Join-Path $game 'mods\2.4.1.1'
if(-not (Get-ChildItem -LiteralPath $modDir -Filter 'aslain.modmenu_*.wotmod')) { throw 'Mod Menu Aslain requis.' }
if(-not (Get-ChildItem -LiteralPath $modDir -Recurse -Filter 'net.openwg.gameface_*.wotmod')) { throw 'OpenWG Gameface requis.' }
$source=Join-Path $PSScriptRoot 'dist\matisse.commander_friend_0.1.1.wotmod'
if(-not (Test-Path -LiteralPath $source)) { throw 'Le paquet compilé est absent.' }
$nativeSource=Join-Path $PSScriptRoot 'dist\native_0.1.1\commander_friend_audio.pyd'
if(-not (Test-Path -LiteralPath $nativeSource)) { throw 'Le lecteur audio est absent.' }
$dest=Join-Path $modDir 'matisse.commander_friend_0.1.1.wotmod'
$old=Get-ChildItem -LiteralPath $modDir -Filter 'matisse.commander_friend_*.wotmod'
foreach($file in $old) {
 if($file.Name -eq 'matisse.commander_friend_0.1.0.wotmod' -and (Get-FileHash -LiteralPath $file.FullName).Hash -eq '019BE86ACBDDC7A9DEFAAE742A2800712C7DE09C7B9058B300C92CCA0185842C') { continue }
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
$backupDir=Join-Path $config ('backups\'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
$previous=Join-Path $modDir 'matisse.commander_friend_0.1.0.wotmod'
if(Test-Path -LiteralPath $previous){
 New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
 # Both absolute paths are confined to this explicitly selected game directory.
 Move-Item -LiteralPath $previous -Destination (Join-Path $backupDir 'matisse.commander_friend_0.1.0.wotmod.disabled')
}
try { Copy-Item -LiteralPath $source -Destination $dest }
catch {
 $saved=Join-Path $backupDir 'matisse.commander_friend_0.1.0.wotmod.disabled'
 if(Test-Path -LiteralPath $saved){ Copy-Item -LiteralPath $saved -Destination $previous }
 throw
}
$hash=(Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash
if($hash -ne (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash){throw 'La copie du paquet est incorrecte.'}
[pscustomobject]@{Path=$dest;SHA256=$hash;Game='2.4.1.1';InstalledAt=(Get-Date).ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'dist\installation.json') -Encoding UTF8
Write-Output 'Alpha installée. Aucun chef de char sélectionné automatiquement. Validation dans le garage encore nécessaire.'
