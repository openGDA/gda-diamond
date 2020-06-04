from constants import aum,keV2A,eradius
from gda.configuration.properties import LocalProperties
import os.path
from mathd import *
#from constants import *
import beamline_info as BLi

class Element:

	def __init__(self,name,Z,atomicweight,nfffile):
		#self.setName(name)
		self.Z = Z
		self.atomicweight = atomicweight
		self.nff=ascii2matrix(nfffile)
	#	self.getXproperties()
		
	def getXproperties(self,energy=None):
		if energy == None:
			#energy = keV2A/BLi.getWavelength()
			energy = BLi.getEnergy()
		if energy>30:
			self.f1=0
			self.f2=0.001
		else:
			self.f1 = interplin(self.nff[0],self.nff[1],1000*energy)
			self.f2 = interplin(self.nff[0],self.nff[2],1000*energy)
		self.ff = [self.f1, self.f2]
		return self.ff

#nffdir = '/home_local/gda/dls-sw/gda/config/I16/nff/'
nffdir = os.path.join(LocalProperties.get("gda.var") ,'nff') + '/'
Be = Element('Beryllium',4,9.012182,nffdir+'be.nff')
C = Element('Carbon',6,12.0107,nffdir+'c.nff')
N = Element('Nitrogen',7,14.0067,nffdir+'n.nff')
O = Element('Oxygen',8,15.9994,nffdir+'o.nff')
Al = Element('Aluminium',13,26.9815386,nffdir+'al.nff')
Ar = Element('Argon',18,39.948,nffdir+'ar.nff')
K = Element('Potassium',19,30.0983,nffdir+'k.nff')
V = Element('Vanadium',23,50.9415,nffdir+'v.nff')
Cr = Element('Chromium',24,51.9961,nffdir+'cr.nff')
Mn = Element('Manganese',25,54.938045,nffdir+'mn.nff')
Fe = Element('Iron',26,55.845,nffdir+'fe.nff')
Co = Element('Cobalt',27,58.933195,nffdir+'co.nff')
Ni = Element('Nickel',28,58.6934,nffdir+'ni.nff')
Cu = Element('Copper',29,63.546,nffdir+'co.nff')
Zn = Element('Zinc',30,65.409,nffdir+'zn.nff')
Ga = Element('Gallium',31,69.723,nffdir+'ga.nff')
Nb = Element('Niobium',41,92.90638,nffdir+'nb.nff')
Nd = Element('Neodymium',60,144.242,nffdir+'nd.nff')
Pt = Element('Platinium',78,195.084,nffdir+'pt.nff')
Pb = Element('Lead',82,207.2,nffdir+'pb.nff')

Fe.edges = {'K':7.112}

class Material:

	def __init__(self,name,elements,numbers,density):
		#self.setName(name)
		self.density = density # [kg/m3]
		self.elements = elements
		self.numbers = numbers
		self.cellweight = 0.
		for i in range(len(elements)):
			self.cellweight = self.cellweight+self.numbers[i]*self.elements[i].atomicweight
		self.Vcell = 1e30*aum*self.cellweight/self.density #[A**3]

	def getXproperties(self,energy=None):
		if energy == None:
			#energy = keV2A/BLi.getWavelength()
			energy = BLi.getEnergy()
		self.f1 = 0.
		self.f2 = 0.
		for i in range(len(self.elements)):
			self.elements[i].getXproperties(energy)
			self.f1 = self.f1+self.numbers[i]*self.elements[i].f1
			self.f2 = self.f2+self.numbers[i]*self.elements[i].f2
		llambda = keV2A/energy
		self.delta = eradius/(2*pi)*llambda**2*self.f1/self.Vcell
		self.beta = eradius/(2*pi)*llambda**2*self.f2/self.Vcell
		self.mu = 4*pi/llambda*self.beta
		self.AttenLength = 1./self.mu #[A]
		self.criticAngle = sqrt(2*self.delta)
		self.BrewsterAngle = pi/4-self.delta/2
		#print 'Critical angle (degrees) =', self.criticAngle*180./pi
		#print 'Attenuation length (microns)=', self.AttenLength*1e-4

AlBulk = Material('AlBulk',[Al],[1],2699.)
PbBulk = Material('PbBulk',[Pb],[1],11340.)
PtBulk = Material('PtBulk',[Pt],[1],21090)
NdBulk = Material('NdBulk',[Nd],[1],6800)
Air = Material('Air',[N,O,C,Ar],[1.562,0.42,0.0003,0.0094],1.2)
#HoMn2O5 = Material('HoMn2O5',[Ho,Mn,O],[1,2,5],9)

class Foil:

	def __init__(self,name,mat,thickness):
		self.name =name
		self.mat = mat
		self.thickness = thickness #[microns]
		 
	def getTransmission(self,_energy=None):
		self.mat.getXproperties(_energy)
		self.trans = exp(-self.thickness/self.mat.AttenLength*1e4)
		return self.trans

PtFoil4um = Foil('Ptfoil',PtBulk,4)
NdFoil5um = Foil('Ndfoil',NdBulk,5)
Air1m = Foil('1 m Air',Air,1000)

def ptfoil(energy=None):
	return PtFoil4um.getTransmission(energy)

def ndfoil(energy=None):
	return NdFoil5um.getTransmission(energy)
