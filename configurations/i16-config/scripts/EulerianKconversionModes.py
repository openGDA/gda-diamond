## @file EulerianKconversionModes.py  contains a module that
#  allows to set and get the modes and the angles used in the transformation
#  between the Eulerian and the K geometry.
#  @author Alessandro Bombardi
#  @version 1.0 (alpha release)
#  Please report bugs to Alessandro.Bombardi@diamond.ac.uk
#  Diamond Light Source Ltd.

#import EuSampleAngles as ESA
#import Ksampleangles as Ka

import java
import shelve
import ShelveIO
import EulerianKconversion
import Angles
from math import *
#print "I am importing it"

class EulerianKconversionModes(java.lang.Object):

   def __init__(self):
#      print "I am importing it"

      self.EKc  = EulerianKconversion.EulerianKconversion()
      self.EKsm =ShelveIO.ShelveIO()
      self.EKsm.path = ShelveIO.ShelvePath+'EulerianKmodeSetting'
      self.EKsm.setSettingsFileName('EulerianKmodeSetting')
      self.out=None
      self.angles=Angles.Angles()
      pass


   ## This void function establish a link with the instantiation of the storedangles
   #  class passed as argument.
   def setEAngles(self,x):
      self.EA=x
      return

   ## This void function establish a link with the instantiation of the storedangles
   #  class passed as argument.
   def setKAngles(self,x):
      self.KA=x
      return

## Set the mode to be used in the E2K conversion
#  The allowed argument values can be print using the function
#  printEuleriantoKmodes()
#  This function is a void, it stores the new
#  value to a file and it changes the global variable out.
   def setEuleriantoKmode(self,x):
      global out
      self.EKsm.ChangeValue('EuleriantoKmode',x)
      out=x
      return

## Get the mode to be used in the E2K conversion
#  This function either return the locally stored mode or, if there is
#  not a stored value locally it access the value from a file.
   def getEuleriantoKmode(self):
      global out
      if out == None:
         out = self.EKsm.getValue('EuleriantoKmode')
      return out

## No arguments, it prints the allowed modes to be used in the E2K conversion
#
   def printEuleriantoKmodes(self):
      print "1: mu=0  ; phik_in = 0  ;(delta,k)"
      print "2: mu=0  ; phik_in = 0  ;(Pi-delta,-k)"
      print "3: mu=180, phik_in = 180;(delta,k)"
      print "4: mu=180, phik_in = 180;(Pi-delta,-k)"
      return

## Two optional arguments:
#  The first argument needs to be a list of three numbers [Kth, Kap, Kphi]
#  The second argument is the mode to be used in the conversion
#  The behavior without argument is to access the stored values of the K angles
#  The function returns the three Eulerian angles
   def getEulerianAngles(self,x=None,y=None):
      if y==None:
         y=self.getEuleriantoKmode()
      if x==None:
         x=self.KA.getAngles()
         x=[x.KTheta,x.K,x.KPhi]
      Euangles=self.EKc.KtoEulerian(x,y)
      return Euangles

## Two optional arguments:
#  The first argument needs to be a list of three numbers [th, chi, phi]
#  The second argument is the mode to be used in the conversion
#  The behavior without argument is to access the stored values of the Eulerian angles
#  The function returns either the three K angles for a give mode or all the possible angles
   def getKPossibleAngles(self,x=None,y=None):
#      print "I am calling it"
      if y==None:
         y=self.getEuleriantoKmode()
      Kangles=self.EKc.EuleriantoK(x)
      Kang=self.angles
      if y == 1:
         try:
            Kangles.K1/1.
            Kang.Vector=[Kangles.theta_K1,Kangles.K1,Kangles.phi_K1 ]
            Kang.KTheta=Kangles.theta_K1
            Kang.K=Kangles.K1
            Kang.KPhi=Kangles.phi_K1
         except:
            print "1 not possible"
            Kang.Vector=[]
      elif y == 2:
         try:
            Kangles.K2/1.
            Kang.Vector=[Kangles.theta_K2,Kangles.K2,Kangles.phi_K2 ]
            Kang.KTheta=Kangles.theta_K2
            Kang.K=Kangles.K2
            Kang.KPhi=Kangles.phi_K2
         except:
            print "2 not possible"
            Kang.Vector=[]
      elif y == 3:
         try:
            Kangles.K3/1.
            Kang.Vector=[Kangles.theta_K3,Kangles.K3,Kangles.phi_K3 ]
            Kang.KTheta=Kangles.theta_K3
            Kang.K=Kangles.K3
            Kang.KPhi=Kangles.phi_K3
         except:
            print "3 not possible"
            Kang.Vector=[]
      elif y == 4:
         try:
            Kangles.K4/1.
            Kang.Vector=[Kangles.theta_K4,Kangles.K4,Kangles.phi_K4 ]
            Kang.KTheta=Kangles.theta_K4
            Kang.K=Kangles.K4
            Kang.KPhi=Kangles.phi_K4
         except:
            print "4 not possible"
            Kang.Vector=[]
      elif y == 'All':
         Kang=Kangles
      return Kang

   def __repr__():
      return '<EulerianKconversionModes error>'

