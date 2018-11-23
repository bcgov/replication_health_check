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


class GetData(object):

    def __init__(self, env):
        self.logger = logging.getLogger(__name__)
        self.env = env

        self.fme = None
        self.kirk = None

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
        fme = self.getFME()
        scheds = fme.getSchedules()
        scheduleList = scheds.getSchedules()
        schedDataObj = FMEUtil.FMEServerApiData.Schedules(scheduleList)
        return schedDataObj
    
    def getFMWs(self, repoName):
        '''
        
        
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

        
