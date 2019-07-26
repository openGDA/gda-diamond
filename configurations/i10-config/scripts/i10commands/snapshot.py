'''
Created on 16 Apr 2018

@author: fy65
'''
from gda.device.scannable import DummyScannable
print "-"*100
print "creating 'dummy' scannable"
dummy = DummyScannable("dummy")

from gda.jython.commands.ScannableCommands import scan
from gda.jython.commands.GeneralCommands import alias
print "-"*100
print "creating 'snap' command for capturing a snapshot off a detector:"
print "    Usage example: >>>snap pimte 6.0"
def snap(*args):
    newargs=[dummy, 1,1,1]
    for arg in args:
        newargs.append(arg)
    scan([e for e in newargs])
alias("snap")
