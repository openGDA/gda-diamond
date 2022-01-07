from gda.jython.commands.GeneralCommands import alias

from Diamond.Utility.BeamlineFunctions import BeamlineFunctionClass
from gda.configuration.properties import LocalProperties
print("-"*100)
print("create 'beamlinefunction' object and commands 'lastscan', 'gettitle', 'settitle', 'getvisit', 'setvisit', 'setdir'")

beamline = LocalProperties.get(LocalProperties.GDA_BEAMLINE_NAME)
beamlinefunction = BeamlineFunctionClass(beamline);
beamlinefunction.setTerminalLogger();

def lastscan():
    return beamlinefunction.getLastScanFile();

def setTitle(title):
    beamlinefunction.setTitle(title);
    
def settitle(title):
    beamlinefunction.setTitle(title);

def getTitle():
    return beamlinefunction.getTitle();

def gettitle():
    return beamlinefunction.getTitle();

def setVisit(visit):
    beamlinefunction.setVisit(visit);
    beamlinefunction.setSubDir("");
    
def setvisit(visit):
    beamlinefunction.setVisit(visit);
    beamlinefunction.setSubDir("");

def getVisit():
    return beamlinefunction.getVisit();
def getvisit():
    return beamlinefunction.getVisit();

def setDir(newSubDir):
    beamlinefunction.setSubDir(newSubDir);
def setdir(newSubDir):
    beamlinefunction.setSubDir(newSubDir);

alias("lastscan")
alias("getTitle"); alias("gettitle")
alias("setTitle"); alias("settitle")
alias("getVisit"); alias("getvisit")
alias("setVisit"); alias("setvisit")
alias("setDir");   alias("setdir")


