'''
Created on Oct 11, 2017

@author: kjnether

This is an attempt to create an emailer, that can be easily encorporated into
The fme framework.

It gets called by the shutdown.
- looks for a published parameter named EMAILER which is a multiline text
  entry (described here)
- The formulates an email with the jobs log attached.

'''

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import smtplib
import DBCSecrets.GetSecrets
import Constants

# import DataBCFMWTemplate
# import DBCFMEConstants


class EmailCoorindator(object):
    '''
    This method coordinates the composition of the actual email body, 
    and it also retrieves the email server / port / addresses 
    from the secrets.

    '''

    def __init__(self):
        secrets = DBCSecrets.GetSecrets()
        
        smtpServerSecretKey = Constants.SMTPSERVER
        smtpPortSecretKey = Constants.SMTPPORT
        
        self.logger = logging.getLogger(__name__)
        self.logger.debug("constructing emailer object")

        self.validNotificationTypes = ['ALL', 'SUCCESS', 'FAIL']

        self.email = None

        # print the macroValues
        # self.printMacros()
        self.notifyAll = []
        self.notifyFail = []
        self.notifySuccess = []

        self.getNotificationEmailsFromFMEMacros()

    def sendNotifications(self):
        '''
        checks to see if notifications are defined in the published
        parameters if notification exist then extracts and parses the
        values from those published parameters and puts them into a list of
        email addresses.

        Grabs the information out of the fmw and the fme object that need
        to be included in the email message, (subject, attachment, status,
        source parameter, destination parameters etc)

        Finally it puts all that information together into an email message
        and sends it to the addresses identifies in the various
        notification parameters.
        '''
        if self.areNotificationsDefined():
            self.logger.debug("There are parameters in the FMW for " +
                              "notifications")

            fromAddress = self.config.getEmailFromAddress()
            # toAddress are a list
            toAddress = self.getEmailAddresses()
            if toAddress:
                subject = self.getEmailSubject()
                body = self.getLogFileBody()
                fmwLogFileName = self.getFMWFileAsLogFile()
                self.logger.debug("toAddress: %s", toAddress)
                #    emailTo, emailFrom, emailSubject, emailBody=None):
                emailMessage = Email(emailTo=toAddress,
                                     emailFrom=[fromAddress],
                                     emailSubject=subject, emailBody=body,
                                     fmwFileName=fmwLogFileName)

                logFile = self.fmeObj.logFileName
                emailMessage.addAttachement(logFile)

                emailServer = EmailServer(self.config)

                sender = SendEmail(emailServer, emailMessage)
                sender.setup()
                sender.send()
            else:
                self.logger.debug("notification parameters are defined but they " + \
                                  "are all blank, ie no addresses defined in any " + \
                                  "of the parameters")
        else:
            self.logger.debug("notification are not configured")


class EmailServer(object):
    '''
    Contains the parameters that are required to actually send
    an email, things like SMTP server, ports etc.

    :ivar param: This is a DataBCFMWTemplate.TemplateConfigFileReader object.
                 this class will extrac the information it needs from the
                 object
    :ivar smtpServer: the smtp server name
    :ivar smtpPort: the smtp port
    '''

    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("created an EmailServer")
        self.config = config
        self.smtpServer = None
        self.smtpPort = None
        self.parseParams()

    def parseParams(self):
        '''
        retrieves the email smtp server and port from the fme framework config
        file.
        '''
        self.smtpServer = self.config.getEmailSMTPServer()
        self.logger.debug("smtpServer: %s", self.smtpServer)
        self.smtpPort = self.config.getEmailSMTPPort()
        self.logger.debug("smtpPort: %s", self.smtpPort)

    def getSMTPPort(self):
        '''
        Returns the SMTP port
        '''
        return self.smtpPort

    def getSMTPServer(self):
        '''
        Returns the SMTP server name
        '''
        return self.smtpServer


class Email(object):
    '''
    This is a class that contains the structure of an email
    message including:
      - To
      - From
      - Subject
      - Body

    :ivar emailTo: a list of email addresses that the message should be sent to.
    :ivar emailFrom: a list of email addresses that the message should appear to
                     be sent from
    :ivar emailSubject: email subject line
    :ivar fmwFileName: the path to the fmw file that was run.
    :ivar emailBody: the body of the message of the email
    :ivar attachementFilePath: if the email is to include an attachement the path
                               to the file that is to be attached is defined here.
    '''

    def __init__(self, emailTo, emailFrom, emailSubject, fmwFileName, emailBody=None):
        self.logger = logging.getLogger(__name__)
        self.emailTo = emailTo
        self.emailFrom = emailFrom
        self.emailSubject = emailSubject
        self.emailBody = emailBody
        self.fmwFileName = fmwFileName
        self.attachementFilePath = None
        if not isinstance(self.emailTo, list):
            msg = 'The emailTo parameter should be a list.  It is currently a' + \
                  ' {0}.  Values: {1}'
            msg = msg.format(type(self.emailTo), self.emailTo)
            raise ValueError, msg
        if not isinstance(self.emailFrom, list):
            msg = 'The emailFrom parameter should be a list.  It is currently a' + \
                  ' {0}.  Values: {1}'
            msg = msg.format(type(self.emailFrom), self.emailFrom)
            raise ValueError, msg

    def getFMWNameLogFile(self):
        '''
        :return: a log file with the same name as the fmw file that is being run
                 but with a .log suffix.
        '''
        return self.fmwFileName

    def addAttachement(self, attachmentFilePath):
        '''
        Defines the location of the file that is to be attached to the email.
        '''
        self.attachementFilePath = attachmentFilePath

    def getAttachementFilePath(self):
        '''
        :return: a string to valid path where the file that is to be attached
                 is located
        '''
        return self.attachementFilePath


class SendEmail(object):
    '''
    This class contains the methods that can be used to send the actual email,

    :ivar logger: needs no explaination
    :ivar emailServer: a EmailServer object
    :ivar emailObj: a Email object
    :ivar msg: the MIMEMultipart message object that is going to be populated
               by this script
    :ivar setupComplete: a flag used to identify if the email message setup has
                         been completed or not
    '''

    def __init__(self, emailSrvr, emailObj):
        self.logger = logging.getLogger(__name__)
        self.emailServer = emailSrvr
        self.emailObj = emailObj
        self.msg = MIMEMultipart()
        self.setupComplete = False

        # verify the types of some args
        if not isinstance(emailSrvr, EmailServer):
            msg = 'The property emailSrvr in the class constructor received an ' + \
                  'object of type {0}.  This property must of type: EmailServer'
            raise ValueError, msg.format(type(emailSrvr))
        if not isinstance(emailObj, Email):
            msg = 'The property emailObj in the class constructor received an ' + \
                  'object of type {0}.  This property must of type: Email'
            raise ValueError, msg.format(type(emailObj))

    def setup(self):
        '''
        Constructs the email message, by adding the to / from / subject / body
        and attachements to it.
        '''
        self.msg["Subject"] = self.emailObj.emailSubject
        self.msg["From"] = ','.join(self.emailObj.emailFrom)
        # msg["To"] = "datamaps@gov.bc.ca,DataBCDA@gov.bc.ca,dataetl@gov.bc.ca,
        #              datadba@gov.bc.ca"
        self.msg["To"] = ','.join(self.emailObj.emailTo)
        self.logger.debug("Email to addresses include: %s",
                          ','.join(self.emailObj.emailTo))

        # Create the body of the message (a plain-text and an HTML version).
        body = MIMEText(self.emailObj.emailBody, 'html')

        # Record the MIME types of both parts - text/plain and text/html.
        # body = MIMEText(html, 'html')
        # self.msg.attach(MIMEText(body))
        self.msg.attach(body)
        self.setupComplete = True

    def send(self):
        '''
        takes the contents of the Email object defined in the constructor and
        extracts the necessary properties from it to assemble an email, then
        initiates communciation with the smtp server defined in the property
        emailServer, and finally sends the email.
        '''
        if not self.setupComplete:
            self.setup()
        emailServerName = self.emailServer.getSMTPServer()
        emailServerPort = self.emailServer.getSMTPPort()
        self.logger.debug("server: %s port: %s", emailServerName, emailServerPort)

        # add attachment here
        attacheFilePath = self.emailObj.getAttachementFilePath()
        if attacheFilePath:
            fmwLogName = self.emailObj.getFMWNameLogFile()
            self.addAttachement(attacheFilePath, fmwLogName)
        self.logger.debug("attempting to send message now")
        smtp = smtplib.SMTP(emailServerName, emailServerPort)
        self.logger.debug("smtp server object created, sending email now")
        smtp.sendmail(self.msg["From"], self.emailObj.emailTo, self.msg.as_string())
        self.logger.debug("notification should now be sent.")
        smtp.quit()

    def addAttachement(self, attachementFile, fmwNameLog):
        '''
        :param attachementFile: a string that describes a valid path to the file
                                that is going to be attached to the email.
        :param fmwNameLog: When the file is attached to the email this is the
                           name that will be assigned to that file as an
                           email attachement.
        This method takes the path defined in attachementFile and does the
        actual attachment of that file to the email that is to be sent.
        '''
        self.logger.debug("attachementFile: %s", attachementFile)
        with open(attachementFile, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=fmwNameLog
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % fmwNameLog
        self.msg.attach(part)
