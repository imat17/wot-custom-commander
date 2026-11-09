@echo off
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul
if errorlevel 1 exit /b 1
pushd "%~dp0.."
if not exist evidence\game-runtime mkdir evidence\game-runtime
copy /y "G:\Jeux\World_of_Tanks_EU\win64\python27.dll" evidence\game-runtime\python27.dll >nul
cl /nologo /MD /O2 /I C:\Python27\include tests\game_python_host.c /Fo:evidence\game-runtime\host.obj /link /LIBPATH:C:\Python27\libs python27.lib /OUT:evidence\game-runtime\host.exe
if errorlevel 1 exit /b 1
evidence\game-runtime\host.exe C:\Python27 tests\test_game_dependencies.py
set test_result=%errorlevel%
popd
exit /b %test_result%
