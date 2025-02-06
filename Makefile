SHELL := /bin/bash

.PHONY: clean-pyc clean-build docs clean


help:  ## This help dialog.
	@IFS=$$'\n' ; \
	help_lines=(`fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##/:/'`); \
	printf "%-15s %s\n" "target" "help" ; \
	printf "%-15s %s\n" "------" "----" ; \
	for help_line in $${help_lines[@]}; do \
		IFS=$$':' ; \
		help_split=($$help_line) ; \
		help_command=`echo $${help_split[0]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		help_info=`echo $${help_split[2]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		printf '\033[36m'; \
		printf "%-15s %s" $$help_command ; \
		printf '\033[0m'; \
		printf "%s\n" $$help_info; \
	done

install:  ## Install the project in development mode (using virtualenv is highly recommended)
	pip install -U flit
	flit install --symlink --extras=all

clean: clean-build clean-pyc clean-test  ## Remove all build, test, coverage and Python artifacts

clean-build:  ## Remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr *.eggs/
	rm -fr *.egg-info/

clean-pyc:  ## Remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:  ## Eemove test and coverage artifacts
	rm -rf .pytest_cache

test:  ## Run tests quickly with the default Python
	pytest

build: clean  ## Package
	flit build

publish: build  ## Package and upload a release
	flit publish

lint:  ## Check style and errors with ruff
	ruff format
	ruff check --fix

bumpversion:  ## Bump the release version
	@python3 scripts/bumpversion.py release

newversion-patch:  ## Set the new development version
	@python3 scripts/bumpversion.py newversion patch

newversion-minor:  ## Set the new development version
	@python3 scripts/bumpversion.py newversion minor

newversion-major:  ## Set the new development version
	@python3 scripts/bumpversion.py newversion major
