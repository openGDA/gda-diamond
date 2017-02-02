from gda.jython.commands.GeneralCommands import alias
from Diamond.Utility.BeamlineFunctions import BeamlineFunctionClass

print "-"*100
print "create 'branchline' object and commands 'lastscan', 'gettitle', 'settitle', 'getvisit', 'setvisit', 'setdir'"

branchline=BeamlineFunctionClass('i06-1');
branchline.setTerminalLogger();

def lastscan():
#    return i06.getLastSrsScanFile("tmp")
    return branchline.getLastScanFile();

def setTitle(title):
    branchline.setTitle(title);
    
def settitle(title):
    branchline.setTitle(title);

def getTitle():
    return branchline.getTitle();

def gettitle():
    return branchline.getTitle();

def setVisit(visit):
    branchline.setVisit(visit);
    branchline.setSubDir("");
    
def setvisit(visit):
    branchline.setVisit(visit);
    branchline.setSubDir("");

def getVisit():
    return branchline.getVisit();
def getvisit():
    return branchline.getVisit();

def setDir(newSubDir):
    branchline.setSubDir(newSubDir);
def setdir(newSubDir):
    branchline.setSubDir(newSubDir);

alias("lastscan")
alias("getTitle"); alias("gettitle")
alias("setTitle"); alias("settitle")
alias("getVisit"); alias("getvisit")
alias("setVisit"); alias("setvisit")
alias("setDir");   alias("setdir")


