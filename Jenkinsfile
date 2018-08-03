pipeline {
  agent any
  stages {
    stage('git') {
      steps {
        git(url: 'ssh://git@gitlab.geekpark.net:2222/data/holoread.git', branch: 'develop')
      }
    }
    stage('build') {
      environment {
        DOCKER_IMAGE_NAME = 'gmirror/holoread:dev'
      }
      steps {
        sh 'docker ps'
      }
    }
  }
}