param([string]$GameRoot='G:\Jeux\World_of_Tanks_EU')
$ErrorActionPreference='Stop'
if(Get-Process -Name WorldOfTanks -ErrorAction SilentlyContinue){throw 'Fermez le jeu avant désinstallation.'}
$target=Join-Path ([IO.Path]::GetFullPath($GameRoot)) 'mods\2.4.1.1\custom_commander_0.3.0.wotmod'
if(Test-Path -LiteralPath $target){
 $reference=Join-Path $PSScriptRoot 'dist\custom_commander_0.3.0.wotmod'
 if((Get-FileHash -LiteralPath $target).Hash -ne (Get-FileHash -LiteralPath $reference).Hash){throw 'Le mod a été modifié : retrait automatique annulé.'}
 Remove-Item -LiteralPath $target
}
Write-Output 'Mod retiré. Vos photos, enregistrements et sélections sont conservés.'
