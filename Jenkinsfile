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
            sh 'cp -r ${WORKSPACE}/koa-node/* ${VOLUME}/koa-node'
        }
    }

    stage('Parallel build') {
        parallel {
            stage('Build sign-in-web') {
                steps {
                    sh 'pwd'
                    sh 'cd ./sign-in-web && npm install && npm run build'
                    sh 'rm -rf /web-code/sign-in-web/* && cp -r ./sign-in-web/dist/* /web-code/sign-in-web'
                }
            }
            
            stage('Build koa-node') {
                steps {
                    sh 'ssh -p 2233 root@124.223.91.248'
                    sh 'pwd'
                    sh 'git pull'
                    sh 'cd ${VOLUME}/koa-node && npm install && docker-compose down && docker-compose up -d'
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