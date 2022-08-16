node('etl-test') {
    try{
        winPaths=getWindowsPaths64()
        //  "PYLINTPATH=E:/sw_nt/python27/python2.7.14/Scripts/pylint.exe", 
        withEnv([
                 "JOB_NAME=ReplicationHealthCheck", 
                 "VEDIR=ve",
                 "TEMP=$WORKSPACE\\tmp",
                 "TMP=$WORKSPACE\\tmp",
                 "PATH+EXTRA=${winPaths}",
                 ]) {
            stage('checkout') {
                sh 'if [ ! -d "$TEMP" ]; then mkdir $TEMP; fi'
                checkout([$class: 'GitSCM', branches: [[name: "${env.TAGNAME}"]], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'SubmoduleOption', disableSubmodules: false, parentCredentials: true, recursiveSubmodules: true, reference: '', trackingSubmodules: false]], gitTool: 'Default', submoduleCfg: [], userRemoteConfigs: [[credentialsId: '607141bd-ef34-4e80-8e7e-1134b7c77176', url: 'https://github.com/bcgov/replication_health_check']]])
            }                   
            stage('prep Virtualenv') {
                sh 'if [ -d "$VEDIR" ]; then rm -Rf $VEDIR; fi'
                sh 'pwd'
                bat '''
                    set TMP=%WORKSPACE%/data
                    set TEMP=%TMP%
                    python -m venv --clear %VEDIR%
                    call %VEDIR%/Scripts/activate.bat || goto :error
                    REM python -m pip install --upgrade pip || goto :error
                    python -m pip install -r ./requirements.txt --cache-dir ./data || goto :error
                    
                    :error
                    echo Failed with error #%errorlevel%.
                    exit /b %errorlevel%
                '''
            }
            stage('Run') {
                bat '''
                    set
                    set TMP=%WORKSPACE%/data
                    set TEMP=%TMP%
                    call ve/Scripts/activate.bat || goto :error
                    cd src
                    python main.py || goto :error
                    
                    :error
                    echo Failed with error #%errorlevel%.
                    exit /b %errorlevel%
                '''
            }
        }
    } catch (e) {
        currentBuild.result = "FAILED"
        notifyFailed()
        throw e
    }
}

//"E:\\sw_nt\\Git\\bin","E:\\sw_nt\\Git\\bin","E:\\sw_nt\\Git\\mingw64\\bin",
def getWindowsPaths64() {
    myPath = ["E:\\sw_nt\\Git\\mingw64\\bin",
              "E:\\sw_nt\\oracle12c\\!instantclient_12_2",
              "E:\\sw_nt\\java\\jdk8u172-b11\\bin",
              "E:\\sw_nt\\java\\jdk8u172-b11\\lib",
              "E:\\sw_nt\\arcgis\\Pro\\bin\\Python\\envs\\arcgispro-py3",
              "E:\\sw_nt\\arcgis\\Pro\\bin\\Python\\envs\\arcgispro-py3\\Scripts",
              ]
    myPathStr = myPath.join(';')
    return myPathStr }
    
def notifyFailed() {
    emailext (
        subject: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
        body: """<p>FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':</p>
            <p>Check console output at "<a href="${env.BUILD_URL}">${env.JOB_NAME} [${env.BUILD_NUMBER}]</a>"</p>""",
        to: 'dataetl@gov.bc.ca'
    )
}
    
