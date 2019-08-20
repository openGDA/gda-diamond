import sys
from gda.device.scannable import ScannableMotionBase
from gda.device.scannable import ScannableBase
#from math import copysign # when we move to Jython 2.6

resetScannables = False
useCorrection = True

# version 10/12/2018. 

GAPvsEnergy = [[52.5,32.35,37.77,37.8],[56.92,34.73,40.38,40.4],[60.65,37,42.9,42.95],[63.84,39,45.03,45.08],[66.625,40.75,46.95,47.03],[69.18,42.35,48.67,48.7],[71.5,43.83,50.25,50.29],[73.65,45.19,51.73,51.77],[75.65,46.5,53.1,53.12],[77.55,47.71,54.41,54.43],[79.32,48.87,55.63,55.66],[81.04,49.98,56.8,56.83],[82.88,51.22,58.28,58.28]]

class ZPEnergy(ScannableMotionBase):
   """Binds ZP and OSA to photon energy"""
   def __init__(self, name, scannableZPZ,scannableZPX,scannableZPY,scannableOSAZ,scannableOSAX,scannableOSAY,scannableMj8_Pitch,scannableMj8_Roll,scannableEnergy):
    self.setName(name)
    self.setInputNames([name])
    self.setOutputFormat(["%5.5g"])
    self.ZPZ = scannableZPZ
    self.ZPX = scannableZPX
    self.ZPY = scannableZPY
    self.OSAZ = scannableOSAZ
    self.OSAX = scannableOSAX
    self.OSAY = scannableOSAY
    self.Energy = scannableEnergy
    self.EnergyStep = 160.76286 #micron per eV
    
    self.TuneGap = False
    self.Gap = None
    self.GAPvsEnergy = [[]]
    self.GapEnergyOffset = 40.0
    self.GapEnergyStep = 10.0
    self.Pols = {'LH':0,'LV':1,'CR':2,'CL':3}

    self.useCorrection = False
    self.mX = scannableMj8_Pitch #mirror pitch - steering along X axes, horizontally
    self.mXOffset = 0.0
    self.XStepOffset = 0.0

    self.mY = scannableMj8_Roll #mirror roll - steering along Y axes, vertically
    self.mYOffset = 0.0
    self.YStepOffset = 0.0
    self.GrazingAngleXZ = 2.166 * 3.14159265359 / 180 # grazing angle  in XZ plane
    
    self.isZPE = True
    self.setLevel(7)

   def isBusy(self):
        return self.ZPZ.isBusy() or self.OSAX.isBusy() or self.OSAY.isBusy() or self.Energy.isBusy() or self.ZPX.isBusy() or self.ZPY.isBusy() or self.mX.isBusy() or self.mY.isBusy()

   def getPosition(self):
        return self.Energy.getPosition()

   def asynchronousMoveTo(self,newEnergy):
       (ShiftZP, ShiftOSA, posGap, Error) = self.getOpticsPosition(newEnergy)
       if (Error == 0):
            CurrentZP = self.ZPZ.getPosition()
            CurrentOSA = self.OSAZ.getPosition()
            if (ShiftZP >= 0):
                self.OSAZ.asynchronousMoveTo(CurrentOSA + ShiftOSA)
                self.ZPZ.asynchronousMoveTo(CurrentZP + ShiftZP)
            else:
                self.ZPZ.asynchronousMoveTo(CurrentZP + ShiftZP)
                self.OSAZ.asynchronousMoveTo(CurrentOSA + ShiftOSA)
            
            if(self.getUseCorrection()):
                ZPXold = self.ZPX.getPosition()
                ZPYold = self.ZPY.getPosition()
                OSAXold = self.OSAX.getPosition()
                OSAYold = self.OSAY.getPosition()
                shiftX = self.getShiftX(ShiftZP)
                self.ZPX.asynchronousMoveTo(ZPXold + shiftX)
                self.OSAX.asynchronousMoveTo(OSAXold + shiftX)
                shiftY = self.getShiftY(ShiftZP)
                self.ZPY.asynchronousMoveTo(ZPYold + shiftY)
                self.OSAY.asynchronousMoveTo(OSAYold + shiftY)

            self.Energy.asynchronousMoveTo(newEnergy)
            
            if (self.TuneGap):
                while (self.Energy.isBusy()):
                    sleep(0.5)
                self.Gap.asynchronousMoveTo(posGap)
            sleep(0.5)

   def getOpticsPosition(self,newEnergy):
        Error = 0
        currentEnergy = self.Energy.getPosition()
        ZPShift = self.EnergyStep * (currentEnergy - float(newEnergy))
        OSAShift = 0
        index = (float(newEnergy) - self.GapEnergyOffset) / self.GapEnergyStep
        Int  = int(index)
        Frac = index - Int
        if (self.TuneGap): 
            posPol = polarisation.getPosition()
            PolInd = int(float(self.Pols[posPol]))
            if PolInd in (0,1,2,3):
                posGap = self.GAPvsEnergy[Int][PolInd] + (self.GAPvsEnergy[Int+1][PolInd] - self.GAPvsEnergy[Int][PolInd]) * Frac
            else:
                posGap = rawid_gap.getPosition()
                Error = 1
        else:
            posGap = rawid_gap.getPosition()
        return (ZPShift, OSAShift, posGap, Error)

   def getUseCorrection(self):
       return self.useCorrection
   
   def setUseCorrection(self, useCorrection):
       self.useCorrection = useCorrection

   def getShiftX(self,shiftZ):
       XBeamAngle = 1e-6 * self.mX.getPosition() #mj7 pitch, in radians
       return (self.XStepOffset + 2 * (XBeamAngle - self.mXOffset)) * shiftZ
       
   def getShiftY(self,shiftZ):
       YBeamAngle = 1e-6 * self.mY.getPosition() #mj7 roll, in radians
       return (self.YStepOffset + 2 * (YBeamAngle - self.mYOffset) * self.GrazingAngleXZ) * shiftZ
       
   def getXStepOffset(self):
        return self.XStepOffset
   def getmXOffset(self):
        return self.mXOffset

   def getYStepOffset(self):
        return self.YStepOffset
   def getmYOffset(self):
        return self.mYOffset
        
   def setXOffsets(self, XStepOffset, mXOffset):
        self.XStepOffset = XStepOffset
        self.mXoffset = mXOffset

   def setYOffsets(self, YStepOffset, mYOffset):
        self.YStepOffset = YStepOffset
        self.mYoffset = mYOffset

   def getXOffsets(self):
        return [self.XStepOffset,self.mXOffset]

   def getYOffsets(self):
        return [self.YStepOffset,self.mYOffset]

   def getEnergyStep(self):
        return self.EnergyStep

   def setEnergyStep(self, newStep):
        self.EnergyStep = newStep

   def getTuneGap(self):
        return self.TuneGap

   def setTuneGap(self, TuneGap):
        self.TuneGap = TuneGap

   def setGap(self, scannableGap):
        self.Gap = scannableGap

   def setGAPvsEnergy(self, GAPvsEnergy):
        self.GAPvsEnergy = GAPvsEnergy

   def getGAPvsEnergy(self):
        return self.GAPvsEnergy

   def getGapEnergyOffset(self):
        return self.EnergyOffset

   def setGapEnergyOffset(self, newOffset):
        self.EnergyOffset = newOffset

   def setGapEnergyStep(self, newStep):
       self.GapEnergyStep = newStep
    
   def getGapEnergyStep(self):
       return self.GapEnergyStep
       
   def isZPE(self):
       return self.isZPE

   def getZPE(self):
       return self.isZPE

   def setZPE(self, ZPE):
       self.isZPE = ZPE
       
   def setMacroMirror(self, MaMState):
        if(self.isZPE() != MaMState):
            return 1
        else:
            return 1


class DA30_z(ScannableMotionBase):
   """Binds """
   def __init__(self, name, Master, Slave1, Slave2):
    self.setName(name)
    self.setInputNames([name])
    self.setOutputFormat(["%5.5g"])
    self.Master = Master
    self.Slave1 = Slave1
    self.Slave2 = Slave2
    self.setLevel(7)
    
   def isBusy(self):
    return self.Master.isBusy() or self.Slave1.isBusy() or self.Slave2.isBusy()

   def getPosition(self):
    return self.Master.getPosition()

   def asynchronousMoveTo(self,newPosition):
    Delta = newPosition - self.Master.getPosition()
    if(abs(Delta)<500.001):
        Slave1newPosition = self.Slave1.getPosition() + Delta
        Slave2newPosition = self.Slave2.getPosition() + Delta
        self.Master.asynchronousMoveTo(newPosition)
        self.Slave1.asynchronousMoveTo(Slave1newPosition)
        self.Slave2.asynchronousMoveTo(Slave2newPosition)
        sleep(0.5)
    else:
        print "Please, step smaller than 500 microns"

    
if(resetScannables):
    if 'zpe' in locals(): del zpe
    if 'da30_z' in locals(): del da30_z
    print "Both ZPE scannablesd killed, \"zpe\" and \"da30_z\". Restart the script with \"resetScannables=False\" to re-create them again"
else:
    #zpe = ZPEnergy("zpe",zpz_lut,zpx_lut,zpy_lut,osaz_lut,osax_lut,osay_lut,mj7j8_pitch,mj7j8_roll,energy)
    #da30_z = DA30_z("da30_z",smdefocus,zpz_lut,osaz_lut)
    zpe = ZPEnergy("zpe",zpz,zpx,zpy,osaz,osax,osay,mj7j8_pitch,mj7j8_roll,energy)
    da30_z = DA30_z("da30_z",smdefocus,zpz,osaz)
    if (useCorrection):
        zpe.setUseCorrection(True)
        # 05/07/2017; mj7 pitch = 2867.8 urad; Xstep = 1.3156e-3
        # 12/10/2018; mj7 pitch = 3240.8 urad; Xstep = 3.90247e-3
        # 10/12/2018; mj7_pitch = 3177 urad; Xstep = 
        zpe.mXOffset = 3.177e-3
        zpe.XStepOffset = 0.00406095
        #zpe.setXOffsets(0, 3.177e-3)
        # 05/07/2017; mj7 roll = -577.7 urad; Ystep = 0.97215e-3
        # 12/10/2018; mj7 roll = 1000 urad; Ystep = 1.59647e-3
        zpe.YStepOffset = 1.59647e-3
        zpe.mYOffset = -1.569e-3
        #zpe.setYOffsets(1.59647e-3, 1e-3)
        
    else:
        zpe.setUseCorrection(False)

    zpe.setGap(rawid_gap)
    zpe.setGAPvsEnergy(GAPvsEnergy)
    zpe.setTuneGap(True)
    zpe.setGapEnergyOffset(39.9)
    zpe.setGapEnergyStep(10.0)
    zpe.setUpperGdaLimits(150.0001)
    zpe.setLowerGdaLimits(59.9999)
    print "ZPE scannables, \"zpe\" and \"da30_z\"created"
