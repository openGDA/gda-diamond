from java import lang
from gda.analysis.numerical.optimization.objectivefunction import AbstractObjectiveFunction
from gda.analysis.numerical.linefunction import Parameter
from gda.analysis.numerical.optimization.objectivefunction import chisquared
from gda.analysis.numerical.optimization.optimizers.leastsquares import minpackOptimizer
#from gda.analysis.numerical.optimization.optimizers.filtering import iffco
from gda.analysis.numerical.optimization.optimizers.differentialevolution import DEOptimizer
from gda.analysis.numerical.optimization.optimizers.simplex import NelderMeadOptimizer
from java.lang import *
from org.python.modules.jarray import *
from org.python.modules.math import *
from Jama import Matrix
import time_module


#
#This function takes as parameters the 9 elements of the ubmatrix
#and the offsets of the diffractometers angles.
#It calculates the hkl values,and try to minimize the squared  difference with
#the observed positions.
#
#
class LSR_HKL_K(AbstractObjectiveFunction):
	def __init__(self,guess,lower,upper,reflections,recspace,listaref):
		params = []
		self.tm=time_module.time_module()
		self.nn=0
		for i in range(len(guess)):
			params.append(Parameter(guess[i],lower[i],upper[i]))
		self.paramArray=array(params,Parameter)
		self.rs=recspace
		self.rm=reflections
		if listaref==None:
			self.nobs=self.rm.getReflectionKeys()
		else: 
			self.nobs=listaref
		self.obs =[]
		for i in self.nobs:
			self.obs.append(self.rm.getReflection(i))

#   def evaluate(UBini,Mu_off=None,Eta_off=None,Chi_off=None,Phi_off=None,Delta_off=None,Gamma_off=None):
	def evaluate(self,UBini):
#		self.tm.reset()	
		UB=Matrix([[UBini[0],UBini[1],UBini[2]],[UBini[3],UBini[4],UBini[5]],[UBini[6],UBini[7],UBini[8]]])
		Deltac=0
		obs=[0]*len(self.nobs)
		for i in range(len(self.nobs)):
			obs[i]=self.obs[i]
			Mu_l=obs[i].sixC.Mu
#			if Mu_off != None:
#				Mu=Mu-Mu_off
			Kth_l=obs[i].sixC.Kth
			if len(UBini) >= 10:
				Kth_l=Kth_l-UBini[9]
			Kap_l=obs[i].sixC.Kap
			if len(UBini) >= 11:
				Kap_l=Kap_l-UBini[10]
			KPhi_l=obs[i].sixC.Kphi
#         if Phi_off != None:
#            Phi=Phi-Phi_off
			Delta_l=obs[i].sixC.Delta
			if len(UBini) >= 12:
				Delta_l=Delta_l-UBini[11]
			Gamma_l=obs[i].sixC.Gamma
#         if Gamma_off != None:
#            Gamma=Gamma-Gamma_off
			hkl_c=self.rs.calcHKL_K(Mu_l,Kth_l,Kap_l,KPhi_l,Delta_l,Gamma_l,UB,obs[i].wl)
			d_h=(obs[i].hkl[0]-hkl_c.get(0,0))**2
			d_k=(obs[i].hkl[1]-hkl_c.get(1,0))**2
			d_l=(obs[i].hkl[2]-hkl_c.get(2,0))**2
			Deltac+=d_h+d_k+d_l
		self.nn+=1

		if int(self.nn/10.) >= self.nn/10. or self.nn ==1:
			print self.nn, Deltac,self.tm
			self.tm.reset()	
		return Deltac

	def getParameters(self):
		return self.paramArray


