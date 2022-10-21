'''
Created on 10 Oct 2014

@author: fy65
'''
from gda.device import Detector
from gda.device.scannable import DummyScannable
from gda.factory import Finder
from gda.jython.commands.ScannableCommands import scan

from gdaserver import process, calibration, GDAMetadata as meta
import time

ds1=DummyScannable("ds1")
NDR=0
CAL=1
calName=Finder.find("calibrantName")

dr=Finder.find("datareduction")
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
            meta['calibration_file'] = ''
            dr.setCalibrant(True)
            proc = calibration
        else:
            dr.setCalibrant(False)
            proc = process
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

        newargs.append(proc)
        scan(newargs)
        if args[0] == CAL:
            print 'Waiting for calibration to complete'
            start = time.time()
            timeout = start + 300
            while time.time() < timeout:
                if meta['calibration_file']:
                    break
                time.sleep(2)
            else:
                raise ValueError('No calibration result received after 300s')

