@echo off
echo ====================================================
echo   Building Portable KeystrokeVisualizer.exe
echo ====================================================
"%~dp0.venv\Scripts\pyinstaller.exe" --noconsole --onefile --clean --add-data "%~dp0sounds;sounds" --add-data "%~dp0checkmark.png;." --icon="%~dp0app_icon.ico" --name="KeystrokeVisualizer" "%~dp0main.py"

echo.
echo Build finished! Check the 'dist' folder for KeystrokeVisualizer.exe
pause
