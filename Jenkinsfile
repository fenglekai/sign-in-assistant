pipeline {
  environment {
    VOLUME = "/code/sign-in-assistant"
    WEBCNG = "/sign-in-web/src/components"
    KOACNG = "/koa-node/public/javascripts"
  }

  agent any

  stages {
    stage('Parallel build') {
        parallel {
            stage('Build sign-in-web') {
                steps {
                    sh 'nvm use 16'
                    sh 'cd ./sign-in-web && npm install && npm run build'
                    sh 'rm -rf /web-code/sign-in-web/* && cp -r ./sign-in-web/dist/* /web-code/sign-in-web'
                }
            }
            
            stage('Build koa-node') {
                steps {
                    sh 'nvm use 16'
                    sh 'cd ${VOLUME}/koa-node && git pull && npm install && docker-compose down && docker-compose up -d'
                }
            }
        }
    }

    stage('Clean workspace') {
      steps {
        cleanWs(deleteDirs: true, cleanupMatrixParent: true, cleanWhenUnstable: true, cleanWhenSuccess: true, cleanWhenNotBuilt: true, cleanWhenFailure: true, cleanWhenAborted: true)
      }
    }

  }
}