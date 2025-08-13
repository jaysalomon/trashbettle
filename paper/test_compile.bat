@echo off
echo Testing LaTeX compilation...
echo.

REM First attempt - just run pdflatex to see errors
echo Step 1: Initial compilation
pdflatex -interaction=nonstopmode main.tex
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Initial compilation failed. Check main.log for details.
    echo Common issues:
    echo - Missing packages: Install MiKTeX or TeX Live
    echo - Missing figures: Check that all .png files exist in figures/simulations/
    echo - Syntax errors: Check for unescaped underscores or missing $
    pause
    exit /b 1
)

echo.
echo Step 2: Bibliography
bibtex main
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: BibTeX failed. This is normal if no citations are used yet.
)

echo.
echo Step 3: Second compilation
pdflatex -interaction=nonstopmode main.tex

echo.
echo Step 4: Final compilation
pdflatex -interaction=nonstopmode main.tex

echo.
echo Compilation complete! Check main.pdf
pause