'''
Created on 30 Aug 2016

@author: fy65
'''
from external import create_function
# from scisoftpy.external import create_function
import time
import logging
from time import sleep

starttime=time.time()
INSIDE_DIAMOND_NETWORK=True
if INSIDE_DIAMOND_NETWORK:
    #The lookupTable table
    lookup_file='/dls_sw/i21/software/gda/config/lookupTables/LinearAngle.csv'
    #Lookup module - a symlink to 'i21-python' project
    local_module_path='/dls_sw/i21/software/gda/pythonscript/lookupTable'
    # To solve the problem that PyDev/ Jython was passing JYTHONPATH as PYTHONPATH to the subprocess.
    # The fix was to load all the environment variables, change the Python Path to the correct spot for Python 2.7 and pass it to Popen through the env argument.
    python_path="/dls_sw/i21/software/miniforge3/envs/gdaenv/lib/python2.7/"
    python_exe="/dls_sw/i21/software/miniforge3/envs/gdaenv/bin/python"
else:
    #The lookupTable table - for ubuntu on laptop running at home, not in Diamond network
    lookup_file='/home/fy65/gda_versions/gda-master-20200626/workspace_git/gda-diamond.git/configurations/i21-config/lookupTables/LinearAngle.csv'
    #Lookup module - a symlink to 'i21-python' project
    local_module_path='/home/fy65/gda_versions/gda-master-20200626/workspace_git/gda-diamond.git/configurations/i21-python/src/lookupTable'
    # To solve the problem that PyDev/ Jython was passing JYTHONPATH as PYTHONPATH to the subprocess.
    # The fix was to load all the environment variables, change the Python Path to the correct spot for Python 2.7 and pass it to Popen through the env argument.
    python_path="/home/fy65/miniforge3/envs/gdaenv/lib/python2.7/"
    python_exe="/home/fy65/miniforge3/envs/gdaenv/bin/python"
    
class IDLookup4LinearAngleMode():
    def __init__(self, name, lut = lookup_file):
        self.name=name
        # keep = False means external python process will end after each function call, it takes 1 to 2 seconds. if True, process only takes 0.1 to 0.5 second.
        self.lookup_polar_energy = create_function("reverseLookup",module="Lookup2Dto2D", exe=python_exe, path=[python_path], extra_path=[local_module_path], keep=True)
        self.lookup_polar_energy_created_in_scan_start = False
        self.lookup_gap_phase = create_function("forwardLookup", module="Lookup2Dto2D", exe=python_exe, path=[python_path], extra_path=[local_module_path], keep=True)
        self.lookup_gap_phase_created_in_scan_start = False
        self.lut = lut
        self.logger = logging.getLogger(self.__class__.__name__)
    

    def parseReturnedString(self, out):
        out = out.split('\n')
        out = [ x for x in out if x != ''] #remove the last empty string
        if len(out) == 1:
            out = [float(x.strip(',')) for x in out[0].strip(']').strip('[').split(' ') if x.strip() not in ('[', ']', '')]
        else:
            #if more then 1 pair returned, use the last pair, see I21-997
            out = [float(x.strip(',')) for x in out[len(out) - 1].strip(']').strip('[').split(' ') if x.strip() not in ('[', ']', '')]
        return out

    def getEnergyPolarisation(self, gap, phase):
        out = self.lookup_gap_phase(gap, phase, filename = str(self.lut))
        if not out: #sometime nothing is returned from external lookup table, then try again
            sleep(1)
            out = self.lookup_gap_phase(gap, phase, filename = str(self.lut))
        if not out:
            raise LookupError("energy and polarisation lookup from gap %f and phase %f failed to return any value" % (gap, phase))
        out = str(out) # convert unicode to string
        self.logger.debug("getEnergyPolarisation(%f, %f) returns %s" % (gap, phase, out))
        out = self.parseReturnedString(out)
        return out
    
    def getGapPhase(self, energy, polarisation):
        out = self.lookup_polar_energy(polarisation, energy, filename = str(self.lut))
        if not out: #sometime nothing is returned from external lookup table, then try again
            sleep(1)
            out = self.lookup_polar_energy(polarisation, energy, filename = str(self.lut))
        if not out:
            raise LookupError("gap and phase lookup from energy %f and polarisation %f failed to return any value" % (energy, polarisation))
        out = str(out)
        self.logger.debug("getGapPhase(%f, %f) returns %s" % (energy, polarisation, out))
        out = self.parseReturnedString(out)
        return out
    
    def stop(self):
        if self.lookup_polar_energy_created_in_scan_start:
            self.lookup_polar_energy.stop()
        if self.lookup_gap_phase_created_in_scan_start:
            self.lookup_gap_phase.stop()
        
idlam=IDLookup4LinearAngleMode("idlam", lut=lookup_file) 

endtime=time.time()
print "time taken for Initialisation: %s" % (endtime-starttime)

def main():
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
    gap1, phase1 = idlam.getGapPhase(820.092920, -80.034049)
    gap2, phase2 = idlam.getGapPhase(855, -80.034049)
    print "speed = ", (gap2 -gap1)/70
    print idlam.getGapPhase(820, -80)
    print idlam.getGapPhase(855, -80)
    