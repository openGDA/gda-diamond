from gda.exafs.xes import XesUtils

class XESCalculate:
    
    def __init__(self, xes_offsets, material, cut1, cut2, cut3, radius):
        self.xes_offsets = xes_offsets
        self.material=material
        self.cut1=cut1
        self.cut2=cut2
        self.cut3=cut3
        self.radius=radius
    
    """
    Using the given fluorescence energy, assumes that the spectrometer is aligned to that 
    energy, so sets the offsets of all the motors and records the values in the default 
    xml store.
    Next time the GDA starts those offsets will continue to be used.
    """
    def recordFromLive(self, fluo_energy):
        self.applyFromLive(fluo_energy)
        self.xes_offsets.save()
    
    """
    Using the given fluorescence energy, assumes that the spectrometer is aligned to that 
    energy, so sets the offsets of all the motors.
    The offsets are only recorded in the xml file if store is set to True.
    """
    def applyFromLive(self, fluo_energy):
        print "fluo_energy " + str(fluo_energy)
        expectedValuesDict = self.calcFromLive(fluo_energy)
        print expectedValuesDict
        self.xes_offsets.setFromExpectedValues(expectedValuesDict)
    
    """
    Using the given fluorescence energy, assumes that the spectrometer is aligned to that 
    energy, so calculates the expected motor positions.
    Returns a dictionary of spectrometer scannables and expected positions.
    """
    def calcFromLive(self, fluo_energy):
        material_val = self.material()
        cut1_val = int(float(self.cut1()))
        cut2_val = int(float(self.cut2()))
        cut3_val = int(float(self.cut3()))
        cut_values = [cut1_val,cut2_val,cut3_val]
        radius_val = float(self.radius())
        return self.calcFromValues(fluo_energy, material_val, cut_values, radius_val)
    
    """
    Using the given fluorescence energy and crystal parameters, assumes that the spectrometer
    is aligned to that energy, so calculates the expected motor positions.
    Returns a dictionary of spectrometer scannables and expected positions.
    """
    def calcFromValues(self, fluo_energy, material, crystalCut, rowlandRadius):
        xesmaterial = XesUtils.XesMaterial.GERMANIUM
        if material == 'Si':
            xesmaterial = XesUtils.XesMaterial.SILICON
        bragg = XesUtils.getBragg(fluo_energy,xesmaterial,crystalCut)
        # FIXME! XesUtils is returning values the wrong way round!
        det_x_expected = XesUtils.getDx(rowlandRadius,bragg)
        det_y_expected = XesUtils.getDy(rowlandRadius,bragg)
        xtal_x_expected = XesUtils.getL(rowlandRadius,bragg)
        xtalPositions_minus1 = XesUtils.getAdditionalCrystalPositions(rowlandRadius,bragg,-137)
        xtalPositions_central = XesUtils.getAdditionalCrystalPositions(rowlandRadius,bragg,0)
        xtalPositions_plus1 = XesUtils.getAdditionalCrystalPositions(rowlandRadius,bragg,137)
        analyserAngle = XesUtils.getCrystalRotation(bragg) * 2
        expected_values = {'xtal_minus1_x' : xtalPositions_minus1[0],\
        'xtal_minus1_y' :  xtalPositions_minus1[1],\
        'xtal_minus1_rot' : xtalPositions_minus1[2],\
        'xtal_minus1_pitch' : xtalPositions_minus1[3],\
        'xtal_central_y' : xtalPositions_central[1],\
        'xtal_central_rot' : xtalPositions_central[2],\
        'xtal_central_pitch' : xtalPositions_central[3],\
        'xtal_plus1_x' : xtalPositions_plus1[0],\
        'xtal_plus1_y' : xtalPositions_plus1[1],\
        'xtal_plus1_rot' : xtalPositions_plus1[2],\
        'xtal_plus1_pitch' : xtalPositions_plus1[3],\
        'det_x': det_x_expected, \
        'det_y' : det_y_expected,\
        'det_rot' : analyserAngle,\
        'xtal_x' : xtal_x_expected}
        return expected_values
    
        #Using the supplied dictionary of expected motor positions, this calculates the required offsets and sets them on the GDA Scannables.
    def setFromExpectedValues(self, expectedValuesDict):
        self._check_name_exists(expectedValuesDict)
        offsetsDict = {}
        for name in expectedValuesDict.keys():
            expected = expectedValuesDict[name]
            print "\t %s %f" % (name,expected)
            newOffset = self._calcOffset(name,expected)
            offsetsDict[name] = newOffset
        print offsetsDict
        self._apply_from_dict(offsetsDict)
        self.save()
        
    def _calcOffset(self, name,expectedReadback):
        scannable = self.spectrometer.getGroupMember(name)
        if scannable == None:
            raise ValueError("scannable '{}' could not be found. Will not apply offsets".format(name))
        readback = scannable()
        currentOffset = scannable.getOffset()
        if currentOffset == None:
            currentOffset = [0]
        currentOffset = currentOffset[0]
        newOffset = expectedReadback - (readback - currentOffset)
        return newOffset
