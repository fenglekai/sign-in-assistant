pipeline {
  environment {
    VOLUME = "/code/sign-in-assistant"
    WEBCNG = "/sign-in-web/src/components"
    KOACNG = "/koa-node/public/javascripts"
  }

  agent {
    docker {
      image 'node:16'
      args '-v /code/sign-in-assistant":/code/sign-in-assistant":rw'
    }

  }
  stages {
    stage('Copy config') {
        steps {
            sh 'cp ${VOLUME}${WEBCNG}/httpUrl.js ${WORKSPACE}${WEBCNG}'
            sh 'cp ${VOLUME}${KOACNG}/config.js ${WORKSPACE}${KOACNG}'
        }
    }

    stage('Build sign-in-web') {
        steps {
            sh 'pwd'
            sh 'cd ./sign-in-web && npm install && npm run build'
            sh 'rm -rf /web-code/sign-in-web* && cp -r ./sign-in-web/dist/* /web-code/sign-in-web'
        }
    }
    
    stage('Build koa-node') {
        steps {
            sh 'cd ./koa-node && npm install && docker-compose down && docker-compose up -d'
        }
    }

    stage('Clean workspace') {
      steps {
        cleanWs(deleteDirs: true, cleanupMatrixParent: true, cleanWhenUnstable: true, cleanWhenSuccess: true, cleanWhenNotBuilt: true, cleanWhenFailure: true, cleanWhenAborted: true)
      }
    }

  }
}