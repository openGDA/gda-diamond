'''
Created on May 17, 2022

@author: fy65
'''
import math as mh
from functions.unitTransferFunctions import energy2wavelength, dspacing

#################################
# K SCAN WITH FIXED H PROJECTION
#################################

def fixKscan2phi(qcut_val,q_cdw,phioffset):
    phival = mh.atan(qcut_val/q_cdw)*180/mh.pi + phioffset
    
    return phival

def fixKscan2th(energy_sa,qcut_val,q_cdw,phioffset,thoffset,tth,h_sa,k_sa,l_sa,a,b,c):

    lamda = energy2wavelength(energy_sa)
    
    Kph = (2*mh.pi/lamda)
    qtrans = Kph*2*mh.sin((tth/2)*mh.pi/180)
    
    phival = mh.atan(qcut_val/q_cdw)*180/mh.pi + phioffset
    
    delta_sa = mh.asin((q_cdw/mh.cos(phival*mh.pi/180)/qtrans)*2*mh.pi/dspacing(h_sa,k_sa,l_sa,a,b,c))*180/mh.pi
    thval = delta_sa + tth/2 + thoffset
    
    return thval


