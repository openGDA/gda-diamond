'''
Created on Jan 26, 2022

@author: fy65
'''

from gda.configuration.properties import LocalProperties
from gda.jython.commands.GeneralCommands import alias

def which_end_station():
    return str(LocalProperties.get("gda.endstation.name"))

alias("which_end_station")