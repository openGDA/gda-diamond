'''
Created on Apr 12, 2023

@author: fy65
'''
from org.slf4j import LoggerFactory
localStation_slf4j_logger = LoggerFactory.getLogger("localStation.py(slf4j)")

localStation_exceptions = []
localStation_warnings = []

def localStation_exception(msg, exception=True):
    """Use exception=None if you don't want a stack trace."""
    import java, sys, traceback
    localStation_exceptions.append("    %s" % msg)
    print("!"*(len(msg)+20))
    print("!!!!  Failure %s  !!!!" % msg)
    print("!"*(len(msg)+20))
    if isinstance(exception, java.lang.Exception) or exception == None:
        localStation_slf4j_logger.error(msg, exception)
    else:
        localStation_slf4j_logger.error(msg + ':\n {}', ''.join(traceback.format_exception(*sys.exc_info())))
    # Check out https://confluence.diamond.ac.uk/x/FZbCB

def localStation_warning(msg):
    localStation_warnings.append("    %s" % msg)

def localStation_print(msg):
    print(msg)
    localStation_slf4j_logger.info(msg)
