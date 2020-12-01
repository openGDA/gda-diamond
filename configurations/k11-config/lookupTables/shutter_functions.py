# modified "close_shutter" Hans 27/01/2020
  
def fe_shutter_open(energy):
    # opens shutter
    return 'Open'

def fe_shutter_close(energy):
    # closes shutter
    return 'Close'
	    
def eh_shutter_open(energy):
    return 'Open'

def eh_shutter_close(energy):
    return 'Close'


		
'''
def fe_shutter_move(energy):
    # opens/closes the shutter depending of current state and position of the optical elements
    return check_optical_element_positions()


def check_optical_element_positions():
	# check positions of dcm1 y and bragg stages, and current shutter status
	y_pos = dummy_dcm1_y.getPosition()
	bragg_pos = dummy_dcm1_bragg.getPosition()
	current_shutter_status = dummy_fe_shutter.getPosition()
	# if shutter is currently closed we dont need to do anything
	if current_shutter_status is 'Close':
	    return 'Close'

	# if mono is outside its operational y position, close shutter. Need to adapty y-range
	if y_pos < y_pos_allowed[0] or y_pos > y_pos_allowed[1]: 
	    #close shutter
	    return 'Close'
	# check if bragg is out of the allowed range. If yes, close shutter
	elif bragg_pos < bragg_pos_allowed[0] or bragg_pos > bragg_pos_allowed[1]:
	    # close shutter
	    return 'Close'
	# else leave shutter in its current state
	else:
	    return current_shutter_status



# allowed y and bragg ranges
y_pos_allowed = [9.1,9.3]
bragg_pos_allowed = [-18.0,-3.0]    
'''