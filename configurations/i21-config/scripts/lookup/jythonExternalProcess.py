'''
This module provides functions to support ID lookupTable table for Linear Angular mode. It calls an external python process to perform the actual lookupTable which requires access to scipy and numpy libraries.
A special 'gdaenv' is created as a virtual environment to run this external process at /dls_sw/i21/software/miniconda2/envs/gdaenv/
Created on 25 Aug 2016

@author: fy65
'''
import subprocess
from subprocess import PIPE
import os
import time

#The lookupTable table
lookup_file='/dls_sw/i21/software/gda/config/lookupTables/LinearAngle.csv'
#Lookup module
lookup_module_dir='/dls_sw/i21/software/gda/pythonscript'

# To solve the problem that PyDev/ Jython was passing JYTHONPATH as PYTHONPATH to the subprocess.
# The fix was to load all the environment variables, change the Python Path to the correct spot for Python 2.7 and pass it to Popen through the env argument.
python_path="/dls_sw/i21/software/miniconda2/envs/gdaenv/lib/python2.7/"
my_env = os.environ
my_env["PYTHONPATH"] = python_path

def lookupGapPhase(gap, rowphase):
    stdoutdata, stderrdata=subprocess.Popen(["./lookup.py", "-f", lookup_file, "gaprowphase", str(gap), str(rowphase)], stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=lookup_module_dir, env=my_env).communicate()
    if stderrdata!='':
        print stderrdata
    return stdoutdata.strip('\n')

def lookupPolarisationEnergy(pol, energy):
    stdoutdata, stderrdata=subprocess.Popen(["./lookup.py", "-f", lookup_file, "polarisationenergy", str(pol), str(energy)], stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=lookup_module_dir, env=my_env).communicate()
    if stderrdata!='':
        print stderrdata
    return stdoutdata.strip('\n')

def test():
    start=time.time()
    print lookupGapPhase(25, 17)
    end=time.time()
    print "time taken for lookup 1st idgap and rowphase: %s" % (end-start)
    start=time.time()
    print lookupGapPhase(60, 20)
    end=time.time()
    print "time taken for lookup 2nd idgap and rowphase: %s" % (end-start)
    start=time.time()
    print lookupGapPhase(45, 10)
    end=time.time()
    print "time taken for lookup 3rd idgap and rowphase: %s" % (end-start)
    
    print
    
    start=time.time()
    print lookupPolarisationEnergy(-50, 1000)
    end=time.time()
    print "time taken for lookup first polarisation and energy: %s" % (end-start)
    start=time.time()
    print lookupPolarisationEnergy(-30, 800)
    end=time.time()
    print "time taken for lookup 2nd polarisation and energy: %s" % (end-start)
    start=time.time()
    print lookupPolarisationEnergy(-15, 450)
    end=time.time()
    print "time taken for lookup 3rd polarisation and energy: %s" % (end-start)

if __name__ == "__main__":
    test()