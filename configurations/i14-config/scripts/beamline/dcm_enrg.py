
from math import asin,sin,degrees,radians
from gda.device.scannable import PseudoDevice
from gda.analysis.datastructure import DataVector
from gda.analysis.numerical.interpolation import Interpolator
from gda.jython.commands.ScannableCommands import pos
import codecs
import os.path
#
# Temporary script...to be replaced by comboDCM GDA motor at some point
#
#

def isNumber(inputvalue):
    """ Check if a string is a number
        The method tries to perform a float conversion
        on the input. If this throws an exception, the exception is
        caught and the input is identified as not a number.
        Ugly but effective..
        Input  : String
        Output : True or False            
    """      
    result=False
    try:
        float(inputvalue)
        result=True
    except:
            result=False
    return result
    
def isColumnData(input_string):
    """
    tests if string contains numerical data
    returns true if there are more than 2 floats in the string 
    and at most one word in the string
    
    Input: input_string
    Output: boolean: Is column data ?
            number of floating data points in the string

    """
    isdata = False
    # Convert string to list of floats and strings
    floats,strings,ifloats,istrings=stringToFloatList(input_string)
    # How many floats and strings do we have
    numberOfFColumns=len(floats)
    numberOfSColumns=len(strings)
    # data needs to have at least two columns and more floats than strings
    if (numberOfFColumns >= 2 and numberOfSColumns<=1):
        isdata = True
    return isdata,numberOfFColumns,numberOfSColumns

def stringToFloatList(input_string):
    """
    
    Method takes a string input and splits it up into numbers and strings.
    The method was for use with file io operations on ascii data.
    The input string is converted to a list by removing commas and using
    the python split method. Each element of the list 
    is checked with isNumber method. The numbers and strings split 
    into seperate lists and returns
    
    Input: string
    Output : float data list, string data list, index of floats in original 
    list, index of strings in original list
    
    """
    line=input_string.replace(',', ' ')
    line=line.strip()
    # split it up
    data = line.split()
    returnData=[]
    returnStrings=[]
    indexOfFloats=[]
    indexOfStrings=[]
    myindex=0
    for x in data:
        if(isNumber(x)):
            indexOfFloats.append(myindex)
            returnData.append(float(x))
        else:
            indexOfStrings.append(myindex)
            returnStrings.append(x)
        myindex=myindex+1
    return returnData,returnStrings,indexOfFloats,indexOfStrings


class DCMpdq(PseudoDevice):
    def __init__(self, name, dcm_bragg, dcm_perp, id_gap):
            self.setName(name);
            self.setInputNames([name])
            self.setExtraNames([])
            self.setOutputFormat(["%5.5g"])
            
            self.dcm_bragg = dcm_bragg
            self.dcm_perp = dcm_perp
            self.id_gap = id_gap

            # Si 111 spacing at 77K
            self.silicon_d111 = 3.134925
            # Conversion factor used in wavelength to keV calculation
            self.wavetokeV=12.39842
            # DCM offset
            self.myoffset = 35.0
            # Min energy for DCM
            self.minEnergy = 4.8
            # Max energ yfor DCM
            self.maxEnergy = 26.0
            # Min gap - just above 5mm
            self.minGap = 5.01
            # Max gap - set to 28mm
            self.maxGap = 28.8
            # Default harmonic is the lowest harmonic = 5
            self.currentharmonic=5
            # Position busy
            self.iambusy = 0
            # Variable to control whether to switch harmonics during scans
            # set using get set methods
            self.disableHarmonicSwitch = 0
            self.selectHarmonic(self.currentharmonic)
            
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
                self.iambusy = 0
                return
            else:
                # if harmonic switching is off keep the current harmonic and just interpolate the gap
                # else select the best harmonic for this energy
                if(self.disableHarmonicSwitch):
                    best_harmonic = self.currentharmonic
                else:
                    best_harmonic = self.selectBestHarmonic(position)
                # If you've updated the harmonic read in the correct lookuptable
                if(best_harmonic != self.currentharmonic):
                    print "selecting harmonic :",best_harmonic
                    self.selectHarmonic(best_harmonic)
                    #self.rolldict = self.read_roll_lookuptable()
                    #rollmove=True
                    self.currentharmonic=best_harmonic
                self.iambusy = 1
                # Look up the bragg, perp and id- linear interpolation of lookuptables
                bragg,perp=self.calcBraggandPerp(position)
                newid_gap = self.lookup_gap(position)
                #newroll =  self.rolldict[self.currentharmonic]
                #if(rollmove):
                #    pos dcm_bragg bragg dcm_perp perp id_gap newid_gap dcm_roll newroll
                #else:
                #    pos dcm_bragg bragg dcm_perp perp id_gap newid_gap
                # Moves bragg, perp and gap together to new positions
                pos(self.dcm_bragg, bragg, self.dcm_perp, perp, self.id_gap, newid_gap)
                self.iambusy = 0

    def rawIsBusy(self):
            return self.iambusy
        
    def calcBraggandPerp(self,energy):
        """
        Calculate  the bragg and perp for a given energy (keV)
        """
        wavelength = self.wavetokeV/energy
        bragg_rad  = asin(wavelength/(2*self.silicon_d111))
        bragg_deg  = degrees(bragg_rad)
        perp = (self.myoffset/sin(2.*bragg_rad))*sin(bragg_rad)
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

        
    def disableHarmonicSwitching(self):
        self.disableHarmonicSwitch = 145

    def enableHarmonicSwitching(self):
        self.disableHarmonicSwitch = 0
                

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
            print 'new interpolated gap',newgap
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

    def selectBestHarmonic(self,energy):
        """
        For a given energy which harmonic should I use...
        Randomly set by PQ to keep the gaps > 5.8mm for now
        """
        if(energy >self.minEnergy and energy < 7.2):
            besth = 5
        elif(energy >=7.2 and energy < 10.1):
            besth = 7
        elif(energy >=10.1 and energy < 13.0):
            besth = 9
        elif(energy >=13.0 and energy < 15.8):
            besth = 11
        elif(energy >=15.8 and energy < 18.8):
            besth = 13
        elif(energy >=18.8 and energy < 22.8):
            besth = 15
        elif(energy >=22.8 and energy < 26.5):
            besth = 17
        else:
            besth=5
        print "Best harmonic for this energy:",besth
        return besth
            
            

    def selectHarmonic(self,harmonic):
        """
        Link to the harmonic files
        These are tab separated lists of energy(keV), bragg(deg), gap(mm)
        
        """
        print "harmonic selected:",harmonic
        harmonics_dir = os.path.dirname(os.path.realpath(__file__)) + '/../harmonics/'
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
        
