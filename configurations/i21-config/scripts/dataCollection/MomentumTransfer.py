'''
defining the momentum transfer at a fixed spectrometer thts angle 
 vec = 1 for along (pi,0) direction
 vec = 2 for along (pi,pi) direction
Created on 10 Jan 2018

@author: fy65
'''

from dataCollection.UnitTransfer import energy2wavelength
import math

def qtransferrlupara(energy_sample,sapolarval,sapolaroffset,thts,vec, a):
    ''' calculate qtransfer_rlu_para
    @param energy_sample: sample energy
    @param sapolarval: sapolar value
    @param sapolaroffset: sapolar offset
    @param thts: spectrometer two theta
    @param vec:  1 for along (pi,0) direction; 2 for along (pi,pi) direction
    @param a: the lattice parameter 
    '''

    qtransfer_rlu = qtransfer_rlu(energy_sample, thts, vec, a)
    
    # defining the projection of the momentum transfer 
    delta_sample = (sapolarval-sapolaroffset) - thts/2
    qtransfer_rlu_para = qtransfer_rlu*math.sin(delta_sample*math.pi/180)
    
    return qtransfer_rlu_para


def qtransfer_rlu(energy_sample, thts, vec, a):
    ''' calculate qtransfer_rlu
    @param energy_sample: sample energy
    @param thts: spectrometer two theta
    @param vec:  1 for along (pi,0) direction; 2 for along (pi,pi) direction
    @param a: the lattice parameter 
    '''
    lamda = energy2wavelength(energy_sample)
    qtransfer = (2 * math.pi / lamda) * 2 * math.sin((thts / 2) * math.pi / 180)
    qtransfer_rlu = qtransfer * a / (2 * math.pi * math.sqrt(vec))
    return qtransfer_rlu


def qtransferrlu2sapolar(energy_sample,qtransferrlupara,sapolaroffset,thts,vec, a):
    ''' calculate sapolar value
    @param energy_sample: sample energy
    @param qtransferrlupara: qtransfer_rlu_para
    @param sapolaroffset: sapolar offset
    @param thts: spectrometer two theta
    @param vec:  1 for along (pi,0) direction; 2 for along (pi,pi) direction
    @param a: the lattice parameter 
    '''

    qtransfer_rlu = qtransfer_rlu(energy_sample, thts, vec, a)
    
    delta_sample = math.asin(qtransferrlupara/qtransfer_rlu)*180/math.pi
    sapolarval = delta_sample + thts/2 + sapolaroffset
    
    return sapolarval

