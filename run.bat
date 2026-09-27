@echo off
title Keystroke Visualizer
echo ===================================================
echo     Starting Keystroke Visualizer...
echo ===================================================
echo.
echo Press any keys or click your mouse to see the visualizer.
echo Look at the bottom center of your screen!
echo Right-click the keyboard icon in the System Tray for settings.
echo.
echo To close, press Ctrl+C in this window or Exit from System Tray.
echo ===================================================
echo.
"%~dp0.venv\Scripts\python.exe" "%~dp0main.py"
pause
