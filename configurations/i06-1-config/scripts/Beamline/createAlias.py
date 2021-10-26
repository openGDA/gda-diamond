#Define some constant used on Beamline I06-1:


from gda.jython.commands.GeneralCommands import  alias
from i06shared.constant import Close, Open
from __main__ import gv4j  # @UnresolvedImport

print("-"*100)
print("create 'closebeam' and 'openbeam' commands - GVJ4")

def closebeam():
	gv4j.moveTo(Close)  # @UndefinedVariable

def openbeam():
	gv4j.moveTo(Open)  # @UndefinedVariable

alias("closebeam")
alias("openbeam")





