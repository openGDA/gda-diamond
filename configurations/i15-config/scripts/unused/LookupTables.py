import sys;
import string;
import gda.factory.Finder as Finder;
from gdascripts.messages import handle_messages
from gdascripts.messages.handle_messages import simpleLog

def getHelpTopics():
    return [ reloadLookupTables ]
    
def reloadLookupTablesEx(logInfo):
    """version of reloadLookupTables that can be used in tests to only generate output when an error is detected"""
    ok = True
    controller = None
    prefix = "reloadLookupTables:"
    if( logInfo ):
       handle_messages.log(controller, prefix + " - started") 
    finder = Finder.getInstance()
    converters = finder.listAllObjects("IReloadableQuantitiesConverter")
    for converter in converters:
        try:
            if( logInfo ):
                handle_messages.log(controller, prefix + "..." + converter.getName() )      
            converter.reloadConverter()
        except:
            type, exception, traceback = sys.exc_info()
            handle_messages.log(controller, prefix + " - ", type, exception, traceback, False)
            ok = False
    if( logInfo ):
        handle_messages.log(controller, prefix + " - completed")
    if( not ok):
        print "reloadLookupTables completed with error"
    return ok

def reloadLookupTables():
    """reloads all lookup tables on the ObjectServer"""
    reloadLookupTablesEx(True)
