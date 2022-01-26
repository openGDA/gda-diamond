#Define a list of useful functions for beamline control

import __main__ as gdamain
import sys;
from os import system;

import zipfile;
import re;
import os;
import cPickle as pickle;


from gda.jython.commands import GeneralCommands


class UtilFunctions(object):
    def __init__(self):
#        self.nsh=globals();
        self.nsh=vars(gdamain);
#        self.cs=Finder.find("command_server");
        self.cs = self.nsh['command_server'];
        self.pickleFileName='/dls_sw/i06/var/defaultList.txt';

    def swap(self, a, b):
        return b,a
    
    #To get the current scan number
    def getScanNumber(self):
        from gda.data import NumTracker
        nt = NumTracker("tmp")
        scanNumber = nt.getCurrentFileNumber();
        del nt;
        return scanNumber
    
    #To get the current scan number
    def incScanNumber(self):
        from gda.data import NumTracker
        nt = NumTracker("tmp")
        nt.incrementNumber();
        del nt;
        return;
    
    #To setup an 'interruptable()' function which can be used to make for-loop interruptable in GDA."
    #To use this, place 'interruptable()' call as the 1st or last line inside a for-loop."
    def interruptable(self):
        GeneralCommands.pause()
    
    #To remvoe all devices inside a list by name
    def removeDevices(self, nameList):
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
                self.nsh[dn]
            except:
                pass;
    
            try:
                exec("del "+ dn);
            except:
                pass;    
        exec("try:\n    del "+ ', '.join(nameList) + "\nexcept:\n    pass;\n")
        

    
    def getDevice(self, deviceName):
        device=None;
        
        if type(deviceName).__name__ in ['str', 'unicode']:#A name is giving
            if deviceName in self.nsh.keys():
                device=self.nsh[str(deviceName)]
            else:
                print "device %s does not exist" %deviceName;
        else:#a real device is given
            if deviceName in self.nsh.values():
                device = deviceName;
            else:
                print "device %s does not exist" %deviceName;
        return device;
    
    def isDefaultDeive(self, deviceName):
        
        device=self.getDevice(deviceName);
        if device is None:
            print "device %s does not exist" %deviceName;
            return False;
            
        defaultList = self.cs.getDefaultScannables();
        result = device in defaultList;
        
        return result;
    
    def removeDefaults(self, nameList):
        
        for deviceName in nameList:
            self.cs.removeDefault(self.nsh[deviceName])
        return
       
    def pickleIt(self, pickleFileName, content):
        try:
            outStream = file(pickleFileName, 'wb');
            #Pickle the file number and dump to a file stream
            pickle.dump(content, outStream);
            outStream.close();
        except IOError:
            print "Can not preserve the content.";
        
    def restoreIt(self, pickleFileName):
        content = None;
        try:
            inStream = file(pickleFileName, 'rb');
            content = pickle.load(inStream);
            inStream.close();
        except IOError:
            print "Can not restore the pickled content.";
        return content;
        
    def backupDefaults(self):
        defaultList=[];
        defaultList.extend( self.cs.getDefaultScannableNames() );
        self.pickleIt(self.pickleFileName, defaultList);
            
    
    def restoreDefaults(self):
        '''Restore the pickled device list'''
    
        fileconetent = self.restoreIt(self.pickleFileName);
    
        if fileconetent is None:
            print "Nothing to restore";
            return;
        
        for deviceName in fileconetent:
            self.cs.addDefault(self.nsh[deviceName])
        return
        
