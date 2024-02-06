"""
Class for creating energy instance that works with both 'cvscan' and 'scan' command in GDA.
In 'cvscan' it delegates to a special 'energy_controller' to deliver continuous motion of ID gap and PGM Grating pitch, 
while in 'scan' command, it delegates to 'energy_s' scannable to deliver ID gap and PGM energy motion in steps.

@author: Fajin Yuan 27 July 2020
"""

from gda.device.scannable import ContinuouslyScannableViaController, \
    ScannableMotionBase, PositionCallableProvider, PositionStreamIndexer, \
    PositionInputStream
from java.util.concurrent import Callable
from org.slf4j import LoggerFactory
from pgm.pgm import angles2energy, enecff2mirror, enemirror2grating  # @UnresolvedImport
from time import sleep
from i10shared import installation
import java
from scannables.continuous.ContinuousPgmGratingIDGapMoveController import ContinuousPgmGratingIDGapMoveController

""" This scannable uses the given motor controller to control the motor motion and calculates the
    actual energy position from the position callables provided by the specified 2 PGM pitch motors.
"""


class ContinuousMovePgmEnergyIDGapBinpointScannable(ContinuouslyScannableViaController, ScannableMotionBase, PositionCallableProvider):
    """ Since the binpoints are slaved from a multi channel scaler card, motion will fail if the
        no scaler channels are specified in the scan.
        
        Also, since this scannable takes over starting the binpoint mechanism, it may not work if
        individual binpoint scannables are added to the scan. """

    def __init__(self, name, move_controller, binpointGrtPitch, binpointMirPitch, binpointPgmEnergy):
        '''
        
        :param name:
        :param move_controller:
        :param binpointGrtPitch:
        :param binpointMirPitch:
        :param binpointPgmEnergy:
        '''
        self.logger = LoggerFactory.getLogger("ContinuousMovePgmEnergyIDGapBinpointScannable:%s" % name)
        self.verbose = False
        self.name = name

        self._move_controller = move_controller
        self._binpointGrtPitch = binpointGrtPitch
        self._binpointMirPitch = binpointMirPitch
        self._binpointPgmEnergy = binpointPgmEnergy

        self.inputNames = [name]
        self.extraNames = EnergyCalculatingCallable.getPositionCallableExtraNames()
        self.outputFormat = EnergyCalculatingCallable.getPositionCallableFormat()

        self._operating_continuously = False
        self._last_requested_position = None
        self.mybusy = False

        self.stream_indexer = None

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
            # Note that we use the binpoint mechanism to get the actual positions of the grating
            # and mirror pitch and calculate the energy from those positions at each point.
            return EnergyCalculatingCallable(self, self._last_requested_position,
                                             self._binpointGrtPitch.getPositionCallable(),
                                             self._binpointMirPitch.getPositionCallable(),
                                             self._binpointPgmEnergy.getPositionCallable())
        else:
            return self.stream_indexer.getPositionCallable()

    # Override: public class ScannableMotionBase extends ScannableBase implements ScannableMotion, INeXusInfoWriteable

    def asynchronousMoveTo(self, position):
        self.mybusy = True
        if self.verbose: self.logger.info('asynchronousMoveTo(%r)...' % position)
        position = float(position)
        if self._operating_continuously:
            if installation.isLive():
                self._last_requested_position = position
            else:
                self._last_requested_position = position
                # Calculate plane mirror angle for given grating density, energy, cff and offsets
                mirr_pitch = enecff2mirror(gd = self.grating_density,
                                           energy = float(position),
                                           cff = self.cff,
                                           groff = self.grating_offset,
                                           pmoff = self.plane_mirror_offset,
                                           ecg = self.energy_calibration_gradient,
                                           ecr = self.energy_calibration_reference)
                # Calculate grating angles for given grating density, energy, mirror angle and offsets
                grat_pitch = enemirror2grating(gd = self.grating_density,
                                               energy = float(position),
                                               pmang = mirr_pitch,
                                               groff = self.grating_offset,
                                               pmoff = self.plane_mirror_offset,
                                               ecg = self.energy_calibration_gradient,
                                               ecr = self.energy_calibration_reference)

                self._move_controller.grating_pitch_positions.append(grat_pitch)
                self._move_controller.mirror_pitch_positions.append(mirr_pitch)
                self._move_controller.pgm_energy_positions.append(float(position))
        else:
            self._last_requested_position = position
            if isinstance(self._move_controller, ContinuousPgmGratingIDGapMoveController):
                self._move_controller.energy.asynchronousMoveTo(position)
            else:
                raise RuntimeError("%s: asynchronousMoveTo only supports Continuous operation" % self.getName())
        self.mybusy = False

    def stop(self):
        if self._operating_continuously:
            if installation.isLive():
                print("Continuous ID motion in energy cannot be stopped, please wait the current cvscan to finish !")
            else:
                self._binpointPgmEnergy.stop()
                self._binpointGrtPitch.stop()
                self._binpointMirPitch.stop()
                self._move_controller.stopAndReset()
        else:
            self._move_controller.energy.stop()
        self.mybusy = False

    def atCommandFailure(self):
        self.stop()

    def atScanLineStart(self):
        if self.verbose: self.logger.info('atScanLineStart()...')
        if self._operating_continuously:
            self._binpointGrtPitch.atScanLineStart()
            self._binpointMirPitch.atScanLineStart()
            self._binpointPgmEnergy.atScanLineStart()
            self._binpointGrtPitch.collectData()
            self._binpointMirPitch.collectData()
            self._binpointPgmEnergy.collectData()
            if installation.isLive():
                (self.grating_density , self.cff, self.grating_offset, self.plane_mirror_offset, self.energy_calibration_gradient,
                 self.energy_calibration_reference) = self._move_controller.getPgmEnergyParameters()
            else:
                self._move_controller.grating_pitch_positions = []
                self._move_controller.mirror_pitch_positions = []
                self._move_controller.pgm_energy_positions = []
                (self.grating_density , self.cff, self.grating_offset, self.plane_mirror_offset, self.energy_calibration_gradient,
                 self.energy_calibration_reference) = self._move_controller.getPgmEnergyParametersFixed()
        else:
            stream = PositionInputStreamImplementer(self._move_controller.energy.pgmenergy)
            self.stream_indexer = PositionStreamIndexer(stream)

    def atScanLineEnd(self):
        if self.verbose: self.logger.info('atScanLineEnd()...')
        if self._operating_continuously:
            self._binpointGrtPitch.atScanLineEnd()
            self._binpointMirPitch.atScanLineEnd()
            self._binpointPgmEnergy.atScanLineEnd()
        else:
            self.stream_indexer = None

    def getPosition(self):
        if self.verbose: self.logger.info('getPosition()...')
        from gdaserver import pgm_energy  # @UnresolvedImport
        if self._operating_continuously:
            from gdaserver import pgm_grat_pitch, pgm_m2_pitch  # @UnresolvedImport
            grtPitch = pgm_grat_pitch.getPosition()
            mirPitch = pgm_m2_pitch.getPosition()
            pgmEnergy = pgm_energy.getPosition()
            energy = angles2energy(gd = self.grating_density,
                                   grang = grtPitch,  # /1000.,
                                   pmang = mirPitch,  # /1000.,
                                   groff = self.grating_offset,
                                   pmoff = self.plane_mirror_offset,
                                   ecg = self.energy_calibration_gradient,
                                   ecr = self.energy_calibration_reference)
            if not self._last_requested_position:
                self._last_requested_position = 0.0
            return energy, self._last_requested_position, self._last_requested_position - energy, pgmEnergy, pgmEnergy - energy
        else:
            if isinstance(self._move_controller, ContinuousPgmGratingIDGapMoveController):
                return self._move_controller.energy.pgmenergy.getPosition()
            else:
                # fix I10-366
                return pgm_energy.getPosition()

    def waitWhileBusy(self):
        if self.verbose: self.logger.info('waitWhileBusy()...')
        while self.isBusy():
            sleep(0.1)

    def isBusy(self):
        if self._operating_continuously:
            return self.mybusy  # don't call self._move_controller.isBusy(), as this is used to set up position callable before actual move in continue scan
        else:
            if isinstance(self._move_controller, ContinuousPgmGratingIDGapMoveController):
                return self._move_controller.energy.isBusy()
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
                return self._move_controller.energy.pgmenergy.getExtraNames()
            except:
                from gdaserver import pgm_energy  # @UnresolvedImport
                return pgm_energy.getExtraNames()

    def getOutputFormat(self):
        if self._operating_continuously:
            return self.super__getOutputFormat()
        else:
            try:
                return self._move_controller.energy.pgmenergy.getOutputFormat()
            except:  #
                from gdaserver import pgm_energy  # @UnresolvedImport
                return pgm_energy.getOutputFormat()

""" Note, self._operating_continuously is being set back to false before atScanEnd is being called. See:
2015-02-04 21:43:26,833 INFO  ContinuousPgmEnergyScannable:egy - setOperatingContinuously(1) was 0
...
2015-02-04 21:43:27,048 INFO  ContinuousPgmEnergyScannable:egy - asynchronousMoveTo(841)...  
2015-02-04 21:43:27,048 INFO  ContinuousPgmEnergyScannable:egy - waitWhileBusy()...  
2015-02-04 21:43:27,048 INFO  ContinuousPgmEnergyScannable:egy - waitWhileBusy()...  
2015-02-04 21:43:27,048 INFO  ContinuousPgmEnergyScannable:egy - getPositionCallable()... last_requested_position=841.0  
...
2015-02-04 21:30:53,128 INFO  ContinuousPgmEnergyScannable:egy - setOperatingContinuously(0) was 1
2015-02-04 21:30:53,128 INFO  ContinuousPgmEnergyScannable:egy - atScanEnd()... _operating_continuously=0
"""


class EnergyCalculatingCallable(Callable):

    def __init__(self,
               parent, demand_position, grtPitchCallable, mirPitchCallable, pgmEnergyCallable):
        (self._parent, self._demand_position, self._grtPitchCallable, self._mirPitchCallable, self._pgmEnergyCallable) = (
               parent, demand_position, grtPitchCallable, mirPitchCallable, pgmEnergyCallable)

    def call(self):
        grtPitch = self._grtPitchCallable.call()
        mirPitch = self._mirPitchCallable.call()
        pgmEnergy = self._pgmEnergyCallable.call()

        energy = angles2energy(gd = self._parent.grating_density,
                               grang = grtPitch,  # /1000.,
                               pmang = mirPitch,  # /1000.,
                               groff = self._parent.grating_offset,
                               pmoff = self._parent.plane_mirror_offset,
                               ecg = self._parent.energy_calibration_gradient,
                               ecr = self._parent.energy_calibration_reference)
        self._parent.logger.info('angles2energy(gd=%r, grang=%r, pmang=%r, groff=%r, pmoff=%r, ecg=%r, ecr=%r) = %r' % (
            self._parent.grating_density, grtPitch, mirPitch, self._parent.grating_offset,
            self._parent.plane_mirror_offset, self._parent.energy_calibration_gradient, self._parent.energy_calibration_reference,
            energy))
        return energy, self._demand_position, self._demand_position - energy, pgmEnergy, pgmEnergy - energy

    @staticmethod
    def getPositionCallableExtraNames():
        return ['demand', 'demand_diff', 'pgm_energy', 'pgm_energy_diff']

    @staticmethod
    def getPositionCallableFormat():
        return ['%f', '%f', '%f', '%f', '%f']


class PositionInputStreamImplementer(PositionInputStream):

    def __init__(self, scannableToRead):
        self.logger = LoggerFactory.getLogger("PositionInputStreamImplementer")
        self.scannable = scannableToRead
        self.verbose = True

    def read(self, max_to_read_in_one_go):
        if self.verbose: self.logger.info("read(%r)... from scannable '%r'" % (max_to_read_in_one_go, self.scannable.getName()))
        return java.util.Vector([float(self.scannable.getPosition())])
