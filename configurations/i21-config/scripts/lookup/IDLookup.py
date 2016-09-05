'''
Created on 30 Aug 2016

@author: fy65
'''
from external import create_function
from gda.device.scannable import ScannableBase
import time

starttime=time.time()
#The lookupTable table
lookup_file='/dls_sw/i21/software/gda/config/lookupTables/LinearAngle.csv'
#Lookup module
local_module_path='/dls_sw/i21/software/gda/pythonscript/lookupTable'
java_pathsubprocess_path='/dls_sw/i21/software/gda_versions/gda_9.1/workspace_git/scisoft-core.git/uk.ac.diamond.scisoft.python/bin'

# To solve the problem that PyDev/ Jython was passing JYTHONPATH as PYTHONPATH to the subprocess.
# The fix was to load all the environment variables, change the Python Path to the correct spot for Python 2.7 and pass it to Popen through the env argument.
python_path="/dls_sw/i21/software/miniconda2/envs/gdaenv/lib/python2.7/"
python_exe="/dls_sw/i21/software/miniconda2/envs/gdaenv/bin/python"

class IDLookupScannable(ScannableBase):
    def __init__(self, name, gap=None, phase=None, lut=lookup_file):
        self.lookupPolarEnergy=create_function("reverseLookup",module="Lookup2Dto2D", exe=python_exe, path=[python_path], extra_path=[local_module_path,java_pathsubprocess_path],  keep=True)
        self.lookupPolarEnergyCreatedInScanStart=False
        self.lookupGapPhase=create_function("forwardLookup", module="Lookup2Dto2D", exe=python_exe, path=[python_path], extra_path=[local_module_path,java_pathsubprocess_path], keep=True)
        self.lookupGapPhaseCreatedInScanStart=False
        self.lut=lut
        self.gap=gap
        self.phase=phase
        
    def atScanStart(self):
        if self.lookupPolarEnergy.proc is None:
            self.lookupPolarEnergy=create_function("reverseLookup",module="Lookup2Dto2D", exe=python_exe, path=[python_path], extra_path=[local_module_path], dls_module=True, keep=True)
            self.lookupPolarEnergyCreatedInScanStart=True
        if self.lookupGapPhase is None:
            self.lookupGapPhase=create_function("forwardLookup",module="Lookup2Dto2D", exe=python_exe, path=[python_path], extra_path=[local_module_path], dls_module=True, keep=True)
            self.lookupGapPhaseCreatedInScanStart=True
        
    def atScanEnd(self):
        self.stop()
             
    def getEnergyPolarisation(self, gap, phase):
        out=self.lookupGapPhase(gap, phase, filename=self.lut)
        return out.strip('\n')
    
    def getGapPhase(self, energy, polarisation):
        out=self.lookupPolarEnergy(polarisation, energy, filename=self.lut)
        return out.strip('\n')
    
    def getPosition(self):
        if not self.gap == None:
            gap=float(self.gap.getPosition())
        if not self.phase == None:
            phase=float(self.phase.getPosition())
        return self.getEnergyPolarisation(gap, phase)
    
    def asynchronousMoveTo(self, energy, polarisation):
        gap, phase = self.getGapPhase(energy, polarisation)
        if not self.gap == None:
            self.gap.asynchronousMoveTo(gap)
        if not self.phase == None:
            self.phase.asynchronousMoveTo(phase)
        
    def isBusy(self):
        _busy=False
        if not self.gap == None:
            _busy=self.gap.isBusy()
        if not self.phase == None:
            _busy = _busy or self.phase.isBusy()
        return _busy
    
    def stop(self):
        if self.lookupPolarEnergyCreatedInScanStart==True:
            self.lookupPolarEnergy.stop()
        if self.lookupGapPhaseCreatedInScanStart==True:
            self.lookupGapPhase.stop()
        
energypolar=IDLookupScannable("energypolar", lut=lookup_file)
endtime=time.time()
print (endtime-starttime)

def main():
    print
    for gap, phase in [(20, 0), (25, 5), (30, 10), (35, 15), (40, 20), (45, 25), (50, 28), (55, 23), (60, 17), (65, 13), (70, 8)]:
        starttime=time.time()
        print energypolar.getEnergyPolarisation(gap,phase)
        endtime= time.time()
        print (endtime-starttime)
    
    print 
    
    for energy, polar in [(300, 0), (400, -10), (500, -20), (600, -30), (700, -40), (800, -50), (900, -60), (1000, -70), (1100, -80)]:
        starttime=time.time()
        print energypolar.getGapPhase(energy, polar)
        endtime= time.time()
        print (endtime-starttime)
    

if __name__=="__main__":
    main()