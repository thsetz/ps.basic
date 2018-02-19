SHELL=/usr/bin/env bash


PYPY_URL =--index-url $(DEVELOPMENT_DEVPI_HTTPS)

MY_NAME = ps.basic
DEV_STAGE=DEVELOPMENT
HERE = $(shell pwd)
VENV = $(HERE)/venv
BIN = $(VENV)/bin
PYTHON = $(BIN)/python
PIP = $(BIN)/pip
INSTALL = $(PIP) install


install_base: 
	virtualenv --no-site-packages --python="/usr/bin/python"  --distribute $(VENV)	
	$(INSTALL) $(PYPY_URL) -U pip
	$(INSTALL) $(PYPY_URL) urllib3[secure]
	$(INSTALL) $(PYPY_URL) twitter.common.contextutil
	$(INSTALL) $(PYPY_URL) invoke
	$(INSTALL) $(PYPY_URL) virtualenv
	$(INSTALL) $(PYPY_URL) pytest 
	$(INSTALL) $(PYPY_URL) pygraphviz --install-option="--include-path=/usr/include/graphviz" --install-option="--library-path=/usr/lib/graphviz"


