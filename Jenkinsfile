pipeline {
  agent {
    docker {
      image 'node:16'
      args '-v /code/sign-in-assistant:/code/sign-in-assistant:rw'
    }

  }
  stages {
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