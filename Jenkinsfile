pipeline {
  environment {
    VOLUME = "/code/sign-in-assistant"
    WEBCNG = "/sign-in-web/src/components"
  }

  agent {
    docker {
      image 'node:16'
      args '-v /code/sign-in-assistant":/code/sign-in-assistant":rw -v /web-code/sign-in-web:/web-code/sign-in-web:rw'
    }
  }
  
  stages {
    stage('Copy files') {
        steps {
            sh 'cp ${VOLUME}${WEBCNG}/httpUrl.js ${WORKSPACE}${WEBCNG}'
        }
    }

    stage('Update npm') {
        steps {
            sh 'npm i -g npm@latest'
        }
    }


    stage('Build sign-in-web') {
        steps {
            sh 'cd ./sign-in-web && npm install && npm run build'
            sh 'rm -rf /web-code/sign-in-web/* && cp -r ./sign-in-web/dist/* /web-code/sign-in-web'
        }
    }

    stage('Clean workspace') {
      steps {
        cleanWs(deleteDirs: true, cleanupMatrixParent: true, cleanWhenUnstable: true, cleanWhenSuccess: true, cleanWhenNotBuilt: true, cleanWhenFailure: true, cleanWhenAborted: true)
      }
    }

  }
}