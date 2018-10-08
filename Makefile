# usage: make help

.PHONY: clean clean-test clean-pyc clean-build docs help clean-pypi clean-build-pypi clean-pyc-pypi clean-test-pypi dist-pypi release-pypi clean-conda clean-build-conda clean-pyc-conda clean-test-conda test tag

.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sorted(sys.stdin):
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("\033[36m%-20s\033[0m %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help: ## this help
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)


### PyPI ###

clean-pypi: clean-build-pypi clean-pyc-pypi clean-test-pypi ## remove all build, test, coverage and python artifacts

clean-build-pypi: ## remove pypi build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc-pypi: ## remove python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test-pypi: ## remove pypi test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

dist-pypi: clean-pypi ## build pypi source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

release-pypi: dist-pypi ## release pypi package
	@echo "\n\nUploading" dist/* "to pypi\n"
	@echo "XXX: disabled for now"
	#twine upload dist/*


### Conda ###

clean-conda: clean-build-conda clean-pyc-conda clean-test-conda ## remove all build, test, coverage and python artifacts

clean-build-conda: ## remove conda build artifacts
	@echo "conda build purge"
	conda build purge
	@echo "rm -fr conda-dist/"
	rm -fr conda-dist/

clean-pyc-conda: ## remove conda python file artifacts

clean-test-conda: ## remove conda test and coverage artifacts

dist-conda: clean-conda ## build conda package
	mkdir "conda-dist"
	conda-build ./conda/ --output-folder conda-dist
	ls -l conda-dist/noarch/*tar.bz2

release-conda: dist-conda ## release conda package
	@echo "\n\nUploading" conda-dist/noarch/*tar.bz2 "to fastai@anaconda.org\n"
	@echo "XXX: disabled for now"
	#anaconda upload conda-dist/noarch/*tar.bz2 -u fastai



### Combined ###

## package and upload a release

clean: clean-pypi clean-conda ## clean pip && conda package

dist: dist-pypi dist-conda ## build pip && conda package

release: dist release-pypi release-conda ## release pip && conda package

git-update: ## git pull
	@echo "Making sure we have the latest checkout"
	git pull

install: clean ## install the package to the active python's site-packages
	python setup.py install


### Tagging ###

tag: ## tag the release with current version
	@git tag $$(python setup.py --version) && git push --tags || echo 'Version already released, update your version!'

test: ## run tests with the default python
	python setup.py test


# # XXX: untested
# test-all: ## run tests on every python version with tox
# 	tox
#
# # XXX: untested
# coverage: ## check code coverage quickly with the default python
# 	coverage run --source fastprogress -m pytest
# 	coverage report -m
# 	coverage html
# 	$(BROWSER) htmlcov/index.html
