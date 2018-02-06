'''
Created on 22 Sep 2009

@author: fy65
'''
from gda.analysis import ScanFileHolder, Plotter
from gda.analysis.io import MACLoader
from org.eclipse.dawnsci.analysis.api.io import ScanFileHolderException


import re
INT_RE = re.compile(r"^[-]?\d+$")
def representsInt(s):
    return INT_RE.match(str(s)) is not None

def plot(filename, Overlay=True):
    '''Plot collected, rebinned MAC data on "MAC" Panel.
    
       syntax: plot(name,[True|False])
       
          where:
                name is the file name or file number
                True means clear old plot data from the graph (Default)
                False means plot over the exist data on the graph
                Negative file number refers to the past data collected relative to the current one (0). 
                        
          e.g.  plot(0)               --> plot current data just collected
                plot(-1)              --> plot the last data collected
                plot(1121)            --> plot data with file number 1121
                plot(0,False)         --> clear graph before plotting current data
        
    '''
    sfh = loadMacData(filename)
    print("Data plotting, please wait ...")
    if Overlay:
        Plotter.plotOver("MAC", sfh.getAxis(0), sfh.getAxis(1))
    else:
        Plotter.plot("MAC", sfh.getAxis(0), sfh.getAxis(1))
  
def loadMacData(filename):
    '''Load MAC data file into a ScanFileHolder object, supporting relative loading with respect to the current collected data (0)'''
    sfh = ScanFileHolder()
    try:
        if filename == None:
            #current file
            sfh.load(MACLoader(0))
        elif representsInt(filename):
            #past file - relative path
            sfh.load(MACLoader(int(filename)))
        else:
            #absolute file path
            sfh.load(MACLoader(filename))
    except ScanFileHolderException, err:
        print "File loader failed. " + err
    return sfh

 

