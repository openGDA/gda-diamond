'''
Usage:
    1. run this script from PyDev editor in Scripts perspective to create function called 'pathscan',
    'multiregionanalyserpathscan', and 'analyserpathscan'
    2. start your scan using one of the following methods from jython terminal:
    
    >>>pathscan((x,y,z), ([1,2,3],[4,5,6],[7,8,9]), [hm3iamp20,])
    for scannables, but you cannot use ew4000 as pathscan does not take filename 'user.seq';
    
    >>>multiregionanalyserpathscan((x,y,z), ([1,2,3],[4,5,6],[7,8,9]), ew4000, "user.seq", hm3iamp20)
    for energy scan with multiple regions collected at any scan data point from the analyser. 
    
    >>>analyserpathscan((x,y,z), ([1,2,3],[4,5,6],[7,8,9]), ew4000, "user.seq", hm3iamp20)
    for energy scan with single region collected from the analyser.
    
Created on 16 Oct 2013

@author: fy65
'''
from gda.device.scannable.scannablegroup import ScannableGroup
from gda.jython.commands.ScannableCommands import scan
from gda.jython.commands.GeneralCommands import alias
from org.opengda.detector.electronanalyser.nxdetector import EW4000,\
    EW4000CollectionStrategy
from gda.factory import Finder
from gda.data import PathConstructor
from org.opengda.detector.electronanalyser.utils import OsUtil, FilenameUtil
from org.opengda.detector.electronanalyser.event import SequenceFileChangeEvent
from time import sleep
from gda.jython import InterfaceProvider, Jython
from org.opengda.detector.electronanalyser.scan import RegionScannable,\
    RegionPositionProvider
import os


def pathscan(scannables, path, args): #@UndefinedVariable
    ''' 
    Scan a group of scannables following the specified path and 
    collect data at each point from scannables args
    '''
    sg=ScannableGroup()
    for each in scannables:
        sg.addGroupMember(each)
    sg.setName("pathgroup")
    scan([sg, path]+list(args))

def multiregionanalyserpathscan(scannables, path, *args):
    '''
    perform a single or multiple regions analyser data collection at each point on the specified path,
    and produce multiple data files - a single scan file recording scannables' poistions and metadata, 
    plus one analyser data file for each region defined in your sequence definition file. Data links 
    are created in the scan file to link to the data items in the analyser data file.
    
    implementation details:
    This function pre-process sequence file to set up analyser 'ew4000' ready for data collection, 
    then delegate the scan process to 'pathscan'.    
    '''
    newargs=[]
    i=0;
    while i< len(args):
        arg = args[i]
        newargs.append(arg)
        i=i+1
        if isinstance( arg,  EW4000 ):
            controller = Finder.getInstance().find("SequenceFileObserver")
            xmldir = PathConstructor.createFromDefaultProperty()+"xml"+os.sep;
            filename=xmldir+args[i];
            if (OsUtil.isWindows()) :
                FilenameUtil.setPrefix("D:")
                filename=FilenameUtil.convertSeparator(filename)
            controller.update(controller,SequenceFileChangeEvent(filename))
            sleep(1.0)
            while (InterfaceProvider.getScanStatusHolder().getScanStatus()==Jython.PAUSED):
                sleep(1.0)
            arg.setSequenceFilename(filename)
            if isinstance(arg.getCollectionStrategy(), EW4000CollectionStrategy):
                arg.getCollectionStrategy().setSequence(arg.loadSequenceData(filename))
            i=i+1
    pathscan(scannables, path, newargs)


def analyserpathscan(scannables, path, *args):
    '''
    perform ascannables, path,  single region analyser data collection at each point on the specified path,
    and produce a single scan data files recording scannables' poistions and metadata, and 
    analyser data for the active region defined in your sequence definition file.
    
    implementation details:
    This function pre-process sequence file to set up Region Position Provider for scannable 
    'regions' ready for data collection using analyser 'ew4001', then delegate the scan 
    process to 'pathscan'.
    '''
    newargs=[]
    i=0;
    while i< len(args):
        arg = args[i]
        newargs.append(arg)
        i=i+1
        if isinstance( arg,  RegionScannable ):
            controller = Finder.getInstance().find("SequenceFileObserver")
            xmldir = PathConstructor.createFromDefaultProperty()+"xml"+os.sep;
            filename=xmldir+args[i];
            if (OsUtil.isWindows()) :
                FilenameUtil.setPrefix("D:")
                filename=FilenameUtil.convertSeparator(filename)
            controller.update(controller,SequenceFileChangeEvent(filename))
            sleep(1.0)
            while (InterfaceProvider.getScanStatusHolder().getScanStatus()==Jython.PAUSED):
                sleep(1.0)
            newargs.append( RegionPositionProvider(filename) )
            #newargs.append( arg ) # to read the actual position
            i=i+1
    pathscan(scannables, path, newargs)

mrapathscan=multiregionanalyserpathscan
srapathscan=analyserpathscan
alias("mrapathscan")
alias("srapathscan")