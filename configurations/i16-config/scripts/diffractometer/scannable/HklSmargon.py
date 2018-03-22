from gda.device.scannable.scannablegroup import ScannableMotionWithScannableFieldsBase
class HklSmargon(ScannableMotionWithScannableFieldsBase):
	'''
	'''
	def __init__(self,name,euler,rs,cal,EDi,az):
		'''
		euler must have input fields: ('phi','chi','eta','mu','delta','gam')
		'''
		self.setName(name)
		self.setInputNames(['h', 'k','l'])
		self.setOutputFormat(["%4.4f","%4.4f","%4.4f"])
		
		self.euler = euler
		self.rs = rs
		self.cal= cal
		self.EDi = EDi
		self.az=az
		self.autoCompletePartialMoveToTargets = True

	def isBusy(self):
		return self.euler.isBusy()
	
	def waitWhileBusy(self):
		return self.euler.waitWhileBusy()

	def rawGetPosition(self,muin=None,etain=None,chiin=None,phiin=None,deltain=None,gammain=None,UB=None,wavelength=None):	
		(phi,chi,eta,mu,delta,gam) = self.euler.getPosition()
		#-->
		if phiin: phi = phiin
		if chiin: chi = chiin
		if etain: eta = etain
		if muin: mu = muin
		if deltain: delta= deltain
		if gammain: gam = gammain
		#<--		
		hkl = self.rs.calcHKL(mu,eta,chi,phi,delta,gam,UB,wavelength)
		h = hkl.get(0,0)
		k = hkl.get(1,0)
		l = hkl.get(2,0)
		return [h,k,l]
	
	def stop(self):
		self.euler.stop()
		ScannableMotionWithScannableFieldsBase.stop(self)
		
	def atCommandFailure(self):
		ScannableMotionWithScannableFieldsBase.atCommandFailure(self)
	
	def getFieldPosition(self, index):
		return self.getPosition()[index]
	
	def hklToEuler(self, hklPos):
		hklPos = map(float, hklPos)
		#hklPos = ArrayUtils.toPrimitive(hklPos) #TODO: why?
		if self.EDi.getMode() == 3: 
			angles = self.cal.getAngles(self.EDi.getMode(),hklPos,None,self.az.getPsi())
		else:
			angles = self.cal.getAngles(self.EDi.getMode(),hklPos)
		return (angles.Phi,angles.Chi,angles.Eta,angles.Mu,angles.Delta,angles.Gamma)

	def rawAsynchronousMoveTo(self, hklPos):
		eulerPos = self.hklToEuler(hklPos)
		self.euler.asynchronousMoveTo( eulerPos )

	def simulateMoveTo(self, hklPos):
		(phi,chi,eta,mu,delta,gam) = self.hklToEuler(hklPos)
		(oldphi,oldchi,oldeta,oldmu,olddelta,oldgam) = self.euler.getPosition()
		result = "Euler would move from/to\n"
		result += "   phi  : % 5.5f --> % 5.5f\n" % (oldphi,phi)
		result += "   chi : % 5.5f --> % 5.5f\n" % (oldchi,chi)
		result += "   eta   : % 5.5f --> % 5.5f\n" % (oldeta,eta)
		result += "   mu   : % 5.5f --> % 5.5f\n" % (oldmu,mu)
		result += "   delta: % 5.5f --> % 5.5f\n" % (olddelta,delta)
		result += "   gam  : % 5.5f --> % 5.5f\n" % (oldgam,gam)
		
		result +="\n"
		result += self.euler.simulateMoveTo((phi,chi,eta,mu,delta,gam))
		
		return result
	


