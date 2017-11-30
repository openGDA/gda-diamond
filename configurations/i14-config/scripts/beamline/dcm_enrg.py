
from math import asin,sin,degrees,radians, cos
from threading import Thread
from gda.device.scannable import ScannableMotionUnitsBase
from gda.analysis.datastructure import DataVector
from gda.analysis.numerical.interpolation import Interpolator
from gda.jython.commands.ScannableCommands import pos
from Beamline.Utilities.file_io_tools import *
from gda.epics import CAClient
from gda.device.scannable import ScannableStatus
import codecs
import os.path


class DCMpdq(ScannableMotionUnitsBase):
    def __init__(self, name, dcm_bragg, dcm_perp, id_gap,m1_mirror_stripe,m2_mirror_stripe, ringCurrentMonitor):
            self.setName(name);
            self.setInputNames([name])
            self.setExtraNames([])
            self.setOutputFormat(["%5.5g"])

            self.dcm_bragg = dcm_bragg
            self.dcm_perp = dcm_perp
            self.id_gap = id_gap
            self.m1_mirror_stripe = m1_mirror_stripe
            self.m2_mirror_stripe = m2_mirror_stripe
            self.ringCurrentMonitor = ringCurrentMonitor

            # Si 111 spacing at 77K
            self.silicon_d111 = 3.134925
            # Conversion factor used in wavelength to keV calculation
            self.wavetokeV=12.39842
            # DCM offset
            self.myoffset = 35.0
            # Min energy for DCM
            self.minEnergy = 4.45
            # Max energ yfor DCM
            self.maxEnergy = 26.0
            # Min gap - just above 5mm
            self.minGap = 5.01
            # Max gap - set to 28mm
            self.maxGap = 28.8
            # Default harmonic is the lowest harmonic = 5
            self.currentharmonic=5
            #self.mirror_stripe_list=[-20.0,0.0,20.0]
            # Variable to control whether to switch harmonics during scans
            # set using get set methods
            self.chan = CAClient()
            # Default mirror stripe is the Rh stripe
            self.current_mirror_stripe="blah"
            self.disableUndulatorHarmonicSwitch = 0
            self.disableMirrorStripeSwitch = 0
            self.disablegap=0
            self.disableDCMFeedback=1
            self.disableMirrorFeedback=1
            self.selectUndulatorHarmonic(self.currentharmonic)
            self.setUserUnits("keV")

    def rawGetPosition(self):
            """
            Return the energy calculated using the current bragg motor position
            """
            return self.calcEnergyFromCurrentBragg()

    def rawAsynchronousMoveTo(self,position):
        """
        Move bragg, perp and id gap to correct values for demanded energy position
        """
        rollmove=False
        # Don't allow a stupid move
        if(position < self.minEnergy or position > self.maxEnergy):
            print "Energy out of range"
            self.notifyIObservers(self, ScannableStatus(self.getName(), ScannableStatus.IDLE))
            return
        else:
            # if harmonic switching is off keep the current harmonic and just interpolate the gap
            # else select the best harmonic for this energy
            if(self.disableUndulatorHarmonicSwitch):
                best_harmonic = self.currentharmonic
            else:
                best_harmonic = self.selectBestUndulatorHarmonic(position)

            if(self.disableMirrorStripeSwitch):
                best_stripe = self.current_mirror_stripe
            else:
                best_stripe = self.selectBestMirrorStripe(position)
                self.current_mirror_stripe = self.determine_current_stripe()

            # If you've updated the harmonic read in the correct lookuptable
            if(best_harmonic != self.currentharmonic):
                #print "selecting harmonic :",best_harmonic
                self.selectUndulatorHarmonic(best_harmonic)
                self.currentharmonic=best_harmonic

            # If you're moving from Rh or Pt to Si
            # then move the DCM first then translate stripe
            # If you're moving from Si to Rh or Pt
            # move the mirror stripe, then the DCM
            moveDCMFirst=True
            moveMirror=False
            #print best_stripe,self.current_mirror_stripe
            if(best_stripe != self.current_mirror_stripe):
                moveMirror=True
                if(best_stripe == "Si"):
                    moveDCMFirst=True
                else:
                    moveDCMFirst=False
            else:
                moveMirror=False

            bragg,perp=self.calcBraggandPerp(position)
            newid_gap = self.lookup_gap(position)

            moveThread = Thread(target = self.doMove, args=(moveDCMFirst, bragg, perp, newid_gap, moveMirror, best_stripe))
            moveThread.start()


    def doMove(self, moveDCMFirst, bragg, perp, newid_gap, moveMirror, best_stripe):
        self.notifyIObservers(self, ScannableStatus.BUSY)

        if(moveDCMFirst):
            self.moveDcm(bragg, perp, newid_gap)
            self.handleMirrorMove(moveMirror, best_stripe)
        else:
            self.handleMirrorMove(moveMirror, best_stripe)
            self.moveDcm(bragg, perp, newid_gap)

        self.notifyIObservers(self, ScannableStatus.IDLE)


    def moveDcm(self, bragg, perp, newid_gap):
        # Look up the bragg, perp and id- linear interpolation of lookuptables
        #print "Moving DCM to :", bragg
        if(self.disablegap or self.ringCurrentMonitor.getPosition() < 10):
            print "Not moving id gap"
            pos(self.dcm_bragg, bragg, self.dcm_perp, perp)
        else:
            print "Moving id gap"
            pos(self.dcm_bragg, bragg, self.dcm_perp, perp, self.id_gap, newid_gap)
        #print "DCM move completed"


    def handleMirrorMove(self, moveMirror, best_stripe):
        if(moveMirror):
            self.moveMirrorStripe(best_stripe)
        else:
            print("Keeping mirror stripe as :", self.current_mirror_stripe)


    def moveMirrorStripe(self, best_stripe):
        self.notifyIObservers(self, ScannableStatus(self.getName(), ScannableStatus.BUSY))
        # Turn off DCM feedback - we're assuming the DCM crystals are parallel
        #self.disableDCMFeedback()
        # Move the mirror stripes before a gap change
        print("Moving mirror stripe to :", best_stripe)
        pos(self.m1_mirror_stripe,best_stripe,self.m2_mirror_stripe,best_stripe)
        print("Mirror stripe change completed")
        self.current_mirror_stripe=best_stripe
        #
        # Now optimize the mirror angle for any offset
        # Turn on mirror feedback, settle, then turn off
        #self.runMirrorFeedback()
        # Turn off mirror feedback
        # Turn on DCM feedback
        #self.enableDCMFeedback()


    def rawIsBusy(self):
        # Always test these motors
        if self.dcm_bragg.isBusy() \
            or self.dcm_perp.isBusy() \
            or self.m1_mirror_stripe.isBusy() \
            or self.m2_mirror_stripe.isBusy():
            return True

        # Test id gap only if we can move it
        # It may appear to be busy if it cannot be moved
        if self.ringCurrentMonitor.getPosition() > 10 and self.id_gap.isBusy():
            return True

        return False

    def calcBraggandPerp(self,energy):
        """
        Calculate  the bragg and perp for a given energy (keV)
        """
        wavelength = self.wavetokeV/energy
        bragg_rad  = asin(wavelength/(2*self.silicon_d111))
        bragg_deg  = degrees(bragg_rad)
        perp = (self.myoffset/sin(2.*bragg_rad))*sin(bragg_rad)
        #perp = (17.533/cos(bragg_rad))-0.1904
     #   perp = (14.048/cos(bragg_rad))+2.9881
      #  perp = (19.171/cos(bragg_rad))-2.3326

        #perp = (17.797/cos(bragg_rad))-0.3138
        #perp = (16.193/cos(bragg_rad))+1.19
        return bragg_deg,perp

    def calcEnergyFromCurrentBragg(self):
        """
        Calculate the energy given the current bragg motor position
        """
        bragg = self.dcm_bragg.getPosition()
        bragg_rad = radians(bragg)
        energy  = self.wavetokeV/(2*self.silicon_d111*sin(bragg_rad))
        return energy

    def calcEnergyFromBragg(self,bragg):
        """
        Calculate the energy given a bragg position (degrees)
        Just a tool for calculation...

        """
        bragg_rad = radians(bragg)
        energy  = self.wavetokeV/(2*self.silicon_d111*sin(bragg_rad))
        return energy

    def determine_current_stripe(self):
        stripe = "Rh"
        m2_inpos= float(self.chan.caget("BL14I-OP-MIRR-02:Y:MP:INPOS"))
        m1_inpos= float(self.chan.caget("BL14I-OP-MIRR-01:Y:MP:INPOS"))
        # logical and doesn't work ...something odd so rewrite to check == 1 ????
        #inpos = (m2_inpos and m1_inpos)
        stripesame = (self.m2_mirror_stripe.getPosition() == self.m1_mirror_stripe.getPosition())
        if(stripesame and m2_inpos==1.0 and m1_inpos ==1.0):
                stripe=self.m2_mirror_stripe.getPosition()
        else:
             stripe="fixme"
        return stripe

    def disableHarmonicSwitching(self):
        self.disableUndulatorHarmonicSwitch = 145

    def enableHarmonicSwitching(self):
        self.disableUndulatorHarmonicSwitch = 0

    def disableMirrorStripeSwitching(self):
        self.disableMirrorStripeSwitch = 145

    def enableMirrorStripeSwitching(self):
        self.disableMirrorStripeSwitch = 0

    def disableSwitching(self):
        self.disableUndulatorHarmonicSwitch = 145
        self.disableMirrorStripeSwitch = 145

    def enableSwitching(self):
        self.disableUndulatorHarmonicSwitch = 0
        self.disableMirrorStripeSwitch = 0
        self.disablegap = 0

    def disableUndulator(self):
        self.disablegap = 1

    def enableUndulator(self):
        self.disablegap = 0

 #   def enableDCMFeedback(self):
 #       self.disableDCMFeedback=1
  #      self.turnonDCMFeedback()

#    def disableDCMFeedback(self):
#        self.disableDCMFeedback=0
 #       self.turnoffDCMFeedback()

    def runMirrorFeedback(self):
        """
        Enable feedback on M2 mirror piezo and wait until it settles...
        If the shutters are closed then don't bother switching it on..
        """
        if(self.chan.caget("BL14I-PS-SHTR-03:STA")=="Open"):
            self.chan.caput("BL14I-DI-IONC-01:FB.FBON",1)
            setpt = float(self.chan.caget("BL14I-DI-IONC-01:FB.VAL"))
            while(self.chan.caget("BL14I-DI-IONC-01:FB.ERR")>0.001):
                  sleep(5)
            self.chan.caput("BL14I-DI-IONC-01:FB.FBON",0)


    def turnonDCMFeedback(self):
        """
        Turn on the DCM feedback and wait for it to settle

        """
        self.chan.caput("BL14I-DI-BEST-01:Login:UserPass","admin:WeAreTheBest")
        # Turn back on the FPGA in case you have been using manual piezo control
        self.chan.caput("BL14I-DI-BEST-01:PreDAC0:OutMux",1)
        # Turn back on the FPGA
        self.chan.caput("BL14I-DI-BEST-01:PID:Enable",1)
        # Tuned timing to judge how long it takes to settle...or we could read the error off...
        sleep(10)

    def turnoffDCMFeedback(self):
        """
        Turn on the DCM feedback and wait for it to settle

        """
        self.chan.caput("BL14I-DI-BEST-01:Login:UserPass","admin:WeAreTheBest")
        # Turn back off the FPGA and enable manual piezo control
        self.chan.caput("BL14I-DI-BEST-01:PreDAC0:OutMux",1)
        self.chan.caput("BL14I-DI-BEST-01:PID:Enable",0)


    def read_lookuptable(self):
        """
        Read in a harmonic lookup table
        """
        # use codecs as the first line of the files sometimes have
        # extra characters depending on what you edited or saved the harmonic table in...
        #
        f = codecs.open(self.lookuptablefile,"r","utf-8-sig")
        AA=f.readlines()
        f.close()
        for i in range(len(AA)):
            a,b,c,d = stringToFloatList(AA[i])
            self.energyset.add(a[0])
            self.braggset.add(a[1])
            self.gapset.add(a[2])
#===============================================================================
#
#     def read_roll_lookuptable(self):
#         rollfilename = "/dls_sw/i14/scripts/Harmonics/roll_lookup.txt"
#         f=open(rollfilename)
#         AA=f.readlines()
#         f.close()
#         rolldict={}
#         for i in range(len(AA)):
#             a,b = stringToFloatList(AA[i])[0]
#             rolldict[a]=b
#         return rolldict
#===============================================================================

    def lookup_gap(self,energy):
        """
        For a given energy lookup the gap needed
        At the moment we'll use energy but bragg may be better at a later date
        """
        newgap= Interpolator.linearInterpolatedPoint(self.energyset, self.gapset, energy)
        if(newgap < self.minGap):
            print "interpolated gap too low, ", newgap
            return self.minGap
        elif(newgap > self.maxGap):
            print "interpolated gap too high, ", newgap
            return self.maxGap
        else:
            #print 'new interpolated gap',newgap
            return newgap

#    def lookup_pitch(self,bragg):
#        return Interpolator.polyInterpolatedPoint(self.braggset, self.pitchset, bragg, 3)[0]

#    def lookup_roll(self,bragg):
#        return Interpolator.polyInterpolatedPoint(self.braggset, self.rollset, bragg, 3)[0]

    def reset_lookuptable(self):
        """
        Reset to clear before loading new harmonic data
        """
        self.braggset=DataVector([])
        self.energyset=DataVector([])
        self.gapset=DataVector([])
        self.read_lookuptable()

    def setLookupTable(self,filename):
        """
        Define a lookuptable to use
        """
        self.lookuptablefile=filename
        self.reset_lookuptable()

    def selectBestUndulatorHarmonic(self,energy):
        """
        For a given energy which harmonic should I use...
        Randomly set by PQ to keep the gaps > 5.8mm for now
        """
        if(energy >self.minEnergy and energy < 7.2):
            besth = 5
        elif(energy >=7.2 and energy < 10.1):
            besth = 7
        elif(energy >=10.1 and energy < 13.1):
            besth = 9
        elif(energy >=13.1 and energy < 15.8):
            besth = 11
        elif(energy >=15.8 and energy < 18.8):
            besth = 13
        elif(energy >=18.8 and energy < 22.8):
            besth = 15
        elif(energy >=22.8 and energy < 26.5):
            besth = 17
        else:
            besth=5
        #print "Best harmonic for this energy:",besth
        return besth

    def selectBestMirrorStripe(self,energy):
        """
        For a given energy which harmonic should I use...
        Randomly set by PQ to keep the gaps > 5.8mm for now
        """
        mirror_stripes = ["Si","Rh","Pt"]
        if(energy >self.minEnergy and energy < 10.5):
            best_stripe = "Si"
        elif(energy >=10.5 and energy < 21):
            best_stripe = "Rh"
        elif(energy >=21 ):
            best_stripe = "Pt"
        else:
            best_stripe="Rh"
        #print "Best mirror stripe for this energy:",mirror_stripes[best_stripe]
        return best_stripe


    def selectUndulatorHarmonic(self,harmonic):
        """
        Link to the harmonic files
        These are tab separated lists of energy(keV), bragg(deg), gap(mm)

        """
        #print "harmonic selected:",harmonic
        #harmonics_dir = os.path.dirname(os.path.realpath(__file__)) + '/../harmonics/'
        harmonics_dir = '/dls_sw/i14/scripts/Beamline/MotionsAndDetectors/harmonics/'
        if(harmonic==5):
            self.setLookupTable(harmonics_dir + 'harmonic5_20160429.txt')
        elif(harmonic==7):
            self.setLookupTable(harmonics_dir + 'harmonic7_20160429.txt')
        elif(harmonic==9):
            self.setLookupTable(harmonics_dir + 'harmonic9_20160429.txt')
        elif(harmonic==11):
            self.setLookupTable(harmonics_dir + 'harmonic11_20160429.txt')
        elif(harmonic==13):
            self.setLookupTable(harmonics_dir + 'harmonic13_20160429.txt')
        elif(harmonic==15):
            self.setLookupTable(harmonics_dir + 'harmonic15_20160429.txt')
        elif(harmonic==17):
            self.setLookupTable(harmonics_dir + 'harmonic17_20160429.txt')

        else:
            print 'Cannot find a match for ',harmonic

