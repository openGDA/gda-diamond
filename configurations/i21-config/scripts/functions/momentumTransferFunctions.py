'''
Created on 27th Mar 2019

@author: i21user
'''
##############################################################################################
###### Defining the momentum transfer at a fixed spectrometer tth angle ######################
#############################################################################################

from functions.unitTransferFunctions import energy2wavelength, dspacing

def th2qtrans_inplane(energy_sa,thval,thoffset,tth,h_sa,k_sa,l_sa,a,b,c):
    '''
    defining the projection of the momentum transfer along the in-plane direction of the sample
    '''
    import math as mh
    lamda = energy2wavelength(energy_sa)    
    
    Kph = (2*mh.pi/lamda)
    qtrans = Kph*2*mh.sin((tth/2)*mh.pi/180)
    delta_sa = (thval-thoffset) - tth/2
    qtrans_rlu_inplane = qtrans*mh.sin(delta_sa*mh.pi/180)*dspacing(h_sa,k_sa,l_sa,a,b,c)/(2*mh.pi)
    
    return qtrans_rlu_inplane

def th2qtrans_normal(energy_sa,thval,thoffset,tth,h_sa,k_sa,l_sa,a,b,c):
    '''
    defining the projection of the momentum transfer along the surface normal direction of the sample
    '''

    import math as mh
    lamda = energy2wavelength(energy_sa)    
    
    Kph = (2*mh.pi/lamda)
    qtrans = Kph*2*mh.sin((tth/2)*mh.pi/180)
    delta_sa = (thval-thoffset) - tth/2
    qtrans_rlu_normal = qtrans*mh.cos(delta_sa*mh.pi/180)*dspacing(h_sa,k_sa,l_sa,a,b,c)/(2*mh.pi)
    
    return qtrans_rlu_normal

def qtransinplane2th(energy_sa,qval_inplane,thoffset,tth,h_sa,k_sa,l_sa,a,b,c):
    '''defining the corresponded th angle for a given momentum transfer along the in-plane direction of the sample
    '''
    import math as mh
    lamda = energy2wavelength(energy_sa)
    
    Kph = (2*mh.pi/lamda)
    qtrans = Kph*2*mh.sin((tth/2)*mh.pi/180)
    
    delta_sa = mh.asin((qval_inplane/qtrans)*2*mh.pi/dspacing(h_sa,k_sa,l_sa,a,b,c))*180/mh.pi
    thval = delta_sa + tth/2 + thoffset
    
    return thval

def qtransnormal2th(energy_sa,qval_normal,thoffset,tth,h_sa,k_sa,l_sa):
    '''defining the corresponded th angle for a given momentum transfer along the surface normal direction of the sample
    '''
    import math as mh
    lamda = energy2wavelength(energy_sa)
    
    Kph = (2*mh.pi/lamda)
    qtrans = Kph*2*mh.sin((tth/2)*mh.pi/180)
    
    delta_sa = mh.acos((qval_normal/qtrans)*2*mh.pi/dspacing(h_sa,k_sa,l_sa))*180/mh.pi
    thval = delta_sa + tth/2 + thoffset
    
    return thval


def tthLscan(energy_sa,qval_inplane,qval_normal,h_sa,k_sa,a,b,c):

    import math as mh
    lamda = energy2wavelength(energy_sa)
    
    Kph = (2*mh.pi/lamda)
    tth_val = 2*mh.asin(qval_inplane*2*mh.pi/dspacing(h_sa,k_sa,0.,a,b,c)/mh.sin(mh.atan((qval_inplane/qval_normal)*dspacing(0.,0.,1.,a,b,c)/dspacing(h_sa,k_sa,0.,a,b,c)))/2/Kph)*180/mh.pi
    
    return tth_val

def thLscan(energy_sa,qval_inplane,qval_normal,thoffset,h_sa,k_sa,a,b,c):
    import math as mh
    th_val = tthLscan(energy_sa,qval_inplane,qval_normal,h_sa,k_sa,a,b,c)/2+mh.atan((qval_inplane/qval_normal)*dspacing(0.,0.,1.,a,b,c)/dspacing(h_sa,k_sa,0.,a,b,c))*180/mh.pi+thoffset
    
    return th_val
