
pipeline {
    agent {
        label 'eswlinuxdocker'
    }

    environment {
        PLATFORM_REPO = "git@github.com:altiasystems/MX.git"
        PYTHON_VIDEO_PATH = "newport/python_video"
        MAMBA_VIDEO_PATH = "newport/mamba_video"
        BASEVERSIONFILE = "newport/solaris2/myriadx/include/version_history.h"
        FILES_CHANGED = "---"
        TEST_REPORT = "---"
        CHECK_PATH = "newport"
        NEW_GERRIT_COMMIT_MSG = "---"
        NOTIFICATION_EMAILS = "arigo@jabra.com, tthai@jabra.com, johzhang@jabra.com, khtran@jabra.com, aram@jabra.com"
    }

    parameters {
        choice(name: 'BRANCH', choices: ['master', 'PYTHON_FCS_BRANCH', 'MAMBA_FCS_BRANCH'])
        booleanParam(defaultValue: true, name: 'DO_PYTHON', description: 'Build Python')
        booleanParam(defaultValue: false, name: 'DO_MAMBA', description: 'Build Mamba')
        booleanParam(defaultValue: true, name: 'RUN_ALL_TESTS')
        booleanParam(defaultValue: false, name: 'CAM_PROP_RAW')
        booleanParam(defaultValue: false, name: 'RES_SWITCH_RAW')
        booleanParam(defaultValue: false, name: 'RES_FPS_RAW')
        // booleanParam(defaultValue: false, name: 'CAM_PROP_MJPG')
        booleanParam(defaultValue: false, name: 'RES_SWITCH_MJPG')
        booleanParam(defaultValue: false, name: 'RES_FPS_MJPG')
    }

    stages {

        stage('checkout') {
            steps {
                script {
                    sh "rm -rf ${WORKSPACE}/cilogs"
                    sh "rm -rf ${WORKSPACE}/logfiles"
                    sh "mkdir -p ${WORKSPACE}/cilogs"
                }
                dir("platform${BRANCH}") {
                    checkout([
                        $class: 'GitSCM',
                        branches: [[name: BRANCH]],
                        userRemoteConfigs: [[url: PLATFORM_REPO, credentialsId:'jenkins']]
                    ])
                }
            }
        }

        stage('check commits') {
            steps {
                dir("platform${BRANCH}") {
                    script {
                        MYRIADX_VERSION = """${sh (
                            returnStdout: true,
                            script: ' \
                                BASEVERSIONFILE=${BASEVERSIONFILE} ; \
                                MAJOR=\$(cat \$BASEVERSIONFILE | grep "#define MAJOR_NUMBER" | sed s"/[^\\s]*\\s\\+//") ; \
                                MINOR=\$(cat \$BASEVERSIONFILE | grep "#define MINOR_NUMBER" | sed s"/[^\\s]*\\s\\+//") ; \
                                BUILD=\$(cat \$BASEVERSIONFILE | grep "#define BUILD_NUMBER" | sed s"/[^\\s]*\\s\\+//") ; \
                                echo "\$MAJOR.\$MINOR.\$BUILD"'
                        ).trim()}"""
                        currentBuild.description = "${BRANCH}<br>\nMyriadx: ${MYRIADX_VERSION}<br>\n${currentBuild.buildCauses.shortDescription}"

                        if(currentBuild.changeSets.size() > 0) {
                            def changeLogSets = currentBuild.changeSets
                            def nrChanges = changeLogSets.size() + 1
                            for (int i = 0; i < changeLogSets.size(); i++) {
                                echo "==============================="
                                def entries = changeLogSets[i].items
                                for (int j = 0; j < entries.length; j++) {
                                    echo "-------------------------------"
                                    def entry = entries[j]
                                    echo "${entry.commitId} by ${entry.author}: ${entry.msg}"

                                    // Check the commit message
                                    // REGEX_ISSUE_ID = '[A-Z]{3,}-[0-9]+'
                                    // echo "${entry.comment}"

                                    // Check if this is a change that should trigger move to Gerrit
                                    def files = new ArrayList(entry.affectedFiles)
                                    for (int k = 0; k < files.size(); k++) {
                                        def file = files[k]
                                        echo "  ${file.editType.name} ${file.path}"
                                        if (CHECK_PATH == "" || file.path.startsWith(CHECK_PATH)) {
                                            FILES_CHANGED = "${FILES_CHANGED}\n  ${file.editType.name} ${file.path}"
                                        }
                                    }

                                    NEW_GERRIT_COMMIT_MSG = "${NEW_GERRIT_COMMIT_MSG}\n\nMX/commit: ${entry.commitId}\nAuthor ${entry.author.toString()} <${entry.authorEmail}>\n${entry.comment}\n---"
                                    // Check who to notify if something fails
                                    NOTIFICATION_EMAILS = "${NOTIFICATION_EMAILS}, ${entry.authorEmail}"
                                }
                            }

                            echo "NOTIFICATION_EMAILS: ${NOTIFICATION_EMAILS}"
                            echo "NEW_GERRIT_COMMIT_MSG"
                            echo "${NEW_GERRIT_COMMIT_MSG}"

                        }
                    }
                }
            }
        }

        stage('python build') {
            when {
                expression {
                    params.DO_PYTHON == true
                }
            }
            steps {
                script {
                    docker.image("jabraesw/mamba-workspace:latest").inside {
                        dir("platform${BRANCH}") {
                            sh """
                                cd ${PYTHON_VIDEO_PATH}
                                make -f mvMakefile.mk prepare-kconfig
                                make cleanall
                                make -j \$(nproc)
                            """
                        }
                        dir("platform${BRANCH}/${PYTHON_VIDEO_PATH}/mvbuild/ma2085") {
                            stash includes: 'python_video.mvcmd', name: 'python_video'
                        }
                    }
                }
            }
        }

        stage('mamba build') {
            when {
                expression {
                    params.DO_MAMBA == true
                }
            }
            steps {
                script {
                    docker.image("jabraesw/mamba-workspace:latest").inside {
                        dir("platform${BRANCH}") {
                            sh """
                                cd ${MAMBA_VIDEO_PATH}
                                make -f mvMakefile.mk prepare-kconfig
                                make cleanall
                                make -j \$(nproc)
                            """
                        }
                        dir("platform${BRANCH}/${MAMBA_VIDEO_PATH}/mvbuild/ma2085") {
                            stash includes: 'mamba_video.mvcmd', name: 'mamba_video'
                        }
                    }
                }
            }
        }

        stage('tests') {
            parallel {

                stage('mamba raw') {
                    when {
                        expression {
                            params.DO_MAMBA == true
                        }
                    }
                    stages {
                        stage('mamba raw') {
                            options {
                                lock resource: 'devkit02-mamba'
                            }
                            agent {
                                label 'devkit02'
                            }
                            when {
                                expression {
                                    params.RUN_ALL_TESTS == true || params.CAM_PROP_RAW == true || params.RES_SWITCH_RAW == true || params.RES_FPS_RAW == true
                                }
                            }
                            stages {
                                stage('test mamba on devkit02') {
                                    steps {
                                        script {
                                            sh "rm -rf result"
                                            sh "mkdir result"
                                            sh "rm -rf ${WORKSPACE}/testscripts"
                                            dir('testscripts') {
                                                checkout([
                                                    $class: 'GitSCM',
                                                    userRemoteConfigs: [[url: 'git@github.com:ashutoshram/TestServer.git']]
                                                ])
                                                unstash 'mamba_video'
                                                sh """
                                                    cd Test_Scripts_Linux
                                                    pip3 install numpy -I
                                                    pip3 install -r requirements.txt

                                                    ./mambaAutoUpdater.sh ../mamba_video.mvcmd
                                                    #// sleep 10m
                                                """
                                            }
                                        }
                                    }
                                }
                                stage('cam prop controls') {
                                    when {
                                        expression {
                                            params.RUN_ALL_TESTS == true || params.CAM_PROP_RAW == true
                                        }
                                    }
                                    steps {
                                        dir('testscripts') {
                                            sh """
                                                cd Test_Scripts_Linux
                                                python3 CamPropControls.py -d True -v "Jabra PanaCast 20"
                                            """
                                        }
                                        dir('testscripts/Test_Scripts_Linux/CamPropControls') {
                                            sh """
                                                find . -name "*.log" -print | xargs -I file basename file | xargs -I f mv f ${WORKSPACE}/result/raw-f
                                            """
                                        }
                                    }
                                }
                                stage('resolution switch') {
                                    when {
                                        expression {
                                            params.RUN_ALL_TESTS == true || params.RES_SWITCH_RAW == true
                                        }
                                    }
                                    steps {
                                        dir('testscripts') {
                                            sh """
                                                cd Test_Scripts_Linux
                                                python3 ResolutionSwitch.py -d True -p True -t res_switch_p20.json -v "Jabra PanaCast 20"
                                            """
                                        }
                                        dir('testscripts/Test_Scripts_Linux/resolutionswitch') {
                                            sh """
                                                find . -name "*.log" -print | xargs -I file basename file | xargs -I f mv f ${WORKSPACE}/result/raw-f
                                            """
                                        }
                                    }
                                }
                                stage('resolution fps') {
                                    when {
                                        expression {
                                            params.RUN_ALL_TESTS == true || params.RES_FPS_RAW == true
                                        }
                                    }
                                    steps {
                                        dir('testscripts') {
                                            sh """
                                                cd Test_Scripts_Linux
                                                python3 ResolutionFPS_cv2.py -d True -p True -t res_fps_p20.json -v "Jabra PanaCast 20"
                                            """
                                        }
                                        dir('testscripts/Test_Scripts_Linux/resolutionfps') {
                                            sh """
                                                find . -name "*.log" -print | xargs -I file basename file | xargs -I f mv f ${WORKSPACE}/result/raw-f
                                            """
                                        }
                                    }
                                }
                                stage('collect results') {
                                    steps {
                                        dir('result') {
                                            stash includes: '*.log', name: 'raw-test'
                                        }
                                        deleteDir() /* clean up our workspace */
                                    }
                                }
                            }
                        }
                    }
                }

                stage('python raw') {
                    when {
                        expression {
                            params.DO_PYTHON == true
                        }
                    }
                    stages {
                        stage('python raw') {
                            options {
                                lock resource: 'devkit02-python'
                            }
                            agent {
                                label 'devkit02'
                            }
                            when {
                                expression {
                                    params.RUN_ALL_TESTS == true || params.CAM_PROP_RAW == true || params.RES_SWITCH_RAW == true || params.RES_FPS_RAW == true
                                }
                            }
                            stages {
                                stage('test raw on devkit02') {
                                    steps {
                                        script {
                                            sh "rm -rf result"
                                            sh "mkdir result"
                                            sh "rm -rf ${WORKSPACE}/testscripts"
                                            dir('testscripts') {
                                                checkout([
                                                    $class: 'GitSCM',
                                                    userRemoteConfigs: [[url: 'git@github.com:ashutoshram/TestServer.git']]
                                                ])
                                                unstash 'python_video'
                                                sh """
                                                    cd Test_Scripts_Linux
                                                    pip3 install numpy -I
                                                    pip3 install -r requirements.txt

                                                    cd ..
                                                    adb devices
                                                    adb push python_video.mvcmd /data/python_video.mvcmd
                                                    adb shell killall -9 newport
                                                    sleep 8m
                                                """
                                            }
                                        }
                                    }
                                }
                                stage('cam prop controls') {
                                    when {
                                        expression {
                                            params.RUN_ALL_TESTS == true || params.CAM_PROP_RAW == true
                                        }
                                    }
                                    steps {
                                        dir('testscripts') {
                                            sh """
                                                cd Test_Scripts_Linux
                                                python3 CamPropControls.py -d True
                                            """
                                        }
                                        dir('testscripts/Test_Scripts_Linux/CamPropControls') {
                                            sh """
                                                find . -name "*.log" -print | xargs -I file basename file | xargs -I f mv f ${WORKSPACE}/result/raw-f
                                            """
                                        }
                                    }
                                }
                                stage('resolution switch') {
                                    when {
                                        expression {
                                            params.RUN_ALL_TESTS == true || params.RES_SWITCH_RAW == true
                                        }
                                    }
                                    steps {
                                        dir('testscripts') {
                                            sh """
                                                cd Test_Scripts_Linux
                                                python3 ResolutionSwitch.py -d True -p True
                                            """
                                        }
                                        dir('testscripts/Test_Scripts_Linux/resolutionswitch') {
                                            sh """
                                                find . -name "*.log" -print | xargs -I file basename file | xargs -I f mv f ${WORKSPACE}/result/raw-f
                                            """
                                        }
                                    }
                                }
                                stage('resolution fps') {
                                    when {
                                        expression {
                                            params.RUN_ALL_TESTS == true || params.RES_FPS_RAW == true
                                        }
                                    }
                                    steps {
                                        dir('testscripts') {
                                            sh """
                                                cd Test_Scripts_Linux
                                                python3 ResolutionFPS_cv2.py -d True -p True
                                            """
                                        }
                                        dir('testscripts/Test_Scripts_Linux/resolutionfps') {
                                            sh """
                                                find . -name "*.log" -print | xargs -I file basename file | xargs -I f mv f ${WORKSPACE}/result/raw-f
                                            """
                                        }
                                    }
                                }
                                stage('collect results') {
                                    steps {
                                        dir('result') {
                                            stash includes: '*.log', name: 'raw-test'
                                        }
                                        deleteDir() /* clean up our workspace */
                                    }
                                }
                            }
                        }
                    }
                }

                stage('python mjpg') {
                    when {
                        expression {
                            params.DO_PYTHON == true
                        }
                    }
                    stages {
                        stage('python mjpg') {
                            options {
                                lock resource: 'altiavideo02-python'
                            }
                            agent {
                                label 'altiavideo02'
                            }
                            when {
                                expression {
                                    params.RUN_ALL_TESTS == true || params.CAM_PROP_MJPG == true || params.RES_SWITCH_MJPG == true || params.RES_FPS_MJPG == true
                                }
                            }
                            stages {
                                stage('test mjpg on altiavideo02') {
                                    steps {
                                        script {
                                            sh "rm -rf result"
                                            sh "mkdir result"
                                            sh "rm -rf ${WORKSPACE}/testscripts"
                                            dir('testscripts') {
                                                checkout([
                                                    $class: 'GitSCM',
                                                    userRemoteConfigs: [[url: 'git@github.com:ashutoshram/TestServer.git']]
                                                ])
                                                unstash 'python_video'
                                                sh """
                                                    cd Test_Scripts_Linux
                                                    pip3 install numpy -I
                                                    pip3 install -r requirements.txt

                                                    cd ..
                                                    adb devices
                                                    adb push python_video.mvcmd /data/python_video.mvcmd
                                                    adb shell killall -9 newport
                                                    sleep 10m
                                                """
                                            }
                                        }
                                    }
                                }

                                // stage('cam prop controls') {
                                //     when {
                                //         expression {
                                //             params.RUN_ALL_TESTS == true || params.CAM_PROP_MJPG == true
                                //         }
                                //     }
                                //     steps {
                                //         dir('testscripts') {
                                //             sh """
                                //                 cd Test_Scripts_Linux
                                //                 python3 CamPropControls.py -d True -p True
                                //             """
                                //         }
                                //         dir('testscripts/Test_Scripts_Linux/CamPropControls') {
                                //             sh """
                                //                 find . -name "*.log" -print | xargs -I file basename file | xargs -I f mv f ${WORKSPACE}/result/mjpg-f
                                //             """
                                //         }
                                //     }
                                // }

                                stage('resolution switch') {
                                    when {
                                        expression {
                                            params.RUN_ALL_TESTS == true || params.RES_SWITCH_MJPG == true
                                        }
                                    }
                                    steps {
                                        dir('testscripts') {
                                            sh """
                                                cd Test_Scripts_Linux
                                                python3 ResolutionSwitch.py -d True -p True -t res_switch_mjpg.json
                                            """
                                        }
                                        dir('testscripts/Test_Scripts_Linux/resolutionswitch') {
                                            sh """
                                                find . -name "*.log" -print | xargs -I file basename file | xargs -I f mv f ${WORKSPACE}/result/mjpg-f
                                            """
                                        }
                                    }
                                }
                                stage('resolution fps') {
                                    when {
                                        expression {
                                            params.RUN_ALL_TESTS == true || params.RES_FPS_MJPG == true
                                        }
                                    }
                                    steps {
                                        dir('testscripts') {
                                            sh """
                                                cd Test_Scripts_Linux
                                                python3 ResolutionFPS_cv2.py -d True -p True -t res_fps_mjpg.json
                                            """
                                        }
                                        dir('testscripts/Test_Scripts_Linux/resolutionfps') {
                                            sh """
                                                find . -name "*.log" -print | xargs -I file basename file | xargs -I f mv f ${WORKSPACE}/result/mjpg-f
                                            """
                                        }
                                    }
                                }
                                stage('collect results') {
                                    steps {
                                        dir('result') {
                                            stash includes: '*.log', name: 'mjpg-test'
                                        }
                                        deleteDir() /* clean up our workspace */
                                    }
                                }

                            }
                        }
                    }
                }

            }
        }

    }
    post {
        always {
            echo 'One way or another, I have finished'

            writeFile file: "cilogs/files_changed.log", text: "${FILES_CHANGED}"
            script {
                FILES_CHANGED = """${sh (
                    returnStdout: true,
                    script: 'cat cilogs/files_changed.log | sort | uniq ').trim()}"""
            }
            echo "${FILES_CHANGED}"

            dir('logfiles') {
                script {
                    try {
                        unstash 'raw-test'
                    } catch (Exception e) {
                        echo 'No results from raw-test'
                    }
                    try {
                        unstash 'mjpg-test'
                    } catch (Exception e) {
                        echo 'No results from mjpg-test'
                    }
                    TEST_REPORT = """${sh (
                        returnStdout: true,
                        script: 'find . -name "*failed_resolutionfps_p50.log" -o -name "*failed_resolutionfps_p20.log" -o -name "*failed_resolutionswitch_p50.log" -o -name "*failed_resolutionswitch_p20.log" | xargs cat').trim()}"""
                    if ( TEST_REPORT != "" ) {
                        TEST_REPORT = "Failed tests:\n ${TEST_REPORT}"
                    }
                }
                echo "${TEST_REPORT}"
            }

            echo "${NOTIFICATION_EMAILS}"
            writeFile file: "cilogs/notification.log", text: "${NOTIFICATION_EMAILS}"
            echo "${NEW_GERRIT_COMMIT_MSG}"
            writeFile file: "cilogs/commit-messages.log", text: "${NEW_GERRIT_COMMIT_MSG}"

            archiveArtifacts artifacts: '**/logfiles/**/*.log, **/cilogs/**/*.log', allowEmptyArchive: true

            script {
                CURRENT_PARAMETERS = ""
                params.each {param ->
                    CURRENT_PARAMETERS = CURRENT_PARAMETERS + " ${param.key}: ${param.value}\n"
                }
            }

            // send email
            emailext attachmentsPattern: '**/logfiles/**/*.log',
            body: """${currentBuild.currentResult}: ${BRANCH} Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':
Check console output at ${env.BUILD_URL}

${TEST_REPORT}

Changes:
${NEW_GERRIT_COMMIT_MSG}

Changed files:
${FILES_CHANGED}

---
---

${CURRENT_PARAMETERS}

""",
            subject: "Jenkins test video: ${BRANCH} [${env.BUILD_NUMBER}] ${currentBuild.currentResult}",
            to: "${NOTIFICATION_EMAILS}"

            deleteDir() /* clean up our workspace */
        }
        success {
            echo 'I succeeded!'
        }
        unstable {
            echo 'I am unstable :/'
        }
        failure {
            echo 'I failed :('
        }
        changed {
            echo 'Things were different before...'
        }
    }

}
