'''
Created on 21 Apr 2017

@author: fy65
'''

from i06shared.scannables.sourceModes import SourceMode
from i06shared.scannables.polarisation import Polarisation
from i06shared.scannables.energy import CombinedEnergy
from i06shared.scannables.linearArbitraryAngle import LinearArbitraryAngle
from i06shared.scannables.offsetHarmonic import HarmonicOffset
import __main__  # @UnresolvedImport
from i06shared import installation

if installation.isLive():
    __main__.smode=SourceMode('smode', defaultmode=SourceMode.SOURCE_MODES[0])
    __main__.offhar=HarmonicOffset('offhar', __main__.smode, __main__.iddpol, __main__.idupol,__main__.iddrpenergy,__main__.idurpenergy, __main__.pgmenergy, offhar=0.0)
    __main__.pol=Polarisation('pol', __main__.iddpol, __main__.iddrpenergy, __main__.iddgap, __main__.idupol, __main__.idurpenergy, __main__.idugap, __main__.pgmenergy, __main__.smode,__main__.offhar, detune=100.0, opengap=100.0,defaultPolarisation=Polarisation.POLARISATIONS[0])
    __main__.energy=CombinedEnergy('energy', __main__.iddgap, __main__.idugap, __main__.iddrpenergy, __main__.idurpenergy, __main__.pgmenergy, __main__.smode, __main__.pol,__main__.offhar, detune=100.0, opengap=100.0)
    __main__.laa=LinearArbitraryAngle('laa', __main__.iddlaangle, __main__.idulaangle, __main__.smode, __main__.pol)
    __main__.offhar.setPolScannable(__main__.pol)
else:
    print 80*"="
    print "IMPORTANT Warning:"
    print "    There are no 'smode', 'pol', 'energy', 'laa', 'offhar' and 'zacscan' scannables in DUMMY mode."
    print "    These scannables require EPICS soft motors, and zacscan to work"