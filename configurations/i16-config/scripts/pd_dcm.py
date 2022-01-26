from gda.epics import CAClient 
from java import lang
from gda.device.scannable import ScannableMotionBase

from time import sleep


class EnergyFromBraggPD(ScannableMotionBase):
	'Energy PD - calls Bragg angle PD'
	def __init__(self, name,link):
		self.setName(name);
		self.setInputNames([name])
		#self.setExtraNames([name])
		self.Units=['keV']
		self.setOutputFormat(['%.4f'])
		self.setLevel(3)
		self.braggpd=bragg
#		self.dspace=3.1356
		self.dspace=3.13475
#		self.dspace=3.1356/3
		self.scalefac=-1
#		self.offset=bragg_offset()
		self.c=6.19921
		self.setLink(link)


	def setLink(self,link):
		"""Establish the link with the diffractometer objects """
		self.link=link

	def getPosition(self):
		ang=self.braggpd()*self.scalefac+bragg_offset()
		self.link.setEnergy(self.c/self.dspace/sin(ang*pi/180))
		return self.c/self.dspace/sin(ang*pi/180)


	def asynchronousMoveTo(self,energy):
		ang=(180/pi*asin(self.c/self.dspace/energy)-bragg_offset())/self.scalefac
		self.braggpd.asynchronousMoveTo(ang)

	def isBusy(self):
		i_am_busy = self.braggpd.isBusy()

		#RJW 21/04/08: added this line so that the link.setEnergy is always called and updated
		# once move has completed
		if not i_am_busy:
			self.getPosition()

		return i_am_busy
	
	def stop(self):
		self.braggpd.stop()

	def calibrate(self, newenergy):
		"""Recalibrate the energy of the monochromator """
		cal_ang=180/pi*asin(self.c/self.dspace/newenergy)
		dcm_ang=self.braggpd()
		bragg_offset(cal_ang-dcm_ang*self.scalefac)
		print 'Calculated offset='+str(bragg_offset())+' deg'


class EnergyFromBraggwithHarmonicPD(ScannableMotionBase):
	'Energy PD - calls Bragg angle PD'
	def __init__(self, name,link,harmonicPD):
		self.setName(name);
		self.setInputNames([name])
		#self.setExtraNames([name])
		self.Units=['keV']
		self.setOutputFormat(['%.4f'])
		self.setLevel(3)
		self.harmonic = harmonicPD
		self.braggpd=bragg
		self.dspace=3.1356
#		self.dspace=3.1356/3
		self.scalefac=-1
#		self.offset=bragg_offset()
		self.c=6.19921
		self.setLink(link)


	def setLink(self,link):
		"""Establish the link with the diffractometer objects """
		self.link=link

	def getPosition(self):
		ang=self.braggpd()*self.scalefac+bragg_offset()
		self.link.setEnergy(self.harmonic()*self.c/self.dspace/sin(ang*pi/180))
		return self.harmonic()*self.c/self.dspace/sin(ang*pi/180)


	def asynchronousMoveTo(self,energy):
		ang=(180/pi*asin(self.harmonic()*self.c/self.dspace/energy)-bragg_offset())/self.scalefac
		self.braggpd.asynchronousMoveTo(ang)

	def isBusy(self):
		i_am_busy = self.braggpd.isBusy()

		#RJW 21/04/08: added this line so that the link.setEnergy is always called and updated
		# once move has completed
		if not i_am_busy:
			self.getPosition()

		return i_am_busy
	
	def stop(self):
		self.braggpd.stop()

	def calibrate(self, newenergy):
		"""Recalibrate the energy of the monochromator """
		cal_ang=180/pi*asin(self.harmonic()*self.c/self.dspace/newenergy)
		dcm_ang=self.braggpd()
		bragg_offset(cal_ang-dcm_ang*self.scalefac)
		print 'Calculated offset='+str(bragg_offset())+' deg'


class EnergyFromBraggFixedoffsetPD(ScannableMotionBase):
	'Energy PD with optional fixed offset - calls Bragg angle PD'
	def __init__(self, name,link):
		self.setName(name);
		self.setInputNames([name])
		#self.setExtraNames([name])
		self.Units=['keV']
		self.setOutputFormat(['%.4f'])
		self.setLevel(3)
		self.braggpd=bragg
		self.perp=perp
		self.dspace=3.1356
#		self.dspace=3.1356/3
		self.scalefac=-1
#			-0.13924 old value
		self.c=6.19921
		self.beamoffset=12
		self.fixedoffsetmode=1
		#self.gap_at_perp_zero=5
		self.gap_at_perp_zero=3.6; #measured by survey may07
		print self.name+'.fixedoffsetmode: '+str(self.fixedoffsetmode)
		print 'gap_at_perp_zero='+str(self.gap_at_perp_zero)
		print self.name+'.beamoffset='+str(self.beamoffset)
		self.setLink(link)


	def setLink(self,link):
		"""Establish the link with the diffractometer objects """
		self.link=link



	def getPosition(self):
		ang=self.braggpd()*self.scalefac+bragg_offset()
		self.link.setEnergy(self.c/self.dspace/sin(ang*pi/180))
		return self.c/self.dspace/sin(ang*pi/180)

	def asynchronousMoveTo(self,energy):
		self.ang=(180/pi*asin(self.c/self.dspace/energy)-bragg_offset())/self.scalefac
		self.braggpd.asynchronousMoveTo(self.ang)
		if self.fixedoffsetmode==1:
			#print "moving perp to",(self.beamoffset/2/cos(ang*pi/180)-self.gap_at_perp_zero)
			self.perp.asynchronousMoveTo(self.beamoffset/2/cos(ang*pi/180)-self.gap_at_perp_zero)

	def isBusy(self):
		i_am_busy = self.braggpd.isBusy() or self.perp.isBusy()

		#RJW 21/04/08: added this line so that the link.setEnergy is always called and updated
		# once move has completed
		if not i_am_busy:
			self.getPosition()

		return i_am_busy



	
	def stop(self):
		self.braggpd.stop()

	def calibrate(self, newenergy):
		cal_ang=180/pi*asin(self.c/self.dspace/newenergy)
		dcm_ang=self.braggpd()
		bragg_offset(cal_ang-dcm_ang*self.scalefac)
		print 'Calculated offset='+str(bragg_offset())+' deg'

class EnergyFromBraggFixedoffsetwithHarmonicPD(ScannableMotionBase):
	'Energy PD with optional fixed offset with Harmonic PD - calls Bragg angle PD'
	def __init__(self,name,link,harmonicPD):
		self.setName(name)
		self.setInputNames([name])
		#self.setExtraNames([name])
		self.Units=['keV']
		self.setOutputFormat(['%.4f'])
		self.setLevel(3)
		self.harmonic = harmonicPD
		self.braggpd=bragg
		self.perp=perp
		self.dspace=3.1356
#		self.dspace=3.1356/3
		self.scalefac=-1
#			-0.13924 old value
		self.c=6.19921
		self.beamoffset=12
		self.fixedoffsetmode=1
		#self.gap_at_perp_zero=5
		self.gap_at_perp_zero=3.6; #measured by survey may07
		print self.name+'.fixedoffsetmode: '+str(self.fixedoffsetmode)
		print 'gap_at_perp_zero='+str(self.gap_at_perp_zero)
		print self.name+'.beamoffset='+str(self.beamoffset)
		self.setLink(link)
		self.warnings=1
		self.next_bragg_angle = None


	def atScanStart(self):
		print self.harmonic
		self.warnings=0

	def atScanEnd(self):
		self.warnings=1


	def setLink(self,link):
		"""Establish the link with the diffractometer objects """
		self.link=link


	def getPosition(self):
		if int(self.harmonic())!=1 and self.warnings == 1:
			print self.harmonic
		self.ang=self.braggpd()*self.scalefac+bragg_offset()
		self.link.setEnergy(self.harmonic()*self.c/self.dspace/sin(self.ang*pi/180))
		return self.harmonic()*self.c/self.dspace/sin(self.ang*pi/180)

	def asynchronousMoveTo(self,energy):
		self.ang=(180/pi*asin(self.harmonic()*self.c/self.dspace/energy)-bragg_offset())/self.scalefac
		self.braggpd.asynchronousMoveTo(self.ang)
		self.next_bragg_angle=self.ang
		if self.fixedoffsetmode==1:
			#print "moving perp to",(self.beamoffset/2/cos(ang*pi/180)-self.gap_at_perp_zero)
			self.perp.asynchronousMoveTo(self.beamoffset/2/cos(self.ang*pi/180)-self.gap_at_perp_zero)

	def isBusy(self):

		i_am_busy = self.braggpd.isBusy() or self.perp.isBusy()

		#RJW 21/04/08: added this line so that the link.setEnergy is always called and updated
		# once move has completed
		if not i_am_busy:
			self.getPosition()

		return i_am_busy


	
	def stop(self):
		self.braggpd.stop()

	def calibrate(self, newenergy):
		cal_ang=180/pi*asin(self.harmonic()*self.c/self.dspace/newenergy)
		dcm_ang=self.braggpd()
		bragg_offset(cal_ang-dcm_ang*self.scalefac)
		print 'Calculated offset='+str(bragg_offset())+' deg'


