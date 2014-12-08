'''
Created on 7 Oct 2013

@author: fy65
'''
from functions.functionClassFor2Scannables import ScannableFunctionClassFor2Scannables


lastx1=0
lastx2=0

def derivative(x1, x2):
    '''returns the differential ratio of two scannables using adjacent points'''
    y=(x2-lastx2)/(x1-lastx1);
    lastx1 = x1
    lastx2 = x2
    return y;

dri20toi19 = ScannableFunctionClassFor2Scannables("dri20toi19", "hm3iamp20", "bfmiamp19", derivative);
