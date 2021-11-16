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
from types import TupleType, FloatType, IntType
from gda.device.detector import NXDetector
from gda.device.detector.addetector.collectionstrategy import ImageModeDecorator
from gdascripts.metadata.nexus_metadata_class import meta
from gda.jython import InterfaceProvider
from scan.miscan import allElementsAreListOfNumber, allElementsAreNumber

PRINTTIME = False
NUMBER_OF_DECIMAL_PLACES = 5
ALWAYS_COLLECT_AT_STOP_POINT = True

def mrscan(*args):
    '''support multiple regions scanning in which each region has different step size. 
    Regions are specified as tuple of list of regions
    For example:
        mrscan testMotor1 ([0, 5, 1], [6,10,0.1], [10,15,1]) detector <number_of_images> 0.1'''
    
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
    
    newargs=[]
    i=0;
    while i< len(args):
        arg = args[i]
        if type(arg)==TupleType:
            command += "(" 
            if allElementsAreListOfNumber(arg):
                #parsing multiple regions into single tuple, fix floating point issue by round the number to NUMBER_OF_DECIMAL_PLACES
                new_position_list=[]
                list_of_lists = []
                for each in arg:
                    position = each[0]
                    while position < each[1]:
                        if not position in new_position_list:
                            new_position_list.append(round(position, DECIMAL_PLACES))
                        position += each[2]
                    if not position == each[1] and ALWAYS_COLLECT_AT_STOP:
                        new_position_list.append(each[1])                                                
                    list_of_lists.append("[" + ",".join([str(x) for x in each]) +"]")
                newargs.append(tuple(new_position_list))
                command += ",".join(list_of_lists)
            elif allElementsAreNumber(arg):
                #parsing scannable group's position lists
                newargs.append(arg)
                command += ",".join([str(x) for x in arg])
            else:
                raise SyntaxError("Tuple of [start, stop, step]s or tuple of position values are required!")
            command += ") "
        else:
            newargs.append(arg)
            if isinstance(arg, Scannable):
                command += arg.getName() + " "
            if type(arg)==IntType or type(arg)== FloatType:
                command += str(arg) + " "

        i=i+1
        if isinstance( arg,  NXDetector ):
            decoratee = arg.getCollectionStrategy().getDecoratee()
            if isinstance(decoratee, ImageModeDecorator):
                if i<len(args)-1: # more than 2 arguments following detector
                    if type(args[i])==IntType and (type(args[i+1])==IntType or type(args[i+1])== FloatType):
                        #support the miscan command - first input after detector is number of images per data point
                        decoratee.setNumberOfImagesPerCollection(args[i])
                    elif type(args[i])==FloatType and (type(args[i+1])==IntType or type(args[i+1])== FloatType):
                        raise TypeError, "Number of images to collect per scan data point must be Int type."
                    elif type(args[i])==FloatType and not (type(args[i+1])==IntType or type(args[i+1])== FloatType):
                        decoratee.setNumberOfImagesPerCollection(1)
                    command += str(args[i]) + " "
                elif i==len(args)-1: #followed by only one argument - must be exposure time
                    decoratee.setNumberOfImagesPerCollection(1)
            else: #exposure time is the last one in the scan command
                newargs.append(args[i]) #single image per data point
                command += str(args[i])
            i=i+1
    
    meta.addScalar("user_input", "command", command)
    try:
        scan([e for e in newargs])
    finally:
        meta.rm("user_input", "command")    

    if PRINTTIME: print ("=== Scan ended: " + time.ctime() + ". Elapsed time: %.0f seconds" % (time.time() - start))

from gda.jython.commands.GeneralCommands import alias 
alias("mrscan")

