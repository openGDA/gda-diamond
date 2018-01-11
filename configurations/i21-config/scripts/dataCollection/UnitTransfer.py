'''
Created on 10 Jan 2018

@author: fy65
'''
#Unit Transfer

import math

def energy2wavelength(E):
    ''' convert energy eV to wavelength angstrom
        @param E: is photon energy in the unit of eV
        @return: The wavelength of light is in the unit of 'angstrom'
    '''
    h_planck = 6.62607004e-34 #The Plank Constant is in the unit of 'J.s'
    c = 299792458 #Speed of light is in the unit of 'm/s'
    eV = 1.6021766208e-19 #One electron-voltage is in the unit of 'J'

    return h_planck*c/(E*eV)*(1.0e+10)

def wavelength2energy(lamda):
    ''' convert wavelength in angstrom to energy in eV
        @param lamda: The wavelength of light is in the unit of 'angstrom'
        @return: photon energy in the unit of eV
    '''
    h_planck = 6.62607004e-34 #The Plank Constant is in the unit of 'J.s'
    c = 299792458 #Speed of light is in the unit of 'm/s'
    eV = 1.6021766208e-19 #One electron-voltage is in the unit of 'J'

    return h_planck*c/(lamda*(1.0e-10)*eV)

def BrillouinLength(a):
    ''' calculate Brillouin length
        @param a: is the crystal parameter along one given direction in the unit of 'Angstrom'
        @return: the Brillouin length. The unit is the inverse of 'Angstrom'
    '''
    return 2*math.pi/a # The unit is the inverse of 'Angstrom'