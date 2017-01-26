'''
commands for directory/file operations: "
   >>>pwd - return the current data directory"
   >>>lwf - return the full path of the last working data file"
   >>>nwf - return the full path of the next working data file"
   >>>nfn - return the next data file number to be collected"
   >>>setSubdirectory('test') - change data directory to a sub-directory named 'test', created first if not exist"
   >>>getSubdirectory() - return the current sub-directory setting if exist"
Please note: users can only create sub-directory within their permitted visit data directory via GDA, not themselves."
'''
from gda.data import PathConstructor, NumTracker
from gda.factory import Finder
import os
import sys
  
# set up a nice method for getting the latest file path
numTracker = NumTracker("scanbase_numtracker");
finder=Finder.getInstance()
 
# function to find the working directory
def pwd():
    '''return the current working directory'''
    cwd = PathConstructor.createFromDefaultProperty()
    return cwd
 
# function to find the last working file path
def lwf():
    '''return the last working file path'''
    cwd = PathConstructor.createFromDefaultProperty()
    filenumber = numTracker.getCurrentFileNumber();
    return os.path.join(cwd,str(filenumber))
     
# function to find the next working file path
def nwf():
    '''query the next working file path'''
    cwd = PathConstructor.createFromDefaultProperty()
    filenumber = numTracker.getCurrentFileNumber();
    return os.path.join(cwd,str(filenumber+1))
     
# function to find the next scan number
def nfn():
    '''query the next file number or scan number'''
    filenumber = numTracker.getCurrentFileNumber();
    return filenumber+1
     
# the subdirectory parts
def setSubdirectory(dirname):
    '''create a new sub-directory under current data directory for data collection that follows'''
    if os.sep not in dirname:
        subdirectory = getSubdirectory()
        if subdirectory:
            dirname=str(subdirectory)+os.sep+str(dirname)
    finder.find("GDAMetadata").setMetadataValue("subdirectory",dirname)
    try:
        os.mkdir(pwd())
    except :
        exceptionType, exception=sys.exc_info()[:2];
        print "Error Type: ", exceptionType
        print "Error value: ", exception
 
def getSubdirectory():
    return finder.find("GDAMetadata").getMetadataValue("subdirectory")

