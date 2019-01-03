'''
A Module defines the diagnostic class and rules for checking PMT and WINDOW voltage settings on the ETLDetector hardware in EPICS, 
i.e. to check if the demand or requested HV values are successfully applied to the hardware - ETL detectors.
This is only a software tool to help scientists to quickly and easily diagnose potential voltage supply problems, 
but should not be regarded as final solution to hardware problems because it only simply compares 
the EPICS setValue with readbackValue. It is the responsibility of EPICS control system to ensure 
that the tested hardware is at the state as EPICS stated.
   
Created on 6 Nov 2009

@author: fy65
'''
from org.slf4j import Logger
from org.slf4j import LoggerFactory
from detector_control_class import DetectorControlClass
from diagnostics.diagnose import Diagnostics
logger=LoggerFactory.getLogger("i11.scripts.diagnostics.macDetectorDiagnostics")

class MACDetectorDiagnostics(Diagnostics):
    '''
    checking PMT, LLIM, ULIM settings for ETLDetectors in EPICS, 
    if they fall within stated tolerance they are OK, else they are reported as FAULT.
    
    To instantiate an object use
    
        macdiagnose=MACDetectorDiagnostics("diagnostic_object_name", ETLDetector_object, tolerance)
        
    to run the diagnose for all ETL detectors:
    
        macdiagnose.run()
        
    You may also diagnose individual voltage setting by (for example):
    
        pmt11.diagnose()
    '''

    def __init__(self, name, pds=[], tolerance=100):
        '''
        Create diagnostic object for all ETL detector voltages checking, with a default tolerance of 100mV.
        '''
        Diagnostics.__init__(self, name, pds)
        self.tolerance = tolerance
        self.addDiagnoseMethodToDetector()
       
    def addDiagnoseMethodToDetector(self):
        '''inject diagnose method to the class of the objects to be diagnosed.'''
        DetectorControlClass.diagnose=diagnose
   
    def __call__(self):
        self.run()

    def __repr__(self):
        self.run()
        return ""
         
          
def diagnose(self, tolerance = 100):
    '''Checking voltage settings for PMT and Window of a detector. Return True if passed, False if failed.'''
    if abs(float(self.getPosition())-float(self.getTargetPosition())) < tolerance:
        #print self.getName() + " is OK. (Target: " + str(self.getTargetPosition()) +", Current: " + str(self.getPosition()) + ")."
        logger.info("{} is OK.", self.getName())
        return True
    else:
        #print self.getName() + " is at FAULT. (Target: " + str(self.getTargetPosition()) +", Current: " + str(self.getPosition()) + ")."
        logger.warn("{} is at FAULT", self.getName())
        return False 
    