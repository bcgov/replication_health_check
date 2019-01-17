'''
Created on Nov 26, 2018

@author: kjnether

Ties together the secrets, and database connections, providing simple
easy to use methods to query specific situations out of the database
'''
import cx_Oracle
import DB.DbLib
import logging
import DBCSecrets.GetSecrets
import Constants
import re


class DBScheduleQueries(object):
    '''
    gets a list of schedules that need to be evaluated for some criteria
    '''

    def __init__(self, scheduleList):
        self.logger = logging.getLogger(__name__)
        self.scheduleList = scheduleList
        secrets = DBCSecrets.GetSecrets.CredentialRetriever()
        self.multiSecrets = secrets.getMultiAccounts()

        self.cachedDbParams = {}

    def getDatabaseConnection(self, destDbEnvKey, destSchema):
        if (self.cachedDbParams) and \
                destDbEnvKey == self.cachedDbParams['ENV'] and \
                destSchema == self.cachedDbParams['SCHEMA']:
            dbConn = self.cachedDbParams['DBCONN']
        else:
            secretKey = Constants.SECRET_LABEL_TEMPLATE.format(
                destDbEnvKey)
            passwrd = self.multiSecrets.getAccountPassword(secretKey,
                                                           destSchema)
            host = self.multiSecrets.getHost(secretKey)
            serviceName = self.multiSecrets.getServiceName(secretKey)

            dbConn = DB.DbLib.DbMethods()
            dbConn.connectNoDSN(destSchema, passwrd, serviceName, host)

            self.cachedDbParams = {'ENV': destDbEnvKey,
                                   'SCHEMA':  destSchema,
                                   'DBCONN': dbConn}
        return dbConn

    def getZeroRecordDestinations(self):
        '''
        Evaluates the schedules and returns any schedules who's
        current destination has 0 records
        '''
        zeroDestSchedules = []
        # start by organizing by schema allowing us to re-use
        # connection objects for each schema.
        schedulesBySchema = {}
        for schedule in self.scheduleList:
            scheduleName = schedule.getScheduleName()
            pubParams = schedule.getPublishedParameters()
            destDbEnvKey = pubParams.getDestDbEnvKey()
            destSchema = pubParams.getDestinationSchema()
            if destSchema is None:
                msg = 'schedule: {0}, has a None destination schema'
                msg = msg.format(scheduleName)
                self.logger.error(msg)
            else:
                destSchema = destSchema.upper()
                if destSchema not in schedulesBySchema:
                    schedulesBySchema[destSchema] = []
                schedulesBySchema[destSchema].append(schedule)

        for scheduleKey in schedulesBySchema:
            for schedule in schedulesBySchema[scheduleKey]:

            # for schedule in self.scheduleList:
                # get the dest_db_env_key
                # scheduleName = schedule.getScheduleName()
                # fmw = schedule.getFMWName()
                scheduleName = schedule.getScheduleName()
                pubParams = schedule.getPublishedParameters()
                destDbEnvKey = pubParams.getDestDbEnvKey()
                destSchema = pubParams.getDestinationSchema()
                destTable = pubParams.getDestinationFeature()
                if destSchema is None:
                    msg = 'schedule: {0}, has a None destination schema'
                    msg = msg.format(scheduleName)
                    self.logger.error(msg)
                else:
                    recordCnt = 0
                    self.logger.debug("destSchema: %s", destSchema)
                    self.logger.debug("destTable: %s", destTable)
                    dbConn = self.getDatabaseConnection(destDbEnvKey, destSchema)

                    isTableSchemaQualified = re.compile("^\w+\.\w+$")
                    if destTable is None:
                        msg = 'schedule: {0}, the destination table is not defined'
                        msg = msg.format(scheduleName)
                        self.logger.error(msg)
                        recordCnt = 0
                    else:
                        if isTableSchemaQualified.match(destTable):
                            schemaTable = destTable
                        else:
                            schemaTable = '{0}.{1}'.format(destSchema, destTable)
                        try:
                            query = 'SELECT COUNT(*) FROM {0}'.format(schemaTable)
                            self.logger.debug("query: %s", query)
                            cur = dbConn.executeOracleSql(query)
                            row = cur.fetchone()
                            self.logger.debug("row: %s", row)
                            recordCnt = row[0]
                        except cx_Oracle.DatabaseError:
                            msg = 'schedule: {0}, Problem with the query that is being ' + \
                                  'run: {1}'
                            msg = msg.format(scheduleName, query)
                            self.logger.error(msg)
                            recordCnt = 0
                if recordCnt == 0:
                    # zeroDataRecord = [scheduleName, fmw, destSchema, destTable]
                    zeroDestSchedules.append(schedule)
        return zeroDestSchedules
