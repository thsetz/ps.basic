SHELL := /bin/bash

export DEVELOPMENT_DEVPI_USER=setzt
export DEVELOPMENT_DEVPI_PASS=setzt
export DEVELOPMENT_DEVPI_HTTPS=http://setz.dnshome.de:4040/setzt/DEVELOPMENT

init:
	python3 -m venv venv
	source ./venv/bin/activate && pip3 install -U setuptools
	source ./venv/bin/activate && pip3 install -U twine
	source ./venv/bin/activate && pip3 install -U pytest
	source ./venv/bin/activate && pip3 install sphinx invoke ipython numpydoc devpi zest.releaser[recommended]
	source ./venv/bin/activate && pip3 install matplotlib pytest docopt 
	#source ./venv/bin/activate && pip3 install --install-option="--include-path=/usr/local/include/" --install-option="--library-path=/usr/local/lib/" pygraphviz
	#source ./venv/bin/activate && pip3 install git+https://github.com/pygraphviz/pygraphviz.git --install-option="--include-path=/usr/include/graphviz" --install-option="--library-path=/usr/lib/graphviz/"
	source ./venv/bin/activate && pip3 install zest.releaser[recommended]
	source ./venv/bin/activate && invoke pre-install
	    

doc:
	source ./venv/bin/activate && invoke doc 
