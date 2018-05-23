SHELL := /bin/bash

export DEVELOPMENT_DEVPI_USER=setzt
export DEVELOPMENT_DEVPI_PASS=setzt
export DEVELOPMENT_DEVPI_HTTPS=http://setz.dnshome.de:4040/setzt/DEVELOPMENT

init:
	python3 -m venv venv
	source ./venv/bin/activate && pip install -U setuptools
	source ./venv/bin/activate && pip install -U twine
	source ./venv/bin/activate && pip install -U pytest
	source ./venv/bin/activate && pip install sphinx invoke ipython numpydoc devpi zest.releaser[recommended]
	source ./venv/bin/activate && pip install matplotlib pytest docopt pygraphviz
	source ./venv/bin/activate && pip install zest.releaser[recommended]
	source ./venv/bin/activate && invoke pre-install
	    

doc:
	source ./venv/bin/activate && invoke doc 
