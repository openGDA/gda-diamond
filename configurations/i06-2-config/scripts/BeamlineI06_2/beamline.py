from gda.jython.commands.GeneralCommands import alias

from Diamond.Utility.BeamlineFunctions import BeamlineFunctionClass
print("-"*100)
print("create 'speleemline' object and commands 'lastscan', 'gettitle', 'settitle', 'getvisit', 'setvisit', 'setdir'")

speleemline=BeamlineFunctionClass('i06-2');
speleemline.setTerminalLogger();

def lastscan():
    return speleemline.getLastScanFile();

def setTitle(title):
    speleemline.setTitle(title);
    
def settitle(title):
    speleemline.setTitle(title);

def getTitle():
    return speleemline.getTitle();

def gettitle():
    return speleemline.getTitle();

def setVisit(visit):
    speleemline.setVisit(visit);
    speleemline.setSubDir("");
    
def setvisit(visit):
    speleemline.setVisit(visit);
    speleemline.setSubDir("");

def getVisit():
    return speleemline.getVisit();
def getvisit():
    return speleemline.getVisit();

def setDir(newSubDir):
    speleemline.setSubDir(newSubDir);
def setdir(newSubDir):
    speleemline.setSubDir(newSubDir);

alias("lastscan")
alias("getTitle"); alias("gettitle")
alias("setTitle"); alias("settitle")
alias("getVisit"); alias("getvisit")
alias("setVisit"); alias("setvisit")
alias("setDir");   alias("setdir")


