pipeline {
    agent any

    stages {
        stage('1. Checkout') {
            steps {
                echo 'Checking out source code from Git...'
                checkout scm
            }
        }

        stage('2. Syntax Check') {
            steps {
                echo 'Checking Python syntax errors...'
                sh 'python3 -m py_compile backend/app.py'
            }
        }

        stage('3. Build Image') {
            steps {
                echo 'Building Docker Images via Compose...'
                sh 'docker compose build'
            }
        }

        stage('4. Automated Deployment') {
            steps {
                echo 'Deploying containers...'
                sh 'docker compose up -d'
            }
        }

        stage('5. Health Check') {
            steps {
                echo 'Checking service health...'
                sleep 5
                sh 'curl -f http://localhost:80/ || exit 1'
                sh 'curl -f http://localhost:80/queue || exit 1'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully for Student Service Queue System!'
        }
        failure {
            echo 'Pipeline build failed!'
        }
    }
}