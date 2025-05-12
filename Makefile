######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : Makefile
# @created     : Sunday May 11, 2025 17:03:06 IST
######################################################################
PYTHON := python
VENV := venv
OUTPUT := _build
TOC_FILES := start.md January.md February.md March.md April.md May.md June.md July.md August.md September.md October.md November.md December.md
CURRENT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD)
READTHEDOCS_BRANCH := readthedocs

.PHONY: all gitcommands venv deps preprocess linkcheck html latex pdf epub clean

all: gitcommands venv deps preprocess linkcheck html pdf epub clean

gitcommands:
	echo "In branch: " $(CURRENT_BRANCH)
	git stash || true
	git checkout -b $(READTHEDOCS_BRANCH)

venv: gitcommands
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

linkcheck:
	. $(VENV)/bin/activate && \
 	$(PYTHON) -m sphinx -b linkcheck -j auto . $(OUTPUT)/linkcheck

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
	git checkout $(CURRENT_BRANCH)
	git stash pop || true
	git branch -d $(READTHEDOCS_BRANCH)
