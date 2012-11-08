


class FlipperClass11(PseudoDevice):
	'''
	dev=FlipperClass11(name, ppdevice, pilatus, pilatus_roi)
	uses pilatus and ic1 with specified pp device
	in: 'energy','offset','counttime','cycles'
	firstnum=first pil file number
	sequence=(+--+)*ncycles
	extra: 'firstnum','ic1ratio'
	'''
	def __init__(self,name,ppdev,pilatus,pilatus_roi):
		self.setName(name)
		self.ppdev=ppdev
		self.pil=pilatus
		self.setLevel(10)
		self.setInputNames(['energy','offset','counttime','ncycles'])
		self.setExtraNames(['filenum','ic1ratio','fracdiff','norm_sum','norm_diff'])
		self.setOutputFormat(['%.3f','%.4f','%.1f','%.0f','%.0f','%.4f','%.5f','%.1f','%.1f'])
		self.energy = 0
		self.offsetval = 0
		self.counttime=0
		#self.rootfilename=rootfilename
		#self.filename=self.rootfilename
		self.roi=pilatus_roi

	def getPosition(self):
		return [self.energy,self.offsetval,self.counttime,self.cycles,self.filenum, self.ic1ratio, self.fracdiff, self.sum, self.diff]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
		self.filenum=self.pil()[1]+1

		self.energy = newpos[0]
		self.offsetval=newpos[1]
		self.counttime=newpos[2]
		self.cycles=newpos[3]

		mon_neg=mon_pos=roi_neg=roi_pos=0

		for n in range(int(self.cycles)):
			self.ppdev([self.energy,-self.offsetval]); w(.5);
			self.pil(self.counttime); 
			roi_neg+=self.roi()[-1]
			mon_neg+=ic1()

			self.ppdev([self.energy,self.offsetval]); w(.5);
			self.pil(self.counttime); 
			roi_pos+=self.roi()[-1]
			mon_pos+=ic1()


			self.ppdev([self.energy,+self.offsetval]); w(.5);
			self.pil(self.counttime); 
			roi_pos+=self.roi()[-1]
			mon_pos+=ic1()

			self.ppdev([self.energy,-self.offsetval]); w(.5);
			self.pil(self.counttime); 
			roi_neg+=self.roi()[-1]
			mon_neg+=ic1()

		try:	
			self.ic1ratio = mon_neg/mon_pos
		except:
			self.ic1ratio = 0

		
		self.sum=roi_neg/mon_neg+roi_pos/mon_pos
		self.diff=roi_neg/mon_neg-roi_pos/mon_pos
		self.fracdiff=self.diff/self.sum
		
