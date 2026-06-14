@echo off
REM Build a standalone Windows executable for the Compliance AI Auditor.
cd /d %~dp0
python -m pip install --upgrade pyinstaller
pyinstaller --onefile --add-data "templates;templates" --add-data "index.html;." --name ComplianceAudit app.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build completed successfully.
    echo Find the executable in dist\ComplianceAudit.exe
) else (
    echo.
    echo Build failed. Check the PyInstaller output for errors.
)
