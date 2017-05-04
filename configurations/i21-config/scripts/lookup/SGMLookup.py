'''
Created on 30 Aug 2016

@author: fy65
'''
from external import create_function
#from scisoftpy.external import create_function
import time

starttime=time.time()
#The lookupTable table
#lookup_file='/dls_sw/i21/software/gda/config/lookupTables/SVLS1-SGM.txt'
lookup_file='/dls_sw/i21/software/gda_versions/gda_master/config/lookupTables/SVLS1-SGM.txt'
#Lookup module
#local_module_path='/dls_sw/i21/software/gda/pythonscript/lookupTable'
local_module_path='/dls_sw/i21/software/gda_versions/gda_master/pythonscript/lookupTable'


# To solve the problem that PyDev/ Jython was passing JYTHONPATH as PYTHONPATH to the subprocess.
# The fix was to load all the environment variables, change the Python Path to the correct spot for Python 2.7 and pass it to Popen through the env argument.
python_path="/dls_sw/i21/software/miniconda2/envs/gdaenv/lib/python2.7/"
python_exe="/dls_sw/i21/software/miniconda2/envs/gdaenv/bin/python"

class sgmLookup():
    def __init__(self, name, lut=lookup_file, lookupindex=[0,1], returnindex=[2,3,4,5], numberOfHeaderLines=2):
        self.name=name
        #TODO need to check and fix external process exit on termination so it does not left external process on after GDA stopped.
        self.lookupBackward=create_function("reverseLookup",module="Lookup2Dto4D", exe=python_exe, path=[python_path], extra_path=[local_module_path], keep=True)
        self.lookupBackwardCreatedInScanStart=False
        self.lookupForward=create_function("forwardLookup", module="Lookup2Dto4D", exe=python_exe, path=[python_path], extra_path=[local_module_path], keep=True)
        self.lookupForwardCreatedInScanStart=False
        self.lut=lut
        self.numberOfHeaderLines=numberOfHeaderLines
        self.lookupIndex=lookupindex
        self.returnIndex=returnindex
    
    def getLR1HGamma(self, energy, alpha, delta=[5, 0.1], interpolationMethod='linear'):
        out=self.lookupForward(energy, alpha, filename=self.lut, delta=delta, lookupindex=self.lookupIndex, returnindex=self.returnIndex, numberOfHeaderLines=self.numberOfHeaderLines, interpolationMethod=interpolationMethod)
#         return out # used in scisoftpy
        #print out
        out= [float(x.strip()) for x in out.strip('\n').strip(']').strip('[').split(',') if x.strip() not in ('[',']','') ]
        return out
    
    def getEnergyAlpha(self, L,r1,H, gamma,delta=[200,400,100,10],interpolationMethod='linear'):
        out=self.lookupBackward(L,r1,H,gamma, filename=self.lut, delta=delta, lookupindex=self.returnIndex, returnindex=self.lookupIndex, numberOfHeaderLines=self.numberOfHeaderLines, interpolationMethod=interpolationMethod)
#         return out # used in scisoftpy
        #print out
        out= [float(x.strip()) for x in out.strip('\n').strip(']').strip('[').split(',') if x.strip() not in ('[',']','') ]
        return out
    
    def stop(self):
        if self.lookupBackwardCreatedInScanStart==True:
            self.lookupBackward.stop()
        if self.lookupForwardCreatedInScanStart==True:
            self.lookupForward.stop()
        
sgmlookup=sgmLookup("sgmlookup", lut=lookup_file, lookupindex=[0,1], returnindex=[2,3,4,5], numberOfHeaderLines=2) 

endtime=time.time()
print "time taken for Initialisation: %s" % (endtime-starttime)

def main():
    print
    for energy, alpha in [(280,87.9),(280,88.3),(450,88.4),(450,87.5),(530,87.4),(530,88.4),(640,87.4),(640,88.4),(710,87.4),(710,88.4),(780,87.4),(780,88.3),(930,87.4),(930,87.9)]:
        print energy,alpha
        starttime=time.time()
        print sgmlookup.getLR1HGamma(energy, alpha, delta=[5, 0.1], interpolationMethod='linear')
        endtime= time.time()
        print "time taken: %s" % (endtime-starttime)
        print
    
    print 
    
    for L, r1, H, gamma in [(1521.993,14515.828,2088.543,41.862),(1149.630,12999.271,1798.699,27.873),(1362.813,11356.905,1287.035,20.758),(2167.039,13772.085,1680.199,39.935),(2387.934,13393.806,1540.650,35.762),(1439.865,10852.700,1150.537,18.880),(2541.141,12675.878,1349.691,27.904),(1530.023,10314.715,1014.204,17.015),(2626.072,12310.252,1256.567,24.817),(1579.977,10038.796,947.775,16.111),(2703.054,11997.630,1178.969,22.547),(1731.515,10011.577,918.379,15.817),(2846.263,11460.696,1049.700,19.278),(2273.515,10406.070,919.032,16.211),(3045.554,10801.499,897.146,16.080)]:
        print L, r1, H, gamma
        starttime=time.time()
        print sgmlookup.getEnergyAlpha(L, r1, H, gamma, delta=[200,400,100,10],interpolationMethod='linear')
        endtime= time.time()
        print "time taken: %s" % (endtime-starttime)
        print
    
    print

if __name__=="__main__":
    main()