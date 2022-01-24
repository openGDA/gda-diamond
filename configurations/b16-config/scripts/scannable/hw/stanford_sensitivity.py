from gda.device.scannable import ScannableMotionBase
from gdascripts.scannable.epics.PvManager import PvManager

class StanfordSensitivity(ScannableMotionBase):

    def __init__(self, name, root_pv):
        self.name = name
        self.inputNames = ['sensitivity']
        self.outputFormat = ['%i']
        self.SENSITIVITY = 'SEL1'
        self.pvs = PvManager([self.SENSITIVITY], root_pv)
        self.pvs.configure()
        self.sensitivityFromValue = { 0: 1,	1: 2,	2: 5,	3: 10,	4: 20,	5: 50,	6: 100,	7: 200,	8: 500}
        self.valueFromSensitivity = dict((v, k) for k, v in self.sensitivityFromValue.iteritems())
        sensitivities = self.valueFromSensitivity.keys()
        sensitivities.sort()
        self.__doc__ = """
Example use:

	pos %s
	pos %s <sensitivity>

where <sensitivity> is one of %r""" % (name, name, sensitivities)

    def rawAsynchronousMoveTo(self, sensitivity):
        try:
            value = self.valueFromSensitivity[sensitivity]
        except:
            sensitivities = self.valueFromSensitivity.keys()
            sensitivities.sort()
            print "Invalid sensitivity %r select one of %r" % (sensitivity, sensitivities)
            return
        self.pvs[self.SENSITIVITY].caput(value)

    def isBusy(self):
        return False

    def rawGetPosition(self):
        value = self.pvs[self.SENSITIVITY].caget()
        try:
            sensitivity = self.sensitivityFromValue[int(value)]
            return sensitivity
        except:
            values = self.sensitivityFromValue.keys()
            values.sort()
            print "Invalid value %r should be one of %r" % (value, values)
