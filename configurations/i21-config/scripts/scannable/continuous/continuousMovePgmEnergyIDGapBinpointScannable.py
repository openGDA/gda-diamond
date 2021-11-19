"""
An energy scannable designed to be used for continuous energy scan operation. 

The PGM energy and corresponding ID gap for the same energy are moved continuously at constant velocity via the specified move controller.
The actual positions of energy and corresponding ID gap along with scannable data collected at the same time during scan are captured into EPICS Bin points waveforms,
These data are read from EPICS waveforms during scanning using the specified Waveform Channel Scannables along with their corresponding demanding values for diagnosis.

@author: Fajin Yuan
@since: 10 Auguest 2020
"""

from gda.device.scannable import ContinuouslyScannableViaController, \
    ScannableMotionBase, PositionCallableProvider, PositionStreamIndexer,\
    PositionInputStream
from java.util.concurrent import Callable
from org.slf4j import LoggerFactory
from time import sleep
import installation
import java
from scannable.continuous.continuousPgmEnergyIDGapMoveController import ContinuousPgmEnergyIDGapMoveController
from gda.device import DeviceException
from gdaserver import pgmEnergy, idgap  # @UnresolvedImport


class ContinuousMovePgmEnergyIDGapBinpointScannable(ContinuouslyScannableViaController, ScannableMotionBase, PositionCallableProvider):
    """ Since the bin points are slaved from a ADC in EPICS, motion will fail if there is no ADC channels are specified in the scan.
        
        Also, since this scannable takes over starting the bin point mechanism, it may not work if
        individual binpoint scannables are added to the scan. """

    def __init__(self, name, move_controller, binpointPgmEnergy, binpointIdGap):
        self.logger = LoggerFactory.getLogger("ContinuousMovePgmEnergyIDGapBinpointScannable:%s" % name)
        self.verbose = False
        
        self.name = name
        self._move_controller = move_controller
        self._binpointPgmEnergy = binpointPgmEnergy
        self._binpointIdGap = binpointIdGap

        self.inputNames = [name]
        self.extraNames = GapCalculatingCallable.getPositionCallableExtraNames()
        self.outputFormat = GapCalculatingCallable.getPositionCallableFormat()

        self._operating_continuously = False
        self._last_requested_position = None
        self.mybusy=False
        
        self.stream_indexer=None

    # Implement: public interface ContinuouslyScannableViaController extends Scannable
    def setOperatingContinuously(self, b):
        if self.verbose: self.logger.info('setOperatingContinuously(%r) was %r' % (b, self._operating_continuously))
        self._operating_continuously = b

    def isOperatingContinously(self):
        return self._operating_continuously

    def getContinuousMoveController(self):
        return self._move_controller

    # Implement: public interface PositionCallableProvider<T> {

    # public Callable<T> getPositionCallable() throws DeviceException;
    def getPositionCallable(self):
        if self.verbose: self.logger.info('getPositionCallable()... last_requested_position=%r' % (
                                               self._last_requested_position))
        if self._operating_continuously:
            # Note that we use the bin_point mechanism to get the actual positions of the pgm energy
            # and id gap which need to be compared with their demand values.
            return GapCalculatingCallable(self, self._last_requested_position,
                                             self._binpointPgmEnergy.getPositionCallable(),
                                             self._binpointIdGap.getPositionCallable())
        else:
            return self.stream_indexer.getPositionCallable()

    # Override: public class ScannableMotionBase extends ScannableBase implements ScannableMotion, INeXusInfoWriteable

    def asynchronousMoveTo(self, position):
        self.mybusy=True
        if self.verbose: self.logger.info('asynchronousMoveTo(%r)...' % position)
        position = float(position)
        self._last_requested_position = position
        if self._operating_continuously:
            if not installation.isLive():
                #in dummy mode, it needs to keep or cache all the positions so it can be returned during continuous move
                self._move_controller.pgm_energy_positions.append(position)
                id_gap_requested=self._move_controller._energy.get_ID_gap_phase_at_current_polarisation(position)[0]
                self._move_controller.id_gap_positions.append(id_gap_requested)
        else:
            if isinstance(self._move_controller, ContinuousPgmEnergyIDGapMoveController):
                self._move_controller._energy.asynchronousMoveTo(position)
            else:
                raise DeviceException("%s: asynchronousMoveTo only supports Continuous operation" % self.name)
        self.mybusy=False

    def stop(self):
        if self._operating_continuously:
            if installation.isLive():
                print("cvscan cannot be stopped, please wait it to finish!")
            else:    
                self._binpointIdGap.stop()
                self._binpointPgmEnergy.stop()
                self._move_controller.stopAndReset()
        else:
            self._move_controller._energy.stop()
        self.mybusy=False
        
    def atCommandFailure(self):
        self.stop()
        
    def atScanLineStart(self):
        if self.verbose: self.logger.info('atScanLineStart()...')
        if self._operating_continuously:
            self._binpointIdGap.atScanLineStart()
            self._binpointPgmEnergy.atScanLineStart()
            self._binpointIdGap.collectData()
            self._binpointPgmEnergy.collectData()
            if installation.isDummy():
                self._move_controller.pgm_energy_positions=[]
                self._move_controller.id_gap_positions=[]
        else:
            stream=PositionInputStreamImplementer(self._move_controller._energy)
            self.stream_indexer=PositionStreamIndexer(stream)
            
    def atScanLineEnd(self):
        if self.verbose: self.logger.info('atScanLineEnd()...')
        if self._operating_continuously:
            self._binpointIdGap.atScanLineEnd()
            self._binpointPgmEnergy.atScanLineEnd()
        else:
            self.stream_indexer=None

    def getPosition(self):
        if self.verbose: self.logger.info('getPosition()...')
        if self._operating_continuously:
            pgm_energy = pgmEnergy.getPosition()
            id_gap = idgap.getPosition()
            id_gap_demand = self._move_controller._energy.get_ID_gap_phase_at_current_polarisation(self._last_requested_position)[0]
            return pgm_energy, self._last_requested_position, self._last_requested_position-pgm_energy, id_gap, id_gap_demand, id_gap_demand-id_gap
        else:
            if isinstance(self._move_controller, ContinuousPgmEnergyIDGapMoveController):
                return self._move_controller._energy.getPosition()
            else:
                return pgmEnergy.getPosition()

    def waitWhileBusy(self):
        if self.verbose: self.logger.info('waitWhileBusy()...')
        while self.isBusy():
            sleep(0.1)

    def isBusy(self):
        if self._operating_continuously:
            return self.mybusy  #cannot call self._move_controller.isBusy() in continuous moving mode 
        else:
            if isinstance(self._move_controller, ContinuousPgmEnergyIDGapMoveController):
                return self._move_controller._energy.isBusy()
            else:
                return self._move_controller.isMoving()

            
    # public interface ScannableMotion extends Scannable

    # Override: public interface Scannable extends Device

    # Note that neither stop() nor atCommandFailure() are called when operatingContinuously, however stopAndReset()
    # is called on the move_controller, so the move_controller needs to handle failures there.
    
    # We do need an atScanEnd() though, since unlike stop() and atCommandFailure(), stopAndReset() isn't called
    # when the scan line completes.
    def atScanEnd(self):
        if self.verbose: self.logger.info('atScanEnd()... _operating_continuously=%r' % self._operating_continuously)
        self._move_controller.atScanEnd()
    
    # we have to implement following scannable interface for it to work outside continuous scanning
    def getExtraNames(self):
        if self._operating_continuously:
            return self.super__getExtraNames()
        else:
            try: 
                return self._move_controller._energy.pgmenergy.getExtraNames()
            except:
                return pgmEnergy.getExtraNames()
    
    def getOutputFormat(self):
        if self._operating_continuously:
            return self.super__getOutputFormat()
        else:
            try:
                return self._move_controller._energy.pgmenergy.getOutputFormat()
            except: #
                return pgmEnergy.getOutputFormat()

class GapCalculatingCallable(Callable):
    def __init__(self, 
               parent,       demand_position,       pgmEnergyCallable,       idGapCallable):
        (self._parent, self._demand_position, self._pgmEnergyCallable, self._idGapCallable) = (
               parent,       demand_position,       pgmEnergyCallable,       idGapCallable)

    def call(self):
        pgmEnergy = self._pgmEnergyCallable.call()
        idGap     = self._idGapCallable.call()
        
        idGap_demand = self._parent._move_controller._energy.get_ID_gap_phase_at_current_polarisation(self._demand_position)[0]
        
        self._parent.logger.info('pgmenergy=%r, energy_demand=%r, idgap=%r, idgad_demand=%r' % (pgmEnergy, self._demand_position, idGap, idGap_demand))
        return pgmEnergy, self._demand_position, self._demand_position-pgmEnergy, idGap, idGap_demand, idGap_demand-idGap

    @staticmethod
    def getPositionCallableExtraNames():
        return ['energy_demand', 'energy_diff', 'id_gap', 'id_gap_demand', 'id_gap_diff']

    @staticmethod
    def getPositionCallableFormat():
        return ['%f', '%f', '%f', '%f', '%f', '%f']
    
class PositionInputStreamImplementer(PositionInputStream):
    
    def __init__(self, scannableToRead):
        self.logger = LoggerFactory.getLogger("PositionInputStreamImplementer")
        self.scannable=scannableToRead
        self.verbose=True
        
    def read(self, max_to_read_in_one_go):
        if self.verbose: self.logger.info("read(%r)... from scannable '%r'" % (max_to_read_in_one_go, self.scannable.getName()))
        return java.util.Vector([float(self.scannable.getPosition())])