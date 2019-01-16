node('ETLdev') {
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
            stage ('Code Check'){
                tool name: 'appqa', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
                withSonarQubeEnv('CODEQA'){
                  // Run the sonar scanner
                  bat 'sonar-scanner.bat -Dsonar.sources=src -Dsonar.projectKey=%JOB_NAME% -Dsonar.host.url=%SONARURL% -Dsonar.python.pylint=%PYLINTPATH% -Dsonar.login=%SONARTOKEN% -Dsonar.python.pylint_config=config/pylint.config'
                  // Get the project id
                  pid = projectId()
                  echo "pid:" + pid
                  aid = analysisId(pid)
                  echo "aid:" + aid
                  env.qualityGateUrl = env.SONARURL + "/api/qualitygates/project_status?analysisId=" + aid
                  
                  sh 'curl -u $SONARTOKEN: $qualityGateUrl -o qualityGate.json'
                  def qualitygate = readJSON file: 'qualityGate.json'
                  echo qualitygate.toString()
                  if ("ERROR".equals(qualitygate["projectStatus"]["status"])) {
                      error  "Quality Gate failure"
                  }
                      echo  "Quality Gate success"
                  } 
            }                          
            stage('prep Virtualenv') {
                sh 'if [ -d "$VEDIR" ]; then rm -Rf $VEDIR; fi'
                sh 'pwd'
                bat '''
                    set TMP=%WORKSPACE%/data
                    set TEMP=%TMP%
                    python -m venv --clear %VEDIR%
                    call %VEDIR%/Scripts/activate.bat || goto :error
                    python -m pip install --upgrade pip || goto :error
                    pip install -r ./requirements.txt --cache-dir ./data || goto :error
                    
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

def projectId() {
    env.projectIdUrl = env.SONARURL + "/api/ce/component?component=" + env.JOB_NAME
    sh 'curl -u $SONARTOKEN: $projectIdUrl -o projectid.json'
    project = readJSON file: 'projectid.json'
    return project[ "current"][ "id" ]
}
def analysisId(id) {
    echo "input id:" + id
    env.taskIdUrl = env.SONARURL + "/api/ce/task?id=" + id
    sh 'curl -u $SONARTOKEN: $taskIdUrl -o taskid.json'
    task = readJSON file: 'taskid.json'
    return task[ "task" ][ "analysisId" ]
}
//"E:\\sw_nt\\Git\\bin","E:\\sw_nt\\Git\\bin","E:\\sw_nt\\Git\\mingw64\\bin",
def getWindowsPaths64() {
    myPath = ["E:\\sw_nt\\Git\\mingw64\\bin",
              "E:\\sw_nt\\oracle12c\\instantclient_12_2_32",
              "E:\\sw_nt\\Java\\jre1.8.0_161\\bin",
              "E:\\sw_nt\\Java\\jre1.8.0_161\\lib",
              "E:\\sw_nt\\arcgis\\Pro\\bin\\Python\\envs\\arcgispro-py3",
              "E:\\sw_nt\\arcgis\\Pro\\bin\\Python\\envs\\arcgispro-py3\\Scripts",
              "E:\\sw_nt\\sonar-scanner\\bin", 
              "E:\\sw_nt\\sonar-scanner\\lib"
              ]
    myPathStr = myPath.join(';')
    return myPathStr }


    
def notifyFailed() {
    emailext (
        subject: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
        body: """<p>FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':</p>
            <p>Check console output at "<a href="${env.BUILD_URL}">${env.JOB_NAME} [${env.BUILD_NUMBER}]</a>"</p>""",
        to: 'kevin.netherton@gov.bc.ca'
    )
}
    
