from gdascripts.messages import handle_messages
from gda.data import NumTracker
import os
from gda.data import PathConstructor
from gda.factory import Finder
import sys

# set up a nice method for getting the latest file path
i12NumTracker = NumTracker("i12");
finder = Finder.getInstance()

def wd():
    dir = PathConstructor.createFromDefaultProperty()
    return dir
    


# function to find the last file path
def pwd():
    dir = PathConstructor.createFromDefaultProperty()
    filenumber = i12NumTracker.getCurrentFileNumber();
    return os.path.join(dir, str(filenumber))
    


# function to find the next file path
def nwd():
    dir = PathConstructor.createFromDefaultProperty()
    filenumber = i12NumTracker.getCurrentFileNumber();
    return os.path.join(dir, str(filenumber + 1))
    
# function to find the next scan number
def nfn():
    filenumber = i12NumTracker.getCurrentFileNumber();
    return filenumber + 1
    
# function to find the next scan number
def cfn():
    filenumber = i12NumTracker.getCurrentFileNumber();
    return filenumber
    

# the subdirectory parts
def setSubdirectory(dirname):
    try:
        finder.find("GDAMetadata").setMetadataValue("subdirectory", dirname)
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "problem setting metadata value -'subdirectory' to " + dirname, exceptionType, exception, traceback, False)
        print "Failed to set metadata (subdirectory) value to:", dirname, exception