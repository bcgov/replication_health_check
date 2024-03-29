'''
Created on Nov 23, 2018

@author: kjnether
'''

import logging
from collections.abc import Iterable

class EmailStrings(object):
    '''
    takes data objects and returns strings that will get inserted into the
    email report.
    '''

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("test")

    def getFormatString(self, dataList):
        '''
        iterates through all the elements in the list determining the
        longest element in the string and creating a format string that
        can accomodate that value.

        :param dataList: input data list, a list of lists, where the inner
                         list represents the rows of data
        :type dataList: list of lists.
        '''
        lengths = None
        # get lengths of each param
        for rowData in dataList:
            if lengths is None:
                lengths = []
                for param in rowData:
                    if param is None:
                        lengths.append(4)
                    else:
                        lengths.append(len(param))
            else:
                for cnt in range(0, len(rowData)):
                    if rowData[cnt] is None:
                        curLen = 4
                    else:
                        curLen = len(rowData[cnt])
                    formatLen = lengths[cnt]
                    if curLen > formatLen:
                        lengths[cnt] = curLen
        formatStr = ' - '
        elem = u' {{{0}:<{1}}} '
        # startElem = ' - {{{0}:>{1}}}'
        cnt = 0

        # just a quick patch to get jenkins job working...
        if isinstance(lengths, Iterable):
            for curLen in lengths:
                formatStr = formatStr + elem.format(cnt, curLen)
                cnt += 1
            self.logger.info(u"format string is: {0}".format(formatStr))
        return formatStr

    def getDisableEmailStr(self, disabledList):
        # disabled = self.getDisabled()
        msgList = []
        msg = 'LIST OF CURRENTLY DISABLED SCHEDULES (SCHEDULE/REPO/FMW)'
        delim = '-' * len(msg)
        msgList.append(msg)
        msgList.append(delim)
        # dataTmplt = ' - {0:>55}, {1:>15}, {2:>55}'
        # iterate through the data so we can get the longest
        # entry for proper formatting
        dataList = []
        dataLen = []
        dataTmplt = self.getFormatString(disabledList)
        self.logger.debug("format string: %s", dataTmplt)
        # converting the data into a nicely formatted string.
        for dataLine in disabledList:
            newLine = dataTmplt.format(*dataLine)
            msgList.append(newLine)
        # append each line in the msg list into a carriage return delimited
        # string
        msgStr = '\n'.join(msgList)
        #msgStr = '<p>{0}</p>'.format(msgStr)
        return msgStr

    def getUnsheduledRepoFMWsStr(self, unscheduledList, repositoryName):
        '''
        converts this data into a single string that can be inserted into
        an email.

        :param unscheduledList: list of the fmw's in the said repository
                                that are not scheduled
        :type unscheduledList: list
        :param repositoryName: name of the repository that the fmw's
                               originated from
        :type repositoryName: str
        '''
        msgList = []
        header = 'FMW\'s in {0} that are not scheduled'
        msgList.append(header.format(repositoryName))
        spacer = '-' * len(header)
        msgList.append(spacer)
        dataTmplt = ' - {0}'
        for fmw in unscheduledList:
            msgList.append(dataTmplt.format(fmw))
        msgStr = '\n'.join(msgList)
        return msgStr

    def getEmbeddedDataEmailStr(self, embedData):
        '''
        expectes Embed data to be a list of lists
        inner list: schedule name, parameter name, parameter value
        '''
        msgList = []
        header = 'Schedules that reference embedded data'
        msgList.append(header)
        spacer = '-' * len(header)
        msgList.append(spacer)
        formatStr = self.getFormatString(embedData)
        self.logger.info("format string is: {0}".format(formatStr))
        for schedData in embedData:
            msgList.append(formatStr.format(*schedData))
        msgStr = '\n'.join(msgList)
        return msgStr

    def getNonProdSchedulesEmailStr(self, embedData):
        '''
        Gets a list of schedules that have the keyword DEST_DB_ENV_KEY
        set to something other than OTHER or PRD.

        :param embedData: a list of lists, where inner list contains
        :type embedData:
        '''
        msgList = []
        header = 'Schedules replicationing to NON PROD Destinations'
        msgList.append(header)
        spacer = '-' * len(header)
        msgList.append(spacer)
        formatStr = self.getFormatString(embedData)
        self.logger.info("format string is: {0}".format(formatStr))
        for lineData in embedData:
            for cnt in range(0, len(lineData)):
                if lineData[cnt] is None:
                    lineData[cnt] = 'None'
                if lineData[cnt] == []:
                    lineData[cnt] = ''
            self.logger.debug("lineData: {0}".format(lineData))
            msgList.append(formatStr.format(*lineData))
        msgStr = '\n'.join(msgList)
        return msgStr

    def getZeroRecordsSchedule(self, schedules):
        '''
        gets a list Schedule object, need to iterate over each schedule
        extract the pieces that are required for

        schedule properties to report on:
          Schedule namne
          fmw name
          dest schema
          dest table
        '''
        msgList = []
        header = 'Scheduled replications with empty destination tables'
        msgList.append(header)
        spacer = '-' * len(header)
        msgList.append(spacer)
        elems2Include = []
        for schedule in schedules:
            fmw = schedule.getFMWName()
            repo = schedule.getRepository()
            schedName = schedule.getScheduleName()
            pp = schedule.getPublishedParameters()
            destSchema = pp.getDestinationSchema()
            destTable = pp.getDestinationFeature()
            elems2Include.append([schedName, repo, fmw,
                                  destSchema, destTable])
        formatStr = self.getFormatString(elems2Include)
        for lineData in elems2Include:
            for cnt in range(0, len(lineData)):
                if lineData[cnt] is None:
                    lineData[cnt] = 'None'
            msgList.append(formatStr.format(*lineData))
        msgStr = '\n'.join(msgList)
        return msgStr


class CachedStrings(object):
    '''
    having generated formatted strings that can be used in the
    email, this class provides a place to store them and
    retrieve them.
    '''

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reportList = []

    def setString(self, inString):
        self.reportList.append(inString)

    def getStrings(self):
        return self.reportList
