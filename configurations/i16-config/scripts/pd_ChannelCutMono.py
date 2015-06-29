# NOTE: Needs classes from pd_undulator



class ChanCutMonoClass(EnergyFromIDandDCM):
	'''
	energy pd 
	pos energy value - changes energy and adjusts vertical positions to compensate
	energy.si() - change to Si coating. Gives better harmonic rejection but usually low reflectivity above 8 keV
	energy.rh() - change to Rh coating. Gives worse harmonic rejection but usually high reflectivity up to 15 keV
	energy.coating() - tells you the current mirror coating
	energy.calibrate() recalibrates heights (don''t do it unless you are sure!!)
	self.maxEnergyChangeBeforeMovingMirrors=energy 	value to prevent mirrors or diffractomter moving for small  energy step
	self.moveDiffWhenNotMovingMirrors=False		set this to True to move diffractometer to compensate for inverted beam movement
	self.mirrormag=-0.666				ratio of vertical movement of focus to source (correct for normal focus)
	'''
	def __init__(self,name,NoWarning=0):
		self.name = name
		self.NoWarning=NoWarning
		self.enpd=energy2
		self.setInputNames(self.enpd.getInputNames())
		self.setExtraNames(self.enpd.getExtraNames())
		self.setOutputFormat(self.enpd.getOutputFormat())
		self.braggpd=bragg
		#self.enpd.__init__()
		self.monogap=7
		self.beamheight=2*self.monogap*cos(self.braggpd()*pi/180)
		self.previousenergy=0
		self.setLevel(3)
		self.maxEnergyChangeBeforeMovingMirrors=0.00001
		self.first_move=True
		self.moveDiffWhenNotMovingMirrors=True
		self.mirrormag=-0.666	#ratio of vertical movement of focus to source

	def getPosition(self):
		self.beamheight=2*self.monogap*cos(self.braggpd()*pi/180)
		self.energy=self.enpd.getPosition()
		return self.energy

	def asynchronousMoveTo(self,new_position):
		self.enpd.asynchronousMoveTo(new_position)
		self.nextheight=2*self.monogap*cos(self.enpd.dcme.next_bragg_angle*pi/180)  
		#option to move mirrors only with large move. Very small number means this is not used.
		if abs(new_position-self.previousenergy)>self.maxEnergyChangeBeforeMovingMirrors or self.first_move==True:
			self.first_move=False
			#use scripted devices due to intermittent probelm with m1x,y
			#M1y.asynchronousMoveTo(m1y_offset()+self.nextheight)
			#M2y.asynchronousMoveTo(m2y_offset()+self.nextheight)
 			m1y.asynchronousMoveTo(m1y_offset()+self.nextheight)
			#print "moving m1y to "+str(m1y_offset()+self.nextheight)
			m2y.asynchronousMoveTo(m2y_offset()+m2_coating_offset()+self.nextheight)
			#print "moving m2y to "+str(m1y_offset()+self.nextheight)
			ztable.asynchronousMoveTo(ztable_offset()+self.nextheight)
			base_z.asynchronousMoveTo(base_z_offset()+self.nextheight)
			self.last_height=self.nextheight	#last value where mirrors were adjusted
		elif self.moveDiffWhenNotMovingMirrors==True:
			base_z.asynchronousMoveTo(base_z_offset()+self.last_height+(self.nextheight-self.last_height)*self.mirrormag)
		self.previousenergy=new_position
		if self.NoWarning <> 1:
			self.check_mirror_coating(new_position)

	def isBusy(self):
		#return self.enpd.isBusy() or m1y.isBusy() or m2y.isBusy() or ztable.isBusy() or base_z.isBusy()
		#return self.enpd.isBusy() or ztable.isBusy() or base_z.isBusy()
		return self.enpd.isBusy() or ztable.isBusy() or base_z.isBusy() or m1y.isBusy() or m2y.isBusy() 

	def waitWhileBusy(self):
		self.enpd.waitWhileBusy()
		ztable.waitWhileBusy()
		base_z.waitWhileBusy()
		m1y.waitWhileBusy()
		m2y.waitWhileBusy() 

	def stop(self):
		self.enpd.stop()
		ztable.stop()
		base_z.stop()
		m1y.stop()
		m2y.stop()
	
	def calibrate(self):
		self.ang=abs(self.braggpd())
		self.beamheight=2*self.monogap*cos(self.braggpd()*pi/180)
		print m1y,'\n',m2y,'\n',ztable,'\n',base_z
		print '=== Old offsets:\n',m1y_offset,'\n',m2y_offset,'\n',ztable_offset,'\n',base_z_offset
		m1y_offset(m1y()-self.beamheight)
		#m2y_offset(m2y()-self.beamheight)
		m2y_offset(m2y()-m2_coating_offset()-self.beamheight)
		ztable_offset(ztable()-self.beamheight)
		base_z_offset(base_z()[0]-self.beamheight)
		print '=== New offsets:\n',m1y_offset,'\n',m2y_offset,'\n',ztable_offset,'\n',base_z_offset

	def check_mirror_coating(self,newenergy):
		if newenergy>8.0:
			if m2y()>0:
				print "=== Warning: mirror coating may be wrong for this energy. Type 'help energy'."

	
	def si(self):
		self.change_coating(m2_coating_offset.si,"=== Changing to Si coating. Gives better harmonic rejection but usually low reflectivity above 8 keV")
	
	def rh(self):
		self.change_coating(m2_coating_offset.rh,"=== Changing to Rh coating. Gives worse harmonic rejection but usually high reflectivity up to 15 keV")
	
	def change_coating(self,offset,message):
		print message
		#move to new coating and cange offset
		#change offset
		m2_coating_offset(offset)
		#make sure a zero energy move is allowed and save warning status and dissable warning
		old_warning=self.NoWarning
		self.NoWarning=1
		old_maxEnergyChangeBeforeMovingMirrors=self.maxEnergyChangeBeforeMovingMirrors
		self.maxEnergyChangeBeforeMovingMirrors=-1
		#do zero energy move to force new mirror offset to change
		energy(energy()[0])
		#go back to previous setting
		self.maxEnergyChangeBeforeMovingMirrors=old_maxEnergyChangeBeforeMovingMirrors
		self.NoWarning=old_warning

	def coating(self):
		if m2y()>0:
			print "=== Mirror coating is probably Si (uncoated). Good for up to 8keV"
		else:
			print "=== Mirror coating is probably Rh. Good for up to 15keV"


