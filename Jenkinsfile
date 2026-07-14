pipeline {
    agent any

    stages {
        stage('Test') {
            steps {
                sh '''
                    docker run --rm \
                      -v jenkins_home:/var/jenkins_home \
                      -w "$WORKSPACE" \
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
        
        stage('Deploy to Kubernetes') {
        steps {
            sh '''
                kubectl set image deployment/padel-api-deployment \
                  padel-api=padel-reservation-api:${BUILD_NUMBER}

                kubectl rollout status deployment/padel-api-deployment \
                  --timeout=120s
            '''
        }
    }

    }
}