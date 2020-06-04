
import java
import ShelveIO
from datetime import date
from mathd import *
from gda.device.scannable import ScannableMotionBase
import traceback

class Harmonic(ScannableMotionBase):

	def __init__(self,name):
		self.setName(name)
		self.setInputNames([name])
		self.h=ShelveIO.ShelveIO()
		self.h.path=ShelveIO.ShelvePath+'harmonic'
		self.h.setSettingsFileName('harmonic')
		self.label=0

	def isBusy(self):
		return 0		

	def getPosition(self):
		return self.h.getValue(name)

	def asynchronousMoveTo(self,position):
		self.label=1
		comstring='self.'+name+'=position'
		comstring2='self.'+name+'label=1'
		exec(comstring)
		exec(comstring2)
		self.h.ChangeValue(name,position)


class Undulator2(ScannableMotionBase):

#	def __init__(self,name,harmonic,gap,gapoffset,GBHfile):
	def __init__(self,name,harmonic,gap,gapoffset,defaultenergydevice,GBHfile):
		self.setName(name)
		self.setInputNames([gap.name])
		self.setExtraNames(['Uenergy',harmonic.name])
		self.setOutputFormat(['%4.4f','%4.4f','%d'])
		self.gap = gap
		self.gapoffset = gapoffset
		self.lambdaU = 2.7 #[cm]
		self.length = 2. #[m]
		self.nperiod = int(100*self.length/self.lambdaU)
		self.Br = 1.06
		#self.Ering = 3.1282
		self.Ering = 3.05 #[GeV]
		self.Emax = keV2A/13.056*self.Ering**2/self.lambdaU
		self.GBH = ascii2matrix(GBHfile)
		self.harmonic = harmonic
		self.harmonics = [0]*12
		self.dcmenergy = defaultenergydevice
		#self.getPosition()

	def getPosition(self):
		#self.Bmax = interplin(self.gapB[0],self.gapB[-1],self.gap())
		self.Bmax = interplin(self.GBH[0],self.GBH[1],self.gap()+self.gapoffset())
		if self.Bmax==None:
			print 'gap out of look-up table range'
			self.Bmax=0.
		#print self.Bmax
		self.Bpeak = 1.8*self.Br*exp(-pi*(self.gap()+self.gapoffset())/self.lambdaU)
		self.Keff = 0.934*self.lambdaU*self.Bmax
		self.GK = self.Keff*(self.Keff**6+24./7*self.Keff**4+4*self.Keff**2+16./7)/(1+self.Keff**2)**3.5
		#self.totalpower = 0.633*self.Ering**2*self.Bmax**2*self.length*rc #[W]
		#self.dPdO0 = 10.84*self.Bmax*self.Ering**4*rc*self.nperiod*self.GK
		self.harmonics[0] = self.Emax/(1+self.Keff**2/2)
		for i in range(1,12):
#			self.harmonic[i]=interplin(self.gapH[0],self.gapH[i+1],self.gap())
#			self.harmonic[i]=interplin(self.GBH[0],self.GBH[i+2],self.gap())
			self.harmonics[i] = (2*i+1)*self.harmonics[0]
		H = int(self.harmonic())
		return [self.gap(), self.harmonics[(H-1)/2], H]

	def asynchronousMoveTo(self,new_position):
		self.gap.asynchronousMoveTo(new_position)

	def isBusy(self):
		return self.gap.isBusy()

	def setK(self,newK):
		newB = newK/self.lambdaU/0.934
#		newGap = interplin(self.gapB[-1],self.gapB[0],newB)
		newGap = interplin(self.GBH[1],self.GBH[0],newB)
		self.asynchronousMoveTo(newGap)
		print 'new gap value:', newGap

	def calcGap(self,newenergy=None,H=None):
		if newenergy==None:
			newenergy = self.dcmenergy()
		if H == None:
			H = self.harmonic()
		if newenergy/H > self.Emax:
			print "This energy is too high for this harmonic"
			return None
		newK = sqrt(2*(keV2A/13.056*self.Ering**2/self.lambdaU*H/newenergy-1))
		newB = newK/self.lambdaU/0.934
		newgap = interplin(self.GBH[1],self.GBH[0],newB)-self.gapoffset()
#		print 'calculated gap =', newgap
		return newgap

	def setEnergy(self,newenergy=None,H=None):
		if newenergy==None:
			newenergy = self.dcmenergy()
		if H != None:
			self.harmonic(H)
		newgap = self.calcGap(newenergy,H)
		#print 'new gap value:', newgap
		try:
			self.asynchronousMoveTo(newgap)
		except:
			print 'gap did not move'

	def calibrate(self,newenergy=None,H=None):
		if newenergy==None:
			newenergy = self.dcmenergy()
		if H==None:
			H = self.harmonic()
		newK = sqrt(2*(keV2A/13.056*self.Ering**2/self.lambdaU*H/newenergy-1))
		newB = newK/self.lambdaU/0.934
		newgap = interplin(self.GBH[1],self.GBH[0],newB)
		self.gapoffset(newgap-self.gap())
		print 'new gap offset:', self.gapoffset()
		nowstr = date.today().strftime('%d-%m-%y')
		wstr = nowstr+'\t'+str(self.harmonic())+'\t'+str(newenergy)+'\t'+str(self.gap())+'\t'+str(self.gapoffset())+'\n'
		f=open('/dls_sw/i16/var/ucalibrate.log','a')
		f.write(wstr)
		f.close()
		print 'new calibration saved in /dls_sw/i16/var/ucalibrate.log'


class Undulator(ScannableMotionBase):

	def __init__(self,name,gap,gapoffset,GBHfile):
		self.setName(name)
		self.setInputNames(['IDgap'])
		self.setExtraNames(['UEnergy','harmonic'])
		self.setOutputFormat(['%4.4f','%4.4f','%4.0f'])
		self.gap = gap
		self.gapoffset = gapoffset
		self.lambdaU = 2.7 #[cm]
		self.length = 2. #[m]
		self.nperiod = int(100*self.length/self.lambdaU)
		self.Br = 1.06
		#self.Ering = 3.1282
		self.Ering = 3.05 #[GeV]
		self.Emax = keV2A/13.056*self.Ering**2/self.lambdaU
		self.GBH = ascii2matrix(GBHfile)
		self.H = 3
		self.harmonic = [0]*12
		self.getPosition()

	def getPosition(self):
		#self.Bmax = interplin(self.gapB[0],self.gapB[-1],self.gap())
		self.Bmax = interplin(self.GBH[0],self.GBH[1],self.gap()+self.gapoffset())
		if self.Bmax==None:
			print 'gap out of look-up table range'
			self.Bmax=0.
		#print self.Bmax
		self.Bpeak = 1.8*self.Br*exp(-pi*(self.gap()+self.gapoffset())/self.lambdaU)
		self.Keff = 0.934*self.lambdaU*self.Bmax
		self.GK = self.Keff*(self.Keff**6+24./7*self.Keff**4+4*self.Keff**2+16./7)/(1+self.Keff**2)**3.5
		#self.totalpower = 0.633*self.Ering**2*self.Bmax**2*self.length*rc #[W]
		#self.dPdO0 = 10.84*self.Bmax*self.Ering**4*rc*self.nperiod*self.GK
		self.harmonic[0] = self.Emax/(1+self.Keff**2/2)
		for i in range(1,12):
#			self.harmonic[i]=interplin(self.gapH[0],self.gapH[i+1],self.gap())
#			self.harmonic[i]=interplin(self.GBH[0],self.GBH[i+2],self.gap())
			self.harmonic[i] = (2*i+1)*self.harmonic[0]
		return [self.gap(), self.harmonic[(self.H-1)/2], self.H]

	def asynchronousMoveTo(self,new_position):
		self.gap.asynchronousMoveTo(new_position)

	def isBusy(self):
		return self.gap.isBusy()

	def setK(self,newK):
		newB = newK/self.lambdaU/0.934
#		newGap = interplin(self.gapB[-1],self.gapB[0],newB)
		newGap = interplin(self.GBH[1],self.GBH[0],newB)
		self.asynchronousMoveTo(newGap)
		print 'new gap value:', newGap

	def calcGap(self,newenergy,harmonic=None,gapoffset2=None):
		if harmonic == None:
			harmonic = self.H
		if newenergy/harmonic > self.Emax:
			print "This energy is too high for this harmonic"
			return None
		if gapoffset2 == None:
			gapoffset2 = 0
		newK = sqrt(2*(keV2A/13.056*self.Ering**2/self.lambdaU*harmonic/newenergy-1))
		newB = newK/self.lambdaU/0.934
		newgap = interplin(self.GBH[1],self.GBH[0],newB)-self.gapoffset()-gapoffset2
#		print 'calculated gap =', newgap
		return newgap

	def setEnergy(self,newenergy,harmonic=None,gapoffset2=None):
		if harmonic != None:
			self.H = harmonic
		newgap = self.calcGap(newenergy,harmonic,gapoffset2)
		#print 'new gap value:', newgap
		try:
			self.asynchronousMoveTo(newgap)
		except:
			print 'gap did not move'

	def calibrate(self,newenergy,harmonic=None):
		if harmonic == None:
			harmonic = self.H
		newK = sqrt(2*(keV2A/13.056*self.Ering**2/self.lambdaU*harmonic/newenergy-1))
		newB = newK/self.lambdaU/0.934
		newgap = interplin(self.GBH[1],self.GBH[0],newB)
		self.gapoffset(newgap-self.gap())
		print 'new gap offset:', self.gapoffset()


class EnergyFromUndulator(ScannableMotionBase):

	def __init__(self,name,undulator):
		self.setName(name)
		self.setInputNames(['Uenergy'])
		self.setExtraNames(['Uharmonic','IDgap'])
		self.setOutputFormat(['%4.4f','%4.0f','%4.4f'])
		self.undulator = undulator

	def getPosition(self):
		val = self.undulator.getPosition()
		#return [self.undulator.harmonic[(self.undulator.H-1)/2],self.undulator.H]
		#return [self.undulator.harmonic[(self.undulator.H-1)/2], self.undulator.H, self.undulator()]
		return [val[1], val[2], val[0]]

	def asynchronousMoveTo(self,energy,harmonic=None,gapoffset2=None):
		self.undulator.setEnergy(energy,harmonic,gapoffset2)

	def isBusy(self):
		return self.undulator.isBusy()


class EnergyFromUndulator2(ScannableMotionBase):

	def __init__(self,name,undulator):
		self.setName(name)
		self.setInputNames(['Uenergy'])
		#self.setExtraNames(['Uharmonic','IDgap'])
		#self.setOutputFormat(['%4.4f','%4.0f','%4.4f'])
		self.setOutputFormat(['%4.4f'])
		self.undulator = undulator

	def getPosition(self):
		val = self.undulator.getPosition()
		#return [self.undulator.harmonic[(self.undulator.H-1)/2],self.undulator.H]
		#return [self.undulator.harmonic[(self.undulator.H-1)/2], self.undulator.H, self.undulator()]
		#return [val[1] val[2] val[0]]
		return val[1]

	def asynchronousMoveTo(self,energy,H=None):
		self.undulator.setEnergy(energy,H)

	def isBusy(self):
		return self.undulator.isBusy()


class EnergyFromIDandDCM(ScannableMotionBase):

	def __init__(self,name,Uenergy,DCMenergy):
		self.setName(name)
		self.ue = Uenergy
		self.dcme = DCMenergy
		self.setInputNames([name])
		self.setExtraNames([self.ue.name,'DCMenergy'])
		self.setOutputFormat(['%4.4f','%4.4f','%4.4f'])
		self.E = self.dcme()

	def getPosition(self):
		#self.id.getPosition()
		#return [self.ue() self.dcme()]
		return [self.E, self.ue(), self.dcme()]

	def asynchronousMoveTo(self,energy):
		self.E = energy
		try:
			self.ue.asynchronousMoveTo(energy)
			self.dcme.asynchronousMoveTo(energy)
		except (java.lang.Exception, Exception), e: # ANYTHING
			print "Error moving " + self.getName() + " (EnergyFromIDandDCM) to: " + `energy`
			print traceback.format_exc() + "<< No exception raised >>>"

	def isBusy(self):
		if self.ue.isBusy() or self.dcme.isBusy():
			return 1
		else:
			return 0

class ShowGapClass(ScannableMotionBase):

	def __init__(self):
		self.setName('idgap')
		self.setInputNames(['energy','harmonic'])
		self.setExtraNames(['idgap'])
		self.setOutputFormat(['%.3f','%.0f','%.3f'])
		self.energy=999
		self.harmonic=3

	def getPosition(self):
		try:
			#print self.calcgap
			self.calcgap=calcgap(self.energy, self.harmonic)
			self.calcgap=float(self.calcgap)
			#print self.calcgap
		except:
			self.calcgap=0.0
		return [float(self.energy), float(self.harmonic), self.calcgap]

	def asynchronousMoveTo(self,newvals):
		self.energy=newvals[0];
		self.harmonic=newvals[1];

	def isBusy(self):
		return 0

showgap=ShowGapClass()
