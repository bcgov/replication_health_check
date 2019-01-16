'''
Created on Nov 22, 2018

@author: kjnether

This module is the coordinator between credentials and data retrieval
methods:


 '''
import logging
import DBCSecrets.GetSecrets
import FMEUtil.PyFMEServerV3 as PyFMEServer
import KirkUtil.PyKirk
import FMEUtil.FMEServerApiData
import Constants
import pprint


class GetData(object):

    def __init__(self, env):
        self.logger = logging.getLogger(__name__)
        self.env = env

        self.fme = None
        self.kirk = None

        # schedules can be used by more than one query here
        # so the results are cached.
        self.schedules = None

    def getKIRK(self):
        '''
        retrieves the credentials required to communicate with KIRK and
        returns the wrapper object
        :return: a reference to the kirk api python wrapper
        :rtype: KirkUtil.PyKirk.Kirk

        '''
        if self.kirk is None:
            secrets = DBCSecrets.GetSecrets.CredentialRetriever()
            kirkLabel = Constants.KIRKSECRETLABEL_TEMPLATE.format(
                self.env).upper()

            kirkAccnt = secrets.getSecretsByLabel(kirkLabel)
            kirkHost = kirkAccnt.getHost()
            kirkToken = kirkAccnt.getAPI()
            kirkUrl = 'https://{0}'.format(kirkHost)
            self.logger.debug('kirk baseurl: {0}'.format(kirkUrl))
            self.kirk = KirkUtil.PyKirk.Kirk(kirkUrl, kirkToken)
        return self.kirk

    def getFME(self):
        '''
        retrieves the secrets needed to connect to fme and returns a
        fme api wrapper object
        :return: fme api wrapper
        :rtype: FMEUtil.PyFMEServerV3.FMEServer
        '''
        if self.fme is None:
            secrets = DBCSecrets.GetSecrets.CredentialRetriever()
            # get fme secrets and create fme wrapper
            fmeLabel = Constants.FMESECRETLABEL_TEMPLATE.format(
                self.env).upper()
            fmeSrvrSecrets = secrets.getSecretsByLabel(fmeLabel)
            fmeHost = fmeSrvrSecrets.getHost()
            fmeToken = fmeSrvrSecrets.getAPI()
            fmeBaseUrl = 'http://{0}/'.format(fmeHost)
            self.fme = PyFMEServer.FMEServer(fmeBaseUrl, fmeToken)

        return self.fme

    def getMiscParam(self, label):
        secrets = DBCSecrets.GetSecrets.CredentialRetriever()
        miscParams = secrets.getMiscParams()
        param = miscParams.getParam(label)
        return param

    def getFMESchedules(self):
        '''
        :return: a schedules data object (wraps the schedules data, and
                 provides builtin iterator)

        :rtype: FMEUtil.FMEServerApiData.Schedules
        '''
        if self.schedules is None:
            fme = self.getFME()
            scheds = fme.getSchedules()
            scheduleList = scheds.getSchedules()
            self.schedules = FMEUtil.FMEServerApiData.Schedules(scheduleList)
        return self.schedules

    def getFMWs(self, repoName):
        '''
        gets the summary information about each FMW in the provided
        respository name.

        :param repoName: name of the repository who's workspaces are
                         to be retrieved
        :type repoName: str
        '''
        fme = self.getFME()
        repo = fme.getRepository()
        wrkspcs = repo.getWorkspaces(repoName)
        wrkspcList = wrkspcs.getWorkspaces()
        wrkspcsDataObj = FMEUtil.FMEServerApiData.Workspaces(wrkspcList)
        return wrkspcsDataObj

    def getScheduledFMWDetailInfo(self):
        '''
        identifies the source fmw / repo for each schedule item then
        issues a query to retrieve detailed information about that
        repository, caches all this info in a list and then returns

        Can take a few minutes to run
        '''
        scheds = self.getFMESchedules()
        fme = self.getFME()
        repo = fme.getRepository()
        detailedFMWInfo = []
        pp = pprint.PrettyPrinter(indent=4)
        for sched in scheds:
            fmwName = sched.getFMWName()
            repoName = sched.getRepository()
            wrkspc = repo.getWorkspaces(repoName)
            wrkspcInfo = wrkspc.getWorkspaceInfo(fmwName)
            wrkspcData = FMEUtil.FMEServerApiData.WorkspaceInfo(wrkspcInfo)
            detailedFMWInfo.append(wrkspcData)
            self.logger.debug('*-*-' * 20)
            # print '*-*-'*20
            pp.pprint(wrkspcInfo)
        return detailedFMWInfo

