"""
Created on Mon Oct 26 11:21:49 2020

@author: xgn26134
"""

def m1_y_in(energy):
    '''check current y position of mirror. If within range, dont move, if not, move...'''
    # define the ranges for the energies
    Pt_y_pos_allowed = [7.0,15.0]
    Pt_y_pos_nominal = 11
    Si_y_pos_allowed = [-4,4]
    Si_y_pos_nominal = 0
    Cr_y_pos_allowed = [-15,-7]
    Cr_y_pos_nominal = -11
    
    # Douglas put this here to make the function work. Fix it!!!
    m1_y_pos_nominal = 11
    
    # get current mosition
    m1_y_pos_current = m1_y.getPosition()
    # check which strip we need
    if energy >= 7 and energy <= 38: # for now we only use Pt strip
        # check y position of mirror, move if  needed
        if m1_y_pos_current < Pt_y_pos_allowed[0] or m1_y_pos_current > Pt_y_pos_allowed[1]:
            return Pt_y_pos_nominal
        else:
            return m1_y_pos_current
    else:
        raise DeviceException("Energy of %f outside permitted range of [7,38] keV" % energy)

def m2_y_in(energy):
    '''check current y position of mirror. If within range, dont move, if not, move...'''
    # define the ranges for the energies
    Pt_y_pos_allowed = [7.0,15.0]	
    Pt_y_pos_nominal = 11
    Si_y_pos_allowed = [-4,4]
    Si_y_pos_nominal = 0
    Cr_y_pos_allowed = [-15,-7]
    Cr_y_pos_nominal = -11
    
    # Douglas put this here to make the function work. Fix it!!!
    m2_y_pos_nominal = 11
    
    # get current mosition
    m2_y_pos_current = m2_y.getPosition()
    # check which strip we need
    if energy >= 7 and energy <= 38: # for now we only use Pt strip
        # check y position of mirror, move if  needed
        if m2_y_pos_current < Pt_y_pos_allowed[0] or m2_y_pos_current > Pt_y_pos_allowed[1]:
            return Pt_y_pos_nominal
        else:
            return m2_y_pos_current
    else:
        raise DeviceException("Energy of %f outside permitted range of [7,38] keV" % energy)



def m2_bender_current_position_check(energy):
    '''checks the current m2 bender position against the nominal position. If 
    either bender is out by more than 10 counts, it returns True, else False'''
    m2_nominal_bender_position = [176365,231365] # where benders should be
    m2_bender_tolerance = 10 # in encoder counts
    m2_current_bendus_position = m2_bendus.getPosition() # where benders are
    m2_current_bendds_position = m2_bendds.getPosition()
    # compare current and nominal positions, return True if outside tolerance
    if abs(m2_current_bendus_position-m2_nominal_bender_position[0]) > m2_bender_tolerance or abs(m2_current_bendds_position-m2_nominal_bender_position[1]) > m2_bender_tolerance:
        m2_bender_move_monoDiff()
        return 0
    else:
        return 0


def m2_bender_move_monoDiff():
    # move to center
    m2_bendus.asynchronousMoveTo(180000)
    m2_bendds.asynchronousMoveTo(235000)
    m2_bendus.waitWhileBusy()
    m2_bendds.waitWhileBusy()
    # move to position
    m2_bendus.asynchronousMoveTo(176365)
    m2_bendds.asynchronousMoveTo(231365)
    m2_bendus.waitWhileBusy()
    m2_bendds.waitWhileBusy()

    