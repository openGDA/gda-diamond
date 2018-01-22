#Define some constant used on Beamline I06:


from gda.jython.commands.GeneralCommands import  alias
from i06shared.constant import Close, Open
from __main__ import gv11i

print "-"*100
print "create 'closebeam' and 'openbeam' commands - GV11"
def closebeam():
	gv11i.moveTo(Close);  # @UndefinedVariable

def openbeam():
	gv11i.moveTo(Open);  # @UndefinedVariable

alias("closebeam")
alias("openbeam")







####################
#Notes: More alias from top three addition-commands for picture, closebeam and openbeam



