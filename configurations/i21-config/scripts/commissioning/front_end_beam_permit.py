'''
create functions and command for front end beam permit control

Created on Sep 15, 2022

@author: fy65
'''
from gdaserver import feBeamPermit  # @UnresolvedImport

def fsclose():
    feBeamPermit.moveTo('Close')

def fsopen():
    feBeamPermit.moveTo('Open')

from gda.jython.commands.GeneralCommands import alias
alias('fsclose')
alias('fsopen')  