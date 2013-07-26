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
    
    parametersBean = _setFixedValues(parametersBean) # wiggler and benders at the moment
    
    parametersBean = _chooseStripes(parametersBean)
    
    parametersBean = _choosePitchAndAttenuators(parametersBean)
    
    parametersBean = _calcBragg(parametersBean) # also set twotheta
    
    parametersBean = _calcPrimarySlits(parametersBean)
    
    parametersBean = _calDetDistance(parametersBean)
    
    parametersBean = _calcEnergyBandwidth(parametersBean)
    
    parametersBean = _calcPower(parametersBean)

    return parametersBean

def _calcEnergy(parametersBean):
    # for the moment, simply use the edge energy
    return parametersBean.getEdge().getEnergy()

def _setFixedValues(parametersBean):
    
    parametersBean.setWigglerGap(18.5)
    parametersBean.setPolyBend1(5)
    parametersBean.setPolyBend2(5)
    return parametersBean
    
def _chooseStripes(parametersBean):
    
    energy = _calcEnergy(parametersBean)
    
    if energy > 20300:
        parametersBean.setMe1stripe(AlignmentParametersBean.ME1Stripe[0])
    else :
        parametersBean.setMe1stripe(AlignmentParametersBean.ME1Stripe[1])
        
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

def _calcPrimarySlits(parametersBean):
    
    poly_length = 250.0 # mm
    
    dist_poly_to_source = 45100 # 45.1m
    
    bragg_radians = math.radians(parametersBean.getBraggAngle())
    
    alpha_rad = (poly_length/dist_poly_to_source) * math.sin(bragg_radians)
    
    alpha_mrad = alpha_rad * 1000
    
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
    parametersBean.setDetectorHeight(0.0)

    return parametersBean
    
def _calcEnergyBandwidth(parametersBean):
    
    real_det_z = _getRealDetDistanceInM()
    calc_det_z = parametersBean.getDetectorDistance()
    energy = _calcEnergy(parametersBean)
    s_mm = _getDetectorSizeInMM(parametersBean)
    omega = parametersBean.getBraggAngle()
    cot_omega = 1.0 / math.tan(math.radians(omega))
    p_m = 45.1
    q_m = parametersBean.getQ()
    alpha_mrad = parametersBean.getPrimarySlitGap()
    
    deltaE = 0.0
    if real_det_z > calc_det_z:
        deltaE = energy * cot_omega * (s_mm/real_det_z) * (((p_m-q_m)/(2*p_m)) / 1000.)
    else :
        deltaE = energy * cot_omega * alpha_mrad * (((p_m-q_m)/(2*q_m)) / 1000.)
    parametersBean.setEnergyBandwidth(deltaE)
    
    return parametersBean

def _calcPower(parametersBean):
    
    # TODO!
    parametersBean.setPower(0.0)
    return parametersBean
    
def _getRealDetDistanceInM():
    
    det_z = Finder.getInstance().find("detector_z")
    return det_z.getPosition() / 1000.

def _getDetectorSizeInMM(parametersBean):
    s_mm = 51.20 # XH
    
    if parametersBean.getDetector() == "XSTRIP":
        s_mm = 25.60
    return s_mm

