from java.lang import *
from gda.configuration.properties import LocalProperties
from gda.factory import Finder

def resetMicroFocusPanel():
    '''Resets the Start/Stop buttons on the MicroFocus Panel.'''
    controller = Finder.find("MicroFocusController")
    controller.update(None, "STOP")