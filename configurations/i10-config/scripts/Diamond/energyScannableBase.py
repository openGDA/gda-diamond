"""
Energy scannable base class
For use with I10 insertion device scannables on GDA at Diamond Light Source
"""
from gda.device.scannable import ScannableMotionBase

class EnergyScannableBase(ScannableMotionBase):
    
    def __init__(self, name, id_gap_scannable,
                 id_rowphase1_scannable, id_rowphase2_scannable,
                 id_rowphase3_scannable, id_rowphase4_scannable,
                 id_jawphase_scannable, pgm_energy_scannable):
        
        self.name = name
        self.id_gap = id_gap_scannable
        self.id_rowphase1 = id_rowphase1_scannable
        self.id_rowphase2 = id_rowphase2_scannable
        self.id_rowphase3 = id_rowphase3_scannable
        self.id_rowphase4 = id_rowphase4_scannable
        self.id_jawphase = id_jawphase_scannable
        self.pgm_energy = pgm_energy_scannable

        self.inputNames = [name]
        self.extraNames = self.getExtraNames()
        self.outputFormat = self.getOutputFormat()
        self.last_energy_eV = 0
        
        self.verbose = False
        self.concurrentRowphaseMoves=False

    def __str__(self):
        format=", ".join([ a + "=" + b for (a,b) in zip(
              self.inputNames+self.extraNames,self.outputFormat)])
        return format % self.getPosition()

    def __repr__(self):
        format = "EnergyScannable(%r, %r, %r, %r, %r, %r, %r, %r, gap=%r, " + \
            "rowphase1=%r, rowphase2=%r, rowphase3=%r, rowphase4=%r, " + \
            "jawphase_poly=%r)"
        return format % (self.name, self.id_gap.name,
            self.id_rowphase1.name, self.id_rowphase2.name,
            self.id_rowphase3.name, self.id_rowphase4.name,
            self.id_jawphase.name, self.pgm_energy.name)

    def isBusy(self):
        return (self.id_gap.isBusy() or 
                self.id_rowphase1.isBusy() or
                self.id_rowphase2.isBusy() or
                self.id_rowphase3.isBusy() or
                self.id_rowphase4.isBusy() or
                self.id_jawphase.isBusy() or 
                self.pgm_energy.isBusy() )

    def moveToMayWait(self, scannable, position, wait):
        from time import sleep
        
        if self.verbose:
            print "Moving %s to %f" % (scannable.name, position)
            
        scannable.asynchronousMoveTo(position)
        
        if wait:
            while scannable.isBusy():
                sleep(0.1)

    def moveTwoToSync(self, scannable1, position1, scannable2, position2):
        from time import sleep
        
        if self.verbose:
            print "Moving %s to %f & %s to %f " % (
                scannable1.name, position1, scannable2.name, position2)
            
        scannable1.asynchronousMoveTo(position1)
        scannable2.asynchronousMoveTo(position2)
        
        while scannable1.isBusy() or scannable2.isBusy():
            sleep(0.1)

    def idMotorsAsynchronousMoveTo(self, idPosition, energy_eV, set_pgm_energy=True):
        self.last_energy_eV = 0

        self.moveToMayWait(self.id_gap, idPosition.gap, wait=True)
        if self.concurrentRowphaseMoves:
            self.moveTwoToSync(self.id_rowphase1, idPosition.rowphase1, 
                               self.id_rowphase3, idPosition.rowphase3)
            self.moveTwoToSync(self.id_rowphase2, idPosition.rowphase2,
                               self.id_rowphase4, idPosition.rowphase4)
        else:
            self.moveToMayWait(self.id_rowphase1, idPosition.rowphase1, wait=True)
            self.moveToMayWait(self.id_rowphase2, idPosition.rowphase2, wait=True)
            self.moveToMayWait(self.id_rowphase3, idPosition.rowphase3, wait=True)
            self.moveToMayWait(self.id_rowphase4, idPosition.rowphase4, wait=True)
        self.moveToMayWait(self.id_jawphase, idPosition.jawphase, wait=False)
        
        if set_pgm_energy:
            self.moveToMayWait(self.pgm_energy, energy_eV, wait=False)
        
        self.last_energy_eV = energy_eV

    def getExtraNames(self): 
        return [self.id_gap.name, self.id_rowphase1.name,
                self.id_rowphase2.name, self.id_rowphase3.name,
                self.id_rowphase4.name, self.id_jawphase.name, 
                self.pgm_energy.name, "diff_energy" ]
        
    def getOutputFormat(self):
        return ['%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f']

    def getPosition(self):
        pgm_energy = self.pgm_energy.getPosition()
        diff = self.last_energy_eV - pgm_energy
        return (self.last_energy_eV, self.id_gap.getPosition(),
                self.id_rowphase1.getPosition(), self.id_rowphase2.getPosition(),
                self.id_rowphase3.getPosition(), self.id_rowphase4.getPosition(),
                self.id_jawphase.getPosition(), pgm_energy, diff)

    # Derived classes must either implement getIdPosition or override asynchronousMoveTo

    def asynchronousMoveTo(self, energy_eV):
        idPosition = self.getIdPosition(energy_eV)
        self.idMotorsAsynchronousMoveTo(idPosition, energy_eV)
