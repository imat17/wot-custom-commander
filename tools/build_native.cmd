@echo off
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul
if errorlevel 1 exit /b 1
pushd "%~dp0.."
if not exist dist\native_0.1.1 mkdir dist\native_0.1.1
cl /nologo /LD /MD /O2 /W4 /I C:\Python27\include src\custom_commander_audio.c /Fo:dist\native_0.1.1\custom_commander_audio.obj /link /LIBPATH:C:\Python27\libs python27.lib winmm.lib /IMPLIB:dist\native_0.1.1\custom_commander_audio.lib /OUT:dist\native_0.1.1\custom_commander_audio.pyd
set build_result=%errorlevel%
popd
exit /b %build_result%
