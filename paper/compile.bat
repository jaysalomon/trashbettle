@echo off
echo Compiling LaTeX document...
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
echo.
echo Compilation complete! Check main.pdf for output.
pause