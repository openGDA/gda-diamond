from gda.jython.commands.GeneralCommands import run
from gda.util import Email

import java.lang.Exception as jException
import logging
logger = logging.getLogger('gda.lde.script_runner')

CURRENT_DIRECTORY = '*CURRENT SCRIPTS/'

# Maybe should be a property but define here for now
EMAIL_LIST = ['claire.murray@diamond.ac.uk',
        'stephen.thompson@diamond.ac.uk',
        'sarah.day@diamond.ac.uk']
CC_LIST = ['peter.holloway@diamond.ac.uk']

def run_current(name):
    """
    Run a script in the CURRENT SCRIPTS directory

    If any errors occur, check if user wants to skip, rerun or abort
    """
    try:
        print '\nRunning script: ' + name
        logger.debug('Running script: %s', name)
        run(CURRENT_DIRECTORY + name)
    except (jException, Exception) as e:
        print 'Error running script ' + name
        Email().to(EMAIL_LIST).cc(CC_LIST)
                .subject('Error running LDE scripts')
                .message('Error running script ' + name + '\n\nError raised:\n' + str(e))
                .send()
        logger.error('Error running script "%s"', name, exc_info=True)
        if checkRerun(name):
            logger.debug('Rerunning script: %s', name)
            run_current(name)
        else:
            print 'skipping ' + name
            logger.debug('Skipping script: %s', name)


def checkRerun(name):
    """
    Check if the user wants to rerun the current script.

    Gives user options of skip, rerun or abort
    Returns:
        True - if user wishes to rerun
        False - if user wishes to skip
    Raises:
        Exception - if user wished to abort
    """
    rerun = None
    while rerun not in {'s', 'r', 'a'}:
        rerun = raw_input('Error running script. Skip(s)/Rerun(r)/Abort(a)?: ')
    if rerun == 'a':
        raise Exception('script aborted')
    else:
        return rerun == 'r'

def checkContinue():
    """
    Asks user whether to continue

    If not, raises Exception
    """
    cont = raw_input('Continue running master script? y/N?: ')
    if cont.upper() != 'Y':
        raise Exception('Script aborted')
