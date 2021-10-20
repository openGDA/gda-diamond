"""
Continuous Energy Scannable and Controller for using Constant Velocity on I10
for use with GDA at Diamond Light Source
"""

from org.slf4j import LoggerFactory
from ContinuousMovePgmEnergyBinpointScannable import EnergyCalculatingCallable
from scannable.continuous.deprecated import ContinuousMovePgmEnergyBinpointScannable
from Diamond.idPosition import IdPosition

""" This scannable uses the motor controller to just control the motor and calculates the
    actual position from the position callables provided by the specified pitch motors.
"""
class ContinuousMovePgmEnergyIdJawPhaseBinpointScannable(ContinuousMovePgmEnergyBinpointScannable):
    """ Since the binpoints are slaved from a multi channel scaler card, motion will fail if the
        no scaler channels are specified in the scan.
        
        Also, since this scannable takes over starting the binpoint mechanism, it may not work if
        individual binpoint scannables are added to the scan. """

    def __init__(self,                                          name, move_controller, binpointGrtPitch, binpointMirPitch, binpointPgmEnergy, idEnergyScannable, binpointIdJawPhaseCallable):
        ContinuousMovePgmEnergyBinpointScannable.__init__(self, name, move_controller, binpointGrtPitch, binpointMirPitch, binpointPgmEnergy)
        self.logger = LoggerFactory.getLogger("ContinuousMovePgmEnergyIdJawPhaseBinpointScannable:%s" % name)

        self._idEnergyScannable = idEnergyScannable
        self._binpointIdJawPhaseCallable = binpointIdJawPhaseCallable
        
        self.extraNames = EnergiesCalculatingCallable.getPositionCallableExtraNames()
        self.outputFormat = EnergiesCalculatingCallable.getPositionCallableFormat()

    # Implement: public interface PositionCallableProvider<T> {

    # public Callable<T> getPositionCallable() throws DeviceException;
    def getPositionCallable(self):
        if self.verbose: self.logger.info('getPositionCallable()... last_requested_position=%r' % (
                                               self._last_requested_position))
        return EnergiesCalculatingCallable(self, self._last_requested_position,
                                           self._binpointGrtPitch.getPositionCallable(),
                                           self._binpointMirPitch.getPositionCallable(),
                                           self._binpointPgmEnergy.getPositionCallable(),
                                           self._idEnergyScannable,
                                           self._binpointIdJawPhaseCallable.getPositionCallable())
        # Note that we use the binpoint mechanism to get the actual positions of the grating
        # and mirror pitch and calculate the energy from those positions at each point.

    def atScanLineStart(self):
        ContinuousMovePgmEnergyBinpointScannable.atScanLineStart(self)
        self._binpointIdJawPhaseCallable.atScanLineStart()
        self._binpointIdJawPhaseCallable.collectData()
        
        (self.grating_density , _, self.grating_offset, self.plane_mirror_offset,  self.energy_calibration_gradient, 
         self.energy_calibration_reference) = self._move_controller.getPgmEnergyParameters()

    def atScanLineEnd(self):
        ContinuousMovePgmEnergyBinpointScannable.atScanLineEnd(self)
        self._binpointIdJawPhaseCallable.atScanLineEnd()


class EnergiesCalculatingCallable(EnergyCalculatingCallable):
    def __init__(                          self, parent, demand_position, grtPitchCallable, mirPitchCallable, pgmEnergyCallable, idEnergyScannable, idJawPhaseCallable):
        EnergyCalculatingCallable.__init__(self, parent, demand_position, grtPitchCallable, mirPitchCallable, pgmEnergyCallable)
        (self._idEnergyScannable, self._idJawPhaseCallable) = (
               idEnergyScannable,       idJawPhaseCallable)

    def call(self):
        energy, demand, demand_diff, pgm_energy, pgm_energy_diff = EnergyCalculatingCallable.call(self)
        idJawPhase = self._idJawPhaseCallable.call()
        
        id_energy = self._idEnergyScannable.getEnergy(IdPosition(0, 0, 0, 0, 0, idJawPhase))
        self._parent.logger.info('idJawPhase=%r, id_energy=%r, id_energy_diff=%r' % (idJawPhase, id_energy, id_energy-energy))
        return energy, demand, demand_diff, pgm_energy, pgm_energy_diff, \
               idJawPhase, id_energy, id_energy-energy

    @staticmethod
    def getPositionCallableExtraNames():
        extraNames = EnergyCalculatingCallable.getPositionCallableExtraNames()
        extraNames.extend(['idJawPhase', 'id_energy', 'id_energy_diff'])
        return extraNames

    @staticmethod
    def getPositionCallableFormat():
        format = EnergyCalculatingCallable.getPositionCallableFormat()
        format.extend(['%f', '%f', '%f'])
        return format
