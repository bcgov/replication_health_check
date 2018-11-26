'''
Created on Nov 23, 2018

@author: kjnether
'''

import logging


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
                    lengths.append(len(param))
            else:
                for cnt in range(0, len(rowData)):
                    curLen = len(rowData[cnt])
                    formatLen = lengths[cnt]
                    if curLen > formatLen:
                        lengths[cnt] = curLen
        formatStr = ' - '
        elem = u' {{{0}:>{1}}} '
        # startElem = ' - {{{0}:>{1}}}'
        cnt = 0
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
        # getting the longest value for each column
        for sched in disabledList:
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
        header = 'Scedules that reference embedded data'
        msgList.append(header)
        spacer = '-' * len(header)
        lengths = None
        # get lengths of each param
        for schedData in embedData:
            if lengths is None:
                lengths = []
                for param in schedData:
                    lengths.append(len(param))
            else:
                for cnt in range(0, len(schedData)):
                    curLen = len(schedData[cnt])
                    formatLen = lengths[cnt]
                    if curLen > formatLen:
                        lengths[cnt] = curLen
        formatStr = ' - '
        elem = u' {{{0}:>{1}}} '
        # startElem = ' - {{{0}:>{1}}}'
        cnt = 0
        for curLen in lengths:
            formatStr = formatStr + elem.format(cnt, curLen)
            cnt += 1
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
