import sys;
import os.path
import java
from java.lang import Math, String
from time import sleep
from time import localtime
import gda
import gda.factory.Finder as Finder;
from gda.device.epicsdevice import ReturnType
from gda.util import VisitPath
from gda.analysis import ScanFileHolder
from gda.jython import JythonServerFacade
from gdascripts.messages import handle_messages
from gdascripts.parameters import beamline_parameters
from gdascripts import lookup_tables

    
import unittest


def get_names(namefile):
    scannable_names=[]
    f = open( namefile )
    lines = f.readlines()
    f.close()

    for l in lines:
        if not l.startswith("#") and not len(l) == 0:
            scannable_names.append(l.strip())
    return scannable_names

def get_objects_from_jythonnamespace(jmap, namefile):
    objects=[]
    for name in get_names(namefile):
        objects.append(jmap.__getattr__(name))
    return objects

def get_test_suite(classType, namefile):
    jmap = beamline_parameters.JythonNameSpaceMapping()
    ts = unittest.TestSuite()
    for s in get_objects_from_jythonnamespace(jmap, namefile):
        ts.addTest(classType(s))
    return ts

def get_test_scannable_suite(namefile):
    return get_test_suite(TestScannable, namefile )


class TestScannable(unittest.TestCase):
    def __init__(self, scannable):
        unittest.TestCase.__init__(self)
        self.scannable = scannable

    def runTest(self):
        if not (self.scannable is None):
            print "%s = %s" % (self.scannable.getName(), `self.scannable.getPosition()`)
        
