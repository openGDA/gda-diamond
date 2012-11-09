import sys;
import string;
import gda.factory.Finder as Finder;

def getHelpTopics():
	return [ reloadLookupTables ]
    
def update(controller, prefix, msg, exception=None, Raise=False):
	if exception != None:
		msg = msg + " " + str(exception)
	if controller != None:
		controller.update(None, msg)
	msg = prefix + msg
	print msg
	if Raise:
		raise msg
        
    
def reloadLookupTables():
	"""reloads all lookup tables on the ObjectServer"""
	controller = None
	prefix = "reloadLookupTables:"
	update(controller, prefix, " - started.")
	finder = Finder.getInstance()
	converters = finder.listAllObjects("IReloadableQuantitiesConverter")
	for converter in converters:
		update(controller, prefix, "..." + converter.getName() )      
		converter.reloadConverter()
	update(controller, prefix, " - completed")

