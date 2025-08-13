# Makefile for LaTeX compilation

MAIN = main
SOURCES = $(MAIN).tex sections/*.tex
BIB = references.bib

all: $(MAIN).pdf

$(MAIN).pdf: $(SOURCES) $(BIB)
	pdflatex $(MAIN)
	bibtex $(MAIN)
	pdflatex $(MAIN)
	pdflatex $(MAIN)

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot

cleanall: clean
	rm -f $(MAIN).pdf

.PHONY: all clean cleanall