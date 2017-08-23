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

__main__.smode=SourceMode('smode', defaultmode=SourceMode.SOURCE_MODES[0])
__main__.pol=Polarisation('pol', __main__.iddpol, __main__.iddgap, __main__.idupol, __main__.idugap, __main__.smode,detune=3.0, gap=100.0,defaultPolarisation=Polarisation.POLARISATIONS[0])
__main__.energy=CombinedEnergy('energy', __main__.denergy, __main__.uenergy, __main__.duenergy, __main__.iddgap, __main__.idugap, __main__.smode, __main__.pol, offhar=0.0, PositionTolerance=0.0001, defaultenergy=400.0)
__main__.laa=LinearArbitraryAngle('laa', __main__.iddlaangle, __main__.idulaangle, __main__.smode, __main__.pol)
__main__.haroff=HarmonicOffset('haroff', __main__.energy)