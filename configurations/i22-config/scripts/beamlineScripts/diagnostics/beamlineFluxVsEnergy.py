import java
import gda.device.scannable.ScannableBase
from math import pow
from java.lang import String

"""
    Purpose:       To measure the flux on the calibrated diode.
                   Only work with d10d1, d10d2 and bsdiode
    running:       type flux = CalibratedDiode() in jython terminal at >>> prompt
                   Normally, the line is written at the end of the script so no need to do it in the jython terminal panel
    Author:        M. Malfois
    Date:          23 April 2013
    
"""

class CalibratedDiode(gda.device.scannable.PseudoDevice):

	""" Constructor method give the device a name - in this case calibratedDiode"""
	def __init__(self , femto ):
		self.name = "Calibrated diode"
		self.coefficients = []
		self.femto = femto
		self.gain = self.setGain(femto)
		self.setInputNames(["flux"])
		self.setExtraNames(["voltage", "gain" , "femto"])
		self.setOutputFormat(["%5.3e", "%6.3f", "%5.3e" , "%s"])

#                            fit y = a x*x + bx + c
#                            E1, E2: Energy range
#                                			    E1  ,  E2 ,    a     ,   b     ,   c
		self.coefficients.append(DiodeCoefficients(  3.60,  4.50, -0.015556, 0.158222, -0.158) )
		self.coefficients.append(DiodeCoefficients(  4.50,  5.50, -0.006000, 0.075000,  0.023) )
		self.coefficients.append(DiodeCoefficients(  5.50,  6.50, -0.002000, 0.031000,  0.144) )
		self.coefficients.append(DiodeCoefficients(  6.50,  7.50,  0.000000, 0.004000,  0.235) )
		self.coefficients.append(DiodeCoefficients(  7.50,  9.00,  0.000000, 0.000000,  0.265) )
		self.coefficients.append(DiodeCoefficients(  9.00, 12.50, -0.001371, 0.020057,  0.195571) )
		self.coefficients.append(DiodeCoefficients( 12.50, 17.50,  0.000400,-0.031000,  0.557) )
		self.coefficients.append(DiodeCoefficients( 17.50, 22.50,  0.000648,-0.038300,  0.6088) )

	""" This device is never busy """
	def isBusy(self):
		return 0

	""" Return the flux, the voltage and the gain position"""
	def getPosition(self):
		e = float( bkeV.getPosition() )
		coefficient = self.getCoefficient(e)
		energyJoule = e * 1000.0 * 1.60218E-19
		voltage = self.femto.getPosition()
		if ( voltage < 0.001 ):
			voltage = 0.0
		gainText = String(self.gain.getPosition())
		gain = pow ( 10 , float(gainText.substring(3,4)) )
		amp = voltage / gain
		w = amp/coefficient
		flux = w / energyJoule
		return [flux,voltage,gain,str(self.femto)]
    
	""" Calibrated diode is not moveable """
	def asynchronousMoveTo(self,X):
		return

	def getCoefficient(self,e):
		n = len(self.coefficients)
		for i in range (n):
			coeff = self.coefficients[i]			
			if coeff.isSelected(e) :
				return coeff.getValue(e)
		return -1
         
	def setFemto(self, femto):
		self.femto = femto
		self.gain = self.setGain(femto)
		return
	
	def getFemto(self):
		return self.femto

	def setGain(self, femto):
		if ( femto.equals(d10d1) ):
			return d10d1gain
		if ( femto.equals(d10d2) ):
			return d10d2gain
		if ( femto.equals(bsdiode) ):
			return bsdiodegain
		raise DeviceException("No gain defined for "+femto.getName())

class DiodeCoefficients:

    """ Constructor method give the initial values"""
    def __init__(self, energyStart, energyEnd, a, b, c):
		self.name = "Coefficients"
		self.energyStart = energyStart
		self.energyEnd = energyEnd
        # y = a x*x + bx + c
		self.a = a
		self.b = b
		self.c = c

    def isSelected(self,e):
		if ( e >= self.energyStart and e < self.energyEnd ):
			return True
		return False
        
    def getValue(self,e):
		return self.a*e*e + self.b*e + self.c

    def test(self , start, end , step):
		energy_position = start 
		while ( energy_position <= end ):
			position = self.getFlux(energy_position)
			print str(energy_position) + " , " + str(1./position) 
			energy_position = energy_position + step
		print "Done"


flux=CalibratedDiode( d10d1 )


