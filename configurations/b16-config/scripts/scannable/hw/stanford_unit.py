from gda.device.scannable import ScannableMotionBase
from gdascripts.scannable.epics.PvManager import PvManager

class StanfordUnit(ScannableMotionBase):

    def __init__(self, name, root_pv):
        self.name = name
        self.inputNames = ['unit']
        self.outputFormat = ['%s']
        self.UNIT = 'SEL2'
        self.pvs = PvManager([self.UNIT], root_pv)
        self.pvs.configure()
        self.unitFromValue = { 0: 'pA/V',	1: 'nA/V',	2: 'uA/V',	3: 'mA/V'}
        self.valueFromUnit = dict((v.lower(), k) for k, v in self.unitFromValue.iteritems())
        self.__doc__ = """
Example use:

	pos %s
	pos %s <unit>

where <unit> is a string or an integer from %r""" % (name, name, self.unitFromValue)

    def rawAsynchronousMoveTo(self, unit):
        if isinstance(unit, int) and unit in self.valueFromUnit.values():
            value = unit
        else:
            try:
                value = self.valueFromUnit[unit.lower()]
            except:
                units = self.unitFromValue.values()
                units.sort()
                print "Invalid unit '%r' select a string or integer from %r" % (unit, self.unitFromValue)
                return
        self.pvs[self.UNIT].caput(value)

    def isBusy(self):
        return False

    def rawGetPosition(self):
        value = self.pvs[self.UNIT].caget()
        try:
            unit = self.unitFromValue[int(value)]
            return unit
        except:
            values = self.unitFromValue.keys()
            values.sort()
            print "Invalid value %r should be one of %r" % (value, values)
