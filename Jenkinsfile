pipeline {
    agent any

    stages {
        stage('Test') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$WORKSPACE:/app" \
                      -w /app \
                      python:3.12-slim \
                      sh -c "pip install --no-cache-dir -r requirements.txt && pytest -v"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                      -t padel-reservation-api:${BUILD_NUMBER} \
                      -t padel-reservation-api:latest \
                      .
                '''
            }
        }
    }
}