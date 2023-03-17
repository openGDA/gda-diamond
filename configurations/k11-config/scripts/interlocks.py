"""
Creates three interlock monitors which are then wrapped in Java scannable objects and grouped as 'interlocks'
"""

from java.lang import Integer, Math  # @UnresolvedImport
from java.util.concurrent import TimeoutException  # @UnresolvedImport
from gda.device import DeviceException  # @UnresolvedImport
from gda.device.monitor import MonitorBase # @UnresolvedImport
from gda.epics import LazyPVFactory # @UnresolvedImport
from k11_utilities import is_live, JPredicate


class EpicsInterlock(MonitorBase):
    def __init__(self, name, bitfield_pv, reverse=False):
        """
        By default, this monitor will return True if all bits are set.
        In some cases, we may want to return True if all bits are unset:
        this is configured by setting reverse=True 
        """
        self.setName(name)
        self.bitfield_pv = LazyPVFactory.newIntegerPV(bitfield_pv)
        self.bitfield_pv.addObserver(lambda source, arg: self.notifyIObservers(self, self.getPosition()))
        self.reverse = reverse
    
    def get_test(self):
        return (lambda x: x == 0) if self.reverse else (lambda x: x > 0)
    
    def mask(self, bitfield, bit):
        return bitfield & int(Math.pow(2, bit))
    
    def bits(self, bitfield):
        """ how many bits? """
        return len(Integer.toBinaryString(bitfield))
    
    def bitfield_to_boolean(self, bitfield):
        test = self.get_test()
        return all([test(self.mask(bitfield, bit)) for bit in range(self.bits(bitfield))])
    
    def rawGetPosition(self):
        bitfield = self.bitfield_pv.get()
        return self.bitfield_to_boolean(bitfield)
    
class LatchEpicsInterlock(EpicsInterlock):
    def __init__(self, name, pv_prefix, bit_name_to_number, reverse=False):
        EpicsInterlock.__init__(self, name, pv_prefix + ":RAWILK", reverse)
        
        self.latched_bitfield_pv = LazyPVFactory.newIntegerPV(pv_prefix + ":ILK")
        self.reset_pv = LazyPVFactory.newIntegerPV(pv_prefix + ":RESET.PROC")
        self.bit_dict = bit_name_to_number
    
    def can_reset(self, ignored_bit_names):
        bitfield = self.latched_bitfield_pv.get()
        bits_to_ignore = [self.bit_dict.get(bitname) for bitname in ignored_bit_names]
        
        test = self.get_test()
        
        return all([test(self.mask(bitfield, bit)) for bit in range(self.bits(bitfield)) if bit not in bits_to_ignore])

    def reset(self, ignored_bit_names):
        # 1) check latched bits - do not proceed if any latch bits other than ignored are set
        if self.can_reset(ignored_bit_names):
            
            try:
            
                # 2) wait for current interlock bits to be set (can take > 5 seconds!)
                self.bitfield_pv.waitForValue(JPredicate(lambda bitfield: self.bitfield_to_boolean(bitfield)), 10)
                
                # 3) hit reset button
                self.reset_pv.putWait(1)
                
                # 4) wait for no latched bits i.e. the result of reset operation
                self.latched_bitfield_pv.waitForValue(JPredicate(lambda bitfield: self.bitfield_to_boolean(bitfield)), 10)
                
            except TimeoutException:
                raise DeviceException("%s interlock not cleared in time" % self.getName())
        else:
            raise DeviceException("Cannot reset - other fields not cleared")


class DummyInterlock(MonitorBase):
    
    def __init__(self, name):
        self.cleared = True
        self.setName(name)
    
    def rawGetPosition(self):
        return self.cleared
    
    def set_cleared(self, cleared):
        self.cleared = cleared
    
    def reset(self, ignored):
        self.cleared = True
    
if is_live():
    eh_non_critical_jy = LatchEpicsInterlock(name="eh_non_critical_jy",
                                                 pv_prefix="BL11K-VA-VLVCC-03:ILK01",
                                                 bit_name_to_number={"kb_gas": 4, "pco_gas": 9})
    
    eh1_searched_locked_jy = EpicsInterlock(name="eh1_searched_locked_jy",
                                            bitfield_pv="BL11K-PS-IOC-01:M11:LOP",
                                            reverse=True)
    
else:
    eh_non_critical_jy = DummyInterlock("eh_non_critical_jy")
    eh1_searched_locked_jy = DummyInterlock("eh1_searched_locked_jy")
