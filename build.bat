@echo off
echo Installing required packages...
pip install pyinstaller transformers torch

echo Building Anupama AI Assistant...
pyinstaller --onefile ^
    --add-data "anupama_model;anupama_model" ^
    --windowed ^
    --name "Anupama_AI_Assistant" ^
    app.py

echo Build complete! Check dist/ folder for the executable.
echo If you don't have an icon, remove the --icon=icon.ico flag
pause
