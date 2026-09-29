pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        PYTHONUNBUFFERED = '1'
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh 'python3 -m compileall -q src tests'
                sh 'docker compose config > /dev/null'
                sh 'docker compose build'
            }
        }

        stage('Test') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    python -m pip install --upgrade pip
                    pip install -r requirements-dev.txt
                    mkdir -p reports
                    pytest -m "not integration and not selenium and not performance" \
                      --html=reports/pytest-report.html --self-contained-html \
                      --junitxml=reports/junit.xml
                '''
            }
        }

        stage('Deploy staging') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    if [ -z "$STAGING_DEPLOY_HOOKS" ]; then
                      echo "STAGING_DEPLOY_HOOKS no está configurado. Configure el secreto en Jenkins para activar el despliegue."
                      exit 1
                    fi
                    bash scripts/deploy_staging.sh
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
            junit testResults: 'reports/junit.xml', allowEmptyResults: true
        }
        success {
            echo 'Pipeline CI/CD completado correctamente.'
        }
        failure {
            echo 'Pipeline falló. Conserve esta ejecución como evidencia de control de calidad.'
        }
    }
}
