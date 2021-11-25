#Define some constant used on Beamline I06:


from gda.jython.commands.GeneralCommands import  alias
from i06shared.constant import Close, Open

print("-"*100)
print("create 'closebeam' and 'openbeam' commands - GV9 and GV11")
def closebeam():
	gv9i.moveTo(Close);  # @UndefinedVariable
	gv11i.moveTo(Close);  # @UndefinedVariable

alias("closebeam")

def openbeam():
	gv11i.moveTo(Open);  # @UndefinedVariable
	gv9i.moveTo(Open);  # @UndefinedVariable

alias("openbeam")







####################
#Notes: More alias from top three addition-commands for picture, closebeam and openbeam



