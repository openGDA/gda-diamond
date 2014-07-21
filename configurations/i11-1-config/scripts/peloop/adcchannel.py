'''
Created on 15 Feb 2011

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from gda.factory import FactoryException
from gov.aps.jca import CAException
import sys
from gov.aps.jca.event import MonitorListener


def sum_datasets(datasets):
    #{0: [1,2,3], 1: [3,4,5], 2: [6,7,8]}
    lists = [x.tolist() for x in datasets.values()]
    if len(lists) == 1:
        return lists[0]
    data = zip(*tuple(lists))
    #[(1,3,6), (2,4,7)...]
    data = [float(sum(xs)) / len(xs) for xs in data]
    #[3.333, ...]
    return data
#EPICS PVs
adcppv="BL11I-EA-PE-01:HV"
adcepv="BL11I-EA-PE-01:EL"
adcgatepv="BL11i-ea-pe-01:TRIG"

class ADCChannel(ScannableMotionBase, MonitorListener):
    
    def __init__(self, name, pv):
        self.setName(name)
        self.setInputNames([])
        self.pvcli=CAClient(pv)
        self.nordcli=CAClient(pv+".NORD")
        self.monitoradded=False
        self.counter=0
        self.numberofgates=0
        self.numberofframes=0
        self.filename=None
        self.filenames=[]
        self.collectionNumber=0 #0 means no collectionNumber
        self.voltagesmonitor=None
        self.firstMonitor = True
        self.voltages = {}
        
    def resetCounter(self):
        self.counter=0
        
    def resetRepetition(self):
        self.collectionNumber=0
        
    def setCollectionNumber(self, num):
        self.collectionNumber=num
        
    def setNumberOfGates(self, num):
        self.numberofgates=num
        
    def setNumberOfFrames(self, num):
        self.numberofframes=num
        
    def getNumberOfGates(self):
        return self.numberofgates
    
    def getNumberOfFrames(self):
        return self.numberofframes
    
    def setFilename(self, filename):
        self.filename=filename
        
    def getFilename(self):
        return self.filename
    
    def getFilenames(self):
        return self.filenames
    
    def getValues(self):
        try:
            if not self.pvcli.isConfigured():
                self.pvcli.configure()
            return self.pvcli.cagetArrayDouble()
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.pvcli.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.pvcli.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
    def getValuesNum(self,num):
        try:
            if not self.pvcli.isConfigured():
                self.pvcli.configure()
            return self.pvcli.cagetArrayDouble(num)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.pvcli.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.pvcli.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getNord(self):
        try:
            if not self.nordcli.isConfigured():
                self.nordcli.configure()
            return int(float(self.nordcli.caget()))
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.nordcli.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.nordcli.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def addMonitor(self, count):
        if self.monitoradded:
            #monitor already added, prevent adding more than one monitor
            return
        self.firstMonitor=True
        try:
            if not self.pvcli.isConfigured():
                self.pvcli.configure()
            self.voltagesmonitor=self.pvcli.camonitor(self, count)
            self.monitoradded=True
        except CAException, e:
            self.monitoradded=False
            print "camonitor Error (%s): %s" % (self.pvcli.getChannel().getName(),e)
        except:
            self.monitoradded=False
            print "Unexpected error:", sys.exc_info()[0]
            raise

    
    def removeMonitor(self):
        if not self.monitoradded:
            #monitor does not exist
            return
        self.firstMonitor=True
        try:
            if not self.pvcli.isConfigured():
                self.pvcli.configure()
            if self.voltagesmonitor != None:
                self.pvcli.removeMonitor(self.voltagesmonitor)
            self.monitoradded=False
        except CAException, e:
            self.monitoradded=True
            print "camonitor Error (%s): %s" % (self.pvcli.getChannel().getName(),e)
        except:
            self.monitoradded=True
            print "Unexpected error:", sys.exc_info()[0]
            raise
        
    def monitorChanged(self, mevent):
        if self.firstMonitor:
            self.firstMonitor = False
            return        
        if self.counter < self.numberofgates:
            if self.counter not in self.voltages:
                self.voltages[self.counter]=[]
            nord=self.getNord()
            print nord
            self.voltages[self.counter] = self.getValuesNum(nord)[1:]
            #print dir(voltages[self.counter])
            #print len(voltages[self.counter])
            #print type(voltages[self.counter]) #[1:nord]
            #print self.voltages[self.counter][:5]
            self.counter += 1
        if self.counter == self.numberofgates:
            self.filenames.append(self.filename+"_"+self.getName()+"_"+str(self.collectionNumber))
            #kick off a thread to process and save data so not to block monitor event process here.
            #savedata=SaveData(name=self.getName()+"-"+str(self.collectionNumber), args=(self.filenames[self.collectionNumber]+".dat", "w", self.getName()), kwargs=voltages)
            #savedata.start()
            self.save(args=(self.filenames[self.collectionNumber]+".dat", "w", self.getName()), kwargs=self.voltages)
            self.voltages={}
            self.collectionNumber+=1
            self.resetCounter()
            self.filenames=[]
            
    def save(self, args=(), kwargs={}):
        print "summing data points..."
        self.data = sum_datasets(kwargs)
        print "%s: saving data to %s" % (args[2], args[0])
        self.file=open(args[0], args[1])
        for each in self.data:
            self.file.write("%s\n"%each)
        self.file.close()
        print "%s: save data to %s completed." % (args[2], args[0])
            
    def getExtraNames(self):
        repetition=[]
        for i in range(self.collectionNumber):
            repetition.append(str(i))
        return repetition
    
    def atScanStart(self):
        self.resetCounter()
        self.resetRepetition()

    def atScanEnd(self):
        pass

    def atPointStart(self):
        self.resetCounter()
        self.resetRepetition()
    
    def atPointEnd(self):
        pass

    def getPosition(self):
        return self.getFilenames()

    def asynchronousMoveTo(self,new_position):
        pass
    
    def isBusy(self):
        return False
    
#    def toString(self):
#        return self.name + " : " + str(self.getPosition())
voltage=ADCChannel("voltage",adcppv)
electrometer=ADCChannel("electrometer", adcepv)
gate=ADCChannel("gate", adcgatepv)