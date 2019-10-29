

########### look at FlipperClass12ttl for fixing filenum problem (.intValue() method)


class FlipperClass(PseudoDevice):
	'''input: [energy,offset on ppth relative to centre,number of flipping cycles,number of samples per cycle]'''

	def __init__(self,name):
		self.setName(name)
		self.setLevel(10)
		self.setInputNames(['energy','offset','ncycles','ncounts'])
		self.setExtraNames(['total','diff','ratio'])
		self.setOutputFormat(['%.3f','%.4f','%.0f','%.1f','%.1f','%.1f','%.4f'])
		self.energy = 0
		self._offset = 0
		self.ncycles = 0
		self.ncounts = 0

	def getPosition(self):
		return [self.energy,self._offset,self.ncycles,self.ncounts,self.tot,self.diff,self.ratio]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
		self.energy = newpos[0]
		self._offset=newpos[1]
		self.ncycles=newpos[2]
		self.ncounts=newpos[3]
		cup = 0
		cdown = 0
		for i in range(int(self.ncycles)):
			pp220([self.energy,self._offset])
			for j in range(int(self.ncounts)):
				ct5(0.5)
				cup+=ct5()/adc4()
			pp220([self.energy,-self._offset])
			for j in range(int(self.ncounts)):
				ct5(0.5)
				cdown+=ct5()/adc4()
		self.tot = cup+cdown
		self.diff = cup-cdown
		self.ratio = self.diff/self.tot
		
class FlipperClass2(PseudoDevice):
	'''input: [energy,offset on ppth relative to centre,number of flipping cycles,number of samples per cycle]'''

	def __init__(self,name):
		self.setName(name)
		self.setLevel(10)
		self.setInputNames(['energy','offset','ncycles','ncounts'])
		self.setExtraNames(['total','diff','ratio','totalref','diffref','ratioref'])
		self.setOutputFormat(['%.3f','%.4f','%.0f','%.1f','%.1f','%.1f','%.4f','%.1f','%.1f','%.4f'])
		self.energy = 0
		self._offset = 0
		self.ncycles = 0
		self.ncounts = 0

	def getPosition(self):
		return [self.energy,self._offset,self.ncycles,self.ncounts,self.tot,self.diff,self.ratio,self.tot_ref,self.diff_ref,self.ratioref]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
		self.energy = newpos[0]
		self._offset=newpos[1]
		self.ncycles=newpos[2]
		self.ncounts=newpos[3]
		cup = 0
		cdown = 0
		ctrefup = 0
		ctrefdown = 0
		for i in range(int(self.ncycles)):
			pp220([self.energy,self._offset])
			for j in range(int(self.ncounts)):
				ct5(0.5)
				cup+=ct5()/adc4()
				ctrefup+=ct3()/adc4()
			pp220([self.energy,-self._offset])
			for j in range(int(self.ncounts)):
				ct5(0.5)
				cdown+=ct5()/adc4()
				ctrefdown+=ct3()/adc4()
		self.tot = cup+cdown
		self.diff = cup-cdown
		self.tot_ref = ctrefup+ctrefdown
		self.diff_ref= ctrefup-ctrefdown
		self.ratio = self.diff/self.tot
		self.ratioref = self.diff_ref/self.tot_ref

class FlipperClass3(PseudoDevice):
	'''input: [energy,offset on ppth relative to centre,number of flipping cycles,number of samples per cycle]'''

	def __init__(self,name):
		self.setName(name)
		self.setLevel(10)
		self.setInputNames(['energy','offset','ncycles','ncounts'])
		self.setExtraNames(['total','diff','ratio'])
		self.setOutputFormat(['%.3f','%.4f','%.0f','%.1f','%.1f','%.1f','%.4f'])
		self.energy = 0
		self._offset = 0
		self.ncycles = 0
		self.ncounts = 0

	def getPosition(self):
		return [self.energy,self._offset,self.ncycles,self.ncounts,self.tot,self.diff,self.ratio]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
		self.energy = newpos[0]
		self._offset=newpos[1]
		self.ncycles=newpos[2]
		self.ncounts=newpos[3]
		cup = 0
		cdown = 0
		for i in range(int(self.ncycles)):
			pp111([self.energy,self._offset])
			for j in range(int(self.ncounts)):
				ct3(0.5)
				cup+=ct3()
			pp111([self.energy,-self._offset])
			for j in range(int(self.ncounts)):
				ct3(0.5)
				cdown+=ct3()
		self.tot = cup+cdown
		self.diff = cup-cdown
		self.ratio = self.diff/self.tot
		
class FlipperClass4(PseudoDevice):
	'''
	dev=FlipperClass4(name,ppdevice)
	uses p100k and ic1 with specified pp device
	input: [energy,offset on ppth relative to centre,number of flipping cycles,number of samples per cycle
	in: 'energy','offset','ncycles','ncounts'
	extra: 'total','diff','ratio','totalref','diffref','ratioref'
	'''

	def __init__(self,name,ppdev):
		self.setName(name)
		self.ppdev=ppdev
		self.setLevel(10)
		self.setInputNames(['energy','offset','ncycles','ncounts'])
		self.setExtraNames(['total','diff','ratio','totalref','diffref','ratioref'])
		self.setOutputFormat(['%.3f','%.4f','%.0f','%.1f','%.1f','%.1f','%.4f','%.1f','%.1f','%.4f'])
		self.energy = 0
		self._offset = 0
		self.ncycles = 0
		self.ncounts = 0

	def getPosition(self):
		return [self.energy,self._offset,self.ncycles,self.ncounts,self.tot,self.diff,self.ratio,self.tot_ref,self.diff_ref,self.ratioref]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
		self.energy = newpos[0]
		self._offset=newpos[1]
		self.ncycles=newpos[2]
		self.ncounts=newpos[3]
		cup = 0
		cdown = 0
		ctrefup = 0
		ctrefdown = 0
		for i in range(int(self.ncycles)):
			self.ppdev([self.energy,self._offset]); w(.5);
			for j in range(int(self.ncounts)):
				pil(1); 
				ic1; 
				pilout=pil(); cts=pilout[2];
				mon=ic1()				
				cup+=cts
				ctrefup+=cts/mon
			self.ppdev([self.energy,-self._offset]); w(.5);
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

class FlipperClass5(PseudoDevice):
	'''
	uses p100k and ic1 with x17_anout analogue output for magnet
	in: 'volts','ncycles','ncounts'
	extra: 'total','diff','ratio','totalref','diffref','ratioref'
	'''

	def __init__(self,name):
		self.setName(name)
		self.setLevel(10)
		self.setInputNames(['volts','ncycles','ncounts'])
		self.setExtraNames(['total','diff','ratio','totalref','diffref','ratioref'])
		self.setOutputFormat(['%.3f','%.0f','%.1f','%.1f','%.1f','%.4f','%.1f','%.1f','%.4f'])
		self.volts = 0
		self.ncycles = 0
		self.ncounts = 0

	def getPosition(self):
		return [self.volts,self.ncycles,self.ncounts,self.tot,self.diff,self.ratio,self.tot_ref,self.diff_ref,self.ratioref]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
		self.volts = newpos[0]
		self.ncycles=newpos[1]
		self.ncounts=newpos[2]
		cup = 0
		cdown = 0
		ctrefup = 0
		ctrefdown = 0
		for i in range(int(self.ncycles)):
			#pp220([self.energy,self._offset])
			x17_anout(self.volts); w(.5)
			for j in range(int(self.ncounts)):
				pil(0.1); 
				ic1; 
				pilout=pil(); cts=pilout[2];
				mon=ic1()				
				cup+=cts
				ctrefup+=cts/mon
			#pp220([self.energy,-self._offset])
			x17_anout(-self.volts); w(.5)
			for j in range(int(self.ncounts)):
				pil(0.1); 
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



class FlipperClass6(PseudoDevice):
	'''
	dev=FlipperClass6(name,ppdevice)
	uses p100k and ic1 with specified pp device
	in: 'energy','offset','offsetshift','ncycles','ncounts'
	extra: 'total','diff','ratio','totalref','diffref','ratioref'
	'''

	def __init__(self,name,ppdev):
		self.setName(name)
		self.ppdev=ppdev
		self.setLevel(10)
		self.setInputNames(['energy','offset','offsetshift','ncycles','ncounts'])
		self.setExtraNames(['total','diff','ratio','totalref','diffref','ratioref'])
		self.setOutputFormat(['%.3f','%.4f','%.4f','%.0f','%.1f','%.1f','%.1f','%.4f','%.1f','%.1f','%.4f'])
		self.energy = 0
		self._offset = 0
		self._offsetshift=0
		self.ncycles = 0
		self.ncounts = 0

	def getPosition(self):
		return [self.energy,self._offset,self._offsetshift,self.ncycles,self.ncounts,self.tot,self.diff,self.ratio,self.tot_ref,self.diff_ref,self.ratioref]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
		self.energy = newpos[0]
		self._offset=newpos[1]
		self._offsetshift=newpos[2]
		self.ncycles=newpos[3]
		self.ncounts=newpos[4]
		cup = 0
		cdown = 0
		ctrefup = 0
		ctrefdown = 0
		for i in range(int(self.ncycles)):
			self.ppdev([self.energy,self._offset+self._offsetshift]); w(.5);
			for j in range(int(self.ncounts)):
				pil(0.1); 
				ic1; 
				pilout=pil(); cts=pilout[2];
				mon=ic1()				
				cup+=cts
				ctrefup+=cts/mon
			self.ppdev([self.energy,-self._offset+self._offsetshift]); w(.5);
			for j in range(int(self.ncounts)):
				pil(0.1); 
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

class FlipperClass7(PseudoDevice):
	'''
	dev=FlipperClass7(name,ppdevice,filename)
	uses p100k and ic1 with specified pp device
	in: 'energy','offset','counttime'
	extra: 'total','diff','ratio','totalref','diffref','ratioref'
	'''

	def __init__(self,name,ppdev,pilatus,rootfilename):
		self.setName(name)
		self.ppdev=ppdev
		self.pil=pilatus
		self.setLevel(10)
		self.setInputNames(['energy','offset','counttime'])
		self.setExtraNames(['filenum_neg','filenum_pos','ic1ratio'])
		self.setOutputFormat(['%.3f','%.4f','%.1f','%.0f','%.0f','%.4f'])
		self.energy = 0
		self._offset = 0
		self.counttime=0
		self.rootfilename=rootfilename
		self.filename=self.rootfilename

	def getPosition(self):
		return [self.energy,self._offset,self.counttime,self.filenum_neg, self.filenum_pos, self.ic1ratio]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
		self.energy = newpos[0]
		self._offset=newpos[1]
		self.counttime=newpos[2]
		
		self.filename=self.rootfilename+'n'
		self.pil.setFileName(self.filename)
		self.ppdev([self.energy,-self._offset]); w(.5);
		self.pil(self.counttime); 
		mon_neg=ic1()
		self.filenum_neg=self.pil.filenum

		self.filename=self.rootfilename+'p'
		self.pil.setFileName(self.filename)
		self.ppdev([self.energy,self._offset]); w(.5);
		self.pil(self.counttime); 
		mon_pos=ic1()
		self.filenum_pos=self.pil.filenum	

		try:	
			self.ic1ratio = mon_neg/mon_pos
		except:
			self.ic1ratio = 0
	def atScanStart(self):
		print "===Pilatus file names: "+self.rootfilename+"n & "+self.rootfilename+"p"

class FlipperClass8(PseudoDevice):
	'''
	uses apd and ic1 with x17_anout analogue output for magnet
	in: 'volts','ncycles','ncounts'
	extra: 'total','diff','ratio','totalref','diffref','ratioref'
	'''

	def __init__(self,name):
		self.setName(name)
		self.setLevel(10)
		self.setInputNames(['volts','ncycles','ncounts'])
		self.setExtraNames(['total','diff','ratio','totalref','diffref','ratioref'])
		self.setOutputFormat(['%.3f','%.0f','%.1f','%.1f','%.1f','%.4f','%.1f','%.1f','%.4f'])
		self.volts = 0
		self.ncycles = 0
		self.ncounts = 0

	def getPosition(self):
		return [self.volts,self.ncycles,self.ncounts,self.tot,self.diff,self.ratio,self.tot_ref,self.diff_ref,self.ratioref]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
		self.volts = newpos[0]
		self.ncycles=newpos[1]
		self.ncounts=newpos[2]
		cup = 0
		cdown = 0
		ctrefup = 0
		ctrefdown = 0
		for i in range(int(self.ncycles)):
			x17_anout(self.volts); w(.5)
			for j in range(int(self.ncounts)):
				t(1); 
				ic1; 
				tout=t();cts=tout[1];
				mon=ic1()				
				cup+=cts
				ctrefup+=cts/mon
			x17_anout(-self.volts); w(.5)
			for j in range(int(self.ncounts)):
				t(1); 
				ic1; 
				tout=t();cts=tout[1];
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

class FlipperClass9(PseudoDevice):
	'''
	uses apd and ic1 with x17_anout analogue output for magnet +--+ cycle and variable count time
	in: 'volts','ncycles','ncounts','ctime'
	extra: 'total','diff','ratio','totalref','diffref','ratioref'
	'''

	def __init__(self,name):
		self.setName(name)
		self.setLevel(10)
		self.setInputNames(['volts','ncycles','ncounts','ctime'])
		self.setExtraNames(['total','diff','ratio','totalref','diffref','ratioref'])
		self.setOutputFormat(['%.3f','%.0f','%.1f','%.1f','%.1f','%.1f','%.4f','%.1f','%.1f','%.4f'])
		self.volts = 0
		self.ncycles = 0
		self.ncounts = 0
		self.ctime=0

	def getPosition(self):
		return [self.volts,self.ncycles,self.ncounts,self.ctime,self.tot,self.diff,self.ratio,self.tot_ref,self.diff_ref,self.ratioref]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
		self.volts = newpos[0]
		self.ncycles=newpos[1]
		self.ncounts=newpos[2]
		self.ctime=newpos[3]
		cup = 0
		cdown = 0
		ctrefup = 0
		ctrefdown = 0
		for i in range(int(self.ncycles)):
			x17_anout(self.volts); w(.5)
			for j in range(int(self.ncounts)):
				t(self.ctime); 
				ic1; 
				tout=t();cts=tout[1];
				mon=ic1()				
				cup+=cts
				ctrefup+=cts/mon
			x17_anout(-self.volts); w(.5)
			for j in range(int(self.ncounts)):
				t(self.ctime); 
				ic1; 
				tout=t();cts=tout[1];
				mon=ic1()				
				cdown+=cts
				ctrefdown+=cts/mon
			x17_anout(-self.volts); w(.5)
			for j in range(int(self.ncounts)):
				t(self.ctime); 
				ic1; 
				tout=t();cts=tout[1];
				mon=ic1()
				cdown+=cts
				ctrefdown+=cts/mon			
			x17_anout(+self.volts); w(.5)
			for j in range(int(self.ncounts)):
				t(self.ctime); 
				ic1; 
				tout=t();cts=tout[1];
				mon=ic1()				
				cup+=cts
				ctrefup+=cts/mon



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

class FlipperClass10(PseudoDevice):
	'''
	dev=FlipperClass10(name, ppdevice, pilatus)
	uses pilatus and ic1 with specified pp device
	in: 'energy','offset','counttime','cycles'
	firstnum=first pil file number
	sequence=(+--+)*ncycles
	extra: 'firstnum','ic1ratio'
	'''
	def __init__(self,name,ppdev,pilatus):
		self.setName(name)
		self.ppdev=ppdev
		self.pil=pilatus
		self.setLevel(10)
		self.setInputNames(['energy','offset','counttime','ncycles'])
		self.setExtraNames(['filenum','ic1ratio'])
		self.setOutputFormat(['%.3f','%.4f','%.1f','%.0f','%.0f','%.4f'])
		self.energy = 0
		self._offset = 0
		self.counttime=0
		#self.rootfilename=rootfilename
		#self.filename=self.rootfilename

	def getPosition(self):
		return [self.energy,self._offset,self.counttime,self.cycles,self.filenum, self.ic1ratio]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
		self.filenum=self.pil()[1]+1

		self.energy = newpos[0]
		self._offset=newpos[1]
		self.counttime=newpos[2]
		self.cycles=newpos[3]

		mon_neg=mon_pos=0

		for n in range(int(self.cycles)):
			self.ppdev([self.energy,-self._offset]); w(.5);
			self.pil(self.counttime); 
			mon_neg+=ic1()

			self.ppdev([self.energy,self._offset]); w(.5);
			self.pil(self.counttime); 
			mon_pos+=ic1()

			self.ppdev([self.energy,+self._offset]); w(.5);
			self.pil(self.counttime); 
			mon_pos+=ic1()

			self.ppdev([self.energy,-self._offset]); w(.5);
			self.pil(self.counttime); 
			mon_neg+=ic1()

		try:	
			self.ic1ratio = mon_neg/mon_pos
		except:
			self.ic1ratio = 0

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
		self._offset = 0
		self.counttime=0
		#self.rootfilename=rootfilename
		#self.filename=self.rootfilename
		self.roi=pilatus_roi

	def getPosition(self):
		return [self.energy,self._offset,self.counttime,self.cycles,self.filenum, self.ic1ratio, self.fracdiff, self.sum, self.diff]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
		self.filenum=self.pil()[1]+1
		#self.filenum=int(str(self.pil()[1]))+1	#temp fix - delete
		self.energy = newpos[0]
		self._offset=newpos[1]
		self.counttime=newpos[2]
		self.cycles=newpos[3]

		mon_neg=mon_pos=roi_neg=roi_pos=0

		for n in range(int(self.cycles)):
			waitforinjection()

			self.ppdev([self.energy,-self._offset]); w(.5);
			self.pil(self.counttime); 
			roi_neg+=self.roi()[-1]
			mon_neg+=ic1()

			self.ppdev([self.energy,self._offset]); w(.5);
			self.pil(self.counttime); 
			roi_pos+=self.roi()[-1]
			mon_pos+=ic1()


			self.ppdev([self.energy,+self._offset]); w(.5);
			self.pil(self.counttime); 
			roi_pos+=self.roi()[-1]
			mon_pos+=ic1()

			self.ppdev([self.energy,-self._offset]); w(.5);
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

class FlipperClass11tmp(PseudoDevice):
	'''
	dev=FlipperClass11(name, ppdevice, pilatus, pilatus_roi)
	uses pilatus and ic1 with specified pp device
	in: 'energy','offset','counttime','cycles'
	firstnum=first pil file number
	sequence=(+--+)*ncycles
	extra: 'firstnum','ic1ratio'
	filenum is not meaningfull unless using the pilatus
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
		self._offset = 0
		self.counttime=0
		#self.rootfilename=rootfilename
		#self.filename=self.rootfilename
		self.roi=pilatus_roi

	def getPosition(self):
		return [self.energy,self._offset,self.counttime,self.cycles,self.filenum, self.ic1ratio, self.fracdiff, self.sum, self.diff]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
		self.filenum=self.pil()[1]+1
		#self.filenum=int(str(self.pil()[1]))+1	#temp fix - delete
		self.energy = newpos[0]
		self._offset=newpos[1]
		self.counttime=newpos[2]
		self.cycles=newpos[3]

		mon_neg=mon_pos=roi_neg=roi_pos=0

		for n in range(int(self.cycles)):
			waitforinjection()

			self.ppdev([self.energy,-self._offset]); w(.5);
			self.pil(self.counttime); 
			roi_neg+=self.roi()[-1]
			mon_neg+=ic1()

			self.ppdev([self.energy,self._offset]); w(.5);
			self.pil(self.counttime); 
			roi_pos+=self.roi()[-1]
			mon_pos+=ic1()


			self.ppdev([self.energy,+self._offset]); w(.5);
			self.pil(self.counttime); 
			roi_pos+=self.roi()[-1]
			mon_pos+=ic1()

			self.ppdev([self.energy,-self._offset]); w(.5);
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

class FlipperClass11Temp(PseudoDevice):
	'''
	temp version to fix waitforinjection bug - delete this class ######################################################
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
		self._offset = 0
		self.counttime=0
		#self.rootfilename=rootfilename
		#self.filename=self.rootfilename
		self.roi=pilatus_roi

	def getPosition(self):
		return [self.energy,self._offset,self.counttime,self.cycles,self.filenum, self.ic1ratio, self.fracdiff, self.sum, self.diff]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
		self.filenum=self.pil()[1]+1

		self.energy = newpos[0]
		self._offset=newpos[1]
		self.counttime=newpos[2]
		self.cycles=newpos[3]

		mon_neg=mon_pos=roi_neg=roi_pos=0

		while timetoinjection()<waitforinjection.due:
			print '=== waiting for injection'
			pos w 3

		for n in range(int(self.cycles)):
			self.ppdev([self.energy,-self._offset]); w(.5);
			self.pil(self.counttime); 
			roi_neg+=self.roi()[-1]
			mon_neg+=ic1()

			self.ppdev([self.energy,self._offset]); w(.5);
			self.pil(self.counttime); 
			roi_pos+=self.roi()[-1]
			mon_pos+=ic1()


			self.ppdev([self.energy,+self._offset]); w(.5);
			self.pil(self.counttime); 
			roi_pos+=self.roi()[-1]
			mon_pos+=ic1()

			self.ppdev([self.energy,-self._offset]); w(.5);
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

class FlipperClass12(PseudoDevice):
	'''
	dev=FlipperClass12(name, magnetdevice, pilatus, pilatus_roi,pilatus_roi field index (default = last)
	uses pilatus and ic1 with specified magnet device
	in: 'magvolts','counttime','ncycles'
	magvolts is, for example, the x17_anout voltage magntitude
	firstnum=first pil file number
	sequence=(+--+)*ncycles
	extra: 'firstnum','ic1ratio'
	waits for self.waittime after flipping
	'''
	def __init__(self,name,magnetdevice,pilatus,pilatus_roi, index=-1):
		self.setName(name)
		self.magdev=magnetdevice
		self.pil=pilatus
		self.setLevel(10)
		self.setInputNames(['magvolts','counttime','ncycles'])
		self.setExtraNames(['filenum','ic1ratio','fracdiff','norm_sum','norm_diff'])
		self.setOutputFormat(['%.4f','%.1f','%.0f','%.0f','%.4f','%.5f','%.1f','%.1f'])
		self.magvolts = 0
		self.counttime=0
		#self.rootfilename=rootfilename
		#self.filename=self.rootfilename
		self.roi=pilatus_roi
		self.waittime=0
		self.index=index

	def getPosition(self):
		return [self.magvolts,self.counttime,self.cycles,self.filenum, self.ic1ratio, self.fracdiff, self.sum, self.diff]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
		try:
			self.filenum=self.pil()[1]+1
		except:
			self.filenum=0

		self.magvolts=newpos[0]
		self.counttime=newpos[1]
		self.cycles=newpos[2]

		mon_neg=mon_pos=roi_neg=roi_pos=0
		

		for n in range(int(self.cycles)):
#			print n
#			waitforinjection#not tested

			self.magdev(-self.magvolts); w(self.waittime);
			self.pil(self.counttime); 
			
			try:
				roi_neg+=self.roi()[self.index]
			except:
				roi_neg+=self.roi()
			mon_neg+=ic1()

			self.magdev(self.magvolts); w(self.waittime);
			self.pil(self.counttime);
			try:
				roi_pos+=self.roi()[self.index]
			except:
				roi_pos+=self.roi() 
			mon_pos+=ic1()


			self.magdev(self.magvolts); w(self.waittime);
			self.pil(self.counttime); 
			try:
				roi_pos+=self.roi()[self.index]
			except:
				roi_pos+=self.roi() 
			mon_pos+=ic1()

			self.magdev(-self.magvolts); w(self.waittime);
			self.pil(self.counttime); 
			try:
				roi_neg+=self.roi()[self.index]
			except:
				roi_neg+=self.roi()
			mon_neg+=ic1()

		try:	
			self.ic1ratio = mon_neg/mon_pos
		except:
			self.ic1ratio = 0

		
		try:
			self.sum=roi_neg/mon_neg+roi_pos/mon_pos
			self.diff=roi_neg/mon_neg-roi_pos/mon_pos
			self.fracdiff=self.diff/self.sum
		except:
			print "===Error calculating ratios (zero counts?). Returning zeros"
			self.sum=0
			self.diff=0
			self.fracdiff=0

class FlipperPPPQBPMClass(PseudoDevice):
	'''
	This PD is for carrying out a precise calibration of the phase plate offset centre
	dev=FlipperPPPQBPMClass(name, ppdevice, qbpmdevice,monitor (I0) device)
	in: 'energy','offset','centre (for offset)'
	example: pos xia1 1; scan ppa111centre [en() 0.022 -.002] [en() 0.022 .002] [0 0 0.0001]; pos xia1 0;
	'''
	def __init__(self,name,ppdev,qbpmdev,mondev):
		self.setName(name)
		self.ppdev=ppdev
		self.qbpm=qbpmdev
		self.mon=mondev
		self.setLevel(10)
		self.setInputNames(['energy','offset','centre'])
		self.setExtraNames(['fracdiff1','fracdiff2','fracdiff3','fracdiff4'])
		self.setOutputFormat(['%.3f','%.4f','%.4f','%.4f','%.4f','%.4f','%.4f'])
		self.energy = 0
		self._offset = 0
		self.centre=0
		self.cycles=1	#pass as extra input if variable cycles requires
		self.waitime=2

	def getPosition(self):
		return [self.energy,self._offset,self.centre,self.fracdiff1,self.fracdiff2,self.fracdiff3,self.fracdiff4]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):

		self.energy = newpos[0]
		self._offset=newpos[1]
		self.centre=newpos[2]

		c1_neg=c1_pos=c2_neg=c2_pos=c3_neg=c3_pos=c4_neg=c4_pos=0;
		
		for n in range(int(self.cycles)):
			self.ppdev([self.energy,self.centre-self._offset]); w(self.waitime); qbpmout=self.qbpm(); 
			mon=self.mon(); c1_neg+=qbpmout[1]/mon; c2_neg+=qbpmout[2]/mon; c3_neg+=qbpmout[3]/mon; c4_neg+=qbpmout[4]/mon;

			self.ppdev([self.energy,self.centre+self._offset]); w(self.waitime); qbpmout=self.qbpm(); 
			mon=self.mon(); c1_pos+=qbpmout[1]/mon; c2_pos+=qbpmout[2]/mon; c3_pos+=qbpmout[3]/mon; c4_pos+=qbpmout[4]/mon;

			self.ppdev([self.energy,self.centre+self._offset]); w(self.waitime); qbpmout=self.qbpm(); 
			mon=self.mon(); c1_pos+=qbpmout[1]/mon; c2_pos+=qbpmout[2]/mon; c3_pos+=qbpmout[3]/mon; c4_pos+=qbpmout[4]/mon;

			self.ppdev([self.energy,self.centre-self._offset]); w(self.waitime); qbpmout=self.qbpm(); 
			mon=self.mon(); c1_neg+=qbpmout[1]/mon; c2_neg+=qbpmout[2]/mon; c3_neg+=qbpmout[3]/mon; c4_neg+=qbpmout[4]/mon;

		self.fracdiff1=(c1_pos-c1_neg)/(c1_pos+c1_neg)
		self.fracdiff2=(c2_pos-c2_neg)/(c2_pos+c2_neg)
		self.fracdiff3=(c3_pos-c3_neg)/(c3_pos+c3_neg)
		self.fracdiff4=(c4_pos-c4_neg)/(c4_pos+c4_neg)


class FlipperClass9diode(PseudoDevice):
	'''
	uses apd and ic1 with x19_anout analogue output for magnet +--+ cycle and variable count time
	in: 'volts','ncycles','ncounts','ctime'
	extra: 'total','diff','ratio','totalref','diffref','ratioref'
	'''

	def __init__(self,name):
		self.setName(name)
		self.setLevel(10)
		self.setInputNames(['volts','ncycles','ncounts','ctime'])
		self.setExtraNames(['total','diff','ratio','totalref','diffref','ratioref'])
		self.setOutputFormat(['%.3f','%.0f','%.1f','%.1f','%.1f','%.1f','%.4f','%.1f','%.1f','%.4f'])
		self.volts = 0
		self.ncycles = 0
		self.ncounts = 0
		self.ctime=0

	def getPosition(self):
		return [self.volts,self.ncycles,self.ncounts,self.ctime,self.tot,self.diff,self.ratio,self.tot_ref,self.diff_ref,self.ratioref]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
		self.volts = newpos[0]
		self.ncycles=newpos[1]
		self.ncounts=newpos[2]
		self.ctime=newpos[3]
		cup = 0
		cdown = 0
		ctrefup = 0
		ctrefdown = 0
		for i in range(int(self.ncycles)):
			x19_anout(self.volts); w(.5)
			print "flipping"
			for j in range(int(self.ncounts)):
				t(self.ctime); 
				ic1; 
				tout=diode();cts=tout;
				mon=ic1()				
				cup+=cts
				ctrefup+=cts/mon
			x19_anout(-self.volts); w(.5)
			print "flipping"
			for j in range(int(self.ncounts)):
				t(self.ctime); 
				ic1; 
				tout=diode();cts=tout;
				mon=ic1()				
				cdown+=cts
				ctrefdown+=cts/mon
			x19_anout(-self.volts); w(.5)
			print "flipping"
			for j in range(int(self.ncounts)):
				t(self.ctime); 
				ic1; 
				tout=diode();cts=tout;
				mon=ic1()
				cdown+=cts
				ctrefdown+=cts/mon			
			x19_anout(+self.volts); w(.5)
			print "flipping"
			for j in range(int(self.ncounts)):
				t(self.ctime); 
				ic1; 
				tout=diode();cts=tout;
				mon=ic1()				
				cup+=cts
				ctrefup+=cts/mon



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


class FlipperClass13(PseudoDevice):
	'''
	dev=FlipperClass13(name, ppdevice, signal_count_PD, signal_read_PD, mon_count_PD, mon_read_PD, signal_read_field=None,  mon_read_field=None)
	allows separate PV's for count and readback (e.g. readback might be a ROI)
	If readback PD's are vectors then the field position must be specified, e.g. -1 for last, 0 for first
	use integrating PD's for signal and monitor
	in: ['energy','offset','counttime','ncycles']
	firstnum=first pil file number
	sequence=(+--+)*ncycles
	extra: ['monratio','fracdiff','norm_sum','norm_diff']
	'''
	def __init__(self, name, ppdevice, signal_count_PD, signal_read_PD, mon_count_PD, mon_read_PD, signal_read_field=None,  mon_read_field=None):
		self.setName(name)
		self.ppdev=ppdevice
		self.signal_count_PD=signal_count_PD
		self.signal_read_PD=signal_read_PD
		self.mon_count_PD=mon_count_PD
		self.mon_read_PD=mon_read_PD
		self.signal_read_field=signal_read_field
		self.mon_read_field=mon_read_field
		self.setLevel(10)
		self.setInputNames(['energy','offset','counttime','ncycles'])
		self.setExtraNames(['monratio','fracdiff','norm_sum','norm_diff'])
		self.setOutputFormat(['%.4f','%.1f','%.0f','%.0f','%.4f','%.5f','%.1f','%.1f'])
		self.wait_time=0.5
		#self.rootfilename=rootfilename
		#self.filename=self.rootfilename
		self.energy=self._offset=self.counttime=self.cycles=self.ic1ratio=self.fracdiff=self.sum=self.diff=0

	def getPosition(self):
		return [self.energy,self._offset,self.counttime,self.cycles, self.ic1ratio, self.fracdiff, self.sum, self.diff]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
			print 'moooving...'
#		try:
			#self.filenum=self.pil()[1]+1
	
			self.energy = newpos[0]
			self._offset=newpos[1]
			self.counttime=newpos[2]
			self.cycles=newpos[3]
	
			mon_neg=mon_pos=roi_neg=roi_pos=0
	
			for n in range(int(self.cycles)):
				waitforinjection()

				self.ppdev([self.energy,-self._offset]); w(self.wait_time);
				if self.signal_count_PD==self.mon_count_PD:
					self.signal_count_PD(self.counttime)
				else:
					pos((self.signal_count_PD,self.counttime,self.mon_count_PD,self.counttime))
				if self.signal_read_field==None:
					roi_neg+=self.signal_read_PD()
				else:
					roi_neg+=self.signal_read_PD()[self.signal_read_field]
				if self.mon_read_field==None:
					mon_neg+=self.mon_read_PD()
				else:
					mon_neg+=self.mon_read_PD()[self.mon_read_field]
				print ' roi_neg, mon_neg', roi_neg, mon_neg


				self.ppdev([self.energy,self._offset]); w(self.wait_time);
				if self.signal_count_PD==self.mon_count_PD:
					self.signal_count_PD(self.counttime)
				else:
					pos((self.signal_count_PD,self.counttime,self.mon_count_PD,self.counttime))
				if self.signal_read_field==None:
					roi_pos+=self.signal_read_PD()
				else:
					roi_pos+=self.signal_read_PD()[self.signal_read_field]
				if self.mon_read_field==None:
					mon_pos+=self.mon_read_PD()
				else:
					mon_pos+=self.mon_read_PD()[self.mon_read_field]
				print ' roi_neg, mon_neg', roi_neg, mon_neg

				self.ppdev([self.energy,self._offset]); w(self.wait_time);
				if self.signal_count_PD==self.mon_count_PD:
					self.signal_count_PD(self.counttime)
				else:
					pos((self.signal_count_PD,self.counttime,self.mon_count_PD,self.counttime))
				if self.signal_read_field==None:
					roi_pos+=self.signal_read_PD()
				else:
					roi_pos+=self.signal_read_PD()[self.signal_read_field]
				if self.mon_read_field==None:
					mon_pos+=self.mon_read_PD()
				else:
					mon_pos+=self.mon_read_PD()[self.mon_read_field]
				print ' roi_neg, mon_neg', roi_neg, mon_neg

				self.ppdev([self.energy,-self._offset]); w(self.wait_time);
				if self.signal_count_PD==self.mon_count_PD:
					self.signal_count_PD(self.counttime)
				else:
					pos((self.signal_count_PD,self.counttime,self.mon_count_PD,self.counttime))
				if self.signal_read_field==None:
					roi_neg+=self.signal_read_PD()
				else:
					roi_neg+=self.signal_read_PD()[self.signal_read_field]
				if self.mon_read_field==None:
					mon_neg+=self.mon_read_PD()
				else:
					mon_neg+=self.mon_read_PD()[self.mon_read_field]
				print ' roi_neg, mon_neg', roi_neg, mon_neg

			self.ic1ratio = mon_neg/mon_pos
			self.sum=roi_neg/mon_neg+roi_pos/mon_pos
			self.diff=roi_neg/mon_neg-roi_pos/mon_pos
			self.fracdiff=self.diff/self.sum
#		except:
#			pass
#			print "=== Something went wrong (divide by zero?): returning zeros"
#			self.energy=self._offset=self.counttime=self.cycles=self.ic1ratio=self.fracdiff=self.sum=self.diff=0


class FlipperPD(PseudoDevice):
	'''
	Flipper device using analogue output. Energy is not used but is included for consistency with other flipper devices such as phase plate
	'''
	def __init__(self, name, anout_PD):
		self.setName(name)
		self.anout_PD=anout_PD
		self.setLevel(9)
		self.setInputNames(['energy','volts'])
		self.setOutputFormat(['%.4f','%.2f'])
		self.energy=0
		self=volts=0

	def getPosition(self):
		return [self.energy,self.anout_PD()]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
		self.energy=newpos[0]
		self.anout_PD(newpos[1])

class FlipperClass12ttl(PseudoDevice):
	'''
	dev=FlipperClass12ttl(name, magnetdevice, pilatus, pilatus_roi,pilatus_roi field index (default = last)
	uses pilatus and ic1 with specified magnet device
	this version flips between magvolts and zero (not -magvolts) for ttl on/off field flipper
	in: 'magvolts','counttime','ncycles'
	magvolts is, for example, the x17_anout voltage magntitude
	firstnum=first pil file number
	sequence=(+--+)*ncycles
	extra: 'firstnum','ic1ratio'
	waits for self.waittime after flipping
	'''
	def __init__(self,name,magnetdevice,pilatus,pilatus_roi, index=-1):
		self.setName(name)
		self.magdev=magnetdevice
		self.pil=pilatus
		self.setLevel(10)
		self.setInputNames(['magvolts','counttime','ncycles'])
		self.setExtraNames(['filenum','ic1ratio','fracdiff','norm_sum','norm_diff'])
		self.setOutputFormat(['%.4f','%.1f','%.0f','%.0f','%.4f','%.5f','%.1f','%.1f'])
		self.magvolts = 0
		self.counttime=0
		#self.rootfilename=rootfilename
		#self.filename=self.rootfilename
		self.roi=pilatus_roi
		self.waittime=0
		self.index=index

	def getPosition(self):
		return [self.magvolts,self.counttime,self.cycles,self.filenum, self.ic1ratio, self.fracdiff, self.sum, self.diff]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
		try:
			fNum=self.filenum=self.pil()[1]
			self.filenum=fNum.intValue()+1
		except:
			self.filenum=0

		self.magvolts=newpos[0]
		self.counttime=newpos[1]
		self.cycles=newpos[2]

		mon_neg=mon_pos=roi_neg=roi_pos=0
		

		for n in range(int(self.cycles)):
#			print n
#			waitforinjection#not tested

			self.magdev(-self.magvolts*0); w(self.waittime);
			self.pil(self.counttime); 
			
			try:
				roi_neg+=self.roi()[self.index]
			except:
				roi_neg+=self.roi()
			mon_neg+=ic1()

			self.magdev(self.magvolts); w(self.waittime);
			self.pil(self.counttime);
			try:
				roi_pos+=self.roi()[self.index]
			except:
				roi_pos+=self.roi() 
			mon_pos+=ic1()


			self.magdev(self.magvolts); w(self.waittime);
			self.pil(self.counttime); 
			try:
				roi_pos+=self.roi()[self.index]
			except:
				roi_pos+=self.roi() 
			mon_pos+=ic1()

			self.magdev(-self.magvolts*0); w(self.waittime);
			self.pil(self.counttime); 
			try:
				roi_neg+=self.roi()[self.index]
			except:
				roi_neg+=self.roi()
			mon_neg+=ic1()

		try:	
			self.ic1ratio = mon_neg/mon_pos
		except:
			self.ic1ratio = 0

		
		try:
			self.sum=roi_neg/mon_neg+roi_pos/mon_pos
			self.diff=roi_neg/mon_neg-roi_pos/mon_pos
			self.fracdiff=self.diff/self.sum
		except:
			print "===Error calculating ratios (zero counts?). Returning zeros"
			self.sum=0
			self.diff=0
			self.fracdiff=0


class FlipperClass12APDspecial(PseudoDevice):
	'''
	====== not yet tested =======
	dev=FlipperClass12APDspecial(name, magnetdevice)
	uses t for signal and monitor (assume signal is t()[2] and monitor is t()[1])
	this version flips between magvolts and zero (not -magvolts) for ttl on/off field flipper
	in: 'magvolts','counttime','ncycles'
	sequence=(+--+)*ncycles
	extra: 'firstnum','ic1ratio'
	waits for self.waittime after flipping
	'''
	def __init__(self,name,magnetdevice,pilatus,pilatus_roi, index=-1):
		self.setName(name)
		self.magdev=magnetdevice
		#self.pil=pilatus
		self.setLevel(10)
		self.setInputNames(['magvolts','counttime','ncycles'])
		self.setExtraNames(['filenum','ic1ratio','fracdiff','norm_sum','norm_diff'])
		self.setOutputFormat(['%.4f','%.1f','%.0f','%.0f','%.4f','%.5f','%.1f','%.1f'])
		self.magvolts = 0
		self.counttime=0
		#self.roi=pilatus_roi
		self.waittime=0
		#self.index=index
		self.test=False

	def getPosition(self):
		return [self.magvolts,self.counttime,self.cycles,self.filenum, self.ic1ratio, self.fracdiff, self.sum, self.diff]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newpos):
		self.filenum=0
		self.magvolts=newpos[0]
		self.counttime=newpos[1]
		self.cycles=newpos[2]

		mon_neg=mon_pos=roi_neg=roi_pos=0
		
		for n in range(int(self.cycles)):

			if self.test:
				print 'neg'
			self.magdev(-self.magvolts*0); w(self.waittime);
			t(self.counttime); tcounts=t()
			roi_neg+=tcounts[2]
			mon_neg+=tcounts[1]

			if self.test:
				print 'pos'
			self.magdev(self.magvolts); w(self.waittime);
			t(self.counttime); tcounts=t()
			roi_pos+=tcounts[2]
			mon_pos+=tcounts[1]

			if self.test:
				print 'pos'
			self.magdev(self.magvolts); w(self.waittime);
			t(self.counttime); tcounts=t()
			roi_pos+=tcounts[2]
			mon_pos+=tcounts[1]

			if self.test:
				print 'neg'
			self.magdev(-self.magvolts*0); w(self.waittime);
			t(self.counttime); tcounts=t()
			roi_neg+=tcounts[2]
			mon_neg+=tcounts[1]

		try:	
			self.ic1ratio = mon_neg/mon_pos
		except:
			self.ic1ratio = 0
		
		try:
			self.sum=roi_neg/mon_neg+roi_pos/mon_pos
			self.diff=roi_neg/mon_neg-roi_pos/mon_pos
			self.fracdiff=self.diff/self.sum
		except:
			print "===Error calculating ratios (zero counts?). Returning zeros"
			self.sum=0
			self.diff=0
			self.fracdiff=0




'''


#magvolts=FlipperPD('magvols',x17_anout)	#flipper device for magnet current via analogie output voltage
#fl=flipper13_pil_t_mag=FlipperClass13('flipper13_pil_t_mag', magvolts, pil, pil, t, t, signal_read_field=-1,  mon_read_field=-1); #mag field and t for signal and mon (fields 2, 1) (make sure mon is last field of t)
#fl1=flipper13_pil_t_mag=FlipperClass13('flipper13_pil_t_ppa220', ppa220, pil, pil, t, t, signal_read_field=-1,  mon_read_field=-1); #ppa220 and t for signal and mon (fields 2, 1) (make sure mon is last field of t)


########commented out - put back as needed ##################
flipper13_pil_t_mag=FlipperClass13('flipper13_pil_t_mag', magvolts, t, t, t, t, signal_read_field=2,  mon_read_field=1); #mag field and t for signal and mon (fields 2, 1)
flipper13_t_t_mag=FlipperClass13('flipper13_t_t_mag', magvolts, t, t, t, t, signal_read_field=2,  mon_read_field=1); #mag field and t for signal and mon (fields 2, 1)
flipper13_apd_t_mag=FlipperClass13('flipper13_apd_t_mag', magvolts, t, t, t, t, signal_read_field=-1,  mon_read_field=1); #mag field and APD for signal and t for mon (fields -1, 1)
flipper13_pil_lcroi_t_mag=FlipperClass13('flipper13_pil_t_mag', magvolts, pil, lcroi, t, t, signal_read_field=-1,  mon_read_field=1); #mag field and  Pil for signal and t for mon (fields -1, 1)
flipper13_pil_t_mag=FlipperClass13('flipper13_pil_t_mag', magvolts, pil, lcroi, t, t, signal_read_field=-1,  mon_read_field=1); #mag field and  Pil for signal and t for mon (fields -1, 1)
flipper13_pil_t=FlipperClass13('flipper13_pil_t', ppa111, pil, lcroi, t, t, signal_read_field=-1,  mon_read_field=1); #Pilatus with lcroi, monitor t (field 1)
flipper13_t_t=FlipperClass13('flipper13_t_t', ppa111, t, t, t, t, signal_read_field=-1,  mon_read_field=1); #t for signal and mon (fields 1, -1)


#flipper8=FlipperClass8('flipper8')
flipper9=FlipperClass9('flipper9')
#flipper7=FlipperClass7('flipper7',ppa111,pil2m,'flipper')
#flipper10a=FlipperClass10('flipper10',ppa111,pil)
#flipper10b=FlipperClass10('flipper10',ppb111,pil)
#flipper4=FlipperClass4('flipper4',ppa111)
#flipper6=FlipperClass6('flipper6',ppa111)#with offset shift
#flipper5=FlipperClass5('flipper5')
#flipper3 = FlipperClass3('flipper3')
#flipper2 = FlipperClass2('flipper2')
#flipper = FlipperClass('flipper')

ppa111centre=FlipperPPPQBPMClass('pppcentre',ppa111,qbpm6,ic1)
ppb111centre=FlipperPPPQBPMClass('pppcentre',ppb111,qbpm6,ic1)
ppa220centre=FlipperPPPQBPMClass('pppcentre',ppa220,qbpm6,ic1)
#ppb111centre=FlipperPPPQBPMClass('pppcentre',ppb111,qbpm8,ic1)

flipper11a=FlipperClass11('flipper11a',ppa111,pil,roi2) 
flipper11b=FlipperClass11('flipper11b',ppb111,pil,pil) 

#flipperapd=FlipperClass11('flipperapd',ppa111,t,t)

#flipper12=FlipperClass12('flipper12',x17_anout,pil,roi2)
#flipper12t=FlipperClass12('flipper12t',x17_anout,t,t)
flipper12t=FlipperClass12('flipper12t',x19_anout,t,t)
flipper12xm=FlipperClass12('flipper12xm',x19_anout,xm,xm)

#flipper10b=FlipperClass10('flipper10',ppb111,pil)
#flipper11b=FlipperClass11Temp('flipper11',ppb111,pil,pil)
#flipper9diode=FlipperClass9diode('flipper9diode')
# ==== USE QPBM6, not QBPM8 =============

#flipper4=FlipperClass4a('flipper4',ppa220)

#ppa220centre=FlipperPPPQBPMClass('ppa220centre', ppa220, qbpm6, ic1)
#flipper220=FlipperClass11('flipper220',ppa220,t,t)
#example: pos xia1 1; scan ppa220centre [en() 0.022 -.002] [en() 0.022 .002] [0 0 0.0001]; pos xia1 0;

'''



