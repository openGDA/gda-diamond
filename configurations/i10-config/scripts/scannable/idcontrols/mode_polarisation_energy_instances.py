'''
Created on 9 May 2018

@author: fy65
'''
from scannable.idcontrols.sourceModes import SourceMode
from gdaserver import idd_gap, idu_gap
from scannable.idcontrols.polarisation import Polarisation

print
print "-"*100
print "Creating X-ray source control and polarisation control:"
print "    1. 'smode' - a scannable to set and get current X-ray source mode, i.e. which ID is used, it disables the ID not used;"
print "    2. 'pol'   - a scannable to set and get current polarisation of the X-ray beam. GDA value only which is not applied to hardware!"
smode=SourceMode('smode',idu_gap, idd_gap, opengap=100, defaultmode=None)
pol=Polarisation('pol', smode, defaultPolarisation=None); pol.verbose=True