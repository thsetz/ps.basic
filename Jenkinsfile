#!/usr/bin/env groovy
pipeline {
    //agent { docker { image 'python:3.7' } }
    agent { docker { image 'drsetz/python-with-graphviz:3.7.1' } }
    stages {
        stage('Build') {
            steps { echo 'Building ...' 
                    //sh 'sudo apt install python-pydot python-pydot-ng graphviz'
                    sh 'uname -a'
                    sh 'make upgrade'
                    sh 'make init '
                  }
        }
        stage('Unit Test') {
            steps { echo 'Unit Testing..'
                    sh 'make unit_test'
                  }
        }
        stage('docTest') {
            steps { echo 'doc Testing..' 
                   sh 'rm dist/*'
                   sh 'make doc'
            }
        }
        stage('Deploy') {
            steps { echo 'Deploying....' 
                    //# add the commit message to the CHANGES file
                    sh 'git log -1 --oneline >> CHANGES.txt'
                    sh 'git commit -m"autocommit from ci"  CHANGES.txt'
                    //# increment the version number and write it to VERSION.txt
                    sh '#!/usr/bin/env bash \n' + 'source ./venv/bin/activate && python version_incr.py '
                    sh 'git commit -m"autocommit from ci"  VERSION.txt'
                    //# remove the old egg
                    sh '/bin/rm dist/* '
                    //# create a new  egg (with the new version number)
                    sh 'make doc '
                    //# upload to pypi
                    sh '#!/usr/bin/env bash \n' + 'source ./venv/bin/activate && twine upload -u thsetz -p Pypi123456789012 --verbose --repository-url https://test.pypi.org/legacy/ dist/* '

                   
                  }
        }
    }
}
