'''
Created on 4 Apr 2018

@author: fy65
'''
from gdascripts.messages.handle_messages import simpleLog
from gdascripts.messages import handle_messages
localStation_exceptions = []

def localStation_exception(exc_info, msg):
    typ, exception, traceback = exc_info
    simpleLog("! Failure %s !" % msg)
    localStation_exceptions.append("    %s" % msg)
    handle_messages.log(None, "Error %s -  " % msg , typ, exception, traceback, False)