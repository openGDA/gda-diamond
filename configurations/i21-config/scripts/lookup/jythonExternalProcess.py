'''
This module provides functions to support ID lookup table for Linear Angular mode. It calls an external python process to perform the actual lookup which requires access to scipy and numpy libraries.
A special 'gdaenv' is created as a virtual environment to run this external process at /dls_sw/i21/software/miniconda2/envs/gdaenv/
Created on 25 Aug 2016

@author: fy65
'''
import subprocess
from subprocess import PIPE
import os

# To solve the problem that PyDev/ Jython was passing JYTHONPATH as PYTHONPATH to the subprocess.
# The fix was to load all the environment variables, change the Python Path to the correct spot for Python 2.7 and pass it to Popen through the env argument.
python_path="/dls_sw/i21/software/miniconda2/envs/gdaenv/lib/python2.7/"
my_env = os.environ
my_env["PYTHONPATH"] = python_path

def lookupGapPhase(gap, rowphase):
    stdoutdata, stderrdata=subprocess.Popen(["./lookup.py", "gaprowphase", str(gap), str(rowphase)], stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd='/dls_sw/i21/software/gda/workspace/i21-python/src/lookup', env=my_env).communicate()
    if stderrdata!='':
        print stderrdata
    return stdoutdata.strip('\n')

def lookupPolarisationEnergy(pol, energy):
    stdoutdata, stderrdata=subprocess.Popen(["./lookup.py", "polarisationenergy", str(pol), str(energy)], stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd='/dls_sw/i21/software/gda/workspace/i21-python/src/lookup', env=my_env).communicate()
    if stderrdata!='':
        print stderrdata
    return stdoutdata.strip('\n')

print lookupGapPhase(25, 17)
print lookupPolarisationEnergy(-50, 1000)