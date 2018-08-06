'''
Created on 10 Jan 2018

@author: fy65
'''
from gdascripts.utils import frange
from dataCollection.MomentumTransfer import qtransferrlu2sapolar

def createPoistions(start, stop, step):
    ''' create a list of positions
    @param start: the start position
    @param stop: the end position
    @param step: the step size between adjacent positions
    @return: a list of positions
    '''
    q_positions=[]
    for each in frange(start, stop, step):
        q_positions.append(each)
    return q_positions

def calculateSapolarPositionsFromQPoistions(energy_sample, q_positions, sapolaroffset,thts,vec, a):
    ''' calculate correspnding sapolar values from a given list of q_positions
    @param energy_sample: sample energy
    @param q_positions: a list of q positions
    @param sapolaroffset: sapolar offset
    @param thts: spectrometer two theta
    @param vec:  1 for along (pi,0) direction; 2 for along (pi,pi) direction
    @param a: the lattice parameter
    @return a tuple containing values for sapolar 
    '''
    sapolarvals=[qtransferrlu2sapolar(energy_sample,qval,sapolaroffset,thts,vec,a) for qval in q_positions]
    return tuple(sapolarvals)
