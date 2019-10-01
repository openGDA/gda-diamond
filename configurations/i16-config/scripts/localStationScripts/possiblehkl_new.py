import Diffractometer as Gonio
import java
import Jama
from Jama import Matrix
from math import *
from Orthonormalize import orthonormalize as orto



def allowed(hval,kkval,lval,sg=1):
	"Contains the extinction rules for the specified space group, and return true is the rules are satisfied"
	return true




def guesswhoold(deltaval=None,refname='nome',error=0.1,change=0,allowedfunc=allowed):
    """The function guesswho(deltaval=None,refname='nome',error=0.1,change=0) returns a dictionary, 
    containing all the possible reflections compatible with the given 2theta (either the current delta value, or a saved value)
    If refname is the reflection name in the list of saved reflections and change is set to 1 (default =0), that reflections is saved to the reflection 
    list with the new hkl and temporrary name.
    Error indicates a given tolerance between the experimental 2th and the calculated one. """
    intero=1
    if deltaval ==None:
        deltaval=delta()
    dictio={}
    for hval in frange(-int(2*d_hkl([1,0,0])/wl()),int(2*d_hkl([1,0,0])/wl()),1):
        for kval in frange(-int(2*d_hkl([0,1,0])/wl()),int(2*d_hkl([0,1,0])/wl()),1):
            for lval in frange(-int(2*d_hkl([0,0,1])/wl()),int(2*d_hkl([0,0,1])/wl()),1):
                if allowedfunc(hval,kval,lval):
                    try:
                        xxx=c2th([hval,kval,lval])-deltaval
                        if abs(xxx)<error:
                            stringa='temp_'+refname+'_'+str(intero)
                            if change ==1:		
                                changehkl(refname,stringa,[hval,kval,lval])	
                            print "Possible", hval,' ',kval,' ',lval,'diff=',xxx
                            dictio[stringa]=[[hval,kval,lval],xxx]
                            intero=intero+1
                    except: 
                        pass
    return dictio







def guessmatrix(diz1,diz2,tol=0.3,maxangle=90.1,printoff=1):
	"""

	guessmatrix(diz1,diz2,tol=0.3,minangle=10,maxangle=90.1)
	"""
	possiblesolutions=[]
	for key1 in diz1.keys():
		delkey1='True'
		for key2 in diz2.keys():
			if  angle(diz1[key1][0],diz2[key2][0])>minangle and angle(diz1[key1][0],diz2[key2][0]) < maxangle:
				ubm(key1,key2)
				one=getref(key1)
				two=getref(key2)
				angletwo=hkl_calc.cal.getAngles(mode=2,hkl=diz2[key2][0],phi=two.sixC.Phi)
				if printoff == 0:
					print "Chi=",one.sixC.Chi,angletwo.Chi
					print "Eta=",one.sixC.Eta,angletwo.Eta
					print "Mu=",one.sixC.Mu, angletwo.Mu
		
				if abs(two.sixC.Chi-angletwo.Chi) < tol and abs(two.sixC.Eta-angletwo.Eta) <tol and abs(two.sixC.Mu-angletwo.Mu) <tol:
					print "possible solution =", diz1[key1], diz2[key2]
			 		delkey1='False'
					possiblesolutions.append([[key1,key2]])
				else:
					print diz1[key1][0],'and',diz2[key2][0],'is not possible'
			else:
				pass
#				print "Not possible, the angle between the two reflection is:"
#				print  angle(diz1[key1][0],diz2[key2][0]),' (',maxangle,')'
		if delkey1:
#			delref(key1)
			print "I got rid of ref:",key1
	return possiblesolutions
  



def guessmatrix2(diz1,diz2,tol=0.3,minangle=0,maxangle=90,printoff=1):
	"""

	guessmatrix(diz1,diz2,tol=0.3,minangle=10,maxangle=90.1)
	"""
	possiblesolutions=[]
	for key1 in diz1.keys():
		delkey1='True'
		for key2 in diz2.keys():
			try:
				if  angle(diz1[key1][0],diz2[key2][0])>minangle and angle(diz1[key1][0],diz2[key2][0]) < maxangle:
					possiblesolutions.append([[key1,key2]])
#				ubm(key1,key2)
#				one=getref(key1)
#				two=getref(key2)
#				angletwo=hkl_calc.cal.getAngles(mode=2,hkl=diz2[key2][0],phi=two.sixC.Phi)
#				if printoff == 0:
#					print "Chi=",one.sixC.Chi,angletwo.Chi
#					print "Eta=",one.sixC.Eta,angletwo.Eta
#					print "Mu=",one.sixC.Mu, angletwo.Mu
		
#				if abs(two.sixC.Chi-angletwo.Chi) < tol and abs(two.sixC.Eta-angletwo.Eta) <tol and abs(two.sixC.Mu-angletwo.Mu) <tol:
#					print "possible solution =", diz1[key1], diz2[key2]
#			 		delkey1='False'
#					possiblesolutions.append([[key1,key2]])
#				else:
#					print diz1[key1][0],'and',diz2[key2][0],'is not possible'
				else:
					pass
#				print "Not possible, the angle between the two reflection is:"
#				print  angle(diz1[key1][0],diz2[key2][0]),' (',maxangle,')'
#		if delkey1:
#			delref(key1)
#			print "I got rid of ref:",key1
			except:
				pass
	return possiblesolutions
  
def testub(diz1,diz2,key1,key2):
	lista=guessmatrix2(diz1,diz2)

	for chiavi in lista:
		t1=chiavi[0][0]
		t2=chiavi[0][1]
		#print chiavi
		changehkl(key1,'newkey1',diz1[t1][0])
		changehkl(key2,'newkey2',diz2[t2][0])
		ubm('newkey1','newkey2')
		if abs(diz2[t2][0][0]-h())<0.2 and abs(diz2[t2][0][1]-k())<0.2 and abs(diz2[t2][0][2]-l())<0.2:
			print '********\n\n'
			print diz1[t1][0], diz2[t2][0], 'hkl=',hkl()
	print "I am done"



 
def tryUBs(diz1,diz2,euler1,euler2,energy=en(),tolerance=0.05):
	"""possible_matrices=tryUBs(diz1,diz2,euler1,euler2,energy,tolerance=0.05). This function is used to check in the provided dictionary couple of reflections compatible with the 
	provided lattice parameter within a given tolerance. Position the diffractometer on the reflection related to the 
	second dictionary and pass to the function the dictionaries related to the first and second reflections you want to index. Energy is assumed to be the current one 
	tolerance by default is 0.05 in every direction"""
	###################################################################################################
	# ORTOGONAL SYSTEM IN THE CRYSTAL CARTESIAN BASIS
	# (X is // to the principal reflection, Y in the plane of the principal and secondary reflection,
	# Z is prependicular to this plane
	####################################################################################################
	possible_matrices={}
	wl=12.39842/energy
	#pass mu eta chi phi,delta,gam
	GonioZ=Gonio.setZ(euler1[0],euler1[1],euler1[2],euler1[3]) #verify the order of the angles
	GonioDA=Gonio.setDA(euler1[4],euler1[5])
	Qm= 2.*pi/wl
	qvpo=[0.,Qm,0.]
	qvp=Matrix([qvpo]).transpose()
	qvp=(GonioDA.minus(ub.I)).times(qvp)
	qvp=qvp.times(1/qvp.normF()).times(Qm)
	uphi_p=GonioZ.inverse().times(qvp)
	Qs =2.*pi/wl
	qvs=[0.,Qs,0.]
	qvs=Matrix([qvs]).transpose()
	GonioZ=Gonio.setZ(euler2[0],euler2[1],euler2[2],euler2[3])
	GonioDA=Gonio.setDA(euler2[4],euler2[5])
	qvs=GonioDA.minus(ub.I).times(qvs)
	uphi_s=GonioZ.inverse().times(qvs)
	############################################################
	# ORTOGONAL SYSTEM IN THE PHI AXIS SYSTEM (diffractometer)
	# (X is // to the principal reflection, Y in the plane of the principal and secondary reflection,
	# Z is prependicular to this plane
	############################################################
	T_phi=orto([uphi_p.get(0,0),uphi_p.get(1,0),uphi_p.get(2,0)],[uphi_s.get(0,0),uphi_s.get(1,0),uphi_s.get(2,0)])
	index=0
	for hkl1 in diz1.keys():
		MH_pc = ub.xtal.MB.times(Matrix(diz1[hkl1][0],3))

	   # Qm=2*sin(self.tt.calctth(hkl1,Energy)/2.*(pi/180.0))/wl
	
		for hkl2 in diz2.keys():
			MH_sc = ub.xtal.MB.times(Matrix(diz2[hkl2][0],3))
			try:
				T_c=orto([MH_pc.get(0,0),MH_pc.get(1,0),MH_pc.get(2,0)],[MH_sc.get(0,0),MH_sc.get(1,0),MH_sc.get(2,0)])
			except:
				print "Exception",diz1[hkl1][0],diz2[hkl2][0]
				pass
				
			UM=T_phi.times(T_c.inverse())
			UM=UM.times(ub.xtal.MB)
			hklm=rs.calcHKL(mu=euler2[0],eta=euler2[1],chi=euler2[2],phi=euler2[3],delta=euler2[4],gamma=euler2[5],UB=UM,wl=wl)
			if abs(hklm.get(0,0)-diz2[hkl2][0][0]) <=tolerance and abs(hklm.get(1,0)-diz2[hkl2][0][1])<=tolerance and  abs(hklm.get(2,0)-diz2[hkl2][0][2]) <=tolerance:
				agreement=abs(hklm.get(0,0)-diz2[hkl2][0][0])+abs(hklm.get(1,0)-diz2[hkl2][0][1])+abs(hklm.get(2,0)-diz2[hkl2][0][2])
				possible_matrices[index]=[diz1[hkl1][0],diz2[hkl2][0],agreement]
				index+=1 
				print "Testing",diz1[hkl1][0],diz2[hkl2][0],[hklm.get(0,0),hklm.get(1,0),hklm.get(2,0)]
	return possible_matrices    






	
def allallowed(hval,kval,lval):
	return True
	
	

def guesswho(deltaval,alwd_refl_func=allallowed,error=.5,enval=en(),change=0,refname=''):
	"""The function dictio=guesswho(deltaval=None,alwd_refl_func=allallowed,refname='nome',error=0.1,change=0) 
	returns a dictionary, containing all the possible reflections compatible within the given error by default 0.1  
	degrees with the given 2theta value (by default the current delta value)
	If refname is the reflection name in the list of saved reflections and change is set to 1 (default =0), that reflections is saved to the reflection 
	list with the new hkl and temporrary name.
	Error indicates a given tolerance between the experimental 2th and the calculated one, and it is returned as second item in the list containing the reflections 
	It is possible to pass a function providing the extinction rules for a given crystal to restrict the possible reflections.    
	"""
	intero=1
	dictio={}
	for hval in frange(-int(2*d_hkl([1,0,0])/wl()),int(2*d_hkl([1,0,0])/wl()),1):
		for kval in frange(-int(2*d_hkl([0,1,0])/wl()),int(2*d_hkl([0,1,0])/wl()),1):
			for lval in frange(-int(2*d_hkl([0,0,1])/wl()),int(2*d_hkl([0,0,1])/wl()),1):
				if alwd_refl_func(hval,kval,lval):
#					print "I am here"
					try:
						xxx=c2th([hval,kval,lval],enval)-deltaval
#						print "errore",xxx
						if abs(xxx)<error:
							stringa='temp_'+refname+'_'+str(intero)
							if change ==1:		
								changehkl(refname,stringa,[hval,kval,lval])	
#							print "Possible", hval,' ',kval,' ',lval,'diff=',xxx
							dictio[stringa]=[[hval,kval,lval],xxx]
							intero=intero+1
					except: 
						pass
	return dictio



	
	
		
def automatrix(key1=1,refkey=2,alwd_refl_func=allallowed):
	"""Warning use tth instead of Delta or Gam """
	saveref(refkey)
	r1=getref(key1)
	r2=getref(refkey)
	r1.euler=[r1.sixC.Mu,r1.sixC.Eta,r1.sixC.Chi,r1.sixC.Phi,r1.sixC.Delta,r1.sixC.Gam]
	r2.euler=[r2.sixC.Mu,r2.sixC.Eta,r2.sixC.Chi,r2.sixC.Phi,r2.sixC.Delta,r2.sixC.Gam]
	diz1=guesswho(r1.sixC.Delta,alwd_refl_func=allallowed)
	diz2=guesswho(r2.sixC.Delta,alwd_refl_func=allallowed)
	possiblehkl=theoreticalcouples(r1.hkl,r2.hkl,diz1,diz2)
	possible_matrices=newautoub(possiblehkl,r1.euler,r2.euler)
	key=min(possible_matrices, key=possible_matrices.get())
	changehkl(refkey,101,possible_matrices[key][2])
	changehkl(key1,100,possible_matrices[key][1])
	ubm(100,101)
	print "\n The best matrix is obtained with" + str(possible_matrices[key][1]) + "and" +str(possible_matrices[key][2])
	print "Error="+str(possible_matrices[key][0]) 


def anglesfromwrong(hkl1,hkl2=hkl()):
	"""Uses the real hkl val of the secondary reflecion to guess the angle between the primary and te secondary relfection"""
	angval=angle(hkl1,hkl())
	return angval
		
		 
def theoreticalcouples(hkl1,hkl2,diz1,diz2,tol1=0.2):
	angval=anglesfromwrong(hkl1,hkl2)
	possiblekeys=[] 
	for key1 in diz1.keys():
		for key2 in diz2.keys():
			if abs(angle(diz1[key1][0],diz2[key2][0])-angval) < tol1:
				possiblekeys.append([diz1[key1][0],diz2[key2][0]])
	return possiblekeys
			
		 

 
def newautoub(possiblekeys,euler1,euler2,energy=en(),tolerance=0.1):
	"""possible_matrices=tryUBs(diz1,diz2,euler1,euler2,energy,tolerance=0.05). This function is used to check in the provided dictionary couple of reflections compatible with the 
	provided lattice parameter within a given tolerance. Position the diffractometer on the reflection related to the 
	second dictionary and pass to the function the dictionaries related to the first and second reflections you want to index. Energy is assumed to be the current one 
	tolerance by default is 0.05 in every direction"""
	###################################################################################################
	# ORTOGONAL SYSTEM IN THE CRYSTAL CARTESIAN BASIS
	# (X is // to the principal reflection, Y in the plane of the principal and secondary reflection,
	# Z is prependicular to this plane
	####################################################################################################
	possible_matrices={}
	wl=12.39842/energy
	#pass mu eta chi phi,delta,gam
	GonioZ=Gonio.setZ(euler1[0],euler1[1],euler1[2],euler1[3]) #verify the order of the angles
	GonioDA=Gonio.setDA(euler1[4],euler1[5])
	Qm= 2.*pi/wl
	qvpo=[0.,Qm,0.]
	qvp=Matrix([qvpo]).transpose()
	qvp=(GonioDA.minus(ub.I)).times(qvp)
	qvp=qvp.times(1/qvp.normF()).times(Qm)
	uphi_p=GonioZ.inverse().times(qvp)
	Qs =2.*pi/wl
	qvs=[0.,Qs,0.]
	qvs=Matrix([qvs]).transpose()
	GonioZ=Gonio.setZ(euler2[0],euler2[1],euler2[2],euler2[3])
	GonioDA=Gonio.setDA(euler2[4],euler2[5])
	qvs=GonioDA.minus(ub.I).times(qvs)
	uphi_s=GonioZ.inverse().times(qvs)
	############################################################
	# ORTOGONAL SYSTEM IN THE PHI AXIS SYSTEM (diffractometer)
	# (X is // to the principal reflection, Y in the plane of the principal and secondary reflection,
	# Z is prependicular to this plane
	############################################################
	T_phi=orto([uphi_p.get(0,0),uphi_p.get(1,0),uphi_p.get(2,0)],[uphi_s.get(0,0),uphi_s.get(1,0),uphi_s.get(2,0)])
	index=0
	for hkl1t,hkl2t in possiblekeys:
		MH_pc = ub.xtal.MB.times(Matrix(hkl1t,3))
		MH_sc = ub.xtal.MB.times(Matrix(hkl2t,3))
		try:
			T_c=orto([MH_pc.get(0,0),MH_pc.get(1,0),MH_pc.get(2,0)],[MH_sc.get(0,0),MH_sc.get(1,0),MH_sc.get(2,0)])
		except:
			print "Exception",hkl1t,hkl2t
			pass
				
		UM=T_phi.times(T_c.inverse())
		UM=UM.times(ub.xtal.MB)
		hklm=rs.calcHKL(mu=euler2[0],eta=euler2[1],chi=euler2[2],phi=euler2[3],delta=euler2[4],gamma=euler2[5],UB=UM,wl=wl)
		if abs(hklm.get(0,0)-hkl2t[0]) <=tolerance and abs(hklm.get(1,0)-hkl2t[1])<=tolerance and  abs(hklm.get(2,0)-hkl2t[2]) <=tolerance:
				agreement=abs(hklm.get(0,0)-hkl2t[0])+abs(hklm.get(1,0)-hkl2t[1])+abs(hklm.get(2,0)-hkl2t[2])
				possible_matrices[index]=[agreement,hkl1t,hkl2t]
				index+=1 
				print "Testing",hkl1t,hkl2t,[hklm.get(0,0),hklm.get(1,0),hklm.get(2,0)]
	return possible_matrices


