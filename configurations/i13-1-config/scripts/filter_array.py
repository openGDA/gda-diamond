from epics_scripts.pv_scannable_utils import createPVScannable
from gda.device.scannable import ScannableMotionBase
    
class filter_array(ScannableMotionBase):
    """
    Filter Array - Makes the Xia Filter Array a scannable:
    
    pos <name> 
    
    returns a list of elements in the beam or "Empty"
    
    <name>.positions - returns the list of possible elements
    
    pos <name> "elememt" - moves all filters out but for the one selected 
    e.g. pos filter "Fe"
    e.g pos filter "Empty"
                    
    """
    def __init__(self, name, prefix="BL13J-OP-ATTN-02:", elements=["Cr", "Fe", "Cu", "Nb"]):
        self.setName(name)
        self.setInputNames([name])
        self.elements=elements;
        self.setExtraNames([])
        self.setOutputFormat(["%s"])
        self.fStateScannable = []
        self.fTriggerScannable = []
        for i in range(1,len(self.elements)+1):
            self.fStateScannable.append( createPVScannable(`i`, prefix + "F"+`i`+"STATE", addToNameSpace=False, hasUnits=False, getAsString=True))
            self.fTriggerScannable.append(createPVScannable(`i`, prefix + "F"+`i`+"TRIGGER", False))

        

        
    def isBusy(self):
        return False

    def rawGetPosition(self):
        fState = []
        for i in range(len(self.fStateScannable)):
            fState.append(self.fStateScannable[i]())
        
        pos = 0
        for i in range( len(fState)):
            pos |= (fState[i] == "IN") << i
        if pos == 0:
            position = "Empty"
        else:
            position=""
            for i in range( len(self.elements) ):
                if pos & (1 << i) != 0:
                    if len(position) != 0:
                        position += "," 
                    position += self.elements[i]
        return position

    def rawAsynchronousMoveTo(self,new_position):
        if new_position == "Empty":
            filter = -1
        else:
            filter=len(self.elements)
            for pos in range(len(self.elements)):
                if new_position == self.elements[pos]:
                    filter = pos
                    break
            
            if filter == len(self.elements):
                raise ValueError("Position requested is inavalid:'" + new_position + "'")
        
        for f in self.fTriggerScannable:
            f.moveTo(0)
        
        #if filter indexes an filter to be moved in - as opposed to Empty    
        if filter >= 0 :
            self.fTriggerScannable[filter].moveTo(1)

    def stop(self):
        pass
