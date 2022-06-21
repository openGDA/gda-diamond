'''
Created on 27th Mar 2019

@author: i21user
'''

#############################################################################################
######  Unit Transfer ### FUNCTIONS
##############################################################################################
def energy2wavelength(E):
    '''convert energy in eV to wavelength in angstrom
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
    '''
    @param a: is the crystal parameter along one given direction in the unit of 'Angstrom'
    @return: Brillouin Length, unit is the inverse of 'Angstrom'
    '''
    import math as mh
    return 2*mh.pi/a # The unit is the inverse of 'Angstrom'

def dspacing(h,k,l,a,b,c):
    ''' this function requires the crystal lattice parameters in the unit of 'Angstrom' a, b,c 
    @param h, k, l: are the Miller indices
    @return d-space
    '''
    import math as mh

    # a, b, c are the crystal lattice parameters in the unit of 'Angstrom'
    return 1/mh.sqrt((h/a)**2+(k/b)**2+(l/c)**2)