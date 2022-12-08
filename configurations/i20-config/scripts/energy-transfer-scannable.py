from gda.util import QuantityFactory
from gda.device.scannable import ConvertorScannable
from gda.util.converters import IQuantityConverter
from __builtin__ import None

# Convert values to/from position relative to current position of scannable
## toTarget converts from relative to absolute position :  absolute position = refScannable.getPosition() - sourcePosition
## toSource converts from absolute to relative position :  relative position = refScannable.getPosition() - targetPosition

class RelativePositionConverter(IQuantityConverter) :

    def __init__(self) :
        self.units = ""
        self.refScannable = None

    # The reference scannable : values are relative to its current position
    def setReferenceScannable(self, refScannable) :
        self.refScannable = refScannable
        self.units = refScannable.getUserUnits()
    
    def getAcceptableSourceUnits(self):
        return [self.units]
    
    def getAcceptableTargetUnits(self):
        return [self.units]
    
    def handlesStoT(self):
        return True
    
    def handlesTtoS(self):
        return True
    
    # Convert given 'source' position (relative to reference scannable) to an absolute value
    def toTarget(self, source):
        #print "To target : source = "+source.toString()
        inputValue = QuantityFactory.createFromObject(source, self.units).getValue();
        #print target.toString(), inputValue.toString()
        ## Position from 'reference' scannable, convert to quantity and get a doubvle
        refValue = self.getReferencePosAsDouble()
        #print refPos, refValue
        return QuantityFactory.createFromObject(refValue-inputValue, self.units);

    # Get the current position of the reference scannable as a double
    def getReferencePosAsDouble(self):
        refPos = self.refScannable.getPosition()
        return QuantityFactory.createFromObject(refPos, self.units).getValue()
    
    # Convert the given 'target' absolute position to one relative to the reference scannable
    def toSource(self, target):
        # print "To source : target = "+target.toString()
        targetValue = QuantityFactory.createFromObject(target, self.units).getValue();
        refValue = self.getReferencePosAsDouble()
        return QuantityFactory.createFromObject(refValue-targetValue, self.units);
    
    def setUnits(self, units):
        self.units = units
    
converterRelativeToBragg = RelativePositionConverter()
converterRelativeToBragg.setReferenceScannable(bragg1)

energyTransfer = ConvertorScannable();
energyTransfer.setName("energyTransfer")
energyTransfer.setOutputFormat(XESEnergy.getOutputFormat())
energyTransfer.setScannable(XESEnergy)
energyTransfer.setConvertor(converterRelativeToBragg)
energyTransfer.configure()
