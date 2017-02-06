###############################################################################
# This script will be run at the end of the main i15-1 localStation script    #
# immediately before the localStationUser script                              #
#                                                                             #
# Thus it will be run whenever the `reset_namespace` command is run on the    #
# Jython terminal console in GDA, or the gda servers are restarted.           #
#                                                                             #
# CAUTION: Any member of i15 staff may edit this script.                      #
#                                                                             #
#          Things you put in here late at night may affect future user runs.  #
#                                                                             #
#          Any errors will prevent subsequent lines in this script being run. #
#                                                                             #
###############################################################################
print "Running /dls_sw/i15-1/scripts/localStationStaff.py (staff editable)"

# import caput and caget
#try:
#    from gda.epics import CAClient
#    caget = CAClient().caget
#    caput = CAClient().caput
#except:
#    localStation_exception(sys.exc_info(), "failed to load caclient modules")

##########################################################################################################
### EPICS PVs ### EPICS PVs ### EPICS PVs ### EPICS PVs ### EPICS PVs ### EPICS PVs ### EPICS PVs ########
##########################################################################################################
try:
    from gdascripts.pd.epics_pds import DisplayEpicsPVClass
    bpm1statTot = DisplayEpicsPVClass("bpm1statTot", "BL15J-DI-BPM-01:STAT:Total_RBV", "counts", "%.0f")
    bpm1statMean = DisplayEpicsPVClass("bpm1statMean", "BL15J-DI-BPM-01:STAT:MeanValue_RBV", "counts", "%f")
    bpm1statCenX = DisplayEpicsPVClass("bpm1statCenX", "BL15J-DI-BPM-01:STAT:CentroidX_RBV", "pixels", "%.0f")
    bpm1statCenY = DisplayEpicsPVClass("bpm1statCenY", "BL15J-DI-BPM-01:STAT:CentroidY_RBV", "pixels", "%.0f")
    bpm1pySizeX = DisplayEpicsPVClass("bpm1pySizeX", "BL15J-DI-BPM-01:PY:Int1_RBV", "um", "%.0f")
    bpm1pySizeY = DisplayEpicsPVClass("bpm1pySizeY", "BL15J-DI-BPM-01:PY:Int2_RBV", "um", "%.0f")
    bpm1pyCenX = DisplayEpicsPVClass("bpm1pyCenX", "BL15J-DI-BPM-01:PY:Double1_RBV", "mm", "%1.4f")
    bpm1pyCenY = DisplayEpicsPVClass("bpm1pyCenY", "BL15J-DI-BPM-01:PY:Double2_RBV", "mm", "%1.4f")
    bpm2statTot = DisplayEpicsPVClass("bpm2statTot", "BL15J-DI-BPM-02:STAT:Total_RBV", "counts", "%.0f")
    bpm2statMean = DisplayEpicsPVClass("bpm2statMean", "BL15J-DI-BPM-02:STAT:MeanValue_RBV", "counts", "%f")
    bpm2statCenX = DisplayEpicsPVClass("bpm2statCenX", "BL15J-DI-BPM-02:STAT:CentroidX_RBV", "pixels", "%.0f")
    bpm2statCenY = DisplayEpicsPVClass("bpm2statCenY", "BL15J-DI-BPM-02:STAT:CentroidY_RBV", "pixels", "%.0f")
    bpm2pySizeX = DisplayEpicsPVClass("bpm2pySizeX", "BL15J-DI-BPM-02:PY:Int1_RBV", "um", "%.0f")
    bpm2pySizeY = DisplayEpicsPVClass("bpm2pySizeY", "BL15J-DI-BPM-02:PY:Int2_RBV", "um", "%.0f")
    bpm2pyCenX = DisplayEpicsPVClass("bpm2pyCenX", "BL15J-DI-BPM-02:PY:Double1_RBV", "mm", "%1.4f")
    bpm2pyCenY = DisplayEpicsPVClass("bpm2pyCenY", "BL15J-DI-BPM-02:PY:Double2_RBV", "mm", "%1.4f")
    eyestatTot = DisplayEpicsPVClass("eyestatTot", "BL15J-DI-EYE-01:STAT:Total_RBV", "counts", "%.0f")
    eyestatMean = DisplayEpicsPVClass("eyestatMean", "BL15J-DI-EYE-01:STAT:MeanValue_RBV", "counts", "%f")
    eyestatCenX = DisplayEpicsPVClass("eyestatCenX", "BL15J-DI-EYE-01:STAT:CentroidX_RBV", "pixels", "%.0f")
    eyestatCenY = DisplayEpicsPVClass("eyestatCenY", "BL15J-DI-EYE-01:STAT:CentroidY_RBV", "pixels", "%.0f")
    eyepySizeX = DisplayEpicsPVClass("eyepySizeX", "BL15J-DI-EYE-01:PY:Int1_RBV", "um", "%.0f")
    eyepySizeY = DisplayEpicsPVClass("eyepySizeY", "BL15J-DI-EYE-01:PY:Int2_RBV", "um", "%.0f")
    eyepyCenX = DisplayEpicsPVClass("eyepyCenX", "BL15J-DI-EYE-01:PY:Double1_RBV", "mm", "%1.4f")
    eyepyCenY = DisplayEpicsPVClass("eyepyCenY", "BL15J-DI-EYE-01:PY:Double2_RBV", "mm", "%1.4f")
    pe1Proc5statMean = DisplayEpicsPVClass("pe1Proc5statMean", "BL15J-EA-DET-01:STAT:MeanValue_RBV", "counts", "%1.4f")
    pe1CamStatmean = DisplayEpicsPVClass("pe1CamStatmean", "BL15J-EA-DET-01:STAT1:MeanValue_RBV", "counts", "%.2f")
    
    blowerT = DisplayEpicsPVClass("blowerT", "BL15J-EA-BLOW-01:PV:RBV", "deg C", "%3.2f")
    
except:
    localStation_exception(sys.exc_info(), "failed to load all staff-defined epics pvs")

print "Attempting to run component .py scripts from users script directory"
for py in ["commissioning","s1","xtal","m1","f2","cameras","sam","pe","dtacq","detectors"]:
    try:
        run(py)
    except java.io.FileNotFoundException, e:
        print "%s.py not found in user scripts directory" % py
    except:
        localStation_exception(sys.exc_info(), "running component "+str(py)+".py staff scripts")

# make a t scannable for recording actual elapsed time.
# usage example >>> scan dummy1 1 10 1 t
from gdascripts.pd.time_pds import showtimeClass
t = showtimeClass('t')

###########################################################################################
################## add maxvel, lcen and rcen to the processors ############################
###########################################################################################
from gdascripts.analysis.datasetprocessor.oned.MaxPositionAndValue import MaxPositionAndValue
scan_processor.processors.append(MaxPositionAndValue())

from gdascripts.analysis.datasetprocessor.oned.scan_stitching import Lcen, Rcen
scan_processor.processors.append(Lcen())
scan_processor.processors.append(Rcen())


##########################################################################################################
### SCAN PROCESSING ### SCAN PROCESSING ### SCAN PROCESSING ### SCAN PROCESSING ### SCAN PROCESSING ###### 
##########################################################################################################
# note the selection of which processors occur is done in localstationuser.py.
from gdascripts.analysis.datasetprocessor.oned.XYDataSetProcessor import XYDataSetFunction
import scisoftpy as dnp
try:
    from org.eclipse.dawnsci.analysis.dataset.impl import Maths
except:
    from org.eclipse.january.dataset import Maths

class _GaussianPeak(XYDataSetFunction):
    def __init__(self, name, labelList, formatString, plotPanel, offset, keyxlabel):
        XYDataSetFunction.__init__(self, name, labelList, keyxlabel, formatString)
        self.plotPanel = plotPanel
        self.offset = offset
    
    def _process(self, xDataset, yDataset):
        if yDataset.max()-yDataset.min() == 0:
            raise ValueError("There is no peak")
        
        x, y = toDnpArrays(xDataset, yDataset)
        fitResult = self.getFitResult(x,y)
        if self.plotPanel != None:
            plotGaussian(x, fitResult, self.plotPanel)
        results = self.getResults(fitResult)
        return [results.get(label, float('NaN')) for label in self.labelList]
    
    def getFitResult(self, x, y):
        funcs = getFitFunctions(self.offset)
        initial = gaussianInitialParameters(x, y, offset=self.offset)
        fitResult_p = dnp.fit.fit(funcs, x, y, initial, bounds=gaussianBounds(x, y, offset=self.offset), optimizer='global')
        fitResult_n = dnp.fit.fit(funcs, x, y, initial, bounds=gaussianBounds(x, y, negative_peak=True, offset=self.offset), optimizer='global')
        return fitResult_p if fitResult_p.residual < fitResult_n.residual else fitResult_n





class GaussianPeakAndBackgroundP(_GaussianPeak):
    """ Gaussian peak fitting with plotting.
    
    Fits a gaussian peak to the scan data (with a background term). 
    The trailing P in the class name denotes that this version plots the output
    to a GUI plot panel.
    """
    def __init__(self, name='peak', labelList=('pos','offset','top', 'fwhm', 'residual'),formatString='Gaussian at %f (pos) with offset: %f, top: %f, fwhm: %f and residual: %f', plotPanel='Gaus. Peak', keyxlabel='pos'):
        _GaussianPeak.__init__(self, name, labelList, formatString, plotPanel, offset=True, keyxlabel=keyxlabel)
    
    def getResults(self, fitResult):
        peak, fwhm, area, offset = fitResult.parameters[:4]
        residual = fitResult.residual
        top = area / fwhm
        return {'pos': peak, 'offset': offset, 'top': top, 'fwhm': fwhm,'residual': residual}


class GaussianPeak(_GaussianPeak):
    def __init__(self, name='peak', labelList=('pos','top', 'fwhm','residual'), formatString='Gaussian at %f (pos) with top: %f, fwhm: %f and residual: %f', plotPanel=None, keyxlabel='pos'):
        _GaussianPeak.__init__(self, name, labelList, formatString, plotPanel, offset=False, keyxlabel=keyxlabel)
    
    def getResults(self, fitResult):
        peak, fwhm, area = fitResult.parameters[:3]
        residual = fitResult.residual
        top = area / fwhm
        return {'pos': peak, 'top': top, 'fwhm': fwhm, 'residual': residual}


def gaussianInitialParameters(x, y, offset=False):
    initialParameters = [x.mean(), x.ptp()*.5, x.ptp()*y.ptp()]
    if offset:
        initialParameters += [y.mean()]
    return initialParameters

def getFitFunctions(offset):
    funcs = [dnp.fit.function.gaussian]
    if offset:
        funcs += [dnp.fit.function.offset]
    return funcs

def gaussianBounds(x, y, negative_peak=False, offset=False):
    bounds = [(x.min(), x.max()), (0, x.ptp())]
    bounds += [(x.ptp()*y.ptp()*-1, 0, x.ptp()*y.ptp())[negative_peak:negative_peak+2]]
    if offset:
        bounds += [(y.min(), y.max())]
    return bounds

def toDnpArrays(*args):
    return [dnp.array(arg) for arg in args]

def plotGaussian(x, fitResult, plotPanel):
    plotData = fitResult.makeplotdata()
    dnp.plot.line(x, toDnpArrays(plotData[0],plotData[1], plotData[2], plotData[3]),
                            name=plotPanel)

class GaussianDiscontinuityP(XYDataSetFunction):
    """ Gaussian discontinuity fitting with plotting.
    
    Takes the second differential of the scan data and fits a gaussian to it.
    The trailing P in the class name denotes that this version plots the output
    to a GUI plot panel.
    """
    def __init__(self, name='discontinuity', labelList=('pos','slope', 'fwhm', 'residual'),formatString='Discontinuity at %f (pos) with sharpness proportional to: %f, fwhm: %f and residual: %f.', plotPanel='Gaus. Disc.', keyxlabel='pos'):
        XYDataSetFunction.__init__(self, name, labelList, keyxlabel, formatString)
        self.smoothwidth = 1
        self.plotPanel = plotPanel
    
    #redevelop this to make it output the maxval as well!!!!!!!!!!!!
    def _process(self,xDataSet, yDataSet):
        dyDataSet = Maths.derivative(xDataSet._jdataset(), yDataSet._jdataset(), self.smoothwidth)
        d2yDataSet = Maths.derivative(xDataSet._jdataset(), dyDataSet, self.smoothwidth)
        minVal, maxVal = d2yDataSet.min(), d2yDataSet.max()
        if maxVal - minVal == 0:
            raise ValueError("There is no edge")
        
        labels = [label if label != 'slope' else 'top' for label in self.labelList]
        
        # DICKHEAD TRY NOT THROWING ALL THE LABELS INTO labels AND ONLY SEND THE ONES THAT IT EXPECTS 
        
        return GaussianPeak(self.name, labels, self.formatString, self.plotPanel)._process(xDataSet, d2yDataSet)

# class Discontinuity(XYDataSetFunction):
#     
#     def __init__(self, name='disc', labelList=('disc', 'peakval'), formatString='The discontinuiuty was at %f (disc) and had a std. dev. of %f (stddev)'):
#         XYDataSetFunction.__init__(self, name, labelList,'disc', formatString)
#     
#     def _process(self, xDataSet, yDataSet):
#         smoothwidth=1
#         dyDataSet = Maths.derivative(xDataSet, yDataSet, smoothwidth)
#         d2yDataSet = Maths.derivative(xDataSet, dyDataSet, smoothwidth)
#         x,y,d2y = dnp.array(xDataSet), dnp.array(yDataSet), dnp.array(d2yDataSet)
#         disc = x[d2y.argmax()]
#         peakval = y[d2y.argmax()]
#         
#         return disc, peakval

class BeamWidth(XYDataSetFunction):
    
    def __init__(self, name='beamwidth', labelList=('width','position'), formatString='The width of the beam was %1.4f and the position as %f'):
        XYDataSetFunction.__init__(self, name, labelList,'width', formatString)
        self.smoothwidth = 1
        
    def _process(self, xDataSet, yDataSet):
        
        dyDataSet = Maths.derivative(xDataSet._jdataset(), yDataSet._jdataset(), self.smoothwidth)
        d2yDataSet = Maths.derivative(xDataSet._jdataset(), dyDataSet, self.smoothwidth)
        
        low_edge = xDataSet[d2yDataSet.argMin()]
        high_edge = xDataSet[d2yDataSet.argMax()] 
        width = high_edge - low_edge
        position = (high_edge+low_edge)/2
        return width, position
    
    
class BeamWidthSmooth(XYDataSetFunction):
    
    def __init__(self, name='beamwidthsmooth', labelList=('width','position'), formatString='The width of the beam was %1.4f and the position as %f'):
        XYDataSetFunction.__init__(self, name, labelList,'width', formatString)
        self.smoothwidth = 2
        
    def _process(self, xDataSet, yDataSet):
        
        dyDataSet = Maths.derivative(xDataSet._jdataset(), yDataSet._jdataset(), self.smoothwidth)
        d2yDataSet = Maths.derivative(xDataSet._jdataset(), dyDataSet, self.smoothwidth)
        
        low_edge = xDataSet[d2yDataSet.argMin()]
        high_edge = xDataSet[d2yDataSet.argMax()] 
        width = high_edge - low_edge
        position = (high_edge+low_edge)/2
        return width, position
#######################################+#######################################
###                              load commissioning                          ###
###############################################################################
try:
    run("commissioning.py")
    run("pe.py")
    print "Successfully loaded commissioning files"
except:
    print "Failed to load commissioning files"





#######################################+#######################################
###                              SLIT ALIGNMENT                             ###
###############################################################################

def defineSlitLimits(sn):
    """Collect the current s3/4/5 dial limits. 
    
    sn: (string) slit name. one of: s3
                                    s4
                                    s5.
                                    
    """
    s3l = {"gXh":10.0871,"gXl":-0.01170,
           "cXh":0.10866,"cXl":-7.68220,
           "gYh":9.44013,"gYl":-0.10634,
           "cYh":8.25850,"cYl":-0.10066,
           }
    s4l = {"gXh":8.98796,"gXl":-0.10734,
           "cXh":0.09437,"cXl":-7.29861,
           "gYh":9.40104,"gYl":-0.09504,
           "cYh":7.97307,"cYl":-0.08449,
           }
    s5l = {"gXh":9.33824,"gXl":-0.10904,
           "cXh":0.11732,"cXl":-6.95832,
           "gYh":9.15625,"gYl":-0.10915,
           "cYh":7.28876,"cYl":-0.15361,
           }
    l = {"s3":s3l,"s4":s4l,"s5":s5l}
    return l[sn]

def fullyOpenSlits(slits):
    """ fully opens and centres the slits, based only on the limit values. 
    """
    # set the gao between the limit and the set point.pe1Proc5statMean
    limit_offset = 1
    
    # get string equivalent of scannable group
    sn = slits.name
    
    #define the four scannables.
    gapX = slits.getGroupMember(sn+'gapX')
    cenX = slits.getGroupMember(sn+'cenX')
    gapY = slits.getGroupMember(sn+'gapY')
    cenY = slits.getGroupMember(sn+'cenY')
    if abs(gapX.getUserOffset())+abs(cenX.getUserOffset())+abs(gapY.getUserOffset())+abs(cenY.getUserOffset()) < 0.01:
#     if [gapX.getUserOffset(),cenX.getUserOffset(),gapY.getUserOffset(),cenY.getUserOffset()].count(0) == 0:
        # calculate the values
        cX = (cenX.lowerMotorLimit + cenX.upperMotorLimit)/2
        gX = gapX.upperMotorLimit - limit_offset
        cY = (cenY.lowerMotorLimit + cenY.upperMotorLimit)/2
        gY = gapY.upperMotorLimit - limit_offset
        print "Opening slits %s..." % sn
        pos cenX cX gapX gX cenY cY gapY gY
    else:
        # assume all the offsets are applied and the motor is good. 
        print "Opening slits %s..." % sn
        pos cenX 0 gapX 8 cenY 0 gapY 8
    
    print "Slits %s fully opened." % sn

def setMotorPositionAs(motor,new_position,current_position=True):
    """ Sets the offset based on current values. 
    Calculates and sets the offset required to make the current_position
    actually equate to the new_position. It doesn't actually move anything. 
    If current_position is True, then it takes the retireives the current position. 
    If it's a number, it works on that instead.
    
    Here are some examples: 
    
    The offset is currently 2. I am at 3 in user units. I want to make this zero. 
    new offset = 2+3=5. I calculate and apply this by setting setMotorPositionAs(motor,0)
    
    I have observed that, in the currently offset units, I want to make 0.154 equal to 0.
    I am at a position of 5. setMotorPositionAs(motor,0,0.154) moves the offset the correct 
    amount so that I am now at 4.846.
    
    """
    from time import sleep
    # get current offset
    gco = motor.getMotor().getUserOffset()
    
    if type(current_position) == bool:
        current_position  = motor.getPosition()
    
    # set the new offset
    motor.getMotor().setUserOffset(new_position+gco-current_position)
    sleep(0.2) # this is to make sure the change is read back before the next step. 

def initialiseSlits(slits=s3):
    """ initialise the selected slits.
    
    Initialise the selected slits. In this case the term initialisation 
    refers to homing, and resetting the limits ready for coarse and fine alignment.
    
    Originally this was built in to coarse alignment, now it's here. 
    """
    from time import sleep, clock
    from gda.jython.commands.InputCommands import requestInput as raw_input
    
    # check real slits have been entered
    if slits not in [s3,s4,s5]:
        print "Those slits (%s) not recognised." % (slits)
        return
    
    #define the slit name
    sn = slits.name
    
    #define the four scannables.
    gapX = slits.getGroupMember(sn+'gapX')
    cenX = slits.getGroupMember(sn+'cenX')
    gapY = slits.getGroupMember(sn+'gapY')
    cenY = slits.getGroupMember(sn+'cenY')
    
    # define the distance to the hard limit to aim for
    limit_offset = 0.08
    print ""
    print " WARNING! This function will reset all limits and user offsets for slits "+slits.name+"!"
    print " The current values are: "
    print "*****************************************************"
    print "            Slit group %s current offsets:" % sn
    print "*****************************************************"
    print "    gapX    |    cenX    ||    gapY    |    cenY    |"
    print " %10.6f   %10.6f   %10.6f   %10.6f" % (gapX.userOffset,cenX.userOffset,gapY.userOffset,cenY.userOffset)
    print "*****************************************************"
    
    yes = raw_input("Are you sure you want to continue?")
    if yes not in ("y","Y","yes","Yes","YES","yep","of course"):
        print "ok, stopping as per your request."
        return
    
    # define the pvstem. 
    pvstem = "BL15J-AL-SLITS-0" + sn[-1] + ":"
    
    # Remove the user offsets
    print "Removing EPICS User offsets..."
    for motor in slits.getGroupMembers():
        motor.getMotor().setUserOffset(0)
    
    # home the motors
    caput(pvstem+"HM:HMGRP", "All")
    sleep(0.2)
    caput(pvstem+"HM:HOME", 1)
    sleep(0.2)
    t0 = clock()
    i = 0
    print("waiting for the motors to home"),
    while caget(pvstem+"HM:HOMING") == "1":
        print("."),
        sleep(1)
        i += 1
        if i % 20 < 0.1:
            print " "
            print "                              ",
        if i > 120:
            raise NameError("Homing timed out") 
    if clock()-t0 < 0.5:
        print "That was very quick, are you sure the motor is in and on?"
        print "initialisation aborted"
        return
    else:
        print "Homing complete."
    print ""
    print "Resetting the limits..."
    
    # get the limit values from the dictionary
    l = defineSlitLimits(sn)
    
    # iterate over the motors and set the limits. 
    for motor in slits.getGroupMembers(): 
        # the key is needed to get the values from the dict. 
        key = str(motor.name[2]+motor.name[5])
        
        if motor.name[2:5]=="cen":
            caput(pvstem+motor.name[-1]+":"+"CENTER.LLM",l[key+'l'])
            caput(pvstem+motor.name[-1]+":"+"CENTER.HLM",l[key+'h'])
        elif motor.name[2:5]=="gap":
            caput(pvstem+motor.name[-1]+":"+"SIZE.LLM",l[key+'l'])
            caput(pvstem+motor.name[-1]+":"+"SIZE.HLM",l[key+'h'])
        else:
            raise NameError('error determining nature of motor %s.',motor)
    print "Initialisation Complete."

def coarseSlitAlignment(slits=s3, diode=d2, alignX=True, alignY=True, automatic=False, XScanSlitWidth=0.5, YScanSlitWidth=0.2):
    """ aligns the requested slits from scratch. Assumes they have been initialised (i.e. homed, epics limits in place.)
    """
    from gda.jython.commands.InputCommands import requestInput as raw_input
    from time import sleep
    # check real slits have been entered
    if slits not in [s3,s4,s5]:
        print "Those slits (%s) not recognised." % (slits)
        return
    
    old_processors = scan_processor.processors
    scan_processor.processors = [GaussianPeakAndBackgroundP(), GaussianDiscontinuityP()]
    
    # define the distance to the soft limit to aim for
    limit_offset = 0.2
    
    #define the four scannables.
    gapX = slits.getGroupMember(slits.name+'gapX')
    cenX = slits.getGroupMember(slits.name+'cenX')
    gapY = slits.getGroupMember(slits.name+'gapY')
    cenY = slits.getGroupMember(slits.name+'cenY')
    
    # check all the offsets are zero (not strictly necessary, but best to make sure.)
    # Causes problems when combined with alignX = False etc. (resets axis not being used) 
#     for motor in slits.getGroupMembers():
#         motor.getMotor().setUserOffset(0.0)
    
    # open all the the slits
    fullyOpenSlits(s3)
    fullyOpenSlits(s4)
    fullyOpenSlits(s5)
    sleep(0.5)
    if alignX:
        # do the scan
        print ""
        print "coarsely locating the x-closed position, starting scan..."
        scan gapX gapX.lowerMotorLimit+limit_offset (gapX.upperMotorLimit+gapX.lowerMotorLimit)/2 0.3 diode
        print "I have identified %f as the point at which the slits open" % (discontinuity.result.pos)
        if automatic:
            gapXValue = discontinuity.result.pos
        else:
            input = raw_input("What do you think? (please enter a value or type y to accept mine)")
            if input == "y":
                gapXValue = discontinuity.result.pos
            else:
                gapXValue = float(input) 
        print "Opening the gapX to XScanSlitWidth."

        # set the offset
#         gapX.getMotor().setUserOffset(gapXValue)
        setMotorPositionAs(gapX,0,gapXValue)
        
        # move the motor
        pos gapX XScanSlitWidth
        
        print "the slits are now open to the tune of %f" % (gapX.getPosition())
        # do the scan
        print "trying to find the x-centre, starting scan..."
        scan cenX cenX.lowerMotorLimit+limit_offset cenX.upperMotorLimit-limit_offset 0.3 diode
        print "I have identified %f as the centre of the slits" % (peak.result.pos)
        if automatic:
            cenXValue = peak.result.pos
        else:
#             cenXValue = float(raw_input("What do you think? (please enter a value)"))
            input = raw_input("What do you think? (please enter a value or type y to accept mine)")
            if input == "y":
                cenXValue = discontinuity.result.pos
            else:
                cenXValue = float(input) 
        print "Moving the slits to the centre..."
        
        # set the offset
#         cenX.getMotor().setUserOffset(cenXValue)
        setMotorPositionAs(cenX,0,cenXValue)
        # move the motor
        pos cenX 0 gapX 6
        
    if alignY:
        # do the scan
        print ""
        print "coarsely locating the y-closed position, starting scan..."
        scan gapY gapY.lowerMotorLimit+limit_offset (gapY.upperMotorLimit+gapY.lowerMotorLimit)/2 0.3 diode
        print "I have identified %f as the point at which the slits open" % (discontinuity.result.pos)
        if automatic:
            gapYValue = discontinuity.result.pos
        else:
            input = raw_input("What do you think? (please enter a value or type y to accept mine)")
            if input == "y":
                gapYValue = discontinuity.result.pos
            else:
                gapYValue = float(input) 
        print "Opening the gapY to YScanSlitWidth"
        
        # set the offset
#         gapY.getMotor().setUserOffset(gapYValue)
        setMotorPositionAs(gapY,0,gapYValue)
        # move the motor
        pos gapY YScanSlitWidth
        
        print "the slits are now open to the tune of %f" % (gapY.getPosition())
        
        # do the scan
        print "trying to find the y-centre, starting scan..."
        scan cenY cenY.lowerMotorLimit+limit_offset cenY.upperMotorLimit-limit_offset 0.3 diode
        print "I have identified %f as the centre of the slits" % (peak.result.pos)
        if automatic:
            cenYValue = peak.result.pos
        else:
#             cenYValue = float(raw_input("What do you think? (please enter a value)"))
            input = raw_input("What do you think? (please enter a value or type y to accept mine)")
            if input == "y":
                cenYValue = discontinuity.result.pos
            else:
                cenYValue = float(input)  
        print "Moving the slits to the centre..."
        
        # set the offset
#         cenY.getMotor().setUserOffset(cenYValue)
        setMotorPositionAs(cenY,0,cenYValue)
        # move the motors
        pos cenY 0 gapY 6
        
    print ""
    print "*****************************************************"
    print "           Slit group %s coarsely aligned." % slits.name
    print "*****************************************************"
    print "    gapX    |    cenX    ||    gapY    |    cenY    |"
    print " %10.6f   %10.6f   %10.6f   %10.6f" % (gapXValue,cenXValue,gapYValue,cenYValue)
    print "*****************************************************"
    scan_processor.processors = old_processors
        
def fineSlitAlignment(slits=s3, diode=d2, alignX=True, alignY=True, automatic=False, XScanSlitWidth=0.25, YScanSlitWidth=0.25, override=False):
    """Fine alignment of the slits s3, s4, s5. 
    
    Perform a fine alignment of the slits. 
    Designed to work immediately after coarseAlignSlits, but can be run at any point to tweak the offsets.  
    
    """
    from gda.jython.commands.InputCommands import requestInput as raw_input
    
    # check real slits have been entered
    if slits not in [s3,s4,s5]:
        print "Those slits (%s) not recognised." % (slits)
        return
    
    old_processors = scan_processor.processors
    scan_processor.processors = [GaussianPeakAndBackgroundP(), GaussianDiscontinuityP() ]
    
    # define the distance to the soft limit to aim for
    limit_offset = 0.08
    
    #define the four scannables.
    gapX = slits.getGroupMember(slits.name+'gapX')
    cenX = slits.getGroupMember(slits.name+'cenX')
    gapY = slits.getGroupMember(slits.name+'gapY')
    cenY = slits.getGroupMember(slits.name+'cenY')
    
    # check all the offsets are not zero
    if not override:
        for motor in slits.getGroupMembers():
            if motor.getMotor().getUserOffset() == 0:
                print "motor %s has zero offset. Have you run a coarse alignment?" % (motor.name)
                print "rerun with override=True to override this message. "
                return
    
#     open the other slits
    for s in [s3,s4,s5]:
        if s != slits:
            fullyOpenSlits(s)
            
    # now position the slits we're interested in.
    # first scan is an x-scan so want small gapX and large gapY.  
    if alignX:
        print ""
        print "Configuring slits for x-gap scan..."
        pos cenX 0 cenY 0 gapX XScanSlitWidth gapY 8
        lv = max(-0.3, gapX.lowerMotorLimit+limit_offset)
        print "Locating the x-closed position, starting scan..."
        scan gapX lv .3 .01 diode
        print "I have identified %f as the point at which the slits open" % (discontinuity.result.pos)
        if automatic:
            gapXValue = discontinuity.result.pos
        else:
            input = raw_input("What do you think? (please enter a value or type y to accept mine)")
            if input == "y":
                gapXValue = discontinuity.result.pos
            else:
                gapXValue = float(input) 
        print "Opening the gapX to XScanSlitWidth."
        
        # set the offset based on wanting the gapXValue to be zero. 
        setMotorPositionAs(gapX,0,gapXValue)
        
        # move the motor
        pos gapX XScanSlitWidth
        
        # do the scan
        print "trying to find the x-centre, starting scan..."
        scan cenX -.5 0.5 .02 diode
        print "I have identified %f as the centre of the slits" % (peak.result.pos)
        if automatic:
            cenXValue = peak.result.pos
        else:
#             cenXValue = float(raw_input("What do you think? (please enter a value)"))
            input = raw_input("What do you think? (please enter a value or type y to accept mine)")
            if input == "y":
                cenXValue = discontinuity.result.pos
            else:
                cenXValue = float(input) 
        print "Moving the slits to the centre..."
        
        # set the offset based on wanting cenXValue to be 0. 
        setMotorPositionAs(cenX,0,cenXValue)
        
        # move the motor
        pos cenX 0 gapX 8
        
    if alignY:
        print ""
        print "Configuring slits for y-gap scan..."
        pos cenX 0 cenY 0 gapX 8 gapY YScanSlitWidth
        lv = max(-.3, gapY.lowerMotorLimit+limit_offset)
        print "Locating the y-closed position, starting scan..."
        scan gapY lv .3 .01 diode
        print "I have identified %f as the point at which the slits open" % (discontinuity.result.pos)
        if automatic:
            gapYValue = discontinuity.result.pos
        else:
#             gapYValue = float(raw_input("What do you think? (please enter a value)"))
            input = raw_input("What do you think? (please enter a value or type y to accept mine)")
            if input == "y":
                gapYValue = discontinuity.result.pos
            else:
                gapYValue = float(input) 
        print "Opening the gapY to YScanSlitWidth."
        
        # set the offset based on wanting the gapYValue to be zero. 
        setMotorPositionAs(gapY,0,gapYValue)
        
        # move the motor
        pos gapY YScanSlitWidth
        
        # do the scan
        print "trying to find the y-centre, starting scan..."
        scan cenY -.5 0.5 0.02 diode
        print "I have identified %f as the centre of the slits" % (peak.result.pos)
        if automatic:
            cenYValue = peak.result.pos
        else:
#             cenYValue = float(raw_input("What do you think? (please enter a value)"))
            input = raw_input("What do you think? (please enter a value or type y to accept mine)")
            if input == "y":
                cenYValue = discontinuity.result.pos
            else:
                cenYValue = float(input)  
        print "Moving the slits to the centre..."
        
        # set the offset based on wanting cenYValue to be 0. 
        setMotorPositionAs(cenY,0,cenYValue)
        
        # move the motor
        pos cenY 0 gapY 8
    if alignX and alignY:
        print ""
        print "*****************************************************"
        print "          Slit group %s fine alignment moves" % slits.name
        print "*****************************************************"
        print "    gapX    |    cenX    ||    gapY    |    cenY    |"
        print " %10.6f   %10.6f   %10.6f   %10.6f" % (gapXValue,cenXValue,gapYValue,cenYValue)
        print "*****************************************************"
    else:
        print "done!"
    scan_processor.processors = old_processors

#######################################+#######################################
###                                   END                                   ###
###############################################################################


def getCalibrationOffsets(slits = s3):
    """ Just returns the user calibration offsets for a slit group. 
    """
    if slits not in [s3,s4,s5]:
        print "Those slits (%s) not recognised." % (slits)
        return
    
    gapX = slits.getGroupMember(slits.name+'gapX')
    cenX = slits.getGroupMember(slits.name+'cenX')
    gapY = slits.getGroupMember(slits.name+'gapY')
    cenY = slits.getGroupMember(slits.name+'cenY')
    print ""
    print "*****************************************************"
    print "          Current Slit group %s offsets" % slits.name
    print "*****************************************************"
    print "    gapX    |    cenX    ||    gapY    |    cenY    |"
    print " %10.6f   %10.6f   %10.6f   %10.6f" % (gapX.getUserOffset(),cenX.getUserOffset(),gapY.getUserOffset(),cenY.getUserOffset())
    print "*****************************************************"
    

try:
    pe1AreaDetectorRunnableDeviceProxyFinder = finder.find("pe1AreaDetectorRunnableDeviceProxyFinder")
    pe1AreaDetectorRunnableDeviceProxy = pe1AreaDetectorRunnableDeviceProxyFinder.getRunnableDevice()

    from PerkinElmer.peAdTest import PeAdTest
    pe1JythonAreaDetectorRunnableDeviceDelegate = PeAdTest(pe1AreaDetectorRunnableDeviceProxy)
    pe1AreaDetectorRunnableDeviceProxy.setDelegate(pe1JythonAreaDetectorRunnableDeviceDelegate)
    pe1AreaDetectorRunnableDeviceProxy.register()
    
    """
    pe1DarkAreaDetectorRunnableDeviceProxyFinder = finder.find("pe1DarkAreaDetectorRunnableDeviceProxyFinder")
    pe1DarkAreaDetectorRunnableDeviceProxy = pe1DarkAreaDetectorRunnableDeviceProxyFinder.getRunnableDevice()

    from PerkinElmer.peAdDarkTest import PeAdDarkTest
    pe1DarkJythonAreaDetectorRunnableDeviceDelegate = PeAdDarkTest(pe1DarkAreaDetectorRunnableDeviceProxy)
    pe1DarkAreaDetectorRunnableDeviceProxy.setDelegate(pe1DarkJythonAreaDetectorRunnableDeviceDelegate)
    pe1DarkAreaDetectorRunnableDeviceProxy.register()
    """
except:
    localStation_exception(sys.exc_info(), "in localStation")

print "Completed running /dls_sw/i15-1/scripts/localStationStaff.py (staff editable)"
