'''
Created on 16 Oct 2013
Updated on 24 Aug 2014
Updated on 24 Jan 2025
@author: fy65
'''
from gdascripts.scan.pathscanCommand import pathscan
from gda.jython.commands.GeneralCommands import alias
from org.opengda.detector.electronanalyser.nxdetector import IAnalyserSequence
from i09shared.scan.analyserScan import get_sequence_filename

def analyserpathscan(scannables, path, *args):
    '''
    USAGE:
    analyserpathscan (x,y,z) ([1,2,3],[4,5,6],[7,8,9]) detector "user.seq"

    Same as pathscan but supports loading in sequence file for detector
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

alias("analyserpathscan")
