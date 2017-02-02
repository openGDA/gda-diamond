#Define some constant used on Beamline I06-1:


from gda.jython.commands.GeneralCommands import  alias
from i06shared.constant import Close, Open

print "-"*100
print "create 'closebeam' and 'openbeam' commands - GV17"

def closebeam():
	gv4j.moveTo(Close);  # @UndefinedVariable

def openbeam():
	gv4j.moveTo(Open);  # @UndefinedVariable

alias("closebeam")
alias("openbeam")





