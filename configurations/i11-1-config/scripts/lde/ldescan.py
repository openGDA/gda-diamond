'''
Created on 10 Oct 2014

@author: fy65
'''
from org.opengda.lde.scannables import DataReductionScannable
from thredds.catalog import CollectionType
from gda.jython.commands.ScannableCommands import scan
from gda.device import Detector
from gda.device.scannable import DummyScannable
from gda.factory import Finder

ds1=DummyScannable("ds1")
NOREDUCTION=0
CALIBRANT=1
SAMPLE=2
dr=Finder.getInstance().find("datareduction")
def ldescan(*args):
    MUSTADDDATAREDUCTIONATEND=False
    newargs=[]
    i=0
    #processing 1st argument
    if (args[i] == NOREDUCTION):
        i=1
        if (isinstance(args[i], Detector)) :
            newargs.append(ds1)  # @UndefinedVariable
            newargs.append(1.0)
            newargs.append(1.0)
            newargs.append(1.0)
        while i<len(args):
            newargs.append(args[i])
            i=i+1
        scan(newargs)
    else:
        if (args[i]==CALIBRANT):
            dr.setCalibrant(True)
        elif (args[i]==SAMPLE):
            dr.setCalibrant(False)
        else:
            raise Exception("Collection Type '" + args[i] +"' not supported. Supported types are (NOREDUCTION, CALIBRANT, SAMPLE)")
        i=1
        if (isinstance(args[i], Detector)) :
            newargs.append(dr)
            newargs.append(1.0)
            newargs.append(1.0)
            newargs.append(1.0)
        else:
            MUSTADDDATAREDUCTIONATEND=True
        while i<len(args):
            newargs.append(args[i])
            i=i+1
        if MUSTADDDATAREDUCTIONATEND:
            newargs.append(dr)
        scan(newargs)
        