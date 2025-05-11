######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : Makefile
# @created     : Sunday May 11, 2025 17:03:06 IST
######################################################################
PYTHON := python
VENV := venv
OUTPUT := _build
TOC_FILES := start.md January.md February.md March.md April.md May.md June.md July.md August.md September.md October.md November.md December.md

.PHONY: all git venv deps preprocess html latex pdf epub clean

all: git venv deps preprocess html pdf epub

git:
	git stash
	git checkout -b readthedocs

venv:
	$(PYTHON) -m venv $(VENV)

deps: venv
	. $(VENV)/bin/activate && \
	$(PYTHON) -m pip install --upgrade pip setuptools && \
	$(PYTHON) -m pip install --upgrade python-dotenv sphinx && \
	$(PYTHON) -m pip install --exists-action=w -r requirements.txt

preprocess:
	. $(VENV)/bin/activate && \
	$(PYTHON) strip_toc.py && \
	$(PYTHON) copytostatic.py && \
	$(PYTHON) rewritelinks.py $(TOC_FILES)

html:
	. $(VENV)/bin/activate && \
	$(PYTHON) -m sphinx -T -W --keep-going -b html -d $(OUTPUT)/doctrees -D language=en . $(OUTPUT)/html

latex:
	. $(VENV)/bin/activate && \
	$(PYTHON) -m sphinx -T -b latex -d $(OUTPUT)/doctrees -D language=en . $(OUTPUT)/latex

pdf: latex
	latexmk -r latexmkrc -pdf -f -dvi- -ps- -jobname=riay -interaction=nonstopmode -output-directory=$(OUTPUT)/latex $(OUTPUT)/latex/riay.tex

epub:
	. $(VENV)/bin/activate && \
	$(PYTHON) -m sphinx -T -W --keep-going -b epub -d $(OUTPUT)/doctrees -D language=en . $(OUTPUT)/epub

clean:
	rm -rf $(VENV) $(OUTPUT)
	git restore .
	git clean -fd
	git checkout development
	git stash pop
	git branch -d readthedocs
