## file Crystal.py  contains a class stores the crystallographic info permanently
#  and calculates some fondamental Crystallographic data
#  @author Alessandro Bombardi
#  @version 1.0 (alpha release)
#  Please report bugs to Alessandro.Bombardi@diamond.ac.uk
#  Diamond Light Source Ltd.
import java
import Jama
from math import *
from jarray import array
from Jama import *
import string
from string import *
import ShelveIO

##  This class stores the crystallographic info permanently
#  and calculates some fondamental Crystallographic data
#
class Crystal(java.lang.Object):
   def __init__(self):
   
      "Might be used to define a dummy starting crystal"
      pass
      self.MB=None

###########  Please do not modify ###################

      ## Path for the Crystals files
      #
      self.Crystaldata=ShelveIO.ShelveIO()  ##
      self.Crystaldata.path=ShelveIO.ShelvePath+'Crystals'
      self.Crystaldata.setSettingsFileName('Crystal') ##
      self.Crystaldatauser=ShelveIO.ShelveIO()  ##
      self.Crystaldatauser.path=ShelveIO.ShelvePath+'Crystals'
      self.Crystaldatauser.setSettingsFileName('Crystal') ##
###################################################
      try:
         self.setLattice()
      except:
         print "WARNING: COULD NOT RETRIEVE THE CRYSTAL LATTICE FROM THE DATABASE"  

   ## set the Crystal File Name
   #
   def setCrystal(self,x=None):
#   """ The argument needs to be a string or None,
#   The default file name is Crystal"""
      if x==None:
         self.Crystaldata.setSettingsFileName('Crystal')
      else:
         self.Crystaldata.setSettingsFileName('Crystal')
         self.Crystaldatauser.setSettingsFileName(x)
      return

   ## Retrieve from the current Crystal File the B matrix and the Lattice
   #
   def getCrystal(self,x=None):
      if x==None:
         self.setLattice(self.Crystaldata.getValue('Lattice'))
         try:
            self.MB=Matrix(self.Crystaldata.getValue('BMatrix'))
         except:
            print "The Bmatrix was not stored yet, please reenter the lattice"
      else:
         self.setLattice(self.Crystaldatauser.getValue('Lattice'))
         try:
            self.MB=Matrix(self.Crystaldatauser.getValue('BMatrix'))
         except:
            print "The Bmatrix was not stored yet, please reenter the lattice"
      return self.Crystaldata.getSettingsFileName()

   def setACB(self,x):
      self.acb=x
      return

   ## set the Direct Lattice parameter and calculate and set the Reciprocal Lattice
   #
   def setLattice(self,L=None):
      """@sig public void setLattice(double[] L)"""
#      print "I am setting the lattice"
      if L==None:
         L=self.Crystaldata.getValue('Lattice')
      self.a = L[0]
      self.b = L[1]
      self.c = L[2]
      self.alpha = L[3]
      self.beta = L[4]
      self.gamma = L[5]
      self.calcRLattice()
      self.Crystaldata.ChangeValue('Lattice',L)
      self.setBMatrix()      
      return

   ## get the Direct Lattice parameter
   #
   def getLattice(self):
      """getLattice() get the stored values of the lattice """
      try:	
         ostr = self.Crystaldata.getValue('Lattice')
      except:
         ostr = None
         print "Warning:: Lattice parameter not saved or not accessible, please check the crystal name "
      return ostr

   ## Calculate and save the Reciprocal Lattice parameter
   #
   def calcRLattice(self):
      "@sig public void calcRLattice()"
      alph = self.alpha
      bet = self.beta
      gamm = self.gamma

      self.alpha1=alph*pi/180.0
      self.alpha2=bet*pi/180.0
      self.alpha3=gamm*pi/180.0

      self.beta1=acos( (cos(self.alpha2)*cos(self.alpha3)-cos(self.alpha1))/(sin(self.alpha2)*sin(self.alpha3)))
      self.beta2=acos( (cos(self.alpha1)*cos(self.alpha3)-cos(self.alpha2))/(sin(self.alpha1)*sin(self.alpha3)))
      self.beta3=acos( (cos(self.alpha1)*cos(self.alpha2)-cos(self.alpha3))/(sin(self.alpha1)*sin(self.alpha2)))



      self.b1=1./(self.a*sin(self.alpha2)*sin(self.beta3))
      self.b2=1./(self.b*sin(self.alpha3)*sin(self.beta1))
      self.b3=1./(self.c*sin(self.alpha1)*sin(self.beta2))

      self.Crystaldata.ChangeValue('RLattice',[round(self.b1,4),round(self.b2,4),round(self.b3,4),round(self.beta1*180.0/pi,4),round(self.beta2*180.0/pi,4),round(self.beta3*180.0/pi,4)])
      return

   ## get the Reciprocal Lattice parameter
   #
   def getRLattice(self):
      "@sig public java.lang.String getRlattice()"
      rl = self.Crystaldata.getValue('RLattice')
      return rl

   ## Calculate the volume of the cells
   #
   def calcVolumes(self):
      "@sig public void CalcVolumes()"
      self.Vce=sqrt((self.a**2)*(self.b**2)*(self.c**2)*(1-cos(self.alpha1)**2-cos(self.alpha2)**2-cos(self.alpha3)**2+2*cos(self.alpha1)*cos(self.alpha2)*cos(self.alpha3)))
      self.Vcr=sqrt((self.b1**2)*(self.b2**2)*(self.b3**2)*(1-cos(self.beta1)**2-cos(self.beta2)**2-cos(self.beta3)**2+2*cos(self.beta1)*cos(self.beta2)*cos(self.beta3)))
      return

   ## get the volumes of the cells
   #
   def getVolumes(self):
      "@sig public java.lang.String getVolumes()"
      outvolumes = "Calculated Vol.(Vce, Vcr, Vce*Vcr): %s %s %s" % (self.Vce,self.Vcr,self.Vce*self.Vcr)
      return outvolumes
      
   ## Set and save the B matrix
   #
   def setBMatrix(self):
      "@sig public void setBMatrix()"
#Comment to check with Pincer
      self.B=[[self.b1, self.b2*cos(self.beta3), self.b3*cos(self.beta2)],[0.0, self.b2*sin(self.beta3), -self.b3*sin(self.beta2)*cos(self.alpha1)], [0.0, 0.0, 1.0/self.c]]
############ remember to go back#######
#Same as pincer
#      self.B=[[self.b1, self.b2*cos(self.beta3), self.b3*cos(self.beta2)],[0.0, self.b2*sin(self.beta3), -self.b2*sin(self.beta2)*cos(self.beta1)], [0.0, 0.0, 1.0/self.c]]
      self.Crystaldata.ChangeValue('BMatrix',self.B)
      self.B = Matrix(self.B)
      self.MB =self.B
      return

   ## Restore the B matrix and returns it
   #
   def getBMatrix(self):
      "@sig public double[][] getUBMatrix()"
      if self.MB == None:
         self.MB=Matrix(self.Crystaldata.getValue('BMatrix'))
      return self.MB

      
   ## Calculate the lattice from the B matrix
   #
   def fromBtolat(self):
      self.Gmu=(self.MB.transpose().times(self.MB)).inverse()
      print "a=",sqrt(self.Gmu.get(0,0))
      print "b=",sqrt(self.Gmu.get(1,1))
      print "c=",sqrt(self.Gmu.get(2,2))
      print "alpha=",acos(self.Gmu.get(1,2)/sqrt(self.Gmu.get(1,1)*self.Gmu.get(2,2)))*180.0/pi
      print "beta=",acos(self.Gmu.get(0,2)/sqrt(self.Gmu.get(0,0)*self.Gmu.get(2,2)))*180.0/pi
      print "gamma=",acos(self.Gmu.get(0,1)/sqrt(self.Gmu.get(0,0)*self.Gmu.get(1,1)))*180.0/pi
      return


   ## Calculate the distance between hkl planes
   #
   def d_hkl(self,H):
      "@sig public double d_hkl(double H)"
      h=H[0]
      k=H[1]
      l=H[2]
      c1= self.b1*self.b2*cos(self.beta3)
      c2= self.b1*self.b3*cos(self.beta2)
      c3= self.b2*self.b3*cos(self.beta1)
      d=sqrt(1.0/(h**2*self.b1**2+k**2*self.b2**2+l**2*self.b3**2+2*h*k*c1+2*h*l*c2+2*k*l*c3))
      return d


   ## Calculate the angle between two reflections,
   #known the lattice parameter and the B matrix
   #
   def Angle(self,H,K):
      H=self.B.times(Matrix(H,3))
      K=self.B.times(Matrix(K,3)).transpose()
      modH=sqrt(H.transpose().times(H).get(0,0))
      modK=sqrt(K.times(K.transpose()).get(0,0))
      a=K.times(H).get(0,0)/(modH*modK)
      alp=acos(a)*180./pi
      return alp

   ## Throws an error message
   #
   def __repr__(self):
      return '<Crystal Bean Error>'
