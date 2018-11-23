'''
Created on Nov 22, 2018

@author: kjnether

methods that evaluate the given schedule
'''

import logging
import FMEUtil.FMEServerApiData

class EvaluateSchedule(object):

    def __init__(self, schedulesData):
        self.logger = logging.getLogger(__name__)
        if not isinstance(schedulesData, FMEUtil.FMEServerApiData.Schedules):
            msg = 'arg schedulesData should be type FMEUtil.FMEServerAp' + \
                  'iData.Schedules instead its a type {0}'
            msg = msg.format(type(schedulesData))
            raise ValueError(msg)
        self.schedule = schedulesData
        
    def getDisabled(self):
        '''
        :return: a list of schedules that are currently disabled
        '''
        disableList = []
        for schedule in self.schedule:
            if not schedule.isEnabled():
                disableList.append(schedule)
        return disableList
    
    def getDisableEmailStr(self):
        disabled = self.getDisabled()
        msgList = []
        msg = 'LIST OF CURRENTLY DISABLED SCHEDULES (SCHEDULE/REPO/FMW)'
        delim = '-' * len(msg)
        msgList.append(msg)
        msgList.append(delim)
        #dataTmplt = ' - {0:>55}, {1:>15}, {2:>55}'
        # iterate through the data so we can get the longest 
        # entry for proper formatting
        dataList = []
        dataLen = []
        # getting the longest value for each column
        for sched in disabled:
            fmw = sched.getFMWName()
            repo = sched.getRepository()
            schedName = sched.getScheduleName()
            dataList.append([schedName, repo, fmw])
            if not dataLen:
                dataLen = [len(schedName), len(repo), len(fmw)]
            else:
                if len(schedName) > dataLen[0]:
                    dataLen[0] = len(schedName)
                elif len(repo) > dataLen[1]:
                    dataLen[1] = len(repo)
                elif len(fmw) > dataLen[2]:
                    dataLen[2] = len(fmw)
        # create a format string that will fit all the items
        dataTmplt = u' - {0:>' + unicode(dataLen[0]) + u'}, ' + \
                    u'{1:>' + unicode(dataLen[1]) + u'}, ' + \
                     u'{2:>' + unicode(dataLen[2]) + u'} '
        self.logger.debug("format string: %s", dataTmplt)
        # converting the data into a nicely formatted string.
        for dataLine in dataList:
            newLine = dataTmplt.format(dataLine[0], dataLine[1], dataLine[2])
            msgList.append(newLine)
        # append each line in the msg list into a carriage return delimited
        # string
        msgStr = '\n'.join(msgList)
        return msgStr
    
    def compareRepositorySchedule(self, workspacesData):
        '''
        identifies FMW's in the workspaces ( workspacesData) that are not
        associated with a a schedule.
        
        :param workspacesData: a fmeserver data api workspaces object that 
                               is to be compared against the schedule data
        :type workspacesData: FMEUtil.FMEServerApiData.Workspaces
        '''
        notScheduled = []
        for workspace in workspacesData:
            repoName = workspace.getRepositoryName()
            workspaceName = workspace.getWorkspaceName()
            scheduleName = self.schedule.getFMWRepositorySchedule(
                repositoryName=repoName, fmwName=workspaceName)
            if scheduleName is None:
                notScheduled.append(workspaceName)
        return notScheduled
            
            