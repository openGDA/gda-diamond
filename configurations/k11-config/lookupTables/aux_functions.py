"""
Created on Tue Nov  3 13:20:16 2020

@author: xgn26134
"""

# Hans: better give these functions distinct names!

#******************************************************************************
# beam selector positioner
def beam_selector_monoDiff_pos(eneregy):
    return 'Diffraction beam' # 45
    
def beam_selector_monoImg_pos(eneregy):
    return 'Mono imaging beam' # 225

def beam_selector_noBeam_pos(eneregy):
    return 'No beam' # 135
  
def beam_selector_allBeams_pos(energy):
    return 'All beams through'

def beam_selector_pinkImg_pos(energy):
    return 'Pink imaging beam'


#******************************************************************************
# filter positioner
def a3_filter_position(energy):
    if energy >=7 and energy < 14:
        return 'Al 2 mm'
    elif energy >= 14  and energy < 28:
        return 'Al 4 mm'
    elif energy >= 28 and energy <= 38:
        return 'Al 4 mm'
    else:
        print "energy outside valid range"

def a3_filter_to_empty(energy):
    return 'empty aperture'

 
'''
def a3_filter_0p1mmAl_position(energy):
    return 'Al 0.1 mm'

def a3_filter_0p5mmAl_position(energy):
    return 'Al 0.5 mm'

def a3_filter_1p0mmAl_position(energy):
    return 'Al 1 mm'

def a3_filter_2p0mmAl_position(energy):
    

def a3_filter_4p0mmAl_position(energy):
''' 