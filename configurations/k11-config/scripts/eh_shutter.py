"""
eh_shutter is defined via Spring as a JythonEnumPositionerWrapper,
wrapping a scannable "eh_shutter_jy", defined in this module
"""


from gas_saving.gas_saving_shutter import GasSavingShutter
from gas_saving.valve import Valve, InterlockedValves
from k11_utilities import is_live
from interlocks import eh_non_critical_jy, eh1_searched_locked_jy


if is_live():
    from gda.device.enumpositioner import EpicsValve # @UnresolvedImport
    from gas_saving.live import EpicsValveController
    from gas_saving.wait_for_gas import WaitForGas
    
    shutter = EpicsValve()
    shutter.setEpicsRecordName("BL11K-PS-SHTR-01")
    shutter.setCheckDemandInStatus(True)
    
    pco_gas_controller = EpicsValveController("BL11K-GA-MFC-01:SAVEGAS")
    kb_gas_controller = EpicsValveController("BL11K-GA-MFC-02:SAVEGAS")
    
    waiter = WaitForGas("BL11K-GA-MFC-02:SAVEGAS:OPEN_STATE", 1, "BL11K-GA-MFC-02:GAS:INTERVAL", "BL11K-GA-MFC-02:GAS:THR")
 
else:
    from gda.device.enumpositioner import DummyValve  # @UnresolvedImport
    from gas_saving.dummy import DummyValveController, DummyWaiter
    
    shutter = DummyValve()
    shutter.setName("EH shutter")
    
    pco_gas_controller = DummyValveController("PCO gas")
    kb_gas_controller = DummyValveController("KB gas")
    
    waiter = DummyWaiter(0)


pco_gas_controller.configure()
pco_gas = Valve("pco_gas", pco_gas_controller)

kb_gas_controller.configure()
kb_gas = Valve("kb_gas", kb_gas_controller)

valves = InterlockedValves([pco_gas, kb_gas], eh_non_critical_jy, waiter)

shutter.configure()

eh_shutter_jy = GasSavingShutter("eh_shutter", shutter, eh1_searched_locked_jy, valves)
del shutter

