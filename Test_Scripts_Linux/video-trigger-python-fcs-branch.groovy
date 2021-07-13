
pipeline {
    agent none
    triggers {
        cron 'H/15 * * * *'
    }

    stages {
        stage('prepare') {
            agent {
                docker {
                    label 'cameratestcupertino'
                    image "jabraesw/mamba-workspace:0.8"
                }
            }

            stages {

                stage('python-fcs') {
                    steps {
                        dir('platformfcs') {
                            checkout([
                                $class: 'GitSCM',
                                branches: [[name: 'PYTHON_FCS_BRANCH']],
                                userRemoteConfigs: [[url: 'git@github.com:altiasystems/MX.git', credentialsId:'jenkins']]
                            ])
                        }
                        script {
                            if(currentBuild.changeSets.size() > 0) {
                                def changeLogSets = currentBuild.changeSets
                                def nrChanges = changeLogSets.size() + 1
                                currentBuild.description = nrChanges + " changes"
                                build job: 'video-test', parameters: [
                                    string(name: 'BRANCH', value: 'PYTHON_FCS_BRANCH'),
                                    booleanParam(name: 'DO_PYTHON', value: true),
                                    booleanParam(name: 'DO_MAMBA', value: false),
                                    booleanParam(name: 'RUN_ALL_TESTS', value: true)
                                ], wait: true

                            }
                        }
                    }
                }

            }

        }
    }
}
