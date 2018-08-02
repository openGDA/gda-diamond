from gda.device.scannable import ScannableMotionBase
from gda.device.scannable import ScannableBase
#from math import copysign # when we move to Jython 2.6

# pseudo code for pgm deflector (grating/mirror) with backlash motion 
# to position deflector at target position whith limit-fork centered around it
# deflector mirror BL05I-OP-PGM:GRT
# deflector mirror BL05I-OP-PGM:MIR
# limit fork motor
#import java

def cpysign(a,b):  # replace with copysign when we move to Jython 2.6
    if (b<0): 
        return -1*a
    else:
        return a


class pgm_trans_backlash(ScannableMotionBase): # instantiate once for grating and once for mirror 

   def __init__(self, name, limitForkMotor, backlash=1.00):
    self.setName(name)
    self.setInputNames([name])
    self.setOutputFormat(["%5.5g"])
    # self.setLevel(7)  

    self.scannable = limitForkMotor # i.e. BL05I-OP-PGM-01:GRT:X  or BL05I-OP-PGM-01:MIR:X  or
    # self.scannable.configure() # not needed?: limitForkMotor already configured
    
    # backlash is the Absolute value of the gap, on either side, between the deflector and the fork, when the deflector and fork are centred on each other
    self.backlash       = backlash  

    # could calculate backlash based on getting the width of the detector between the fork, and the size of the gap between the two fork prongs 
    #self.deflectorWidth = 3  # mm 
    #self.forkWidth      = 5  # mm
    #self.backlash      = (self.forkWidth - self.deflectorWidth)/2.0 (5-3)/2=1    # gap is half the difference between the "fork" gap and the deflector between the gap 

    self.isBusyFlg      = False
  

   def isBusy(self):
    return self.isBusyFlg

   def getPosition(self):
       return self.scannable.getPosition()

   def asynchronousMoveTo(self, new_position):
       self.isBusyFlg = True
       cur_position = self.getPosition()
       # bcklsh = cpysign(self.backlash - (self.deflectorWidth/2.0), new_position - cur_position)
       bcklsh = cpysign(self.backlash, new_position - cur_position)
       self.scannable.moveTo(new_position + bcklsh)  # move the fork (e.g. 1mm) beyond target, so the deflector is nudged to the desired position
       pos2 = self.getPosition()
       self.scannable.moveTo(new_position)           # move the fork (e.g. 1mm) back so, it too is in target position, centred on the deflector 
       pos3 = self.getPosition()
       print self.getName(), "BL=", bcklsh, ", pos1=", cur_position, ", pos2=", pos2, ", pos3=", pos3
       self.isBusyFlg = False
    
   def centreOnDeflector(): # TBD: if deflector and fork are do not have their translational centres aligned, invoke this to align them
        # 1 move for until limit switch is touched
        # 2 moved back by gave backlash gap
        pass

#pgm_gtrans_bl = pgm_trans_backlash("pgm_gtrans_bl", pgm_gtrans, backlash=1.00)       
#pgm_mtrans_bl = pgm_trans_backlash("pgm_mtrans_bl", pgm_mtrans, backlash=1.00)       

#1)
# scan pgm_gtrans_bl 1 13 4
# scan pgm_gtrans_bl 1 13 4 showtime
#
#for displ in range(displ_start, displ_end, dispStep):
#   pos pgm_gtrans_bl # include revision by 1mm
#   pos energy enStart
#   pos pgm_energy enStart -1e-3
#   print "PGM translation", displ
#   scan energy beamCur 




pgm_gtrans_bl = pgm_trans_backlash("pgm_gtrans_bl",pgm_gtrans,backlash = 1.00)
pgm_mtrans_bl = pgm_trans_backlash("pgm_mtrans_bl",pgm_mtrans,backlash = 1.00)
