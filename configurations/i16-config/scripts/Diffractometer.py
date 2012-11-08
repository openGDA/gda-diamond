import Rotations as Rot
import java
import Jama
from Jama import Matrix
from math import *
##############################################
flag = "You"
#flag= "Me"


def setZ(mu,eta,chi,phi):
   "@sig public void setZ(double phi,double chi,double omega )"
   PHI=R_phi(phi)
   CHI=R_chi(chi)
   ETA=R_eta(eta)
   MU=R_mu(mu)
   Z = MU.times(ETA.times(CHI.times(PHI)))
   return Z
   
   
   
def setZK(mu,eta,k,alpha,phi):
   "@sig public void setZ(double phi,double chi,double omega )"
   PHI=R_phi(phi)
   ETA=R_eta(eta)
   KAP=R_kappa(k,alpha)
   MU=R_mu(mu)
   Z = MU.times(ETA.times(KAP.times(PHI)))
   return Z


def setDA(delta,gamma):
   DELTA = R_delta(delta)
   GAMMA = R_gamma(gamma)
   da = GAMMA.times(DELTA) #.times(k_i))
   return da


##  Rotations ##
def R_phi(phi):
   "@sig public double R_phi(double phi)"
   phi=phi*pi/180.0
   if flag == "Me":
      PHI=Matrix(Rot.R_z_r(phi))
   elif flag == "You":
      PHI=Matrix(Rot.R_z_l(phi))
   return PHI

def R_chi(chi):
   "@sig public double R_chi(double chi)"
   chi=chi*pi/180.0
   if flag == "Me":
      CHI = Matrix(Rot.R_y_l(chi))
   elif flag == "You":
#You conventions
      CHI = Matrix(Rot.R_y_r(chi))
   return CHI

def R_eta(eta):
   "@sig public double R_omega(double eta)"
   eta=eta*pi/180.0
   if flag == "Me":
      ETA = Matrix(Rot.R_z_r(eta))
   elif flag == "You":
#You conventions
      ETA = Matrix(Rot.R_z_l(eta))
   return ETA

def R_mu(mu):
   "@sig public double R_MU(double mu)"
   mu=mu*pi/180.0
   if flag == "Me":
      MU=Matrix(Rot.R_x_r(mu))
   elif flag == "You":
      MU=Matrix(Rot.R_x_r(mu))
   return MU

def R_delta(delta):
   "@sig public double R_delta(double delta)"
   delta=delta*pi/180.0
   if flag == "Me":
      DELTA=Matrix(Rot.R_z_r(delta))
#You conventions
   elif flag == "You":
      DELTA=Matrix(Rot.R_z_l(delta))
   return DELTA

def R_gamma(gamma):
   "@sig public double R_gamma(double gamma)"
   gamma=gamma*pi/180.0
   if flag == "Me":
#      print "My diffractometer"
      GAMMA=Matrix(Rot.R_x_r(gamma))
# You convention below
   elif flag == "You":
      GAMMA=Matrix(Rot.R_x_r(gamma))
   return GAMMA

def R_kappa(kappa,alpha):
   kappa=kappa*pi/180.0
   alpha=alpha*pi/180.0
   ALP=Matrix(Rot.R_x_r(pi/2-alpha))
   KAP=ALP.times(Matrix(Rot.R_y_l(kappa)).times(ALP.inverse()))
   return KAP
   




