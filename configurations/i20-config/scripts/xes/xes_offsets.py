import os
from gda.util.persistence import LocalParameters

class XESOffsets:

    def __init__(self, store_dir, spectrometer):
        self.store_dir = store_dir
        self.spectrometer = spectrometer
        self.spectrometer_scannables = spectrometer.getGroupMembers()
        self.temp_save_name = "xes_temp"
        self.current_offsets_file = ""

    def getCurrentFile(self):
        return self.current_offsets_file

    def listFiles(self):
        files = os.listdir(self.store_dir)
        if len(files)>0:
            print "Offset files available :"
            for name in files:
                if name.endswith(".xml"):
                    name_length = len(name)
                    print name[0:name_length-4]
        else:
            print "No saved offset files available"

    def getCurrent(self):
        print "Current GDA spectrometer offsets:"
        for scannable in self.spectrometer_scannables:
            name = scannable.getName()
            offset = self.spectrometer.getGroupMember(name).getOffset()
            if offset == None:
                offset = [0]
            offset = offset[0]
            print "%20s : %.2f" % (name, offset)

    def removeAll(self):
        for scannable in self.spectrometer_scannables:
            scannable.setOffset(0.0)

    def saveAs(self, storeName):
        store = LocalParameters.getXMLConfiguration(self.store_dir, storeName, True)
        for scannable in self.spectrometer_scannables:
            name = scannable.getName()
            value = scannable.getOffset()
            if value == None:
                value = 0
            store.setProperty(name,value)
        store.save()

    def save(self):
        self.saveAs(self.temp_save_name)
        
    def view(self, filename):
        store = LocalParameters.getXMLConfiguration(self.store_dir, filename, False)
        print "Spectrometer offsets for",filename,":"
        for scannable in self.spectrometer_scannables:
            name = scannable.getName()
            value = float(store.getProperty(name))
            print "%20s : %.2f" % (name, value)

    def reApply(self):
        print "Reapplying previous spectrometer offsets..."
        self.apply(self.current_offsets_file)

    #Loads and sets the Spectrometer offsets from the named store.
    def apply(self, filename):
        if filename!='var':
            store = LocalParameters.getXMLConfiguration(self.store_dir, filename, False)
            valuesDict = {}
            print "Applying offsets from store",filename,"..."
            for scannable in self.spectrometer_scannables:
                name = scannable.getName()
                prop = store.getProperty(name)
                if prop == None:
                    prop = 0.0
                valuesDict[name] = float(prop)
            self._applyFromDict(valuesDict)
            self.current_offsets_file=filename
            print "Offsets applied."
    
    def _applyFromDict(self, offsetsDict):
        self._checkNameExists(offsetsDict)
        print "Setting the spectrometer offsets:"
        for name in offsetsDict.keys():
            offset = offsetsDict[name]
            print "\t %20s offset -> %.2f" % (name,offset)
            self.spectrometer.getGroupMember(name).setOffset([offset])
    
    def _checkNameExists(self, dictionary):
        for name in dictionary.keys():
            scannable = self.spectrometer.getGroupMember(name)
            if scannable == None:
                message = "scannable " + name +" could not be found. Will not apply offsets"
                raise ValueError(message)