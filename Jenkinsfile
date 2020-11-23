#!/usr/bin/env groovy
pipeline {
    //agent { docker { image 'python:3.7' } }
    //agent { docker { image 'drsetz/python-with-graphviz:3.7.1' } }
    agent any
    stages {
        stage('Build') {
            steps { echo 'Building ...' 
                    //sh 'sudo apt install python-pydot python-pydot-ng graphviz'
                    sh 'uname -a'
                    //sh 'make upgrade'
                    sh 'make init '
                  }
        }
        stage('Unit Test') {
            steps { echo 'Unit Testing..'
                    sh 'make test'
                    sh 'make coverage'
                  }
        }
        stage('docTest') {
            steps { echo 'doc Testing..' 
                   sh 'make doc'
            }
        }
        stage('Deploy') {
            steps { echo 'Deploying....' 
                    //# remove the old egg
                    sh '/bin/rm -fR dist/* '
                    //# create a new  egg (with the new version number)
                    //sh 'python3 setup.py sdist'
                    sh 'make release'
                    sh 'ls dist/*'
                    //# upload to pypi
                    //sh '#!/usr/bin/env bash \n' + 'source ./venv/bin/activate && twine upload -u thsetz -p Pypi123456789012 --verbose --repository-url https://test.pypi.org/legacy/ dist/* '
                    //sh '#!/usr/bin/env bash \n' + 'source ./venv/bin/activate && twine upload -u thsetz -p pypi123456789012 --verbose  dist/* '

                   
                  }
        }
    }
}
