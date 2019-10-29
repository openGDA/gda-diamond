## @file Reflmanagement.py  contains a class that
#  allows to save and retrieve the measured reflections using labels.
#
#  @author Alessandro Bombardi
#  @version 1.0 (alpha release)
#  Please report bugs to Alessandro.Bombardi@diamond.ac.uk
#  Diamond Light Source Ltd.
import java
from Jama import Matrix
import os
import shelve
import UBmatrix
import Reflection as Reflections
import string
from string import *
from math import *
import ShelveIO
from string import *
import beamline_info as BLi
import installation
import gda.data.PathConstructor
## The class manages the reflection list, using shelveIO
#
class Reflmanagement(java.lang.Object):

   ## The constructor
   #
   def __init__(self):
   
      self.fname='toto.lis'
      self.ref=[]
      self.SIO=ShelveIO.ShelveIO()
      if installation.isDummy():
         f=open(os.path.join(gda.data.PathConstructor.createFromProperty('gda.var'), 'reffilename.log'),'r')
      else:
         f=open('/dls_sw/i16/var/reffilename.log','r')
      
      lista=f.readlines()
      f.close()

      self.SIO.path=ShelveIO.ShelvePath+'Reflections'
      self.SIO.setSettingsFileName(lista[-1][:-1])
      self.Reflections=Reflections.Reflections()
################## Link with other Classes #################


   ## This void function establish a link with the instantiation of the RecSpace
   #  class passed as argument.
   #
   def setRecSpaceMan(self,x):
      self.rs=x
      return

   ## This void function establish a link with the instantiation of the Azimuth
   #  class passed as argument.
   #
   def setAzMan(self,x):
      self.az=x
      return
      
      
   def Angles(self,x):
      self.SA=x
      return
      
##########################################################################

   def getReflectionsObj(self):
      return self.Reflections

   ##  set the current reflection File Name
   #
   def setReflectionsFileName(self,fname):
      if installation.isDummy():
         f=open(os.path.join(gda.data.PathConstructor.createFromProperty('gda.var'), 'reffilename.log'),'a')
      else:
         f=open('/dls_sw/i16/var/reffilename.log','a')
      
      stringa=fname+'\n'
      f.write(stringa)
      f.close()
      self.SIO.setSettingsFileName(fname)
      return






   ##  return the current reflection File Name
   #
   def getReflectionsFileName(self):
      return  self.SIO.SettingsFileName

   ##  Change the values associated with a label
   #
   def setReflection(self,key,data):
      self.SIO.ChangeValue(str(key),data)
      return

   ## Return a reflection by key
   #
   def getReflection(self,key):
      try:
         a=self.SIO.getValue(key)
      except:
         a='The key does not exist'
      return a

   ## Remove data from the dictionary
   #
   def removeReflection(self,key):
      self.SIO.delkey(key)
      return

   ## Append data to a dictionary assigning an increasing number
   #
   def appendReflection(self,data):
      if range(len(self.SIO.getAllKeys())) == []:
            self.SIO.setNewValue('1',data)
      else:
         x=[]
         for i in range(len(self.SIO.getAllKeys())):
            x.append(int(self.SIO.getAllKeys()[i]))
         a=str(max(x)+1)
         self.SIO.setNewValue(a,data)
      return
      
   ## Public return all the saved reflections
   #
   def getAllSavedReflections(self,filename=None):
      try:
         if filename != None:
            print "Warning: you are changing the reflection filename"
            print "use setReflectionsFileName(filename) to go back to the old one"
            print "The default filename is Reflections" 
            self.SIO.SettingsFileName = filename
         ans=[]
         i=0
         for i in range(len(self.SIO.getAllKeys())):
#            ans.append([self.SIO.getAllKeys()[i],self.getReflection(self.SIO.getAllKeys()[i])])
            ans.append(self.SIO.getAllKeys()[i])
      except:
         a='getAllSavedReflections::Maybe the file is empty'
      return ans
      
   ## Public return a list of all the reflection keys
   #
   def getReflectionKeys(self,filename=None):
#      self.setReflectionsFileName(filename)            
      try:
         if filename != None:
            print "Warning: you are changing the reflection filename"
            print "use setReflectionsFileName(filename) to go back to the old one" 
            print "The default filename is Reflections" 
            self.setReflectionsFileName(filename)            
         ans=self.SIO.getAllKeys()
      except:
         ans='getReflectionKeys::Maybe the file is empty'			
      return ans

   ## Public print for all the saved reflections labels, hkl and energy
   #
   def ReflList(self,string=None):
      if string == None:
         string=['hkl','Energy']
      for i in(range(len(self.getAllSavedReflections()))):
         print "Label=%s,[hkl]=%s, Energy=%s" %(i+1,self.getReflection(str(i+1))[string[0]],self.getReflection(str(i+1))[string[1]])
      return
      

   ## Public void
   #  AddReflection( string key=None,Jama Matrix hkl=None,[list] angles=None,double Energy=None)
   #  The function takes four optional arguments and build up an instance of a class.
   #  If the arguments are not provided the hkl are calculated from the current energy and angles
   def Addreflections(self,key=None,hkl=None,angles=None,Energy=None):
         "@sig public void addReflection(double[] hkl)"
         d=self.Reflections
         d.sample=Reflections.Reflections()
         d.surf = Reflections.Reflections()
         d.az = Reflections.Reflections()
#      try:
         if Energy ==None:
            Energy = BLi.getEnergy()
         d.Energy = Energy
         d.wl = 12.39842/d.Energy
         if angles==None:
            d.sixC=self.SA.getAngles()
         else:
            print "to implement"
         if hkl!=None:
            hkl = Matrix(hkl,3)
         elif hkl==None:
            hkl = self.rs.calcHKL(d.sixC.Mu,d.sixC.Eta,d.sixC.Chi,d.sixC.Phi,d.sixC.Delta,d.sixC.Gamma,None,d.wl)
         try:
            d.sample.psi=self.az.calcPsi()
         except:
            d.sample.psi=[666,666]
            print "WARNING: Could not calculate psi value (recording 666,666 and continuing)"
         d.hkl=[hkl.get(0,0),hkl.get(1,0),hkl.get(2,0)]
         try:
            d.sample.ttheta_mes = acos(cos(d.sixC.Delta*pi/180.)*cos(d.sixC.Gamma*pi/180.))*180./pi
            d.sample.theta_az = atan(tan(d.sixC.Delta*pi/180.)/sin(d.sixC.Gamma*pi/180.))*180./pi
         except:
            d.sample.ttheta_mes='Error::Not calculated'
            d.sample.theta_az='Error::Not calculated'
         try:
            d.az.N_L=self.az.calcN_L()
            d.surf.alpha = self.az.getAlpha()
            d.surf.phi_az= atan(d.az.N_L[0]/d.az.N_L[2])*180./pi
            d.az.psi =self.az.calcPsi()
            d.surf.beta  = self.az.getBeta()
         except:
            print "WARNING: Could not calculate either N_L, alpha, phi_az, psi or beta (!) (recording 666 for psi, beta and alpha and continuing)"
            d.az.psi=[666,666]
            d.surf.beta=666
            d.surf.alpha=666
            pass
         if key==None:
            self.appendReflection(d)
         else:
            self.lastd = d
            self.setReflection(key,d)
         return


   ## Public void
   #  AddReflection_b( string key=None,Jama Matrix hkl=None,[list] angles=None,double Energy=None)
   #  The function takes four optional arguments and build up an instance of a class.
   #  If the arguments are not provided the hkl are calculated from the current energy and angles
   def AddreflectionsVER(self,hkl=None,comments=None,angles=None,Energy=None):
         "@sig public void addReflection(double[] hkl)"
         print " I am using really this one!!!"
         d=self.Reflections

#         d.sample=self.Reflections
#         d.surf = self.Reflections
#         d.az = self.Reflections
#      try:
         if Energy ==None:
            Energy = BLi.getEnergy()
         d.Energy = Energy
         d.wl = 12.39842/d.Energy
         if angles==None:
            d.Chi=self.SA.getAngles().Chi
            d.Delta=self.SA.getAngles().Delta
            d.Eta=self.SA.getAngles().Eta
            d.Gam=self.SA.getAngles().Gam
            d.Gamma=self.SA.getAngles().Gamma
            d.Kap=self.SA.getAngles().Kap
            d.Kmu=self.SA.getAngles().Kmu
            d.Kphi=self.SA.getAngles().Kphi
            d.Kth=self.SA.getAngles().Kth
            d.Mu=self.SA.getAngles().Mu
            d.Phi=self.SA.getAngles().Phi
            d.Theta=self.SA.getAngles().Theta
         else:
            print "to implement"
         if hkl!=None:
            hkl = Matrix(hkl,3)
         elif hkl==None:
            hkl = self.rs.calcHKL(d.Mu,d.Eta,d.Chi,d.Phi,d.Delta,d.Gamma,None,d.wl)
#         try:
#            d.psi=self.az.calcPsi(-(sixC[0]/2-sixC[2][0]),sixC[2][1],sixC[2][2],hkl)
#         except:
#            d.psi=[666,666]
         d.hkl=[hkl.get(0,0),hkl.get(1,0),hkl.get(2,0)]
         try:
            d.ttheta_mes = acos(cos(d.Delta*pi/180.)*cos(d.Gamma*pi/180.))*180./pi
            d.theta_az = atan(tan(d.Delta*pi/180.)/sin(d.Gamma*pi/180.))*180./pi
         except:
            d.ttheta_mes='Error::Not calculated'
            d.theta_az='Error::Not calculated'
         try:
            d.N_L=self.az.calcN_L(None,d.hkl,None)
            d.alpha = self.az.getAlpha(None,d.hkl,None)
            d.phi_az= atan(d.N_L[0]/d.N_L[2])*180./pi
            d.psi =self.az.calcPsi(None,d.hkl,None)
            d.beta  = self.az.getBeta(None,d.hkl,None)
         except:
            pass
         if comments==None:
            d.comment='no labels'
            self.appendReflection(d)
         else:
            d.comment=comments
            self.appendReflection(d)
#            self.setReflection(key,d)
         return



   def showreflections(self,string=None,n=None):
       a=[['key',      'h    ','k    ','l    ', 'Energy','psi' ,'phi ' ,'chi ', 'eta ' ,'mu','delta' ,'gamma' ,'alpha','beta']]
       www=''
       ans=self.getReflectionKeys(string)
       mass=len('key')
       for i in range(len(ans)):
          if len(ans[i]) > mass:
             mass=len(ans[i])
       for j in range(1,len(a[0])):
          www=www+' '*3+'%9s'%(a[0][j])
       aaa = a[0][0]+' '*(mass-len('key'))+www
       print aaa
       for i in range(len(ans)):
            r=self.getReflection(ans[i])
#            xxx=[ans[i],r.hkl[0],r.hkl[1],r.hkl[2],r.Energy,r.psi[0],r.sixC.Phi,r.sixC.Chi,r.sixC.Eta,r.sixC.Mu,r.sixC.Delta,r.sixC.Gamma,r.surf.alpha,r.surf.beta]
            try:
                try:
                    psi_0 = r.sample.psi[0]
                except AttributeError:
                    psi_0 = -999
                xxx=[ans[i],r.hkl[0],r.hkl[1],r.hkl[2],r.Energy,psi_0,r.sixC.Phi,r.sixC.Chi,r.sixC.Eta,r.sixC.Mu,r.sixC.Delta,r.sixC.Gamma,r.surf.alpha,r.surf.beta]
            except:
                xxx=[]
                print "Warning::Reflection '",ans[i],"'can't be read"
                print "one of the value is missing"
                print "use getref('",ans[i],"') or showKref() if you need access to the other values"
                      
            www=ans[i]+' '*(mass-len(ans[i]))	
            for j in range(1,len(xxx)):
                if type(xxx[j]) ==type(0.) or type(xxx[j]) ==type(1):
                   xxx[j]='%+0009.4f' %(xxx[j])
                   xxx[j]=xxx[j].replace('+000','    ')
                   xxx[j]=xxx[j].replace('+00','   ')
                   xxx[j]=xxx[j].replace('+0','  ')
                   xxx[j]=xxx[j].replace('+',' ')
                   xxx[j]=xxx[j].replace('-000','   -')
                   xxx[j]=xxx[j].replace('-00','  -')
                   xxx[j]=xxx[j].replace('-0',' -')
                   xxx[j]=xxx[j].replace(' -.','-0.')
                   xxx[j]=xxx[j].replace(' .','0.')                   
                elif type(xxx[j]) == type('1'):
                   xxx[j]='%9s'%(xxx[j])
                www=www+' '*3+xxx[j]	
            a.append(www)            
            print a[i+1]
       return
   	
   def showreflectionsVER(self,string=None,n=None):
       a=[['key','comment',      'h    ','k    ','l    ', 'Energy','psi' ,'phi ' ,'chi ', 'eta ' ,'mu','delta' ,'gamma' ,'alpha','beta']]
       www=''
       ans=self.getReflectionKeys(string)
       mass=len('key')
       for i in range(len(ans)):
          if len(ans[i]) > mass:
             mass=len(ans[i])
       for j in range(1,len(a[0])):
          www=www+' '*3+'%9s'%(a[0][j])
       aaa = a[0][0]+' '*(mass-len('key'))+www
       print aaa
       for i in range(len(ans)):
            r=self.getReflection(ans[i])
#            xxx=[ans[i],r.hkl[0],r.hkl[1],r.hkl[2],r.Energy,r.psi[0],r.sixC.Phi,r.sixC.Chi,r.sixC.Eta,r.sixC.Mu,r.sixC.Delta,r.sixC.Gamma,r.surf.alpha,r.surf.beta]
            try:
                xxx=[ans[i],r.comment,r.hkl[0],r.hkl[1],r.hkl[2],r.Energy,r.psi[0],r.Phi,r.Chi,r.Eta,r.Mu,r.Delta,r.Gamma,r.alpha,r.beta]
            except:
                xxx=[]
                print "Warning::Reflection '",ans[i],"'can't be read"
                print "one of the value is missing"
                print "use getref('",ans[i],"') or showKref() if you need access to the other values"
                      
            www=ans[i]+' '*(mass-len(ans[i]))	
            for j in range(1,len(xxx)):
                if type(xxx[j]) ==type(0.) or type(xxx[j]) ==type(1):
                   xxx[j]='%+0009.4f' %(xxx[j])
                   xxx[j]=xxx[j].replace('+000','    ')
                   xxx[j]=xxx[j].replace('+00','   ')
                   xxx[j]=xxx[j].replace('+0','  ')
                   xxx[j]=xxx[j].replace('+',' ')
                   xxx[j]=xxx[j].replace('-000','   -')
                   xxx[j]=xxx[j].replace('-00','  -')
                   xxx[j]=xxx[j].replace('-0',' -')
                   xxx[j]=xxx[j].replace(' -.','-0.')
                   xxx[j]=xxx[j].replace(' .','0.')                   
                elif type(xxx[j]) == type('1'):
                   xxx[j]='%9s'%(xxx[j])
                www=www+' '*3+xxx[j]	
            a.append(www)            
            print a[i+1]
       return
   	
 			
                  
   def showKreflections(self,string=None,n=None):
       a=[['key',      'h    ','k    ','l    ', 'Energy','kphi ' ,'Kap ', 'Kth ' ,'delta' ,'gamma' ]]
       www=''
       ans=self.getReflectionKeys(string)
       mass=len('key')
       for i in range(len(ans)):
          if len(ans[i]) > mass:
             mass=len(ans[i])
       for j in range(1,len(a[0])):
          www=www+' '*3+'%9s'%(a[0][j])
       aaa = a[0][0]+' '*(mass-len('key'))+www
       print aaa
       for i in range(len(ans)):
            r=self.getReflection(ans[i])
            xxx=[ans[i],r.hkl[0],r.hkl[1],r.hkl[2],r.Energy,r.sixC.Kphi,r.sixC.Kap,r.sixC.Kth,r.sixC.Delta,r.sixC.Gamma]
            www=ans[i]+' '*(mass-len(ans[i]))	
            for j in range(1,len(xxx)):
                if type(xxx[j]) ==type(0.):
                   xxx[j]='%+0009.4f' %(xxx[j])
                   xxx[j]=xxx[j].replace('+000','    ')
                   xxx[j]=xxx[j].replace('+00','   ')
                   xxx[j]=xxx[j].replace('+0','  ')
                   xxx[j]=xxx[j].replace('+',' ')
                   xxx[j]=xxx[j].replace('-000','   -')
                   xxx[j]=xxx[j].replace('-00','  -')
                   xxx[j]=xxx[j].replace('-0',' -')
                   xxx[j]=xxx[j].replace(' -.','-0.')
                   xxx[j]=xxx[j].replace(' .','0.')                   
                elif type(xxx[j]) == type('1'):
                   xxx[j]='%9s'%(xxx[j])
                www=www+' '*3+xxx[j]	
            a.append(www)            
            print a[i+1]
       return

   def importFile(self):
      return self.SIO.importFile()
   	
 	

   ## Throws an error message
   #
   def __repr__(self):
      return '<Reflmanagement error>'



