import scisoftpy as numpy

from gda.factory import Finder
finder = Finder.getInstance()

ss1_rot = finder.find('ss1_rot')
ss1_x = finder.find('ss1_x')
ss1_z = finder.find('ss1_z')

def mvr_sampleX(value):
    _posTheta = ss1_rot()
    
    pos(ss1_z, -numpy.sin(_posTheta * numpy.pi /180) * value + ss1_z())
    pos(ss1_x, numpy.cos(_posTheta * numpy.pi /180) * value + ss1_x())
    
#def TXMvirtualX