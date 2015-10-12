from gda.data import NumTracker
import os
from gda.data import PathConstructor
from gda.factory import Finder


# set up a nice method for getting the latest file path
i13jNumTracker = NumTracker("i13j");
finder = Finder.getInstance()

# function to output the current scan number
def csn():
    return cfn()

# function to output the current file number
def cfn():
    filenumber = i13jNumTracker.getCurrentFileNumber();
    return filenumber

# function to output the next scan number
def nsn():
    return nfn()

# function to output the next file number
def nfn():
    filenumber = i13jNumTracker.getCurrentFileNumber();
    return filenumber + 1

# function to output the last file path
def pwd():
    dir = PathConstructor.createFromDefaultProperty()
    filenumber = i13jNumTracker.getCurrentFileNumber();
    return os.path.join(dir, str(filenumber))
    

# function to output the next file path
def nwd():
    dir = PathConstructor.createFromDefaultProperty()
    filenumber = i13jNumTracker.getCurrentFileNumber();
    return os.path.join(dir, str(filenumber + 1))