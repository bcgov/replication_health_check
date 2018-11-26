'''
Created on Nov 26, 2018

@author: kjnether

Ties together the secrets, and database connections, providing simple
easy to use methods to query specific situations out of the database
'''

import DB.DbLib
import logging
import DBCSecrets.GetSecrets
import Constants


class DBScheduleQueries(object):
    '''
    gets a list of schedules that need to be evaluated for some criteria
    '''

    def __init__(self, scheduleList):
        self.logger = logging.getLogger(__name__)
        self.scheduleList = scheduleList
        secrets = DBCSecrets.GetSecrets.CredentialRetriever()
        self.multiSecrets = secrets.getMultiAccounts()

    def getZeroRecordDestinations(self):
        '''
        Evaluates the schedules and returns any schedules who's
        current destination has 0 records
        '''
        zeroDestSchedules = []
        for schedule in self.scheduleList:
            # get the dest_db_env_key
            pubParams = schedule.getPublishedParameters()
            destDbEnvKey = pubParams.getDestDbEnvKey()
            destSchema = pubParams.getDestinationSchema()
            destTable = pubParams.getDestinationFeature()

            secretKey = Constants.SECRET_LABEL_TEMPLATE.format(destDbEnvKey)
            passwrd = self.multiSecrets.getAccountPassword(secretKey,
                                                           destSchema)
            host = self.multiSecrets.getHost(secretKey)
            serviceName = self.multiSecrets.getServiceName(secretKey)
            dbConn = DB.DbLib.DbMethods()
            dbConn.connectNoDSN(destSchema, passwrd, serviceName, host)
            
            query = 'SELECT COUNT(*) FROM {0}.{1}'.format(destSchema, destTable)
            cur = dbConn.executeOracleSql(query)
            row = cur.fetchone()
            self.logger.debug("row: %s", row)
            recordCnt = row[0]
            if recordCnt == 0:
                zeroDestSchedules.append(recordCnt)
        return zeroDestSchedules


