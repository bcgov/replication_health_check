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

    def getDisableEmailStr(self, disabledList):
        #disabled = self.getDisabled()
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
