from gda.data import NumTracker
from gda.factory import Finder


# set up a nice method for getting the latest file path
i13jNumTracker = NumTracker("i13j");
finder = Finder.getInstance()

# function to find the current scan number
def csn():
    filenumber = i13jNumTracker.getCurrentFileNumber();
    return filenumber

# function to find the next scan number
def nsn():
    filenumber = i13jNumTracker.getCurrentFileNumber();
    return filenumber + 1

