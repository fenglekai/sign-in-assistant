pipeline {
  agent {
    docker {
      image 'node:16'
      args '-v /code/sign-in-assistant:/code/sign-in-assistant:rw'
    }

  }
  stages {
    stage('cd sign-in-web') {
        steps {
            sh 'cd ./sign-in-web'
        }
    }

    stage('Web initial') {
        steps {
            sh 'npm install'
        }
    }

    stage('Web build') {
        steps {
            sh 'npm run build'
        }
    }

    stage('Update file to nginx') {
        steps {
            sh 'rm -rf /web-code/sign-in-web* && cp -r ./dist/* /web-code/sign-in-web'
        }
    }
    
    stage('cd koa-node') {
        steps {
            sh 'cd ../koa-node'
        }
    }

    stage('Koa initial') {
        steps {
            sh 'npm install'
        }
    }

    stage('Koa build') {
        steps {
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