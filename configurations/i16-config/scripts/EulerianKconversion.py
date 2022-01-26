## @file EulerianKconversion.py  contains a module that
#  calculates the angles used in the transformation
#  between the Eulerian and the K geometry.
#  Usually is not accessed directly but through EulerianKconversionModes
#  @author Alessandro Bombardi
#  @version 1.0 (alpha release)
#  Please report bugs to Alessandro.Bombardi@diamond.ac.uk
#  Diamond Light Source Ltd.

import java
from math import *
import Angles
# Global Variables of the module; Please do not change
class EulerianKconversion(java.lang.Object):

   def __init__(self):
#      self.Kalpha=50.164*pi/180.0 # Value communicated from Newport of Kalpha 50.164
      self.Kalpha=50.*pi/180.0 # Value to have chi=90 
      self.angles1=Angles.Angles()
      self.angles2=Angles.Angles()

   ## This void function establish a link with the instantiation of the storedangles
   #  class passed as argument.
   def setSA(self,x):
      self.SA=x
      return

## Return the current value of the global variable
#  Kalpha, if not known more precisely, this value should be set at 50 degrees
#
#
   def getKalpha(self):
      return self.Kalpha

## Public function returns a list in the form
#  [[kth kap kphi],[kth kap kphi],[kth kap kphi],[kth kap kphi]]
#  of the four possible solution for the Eulerian - K conversion.
#
#
   def EuleriantoK(self,x=None):
      """@sig public double[[],[],[],[]] EuleriantoK([theta_now chi_now phi_now])"""
#      print "EuleriantoK"
      Kangles=self.angles1
      if x == None:
         d= self.SA.getAngles()
         theta_now=d.Eta
         chi_now=d.Chi
         phi_now=d.Phi
      else:
         theta_now = x[0]
         chi_now = x[1]
         phi_now = x[2]
      if abs(chi_now) <= self.Kalpha*180./pi*2:
         delta1=-asin(tan(pi/180.*chi_now/2.)/tan(self.Kalpha))
#         K1=asin(cos(delta1)*sin(pi/180*chi_now)/sin(Kalpha))*180/pi
         Kangles.K1=-asin(cos(delta1)*sin(pi/180*chi_now)/sin(self.Kalpha))*180/pi
         if abs(chi_now) > 65.595503 and chi_now > 0.:
            Kangles.K1=self.setRange(180-Kangles.K1)
         elif abs(chi_now) > 65.595503 and chi_now < 0.:
            Kangles.K1=self.setRange(-180-Kangles.K1)
         Kangles.theta_K1=self.setRange(theta_now-delta1*180/pi,-90.,270.)
         Kangles.phi_K1=self.setRange(phi_now-delta1*180/pi,-90.,270.)
         Kangles.theta_K2=self.setRange(theta_now-(pi-delta1)*180/pi,-90.,270.)
         Kangles.phi_K2=self.setRange(phi_now-(pi-delta1)*180/pi,-90.,270.)
         Kangles.K2=self.setRange(-Kangles.K1)
#      print "Thiese are the values after the range",Kangles.theta_K1,Kangles.phi_K1
      elif abs(chi_now) > self.Kalpha*180./pi*2:
         Kangles.K1='NA'
         Kangles.K2='NA'
         Kangles.phi_K1='NA'
         Kangles.phi_K2='NA'
         Kangles.theta_K1='NA'
         Kangles.theta_K2='NA'
      if abs(chi_now) >= (180.-self.Kalpha*180./pi*2):
   #      chi_r = -(180-chi_now)
         chi_r =  self.setRange(180-chi_now)
         delta3=-asin(tan(pi/180.*chi_r/2.)/tan(self.Kalpha))
   #      K3=asin(cos(delta3)*sin(pi/180*chi_r)/sin(Kalpha))*180/pi
         Kangles.K3=-asin(cos(delta3)*sin(pi/180*chi_r)/sin(self.Kalpha))*180/pi
         if abs(chi_r) > 65.595503 and chi_r > 0.:
            Kangles.K3=self.setRange(180-Kangles.K3)
         elif abs(chi_r) > 65.595503 and chi_r < 0.:
            Kangles.K3=self.setRange(-180-Kangles.K3)
         Kangles.theta_K3=self.setRange(theta_now-delta3*180/pi,-90.,270.)
         Kangles.phi_K3=self.setRange(phi_now-delta3*180/pi+180,-90.,270.)
         Kangles.theta_K4=self.setRange(theta_now-(pi-delta3)*180/pi,-90.,270.)
         Kangles.phi_K4=self.setRange(phi_now-(pi-delta3)*180./pi+180.,-90.,270.)
         Kangles.K4=self.setRange(-Kangles.K3)
      elif abs(chi_now) < (180.-self.Kalpha*180./pi*2):
         Kangles.K3='NA'
         Kangles.K4='NA'
         Kangles.phi_K3='NA'
         Kangles.phi_K4='NA'
         Kangles.theta_K3='NA'
         Kangles.theta_K4='NA'
#      Kvalues = [[theta_K1,K1,phi_K1],[theta_K2,K2,phi_K2],[theta_K3,K3,phi_K3],[theta_K4,K4,phi_K4]]
      return Kangles

   ## Public double [] KtoEulerian(x,y)
   #  perform the  K - Eulerian conversion.
   #
   def KtoEulerian(self,x,y):
      """@sig public double[] EuleriantoK(double [],integer)"""
      Euangles=self.angles2
      theta_K_now=x[0]
      K=x[1]
      phi_K_now=x[2]
      if y==1:
         gamma = -atan(cos(self.Kalpha)*tan(K/2.*pi/180.))*180./pi
   #      chi_now=asin(sin(K*pi/180)*sin(Kalpha)/cos(gamma*pi/180))*180/pi
         Euangles.Chi   = -2*asin(sin(K*pi/180/2)*sin(self.Kalpha))*180./pi
         Euangles.Theta =  theta_K_now-gamma
         Euangles.Phi   =  phi_K_now-gamma
      elif y==2:
         gamma = -atan(cos(self.Kalpha)*tan(K/2.*pi/180.))*180./pi+180.
   #      chi_now=asin(sin(K*pi/180)*sin(Kalpha)/cos(gamma*pi/180))*180/pi
         Euangles.Chi   = 2*asin(sin(K/2*pi/180)*sin(self.Kalpha))*180./pi
         Euangles.Theta = theta_K_now-gamma
         Euangles.Phi   = phi_K_now-gamma
      elif y==3:
         Euangles.gamma = -atan(cos(self.Kalpha)*tan(K/2.*pi/180.))*180./pi
   #      chi_now=asin(sin(K*pi/180)*sin(Kalpha)/cos(gamma*pi/180))*180/pi+180
         Euangles.Chi   = 2*asin(sin(K/2*pi/180)*sin(self.Kalpha))*180./pi+180.
         Euangles.Theta = theta_K_now-gamma
         Euangles.Phi   = phi_K_now-gamma+180.
      elif y==4:
         gamma = -atan(cos(self.Kalpha)*tan(K/2.*pi/180.))*180./pi
   #      chi_now=-asin(sin(K*pi/180)*sin(Kalpha)/cos(gamma*pi/180))*180/pi+180
         Euangles.Chi = -2*asin(sin(K/2*pi/180)*sin(self.Kalpha))*180./pi+180.
         Euangles.Theta =theta_K_now-gamma+180.
         Euangles.Phi=phi_K_now-gamma
      Euangles.Theta=self.setRange(Euangles.Theta,-90.,270.)
      Euangles.Chi=self.setRange(Euangles.Chi)
      Euangles.Phi=self.setRange(Euangles.Phi,-90.,270.)
      return Euangles

   ## double x setRange(double x,m=-180.,M=180.)
   #
   def setRange(self,x,m=-180.,M=180.):
      if x  <  m:
         x=x+360.
      elif x > M:
         x=x-360.
      return x

   ## Throws an error message
   #
   def __repr__():
      return '<EulerianKconversion error>'

