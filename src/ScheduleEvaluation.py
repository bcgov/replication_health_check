'''
Created on Nov 22, 2018

@author: kjnether

methods that evaluate the given schedule
'''

import logging
import FMEUtil.FMEServerApiData
import re


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
                fmw = schedule.getFMWName()
                repo = schedule.getRepository()
                schedName = schedule.getScheduleName()
                disableList.append([schedName, repo, fmw])
        # sort by the fmw name
        disableList.sort(key=lambda x: x[0])

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
        notScheduled.sort()
        return notScheduled

    def getEmbeddedData(self):
        '''
        identifies dataset that probably should be sourcing info from the
        staging area but instead are sourcing from some other location
        '''
        searchRegex = re.compile('^\$\(FME_MF_\w*\).*$')
        schedEmbeds = []
        self.schedule.reset()
        for schedule in self.schedule:
            pubparams = schedule.getPublishedParameters()
            schedName = schedule.getScheduleName()
            for pubparam in pubparams:
                paramName = pubparam.getName()
                paramValue = pubparam.getValue()
                self.logger.debug("paramName: %s", paramName)
                self.logger.debug("paramValue: %s", paramValue)
                if isinstance(paramValue, list):
                    paramValue = ', '.join(paramValue)
                    self.logger.info("list param as string: %s", paramValue)
                if searchRegex.match(paramValue):
                    schedEmbeds.append([schedName, paramName, paramValue])
        schedEmbeds.sort(key=lambda x: x[0])
        return schedEmbeds

    def getNonProdSchedules(self):
        '''
        iterates through the schedules returning a list of lists, where
        the inner list contains the:

        - FMW Name
        - Value that DEST_DB_ENV_KEY is set to. Returns None if the parameter
          doesn't exist at all.
        '''
        filterList = ['OTHR', 'PRD', 'DBCPRD', 'OTHER']
        filteredScheds = self.getSchedsFilterByDestDbEnvKey(filterList,
                                                            includeNull=True)
        nonProdList = []
        for schedule in filteredScheds:
            scheduleName = schedule.getScheduleName()
            fmw = schedule.getFMWName()
            scheduleName = schedule.getScheduleName()
            fmw = schedule.getFMWName()
            if fmw.upper() != 'APP_KIRK__FGDB.FMW':
                pubparams = schedule.getPublishedParameters()
                destDbEnvKey = pubparams.getDestDbEnvKey()
                nonProdList.append([scheduleName, destDbEnvKey])
        nonProdList.sort(key=lambda x: x[0])
        return nonProdList

    def getSchedsFilterByDestDbEnvKey(self, envKeysToExclude, includeNull=False):
        '''
        returns a filtered list based on the parameters identified, does 
        not include KIRK jobs

        :param envKeysToExclude: Schedules that are configured with these
                                 values will be excluded from the list
        :type envKeysToExclude: list of  strings
        :param includeNull: whether replication scripts that do not have
                            a DEST_DB_ENV_KEY defined for them should be
                            included in the replication.
        :type includeNull:
        '''
        envKeysToExcludeUC = [element.upper() for element in
                              envKeysToExclude]
        filterList = []
        self.schedule.reset()
        for schedule in self.schedule:
            scheduleName = schedule.getScheduleName()
            fmw = schedule.getFMWName()
            if fmw.upper() != 'APP_KIRK__FGDB.FMW':
                pubparams = schedule.getPublishedParameters()
                destDbEnvKey = pubparams.getDestDbEnvKey()
                if destDbEnvKey is None and includeNull:
                    filterList.append(schedule)
                elif isinstance(destDbEnvKey, list):
                    if len(destDbEnvKey) == 1:
                        destDbEnvKey = destDbEnvKey[0]
                    else:
                        msg = 'The schedule {0} is configured with ' + \
                              "multiple DEST_DB_ENV_KEYS, uncertain " + \
                              "which key to use.  The fmw associated " + \
                              'with the job is {1}'
                        msg = msg.format(scheduleName, fmw)
                        raise ValueError(msg)
                if destDbEnvKey is not None and destDbEnvKey.upper() \
                        not in envKeysToExcludeUC:
                    filterList.append(schedule)
        return filterList

    def getAllBCGWDestinations(self):
        '''
        retrieves all the BCGW destinations, to retrieve these they MUST
        have the DEST_DB_ENV_KEY defined for them
        '''
        filterList = ['OTHR', 'OTHER']
        filteredSchedules = self.getSchedsFilterByDestDbEnvKey(envKeysToExclude=filterList)
        return filteredSchedules
    