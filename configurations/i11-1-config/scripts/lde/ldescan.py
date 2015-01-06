'''
Created on 10 Oct 2014

@author: fy65
'''
from gda.device import Detector
from gda.device.scannable import DummyScannable
from gda.factory import Finder
from gda.jython.commands.ScannableCommands import scan

ds1=DummyScannable("ds1")
NDR=0
CAL=1
calName=Finder.getInstance().find("calibrantName")

dr=Finder.getInstance().find("datareduction")
def ldescan(*args):
    MUSTADDDATAREDUCTIONATEND=False
    newargs=[]
    i=0
    #processing 1st argument
    if (args[i] == NDR):
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
        if (args[i]==CAL):
            if (str(calName.getPosition())=="Undefined"):  # @UndefinedVariable
                raise Exception("Calibrant name is not defined.")
            dr.setCalibrant(True)
        else:
            dr.setCalibrant(False)
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
        