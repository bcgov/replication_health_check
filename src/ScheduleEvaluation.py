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
            
            
    def getUnsheduledRepoFMWsStr(self):
        

            