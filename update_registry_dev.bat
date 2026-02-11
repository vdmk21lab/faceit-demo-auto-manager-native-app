@echo off
echo Updating Windows Registry for development...
echo.

reg add "HKCU\Software\Google\Chrome\NativeMessagingHosts\com.faceit.demomanager" /ve /t REG_SZ /d "C:\Users\VadimPrivate\WebstormProjects\faceit-demo-manager\faceit-demo-auto-manager-host\com.faceit.demomanager.json" /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Registry updated!
    echo.
    echo Now reload your Chrome extension:
    echo 1. Open chrome://extensions
    echo 2. Click the reload icon on FACEIT Demo Auto Manager
    echo 3. Try downloading a demo again
) else (
    echo.
    echo [ERROR] Failed to update registry
)

pause
