from gda.device.scannable import PseudoDevice

class hkl_mod(PseudoDevice):
	def __init__(self, name, anglecalcPD,gethklPD):
		self.setName(name);
		self.setLevel(6)
		self.setInputNames(['h','k','l'])
		self.setOutputFormat(['%6f','%6f','%6f'])
		self.anglecalcPD=anglecalcPD
		self.gethklPD=gethklPD

	def asynchronousMoveTo(self,new_position):
		self.anglecalcPD(new_position)
		gam.asynchronousMoveTo(self.anglecalcPD.angles.Gamma)
		mu.asynchronousMoveTo(self.anglecalcPD.angles.Mu)
		delta.asynchronousMoveTo(self.anglecalcPD.angles.Delta)
		eta.asynchronousMoveTo(self.anglecalcPD.angles.Eta)
		phi.asynchronousMoveTo(self.anglecalcPD.angles.Phi)
		chi.asynchronousMoveTo(self.anglecalcPD.angles.Chi)

	def isBusy(self):
		return (gam.isBusy() or mu.isBusy() or delta.isBusy() or eta.isBusy() or phi.isBusy() or chi.isBusy()) 

	def getPosition(self):
		return self.gethklPD.getPosition()
 
class hkl_h(hkl_mod):
	def asynchronousMoveTo(self,new_position):
		self.anglecalcPD(new_position)
		gam.asynchronousMoveTo(self.anglecalcPD.angles.Gamma)
		mu.asynchronousMoveTo(self.anglecalcPD.angles.Mu)
		phi.asynchronousMoveTo(self.anglecalcPD.angles.Phi)
		chi.asynchronousMoveTo(self.anglecalcPD.angles.Chi)
 
hkl2=hkl_h('hkl_h', hkl_calc, hkl)
