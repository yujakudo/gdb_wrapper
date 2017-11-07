@echo off
set TARGET="B:/msys64/mingw64/bin/gdb.exe"
set PYTHON3=python.exe
rem set FLAGS=DLE
set FLAGS=D
set TARGET_ENCODING=UTF-8
set HOST_ENCODING=CP932
set THE_DIR=%~dp0

echo "%FLAGS%" | find "E" >NUL
if not ERRORLEVEL 1 (
	start "" %PYTHON3% %THE_DIR%pserver.py %TARGET_ENCODING%
)
%PYTHON3% %THE_DIR%wrapper.py %FLAGS% %TARGET_ENCODING% %HOST_ENCODING% %TARGET% %1 %2 %3 %4 %5 %6 %7 %8 %9
