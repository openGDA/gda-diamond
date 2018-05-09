'''
Created on 9 May 2018

@author: fy65
'''
from scannable.idcontrols.sourceModes import SourceMode
from gdaserver import idd_gap, idu_gap
from scannable.idcontrols.polarisation import Polarisation

smode=SourceMode('smode',idu_gap, idd_gap, opengap=100, defaultmode=None)
pol=Polarisation('pol', smode, defaultPolarisation=None)