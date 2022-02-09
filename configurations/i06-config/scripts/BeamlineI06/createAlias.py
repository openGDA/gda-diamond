#Define some constant used on Beamline I06:


from gda.jython.commands.GeneralCommands import  alias
from i06shared.constant import Close, Open
from __main__ import gv11i, gv9i  # @UnresolvedImport

print("-"*100)
print("create 'closebeam' and 'openbeam' commands - GV9 and GV11")
def closebeam():
	gv9i.moveTo(Close);
	gv11i.moveTo(Close);

alias("closebeam")

def openbeam():
	gv11i.moveTo(Open);
	gv9i.moveTo(Open); 

alias("openbeam")







####################
#Notes: More alias from top three addition-commands for picture, closebeam and openbeam



