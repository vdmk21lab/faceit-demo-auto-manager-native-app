@echo off
REM Native host launcher for Chrome Extension
REM This batch file launches the Python script for native messaging

REM Use the specific Python installation
"C:\Python312\python.exe" "%~dp0native_host.py" %*
