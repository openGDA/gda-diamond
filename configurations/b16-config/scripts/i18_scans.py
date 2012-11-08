from java.lang import *
from gda.configuration.properties import LocalProperties

def resetMicroFocusPanel():
    '''Resets the Start/Stop buttons on the MicroFocus Panel.'''
    controller = finder.find("MicroFocusController")
    controller.update(None, "STOP")