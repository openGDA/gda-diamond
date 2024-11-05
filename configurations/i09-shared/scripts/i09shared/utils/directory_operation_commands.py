from gda.factory import Finder
from gda.data import NumTracker
from gda.jython import InterfaceProvider
from gda.jython.commands.GeneralCommands import alias

import os

print("-"*100)
print "create directory operation commands: "
num_tracker = NumTracker("i09");

print "    pwd : present working directory;"
# function to find the working directory
def pwd():
    '''return the current working directory'''
    curdir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    return curdir
alias("pwd")

print "    lwf : last working file path;"
# function to find the last working file path
def lwf():
    '''return the absolute path of the last working file'''
    curdir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    filenumber = num_tracker.getCurrentFileNumber();
    return os.path.join(curdir,str(filenumber))
alias("lwf")

print "    nwf : next working file path;"
# function to find the next working file path
def nwf():
    '''query the absolute path of the next working file'''
    curdir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    filenumber = num_tracker.getCurrentFileNumber();
    return os.path.join(curdir,str(filenumber+1))
alias("nwf")

print "    cfn : current file number;"
# function to find the next scan number
def cfn():
    '''query the current file number'''
    filenumber = num_tracker.getCurrentFileNumber();
    return filenumber
alias("cfn")

print "    nfn : next file number;"
# function to find the next scan number
def nfn():
    '''query the next file number'''
    return cfn() + 1

alias("nfn")

print "    setSubdirectory('newdir/newsubdir')"
# the subdirectory parts
def setSubdirectory(dirname):
    '''create a new sub-directory for data collection that follows'''
    Finder.find("GDAMetadata").setMetadataValue("subdirectory", dirname)
    #Only make data folder if doesn't already exist
    if not os.path.isdir(pwd()):
        os.makedirs(pwd())
        #Refresh client to display new folder
        client_file_announcer = Finder.find("client_file_announcer")
        if client_file_announcer is not None:
            client_file_announcer.notifyFilesAvailable([pwd()])

print "    getSubdirectory()"
def getSubdirectory():
    '''get the current sub-directory for data collection '''
    return Finder.find("GDAMetadata").getMetadataValue("subdirectory")

print