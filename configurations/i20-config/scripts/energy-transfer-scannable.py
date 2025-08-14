from gda.util import QuantityFactory
from gda.device.scannable import ConvertorScannable, ScannableGroupSinglePosition
from gda.util.converters import IQuantityConverter


print("\nRunning 'energy-transfer-scannable.py")
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


class SinglePositionConvertorScannable(ConvertorScannable) :
    """
    Version of the ConvertorScannable class that overrides asynchronousMoveTo and checkPositionValid
    to ensure only single number is passed to underlying functions 
    (ConvertorScannable does not work if passed an array even if it has only 1-element).
    """
    def asynchronousMoveTo(self, demandPos) :
        singlePos = self.getSinglePosition(demandPos)
        super(SinglePositionConvertorScannable, self).asynchronousMoveTo(singlePos)

    # Return first element in demandPosition
    def getSinglePosition(self, demandPos) :
        return ScannableUtils.objectToArray(demandPos)[0]
    
    def checkPositionValid(self, demandPos) :
        singlePos = self.getSinglePosition(demandPos)
        return super(SinglePositionConvertorScannable, self).checkPositionValid(singlePos)

converterRelativeToBragg = RelativePositionConverter()
converterRelativeToBragg.setReferenceScannable(bragg1)

# Reduce the level of the mono scannables. This ensures that they are moved initial
# positions in scans first and are in place *before* energy transfer scannables are positioned.
bragg1.setLevel(4)
bragg1WithOffset.setLevel(4)

def createEnergyTransferScannable(sourceScn, name):
    energyTransfer = SinglePositionConvertorScannable();
    energyTransfer.setName(name)
    energyTransfer.setOutputFormat(sourceScn.getOutputFormat())
    energyTransfer.setScannable(sourceScn)
    energyTransfer.setConvertor(converterRelativeToBragg)
    energyTransfer.configure()
    return energyTransfer

print("Creating energy transfer scannables : XESEnergyTransferLower, XESEnergyTransferUpper, XESEnergyTransferBoth, XESEnergyTransferGroup")

XESEnergyTransferLower = createEnergyTransferScannable(XESEnergyLower, "XESEnergyTransferLower");
XESEnergyTransferUpper = createEnergyTransferScannable(XESEnergyUpper, "XESEnergyTransferUpper");

XESEnergyTransferGroup = ScannableGroup()
XESEnergyTransferGroup.setGroupMembers([XESEnergyTransferLower,XESEnergyTransferUpper])
XESEnergyTransferGroup.setName("XESEnergyTransferGroup")
XESEnergyTransferGroup.configure()

XESEnergyTransferBoth = ScannableGroupSinglePosition()
XESEnergyTransferBoth.setGroupMembers([XESEnergyTransferLower,XESEnergyTransferUpper])
XESEnergyTransferBoth.setName("XESEnergyTransferBoth")
XESEnergyTransferBoth.configure()