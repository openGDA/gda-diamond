"""
An energy scannable designed to be used for continuous energy scan operation as well as energy scan in step. 

The Mono energy and corresponding ID gap for the same energy are moved continuously at constant velocity via the specified move controller.
The actual positions of energy and corresponding ID gap along with detector data collected at the same time during scan are captured into EPICS Bin points waveforms,
These data are read from EPICS waveforms during scanning using the specified Waveform Channel Scannables along with their corresponding demanding values for diagnosis.
    
"""

from gda.device.scannable import ContinuouslyScannableViaController, \
    ScannableMotionBase, PositionCallableProvider, PositionStreamIndexer,\
    PositionInputStream
from java.util.concurrent import Callable
from org.slf4j import LoggerFactory
from time import sleep
import installation
import java
from gda.device import DeviceException
from scannable.continuous.continuousEnergyMoveController import ContinuousEnergyMoveController

class ContinuousMoveEnergyIDGapBinpointScannable(ContinuouslyScannableViaController, ScannableMotionBase, PositionCallableProvider):
    """ Since the bin points are slaved from a multi channel scaler card, motion will fail if there is
        no scaler channels are specified in the scan.
        
        Also, since this scannable takes over starting the bin point mechanism, it may not work if
        individual binpoint scannables are added to the scan. """

    def __init__(self, name, move_controller, binpoint_energy, binpoint_idgap):
        self.logger = LoggerFactory.getLogger("ContinuousMovePgmEnergyIDGapBinpointScannable:%s" % name)
        self.verbose = False
        
        self.name = name
        self._move_controller = move_controller
        self._binpointEnergy = binpoint_energy
        self._binpointIdGap = binpoint_idgap

        self.inputNames = [name]
        self.extraNames = GapCalculatingCallable.getPositionCallableExtraNames()
        self.outputFormat = GapCalculatingCallable.getPositionCallableFormat()

        self._operating_continuously = False
        self._last_requested_position = None
        self.mybusy=False
        
        self.stream_indexer=None
        
    def setOrder(self,n):
        self._move_controller._energy.setOrder(n)
        
    def getOrder(self):
        return self._move_controller._energy.getOrder()
    
    def calc(self, energy, order):
        return self._move_controller._energy.calc(energy, order)

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
        if self.verbose: self.logger.info('getPositionCallable()... last_requested_position=%r' % (self._last_requested_position))
        if self._operating_continuously:
            # Note that we use the bin_point mechanism to get the actual positions of the energy
            # and id gap which need to be compared with their demand values.
            return GapCalculatingCallable(self, self._last_requested_position,
                                             self._binpointEnergy.getPositionCallable(),
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
            if installation.isDummy():
                #in dummy mode, it needs to keep or cache all the positions so it can be returned during continuous move
                if self.getName() == 'jenergy':
                    id_gap_requested=self._move_controller._energy.idgap(position)
                else: #hard X-ray need to support harmonic order
                    id_gap_requested=self._move_controller._energy.idgap(position, self._move_controller._energy.getOrder())
                self._move_controller.mono_energy_positions.append(position)
                self._move_controller.id_gap_positions.append(id_gap_requested)
        else:
            if isinstance(self._move_controller, ContinuousEnergyMoveController):
                self._move_controller._energy.asynchronousMoveTo(position)
            else:
                raise DeviceException("%s: asynchronousMoveTo only supports Continuous operation" % self.name)
        self.mybusy=False

    def stop(self):
        if self._operating_continuously:
            if installation.isLive():
                print("Continuous ID motion in energy cannot be stopped, please wait the current cvscan to finish !")
            else:
                self._binpointIdGap.stop()
                self._binpointEnergy.stop()
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
            self._binpointEnergy.atScanLineStart()
            self._binpointIdGap.collectData()
            self._binpointEnergy.collectData()
            if installation.isDummy():
                self._move_controller.mono_energy_positions=[]
                self._move_controller.id_gap_positions=[]
        else:
            stream=PositionInputStreamImplementer(self._move_controller._energy)
            self.stream_indexer=PositionStreamIndexer(stream)
            
    def atScanLineEnd(self):
        if self.verbose: self.logger.info('atScanLineEnd()...')
        if self._operating_continuously:
            self._binpointIdGap.atScanLineEnd()
            self._binpointEnergy.atScanLineEnd()
        else:
            self.stream_indexer=None

    def getPosition(self):
        if self.verbose: self.logger.info('getPosition()...')
        if self._operating_continuously:
            raise DeviceException("%s: getPosition() is not supported during continuous operation" % self.name)
        else:
            return self._move_controller._energy.getPosition()

    def waitWhileBusy(self):
        if self.verbose: self.logger.info('waitWhileBusy()...')
        while self.isBusy():
            sleep(0.1)

    def isBusy(self):
        if self._operating_continuously:
            return self.mybusy  #cannot call self._move_controller.isBusy() in continuous moving mode 
        else:
            return self._move_controller._energy.isBusy()

            
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
            return self._move_controller._energy.getExtraNames()
    
    def getOutputFormat(self):
        if self._operating_continuously:
            return self.super__getOutputFormat()
        else:
            return self._move_controller._energy.getOutputFormat()

class GapCalculatingCallable(Callable):
    def __init__(self, 
               parent,       demand_position,       energy_callable,       idgap_callable):
        (self._parent, self._demand_position, self._energy_callable, self._idgap_callable) = (
               parent,       demand_position,       energy_callable,       idgap_callable)

    def call(self):
        if self._parent._move_controller._energy.getName() == 'pgmenergy':
            energy = self._energy_callable.call()/1000 #EPICS unit is eV, beamline wants keV
        else:
            energy = self._energy_callable.call()
        idgap     = self._idgap_callable.call()
        
        if self._parent.getName()== 'jenergy':
            idgap_demand = self._parent._move_controller._energy.idgap(self._demand_position)
        else:
            idgap_demand = self._parent._move_controller._energy.idgap(self._demand_position, self._parent._move_controller._energy.getOrder())
        self._parent.logger.info('energy=%r, energy_demand=%r, idgap=%r, idgad_demand=%r' % (energy, self._demand_position, idgap, idgap_demand))
        return energy, self._demand_position, self._demand_position-energy, idgap, idgap_demand, idgap_demand-idgap

    @staticmethod
    def getPositionCallableExtraNames():
        return ['energy_demand', 'energy_diff', 'id_gap', 'id_gap_demand', 'id_gap_diff']

    @staticmethod
    def getPositionCallableFormat():
        return ['%f', '%f', '%f', '%f', '%f', '%f']
    
class PositionInputStreamImplementer(PositionInputStream):
    
    def __init__(self, scannable_to_read):
        self.logger = LoggerFactory.getLogger("PositionInputStreamImplementer")
        self.scannable=scannable_to_read
        self.verbose=True
        
    def read(self, max_to_read_in_one_go):
        if self.verbose: self.logger.info("read(%r)... from scannable '%r'" % (max_to_read_in_one_go, self.scannable.getName()))
        return java.util.Vector([float(self.scannable.getPosition())])