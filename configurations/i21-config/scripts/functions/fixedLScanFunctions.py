'''
Created on May 17, 2022

@author: fy65
'''
import math as mh
from functions.unitTransferFunctions import energy2wavelength, dspacing

#################################
# FIXED L SCAN
#################################

def tthLscan(energy_sa,qval_normal,h_sa,k_sa,l_sa,a,b,c):

    lamda = energy2wavelength(energy_sa)
    
    Kph = (2*mh.pi/lamda)
    tth_val = 2*mh.asin(qval_normal*mh.pi/dspacing(h_sa,k_sa,l_sa,a,b,c)/Kph)*180/mh.pi
    
    return tth_val

def thLscan(energy_sa,qval_normal,thoffset,h_sa,k_sa,l_sa,a,b,c):

    th_val = tthLscan(energy_sa,qval_normal,h_sa,k_sa,l_sa,a,b,c)/2+thoffset
    
    return th_val
