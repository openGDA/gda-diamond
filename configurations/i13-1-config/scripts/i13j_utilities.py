from gda.data import NumTracker
import os
from gda.data import PathConstructor
from gda.factory import Finder


# set up a nice method for getting the latest file path
i13jNumTracker = NumTracker("i13j");
finder = Finder.getInstance()

# function to output the current scan number
def csn():
    return cfn()

# function to output the current file number
def cfn():
    filenumber = i13jNumTracker.getCurrentFileNumber();
    return filenumber

# function to output the next scan number
def nsn():
    return nfn()

# function to output the next file number
def nfn():
    filenumber = i13jNumTracker.getCurrentFileNumber();
    return filenumber + 1

# function to output the last file path
def pwd():
    dir = PathConstructor.createFromDefaultProperty()
    filenumber = i13jNumTracker.getCurrentFileNumber();
    return os.path.join(dir, str(filenumber))
    

# function to output the next file path
def nwd():
    dir = PathConstructor.createFromDefaultProperty()
    filenumber = i13jNumTracker.getCurrentFileNumber();
    return os.path.join(dir, str(filenumber + 1))

import smtplib
from email.mime.text import MIMEText
def send_email(whoto, subject, body):
    """
    To send an e-mail from the beamline's GDA server to one or more recipients
    
    whoto - the list of e-mail addresses of the intended recipients (list of strings, eg ['user_name@diamond.ac.uk'] or ["user_name_one@diamond.ac.uk", "user_name_two@gmail.com"])
    subject - the subject of the e-mail to be send (string)
    body - the content of the e-mail to be send (string)
    
    Example:
    send_email(["user_name_one@diamond.ac.uk", "user_name_two@gmail.com"], "Update on myscript's relentless progress...", "myscript completed without errors - hurrah!")
    
    The e-mail message sent by the above command will show up in the relevant mail boxes as follows:   
        From:       gda@i13-1-control.diamond.ac.uk
        Subject:    Update on myscript's relentless progress...
        Content:    myscript completed without errors - hurrah!
    """
    whofrom = "gda"
    if not type(whoto) is list:
        msg = "'whoto' must be a list, eg ['user_name@diamond.ac.uk'] or ['user_name_one@diamond.ac.uk', 'user_name_two@gmail.com']"
        raise Exception(msg)
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = whofrom
    msg['To'] = ", ".join(whoto)
     
    # send the message via our own SMTP server, but don't include the envelope header
    try:
        s = smtplib.SMTP('localhost')
        s.sendmail(whofrom, whoto, msg.as_string())
        s.quit()
        print "E-mail successfully sent!"
    except smtplib.SMTPException, ex:
    #except Exception, ex:
        print "Failed to send e-mail: %s!" %(str(ex))


