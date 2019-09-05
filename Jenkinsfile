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
                    sh 'make doc'
            }
        }
        stage('Deploy') {
            steps { echo 'Deploying....' 
                    sh '#!/usr/bin/env bash \n' + 'source ./venv/bin/activate && twine upload -u thsetz -p Pypi123456789012 --repository-url https://test.pypi.org/legacy/ dist/* '
                  }
        }
    }
}
