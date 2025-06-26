'''
Smart amplifiers which automatically adjust their gain
'''
from gda.device.scannable import ScannableBase

class SmartAmplifier(ScannableBase):
    '''
    Base class decreases or increases gain accordingly at the start of every point in a scan.
    Child classes need to implement decrease_gain, increase_gain, reset_gain and rawGetPosition.
    '''
    def __init__(self, name, signal_scannable, lo_threshold, hi_threshold):
        self.setName(name)
        self.signal_scannable = signal_scannable
        self.lo_threshold = lo_threshold
        self.hi_threshold = hi_threshold
        self.setLevel(6)  # should be higher than moving scannables' and lower than the detector's
        
    def atScanStart(self):
        ''' Reset gain every new scan '''
        self.reset_gain()
    
    def atLevelStart(self):
        '''
        This will trigger every point of the scan,
        after scannables have moved, before detectors are exposed
        NB: as long as this device's level is greater than the scannables', and lower than the detector's
        '''
        self.adjust_gain_if_necessary()

    def adjust_gain_if_necessary(self):
        while True:
            signal = self.signal_scannable.getPosition()
        
            if signal > self.hi_threshold:
                if not self.decrease_gain():
                    break
            elif signal < self.lo_threshold:
                if not self.increase_gain():
                    break
            else:
                break

    def decrease_gain(self):
        '''
        Decrease gain and return True if successful, else False
        '''
        pass
    
    def increase_gain(self):
        '''
        Increase gain and return True if successful, else False
        '''
        pass

    def reset_gain(self):
        '''
        Set initial gain
        '''
        pass

    def rawAsynchronousMoveTo(self, position):
        ''' Should not be moved '''

    def isBusy(self):
        ''' Not needed, nothing should be operating simultaneously '''
        return False


class Keithley(SmartAmplifier):
    
    '''
    This amplifier increases and decreases the gain by one order of magnitude.
    '''
    
    def __init__(self, name, amplifier, signal_scannable, lo_threshold=0, hi_threshold=10):
        '''
        @param amplifier instance of scannable.hw.keithley.KeithleyGain
        '''
        SmartAmplifier.__init__(self, name, signal_scannable, lo_threshold, hi_threshold)
        self.amplifier = amplifier
        self.initial_gain = 10  # exponent i.e. 10^10 V/A
        self.selection = self.initial_gain
    
    def apply_selection(self):
        self.amplifier.moveTo(self.selection)
    
    def decrease_gain(self):
        '''
        Decrease gain by one order of magnitude
        '''
        if self.selection > 3:
            self.selection -= 1
            self.apply_selection()
            return True
        else:
            print("At max sensitivity!")
            return False
    
    def increase_gain(self):
        '''
        Increase gain by one order of magnitude
        '''
        if self.selection < 10:
            self.selection += 1
            self.apply_selection()
            return True
        else:
            print("At min sensitivity!")
            return False
    
    def reset_gain(self):
        self.selection = self.initial_gain
        self.apply_selection()
    
    def rawGetPosition(self):
        return "10^%d" % self.selection


class Stanford(SmartAmplifier):
    '''
    Toggle sensitivity by 1 order of magnitude using a value PV and a units PV
    '''
    def __init__(self, name, amplifier_val, amplifier_units, signal_scannable, lo_threshold=0, hi_threshold=6.2):
        '''
        @param amplifier_val: scannable.hw.stanford_sensitivity.StanfordSensitivity (moveTo takes the actual value)
        @param amplifier_units: scannable.hw.stanford_unit.StanfordUnit (moveTo takes the enum index)
        '''
        SmartAmplifier.__init__(self, name, signal_scannable, lo_threshold, hi_threshold)
        self.amp_val = amplifier_val
        self.amp_units = amplifier_units
        
        self.vals = [1, 10, 100]
        self.max_unit = 3 # pA/V, nA/V, uA/V, mA/V
        self.initial_val_index = 0 # i.e. 1
        self.initial_unit_index = 1 # i.e. nA/V
        
        self.selected_val_index = self.initial_val_index
        self.selected_unit_index = self.initial_unit_index

    def apply_selection(self):
        '''
        StanfordSensitivity takes the actual value i.e. 1, 10 or 100;
        StanfordUnit takes the enum index (enums defined in increasing order, so [0..3])
        '''
        self.amp_val.moveTo(self.vals[self.val_index])
        self.amp_units.moveTo(self.unit_index)
    
    def decrease_gain(self):
        ''' i.e. increase sensitivity '''
        if self.selected_val_index < len(self.vals) - 1:
            # increase by order of magnitude in same units
            self.selected_val_index += 1
        elif self.selected_unit_index < self.max_unit:
            # increase units
            self.selected_unit_index += 1
            self.selected_val_index = 0
        else:
            print("At max sensitivity!")
            return False
        self.apply_selection()
        return True

    def increase_gain(self):
        ''' i.e. decrease sensitivity '''
        if self.selected_val_index > 0:
            self.selected_val_index -= 1
        elif self.selected_unit_index > 0:
            self.selected_unit_index -= 1
            self.selected_val_index = len(self.vals) - 1
        else:
            print("At min sensitivity!")
            return False
        self.apply_selection()
        return True

    def reset_gain(self):
        self.selected_val_index = self.initial_val_index
        self.selected_unit_index = self.initial_unit_index
        self.apply_selection()
    
    def rawGetPosition(self):
        ''' Concatenate amplifier sensitivity (value + units) '''
        return "%s %s" % (self.amp_val.getPosition(), self.amp_units.getPosition())
