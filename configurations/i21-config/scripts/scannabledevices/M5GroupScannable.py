'''
A Scannable class that moves armtth, m5tth, sgmpitch, m5hqx and m5hqry concurrently for a single given position. 
Polynomial coefficients are required to calculate the position for sgmpitch, m5hqry, and m5hqx, these are defined in the constructor.
Further requirements implemented are:
1. m5hqx can only move after m5hqry motion completed
2. this scannable should be supported in 'move' command just like 'armtth'

Created on Feb 17, 2021
Added sgmpitch on 14 May 2024

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from org.slf4j import LoggerFactory

INPUT_MESSAGE = "Input must be a list of coefficients."

def evaluate_ploynomial(lst, x):
    return sum((x**power) * coeff for power, coeff in enumerate(lst))

class M5GroupScannable(ScannableMotionBase):
    '''
    A group scannable dedicated to two theta motion in I21. It has I21 armtth motion specific logics.
    '''

    def __init__(self, name, armtth, m5tth, sgmpitch, m5hqry, m5hqx, m5hqry_coeffs = None, m5hqx_coeffs = None, sgmpitch_coeffs = None):
        '''
        create a wrapper scannable that moves ARM tth, M5 tth, m5hqry, and m5hqx for a single tth position input, it returns positions of these motors on completion.
        '''
        self.logger = LoggerFactory.getLogger(M5GroupScannable.__class__.__name__)
        self.setName(name)
        self.setInputNames([armtth.getName()])
        self.setExtraNames([m5tth.getName(), sgmpitch.getName(), m5hqry.getName(), m5hqx.getName()])
        self.setOutputFormat([armtth.getOutputFormat()[0], m5tth.getOutputFormat()[0], sgmpitch.getOutputFormat()[0], m5hqry.getOutputFormat()[0], m5hqx.getOutputFormat()[0]])
        self.armtth = armtth
        self.m5tth = m5tth
        self.sgmpitch = sgmpitch
        self.m5hqry = m5hqry
        self.m5hqx = m5hqx
        self.m5hqry_coeffs = m5hqry_coeffs
        self.m5hqx_coeffs = m5hqx_coeffs
        self.sgmpitch_coeffs = sgmpitch_coeffs
        self.markbusy = False

    def asynchronousMoveTo(self, newpos):
        newpos = float(newpos)
        try:
            self.markbusy = True  # need to set this to prevent race condition due to network communication and PV request response times.
            print("moving armtth to %s ..." % newpos)
            self.armtth.asynchronousMoveTo(newpos) 
            print("moving m5tth to %s ..." % newpos)
            self.m5tth.asynchronousMoveTo(newpos)
            sgmpicth_val = evaluate_ploynomial(self.sgmpitch_coeffs, newpos)
            print("moving sgmpitch to %s ..." % sgmpicth_val)
            self.sgmpitch.asynchronousMoveTo(sgmpicth_val)
            m5hqry_val = evaluate_ploynomial(self.m5hqry_coeffs, newpos)
            m5hqx_val = evaluate_ploynomial(self.m5hqx_coeffs, newpos)
            print("moving m5hqry to %s ..." % (m5hqry_val))
            self.m5hqry.asynchronousMoveTo(m5hqry_val)
            print("waiting for m5hqry to complete ...")
            self.m5hqry.waitWhileBusy()
            print("moving m5hqx to %s ..." % (m5hqx_val))
            self.m5hqx.asynchronousMoveTo(m5hqx_val)
        except Exception, e:
            self.logger.error("Exception throws in asynchronousMoveTo ", e)
            raise e
        finally:
            self.markbusy = False

    def getPosition(self):
        return float(self.armtth.getPosition()), float(self.m5tth.getPosition()), float(self.sgmpitch.getPosition()), float(self.m5hqry.getPosition()), float(self.m5hqx.getPosition())

    def isBusy(self):
        return self.markbusy or self.armtth.isBusy() or self.m5tth.isBusy() or self.m5hqry.isBusy() or self.m5hqx.isBusy() or self.sgmpitch.isBusy()

    def stop(self):
        self.armtth.stop()
        self.m5tth.stop()
        self.sgmpitch.stop()
        self.m5hqry.stop()
        self.m5hqx.stop()

    def showCoefficients(self):
        print("Polynomial coefficients for  m5hqx: %r" % (self.m5hqx_coeffs))
        print("Polynomial coefficients for  m5hqry: %r" % (self.m5hqry_coeffs))
        print("Polynomial coefficients for  sgmpitch: %r" % (self.sgmpitch_coeffs))

    def setCoefficientsForM5hqx(self, value):
        if not isinstance(value, list):
            raise ValueError(INPUT_MESSAGE)
        self.m5hqx_coeffs = [float(x) for x in value]

    def setCoefficientsForM5hqry(self, value):
        if not isinstance(value, list):
            raise ValueError(INPUT_MESSAGE)
        self.m5hqry_coeffs = [float(x) for x in value]

    def setCoefficientsForSgmpitch(self, value):
        if not isinstance(value, list):
            raise ValueError(INPUT_MESSAGE)
        self.sgmpitch_coeffs = [float(x) for x in value]

from gdaserver import armtth,m5tth,m5hqry,m5hqx  # @UnresolvedImport
alltth = M5GroupScannable("alltth", armtth, m5tth, sgmpitch, m5hqry, m5hqx, m5hqry_coeffs = [342.9979644425, -0.2487741425, 0.0018219019], m5hqx_coeffs = [-363.5691038104, -2.1936146304, 0.0074169737], sgmpitch_coeffs = [2.30846094e+00,-1.45880208e-03,3.51562500e-05,-4.11458333e-07,2.34375000e-09,-5.20833333e-12])  # @UndefinedVariable

