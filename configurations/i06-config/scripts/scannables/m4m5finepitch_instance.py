'''
define a compound scannable for m5 and m4 fine pitches motion
Created on 14 Jul 2023

@author: fy65
'''
from scannables.CompondScannable import CompoundScannable
from gdascripts.utils import caget
from scannables.m4m5finepitches import m4fpitch, m5fpitch

def calculate_target_for_scannables(input_targets):
    import math
    from i06shared import installation
    if installation.isDummy():
        deg = -139.0
    if installation.isLive():
        deg = float(caget("BL06I-EA-LEEM-01:IMAGE:ROT:RBV"))
        
    rad = deg*math.pi/180.0
    s = math.sin(rad)
    c = math.cos(rad)
    
    Xmum = input_targets[0]
    Ymum = input_targets[1]
    V5 = -1.0/920*( -Xmum*c + Ymum*s ) # motion of of M5fpitch in Volts
    V4 = -1.0/500*( Xmum*s + Ymum*c ) # motion of M4fpitch in Volts
    return [V5,V4]

m4m5fpitch = CompoundScannable("m4m5fpitch", calculate_target_for_scannables, m5fpitch, m4fpitch)