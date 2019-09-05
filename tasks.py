from invoke import task, Collection, run
import pytest
import os

MY_PACKAGE_NAME="ps.basic"

PRE_INSTALL_PAKETS        =  ["sphinx devpi-client tox tzlocal  pygraphviz  docopt GitPython gitdb smmap pytest-cov urllib3 chardet certifi idna"]
MY_VERSION_NUMBER         =  open("VERSION.txt","r").read().strip()

DEVELOPMENT_DEVPI_USER    = os.environ.get("DEVELOPMENT_DEVPI_USER", None)
DEVELOPMENT_DEVPI_PASS    = os.environ.get("DEVELOPMENT_DEVPI_PASS", None)
DEVELOPMENT_DEVPI_HTTPS   = os.environ.get("DEVELOPMENT_DEVPI_HTTPS",None)


@task
def pre_install(ctx): 
  for elem in PRE_INSTALL_PAKETS: 
                          #run("pip install --trusted-host setz.dnshome.de  -i %s %s"%(DEVELOPMENT_DEVPI_HTTPS, elem)) 
                          run("pip install  %s"%( elem)) 
  # fsm module needs enhanced things
  #run('pip install pygraphviz --install-option="--include-path=/usr/include/graphviz" --install-option="--library-path=/usr/lib/graphviz"') 
  run('mkdir -p tests/junit_data ; mkdir -p tests/coverage_data', pty=True )

@task
def package_uninstall(ctx): run("pip uninstall -y %(MY_PACKAGE_NAME)s || true"%(globals()), pty=True)

@task(pre=[package_uninstall])
def package_install(ctx):   run("python setup.py install ", pty=True)

@task(pre=[package_uninstall])
def package_install_develop(ctx): run("python setup.py develop", pty=True)


@task
def clean(ctx):             run("rm -fR *pyc  *log *.db Test_rsync*cfg tests/coverage_data/* tests/junit_data/*") 

@task(pre=[clean])
def all_clean(ctx):         run("rm -fR  docs/source/_build docs/source/LOG LOG parts eggs bin dist build venv .tox develop-eggs") 

@task
def devpi_logoff(ctx):      run("devpi logoff") 

@task
def devpi_login(ctx):       run("devpi login  %(DEVELOPMENT_DEVPI_USER)s --password %(DEVELOPMENT_DEVPI_PASS)s &&  \
                                       devpi use %(DEVELOPMENT_DEVPI_HTTPS)s"%(globals())) 


@task(pre=[devpi_login])
def devpi_test(ctx):        run(" devpi  test %(MY_PACKAGE_NAME)s"%globals(),pty=True) 


@task(pre=[package_install_develop])
def unit_test(ctx):
                      
                         run('export DEV_STAGE=TESTING && py.test --cov=src/ps  --junitxml=tests/junit_data/test_unit.xml tests/*.py')
                         #run('export DEV_STAGE=TESTING && py.test --cov=src/ps  --junitxml=tests/junit_data/test_unit.xml tests/test_base.py::TestBasic::test_that_it_is_possible_to_create_a_base_object_for_the_dev_stages')
                         #run('export DEV_STAGE=TESTING && py.test --cov=src/ps  --junitxml=tests/junit_data/test_unit.xml tests/test_base.py::TestBasic')
                         #run('export DEV_STAGE=TESTING && nosetests -v --with-xunit --xunit-file="tests/junit_data/test_base.xml" \
                         #--with-coverage --cover-erase --cover-package=ps tests/*.py', pty=True)
@task(pre=[package_install_develop,unit_test])
def doc_test(ctx):
                         run('export DEV_STAGE=TESTING && py.test --junitxml=tests/junit_data/test_doc.xml --cov-append --cov=src/ps --doctest-glob="*,rst" --doctest-modules src/ps/*.py')
                         run("coverage xml -i && mv coverage.xml tests/coverage_data/base_coverage.xml")
                         #run('nosetests -v --with-doctest --with-xunit \
                         #--xunit-file="tests/junit_data/doctest.xml" --with-coverage  --cover-package=ps ps', pty=True)




#@task(pre=[clean, package_uninstall, package_install])
#def test(ctx): 
#                         run('mkdir -p tests/junit_data ; mkdir -p tests/coverage_data' )
#                         run('nosetests -vv --with-xunit --xunit-file="tests/junit_data/test_base.xml" \
#                         --with-coverage --cover-erase --cover-package=ps tests/test_base.py')
#                         run('nosetests -vv --with-doctest --with-xunit \
#                         --xunit-file="tests/junit_data/doctest.xml" --with-coverage  --cover-package=ps ps')
#                         run("coverage xml -i && mv coverage.xml tests/coverage_data/base_coverage.xml")

@task(pre=[package_uninstall, package_install])
def doctest(ctx):           run("cd docs;   make doctest", pty=True)

@task(pre=[package_uninstall, package_install])
def doc(ctx):               run("cd docs/source; make html", pty=True)


@task(pre=[devpi_login ])
def ipush(ctx):
    run("devpi push %s==%s ps/INTEGRATION"%(MY_PACKAGE_NAME,MY_VERSION_NUMBER), pty=True)

@task(pre=[devpi_login ])
def ppush(ctx):
    run("devpi push %s==%s ps/PRODUCTION"%(MY_PACKAGE_NAME,MY_VERSION_NUMBER), pty=True)


#@task(pre=[clean, package_uninstall, package_install,  devpi_logoff, devpi_login, devpi_test])
@task(pre=[clean, package_uninstall, package_install,  devpi_logoff, devpi_login])
def upload(ctx):            run("devpi upload --with-docs", pty=True)

@task(pre=[clean, package_uninstall, package_install,  devpi_logoff, devpi_login])
def upload_test(ctx):            run("python3 setup.py sdist bdist_wheel", pty=True)

@task(pre=[devpi_test, devpi_login ], post=[upload,doc_test])
def eggrelease(ctx): 
                         run("eggrelease -d   --server=%s --user=%s \
                         --password=%s"%(DEVELOPMENT_DEVPI_HTTPS, DEVELOPMENT_DEVPI_USER, DEVELOPMENT_DEVPI_PASS), pty=True)




