from gda.exafs.xes import XesUtils

def calcFromLive():
    jython_mapper = JythonNameSpaceMapping()
    spectrometer = jython_mapper.spectrometer

    # get energy
    
    # current radius, material, cut1/2/3
    
    return calcFromValues(energy, material, crystalCut, rowlandRadius)

def calcFromValues(energy, material, crystalCut, rowlandRadius):

    xesmaterial = XesUtils.XesMaterial.GERMANIUM
    if str(material).lower().startsWith('s'):
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
    'xtal_central_y' : xtal_central_y_expected,\
    'xtal_central_rot' : xtal_central_rot_expected,\
    'xtal_central_pitch' : xtal_central_pitch_expected,\
    'xtal_plus1_x' : xtalPositions_plus1[0],\
    'xtal_plus1_y' : xtalPositions_plus1[1],\
    'xtal_plus1_rot' : xtalPositions_plus1p[3],\
    'xtal_plus1_pitch' : xtalPositions_plus1[2],\
    'det_x': det_x_expected, \
    'det_y' : det_y_expected,\
    'det_rot' : det_rot_expected,\
    'xtal_x' : xtal_x_expected,\
    'spec_rot' : analyserAngle }
    