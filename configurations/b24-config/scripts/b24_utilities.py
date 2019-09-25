from gda.data import NumTracker
from gda.jython import InterfaceProvider
from gda.factory import Finder

print "Running b24_utilities.py..."

# set up a nice method for getting the latest file path
b24NumTracker = NumTracker("b24")
finder = Finder.getInstance()

# to get working directory, eg /dls/b24/data/2017/cm16787-4/
def wd():
    """
    Method to get working directory for the current visit in GDA
    """
    dir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    return dir

# to get the current file (scan) number, eg 5834
def cfn():
    """
    Method to get the last file (scan) number used by GDA
    """
    filenumber = b24NumTracker.getCurrentFileNumber()
    return filenumber

# to get the next file (scan) number, eg 5835
def nfn():
    """
    Method to get the next file (scan) number, eg 5835
    """
    filenumber = b24NumTracker.getCurrentFileNumber()
    return filenumber + 1

# to get the last file path, eg /dls/b24/data/2017/cm16787-4/5834
def pwd():
    """
    Method to get the last file path used by GDA, eg /dls/b24/data/2017/cm16787-4/5834
    """
    dir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    filenumber = b24NumTracker.getCurrentFileNumber()
    return os.path.join(dir, str(filenumber))

# to get the next file path, eg /dls/b24/data/2017/cm16787-4/5835
def nwd():
    """
    Method to get the next file path, eg /dls/b24/data/2017/cm16787-4/5835
    """
    dir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    filenumber = b24NumTracker.getCurrentFileNumber()
    return os.path.join(dir, str(filenumber + 1))

print "Finished running b24_utilities.py - bye!"
