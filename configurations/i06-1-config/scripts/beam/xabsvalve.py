'''
Created on May 4, 2023

@author: fy65
'''
from gda.jython.commands.GeneralCommands import  alias
from i06shared.constant import Close, Open
from __main__ import gv6j  # @UnresolvedImport

print("-"*100)
print("create 'closebeam' and 'openbeam' commands - GVJ6")

def closebeam():
    gv6j.moveTo(Close) 

def openbeam():
    gv6j.moveTo(Open)

alias("closebeam")
alias("openbeam")