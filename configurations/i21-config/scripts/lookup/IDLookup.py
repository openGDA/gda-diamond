'''
Created on 30 Aug 2016

@author: fy65
'''
from external import create_function
# from scisoftpy.external import create_function
import time

starttime=time.time()
INSIDE_DIAMOND_NETWORK=True
if INSIDE_DIAMOND_NETWORK:
    #The lookupTable table
    lookup_file='/dls_sw/i21/software/gda/config/lookupTables/LinearAngle.csv'
    #Lookup module - a symlink to 'i21-python' project
    local_module_path='/dls_sw/i21/software/gda/pythonscript/lookupTable'
    # To solve the problem that PyDev/ Jython was passing JYTHONPATH as PYTHONPATH to the subprocess.
    # The fix was to load all the environment variables, change the Python Path to the correct spot for Python 2.7 and pass it to Popen through the env argument.
    python_path="/dls_sw/i21/software/miniconda2/envs/gdaenv/lib/python2.7/"
    python_exe="/dls_sw/i21/software/miniconda2/envs/gdaenv/bin/python"
else:
    #The lookupTable table
    lookup_file='/home/fy65/gda_versions/gda-master-20200626/workspace_git/gda-diamond.git/configurations/i21-config/lookupTables/LinearAngle.csv'
    #Lookup module - a symlink to 'i21-python' project
    local_module_path='/home/fy65/gda_versions/gda-master-20200626/workspace_git/gda-diamond.git/configurations/i21-python/src/lookupTable'
    # To solve the problem that PyDev/ Jython was passing JYTHONPATH as PYTHONPATH to the subprocess.
    # The fix was to load all the environment variables, change the Python Path to the correct spot for Python 2.7 and pass it to Popen through the env argument.
    python_path="/home/fy65/miniconda2/envs/gdaenv/lib/python2.7/"
    python_exe="/home/fy65/miniconda2/envs/gdaenv/bin/python"
    
class IDLookup4LinearAngleMode():
    def __init__(self, name, lut=lookup_file):
        self.name=name
        #TODO need to check and fix external process exit on termination so it does not left external process on after GDA stopped.
        self.lookupPolarEnergy=create_function("reverseLookup",module="Lookup2Dto2D", exe=python_exe, path=[python_path], extra_path=[local_module_path], keep=True)
        #self.lookupPolarEnergy=create_function("reverseLookup",module="Lookup2Dto2D", exe=python_exe, path=[python_path], extra_path=[local_module_path], dls_module=True, keep=True)
        self.lookupPolarEnergyCreatedInScanStart=False
        self.lookupGapPhase=create_function("forwardLookup", module="Lookup2Dto2D", exe=python_exe, path=[python_path], extra_path=[local_module_path], keep=True)
        #self.lookupGapPhase=create_function("forwardLookup", module="Lookup2Dto2D", exe=python_exe, path=[python_path], extra_path=[local_module_path], dls_module=True, keep=True)
        self.lookupGapPhaseCreatedInScanStart=False
        self.lut=lut
    
    def getEnergyPolarisation(self, gap, phase):
        out=self.lookupGapPhase(gap, phase, filename=self.lut)
#         return out # used in scisoftpy
        out= [float(x.strip(',')) for x in out.strip('\n').strip(']').strip('[').split(' ') if x.strip() not in ('[',']','') ]
        return out
    
    def getGapPhase(self, energy, polarisation):
        out=self.lookupPolarEnergy(polarisation, energy, filename=self.lut)
#         return out # used in scisoftpy
        out= [float(x.strip(',')) for x in out.strip('\n').strip(']').strip('[').split(' ') if x.strip() not in ('[',']','') ]
        return out
    
    def stop(self):
        if self.lookupPolarEnergyCreatedInScanStart==True:
            self.lookupPolarEnergy.stop()
        if self.lookupGapPhaseCreatedInScanStart==True:
            self.lookupGapPhase.stop()
        
idlam=IDLookup4LinearAngleMode("idlam", lut=lookup_file) 

endtime=time.time()
print "time taken for Initialisation: %s" % (endtime-starttime)

def main():
    # print idlam.getGapPhase(778.5350225, 30.0)
    print
    
    print "[gap, phase] -> [polarisation, energy]"
    for gap, phase in [(20, 0), (25, 5), (30, 10), (35, 15), (40, 20), (45, 25), (50, 28), (55, 23), (60, 17), (65, 13), (70, 8)]:
        starttime=time.time()
        print "[",gap,',', phase,']', "->", idlam.getEnergyPolarisation(gap,phase)
        endtime= time.time()
        print "time taken: %s" % (endtime-starttime)
        print
    
    print 
    
    print "[energy,polarisation] -> [gap,phase]"
    for energy, polar in [(300, 0), (400, -10), (500, -20), (600, -30), (700, -40), (800, -50), (900, -60), (1000, -70), (1100, -80)]:
        starttime=time.time()
        print "[",energy,",",polar,']', "->", idlam.getGapPhase(energy, polar)
        endtime= time.time()
        print "time taken: %s" % (endtime-starttime)
        print
    

if __name__=="__main__":
    main()