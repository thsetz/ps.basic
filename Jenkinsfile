#!/usr/bin/env groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps { echo 'Building ...' 
                    sh 'make init || true '
                    sh 'make doc'
                  }
        }
        stage('Unit Test') {
            steps { echo 'Unit Testing..' }
        }
        stage('docTest') {
            steps { echo 'doc Testing..' }
        }
        stage('Deploy') {
            steps { echo 'Deploying....' 
                    sh '#!/usr/bin/env bash \n' + 'source ./venv/bin/activate && devpi use http://setz.dnshome.de:4040/setzt/DEVELOPMENT && devpi login setzt --password setzt && devpi upload --with-docs'
                  }
        }
    }
}
