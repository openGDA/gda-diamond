'''
file: pedatacapturer.py

Module defines a class that monitors PE data capturing in EPICS ADC during a PE Loop experiment.
It saves the whole PE data along with the gate signal from ADC to disk files and 
plots PE-Loop in 'DataPlot' panel.

This class requires the High Voltage Amplifier HV monitor being coonected to one ADC channel, 
the Keithley Amplifier measurement output being connected to another ADC channel,
and the gate signal from PSD gate out being connected to a third ADC channel.

Created on 30 Jan 2012
Based on adc.py create 15/02/2011.

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from gda.factory import FactoryException
from gov.aps.jca import CAException
import sys
from gov.aps.jca.event import MonitorListener
from gda.analysis import Plotter
import scisoftpy
from threading import Thread
#from localStation import adc2

def sum_datasets(lists):
    ''' sum multiple lists point-to-point and provide an average of the summed value for each point, return as a single list
    '''
    #[[1,2,3], [3,4,5], [6,7,8]]
    if len(lists) == 1:
        return lists[0]
    data = zip(*tuple(lists))
    #[(1,3,6), (2,4,7)...]
    data = [float(sum(xs)) / len(xs) for xs in data]
    #[3.333, ...]
    return data

#EPICS PVs represent data channels to collect from.
adcppv="BL11I-EA-PE-01:HV1"
adcepv="BL11I-EA-PE-01:EL1"

class DataCapturer(ScannableMotionBase, MonitorListener):
    
    def __init__(self, name, hv=adcppv, el=adcepv): 
        self.setName(name)
        self.setInputNames(["HV","Electrometer"])
        self.hv=hv
        self.el=el
        self.voltagecli=CAClient(hv)
        self.electrometercli=CAClient(el)
        self.monitoradded=False
        self.filename=None
        self.voltagemonitor=None
        self.electrometermonitor=None
        self.firstMonitor = True
        self.data={hv:[],el:[]}
        self.voltages = []      # for holding voltage data array
        self.electrometers=[]   # for holding electrometer data array
        self.firstData = True
        self.updatecounter=0
        self.capturecounter=0
        self.numberofgate=0
        self.collectionNumber=1
        self.frameCounter=0

    def setNumberOfGates(self, ng):
        self.numberofgate=ng
        
    def getNumberOfGates(self):
        return self.numberofgate

    def getCollectionNumber(self):
        return self.collectionNumber
    
    def setCollectionNumber(self, num):
        self.collectionNumber=num

    def reset(self):
        self.electrometers = []
        self.voltages = []
        self.updatecounter=0
        self.capturecounter=0
        self.firstData = True
        self.data={self.hv:[],self.el:[]}
        self.frameCounter=0
        
    def setFilename(self, filename):
        self.filename=filename
        
    def getFilename(self):
        return self.filename
    
    def getElectrometer(self, num):
        ''' retrieve electrometer data from Keithley amplifier.
        '''
        try:
            if not self.electrometercli.isConfigured():
                self.electrometercli.configure()
            return self.electrometercli.cagetArrayDouble(num)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.electrometercli.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.electrometercli.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getVoltage(self, num):
        '''retrieve high voltage data from the High Voltage Amplifier
        '''
        try:
            if not self.voltagecli.isConfigured():
                self.voltagecli.configure()
            return self.voltagecli.cagetArrayDouble(num)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.voltagecli.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.voltagecli.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def addMonitors(self):
        '''add monitors to EPICS ADC HV, electrometer, and gate channels 
        '''
        if self.monitoradded:
            #monitor already added, prevent adding more than one monitor
            return
        self.firstMonitor=True  #to stop add update
        print "%s: adding PE and gate data monitors" % self.getName()
        #self.adc.disable()
        try:
            if not self.voltagecli.isConfigured():
                self.voltagecli.configure()
            self.voltagemonitor=self.voltagecli.camonitor(self)
            if not self.electrometercli.isConfigured():
                self.electrometercli.configure()
            self.electrometermonitor=self.electrometercli.camonitor(self)
            self.monitoradded=True
            print "%s: PE and gate data monitors are added." % self.getName()
        except CAException, e:
            self.monitoradded=False
            print "camonitor Error (%s): %s" % ("failed to add required monitors",e)
        except:
            self.monitoradded=False
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def removeMonitors(self):
        '''remove monitors to EPICS ADC HV, electrometer, and gate channels
        '''
        if not self.monitoradded:
            #monitors doe not exist
            return
        self.firstMonitor=True
        try:
            if not self.voltagecli.isConfigured():
                self.voltagecli.configure()
            if self.voltagemonitor != None:
                self.voltagecli.removeMonitor(self.voltagemonitor)
            if not self.electrometercli.isConfigured():
                self.electrometercli.configure()
            if self.electrometermonitor != None:
                self.electrometercli.removeMonitor(self.electrometermonitor)
            self.monitoradded=False
            print "%s: PE and gate data monitors removed." % self.getName()
        except CAException, e:
            self.monitoradded=True
            print "camonitor Error (%s): %s" % ("failed to remove monitors",e)
        except:
            self.monitoradded=True
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def monitorChanged(self, mevent):
        if self.firstMonitor:
            self.firstMonitor = False
            self.updatecounter=0
            self.data={self.hv:[],self.el:[]}
            self.frameCounter=0
            return
        self.data[mevent.getSource().getName()].append(mevent.getDBR().getDoubleValue()[0])
        #print mevent.getSource().getName()
        self.updatecounter += 1
        if self.updatecounter%2 == 0:
            self.capturecounter += 1
            print  "%s: PE data %d: HV=%f,EL=%f" % (self.getName(), self.capturecounter, self.data[self.hv][-1], self.data[self.el][-1])
            if self.capturecounter==self.numberofgate:
                #plotthread=Thread(target=self.plotPEdata, name="plot", args=(self.capturecounter-1,), kwargs=self.data)
                #plotthread.start()
                self.save(self.filename, self.collectionNumber, self.frameCounter)
                self.frameCounter +=1
                self.capturecounter=0
                
            
    def plotPEdata(self, *args, **kwargs):
            xarray=scisoftpy.array(kwargs[self.hv][args[0]])
            yrarray=scisoftpy.array(kwargs[self.el][args[0]])
            vds=scisoftpy.toDS(xarray)
            eds=scisoftpy.toDS(yrarray)
            print "plotting PE-loop in 'DataPlot' panel..."
            if self.firstData:
                Plotter.plot("DataPlot", vds, eds)
                self.firstData=False
            else:
                Plotter.plotOver("DataPlot", vds, eds)
            
            
    def save(self, filename,collectionNumber,frameNumber):
        #voltages=[]
        #electrometers=[]
        filename = filename+"-"+self.getName()+"-"+str(collectionNumber)+"_"+str(frameNumber)+".dat"
        print "process PE and gate data ..."
        #for each in self.data[self.hv]:
        voltages = self.data[self.hv]
        # for each in self.data[self.el]:
        electrometers = self.data[self.el]
        self.data[self.hv]=[]
        self.data[self.el]=[]
        print "%s: saving PE and gate data to %s" % (self.getName(), filename)
        if len(voltages) != len(electrometers):
            print "***Warning: voltage length: %d, electrometer length: %d" % (len(voltages),len(electrometers))
        self.file=open(filename, "w")
        for voltage, electrometer in zip(voltages, electrometers):
            self.file.write("%f\t%f\n"%(voltage, electrometer))
        self.file.close()
        print "%s: save data to %s completed." % (self.getName(), filename)

    def atScanStart(self):
        self.reset()
  
    def atScanEnd(self):
        pass

    def atPointStart(self):
        self.reset()
    
    def atPointEnd(self):
        pass

    def rawGetPosition(self):
        pass

    def rawAsynchronousMoveTo(self,new_position):
        pass
    
    def rawIsBusy(self):
        return False

    
    def setFirstData(self, value):
        self.firstData = value
    
    
    
#    def toString(self):
#        return self.name + " : " + str(self.getPosition())
