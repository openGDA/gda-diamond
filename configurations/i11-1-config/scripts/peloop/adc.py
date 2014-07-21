'''
file: adc.py

Module defines ADC class that captures PE data from HV and Electro-meter potential during a PE Loop experiment.
It plots PE-Loop in 'DataPlot' panel.

Created on 15 Feb 2011
Modified on 21 June 2011

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
adcppv="BL11I-EA-PE-01:HV"
adcepv="BL11I-EA-PE-01:EL"
adcgatepv="BL11I-EA-PE-01:TRIG"
#EPICS PVs for control of ADC settings
adcmodepv="BL11I-EA-ADC-02:MODE"
adcclockratepv="BL11I-EA-ADC-02:CLOCKRATE"
adcextclockpv="BL11I-EA-ADC-02:EXTCLOCK"
adcenablepv="BL11I-EA-ADC-02:ENABLE"
adcreenablepv="BL11I-EA-ADC-02:REENABLE"
adcsofttrigpv="BL11I-EA-ADC-02:SOFTTRIGGER.VAL"
adcsamplespv="BL11I-EA-ADC-02:SAMPLES:OUT"
adcoffsetpv="BL11I-EA-ADC-02:OFFSET:OUT"
adcaveragepv="BL11I-EA-ADC-02:AVERAGE:OUT"
#EPICS key-value enum setting
adcmode={ "Continuous":0,"Trigger":1,"Gate":2}
adcclockrate={"1 Hz":0, "2 Hz":1,"5 Hz":2,"10 Hz":3, "20 Hz":4,"50 Hz":5,"100 Hz":6, "200 Hz":7,"500 Hz":8, "1 kHz":9, "2 kHz":10,"5 kHz":11, "10 kHz":12, "20 kHz":13,"50 kHz":14,"110 kHz":15}
adcextclock={"Internal":0, "External":1}
adcenable={"Disabled":0,"Enabled":1}
adcreenable={ "Manual":0,"Auto":1}
adcsofttrig={"Done":0,"Busy":1}

class ADC(ScannableMotionBase, MonitorListener):
    
    def __init__(self, name, hv=adcppv, el=adcepv, gate=adcgatepv):
        self.setName(name)
        self.setInputNames([])
        self.hv=hv
        self.el=el
        self.gate=gate
        self.voltagecli=CAClient(hv)
        self.electrometercli=CAClient(el)
        self.gatecli=CAClient(gate)
        self.voltagenordcli=CAClient(hv+".NORD")
        self.electrometernordcli=CAClient(el+".NORD")
        self.monitoradded=False
        self.filename=None
        self.voltagemonitor=None
        self.electrometermonitor=None
        self.gatemonitor=None
        self.firstMonitor = True
        self.data={hv:[],el:[],gate:[]}
        self.voltages = []      # for holding voltage data array
        self.electrometers=[]   # for holding electrometer data array
        self.gates=[]
        self.firstData = True
        self.fastmode = False
        self.numberofgate=0
        self.fastMode=True
        self.updatecounter=0
        self.collectionNumber=1
               
    def setNumberOfGates(self, ng):
        self.numberofgate=ng
        
    def getNumberOfGates(self):
        return self.numberofgate
    
    def getCollectionNumber(self):
        return self.collectionNumber
    
    def setCollectionNumber(self, num):
        self.collectionNumber=num
    
    def isFastMode(self):
        return self.fastMode
    
    def setFastMode(self, mode):
        self.fastMode=mode
        
    def reset(self):
        self.electrometers = []
        self.voltages = []
        self.updatecounter=0
        self.collectionNumber=1
        
    def setFilename(self, filename):
        self.filename=filename
        
    def getFilename(self):
        return self.filename
    
    def getElectrometer(self, num):
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
        
    def getElectrometerNord(self):
        try:
            if not self.electrometernordcli.isConfigured():
                self.electrometernordcli.configure()
            return int(float(self.electrometernordcli.caget()))
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.electrometernordcli.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.electrometernordcli.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getVoltageNord(self):
        try:
            if not self.voltagenordcli.isConfigured():
                self.voltagenordcli.configure()
            return int(float(self.voltagenordcli.caget()))
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.voltagenordcli.getChannel().getName(),e)
        except CAException, e:
            print "caget Error (%s): %s" % (self.voltagenordcli.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
   
    def addMonitor(self, count):
        if self.monitoradded:
            #voltagemonitor already added, prevent adding more than one voltagemonitor
            return
        self.firstMonitor=True
        try:
            if not self.voltagecli.isConfigured():
                self.voltagecli.configure()
            self.voltagemonitor=self.voltagecli.camonitor(self, count)
            self.monitoradded=True
        except CAException, e:
            self.monitoradded=False
            print "camonitor Error (%s): %s" % (self.voltagecli.getChannel().getName(),e)
        except:
            self.monitoradded=False
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def addMonitors(self):
        if self.monitoradded:
            #voltagemonitor already added, prevent adding more than one voltagemonitor
            return
        self.firstMonitor=True
        try:
            if not self.voltagecli.isConfigured():
                self.voltagecli.configure()
            self.voltagemonitor=self.voltagecli.camonitor(self)
            if not self.electrometercli.isConfigured():
                self.electrometercli.configure()
            self.electrometermonitor=self.electrometercli.camonitor(self)
            if not self.gatecli.isConfigured():
                self.gatecli.configure()
            self.gatemonitor=self.gatecli.camonitor(self)
            self.monitoradded=True
        except CAException, e:
            self.monitoradded=False
            print "camonitor Error (%s): %s" % (self.voltagecli.getChannel().getName(),e)
        except:
            self.monitoradded=False
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def removeMonitor(self):
        if not self.monitoradded:
            #voltagemonitor does not exist
            return
        self.firstMonitor=True
        try:
            if not self.voltagecli.isConfigured():
                self.voltagecli.configure()
            if self.voltagemonitor != None:
                self.voltagecli.removeMonitor(self.voltagemonitor)
            self.monitoradded=False
        except CAException, e:
            self.monitoradded=True
            print "camonitor Error (%s): %s" % (self.voltagecli.getChannel().getName(),e)
        except:
            self.monitoradded=True
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def removeMonitors(self):
        if not self.monitoradded:
            #voltagemonitor does not exist
            return
        self.firstMonitor=True
        try:
            if not self.voltagecli.isConfigured():
                self.voltagecli.configure()
            if self.voltagemonitor != None:
                self.voltagecli.removeMonitor(self.voltagemonitor)
            if self.electrometermonitor != None:
                self.voltagecli.removeMonitor(self.electrometermonitor)
            if self.gatemonitor != None:
                self.voltagecli.removeMonitor(self.gatemonitor)
            self.monitoradded=False
        except CAException, e:
            self.monitoradded=True
            print "camonitor Error (%s): %s" % (self.voltagecli.getChannel().getName(),e)
        except:
            self.monitoradded=True
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def monitorChanged(self, mevent):
        if self.firstMonitor:
            self.firstMonitor = False
            return
        self.updatecounter +=1
        self.data[mevent.getSource().getName()].append(mevent.getDBR().getDoubleValue())      
        #vnord=self.getVoltageNord()
        #if not self.isFastMode():
            #print "frame number collected: ", self.framenumber
            #self.framenumber +=1
        #self.voltages.append(self.getVoltage(vnord)[1:])
        #self.electrometers.append(self.getElectrometer(vnord)[1:])
        if self.updatecounter/3 >= self.numberofgate:
            self.collectionNumber += 1
            self.updatecounter=0
            self.save3Data(self.collectionNumber)
            
    def save3Data(self, collectionNumber=None):
        voltages=[]
        electrometers=[]
        gates=[]
        if collectionNumber == None:
            filename = self.filename+"_"+self.getName()+".dat"
            print "concatenating data points to produce P-E data..."
            for each in self.data[self.hv]:
                voltages += each
                self.data[self.hv] += []
            for each in self.data[self.el]:
                electrometers += each
                self.data[self.el] += []
            for each in self.data[self.gate]:
                gates += each
                self.data[self.gate] += []
        else:
            filename = self.filename+"_"+self.getName()+"_"+str(collectionNumber)+".dat"
            for each in self.data[self.hv]:
                voltages += each
                #voltages += []
            for each in self.data[self.el]:
                electrometers += each
                #electrometers += []
            for each in self.data[self.gate]:
                gates += each
            self.data[self.hv]=[]
            self.data[self.el]=[]
            self.data[self.gate]=[]
        print "%s: saving data to %s" % (self.getName(), filename)
        if len(voltages) != len(electrometers):
            print "***Warning: voltage nord: %d, electrometer nord: %d" % (len(voltages),len(electrometers))
        self.file=open(filename, "w")
        for voltage, electrometer, gate in zip(voltages, electrometers, gates):
            self.file.write("%f\t%f\t%f\n"%(voltage, electrometer,gate))
        self.file.close()
        print "%s: save data to %s completed." % (self.getName(), filename)
        voltagearray=scisoftpy.array(voltages)
        electrometerarray=scisoftpy.array(electrometers)
        vds=scisoftpy.toDS(voltagearray)
        eds=scisoftpy.toDS(electrometerarray)
        print "plotting PE-loop in 'DataPlot' panel..."
        if self.firstData:
            Plotter.plot("DataPlot", vds, eds)
            self.firstData=False
        else:
            Plotter.plotOver("DataPlot", vds, eds)

    def saveData(self, collectionNumber=None):
        voltages=[]
        electrometers=[]
        if collectionNumber == None:
            filename = self.filename+"_"+self.getName()+".dat"
            print "concatenating data points to produce P-E data..."
            for each in self.voltages:
                voltages += each
                self.voltages += []
            for each in self.electrometers:
                electrometers += each
                self.electrometers += []
        else:
            filename = self.filename+"_"+self.getName()+"_"+str(collectionNumber)+".dat"
            if self.numberofgate >1:
                print "summing data points to produce P-E data..."
                voltages = sum_datasets(self.voltages)
                electrometers = sum_datasets(self.electrometers)
            else:
                for each in self.voltages:
                    voltages += each
                    #voltages += []
                for each in self.electrometers:
                    electrometers += each
                    #electrometers += []
            self.voltages=[]
            self.electrometers=[]
        print "%s: saving data to %s" % (self.getName(), filename)
        if len(voltages) != len(electrometers):
            print "***Warning: voltage nord: %d, electrometer nord: %d" % (len(voltages),len(electrometers))
        self.file=open(filename, "w")
        for voltage, electrometer in zip(voltages, electrometers):
            self.file.write("%f\t%f\n"%(voltage, electrometer))
        self.file.close()
        print "%s: save data to %s completed." % (self.getName(), filename)
        voltagearray=scisoftpy.array(voltages)
        electrometerarray=scisoftpy.array(electrometers)
        vds=scisoftpy.toDS(voltagearray)
        eds=scisoftpy.toDS(electrometerarray)
        print "plotting PE-loop in 'DataPlot' panel..."
        if self.firstData:
            Plotter.plot("DataPlot", vds, eds)
            self.firstData=False
        else:
            Plotter.plotOver("DataPlot", vds, eds)
        
    def save(self, collectionNumber=None):
        voltages=[]
        electrometers=[]
        if collectionNumber == None:
            filename = self.filename+"_"+self.getName()+".dat"
            print "concatenating data points to produce P-E data..."
            for each in self.voltages:
                voltages += each
                voltages += []
            for each in self.electrometers:
                electrometers += each
                electrometers += []
        else:
            filename = self.filename+"_"+self.getName()+"_"+str(collectionNumber)+".dat"
            print "summing data points to produce P-E data..."
            voltages = sum_datasets(self.voltages)
            electrometers = sum_datasets(self.electrometers)
        print "%s: saving data to %s" % (self.getName(), filename)
        if len(voltages) != len(electrometers):
            print "***Warning: voltage nord: %d, electrometer nord: %d" % (len(voltages),len(electrometers))
        self.file=open(filename, "w")
        for voltage, electrometer in zip(voltages, electrometers):
            self.file.write("%f\t%f\n"%(voltage, electrometer))
        self.file.close()
        print "%s: save data to %s completed." % (self.getName(), filename)
        voltagearray=scisoftpy.array(voltages)
        electrometerarray=scisoftpy.array(electrometers)
        vds=scisoftpy.toDS(voltagearray)
        eds=scisoftpy.toDS(electrometerarray)
        print "plotting PE-loop in 'DataPlot' panel..."
        if self.firstData:
            Plotter.plot("DataPlot", vds, eds)
            self.firstData=False
        else:
            Plotter.plotOver("DataPlot", vds, eds)
        

    
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
