from gda.device.scannable import PseudoDevice

class FlipperClass4a(PseudoDevice):
	'''
	dev=FlipperClass4(name,ppdevice)
	uses p100k and ic1 with specified pp device
	input: [energy,offset on ppth relative to centre,number of flipping cycles,number of samples per cycle
	in: 'energy','offsetp','offsetn','ncycles','ncounts'
	extra: 'total','diff','ratio','totalref','diffref','ratioref'
	'''

	def __init__(self,name,ppdev):
		self.setName(name)
		self.ppdev=ppdev
		self.setLevel(10)
		self.setInputNames(['energy','offsetp','offsetn','ncycles','ncounts'])
		self.setExtraNames(['total','diff','ratio','totalref','diffref','ratioref'])
		self.setOutputFormat(['%.3f','%.4f','%.4f','%.0f','%.1f','%.1f','%.1f','%.4f','%.1f','%.1f','%.4f'])
		self.energy = 0
		self._offsetp = 0
		self._offsetn = 0
		self.ncycles = 0
		self.ncounts = 0

	def getPosition(self):
		return [self.energy,self._offsetp,self._offsetn,self.ncycles,self.ncounts,self.tot,self.diff,self.ratio,self.tot_ref,self.diff_ref,self.ratioref]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
		self.energy = newpos[0]
		self._offsetp=newpos[1]
		self._offsetn=newpos[2]
		self.ncycles=newpos[3]
		self.ncounts=newpos[4]
		cup = 0
		cdown = 0
		ctrefup = 0
		ctrefdown = 0
		for i in range(int(self.ncycles)):
			self.ppdev([self.energy,self._offsetp]); w(.5);
			for j in range(int(self.ncounts)):
				pil(1); 
				ic1; 
				pilout=pil(); cts=pilout[2];
				mon=ic1()				
				cup+=cts
				ctrefup+=cts/mon
			self.ppdev([self.energy,self._offsetn]); w(.5);
			for j in range(int(self.ncounts)):
				pil(1); 
				ic1; 
				pilout=pil(); cts=pilout[2];
				mon=ic1()				
				cdown+=cts
				ctrefdown+=cts/mon

		self.tot = cup+cdown
		self.diff = cup-cdown
		self.tot_ref = ctrefup+ctrefdown
		self.diff_ref= ctrefup-ctrefdown
		try:	
			self.ratio = self.diff/self.tot
		except:
			self.ratio = 0
		try: 
			self.ratioref = self.diff_ref/self.tot_ref
		except:
			self.ratioref =0
