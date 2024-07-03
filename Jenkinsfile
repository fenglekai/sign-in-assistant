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
            sh 'cd ./sign-in-web'
            sh 'npm install'
            sh 'npm run build'
            sh 'rm -rf /web-code/sign-in-web* && cp -r ./dist/* /web-code/sign-in-web'
        }
    }
    
    stage('Build koa-node') {
        steps {
            sh 'cd ./koa-node'
            sh 'npm install'
            sh 'docker-compose down && docker-compose up -d'
        }
    }

    stage('Clean workspace') {
      steps {
        cleanWs(deleteDirs: true, cleanupMatrixParent: true, cleanWhenUnstable: true, cleanWhenSuccess: true, cleanWhenNotBuilt: true, cleanWhenFailure: true, cleanWhenAborted: true)
      }
    }

  }
}