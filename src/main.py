'''
Created on Nov 22, 2018

@author: kjnether

This is the script that:
  - initiates all the checks
  - creates and sends out the email.
'''
import ScheduleEvaluation
import DataUtil
import logging.config
import Constants
import Reporting
import DBEvaluation
import warnings
import Emailer
import yaml
import os.path

msg = 'Unverified HTTPS request is being made. Adding certificate verif' + \
      'ication is strongly advised. See: https://urllib3.readthedocs.i' + \
      'o/en/latest/advanced-usage.html#ssl-warnings'
warnings.filterwarnings("ignore", message=msg)

if __name__ == '__main__':
    logConfigYaml = os.path.join(os.path.dirname(__file__), '..',
                                 'loggingConfig.yaml')
    with open(logConfigYaml, 'rt') as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

    # Settup logger initially
#     formatStr = '%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s'
#     datefmt = '%Y-%m-%d %H:%M:%S'
#     # logging.basicConfig(level=logging.DEBUG)
#     # formatStr = '[%(asctime)s] - %(name)s - {%(pathname)s:%(lineno)d} ' + \
#     #            '%(levelname)s - %(message)s', datefmt
#     logging.basicConfig(format=formatStr,
#                         datefmt=datefmt,
#                         level=logging.DEBUG)

    logger = logging.getLogger(__name__)
    logger.info("fiurst log message!")
    # define what environment to work with
    env = 'PRD'

    # used to help with formatting information into a string that
    # can be included in an email.
    emailReporter = Reporting.EmailStrings()
    dataCache = Reporting.CachedStrings()
    dataUtil = DataUtil.GetData(env)

    # add a header to the email
    jenkinsUrl = dataUtil.getMiscParam(Constants.JENKINSURL)
    ln1 = "    ----  DataBC Replication Health Check  ----\n"
    ln2 = 'src: https://github.com/bcgov/replication_health_check\n'
    ln3 = f'jenkins: {jenkinsUrl}\n\n\n'
    emailHeaderString = ln1 + ln2 + ln3
    dataCache.setString(emailHeaderString)
    logger.debug(f"emailHeaderString: {emailHeaderString}")

    # get the disabled schedules string
    scheds = dataUtil.getFMESchedules()
    schedsEval = ScheduleEvaluation.EvaluateSchedule(scheds)
    disabledSchedules = schedsEval.getDisabled()
    schedEvalStr = emailReporter.getDisableEmailStr(disabledSchedules)
    dataCache.setString(schedEvalStr)
    logger.info(f'schedEvalStr: {schedEvalStr}')

    # getting fmw's in scheduled repo that don't have schedules
    scheduledRepoName = dataUtil.getMiscParam(Constants.SCHEDULE_REPO_LABEL)
    wrkSpcData = dataUtil.getFMWs(scheduledRepoName)
    notScheduled = schedsEval.compareRepositorySchedule(wrkSpcData)
    unschedFMWsStr = emailReporter.getUnsheduledRepoFMWsStr(notScheduled,
                                                            scheduledRepoName)
    dataCache.setString(unschedFMWsStr)
    logger.info(f'unschedFMWsStr: {unschedFMWsStr}')

    # schedules that reference data on the E: drive
    embedData = schedsEval.getEmbeddedData()
    embedDataEmailStr = emailReporter.getEmbeddedDataEmailStr(embedData)
    dataCache.setString(embedDataEmailStr)
    logger.info(f'embedDataEmailStr: {embedDataEmailStr}')

    # now non prod or non OTHR replications
    nonProd = schedsEval.getNonProdSchedules()
    nonProdEmailStr = emailReporter.getNonProdSchedulesEmailStr(nonProd)
    dataCache.setString(nonProdEmailStr)
    logger.info(f'nonProd: {nonProd}')

    # get destinations with 0 records
    nonProd = schedsEval.getAllBCGWDestinations()
    db = DBEvaluation.DBScheduleQueries(nonProd)
    schedsZeroRecords = db.getZeroRecordDestinations()
    zeroRecords = emailReporter.getZeroRecordsSchedule(schedsZeroRecords)
    dataCache.setString(zeroRecords)
    logger.info(f'zeroRecords: {zeroRecords}')

    # now send the email
    emailer = Emailer.EmailCoorindator(dataCache)
    emailer.sendEmail()
