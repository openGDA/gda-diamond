from org.slf4j import LoggerFactory
import traceback

def run_in_try_catch(function):
    logger = LoggerFactory.getLogger("run_in_try_catch")

    try :
        print "Running ",function.__name__," function"
        function()
    except (Exception, java.lang.Throwable) as ex:
        stacktrace=traceback.format_exc()
        print("Problem running ",function.__name__," - see log for more details")
        print "Stack trace : ", stacktrace
        logger.warn("Problem running jython function {} {}", function.__name__, stacktrace)
