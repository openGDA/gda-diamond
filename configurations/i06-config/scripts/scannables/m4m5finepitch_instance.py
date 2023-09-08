'''
define a compound scannable for m5 and m4 fine pitches motion
Created on 14 Jul 2023

@author: fy65
'''
from scannables.CompondScannable import CompoundScannable
from gdascripts.utils import caget
from scannables.m4m5finepitches import m4fpitch, m5fpitch
from scannables.VirtualScannable import VirtualScannable

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

    Xmum = input_targets[0][0]
    Ymum = input_targets[1][0]
    V5 = -1.0/920*( -Xmum*c + Ymum*s ) # motion of of M5fpitch in Volts
    V4 = -1.0/500*( Xmum*s + Ymum*c ) # motion of M4fpitch in Volts
    return [V5,V4]

def beam_motion_x(new_pos, x_current, y_current, s, c):
    V5 = 1.0/920.0*( new_pos*c -y_current*s ) # motion of of M5fpitch in Volts
    V4 = -1.0/500*( new_pos*s + y_current*c ) # motion of M4fpitch in Volts
    return V5, V4

def beam_motion_y(new_pos, x_current, y_current, s, c):
    V5 = 1.0/920.0*( x_current*c -new_pos*s ) # motion of of M5fpitch in Volts
    V4 = -1.0/500*( x_current*s + new_pos*c ) # motion of M4fpitch in Volts
    return V5, V4

m4m5fpitch = CompoundScannable("m4m5fpitch", calculate_target_for_scannables, m5fpitch, m4fpitch)

beam_x = VirtualScannable("beam_x", beam_motion_x, m5fpitch, m4fpitch)
beam_y = VirtualScannable("beam_y", beam_motion_y, m5fpitch, m4fpitch)
