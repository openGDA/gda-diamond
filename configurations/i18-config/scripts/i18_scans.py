from java.lang import *
from gda.configuration.properties import LocalProperties

def resetMicroFocusPanel():
    '''Resets the Start/Stop buttons on the MicroFocus Panel.'''
    controller = finder.find("MicroFocusController")
    controller.update(None, "STOP")

def getMicroFocusStepScanClass():
    printProperty("gda.microfocus.i18.step.scan.class")

def setMicroFocusStepScanClass(newClass):
    LocalProperties.set("gda.microfocus.i18.step.scan.class",newClass)
    getMicroFocusStepScanClass()

def getExafsScanClass():
    printProperty("gda.exafs.i18.scan.class")

def setExafsScanClass(newClass):
    LocalProperties.set("gda.exafs.i18.scan.class",newClass)
    getExafsScanClass()

def getExafsWindowsDirectory():
    printProperty("gda.exafs.i18.windows.directory")
    
def setExafsWindowsDirectory(newDir):
    LocalProperties.set("gda.exafs.i18.windows.directory",newDir)
    getExafsWindowsDirectory()

def getExafsWindowsFilename():
    printProperty("gda.exafs.i18.windows.filename")
 
def setExafsWindowsFilename(newFilename):
    LocalProperties.set("gda.exafs.i18.windows.filename",newFilename)
    getExafsWindowsFilename()
   
def getExafsWindowsLabel():
    printProperty("gda.exafs.i18.windows.label")

def setExafsWindowsLabel(newLabel):
    LocalProperties.set("gda.exafs.i18.windows.label",newLabel)
    getExafsWindowsLabel()

def getExafsProperties():
    getExafsScanClass()
    getExafsWindowsDirectory()
    getExafsWindowsFilename()
    getExafsWindowsLabel()

def printProperty(property):
    print "%s = %s" % (property, LocalProperties.get(property))

def helpi18():
    print "The available commands are:"
    print "MicroFocus:"
    print "\t resetMicroFocusPanel()"
    print "\t getMicroFocusStepScanClass()"
    print "\t setMicroFocusStepScanClass('newClassName')"
    print "EXAFS:"
    print "\t getExafsProperties()"
    print "\t getExafsScanClass()"
    print "\t setExafsScanClass('newClassName')"
    print "\t getExafsWindowsDirectory()"
    print "\t setExafsWindowsDirectory('newDirectory')"
    print "\t getExafsWindowsFilename()"
    print "\t setExafsWindowsFilename('newFilename')"
    print "\t getExafsWindowsLabel()"
    print "\t setExafsWindowsLabel('newLabel')"
    
