#Define a list of useful functions for beamline control

import __main__ as gdamain  # @UnresolvedImport
import cPickle as pickle;

from gda.factory import Finder
from gda.jython.commands import GeneralCommands

from Diamond.Utility.ScriptLogger import ScriptLoggerClass;
from gda.configuration.properties import LocalProperties

print "-"*100
print "Setup the utility functions"
print "    'logger' object for script logging"
print "    'finder' object for finding object by object's name"
print "    'getScanNumber()' returns current scan file number "
print "    'interruptable()' used in script to make the script interruptable when click STOP button in GDA client"
print "    'removeDevices(nameList)' remvoe all devices inside a given list"
print "    'getDevice(deviceName)' get a device by its name"
print "    'isDefaultDevice(deviceName)' check if a named device in GDA default list"
print "    'removeDefaults(nameList)'m removes a list of named devices from GDA default list"
print "    'backupDefaults()' backup current GDA default list to GDA cache in the file system"
print "    'restoreDefaults()' restores GDA defaults list from GDA cache"

#Introduce the script logger
logger=ScriptLoggerClass()

def swap(a, b):
    return b,a

#To get the current scan number
def getScanNumber():
    from gda.data import NumTracker
    nt = NumTracker("tmp")
    scanNumber = nt.getCurrentFileNumber();
    del nt;
    return scanNumber

#To get the current scan number
def incScanNumber():
    from gda.data import NumTracker
    nt = NumTracker("tmp")
    nt.incrementNumber();
    del nt;
    return;

#To setup an 'interruptable()' function which can be used to make for-loop interruptable in GDA."
#To use this, place 'interruptable()' call as the 1st or last line inside a for-loop."
def interruptable():
    GeneralCommands.pause()

#To remvoe all devices inside a list by name
def removeDevices(nameList):
    for dn in nameList:
        try:
            del globals()[dn];
        except:
            pass;
        
        try:
            del locals()[dn];
        except:
            pass;
        
        try:
            del vars(gdamain)[dn]
        except:
            pass;

        try:
            exec("del "+ dn);
        except:
            pass;    

    exec("try:\n    del "+ ', '.join(nameList) + "\nexcept:\n    pass;\n")
    

def getDevice(deviceName):
    device=None;
#    nsh=globals();
    nsh=vars(gdamain);
    
    if type(deviceName).__name__ in ['str', 'unicode']:#A name is giving
        if deviceName in nsh.keys():
            device=nsh[str(deviceName)]
        else:
            print "device %s does not exist" %deviceName;
    else:#a real device is given
        if deviceName in nsh.values():
            device = deviceName;
        else:
            print "device %s does not exist" %deviceName;
    return device;

def isDefaultDevice(deviceName):
    
    device=getDevice(deviceName);
    if device is None:
        print "device %s does not exist" %deviceName;
        return False;
        
    cs=Finder.find("command_server");
    defaultList = cs.getDefaultScannables();
    result = device in defaultList;
    
    return result;

def removeDefaults(nameList):
    cs=Finder.find("command_server");
#    nsh=globals();
    nsh=vars(gdamain);
    
    for deviceName in nameList:
        cs.removeDefault(nsh[deviceName])
    return
   
def backupDefaults():
    cs=Finder.find("command_server");
    defaultscannables=cs.getDefaultScannables()
    defaultScannableNames=[]
    for each in defaultscannables:
        defaultScannableNames.append(each.getName())
    defaultList=[];
    defaultList.extend( defaultScannableNames );
    beamlineName=LocalProperties.get("gda.beamline.name")
    pickleFileName='/dls_sw/'+beamlineName+'/software/gda_versions/var/defaultList.txt';

    try:
        outStream = file(pickleFileName, 'wb');
        #Pickle the file number and dump to a file stream
        pickle.dump(defaultList, outStream);
        outStream.close();
    except IOError:
        print "Can not preserve the default file list.";
        

def restoreDefaults():
    '''Restore the pickled device list'''

    beamlineName=LocalProperties.get("gda.beamline.name")
    pickleFileName='/dls_sw/'+beamlineName+'/software/gda_versions/var/defaultList.txt';
    fileconetent = None;
    try:
        inStream = file(pickleFileName, 'rb');
        fileconetent = pickle.load(inStream);
        inStream.close();
    except IOError:
        print "No previous pickled file numbers. Create new one";

    if fileconetent is None:
        print "Nothing to restore";
        return;
    
    cs=Finder.find("command_server");
#    nsh=globals();
    nsh=vars(gdamain);
    
    for deviceName in fileconetent:
        cs.addDefault(nsh[deviceName])
    return
        
