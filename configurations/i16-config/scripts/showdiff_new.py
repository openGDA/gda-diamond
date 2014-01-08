#modified version - output names derived from PV name to allow multiple samples during scan

class ShowDiff(PseudoDevice):
	'''
	Device to read Diff encoder positions
	need to give an input value e.g. pos showdiff 1 in order to force levels to work correctly in scans
	see also: showdiff.m
	'''
	def __init__(self, name, comchan='BL16I-MO-DIFF-01:', help=None):
		self.name = name		
		self.inputNames = []
		self.extraNames = ['kphi_'+self.name, 'kap_'+self.name, 'kth_'+self.name, 'mu_'+self.name,'delta_'+self.name,'gam_'+self.name]
		self.outputFormat =['%4.6f'] * 7
		self.level = 7
		self.pvs = PvManager(pvroot = comchan)
		self.setInputNames(['inval_'+self.name])
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help

	def asynchronousMoveTo(self,dummy_position):
		self.inval=dummy_position
		self.kphi_en = (float(self.pvs['SAMPLE:KPHI.REP'].caget())*float(self.pvs['SAMPLE:KPHI.ERES'].caget()))+float(self.pvs['SAMPLE:KPHI.OFF'].caget())
		self.kap_en = (float(self.pvs['SAMPLE:KAPPA.REP'].caget())*float(self.pvs['SAMPLE:KAPPA.ERES'].caget()))+float(self.pvs['SAMPLE:KAPPA.OFF'].caget())
		self.kth_en = (float(self.pvs['SAMPLE:KTHETA.REP'].caget())*float(self.pvs['SAMPLE:KTHETA.ERES'].caget()))+float(self.pvs['SAMPLE:KTHETA.OFF'].caget())
		self.mu_en = (float(self.pvs['SAMPLE:MU.REP'].caget())*float(self.pvs['SAMPLE:MU.ERES'].caget()))+float(self.pvs['SAMPLE:MU.OFF'].caget())
		self.delta_en = (float(self.pvs['ARM:DELTA.REP'].caget())*float(self.pvs['ARM:DELTA.ERES'].caget()))+float(self.pvs['ARM:DELTA.OFF'].caget())
		self.gam_en = (float(self.pvs['ARM:GAMMA.REP'].caget())*float(self.pvs['ARM:GAMMA.ERES'].caget()))+float(self.pvs['ARM:GAMMA.OFF'].caget())

	def getPosition(self):
		return [self.inval,self.kphi_en,self.kap_en,self.kth_en,self.mu_en,self.delta_en,self.gam_en]

	def isBusy(self):
		return False

sd=ShowDiff("sd7")	#level 7
sd5=ShowDiff("sd5"); sd5.setLevel(5);	 #level 5 (below hkl)
sd10=ShowDiff("sd10"); sd10.setLevel(10); #level 10 (above pil, t)
