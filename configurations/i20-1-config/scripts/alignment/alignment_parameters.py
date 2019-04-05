#
# Using the supplied bean which contains the required options, calculates 
# the parameters required to align the beamline and returns the same bean
# to the main namespace.
#

import math

from gda.util.exafs import AbsorptionEdge
from uk.ac.gda.exafs.data import AlignmentParametersBean
from gda.factory import Finder

def calc_parameters(parametersBean):
    
    parametersBean = _setFixedValues(parametersBean) # wiggler at the moment
    
    parametersBean = _chooseStripes(parametersBean)
    
    parametersBean = _choosePitchAndAttenuators(parametersBean)
    
    parametersBean = _calcBragg(parametersBean) # also set twotheta
    
    parametersBean = _calcBenders(parametersBean) # must be done after bragg
    
    parametersBean = _calcPrimarySlits(parametersBean)
    
    parametersBean = _calDetDistance(parametersBean)
    
    parametersBean = _calcEnergyBandwidth(parametersBean)
    
    parametersBean = _calcReadbackEnergyBandwidth(parametersBean)

    parametersBean = _calcPower(parametersBean)

    return parametersBean

def _calcEnergy(parametersBean):
    # for the moment, simply use the edge energy
    return parametersBean.getEdge().getEnergy()

def _setFixedValues(parametersBean):
    
    parametersBean.setWigglerGap(18.5)
#    parametersBean.setPolyBend1(5)
#    parametersBean.setPolyBend2(5)
    return parametersBean
    
def _chooseStripes(parametersBean):
    
    energy = _calcEnergy(parametersBean)
    
    if energy > 20300:
        parametersBean.setMe1stripe(AlignmentParametersBean.ME1Stripe[1])
    else :
        parametersBean.setMe1stripe(AlignmentParametersBean.ME1Stripe[0])
        
    if energy < 9600:
        parametersBean.setMe2stripe(AlignmentParametersBean.ME2Stripe[0])
    elif energy >= 9600 and energy < 20300:
        parametersBean.setMe2stripe(AlignmentParametersBean.ME2Stripe[1])
    else:
        parametersBean.setMe2stripe(AlignmentParametersBean.ME2Stripe[2])
        
    return parametersBean

def _choosePitchAndAttenuators(parametersBean):
    
    energy = _calcEnergy(parametersBean)
    
    if parametersBean.getCrystalCut() == "Si111":
        if energy < 7000:
            parametersBean.setMe2Pitch(4)
            parametersBean.setAtn1(AlignmentParametersBean.ATN1[0])
            parametersBean.setAtn2(AlignmentParametersBean.ATN2[0])
            parametersBean.setAtn3(AlignmentParametersBean.ATN3[0])
        elif energy >= 7000 and energy < 8000:
            parametersBean.setMe2Pitch(3.5)
            parametersBean.setAtn1(AlignmentParametersBean.ATN1[1])
            parametersBean.setAtn2(AlignmentParametersBean.ATN2[0])
            parametersBean.setAtn3(AlignmentParametersBean.ATN3[0])
        elif energy >= 800 and energy < 9600:
            parametersBean.setMe2Pitch(3)
            parametersBean.setAtn1(AlignmentParametersBean.ATN1[2])
            parametersBean.setAtn2(AlignmentParametersBean.ATN2[0])
            parametersBean.setAtn3(AlignmentParametersBean.ATN3[0])
        elif energy >= 9600 and energy < 12200:
            parametersBean.setMe2Pitch(5)
            parametersBean.setAtn1(AlignmentParametersBean.ATN1[4])
            parametersBean.setAtn2(AlignmentParametersBean.ATN2[0])
            parametersBean.setAtn3(AlignmentParametersBean.ATN3[0])
        elif energy >= 12200:
            parametersBean.setMe2Pitch(4)
            parametersBean.setAtn1(AlignmentParametersBean.ATN1[4])
            parametersBean.setAtn2(AlignmentParametersBean.ATN2[0])
            parametersBean.setAtn3(AlignmentParametersBean.ATN3[0])
        
    else:  # Si311
        if energy < 8000:
            parametersBean.setMe2Pitch(3.5)
            parametersBean.setAtn1(AlignmentParametersBean.ATN1[1])
            parametersBean.setAtn2(AlignmentParametersBean.ATN2[0])
            parametersBean.setAtn3(AlignmentParametersBean.ATN3[0])
        elif energy >= 8000 and energy < 9600:
            parametersBean.setMe2Pitch(3)
            parametersBean.setAtn1(AlignmentParametersBean.ATN1[1])
            parametersBean.setAtn2(AlignmentParametersBean.ATN2[0])
            parametersBean.setAtn3(AlignmentParametersBean.ATN3[0])
        elif energy >= 9600 and energy < 12200:
            parametersBean.setMe2Pitch(5)
            parametersBean.setAtn1(AlignmentParametersBean.ATN1[4])
            parametersBean.setAtn2(AlignmentParametersBean.ATN2[0])
            parametersBean.setAtn3(AlignmentParametersBean.ATN3[0])
        elif energy >= 12200 and energy < 13500:
            parametersBean.setMe2Pitch(4.5)
            parametersBean.setAtn1(AlignmentParametersBean.ATN1[0])
            parametersBean.setAtn2(AlignmentParametersBean.ATN2[2])
            parametersBean.setAtn3(AlignmentParametersBean.ATN3[0])
        elif energy >= 13500 and energy < 15200:
            parametersBean.setMe2Pitch(4)
            parametersBean.setAtn1(AlignmentParametersBean.ATN1[4])
            parametersBean.setAtn2(AlignmentParametersBean.ATN2[2])
            parametersBean.setAtn3(AlignmentParametersBean.ATN3[0])
        elif energy >= 15200 and energy < 17400:
            parametersBean.setMe2Pitch(3.5)
            parametersBean.setAtn1(AlignmentParametersBean.ATN1[3])
            parametersBean.setAtn2(AlignmentParametersBean.ATN2[2])
            parametersBean.setAtn3(AlignmentParametersBean.ATN3[1])
        elif energy >= 17400 and energy < 20300:
            parametersBean.setMe2Pitch(3)
            parametersBean.setAtn1(AlignmentParametersBean.ATN1[0])
            parametersBean.setAtn2(AlignmentParametersBean.ATN2[4])
            parametersBean.setAtn3(AlignmentParametersBean.ATN3[1])
        elif energy > 20300:
            parametersBean.setMe2Pitch(-1) # means move it out of beam
            parametersBean.setAtn1(AlignmentParametersBean.ATN1[0])
            parametersBean.setAtn2(AlignmentParametersBean.ATN2[5])
            parametersBean.setAtn3(AlignmentParametersBean.ATN3[1])
    
    return parametersBean

def _getLatticeConstant(parametersBean):
    
    if parametersBean.getCrystalCut() == "Si111":
        return 3.1357017
    else:
        return 1.6375668  # Si 311
    
def _calcBragg(parametersBean):
    
    energy = _calcEnergy(parametersBean)
    
    lattice_constant = _getLatticeConstant(parametersBean)
    
    bragg_radians  = math.asin(6199.0 / (energy * lattice_constant) )
    
    bragg_degrees = math.degrees(bragg_radians)
    
    parametersBean.setBraggAngle(bragg_degrees)
    
    parametersBean.setArm2Theta(bragg_degrees * 2)
    
    return parametersBean

def _calcBenders(parametersBean):
    
    bragg = parametersBean.getBraggAngle() # degrees
    sineBragg = math.sin(math.radians(bragg))
    
    q = parametersBean.getQ() # set in UI
    if q == None:
        raise RuntimeError("Q value not set, so cannot calculate bender values")
    
    offset1 = -0.31833 # mm, fixed at the moment
    offset2 =  0.90130 # mm, fixed at the moment
    
    if q == 0.8 :
        bend1 = offset1 + (11.55945 * sineBragg)
        bend2 = offset2 + (10.65425 * sineBragg)
        parametersBean.setPolyBend1(bend1)
        parametersBean.setPolyBend2(bend2)
        return parametersBean
    
    elif q == 1.0 :
        bend1 = offset1 + ( 9.2847 * sineBragg)
        bend2 = offset2 + ( 8.55763* sineBragg)
        parametersBean.setPolyBend1(bend1)
        parametersBean.setPolyBend2(bend2)
        return parametersBean
    
    elif q == 1.2 :
        bend1 = offset1 + ( 7.77129 * sineBragg)
        bend2 = offset2 + ( 7.16274 * sineBragg)
        parametersBean.setPolyBend1(bend1)
        parametersBean.setPolyBend2(bend2)
        return parametersBean
    
    raise ValueError("Q value not valid!. Must be 0.8, 1.0 or 1.2")
    
def _calcPrimarySlits(parametersBean):
    
    poly_length = 250.0 # mm
    
    dist_poly_to_source = 45100 # 45.1m
    
    bragg_radians = math.radians(parametersBean.getBraggAngle())
    
    alpha_rad = (poly_length/dist_poly_to_source) * math.sin(bragg_radians)
    
    alpha_mrad = alpha_rad * 1000
    
    if alpha_mrad > 1.6: # If calculated size is > 1.6mrand then fixed to 1.6mrand
        parametersBean.setPrimarySlitGap(1.6)
    else:
        parametersBean.setPrimarySlitGap(alpha_mrad)
    
    return parametersBean

def _calDetDistance(parametersBean):
    
    alpha_mrad = parametersBean.getPrimarySlitGap()
    
    dist_poly_to_source = 45.1
    
    q_m = parametersBean.getQ()
    
    s_mm = _getDetectorSizeInMM(parametersBean)
    
    det_dist_m = (s_mm * q_m) / (alpha_mrad * dist_poly_to_source)
    
    parametersBean.setDetectorDistance(det_dist_m)
    
    # TODO beam is going upwards at an angle of 6mrad, so based on
    # detector z values, their height needs to be calculated 
    offset = 0.0
    det_height_mm = offset - (6 * (q_m + _getRealDetDistanceInM()))
    me2_y_positioner = Finder.getInstance().find("me2_y_positioner")
    if me2_y_positioner.getPosition() == "In" :
        det_height_mm = det_height_mm + 3.0
    parametersBean.setDetectorHeight(det_height_mm)
    return parametersBean
    
def _calcEnergyBandwidth(parametersBean):

    calc_det_z = parametersBean.getDetectorDistance()
    deltaE = _calcBandwidth(parametersBean,calc_det_z)
    parametersBean.setEnergyBandwidth(deltaE)
    
    return parametersBean

def _calcReadbackEnergyBandwidth(parametersBean):
    
    real_det_z = _getRealDetDistanceInM()
    calc_det_z = parametersBean.getDetectorDistance()
    if real_det_z > calc_det_z:
        deltaE = _calcBandwidth(parametersBean,real_det_z)
    else:
        deltaE = _calcBandwidth(parametersBean,calc_det_z)
    parametersBean.setReadBackEnergyBandwidth(deltaE)
    
    return parametersBean

def _calcBandwidth(parametersBean,det_z_m):

    energy = _calcEnergy(parametersBean)
    s_mm = _getDetectorSizeInMM(parametersBean)
    omega = float(parametersBean.getBraggAngle())
    cot_omega = float(1.0 / math.tan(math.radians(omega)))
    p_m = 45.1
    q_m = parametersBean.getQ()
    
    deltaE = 0.0
    try:
        deltaE = energy * cot_omega * (s_mm/det_z_m) * (((p_m-q_m)/(2*p_m)) / 1000.)
    except:
        deltaE = 0.0
    
    return deltaE

def _calcPower(parametersBean):
    
    # TODO!
    parametersBean.setPower(0.0)
    return parametersBean
    
def _getRealDetDistanceInM():
    
    det_z = Finder.getInstance().find("det_z")
    return det_z.getPosition() / 1000.

def _getDetectorSizeInMM(parametersBean):
    s_mm = 51.20 # XH
    
    if parametersBean.getDetector() == "xstrip":
        s_mm = 25.60
    return s_mm

