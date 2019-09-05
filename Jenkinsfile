#!/usr/bin/env groovy
pipeline {
    agent { docker { image 'python:3.7' } }
    stages {
        stage('Build') {
            steps { echo 'Building ...' 
                    //sh 'sudo apt install python-pydot python-pydot-ng graphviz'
                    sh 'pip install --upgrade pip'
                    sh 'make init '
                  }
        }
        stage('Unit Test') {
            steps { echo 'Unit Testing..' }
        }
        stage('docTest') {
            steps { echo 'doc Testing..' 
                    sh 'make doc'
            }
        }
        stage('Deploy') {
            steps { echo 'Deploying....' 
                    sh '#!/usr/bin/env bash \n' + 'source ./venv/bin/activate && devpi use http://setz.dnshome.de:4040/setzt/DEVELOPMENT && devpi login setzt --password setzt && devpi upload --with-docs'
                  }
        }
    }
}
