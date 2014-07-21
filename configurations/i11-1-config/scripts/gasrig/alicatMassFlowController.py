'''
Created on 6 Dec 2013

@author: fy65
'''
from gda.epics import CAClient
#ROOT_PV="I11GasRig:MFC1:"
READ_MASS_FLOW="MASS:FLOW:RD"
READ_MASS_FLOW_TARGET="SETPOINT:RD"
SET_MASS_FLOW_TARGET="SETPOINT:WR"
READ_GAS_TYPE="GAS:STR:RD"
SET_GAS_TYPE_BY_NUMBER="GAS:WR"
SELECT_GAS_TYPE_1="GAS:SEL1"
SELECT_GAS_TYPE_2="GAS:SEL2"
READ_PRESSURE_IN_BAR="PBAR:RD"
READ_TEMPERATURE="TEMP:RD"
READ_VOLUMETRIC_FLOW="VOL:FLOW:RD"
READ_PROPORTIONAL_GAIN="PGAIN:RD"
SET_PROPORTIONAL_GAIN="PGAIN:WR"
READ_DERIVATIVE_GAIN="DGAIN:RD"
SET_DERIVATIVE_GAIN="DGAIN:WR"

gasTypes={0:"Air",1:"Ar",2:"CH4",3:"CO",4:"CO2",5:"C2H6",6:"H2",7:"He",8:"N2",9:"N2O",10:"Ne",
          11:"O2",12:"C3H8",13:"n-C4H10",14:"C2H2",15:"C2H4",16:"i-C2H10",17:"Kr",18:"Xe",19:"SF6",20:"C-25",
          21:"C-10",22:"C-8",23:"C-2",24:"C-75",25:"A-75",26:"A-25",27:"A-1025",28:"Star29",29:"P-5"}

from gda.device.scannable import ScannableMotionBase

class AlicatMassFlowController(ScannableMotionBase):
    '''
    classdocs
    '''
    def __init__(self,name, rootPV, formatstring):
        '''
        Constructor
        '''
        self.setName(name);
        self.setInputNames([name])
        self.setOutputFormat([formatstring])
        self.setLevel(3)
        self.currentflowcli=CAClient(rootPV+READ_MASS_FLOW)
        self.setflowtargetcli=CAClient(rootPV+SET_MASS_FLOW_TARGET)
        self.readflowtargetcli=CAClient(rootPV+READ_MASS_FLOW_TARGET)
        self.currentgastypecli=CAClient(rootPV+READ_GAS_TYPE)
        self.setfgastype1cli=CAClient(rootPV+SELECT_GAS_TYPE_1)
        self.setfgastype2cli=CAClient(rootPV+SELECT_GAS_TYPE_2)
        self.setgastypenumbercli=CAClient(rootPV+SET_GAS_TYPE_BY_NUMBER)
        self.pressurecli=CAClient(rootPV+READ_PRESSURE_IN_BAR)
        self.temperaturecli=CAClient(rootPV+READ_TEMPERATURE)
        self.volumetricflowcli=CAClient(rootPV+READ_VOLUMETRIC_FLOW)
        self.setproportionalgaincli=CAClient(rootPV+SET_PROPORTIONAL_GAIN)
        self.readproportionalgaincli=CAClient(rootPV+READ_PROPORTIONAL_GAIN)
        self.setderivativegaincli=CAClient(rootPV+SET_DERIVATIVE_GAIN)
        self.readderivativegaincli=CAClient(rootPV+READ_DERIVATIVE_GAIN)
        
    def getCurrentFlow(self):
        try:
            if not self.currentflowcli.isConfigured():
                self.currentflowcli.configure()
                output=float(self.currentflowcli.caget())
                self.currentflowcli.clearup()
            else:
                output=float(self.currentflowcli.caget())
            return output
        except:
            print "Error returning current flow value"
            return 0

    def setTarget(self, target):
        try:
            if not self.setflowtargetcli.isConfigured():
                self.setflowtargetcli.configure()
                self.setflowtargetcli.caput(target)
                self.setflowtargetcli.clearup()
            else:
                self.setflowtargetcli.caput(target)
        except:
            print "error set to target flow value"

    def getTarget(self):
        try:
            if not self.readflowtargetcli.isConfigured():
                self.readflowtargetcli.configure()
                output=float(self.currentflowcli.caget())
                self.readflowtargetcli.clearup()
            else:
                output=float(self.readflowtargetcli.caget())
            return output
        except:
            print "Error returning flow target value"
            return 0

    def getGasType(self):
        #self.currentgastypecli does not work in EPICS
        try:
            if not self.setgastypenumbercli.isConfigured():
                self.setgastypenumbercli.configure()
                output=int(self.setgastypenumbercli.caget())
                self.setgastypenumbercli.clearup()
            else:
                output=int(self.setgastypenumbercli.caget())
            return gasTypes[output]
        except:
            print "Error returning current gas type"
            return 0
        
    def setGasType(self,name):
        key=gasTypes.keys()[(gasTypes.values()).index(name)]
        if int(key)>=0 or int(key) <16:
            try:
                if not self.setfgastype1cli.isConfigured():
                    self.setfgastype1cli.configure()
                    self.setfgastype1cli.caput(name)
                    self.setfgastype1cli.clearup()
                else:
                    self.setfgastype1cli.caput(name)
            except:
                print "error set to gas type 1"
        else:
            try:
                if not self.setfgastype2cli.isConfigured():
                    self.setfgastype2cli.configure()
                    self.setfgastype2cli.caput(name)
                    self.setfgastype2cli.clearup()
                else:
                    self.setfgastype2cli.caput(name)
            except:
                print "error set to gas type 2"
            
    def getPressure(self):
        try:
            if not self.pressurecli.isConfigured():
                self.pressurecli.configure()
                output=float(self.pressurecli.caget())
                self.pressurecli.clearup()
            else:
                output=float(self.pressurecli.caget())
            return output
        except:
            print "Error returning pressure"
            return 0
        
    def getTemperature(self):
        try:
            if not self.temperaturecli.isConfigured():
                self.temperaturecli.configure()
                output=float(self.temperaturecli.caget())
                self.temperaturecli.clearup()
            else:
                output=float(self.temperaturecli.caget())
            return output
        except:
            print "Error returning temperature"
            return 0
   
    def getVolumetricFlow(self):
        try:
            if not self.volumetricflowcli.isConfigured():
                self.volumetricflowcli.configure()
                output=float(self.volumetricflowcli.caget())
                self.volumetricflowcli.clearup()
            else:
                output=float(self.volumetricflowcli.caget())
            return output
        except:
            print "Error returning volumetric flow"
            return 0

    def getProportionalGain(self):
        try:
            if not self.readproportionalgaincli.isConfigured():
                self.readproportionalgaincli.configure()
                output=float(self.readproportionalgaincli.caget())
                self.readproportionalgaincli.clearup()
            else:
                output=float(self.readproportionalgaincli.caget())
            return output
        except:
            print "Error returning Proportional Gain"
            return 0

    def setProportionalGain(self, gain):
        try:
            if not self.setproportionalgaincli.isConfigured():
                self.setproportionalgaincli.configure()
                self.setproportionalgaincli.caput(gain)
                self.setproportionalgaincli.clearup()
            else:
                self.setproportionalgaincli.caput(gain)
        except:
            print "error set to proportional gain"

    def getDerivativeGain(self):
        try:
            if not self.readderivativegaincli.isConfigured():
                self.readderivativegaincli.configure()
                output=float(self.readderivativegaincli.caget())
                self.readderivativegaincli.clearup()
            else:
                output=float(self.readderivativegaincli.caget())
            return output
        except:
            print "Error returning Derivative Gain"
            return 0

    def setDerivativeGain(self, gain):
        try:
            if not self.setderivativegaincli.isConfigured():
                self.setderivativegaincli.configure()
                self.setderivativegaincli.caput(gain)
                self.setderivativegaincli.clearup()
            else:
                self.setderivativegaincli.caput(gain)
        except:
            print "error set to derivative gain"
            
            
#### methods for scannable 
    def atScanStart(self):
        pass
    def atPointStart(self):
        pass
    def getPosition(self):
        pass
    def asynchronousMoveTo(self, posi):
        pass
    def isBusy(self):
        return False
    def stop(self):
        pass
    def atPointEnd(self):
        pass
    def atScanEnd(self):
        pass
    

