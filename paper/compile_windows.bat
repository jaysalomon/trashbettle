@echo off
echo Compiling LaTeX document with MiKTeX...
echo.

REM Try to find pdflatex in common locations
set PDFLATEX=pdflatex

REM Check if pdflatex is in PATH
where pdflatex >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo pdflatex not in PATH, searching common locations...
    
    REM Check Program Files
    if exist "C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" (
        set PDFLATEX="C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe"
        set BIBTEX="C:\Program Files\MiKTeX\miktex\bin\x64\bibtex.exe"
        echo Found MiKTeX in Program Files
    ) else if exist "C:\Program Files (x86)\MiKTeX\miktex\bin\pdflatex.exe" (
        set PDFLATEX="C:\Program Files (x86)\MiKTeX\miktex\bin\pdflatex.exe"
        set BIBTEX="C:\Program Files (x86)\MiKTeX\miktex\bin\bibtex.exe"
        echo Found MiKTeX in Program Files (x86)
    ) else if exist "%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe" (
        set PDFLATEX="%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"
        set BIBTEX="%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64\bibtex.exe"
        echo Found MiKTeX in Local AppData
    ) else (
        echo ERROR: Cannot find pdflatex.exe
        echo Please ensure MiKTeX is installed
        pause
        exit /b 1
    )
) else (
    set BIBTEX=bibtex
    echo Found pdflatex in PATH
)

echo.
echo Step 1: First compilation...
%PDFLATEX% -interaction=nonstopmode main.tex
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: First compilation had issues. Check main.log for details.
    echo Continuing anyway...
)

echo.
echo Step 2: Processing bibliography...
%BIBTEX% main
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo NOTE: Bibliography processing had warnings (this is normal if no citations yet)
)

echo.
echo Step 3: Second compilation...
%PDFLATEX% -interaction=nonstopmode main.tex

echo.
echo Step 4: Final compilation...
%PDFLATEX% -interaction=nonstopmode main.tex

echo.
echo ========================================
if exist main.pdf (
    echo SUCCESS! Paper compiled to main.pdf
    echo Opening PDF...
    start main.pdf
) else (
    echo FAILED! Check main.log for errors
)
echo ========================================
pause