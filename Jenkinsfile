pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t hello-world-flask:tw2 .'
            }
        }

        stage('Verify Docker Image') {
            steps {
                bat 'docker images hello-world-flask'
            }
        }
    }
}
