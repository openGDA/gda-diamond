"""
Function launchRecon

GDA jython command to run the python script to perform sinogram generation ( if not using hdf) and quick reconstruction


e.g.
>import reconstruction
>reconstruction.launchRecon(inNXSFile="/dls/i13/data/2012/mt5849-2/4895.nxs", outDir="/dls/i13/data/2012/mt5849-2/processing",
localTomoFile="/dls_sw/i13/software/gda/config/scripts/reconstruction_localTomoFile.xml",
templateSettingsFile="/dls_sw/i12/software/gda_git/gda-tomography.git/uk.ac.diamond.tomography.reconstruction/resources/settings.xml")

inNXSFile - Single tomogram scan file path
outDir    - the same outDir as used by makeLinks
localTomoFile - beamline specific settings file
templateSettingsFile - settings file for Manchester reconstruction program
e.g. /dls_sw/i12/software/gda_git/gda-tomography.git/uk.ac.diamond.tomography.reconstruction/resources/settings.xml

"""

from gda.factory import Finder
from gdascripts.messages import handle_messages
from time import sleep
import math
import sys
import os
import subprocess
from gdascripts.configuration.properties.localProperties import LocalProperties

from gda.data import NumTracker
from gda.jython import InterfaceProvider
from gda.util import PropertyUtils


def launchRecon(inNXSFile, outDir, localTomoFile, templateSettingsFile):
    exe_sh = getPathToReconstructionShellScript()
    exe_py = getPathToReconstructionPythonScript()
    
    args = [exe_sh]
    args += [exe_py]
    #args += ["-h"]
    args += [ "-f", inNXSFile]
    args += [ "-o", outDir]
    args += [ "--local", localTomoFile]
    args += [ "--template", templateSettingsFile]
    args += [ "--sino"]
    args += [ "--recon"]
    args += [ "--quick"]
    print args
    try:
        proc = subprocess.Popen( args, executable = exe_sh, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
        proc.wait()
        (out, err) = proc.communicate()
        print "Return value after spawning reconstruction script was %s\n" % proc.returncode
        print "Reconstruction script's stout...\n", out
        print "Reconstruction script's sterr...\n", err
    except Exception, ex:
        msg = "Error spawning reconstruction script: " + str(ex)
        print msg
        #raise Exception(msg)

def getPathToTomographyReconstructionRoot():
    # eg, '/dls_sw/i12/software/gda_git/gda-tomography.git/uk.ac.diamond.tomography.reconstruction'
    git_dir = PropertyUtils.getExistingDirFromLocalProperties("gda.install.git.loc")
    trr_path = os.path.join(git_dir, 'gda-tomography.git')
    trr_path = os.path.join(trr_path, 'uk.ac.diamond.tomography.reconstruction')
    return trr_path

def getPathToReconstructionShellScript(scriptBasename='tomodo.sh'):
    # eg, "/dls_sw/i12/software/gda_git/gda-tomography.git/uk.ac.diamond.tomography.reconstruction/scripts/tomodo.sh"
    trr_path = getPathToTomographyReconstructionRoot()
    shscript_dir = os.path.join(trr_path, 'scripts')
    shscript_path = shscript_dir + os.sep + scriptBasename
    return shscript_path

def getPathToReconstructionPythonScript(scriptBasename='tomodo.py'):
    # eg, "/dls_sw/i12/software/gda_git/gda-tomography.git/uk.ac.diamond.tomography.reconstruction/scripts/tomodo.py"
    trr_path = getPathToTomographyReconstructionRoot()
    pyscript_dir = os.path.join(trr_path, 'scripts')
    pyscript_path = pyscript_dir + os.sep + scriptBasename
    return pyscript_path

