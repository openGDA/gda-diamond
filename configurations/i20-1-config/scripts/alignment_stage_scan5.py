from gda.factory import Finder
from gda.device.zebra.controller.impl import ZebraImpl
from gda.device.zebra.controller import Zebra
from gda.device import ContinuousParameters
from gda.scan import ContinuousScan
from uk.ac.gda.server.exafs.epics.device.scannable import QexafsTestingScannable
from gda.device.detector import BufferedEdeDetector
from java.lang import Thread

# COnfigure zebra for doing alignment stage scan with Frelon :
#      Position based gate based on alignment stage position, time based pulses; trigger at start of gate should start Frelon collection.
# imh 27/10/2017
# 8/2/2018  : 
#         AlignmentStageScannable sets up zebra, tfg etc. at start of scan
#         Frelon triggered correctly using Tfg, 
#         Frelon wrapped in BufferedDetector for use in continuous scan; configured before scan using prepareDetectorForCollection
#         with num spectra, time per spectrum, num accumulations time per accumulation. (time per spectrum is redundant).
#         Pulse step on Zebra is set to match time per spectrum on Frelon.
#         Scan working ok.
# 16/2/2018 : Zebra encoder position readout, actual position for each spectrum (from interpolated) added to Nexus file in AlignmentStageScannable 
#         Mean, std deviation of actual vs calculated position for each spectrum to console at end of scan.
#         Make sure ramp distance is adjusted to have uniform velocity for region being scanned!
#         frelon.stop() added at end of scan.

from org.slf4j import LoggerFactory

import org.eclipse.january.dataset.DatasetFactory as DatasetFactory
import org.eclipse.january.dataset.DoubleDataset as DoubleDataset

class AlignmentSlitScannable(QexafsTestingScannable) :

    
    def __init__(self, motor_to_move) :
        self.motorToMove = motor_to_move
        self.setName(motor_to_move.getName()+"_cont")
        self.setMotor(motor_to_move.getMotor())
        self.setOutputFormat(["%.4f"])

        self.triggerInputForTfg = 2 # same as used on scaler_for_zebra
        self.triggerOutputForDetector =1 
        self.logger = LoggerFactory.getLogger(AlignmentSlitScannable);

    def getMotorToMove(self):
        return self.motorToMove

    def setMainDetector(self, mainDetector) :
        self.mainDetector = mainDetector

    def setZebra(self, zebraDevice) :
        self.zebraDevice = zebraDevice

    def setDaServer(self, daServer) :
        self.daServer = daServer

    def atScanStart(self) :
        self.logger.info("atScanStart")

    def stop(self):
        self.atScanEnd()

    def atScanEnd(self):
        frelon.stop()
        self.zebraDevice.pcDisarm()

        # Wait for zebra to finish, so all points have been captured and 
        # complete encoder positions and time arrays can be read out.
        while self.zebraDevice.isPCArmed() :
            print "Waiting for zebra to disarm at scan end..."
            Thread.sleep(100)

        self.addZebraDataToFile();
        
    def prepareForContinuousMove(self) :
        self.logger.info("Moving motor to initial position...")
        super(AlignmentSlitScannable, self).prepareForContinuousMove()

        self.logger.info("Preparing and arming Zebra ...")
        self.prepareZebra()

        self.logger.info("Preparing Tfg2 ...")
        self.prepareTfg()

    def prepareZebra(self) :

        params = self.getContinuousParameters()
        scanStartPos = params.getStartPosition()
        scanEndPos = params.getEndPosition()
        scanTime = params.getTotalTime()
        numReadouts = params.getNumberDataPoints()
        maxPulses = int(numReadouts*1.5)
        gateWidth = abs(scanEndPos - scanStartPos)

        time_units = Zebra.PC_TIMEUNIT_SEC
        pos_encoder = Zebra.PC_ENC_ENC1
        if scanStartPos < scanEndPos :
            pos_direction = Zebra.PC_DIR_POSITIVE
        else :
            pos_direction = Zebra.PC_DIR_NEGATIVE

        gateTrigSource=Zebra.PC_GATE_SOURCE_POSITION

        pulseStart = 0
        pulseStep = scanTime/numReadouts
        pulseWidth = pulseStep*0.5
        pulseTrigSource=Zebra.PC_PULSE_SOURCE_TIME

        # Disarm first
        self.zebraDevice.pcDisarm()

          # Trig encoder, position direction
        self.zebraDevice.setPCEnc(pos_encoder)
        self.zebraDevice.setPCDir(pos_direction)
        self.zebraDevice.setPCTimeUnit(time_units)
        
         # Gate source
        self.zebraDevice.setPCGateNumberOfGates(1)
        self.zebraDevice.setPCGateSource(gateTrigSource)
        self.zebraDevice.setPCGateStart(scanStartPos)
        self.zebraDevice.setPCGateWidth(gateWidth)

        # Pulses (time based)
        self.zebraDevice.setPCPulseSource(pulseTrigSource)
        self.zebraDevice.setPCPulseStart(pulseStart)
        self.zebraDevice.setPCPulseWidth(pulseWidth)
        self.zebraDevice.setPCPulseStep(pulseStep)
        self.zebraDevice.setPCPulseMax(maxPulses)
        # set flag so zebra doesn't wait for callback after arming (missing callback for this PV...)
        #self.zebraDevice.setArmPutNoWait(True)
        ## arm the zebra
        self.zebraDevice.pcArm()

    def setTriggerInputForTfg(self, triggerInputForTfg) :
        self.triggerInputForTfg = triggerInputForTfg

    def setTriggerOutputForDetector(self, triggerOutputForDetector) :
        self.triggerOutputForDetector = triggerOutputForDetector

    def prepareTfg(self) :
        self.daServer.sendCommand("tfg setup-trig start ttl"+str(self.triggerInputForTfg))

        command = ""
        command +=  "tfg setup-groups ext-start cycles 1\n"    
        # produce single pulse on output port (to start the frelon)
        command += "1 0.001000 0.0 %d 0 0 0\n"%(2**self.triggerOutputForDetector)
        
        min_dead_time = 1e-6
        numTriggersToWaitFor = self.getContinuousParameters().getNumberDataPoints()-1
        # Count remaining triggers
        command += "%d %f %f 0 0 0 %d\n"%(numTriggersToWaitFor, min_dead_time, min_dead_time, self.triggerInputForTfg+8)
        command += "-1 0 0 0 0 0 0\n"

        self.daServer.sendCommand( command )
        self.daServer.sendCommand( "tfg arm")

    def getInterpolatedPositions(self, timeDataset, positionDataset) :
        from uk.ac.diamond.scisoft.analysis.dataset.function import Interpolation1D

        scanTime = self.getContinuousParameters().getTotalTime()
        numReadouts = self.getContinuousParameters().getNumberDataPoints()
        timePerSpectrum = scanTime/numReadouts;
        startTime = timeDataset.get(0);
        self.logger.info("Calculating interpolated positions : {} spectra, time per spectrum = {} sec, start time = {} sec", numReadouts, timePerSpectrum, startTime)
        
        # Make dataset of times when detector readout occurred : add multiples of detector 'time per spectrum' to start 
        # time when the detector was triggered (i.e. first encoder time)
        detectorTime = DatasetFactory.zeros(DoubleDataset, numReadouts)
        for i in range(numReadouts) :
            detectorTime.set(startTime + i*timePerSpectrum, i)
        
        # Get positions for each detector readout by interpolating on the zebra encoder position and time arrays
        positionAtDetectorTime = Interpolation1D.linearInterpolation( timeDataset, positionDataset, detectorTime)
        return detectorTime, positionAtDetectorTime

    def addAxisAttributes(self, nexusFile, dataNode, units) :
        from org.eclipse.dawnsci.analysis.tree import TreeFactory
        from org.eclipse.dawnsci.nexus import NexusConstants
        nexusFile.addAttribute(dataNode, TreeFactory.createAttribute(NexusConstants.DATA_AXIS, 2) );
        nexusFile.addAttribute(dataNode, TreeFactory.createAttribute(NexusConstants.UNITS, units) )

    def addDataToNexusFile(self, nexusFile, detectorGroupName, dataName, dataset, units=None):
        self.logger.info("Adding data to NexusFile : {}/{}", detectorGroupName, dataName)
        nexusFile.createData(detectorGroupName, dataName, dataset, True)
        if units is not None :
            self.addAxisAttributes(nexusFile, detectorGroupName+"/"+dataName, units)
        
    def addZebraDataToFile(self) :
        self.logger.info("Getting time and encoder position from Zebra")
        from org.eclipse.dawnsci.hdf5.nexus import NexusFileHDF5
        from uk.ac.diamond.scisoft.analysis.dataset.function import Interpolation1D

        # Get zebra encoder information (num captured points, encoder and time arrays)
        numPointsCaptured  = self.zebraDevice.getPCNumberOfPointsCaptured();
        timesArray = self.zebraDevice.getPCTimePV().get();
        encoderPositionsArray = self.zebraDevice.getPcCapturePV(0).get();
                
        # Make datasets of Zebra encoder data
        timesDataset = DatasetFactory.zeros(DoubleDataset, numPointsCaptured)
        positionsDataset = DatasetFactory.zeros(DoubleDataset, numPointsCaptured)
        for i in range(numPointsCaptured) :
            timesDataset.set(timesArray[i], i)
            positionsDataset.set(encoderPositionsArray[i], i)
    
        # Add datasets to nexus file ...
        nexusFilename = lastScanDataPoint().getCurrentFilename();
        detectorEntry = "/entry1/"+self.mainDetector.getName()+"/"
        self.logger.info("Adding time and encoder positions to nexus file {} in {}", nexusFilename, detectorEntry)
        
        # Zebra encoder position and and time arrays
        file = NexusFileHDF5.openNexusFile(nexusFilename)
        self.addDataToNexusFile(file, detectorEntry, "zebra_time", timesDataset, "secs")
        self.addDataToNexusFile(file, detectorEntry, "zebra_position", positionsDataset, "cm")

        # Interpolated position and time : position of the motor at start of each detector readout
        interpolatedVals = self.getInterpolatedPositions(timesDataset, positionsDataset)
        self.addDataToNexusFile(file, detectorEntry, "detector_time", interpolatedVals[0], "secs")
        self.addDataToNexusFile(file, detectorEntry, "detector_position", interpolatedVals[1], "cm")
        
        # Difference between actual and calculated position for each spectrum
        det_positions=interpolatedVals[1]
        positionDiffDataset = DatasetFactory.zeros(DoubleDataset, det_positions.getSize())
        for i in range(det_positions.getSize()) :
            positionDiffDataset.set(det_positions.getDouble(i) - self.calculateEnergy(i), i)

        self.addDataToNexusFile(file, detectorEntry, "detector_position-calculated_position", positionDiffDataset, "cm")
        file.close()

        print "Mean, Std deviation of (actual - calculated position) : ", positionDiffDataset.mean(), ", ",positionDiffDataset.stdDeviation()


def delete_scannables() :
    global scalerForZebra, contScannable, motor_to_move, bufferedDetector
    del scalerForZebra
    del motor_to_move
    del contScannable
    del bufferedDetector


def showInfo(infoString, command) :
    result = eval(command)
    print infoString,",",command,"\t:",result

def showFrelonState() :
    limaCcd="frelon.getDetectorData()."
    showInfo("Accumulation mode", limaCcd+"getAcqMode()" )
    showInfo("Number of images to be acquired", limaCcd+"getNumberOfImages()" )
    showInfo("Trigger mode", limaCcd+"getTriggerMode()" )
    showInfo("Accumulation time mode", limaCcd+"getAccumulationTimeMode()" )
    showInfo("Max exposure time per accumulation", limaCcd+"getAccumulationMaximumExposureTime()" )
    showInfo("Exposure time of image", limaCcd+"getExposureTime()" )

def plot_last_data() :
    fname = lastScanDataPoint().getCurrentFilename()
    nexusData=dnp.io.load(fname)
    frelonData = nexusData.entry1.frelon
    position = frelonData.value[...]
    posAtDetectorMeasurement = nexusData.entry1.bufferedFrelon.detector_position[...]
    frelonRoiData=[ frelonData.ROI_1[...], frelonData.ROI_2[...], frelonData.ROI_3[...], frelonData.ROI_4[...] ]
    xlabel = "Position from zebra [cm]"
    dnp.plot.line( {xlabel:posAtDetectorMeasurement}, frelonRoiData, title="ROI counts vs position (from zebra encoder)")


zebra_device = Finder.getInstance().find("zebra_device")
daserverForTfg = Finder.getInstance().find("daserverForTfg")
scalerForZebra = Finder.getInstance().find("scaler_for_zebra")
motor_to_move = Finder.getInstance().find("as_hoffset")

## Buffered detector to use for continuous scan
bufferedDetector = BufferedEdeDetector()
bufferedDetector.setName("bufferedFrelon")
bufferedDetector.setDetector(frelon)
bufferedDetector.setExternalTriggerMode(True)

triggerInputForTfg = scalerForZebra.getTtlSocket() ## use same port for Tfg trigger input as for TurboXAS scan
triggerOutputForFrelon = 1

# Setup continuously scannable to control the motor
contScannable = AlignmentSlitScannable(motor_to_move)
contScannable.setZebra(zebra_device)
contScannable.setDaServer(daserverForTfg)
contScannable.setMainDetector(bufferedDetector)
contScannable.setTriggerInputForTfg( scalerForZebra.getTtlSocket() )
contScannable.setTriggerOutputForDetector( 1 )
contScannable.setMaxMotorSpeed(50.0) # motor speed used when moving to runup position for scan
contScannable.setRampDistance(0.2)

#cvscan contScannable scan_start scan_end scan_num_readouts scan_time bufferedDetector
import math

accumulation_readout_time=0.8e-3

# start, stop, step, frelon accumulation time [secs], frelon num accumulations,
def run_slit_scan(scan_start, scan_end, scan_step, accumulation_time, num_accumulations) :
    scan_num_readouts = math.ceil( float((scan_end - scan_start)/scan_step) )
    scan_time_per_spectrum = (accumulation_time+accumulation_readout_time)*num_accumulations
    scan_total_time = scan_num_readouts * scan_time_per_spectrum
    units = contScannable.getMotorToMove().getUserUnits()
    
    print "Scan range   :", scan_start," ... ", scan_end, units,"(stepsize = ", scan_step, units,")"
    print "Num readouts :", int(scan_num_readouts)
    print "Motor speed :", float((scan_end - scan_start)/scan_total_time)," ",scan_step, units," per sec"

    print "Time per point  :", scan_time_per_spectrum,"sec (accumulation time =", accumulation_time," sec, num accumulations =", num_accumulations,")"
    print "Total scan time :", scan_total_time,"sec"
    
    # bufferedDetector.prepareDetectorForCollection(scan_num_readouts, timePerSpectrum, accumulationTime, numAccumulations)
    bufferedDetector.prepareDetectorForCollection( int(scan_num_readouts), scan_time_per_spectrum, accumulation_time, int(num_accumulations))

    cvscan contScannable scan_start scan_end scan_num_readouts scan_total_time bufferedDetector
    

