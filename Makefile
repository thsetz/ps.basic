SHELL := /bin/bash
SPHINXBUILD   := python3 -msphinx


clean:
	rm -fR LOG *pyc  *log *.db Test_rsync*cfg tests/coverage_data/* tests/junit_data/* docs/source/_build docs/source/LOG LOG parts eggs bin dist build .tox develop-eggs __pycache__
	rm  -f Tests2*cfg
	rm -f TEST_FSM.*


init:
	/bin/rm -fR venv
	python3 -m venv venv
	source ./venv/bin/activate && pip3 install --upgrade pip setuptools 
	source ./venv/bin/activate && pip3 install -U sphinx_rtd_theme
	source ./venv/bin/activate && pip3 install -U twine, tox
	source ./venv/bin/activate && pip3 install -U pytest
	source ./venv/bin/activate && pip3 install -U pytest-cov
	source ./venv/bin/activate && pip3 install -U black
	source ./venv/bin/activate && pip3 install sphinx coverage ipython numpydoc bump2version
	source ./venv/bin/activate && pip3 install matplotlib pytest docopt 
	source ./venv/bin/activate && pip3 install --install-option="--include-path=/usr/local/include/" --install-option="--library-path=/usr/local/lib/" pygraphviz
	#source ./venv/bin/activate && pip3 install zest.releaser[recommended]
	#source ./venv/bin/activate && invoke all-clean
	#source ./venv/bin/activate && invoke pre-install
	    

install:
	 export DEV_STAGE=TESTING && source ./venv/bin/activate &&  python3 setup.py install

coverage:
	source ./venv/bin/activate &&  python -m pytest --cov=ps --cov-report=term tests/*.py

test:
	export DEV_STAGE=TESTING && source ./venv/bin/activate &&  tox -e tests
	#export DEV_STAGE=TESTING && source ./venv/bin/activate && py.test -cov=src/ps  --junitxml=tests/junit_data/test_unit.xml tests/*.py
	#mkdir -p tests/coverage_data
	#export DEV_STAGE=TESTING && source ./venv/bin/activate &&  py.test  tests/test_ps_basic_utils.py
	#export DEV_STAGE=TESTING && source ./venv/bin/activate &&  py.test  tests/test_ps_basic_Lock.py
	#export DEV_STAGE=TESTING && source ./venv/bin/activate &&  py.test  tests/test_ps_basic_Config.py
	#export DEV_STAGE=TESTING && source ./venv/bin/activate &&  py.test  tests/test_ps_basic_State.py
	#export DEV_STAGE=TESTING && source ./venv/bin/activate &&  py.test  tests/test_ps_basic_fsm.py
	#export DEV_STAGE=TESTING && source ./venv/bin/activate &&  py.test  tests/test_ps_basic_ps_shell_log.py
        ## TBD Fix THAT
	#export DEV_STAGE=TESTING && source ./venv/bin/activate && py.test --junitxml=tests/junit_data/test_doc.xml --cov-append --cov=src/ps --doctest-glob="*,rst" --doctest-modules src/ps/basic/*.py
        ## TBD Fix THAT
	##export DEV_STAGE=TESTING && source ./venv/bin/activate && py.test --junitxml=tests/junit_data/test_doc.xml --cov-append --cov=src/ps --doctest-glob="*,rst" --doctest-modules docs/source/*.rst
	#source ./venv/bin/activate && coverage xml -i && mv coverage.xml tests/coverage_data/base_coverage.xml

doc:
	export IS_TESTING="YES" && export DEV_STAGE=TESTING && source ./venv/bin/activate && cd docs && py.test --junitxml=../tests/junit_data/test_doc.xml --cov-append --cov=../src/ps --doctest-glob="*,rst" --doctest-modules source/*.rst
	export IS_TESTING="YES" && export DEV_STAGE=TESTING && source ./venv/bin/activate && python setup.py develop && cd docs/source; make html 

release_dry:
	export DEV_STAGE=TESTING && source ./venv/bin/activate && bumpversion --dry-run --verbose patch
	#export DEV_STAGE=TESTING && source ./venv/bin/activate && python3 setup.py sdist
release:
	export DEV_STAGE=TESTING && source ./venv/bin/activate && bumpversion --verbose patch
	#export DEV_STAGE=TESTING && source ./venv/bin/activate && python3 setup.py sdist


