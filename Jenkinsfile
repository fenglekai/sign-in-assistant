pipeline {
  environment {
    VOLUME = "/code/sign-in-assistant"
    WEBCNG = "/sign-in-web/src/components"
  }

  agent {
    docker {
      image 'node:16'
      args '-v /code/sign-in-assistant":/code/sign-in-assistant":rw -v /web-code/sign-in-web:/web-code/sign-in-web:rw --network=host'
    }
  }
  
  stages {
    stage('Copy files') {
        steps {
            sh 'cp ${VOLUME}${WEBCNG}/httpUrl.js ${WORKSPACE}${WEBCNG}'
        }
    }

    stage('Set npm configure') {
        steps {
            sh 'npm config set registry https://registry.npmmirror.com'
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