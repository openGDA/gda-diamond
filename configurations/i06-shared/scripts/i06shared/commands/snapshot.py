'''
Created on 16 Apr 2018

@author: fy65
'''
from gda.jython.commands.ScannableCommands import scan
from gda.jython.commands.GeneralCommands import alias

print "-"*100
print "creating 'snap' command for capturing a snapshot off a detector:"
print "    Usage example: >>>snap pimte 6.0"

def snap(*args):
    newargs=[ds, 1,1,1]  # @UndefinedVariable
    for arg in args:
        newargs.append(arg)
    scan([e for e in newargs])
    
alias("snap")
