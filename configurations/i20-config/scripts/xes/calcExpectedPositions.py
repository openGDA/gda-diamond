from gda.exafs.xes import XesUtils

from BeamlineParameters import JythonNameSpaceMapping
from xes import setOffsets

def calcFromLive():
    jython_mapper = JythonNameSpaceMapping()
    spectrometer = jython_mapper.spectrometer

    current_energy = jython_mapper.bragg1()
    
    # current radius, material, cut1/2/3
    current_material = jython_mapper.material()
    current_crystalCut0 = int(float(jython_mapper.cut1()))
    current_crystalCut1 = int(float(jython_mapper.cut2()))
    current_crystalCut2 = int(float(jython_mapper.cut3()))
    current_crystalCut = [current_crystalCut0,current_crystalCut1,current_crystalCut2]
    current_rowlandRadius = float(jython_mapper.radius())
    
    return calcFromValues(current_energy, current_material, current_crystalCut, current_rowlandRadius)

def calcFromValues(energy, material, crystalCut, rowlandRadius):

    xesmaterial = XesUtils.XesMaterial.GERMANIUM
    if material == 1:
        xesmaterial = XesUtils.XesMaterial.SILICON
        
    bragg = XesUtils.getBragg(energy,xesmaterial,crystalCut)
    
    analyserAngle = XesUtils.getCrystalRotation(bragg)
    
    det_x_expected = XesUtils.getDx(rowlandRadius,analyserAngle)
    det_y_expected = XesUtils.getDy(rowlandRadius,analyserAngle)
    xtal_x_expected = XesUtils.getL(rowlandRadius,bragg)
    
    # ax,az,tilt,rotation
    xtalPositions_minus1 = XesUtils.getAdditionalCrystalPositions(rowlandRadius,bragg,-137)
    xtalPositions_central = XesUtils.getAdditionalCrystalPositions(rowlandRadius,bragg,0)
    xtalPositions_plus1 = XesUtils.getAdditionalCrystalPositions(rowlandRadius,bragg,137)
    
    # todo
    expected_values = {'xtal_minus1_x' : xtalPositions_minus1[0],\
    'xtal_minus1_y' :  xtalPositions_minus1[1],\
    'xtal_minus1_rot' : xtalPositions_minus1[3],\
    'xtal_minus1_pitch' : xtalPositions_minus1[2],\
    'xtal_central_y' : xtalPositions_central[1],\
    'xtal_central_rot' : xtalPositions_central[3],\
    'xtal_central_pitch' : xtalPositions_central[2],\
    'xtal_plus1_x' : xtalPositions_plus1[0],\
    'xtal_plus1_y' : xtalPositions_plus1[1],\
    'xtal_plus1_rot' : xtalPositions_plus1[3],\
    'xtal_plus1_pitch' : xtalPositions_plus1[2],\
    'det_x': det_x_expected, \
    'det_y' : det_y_expected,\
    'det_rot' : analyserAngle,\
    'xtal_x' : xtal_x_expected,\
    'spec_rot' : analyserAngle }
    
    print expected_values
    
    #setOffsets.set(expected_values)
    
