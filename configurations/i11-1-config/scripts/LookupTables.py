import sys;
import string;
from gda.factory import Finder;
from gda.util.converters import IReloadableQuantitiesConverter

def getHelpTopics():
    return [ reloadLookupTables ]

def update(controller, prefix, msg, exception=None, Raise=False):
    if exception != None:
        msg = msg + " " + str(exception)
    if controller != None:
        controller.update(None, msg);
    msg = prefix + msg;
    print msg
    if Raise:
        raise msg


def reloadLookupTables():
    """reloads all lookup tables on the ObjectServer"""
    controller = None
    prefix = "reloadLookupTables:"
    update(controller, prefix, " - started.")
    converters = Finder.listFindablesOfType(IReloadableQuantitiesConverter)
    for converter in converters:
        update(controller, prefix, "..." + converter.getName() )
        converter.reloadConverter()
    update(controller, prefix, " - completed")

def readLookupTable(filename):
    '''
    read in the lookup table from a tab-delimited data file.
    :param filename:
    '''
    f = open(filename, "r")
    lines = f.readlines()
    f.close()
    lines = map(string.split, map(string.strip, lines))
    lookuptable={}
    for x in lines[2:]:
        lookuptable[x[0]]=[float(item) for item in x[1:]]
    return lookuptable