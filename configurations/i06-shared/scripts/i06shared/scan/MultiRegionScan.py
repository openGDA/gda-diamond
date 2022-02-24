'''
scan over multiple regions, each of which specify its own [start, stop, step] as a list for this region. 
It supports both single and multiple images at each scan data point to be collected by the detector, 
first parameter after detector is the number of images to be collected, the second parameter is the detector exposure time.
If the 1st parameter is not given, it is default to single image per scan data point.

Following Jython namespace parameters are available to control the behaviour of the mrscan

ALWAYS_COLLECT_AT_STOP_POINT - determine if data at the end or stop point is collected or not, default is True.
NUMBER_OF_DECIMAL_PLACES - determine the number of decimal point is used for each scan data point position, default is 5.

Created on Nov 15, 2021

@author: fy65
'''
from gda.jython.commands.ScannableCommands import scan
from gda.device import Scannable
import time
from i06shared.scan.miscan import all_elements_are_list_of_number, all_elements_are_number, \
    parse_other_arguments, save_detector_settings_before_scan, \
    restore_detector_setting_after_scan, parse_detector_arguments
from types import TupleType
from gda.device.detector import NXDetector
from gdascripts.metadata.nexus_metadata_class import meta
from gda.jython import InterfaceProvider

PRINTTIME = False
NUMBER_OF_DECIMAL_PLACES = 5
ALWAYS_COLLECT_AT_STOP_POINT = True


def parse_tuple_arguments(command, newargs, arg, always_collect_at_stop, decimal_places):
    command += "("
    if all_elements_are_list_of_number(arg):  # parsing multiple regions into single tuple, fix floating point issue by round the number to decimal_places
        new_position_list = []
        list_of_lists = []
        # parseing multiple regions into a single tuple of positions
        for each in arg:
            position = each[0]
            while position <= each[1]:
                if not position in new_position_list:
                    new_position_list.append(round(float(position), decimal_places))
                position += each[2]
            
            if position > each[1] and always_collect_at_stop and not float(each[1]) in new_position_list:
                new_position_list.append(each[1])
            list_of_lists.append("[" + ",".join([str(x) for x in each]) + "]")        
        newargs.append(tuple(new_position_list))
        command += ",".join(list_of_lists)
    elif all_elements_are_number(arg):  # parsing scannable group's position lists
        newargs.append(arg)
        command += ",".join([str(x) for x in arg])
    else:
        raise SyntaxError("Tuple of [start, stop, step]s or tuple of position values are required!")
    command += ") "
    return command, newargs


def mrscan(*args):
    '''support multiple regions scanning in which each region has different step size. 
    Regions are specified as tuple of list of regions
    For example:
        mrscan testMotor1 ([0,5,1], [6,10,0.1], [10,15,1]) detector <number_of_images> 0.1'''
    
    ALWAYS_COLLECT_AT_STOP = InterfaceProvider.getJythonNamespace().getFromJythonNamespace("ALWAYS_COLLECT_AT_STOP_POINT")
    DECIMAL_PLACES = InterfaceProvider.getJythonNamespace().getFromJythonNamespace("NUMBER_OF_DECIMAL_PLACES")
    
    if len(args) == False:
        raise SyntaxError("No argument is given to scan command!")
    
    if not isinstance(args[0], Scannable):
        raise SyntaxError("First argument to scan command must be a scannable")
    
    command = "mrscan "
    
    starttime = time.ctime()
    start = time.time()
    if PRINTTIME: print("=== Scan started: " + starttime)
    
    newargs = []
    i = 0;
    while i < len(args):
        arg = args[i]
        if type(arg) == TupleType:
            command, newargs = parse_tuple_arguments(command, newargs, arg, ALWAYS_COLLECT_AT_STOP, DECIMAL_PLACES)
        else:
            newargs.append(arg)
            command = parse_other_arguments(command, arg)
        i = i + 1
        CACHE_PARAMETER_TOBE_CHANGED = False
        if isinstance(arg, NXDetector):
            adbase, image_mode, num_images = save_detector_settings_before_scan(arg)
            if all((adbase, image_mode, num_images)):
                CACHE_PARAMETER_TOBE_CHANGED = True
            command, newargs = parse_detector_arguments(command, newargs, args, i, arg)
            i = i + 1

    meta.addScalar("user_input", "command", command)
    try:
        scan([e for e in newargs])
    finally:
        if CACHE_PARAMETER_TOBE_CHANGED:
            restore_detector_setting_after_scan(adbase, image_mode, num_images)
        meta.rm("user_input", "command")    

    if PRINTTIME: print ("=== Scan ended: " + time.ctime() + ". Elapsed time: %.0f seconds" % (time.time() - start))


from gda.jython.commands.GeneralCommands import alias 
alias("mrscan")

