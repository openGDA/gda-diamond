#bragg is quite slow to move, fast to read back
# remove sleep in singleepics positioner
# remove commandstring?
# this needs serious testing...


class OpticPDClass(ScannableMotionBase):
	'''
	Optical device
	inXY, outXY return entrance and exit coordinates as two element list of reals [horiz, vert]
	'''

	def setEntranceXYfunction(self,infunc):
		self.infunc=infunc

	def setExitXYfunction(self,outfunc):
		self.outfunc=outfunc

	def inXY(self):
		return self.infunc()

	def outXY(self):
		return self.outfunc()

def directbeam():
	return [0.0,0.0]



class EnergyPDClass(ScannableMotionBase):
	'Energy PD - calls Bragg angle PD'
	def __init__(self, name, braggPD, dspace, braggoffsetPD, directionsign, BeamlineInfoModule):
		self.setName(name);
		self.setInputNames([name])
		self.Units=['keV']
		self.setOutputFormat(['%.4f'])
		self.setLevel(3)
		self.bragg=braggPD
		self.bragg_offset=braggoffsetPD
		self.dspace=dspace
		self.scalefac=directionsign
#		self.offset=bragg_offset()
		self.c=6.19921
		self.link=BeamlineInfoModule

	def getPosition(self):
		self.ang=self.bragg()*self.scalefac+self.bragg_offset()
		self.energy=self.c/self.dspace/sin(self.ang*pi/180)
		self.link.setEnergy(self.energy)
		return self.energy

	def calcAngle(en):
		return 180/pi*asin(self.c/self.dspace/en)-self.bragg_offset())/self.scalefac

	def asynchronousMoveTo(self,en):
		self.bragg.asynchronousMoveTo(self.calcAngle(en))

	def isBusy(self):
		return self.bragg.isBusy()
	
	def stop(self):
		self.bragg.stop()

	def calibrate(self, newenergy):
		"""Recalibrate the energy of the monochromator """
		cal_ang=180/pi*asin(self.c/self.dspace/newenergy)
		dcm_ang=self.bragg()
		self.bragg_offset(cal_ang-dcm_ang*self.scalefac)
		print 'Calculated offset='+str(bragg_offset())+' deg'


#ee=EnergyPDClass('energy',bragg,3.1356,bragg_offset,-1,BLi)

class EnergyChancutIDgap(OpticPDClass):
	'''Channel-cut mono'''
	def __init__(self, MonoEnergyPD, IDEnergyPD ):
		self.en=energypd
		self.setName(en.getName());
		self.setInputNames([en.getName()])
		self.Units=en.Units
		self.setOutputFormat(en.getOutputFormat)
		self.setLevel(3)
		self.setEntranceXYfunction(directbeam)
		self.setExitXYfunction(self.beamoffset)
		self.monogap=7
		self.en=MonoEnergyPD
		self.id=IDEnergyPD

	def getPosition(self):
		return self.en()

	def asynchronousMoveTo(self,new_position):
		self.en.asynchronousMoveTo(new_position)
		self.id.asynchronousMoveTo(new_position)

		#self.height=2*self.monogap*cos(-self.en.calcAngle(new_position)*pi/180)

		#option to move mirrors only with large move. Very small number means this is not used.
		if abs(new_position-self.previousenergy)>0.00001:
			#use scripted devices due to intermittent probelm with m1x,y
			M1y.asynchronousMoveTo(m1y_offset()+self.height)
			M2y.asynchronousMoveTo(m2y_offset()+self.height) 

		ztable.asynchronousMoveTo(ztable_offset()+self.height)
		base_z.asynchronousMoveTo(base_z_offset()+self.height)

	def isBusy(self):
		#return self.enpd.isBusy() or m1y.isBusy() or m2y.isBusy() or ztable.isBusy() or base_z.isBusy()
		return self.en.isBusy() or ztable.isBusy() or base_z.isBusy() or self.id.isBusy()

	def stop(self):
		self.en.stop()
		ztable.stop()
		base_z.stop()
		m1y.stop()
		m2y.stop()
		self.id.stop()
	
	def calibrate(self):
		self.ang=self.en.calcAngle(self())
		self.beamheight=2*self.monogap*cos(self.braggpd()*pi/180)
		print m1y,'\n',m2y,'\n',ztable,'\n',base_z
		print '=== Old offsets:\n',m1y_offset,'\n',m2y_offset,'\n',ztable_offset,'\n',base_z_offset
		m1y_offset(m1y()-self.beamheight)
		m2y_offset(m2y()-self.beamheight)
		ztable_offset(ztable()-self.beamheight)
		base_z_offset(base_z()[0]-self.beamheight)
		print '=== New offsets:\n',m1y_offset,'\n',m2y_offset,'\n',ztable_offset,'\n',base_z_offset

	def beamoffset():
		return [0.0, 2*self.monogap*cos(-self.en.calAngle()*pi/180)]


ee=EnergyPDClass('energy',bragg,3.1356,bragg_offset,-1,BLi)

eee=EnergyChancutIDgap(ee, uenergy)
# or EnergyChancutIDgap(EnergyPDClass('energy',bragg,3.1356,bragg_offset,-1,BLi), uenergy)




