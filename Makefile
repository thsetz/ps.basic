SHELL := /bin/bash

export DEVELOPMENT_DEVPI_USER=setzt
export DEVELOPMENT_DEVPI_PASS=setzt
export DEVELOPMENT_DEVPI_HTTPS=http://setz.dnshome.de:4040/setzt/DEVELOPMENT

init:
	python3 -m venv venv
	source ./venv/bin/activate && pip3 install --upgrade pip
	source ./venv/bin/activate && pip3 install -U sphinx_rtd_theme
	source ./venv/bin/activate && pip3 install -U setuptools
	source ./venv/bin/activate && pip3 install -U twine
	source ./venv/bin/activate && pip3 install -U pytest
	source ./venv/bin/activate && pip3 install sphinx invoke ipython numpydoc devpi zest.releaser[recommended]
	source ./venv/bin/activate && pip3 install matplotlib pytest docopt 
	source ./venv/bin/activate && pip3 install --install-option="--include-path=/usr/local/include/" --install-option="--library-path=/usr/local/lib/" pygraphviz
	source ./venv/bin/activate && pip3 install zest.releaser[recommended]
	source ./venv/bin/activate && invoke all-clean
	source ./venv/bin/activate && invoke pre-install
	    

upgrade:
	source ./venv/bin/activate && pip install --upgrade pip

coverage:
	source ./venv/bin/activate &&  python -m pytest --cov=ps --cov-report=term tests/*.py
unit_test:
	source ./venv/bin/activate && invoke unit-test
	source ./venv/bin/activate && invoke doctest

doc:
	source ./venv/bin/activate && invoke doc 
