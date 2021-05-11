"""Editable script to generate a scannable group and
perform a scan using that group with positions for each secondary member
calculated by user-defined functions
"""

######################################################################
# Define start, stop and step for primary scannable here
######################################################################
start = 3
stop = 5
step = 0.2

######################################################################
# Define your functions for secondary scannables here
# eg:
#
# def func1(a):
#   return 3*a + 5*a**2 - 6
#
######################################################################

def test_func1(a):
    return a * 3

def test_func2(a):
    return 3 * a + 5 * a ** 2 - 6

#####################################################################
# Scannable list
#--------------------
# Edit this list with the primary scannable name as first member
# and secondary scannables added as (secondary_scannable, function_name, secondary_start_val)
# Defining secondary_start_val will cause an offset to  be applied, allowing you to choose
# the starting value for the sequence relating to that scannable
#
# If secondary_start_val is not required, define it as: None
# eg:
#
# input_list = [   stagex,
#                 (stagey, func1, None),
#                 (stage_z, func2, 12)
#              ]
#
#####################################################################
input_list = [   stagex,
                (stagey, test_func1, None),
                (stage_z, test_func2, 12)
             ]
#####################################################################


scan_creator = ScanCreator(start, stop, step, input_list)
scan_creator.create_group_and_tuples()
# Could add a scan command here
# eg: scan scan_group scan_points analyser
