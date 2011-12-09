from gda.exafs.xes import XesUtils

from BeamlineParameters import JythonNameSpaceMapping
from xes import setOffsets


def recordFromLive(fluo_energy):
    """
    Using the given fluorescence energy, assumes that the spectrometer is aligned to that 
    energy, so sets the offsets of all the motors and records the values in the default 
    xml store.
    
    Next time the GDA starts those offsets will continue to be used.
    """
    applyFromLive(fluo_energy,True)

def applyFromLive(fluo_energy,store=False):
    """
    Using the given fluorescence energy, assumes that the spectrometer is aligned to that 
    energy, so sets the offsets of all the motors.
    
    The offsets are only recorded in the xml file if store is set to True.
    """
    expectedValuesDict = calcFromLive(fluo_energy)
    
    print expectedValuesDict
    
    setOffsets.setFromExpectedValues(expectedValuesDict, False)


def calcFromLive(fluo_energy):
    """
    Using the given fluorescence energy, assumes that the spectrometer is aligned to that 
    energy, so calculates the expected motor positions.
    
    Returns a dictionary of spectrometer scannables and expected positions.
    """
    jython_mapper = JythonNameSpaceMapping()
    
    # current radius, material, cut1/2/3
    current_material = jython_mapper.material()
    current_crystalCut0 = int(float(jython_mapper.cut1()))
    current_crystalCut1 = int(float(jython_mapper.cut2()))
    current_crystalCut2 = int(float(jython_mapper.cut3()))
    current_crystalCut = [current_crystalCut0,current_crystalCut1,current_crystalCut2]
    current_rowlandRadius = float(jython_mapper.radius())
    
    return calcFromValues(fluo_energy, current_material, current_crystalCut, current_rowlandRadius)

def calcFromValues(fluo_energy, material, crystalCut, rowlandRadius):
    """
    Using the given fluorescence energy and crystal parameters, assumes that the spectrometer
    is aligned to that energy, so calculates the expected motor positions.
    
    Returns a dictionary of spectrometer scannables and expected positions.
    """
    xesmaterial = XesUtils.XesMaterial.GERMANIUM
    if material == 'Si':
        xesmaterial = XesUtils.XesMaterial.SILICON
        
    bragg = XesUtils.getBragg(fluo_energy,xesmaterial,crystalCut)
    
    
    # FIXME! XesUtils is returning values the wrong way round!
    det_x_expected = XesUtils.getDx(rowlandRadius,bragg)
    det_y_expected = XesUtils.getDy(rowlandRadius,bragg)
    xtal_x_expected = XesUtils.getL(rowlandRadius,bragg)
    
    # ax,az,tilt,rotation
    xtalPositions_minus1 = XesUtils.getAdditionalCrystalPositions(rowlandRadius,bragg,-137)
    xtalPositions_central = XesUtils.getAdditionalCrystalPositions(rowlandRadius,bragg,0)
    xtalPositions_plus1 = XesUtils.getAdditionalCrystalPositions(rowlandRadius,bragg,137)

    analyserAngle = XesUtils.getCrystalRotation(bragg)

    expected_values = {'xtal_minus1_x' : xtalPositions_minus1[0],\
    'xtal_minus1_y' :  xtalPositions_minus1[1],\
    'xtal_minus1_rot' : xtalPositions_minus1[2],\
    'xtal_minus1_pitch' : xtalPositions_minus1[3],\
    'xtal_central_y' : xtalPositions_central[1],\
    'xtal_central_rot' : xtalPositions_central[2],\
    'xtal_central_pitch' : xtalPositions_central[3],\
    'xtal_plus1_x' : xtalPositions_plus1[0],\
    'xtal_plus1_y' : xtalPositions_plus1[1],\
    'xtal_plus1_rot' : xtalPositions_plus1[2],\
    'xtal_plus1_pitch' : xtalPositions_plus1[3],\
    'det_x': det_x_expected, \
    'det_y' : det_y_expected,\
    'det_rot' : analyserAngle,\
    'xtal_x' : xtal_x_expected}
    
    return expected_values
    
