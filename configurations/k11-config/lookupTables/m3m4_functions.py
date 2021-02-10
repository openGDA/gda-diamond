"""
Created on Mon Oct 26 11:21:49 2020

@author: xgn26134
"""

def m3_y_in(energy):
    '''check current y position of mirror. If within range, dont move, if not, move...'''
    # define the ranges for the energies
    Pt_y_pos_allowed = [7.0,15.0]
    Pt_y_pos_nominal = 11
    Si_y_pos_allowed = [-4,4]
    Si_y_pos_nominal = 0
    Cr_y_pos_allowed = [-15,-7]
    Cr_y_pos_nominal = -11
    
    # get current mosition
    m3_y_pos_current = m3_y.getPosition()
    # check which strip we need
    if energy >= 7 and energy <= 38: # for now we only use Pt strip
        # check y position of mirror, move if  needed
        if m3_y_pos_current < Pt_y_pos_allowed[0] or m3_y_pos_current > Pt_y_pos_allowed[1]:
            return Pt_y_pos_nominal
        else:
            return m3_y_pos_current
    else:
        raise DeviceException("Energy of %f outside permitted range of [7,38] keV" % energy)

def m4_y_in(energy):
    '''check current y position of mirror. If within range, dont move, if not, move...'''
    # define the ranges for the energies
    Pt_y_pos_allowed = [7.0,15.0]	
    Pt_y_pos_nominal = 11
    Si_y_pos_allowed = [-4,4]
    Si_y_pos_nominal = 0
    Cr_y_pos_allowed = [-15,-7]
    Cr_y_pos_nominal = -11
    
    # get current mosition
    m4_y_pos_current = m4_y.getPosition()
    # check which strip we need
    if energy >= 7 and energy <= 38: # for now we only use Pt strip
        # check y position of mirror, move if  needed
        if m4_y_pos_current < Pt_y_pos_allowed[0] or m4_y_pos_current > Pt_y_pos_allowed[1]:
            return Pt_y_pos_nominal
        else:
            return m4_y_pos_current
    else:
        raise DeviceException("Energy of %f outside permitted range of [7,38] keV" % energy)


#******************************************************************************
def m4_bender_monoImg_current_position_check(energy):
    '''checks the current m2 bender position against the nominal position. If 
    either bender is out by more than 10 counts, it returns True, else False'''
    m4_nominal_bender_position = [156270,173770] # where benders should be
    m4_bender_tolerance = 10 # in encoder counts
    m4_current_bendus_position = m4_bendus.getPosition() # where benders are
    m4_current_bendds_position = m4_bendds.getPosition()
    # compare current and nominal positions, return True if outside tolerance
    if abs(m4_current_bendus_position-m4_nominal_bender_position[0]) > m4_bender_tolerance or abs(m4_current_bendds_position-m4_nominal_bender_position[1]) > m4_bender_tolerance:
        m4_bender_move_monoImg()
        return 0
    else:
        return 0

def m4_bender_move_monoImg():
    # move to center
    m4_bendus.asynchronousMoveTo(168000)
    m4_bendds.asynchronousMoveTo(183000)
    m4_bendus.waitWhileBusy()
    m4_bendds.waitWhileBusy()
    # move to position
    m4_bendus.asynchronousMoveTo(156270)
    m4_bendds.asynchronousMoveTo(173770)
    m4_bendus.waitWhileBusy()
    m4_bendds.waitWhileBusy()


#******************************************************************************
def m4_bender_pinkLow_current_position_check(energy):
    '''checks the current m2 bender position against the nominal position. If 
    either bender is out by more than 10 counts, it returns True, else False'''
    m4_nominal_bender_position = [156270,173770] # where benders should be
    m4_bender_tolerance = 10 # in encoder counts
    m4_current_bendus_position = m4_bendus.getPosition() # where benders are
    m4_current_bendds_position = m4_bendds.getPosition()
    # compare current and nominal positions, return True if outside tolerance
    if abs(m4_current_bendus_position-m4_nominal_bender_position[0]) > m4_bender_tolerance or abs(m4_current_bendds_position-m4_nominal_bender_position[1]) > m4_bender_tolerance:
        m4_bender_move_pinkLow()
        return 0
    else:
        return 0

def m4_bender_move_pinkLow():
    # move to center
    m4_bendus.asynchronousMoveTo(168000)
    m4_bendds.asynchronousMoveTo(183000)
    m4_bendus.waitWhileBusy()
    m4_bendds.waitWhileBusy()
    # move to position
    m4_bendus.asynchronousMoveTo(156270)
    m4_bendds.asynchronousMoveTo(173770)
    m4_bendus.waitWhileBusy()
    m4_bendds.waitWhileBusy()


#******************************************************************************
def m4_bender_pinkMid_current_position_check(energy):
    '''checks the current m2 bender position against the nominal position. If 
    either bender is out by more than 10 counts, it returns True, else False'''
    m4_nominal_bender_position = [155260,172810] # where benders should be
    m4_bender_tolerance = 10 # in encoder counts
    m4_current_bendus_position = m4_bendus.getPosition() # where benders are
    m4_current_bendds_position = m4_bendds.getPosition()
    # compare current and nominal positions, return True if outside tolerance
    if abs(m4_current_bendus_position-m4_nominal_bender_position[0]) > m4_bender_tolerance or abs(m4_current_bendds_position-m4_nominal_bender_position[1]) > m4_bender_tolerance:
        m4_bender_move_pinkMid()
        return 0
    else:
        return 0

def m4_bender_move_pinkMid():
    # move to center
    m4_bendus.asynchronousMoveTo(168000)
    m4_bendds.asynchronousMoveTo(183000)
    m4_bendus.waitWhileBusy()
    m4_bendds.waitWhileBusy()
    # move to position
    m4_bendus.asynchronousMoveTo(155260)
    m4_bendds.asynchronousMoveTo(172810)
    m4_bendus.waitWhileBusy()
    m4_bendds.waitWhileBusy()


#******************************************************************************
def m4_bender_pinkHi_current_position_check(energy):
    '''checks the current m2 bender position against the nominal position. If 
    either bender is out by more than 10 counts, it returns True, else False'''
    m4_nominal_bender_position = [154170,171720] # where benders should be
    m4_bender_tolerance = 10 # in encoder counts
    m4_current_bendus_position = m4_bendus.getPosition() # where benders are
    m4_current_bendds_position = m4_bendds.getPosition()
    # compare current and nominal positions, return True if outside tolerance
    if abs(m4_current_bendus_position-m4_nominal_bender_position[0]) > m4_bender_tolerance or abs(m4_current_bendds_position-m4_nominal_bender_position[1]) > m4_bender_tolerance:
        m4_bender_move_pinkHi()
        return 0
    else:
        return 0

def m4_bender_move_pinkHi():
    # move to center
    m4_bendus.asynchronousMoveTo(168000)
    m4_bendds.asynchronousMoveTo(183000)
    m4_bendus.waitWhileBusy()
    m4_bendds.waitWhileBusy()
    # move to position
    m4_bendus.asynchronousMoveTo(154170)
    m4_bendds.asynchronousMoveTo(171720)
    m4_bendus.waitWhileBusy()
    m4_bendds.waitWhileBusy()    