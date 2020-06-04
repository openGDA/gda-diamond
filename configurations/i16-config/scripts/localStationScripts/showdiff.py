from gda.device.scannable import ScannableMotionBase

class ShowDiff(ScannableMotionBase):
	'''
	Device to read Diff encoder positions
	see also: showdiff_new.m
	'''
	def __init__(self, name, comchan='BL16I-MO-DIFF-01:', help=None):
		self.name = name		
		self.inputNames = []
		self.extraNames = ['kphi_en', 'kap_en', 'kth_en', 'mu_en','delta_en','gam_en']
		self.outputFormat =['%4.6f'] * 6
		self.level = 7
		self.pvs = PvManager(pvroot = comchan)
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help 

	def getPosition(self):
		#caput('BL16I-DI-COR-01:TIFF:Capture',1)
		kphi_en = (float(self.pvs['SAMPLE:KPHI.REP'].caget())*float(self.pvs['SAMPLE:KPHI.ERES'].caget()))+float(self.pvs['SAMPLE:KPHI.OFF'].caget())
		kap_en = (float(self.pvs['SAMPLE:KAPPA.REP'].caget())*float(self.pvs['SAMPLE:KAPPA.ERES'].caget()))+float(self.pvs['SAMPLE:KAPPA.OFF'].caget())
		kth_en = (float(self.pvs['SAMPLE:KTHETA.REP'].caget())*float(self.pvs['SAMPLE:KTHETA.ERES'].caget()))+float(self.pvs['SAMPLE:KTHETA.OFF'].caget())
		mu_en = (float(self.pvs['SAMPLE:MU.REP'].caget())*float(self.pvs['SAMPLE:MU.ERES'].caget()))+float(self.pvs['SAMPLE:MU.OFF'].caget())
		delta_en = (float(self.pvs['ARM:DELTA.REP'].caget())*float(self.pvs['ARM:DELTA.ERES'].caget()))+float(self.pvs['ARM:DELTA.OFF'].caget())
		gam_en = (float(self.pvs['ARM:GAMMA.REP'].caget())*float(self.pvs['ARM:GAMMA.ERES'].caget()))+float(self.pvs['ARM:GAMMA.OFF'].caget())
		return [kphi_en,kap_en,kth_en,mu_en,delta_en,gam_en]
	def isBusy(self):
		return False
showdiff=ShowDiff("showdiff")

class ShowDiffDiff(ScannableMotionBase):
	'''
	Same as ShowDiff but subtracts first value in scan for easy plotting
	'''
	def __init__(self, name, comchan='BL16I-MO-DIFF-01:', help=None):
		self.name = name		
		self.inputNames = []
		self.extraNames = ['kphi_diff', 'kap_diff', 'kth_diff', 'mu_diff','delta_diff','gam_diff']
		self.outputFormat =['%4.6f'] * 6
		self.level = 7
		self.pvs = PvManager(pvroot = comchan)
		self.startpositions=[0,0,0,0,0,0] #default positions if no scan started
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
	
	def atScanStart(self):
		self.startpositions=self.getDiffPosition()

	def getDiffPosition(self):
		#caput('BL16I-DI-COR-01:TIFF:Capture',1)
		kphi_en = (float(self.pvs['SAMPLE:KPHI.REP'].caget())*float(self.pvs['SAMPLE:KPHI.ERES'].caget()))+float(self.pvs['SAMPLE:KPHI.OFF'].caget())
		kap_en = (float(self.pvs['SAMPLE:KAPPA.REP'].caget())*float(self.pvs['SAMPLE:KAPPA.ERES'].caget()))+float(self.pvs['SAMPLE:KAPPA.OFF'].caget())
		kth_en = (float(self.pvs['SAMPLE:KTHETA.REP'].caget())*float(self.pvs['SAMPLE:KTHETA.ERES'].caget()))+float(self.pvs['SAMPLE:KTHETA.OFF'].caget())
		mu_en = (float(self.pvs['SAMPLE:MU.REP'].caget())*float(self.pvs['SAMPLE:MU.ERES'].caget()))+float(self.pvs['SAMPLE:MU.OFF'].caget())
		delta_en = (float(self.pvs['ARM:DELTA.REP'].caget())*float(self.pvs['ARM:DELTA.ERES'].caget()))+float(self.pvs['ARM:DELTA.OFF'].caget())
		gam_en = (float(self.pvs['ARM:GAMMA.REP'].caget())*float(self.pvs['ARM:GAMMA.ERES'].caget()))+float(self.pvs['ARM:GAMMA.OFF'].caget())
		return [kphi_en,kap_en,kth_en,mu_en,delta_en,gam_en]

	def getPosition(self):
		s=self.startpositions
		raw=self.getDiffPosition()
		return [raw[0]-s[0], raw[1]-s[1],raw[2]-s[2],raw[3]-s[3],raw[4]-s[4],raw[5]-s[5]]

	def isBusy(self):
		return False
showdiffdiff=ShowDiffDiff("showdiffdiff")
