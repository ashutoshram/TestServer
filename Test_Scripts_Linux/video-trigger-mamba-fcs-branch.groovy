
pipeline {
    agent none

    stages {
        stage('prepare') {
            agent {
                docker {
                    label 'cameratestcupertino'
                    image "jabraesw/mamba-workspace:0.8"
                }
            }

            stages {
                stage('MAMBA_FCS_BRANCH') {
                    steps {
                        dir('platform') {
                            checkout([
                                $class: 'GitSCM',
                                branches: [[name: 'MAMBA_FCS_BRANCH']],
                                userRemoteConfigs: [[url: 'git@github.com:altiasystems/MX.git', credentialsId:'jenkins']]
                            ])
                        }
                        script {
                            if(currentBuild.changeSets.size() > 0) {
                                def changeLogSets = currentBuild.changeSets
                                def nrChanges = changeLogSets.size() + 1
                                currentBuild.description = nrChanges + " changes"
                                build job: 'video-test', parameters: [
                                    string(name: 'BRANCH', value: 'MAMBA_FCS_BRANCH'),
                                    booleanParam(name: 'DO_PYTHON', value: false),
                                    booleanParam(name: 'DO_MAMBA', value: true),
                                    booleanParam(name: 'RUN_ALL_TESTS', value: false),
                                    booleanParam(name: 'CAM_PROP_RAW', value: false),
                                    booleanParam(name: 'RES_SWITCH_RAW', value: true),
                                    booleanParam(name: 'RES_FPS_RAW', value: true)
                                ], wait: true
                            }
                        }
                    }
                }

            }

        }
    }
}
