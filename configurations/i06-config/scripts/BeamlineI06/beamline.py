from gda.jython.commands.GeneralCommands import alias

from Diamond.Utility.BeamlineFunctions import BeamlineFunctionClass
print "-"*100
print "create 'peemline' object and commands 'lastscan', 'gettitle', 'settitle', 'getvisit', 'setvisit', 'setdir'"

peemline=BeamlineFunctionClass('i06');
peemline.setTerminalLogger();

def lastscan():
#    return peemline.getLastSrsScanFile("tmp")
    return peemline.getLastScanFile();

def setTitle(title):
    peemline.setTitle(title);
    
def settitle(title):
    peemline.setTitle(title);

def getTitle():
    return peemline.getTitle();

def gettitle():
    return peemline.getTitle();

def setVisit(visit):
    peemline.setVisit(visit);
    peemline.setSubDir("");
    
def setvisit(visit):
    peemline.setVisit(visit);
    peemline.setSubDir("");

def getVisit():
    return peemline.getVisit();
def getvisit():
    return peemline.getVisit();

def setDir(newSubDir):
    peemline.setSubDir(newSubDir);
def setdir(newSubDir):
    peemline.setSubDir(newSubDir);

alias("lastscan")
alias("getTitle"); alias("gettitle")
alias("setTitle"); alias("settitle")
alias("getVisit"); alias("getvisit")
alias("setVisit"); alias("setvisit")
alias("setDir");   alias("setdir")


