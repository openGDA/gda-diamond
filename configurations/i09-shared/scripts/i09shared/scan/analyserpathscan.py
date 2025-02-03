'''
Created on 16 Oct 2013
Updated on 24 Aug 2014
Updated on 24 Jan 2025
@author: fy65
'''
from gdascripts.scan.pathscanCommand import pathscan
from gda.jython.commands.GeneralCommands import alias
from org.opengda.detector.electronanalyser.nxdetector import IAnalyserSequence
from i09shared.scan.analyserScan import get_sequence_filename, DETECTOR_DOC_STR

print("-"*100)
print("Installing analyserpathscan:")

def analyserpathscan(scannables, path, *args):
    '''
    USAGE:
    analyserpathscan (x,y,z) ([1,2,3],[4,5,6],[7,8,9]) DETECTOR "user.seq"
    
    Same as pathscan but supports loading in sequence file for DETECTOR
    '''
    newargs=[]
    i=0;
    while i< len(args):
        arg = args[i]
        newargs.append(arg)
        i=i+1
        if isinstance(arg,  IAnalyserSequence):
            filename=get_sequence_filename(args[i]);
            arg.setSequenceFile(filename)
            i=i+1
    pathscan(scannables, path, *newargs)

analyserpathscan.__doc__ = analyserpathscan.__doc__.replace("DETECTOR", DETECTOR_DOC_STR)
print(analyserpathscan.__doc__)

alias("analyserpathscan")
