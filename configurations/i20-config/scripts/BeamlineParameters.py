import sys;
import gda.configuration.properties.LocalProperties as LocalProperties
from gda.jython import JythonServerFacade
from gda.factory import Finder

def readDictionaryFromFile( mappingFile, mydict):
    dictMapFile = open( mappingFile,'r')
    lines = dictMapFile.readlines()
    dictMapFile.close()
    for line in lines:
        # only deal with text up to the # comment character
        items = line.split('#')
        line = items[0]
        items = line.split()
        if items == None or len( items) != 2:
            items = line.split('=')
        if items != None and len( items) == 2:
            mydict[(items[0]).strip()] = items[1].strip()
    return mydict

class JythonNameSpaceMapping:
    def __init__(self):
        self.jythonNamespaceMap={}
        self.load()
    def __getattr__(self, attrName):
        if attrName == "__eq__":
            raise AttributeError
        if attrName == "__cmp__":
            raise AttributeError
        if attrName == "__coerce__":
            raise AttributeError
        if( self.jythonNamespaceMap.has_key(attrName)) :
            nameInNameSpace = self.jythonNamespaceMap[attrName]
        else:
            nameInNameSpace = attrName
        try:
            return JythonServerFacade.getInstance().getFromJythonNamespace(nameInNameSpace)
        except:
            msg =  "Error getting value for item named " + nameInNameSpace + " in jythonNamespace for attribute " +attrName
            # print out now as it is not output by the Jython terminal
            print msg
            raise AttributeError, msg
    def load(self):
        self.jythonNamespaceMapFilePath = LocalProperties.get('gda.jython.namespaceMappingFile' )
        if(self.jythonNamespaceMapFilePath == None):
            raise AttributeError, "property gda.jython.namespaceMappingFile is not set"
        self.jythonNamespaceMap = readDictionaryFromFile(self.jythonNamespaceMapFilePath, self.jythonNamespaceMap)

class FinderNameMapping:
    def __init__(self ):
        self.finderNameMap={}
        self.load()
    def __getattr__(self, attrName):
        if attrName == "__eq__":
            raise AttributeError
        if attrName == "__cmp__":
            raise AttributeError
        if attrName == "__coerce__":
            raise AttributeError
        if( self.finderNameMap.has_key(attrName)) :
            nameToFind = self.finderNameMap[attrName]
        else:
            nameToFind = attrName
        try:
            obj = Finder.getInstance().find(nameToFind)
        except:
            # print out now as it is not output by the Jython terminal
            msg = "Error getting value for item named " + nameToFind + " in finderNameMap for attribute " + attrName
            print msg
            raise AttributeError, msg
        if( obj == None):
            msg = "Error getting value for item named " + nameToFind + " in finderNameMap for attribute " + attrName
            print msg
            raise AttributeError, msg
        return obj
    def load(self):
        self.finderNameMapFilePath = LocalProperties.get( 'gda.jython.finderNameMappingFile' )
        if(self.finderNameMapFilePath == None):
            raise AttributeError, "property gda.jython.finderNameMappingFile is not set"
        self.finderNameMap = readDictionaryFromFile(self.finderNameMapFilePath, self.finderNameMap)

class DictionaryWrapper:
    def __init__(self, map):
        self.map = map
    def __getattr__(self, attrName):
        if( self.map.has_key(attrName)) :
            return self.map[attrName]
        else:
            raise AttributeError, attrName
        
class Parameters:
    def __init__(self ):
        self.parametersMap={}
        self.load()
    def __getattr__(self, attrName):
        if( self.parametersMap.has_key(attrName)) :
            return self.parametersMap[attrName]
        else:
            raise AttributeError, attrName
    def getValueOrNone(self, attrName):
        if( self.parametersMap.has_key(attrName)) :
            return self.parametersMap[attrName]
        else:
          return None
    def load(self):
        self.parametersFilePath = LocalProperties.get( 'gda.jython.beamlineParametersFile' )
        if(self.parametersFilePath == None):
            raise AttributeError, "property gda.jython.beamlineParameters is not set"
        self.parametersMap = readDictionaryFromFile(self.parametersFilePath, self.parametersMap)
    def getValueFromObjectOrNone(self, attrName, object):
        if( self.parametersMap.has_key(attrName)) :
            return object.__getattr__(self.parametersMap[attrName])
        else:
          return None
    