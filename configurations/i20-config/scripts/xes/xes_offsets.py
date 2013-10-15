import os
from gda.util.persistence import LocalParameters

class XESOffsets:

    def __init__(self, store_dir, spectrometer):
        self.store_dir = store_dir
        self.spectrometer = spectrometer
        self.spectrometer_scannables = spectrometer.getGroupMembers()
        self.temp_save_name = "xes_temp"
        self.current_offsets_file = ""

    #Lists the available stores (xml files) which each hold a collection of offsets
    def list_files(self):
        files = os.listdir(self.store_dir)
        if len(files)>0:
            print "Offset files available :"
            for name in files:
                if name.endswith(".xml"):
                    name_length = len(name)
                    print name[0:name_length-4]
        else:
            print "No saved offset files available"

    #Lists the current live Spectrometer offsets.
    def current(self):
        print "Current GDA spectrometer offsets:"
        for scannable in self.spectrometer_scannables:
            name = scannable.getName()
            offset = self.spectrometer.getGroupMember(name).getOffset()
            if offset == None:
                offset = [0]
            offset = offset[0]
            print "%20s : %.2f" % (name, offset)

    #Sets all the offsets to 0. Does not save the values to an xml store.
    def remove(self):
        for scannable in self.spectrometer_scannables:
            scannable.setOffset(0.0)

    #Stores the current Spectrometer offsets in the named store. This store will not be re-loaded on GDA restart.
    def save_as(self, storeName):
        store = LocalParameters.getXMLConfiguration(self.store_dir, storeName, True)
        for scannable in self.spectrometer_scannables:
            name = scannable.getName()
            # now store the offset, not the motor position
            value = scannable.getOffset()
            if value == None:
                value = 0
            store.setProperty(name,value)
        store.save()

    #Save offsets to temporary file. This file is overwritten for each save
    def save(self):
        self.save_as(self.temp_save_name)
        
    #Views the Spectrometer offsets held in the named store.
    def view(self, filename):
        store = LocalParameters.getXMLConfiguration(self.store_dir, filename, False)
        print "Spectrometer offsets for",filename,":"
        for scannable in self.spectrometer_scannables:
            name = scannable.getName()
            value = float(store.getProperty(name))
            print "%20s : %.2f" % (name, value)

    def apply_current(self):
        print "Reapplying previous spectrometer offsets..."
        apply(self.current_offsets_file)

    #Loads and sets the Spectrometer offsets from the named store.
    def apply(self, filename):
        store = LocalParameters.getXMLConfiguration(self.store_dir, filename, False)
        valuesDict = {}
        print "Applying offsets from store",filename,"..."
        for scannable in self.spectrometer_scannables:
            name = scannable.getName()
            prop = store.getProperty(name)
            if prop == None:
                prop = 0.0
            valuesDict[name] = float(prop)
        self._setFromDict(valuesDict)
        self.current_offsets_file=filename
        print "Offsets applied."
        
    def get_filename(self):
        return self.current_offsets_file
    
    #Sets the supplied dictionary of offsets to the GDA Scannables.
    #The optional second argument is a boolean, if true this will store the new offsets to the default xml store of offsets as well.
    def _setFromDict(self, offsetsDict):
        self._checkDictNames(offsetsDict)
        print "Setting the spectrometer offsets:"
        for name in offsetsDict.keys():
            offset = offsetsDict[name]
            print "\t %20s offset -> %.2f" % (name,offset)
            self.spectrometer.getGroupMember(name).setOffset([offset])
    
    def _checkDictNames(self, valuesDict):
        for name in valuesDict.keys():
            scannable = self.spectrometer.getGroupMember(name)
            if scannable == None:
                message = "scannable " + name +" could not be found. Will not apply offsets"
                raise ValueError(message)
            
    #Using the supplied dictionary of expected motor positions, this calculates the required offsets and sets them on the GDA Scannables.
    def setFromExpectedValues(self, expectedValuesDict):
        self._checkDictNames(expectedValuesDict)
        offsetsDict = {}
        for name in expectedValuesDict.keys():
            expected = expectedValuesDict[name]
            print "\t %s %f" % (name,expected)
            newOffset = self._calcOffset(name,expected)
            offsetsDict[name] = newOffset
        print offsetsDict
        self._setFromDict(offsetsDict)
        self.save()
    
    def _calcOffset(self, name,expectedReadback):
        scannable = self.spectrometer.getGroupMember(name)
        if scannable == None:
            raise "scannable",name,"could not be found. Will not apply offsets"
        readback = scannable()
        currentOffset = scannable.getOffset()
        if currentOffset == None:
            currentOffset = [0]
        currentOffset = currentOffset[0]
        newOffset = expectedReadback - (readback - currentOffset)
        return newOffset