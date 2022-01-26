## @file UBmatrix.py contains a class dealing with the orientation
#  matrix of a crystal
#
#  @author Alessandro Bombardi
#  @version 1.0 (alpha release)
#  Please report bugs to Alessandro.Bombardi@diamond.ac.uk
#  Diamond Light Source Ltd.

import java
import Jama
from Jama import Matrix
import Rotations
from Rotations import *
from math import *
import string
from string import *
from MatrixAlgebra import CROSS
from Orthonormalize import orthonormalize as orto
import ShelveIO
from Reflection import Reflections

import Diffractometer as sixC

## class dealing with the orientation
#  matrix of a crystal
class UBmatrix(java.lang.Object):
   def __init__(self):

###########  Please do not modify ###################
      self.UBdata=ShelveIO.ShelveIO()  ##
      self.UBdata.path=ShelveIO.ShelvePath+'UB'
      self.UBdata.setSettingsFileName('UB') ##
      self.UB=None
      self.U=None
      self.I = Matrix([[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])
      self.orO=None
      self.or1=None
      self.or2=None
      self.getUB()
###################################################


################ LINKS WITH THE OTHER CLASSES  #################################

   ## Establish a link with the Crystal class
   #
   def setCrystalmanagement(self,Xtalmanager):
      """ Void function that establish a link with the instantiation of the Crystal class: 
      Takes as argument the name of the instantiation of the Crystal class. \n 
      It returns no argument and does not provide any error message. \n
      Called only when the instance of the anglecalculation code is created. \n
      """
      self.xtal = Xtalmanager
      return

   ## Establish a link with the ReflManagement class
   #
   def setReflmanagement(self,reflmanager):
      """ Void function that establish a link with the instantiation of the Reflmanagement class
      ...Takes as argument the name of the instantiation of the Reflmanagement class.
      It returns no argument and does not provide any error message. 
      Called only when the instance of the anglecalculation code is created. 
      """
      self.rm = reflmanager
      return

   ## Establish a link with the gettth class
   #
   def set2theta(self,get2theta):
      """ Void function that establish a link with the instantiation of the gettth class
      ...Takes as argument the name of the instantiation of the gettth class.
      It returns no argument and does not provide any error message. 
      Called only when the instance of the anglecalculation code is created. 
      """
      self.tt =get2theta
      return
################################################################################


   ## Assign the reflection specified to the 1st, 2nd and an optional
   #  3rd reflection to or0, or1 and or2 respectively, and stores these reflections
   def setOrient(self,n1,n2=None,n3=None):
      """ Void functions, Takes three arguments, the second and the thirs are optional. 
The arguments are the name in the dictionary of the reflections. The function associates the three 
reflections to or0, or1 and or2
3rd reflection to or0, or1 and or2 respectively, and stores these reflections in the UB matrix database
      """
      self.or0=self.rm.getReflection(n1)
      self.UBdata.ChangeValue('or0',self.rm.getReflection(n1))
      if n2 is not None:
         self.or1=self.rm.getReflection(n2)
         self.UBdata.ChangeValue('or1',self.rm.getReflection(n2))
      if n3 ==None:
         self.or2=None
      elif n3 != None:
         self.or2=self.rm.getReflection(n3)
         self.UBdata.ChangeValue('or2',self.rm.getReflection(n3))
      return

   ## to implement will return the reflection currently used for the UB matrix
   #  calculations
   def getOrient(self):
      return



   ## Return or0
   #
   def getOr0(self):
      return self.UBdata.getValue('or0')

   ## Return or1
   #
   def getOr1(self):
      return self.UBdata.getValue('or1')

   ## Return or2
   #
   def getOr2(self):
      return self.UBdata.getValue('or2')



   def setUB(self,refl1=None):
      """ 
      Void function, takes one optional argument [h,k,l] 
      and according to the number of argument and to the existence of 1,2, or 3 
      reflections to orient the crystal will chose the method to calculate the UB matrix.
      """
#      try:
      if isinstance(self.or2,Reflections) and isinstance(self.rm.getReflectionsObj(),Reflections):
      #elif isinstance(self.or2,self.rm.Reflections.getClass()) == 1:
         pass
         self.setUB3()
      #if isinstance(self.or2,self.rm.getReflectionsObj().getClass()) == 0:
      else:
         self.setUB2(refl1)
      self.SaveMatrix('U',self.U)
      self.UB=self.U.times(self.xtal.MB)
      self.SaveMatrix('UB',self.UB)
#      except:
#         print "Exception raised: It is not possible to set the UB matrix"
      return

   def setUB2VER(self,refl1=None):
      """ Void function called normally with no arguments, the optional argument is [h,k,l], 
      if provided the [h,k,l] values will be considered as a reflection in the scattering plane. 
      Therefore it will be used to determine a theoretical or1 reflection. With no argument setUB2 
      will determine the UB matrix using the two stored reflections """
###################################################################################################
# ORTOGONAL SYSTEM IN THE CRYSTAL CARTESIAN BASIS
# (X is // to the principal reflection, Y in the plane of the principal and secondary reflection,
# Z is prependicular to this plane
####################################################################################################
      MH_pc = self.xtal.MB.times(Matrix(self.or0.hkl,3))
      #if isinstance(self.or1,self.rm.Reflections.getClass()) == 0:
#      if self.or1 == None:
      if refl1 is not None:
         self.or1 = self.rm.Reflections
         self.or1.sixC  = self.rm.Reflections
         try:
            self.or1.hkl = refl1
            self.or1.Energy = self.or0.Energy
            self.or1.wl = self.or0.wl
            self.or1.sixC.Phi = self.or0.Phi
            self.or1.sixC.Chi =self.or0.Chi
            ang1=self.xtal.Angle(self.or0.hkl,self.or1.hkl)
#            print "ang1",ang1
            if abs(self.or0.Delta) <= 1.0e-2 and self.or0.Gamma != 0.0:
               self.or1.Delta = 0.
               self.or1.Eta =self.or0.Eta
               self.or1.Gamma = self.tt.calctth(self.or1.hkl,self.or1.Energy)
               ang2= self.or0.Gamma/2.-self.or0.Mu
               self.or1.Mu = self.tt.calctth(self.or1.hkl,self.or1.Energy)/2. +ang2 +ang1
            elif self.or0.sixC.Delta != 0.0 and abs(self.or0.Gamma) <= 1.0e-2:
               self.or1.Delta = self.tt.calctth(self.or1.hkl,self.or1.Energy)
               self.or1.Mu =self.or0.Mu
               ang2= self.or0.Delta/2.-self.or0.Eta
               self.or1.Gamma = 0.
               self.or1.Eta = self.tt.calctth(self.or1.hkl,self.or1.Energy)/2. -ang2 +ang1
            else:
               print "TO IMPLEMENT"
         except:
            print "Warning: Please provide the index of a dummy reflection"
      MH_sc = self.xtal.MB.times(Matrix(self.or1.hkl,3))
      T_c=orto([MH_pc.get(0,0),MH_pc.get(1,0),MH_pc.get(2,0)],[MH_sc.get(0,0),MH_sc.get(1,0),MH_sc.get(2,0)])
      Qm=2*sin(self.tt.calctth(self.or0.hkl,self.or0.Energy)/2.*(pi/180.0))/self.or0.wl
      Qm= 2.*pi/self.or0.wl
      qvpo=[0.,Qm,0.]
      qvp=Matrix([qvpo]).transpose()
      self.Z=sixC.setZ(self.or0.Mu,self.or0.Eta,self.or0.Chi,self.or0.Phi)
      self.DA=sixC.setDA(self.or0.Delta,self.or0.Gamma)
      qvp=(self.DA.minus(self.I)).times(qvp)
      qvp=qvp.times(1/qvp.normF()).times(Qm)
      uphi_p=self.Z.inverse().times(qvp)
      Qs=2*sin(self.tt.calctth(self.or1.hkl,self.or1.Energy)/2.*(pi/180.0))/self.or1.wl
      Qs =2.*pi/self.or1.wl
#      print "Test of the UB "
      qvs=[0.,Qs,0.]
      qvs=Matrix([qvs]).transpose()
      self.Z=sixC.setZ(self.or1.Mu,self.or1.Eta,self.or1.Chi,self.or1.Phi)
      self.DA=sixC.setDA(self.or1.Delta,self.or1.Gamma)
      qvs=self.DA.minus(self.I).times(qvs)
      uphi_s=self.Z.inverse().times(qvs)
############################################################
# ORTOGONAL SYSTEM IN THE PHI AXIS SYSTEM (diffractometer)
# (X is // to the principal reflection, Y in the plane of the principal and secondary reflection,
# Z is prependicular to this plane
############################################################
      T_phi=orto([uphi_p.get(0,0),uphi_p.get(1,0),uphi_p.get(2,0)],[uphi_s.get(0,0),uphi_s.get(1,0),uphi_s.get(2,0)])
      self.U=T_phi.times(T_c.inverse())
      return





   def setUB2(self,refl1=None):
      """ Void function called normally with no arguments, the optional argument is [h,k,l], 
      if provided the [h,k,l] values will be considered as a reflection in the scattering plane. 
      Therefore it will be used to determine a theoretical or1 reflection. With no argument setUB2 
      will determine the UB matrix using the two stored reflections """
###################################################################################################
# ORTOGONAL SYSTEM IN THE CRYSTAL CARTESIAN BASIS
# (X is // to the principal reflection, Y in the plane of the principal and secondary reflection,
# Z is prependicular to this plane
####################################################################################################
      MH_pc = self.xtal.MB.times(Matrix(self.or0.hkl,3))
      #if isinstance(self.or1,self.rm.Reflections.getClass()) == 0:
#      if self.or1 == None:
      if refl1 is not None:
         self.or1 = self.rm.Reflections
         self.or1.sixC  = self.rm.Reflections
         try:
            self.or1.hkl = refl1
            self.or1.Energy = self.or0.Energy
            self.or1.wl = self.or0.wl
            self.or1.sixC.Phi = self.or0.sixC.Phi
            self.or1.sixC.Chi =self.or0.sixC.Chi
            ang1=self.xtal.Angle(self.or0.hkl,self.or1.hkl)
#            print "ang1",ang1
            if abs(self.or0.sixC.Delta) <= 1.0e-2 and self.or0.sixC.Gamma != 0.0:
               self.or1.sixC.Delta = 0.
               self.or1.sixC.Eta =self.or0.sixC.Eta
               self.or1.sixC.Gamma = self.tt.calctth(self.or1.hkl,self.or1.Energy)
               ang2= self.or0.sixC.Gamma/2.-self.or0.sixC.Mu
               self.or1.sixC.Mu = self.tt.calctth(self.or1.hkl,self.or1.Energy)/2. +ang2 +ang1
            elif self.or0.sixC.Delta != 0.0 and abs(self.or0.sixC.Gamma) <= 1.0e-2:
               self.or1.sixC.Delta = self.tt.calctth(self.or1.hkl,self.or1.Energy)
               self.or1.sixC.Mu =self.or0.sixC.Mu
               ang2= self.or0.sixC.Delta/2.-self.or0.sixC.Eta
               self.or1.sixC.Gamma = 0.
               self.or1.sixC.Eta = self.tt.calctth(self.or1.hkl,self.or1.Energy)/2. -ang2 +ang1
            else:
               print "TO IMPLEMENT"
         except:
            print "Warning: Please provide the index of a dummy reflection"
      MH_sc = self.xtal.MB.times(Matrix(self.or1.hkl,3))
      T_c=orto([MH_pc.get(0,0),MH_pc.get(1,0),MH_pc.get(2,0)],[MH_sc.get(0,0),MH_sc.get(1,0),MH_sc.get(2,0)])
      Qm=2*sin(self.tt.calctth(self.or0.hkl,self.or0.Energy)/2.*(pi/180.0))/self.or0.wl
      Qm= 2.*pi/self.or0.wl
      qvpo=[0.,Qm,0.]
      qvp=Matrix([qvpo]).transpose()
      self.Z=sixC.setZ(self.or0.sixC.Mu,self.or0.sixC.Eta,self.or0.sixC.Chi,self.or0.sixC.Phi)
      self.DA=sixC.setDA(self.or0.sixC.Delta,self.or0.sixC.Gamma)
      qvp=(self.DA.minus(self.I)).times(qvp)
      qvp=qvp.times(1/qvp.normF()).times(Qm)
      uphi_p=self.Z.inverse().times(qvp)
      Qs=2*sin(self.tt.calctth(self.or1.hkl,self.or1.Energy)/2.*(pi/180.0))/self.or1.wl
      Qs =2.*pi/self.or1.wl
#      print "Test of the UB "
      qvs=[0.,Qs,0.]
      qvs=Matrix([qvs]).transpose()
      self.Z=sixC.setZ(self.or1.sixC.Mu,self.or1.sixC.Eta,self.or1.sixC.Chi,self.or1.sixC.Phi)
      self.DA=sixC.setDA(self.or1.sixC.Delta,self.or1.sixC.Gamma)
      qvs=self.DA.minus(self.I).times(qvs)
      uphi_s=self.Z.inverse().times(qvs)
############################################################
# ORTOGONAL SYSTEM IN THE PHI AXIS SYSTEM (diffractometer)
# (X is // to the principal reflection, Y in the plane of the principal and secondary reflection,
# Z is prependicular to this plane
############################################################
      T_phi=orto([uphi_p.get(0,0),uphi_p.get(1,0),uphi_p.get(2,0)],[uphi_s.get(0,0),uphi_s.get(1,0),uphi_s.get(2,0)])
      self.U=T_phi.times(T_c.inverse())
      return




   ## Not accessed Directly, it calculates the UB matrix from or0, or1 and or2,
   #  when the lattice is not known. This function returns an UB matrix but it
   #  does not automatically set
   def setUB3(self):
      """ Not often used, it attempts to calculate the UB matrix from or0, or1 and or2,
      when the lattice is not known."""
      Qm= 2.*pi/self.or0.wl
      Qm= 1./self.or0.wl
      qvpo=[0.,Qm,0.]
      qvp=Matrix([qvpo]).transpose()
      self.Z=sixC.setZ(self.or0.sixC.Mu,self.or0.sixC.Eta,self.or0.sixC.Chi,self.or0.sixC.Phi)
      self.DA=sixC.setDA(self.or0.sixC.Delta,self.or0.sixC.Gamma)
      qvp=(self.DA.minus(self.I)).times(qvp)
      #qvp=qvp.times(1/qvp.normF()).times(Qm)
      uphi_p=self.Z.inverse().times(qvp)
      Qs =2.*pi/self.or1.wl
      Qs =1./self.or1.wl
      qvs=[0.,Qs,0.]
      qvs=Matrix([qvs]).transpose()
      self.Z=sixC.setZ(self.or1.sixC.Mu,self.or1.sixC.Eta,self.or1.sixC.Chi,self.or1.sixC.Phi)
      self.DA=sixC.setDA(self.or1.sixC.Delta,self.or1.sixC.Gamma)
      qvs=self.DA.minus(self.I).times(qvs)
      #qvs=qvs.times(1/qvs.normF()).times(Qs)
      uphi_s=self.Z.inverse().times(qvs)
      Qt =2.*pi/self.or2.wl
      Qt =1./self.or2.wl
      qvt=[0.,Qt,0.]
      qvt=Matrix([qvt]).transpose()
      self.Z=sixC.setZ(self.or2.sixC.Mu,self.or2.sixC.Eta,self.or2.sixC.Chi,self.or2.sixC.Phi)
      self.DA=sixC.setDA(self.or2.sixC.Delta,self.or2.sixC.Gamma)
      qvt=self.DA.minus(self.I).times(qvt)
      #qvt=qvt.times(1/qvt.normF()).times(Qt)
      print "I am using the new method"
      uphi_t=self.Z.inverse().times(qvt)


      H_phi =  Matrix(3,3)
      H_phi.setMatrix(0,2,0,0,uphi_p)
      H_phi.setMatrix(0,2,1,1,uphi_s)
      H_phi.setMatrix(0,2,2,2,uphi_t)

      H = Matrix(3,3)
      H.setMatrix(0,2,0,0,Matrix([self.or0.hkl]).transpose())
      H.setMatrix(0,2,1,1,Matrix([self.or1.hkl]).transpose())
      H.setMatrix(0,2,2,2,Matrix([self.or2.hkl]).transpose())

      UB=H_phi.times(H.inverse())
      return UB

   def setUBnrefVER(self,lista=None):
      if lista==None:
      	lista=self.rm.getReflectionKeys()
      H_phi =Matrix(3,len(lista))
      H = Matrix(3,len(lista))
      for i in range(len(lista)):
         refl=self.rm.getReflection(lista[i])
         Qm= 1./refl.wl
         qvpo=[0.,Qm,0.]
         qvp=Matrix([qvpo]).transpose()
         self.Z=sixC.setZ(refl.Mu,refl.Eta,refl.Chi,refl.Phi)
         self.DA=sixC.setDA(refl.Delta,refl.Gamma)
         qvp=(self.DA.minus(self.I)).times(qvp)
         uphi=self.Z.inverse().times(qvp)
         H_phi.setMatrix(0,2,i,i,uphi)
         H.setMatrix(0,2,i,i,Matrix([refl.hkl]).transpose())
      Ht=H.transpose()
      HHt_i=H.times(H.transpose()).inverse()
      self.UB=H_phi.times(Ht.times(HHt_i))
      self.SaveMatrix('UB',self.UB)
      return self.UB

        
   def setUBnref(self,lista=None):
      if lista==None:
      	lista=self.rm.getReflectionKeys()
      H_phi =Matrix(3,len(lista))
      H = Matrix(3,len(lista))
      for i in range(len(lista)):
         refl=self.rm.getReflection(lista[i])
         Qm= 1./refl.wl
         qvpo=[0.,Qm,0.]
         qvp=Matrix([qvpo]).transpose()
         self.Z=sixC.setZ(refl.sixC.Mu,refl.sixC.Eta,refl.sixC.Chi,refl.sixC.Phi)
         self.DA=sixC.setDA(refl.sixC.Delta,refl.sixC.Gamma)
         qvp=(self.DA.minus(self.I)).times(qvp)
         uphi=self.Z.inverse().times(qvp)
         H_phi.setMatrix(0,2,i,i,uphi)
         H.setMatrix(0,2,i,i,Matrix([refl.hkl]).transpose())
      Ht=H.transpose()
      HHt_i=H.times(H.transpose()).inverse()
      self.UB=H_phi.times(Ht.times(HHt_i))
      self.SaveMatrix('UB',self.UB)
      return self.UB

        



   ## Not accessed Directly, takes one optional argument (Jama 3*3 matrix), and returns a
   #  6 elements list.
   #  Back calculate the lattice parameter from either an user
   #  provided UB matrix (Jama 3*3 matrix), or if called without arguments from the
   #  present UB matrix. Returns a vector that can be directly used to reset the Lattice
   def UB2Lat(self,x=None):
      """ Takes one optional argument (Jama 3*3 matrix), by default theUB matrix and returns 
a elements list [a,b,c, alpha,beta, gamma], that can be used to reset the lattice. """
      if x==None:
         x=self.UB
      Gmu=x.transpose().times(x).inverse()
      a=sqrt(Gmu.get(0,0))
      b=sqrt(Gmu.get(1,1))
      c=sqrt(Gmu.get(2,2))
      alpha = acos(Gmu.get(1,2)/sqrt(Gmu.get(1,1)*Gmu.get(2,2)))*180.0/pi
      beta = acos(Gmu.get(0,2)/sqrt(Gmu.get(0,0)*Gmu.get(2,2)))*180.0/pi
      gamma = acos(Gmu.get(0,1)/sqrt(Gmu.get(0,0)*Gmu.get(1,1)))*180.0/pi
      return [a,b,c,alpha,beta,gamma]

   ## Usually not accessed externally. Void function,
   #  takes two arguments a label (string) and a
   #  (3*3) Jama matrix, convert it to a list and
   #  save it to the shelve archive defined at top level under the provided key
   #
   def SaveMatrix(self,key,matrice):
      """ SaveMatrix(self,key,matrice): Usually not accessed externally. Void function, takes two arguments a label (string) and a 
(3*3) Jama matrix, convert it to a list and save it to the shelve archive defined at top level under the provided label
      """
      try:
         l=[[1,1,1],[1,1,1],[1,1,1]]
         for i in range(3):
            for j in range(3):
               l[i][j]=matrice.get(i,j)
         self.UBdata.ChangeValue(key,l)
      except:
         print "UBmatrix::SaveMatrix::Error"
      return

   ## This function takes no arguments and returns
   #  the UB matrix either from the archive or from a locally stored copy if
   #  available
   #
   def getUB(self):
      try:
         if self.UB == None:
            self.UB=Matrix(self.UBdata.getValue('UB'))
      except:
         print "UBmatrix::getUB::Error"
      return self.UB

   ## This function takes no arguments and returns
   #  the U matrix either from the archive or from a locally stored copy if
   #  available
   #
   def getU(self):
      try:
         if self.U == None:
            self.U=Matrix(self.UBdata.getValue('U'))
      except:
         print "UBmatrix::getU::Error"
      lista=[]
      for l in range(9):
         lista.append(self.U.getRowPackedCopy()[l])
      return lista

   ## Error Message generator
   #
   def __repr__(self):
      return '<UBMatrix bean error>'


