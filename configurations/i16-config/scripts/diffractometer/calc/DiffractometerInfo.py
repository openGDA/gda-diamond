import ShelveIO
from math import pi

###########  Please do not modify ###################
DifInfo=ShelveIO.ShelveIO()  ##
DifInfo.path=ShelveIO.ShelvePath+'DifInfo'
DifInfo.setSettingsFileName('DifInfo') ##
#DifInfo.rebuildPath() #(rdw) hack to fix logic problem in IO shelve
mode = None
mode_old = None
geo = None
###################################################

def setGeometry(x='v'):
   "@sig public void setGeometry(string geo)"
   global geo
   geo=x
   DifInfo.ChangeValue('Geometry',geo)
   return

   
def getGeometry():
   "@sig public void setGeometry(string geo)"
   global geo
   if geo == None:
      geo = DifInfo.getValue('Geometry')
   return geo

def setMode(x):
   "@sig public void setMode(int[] mode)"
   global mode
   global mode_old
   try:
      mode_old=getMode()
      DifInfo.ChangeValue('mode_old',mode_old)
   except:
       pass
   mode=x
   DifInfo.ChangeValue('mode',mode)
   return

def getModeOld():
   "@sig public int getMode()"
   global mode_old
   if mode_old == None:
      mode_old = DifInfo.getValue('mode_old')
   return mode_old

def getMode():
   "@sig public int getMode()"
   global mode
   if mode == None:
      mode=DifInfo.getValue('mode')
   return mode

def printMode():
   "@sig public int printMode()"
   a="1=bisecting \\n2=fixed phi\\n3= fixed psi\\n"
   return a

def setSector(sector):
   DifInfo.ChangeValue('sector',sector)
   return

def getSector():
   return DifInfo.getValue('sector')

def setCuts(self,tth,th,chi,phi,psi):
   self.tth_cut = tth
   self.th_cut = th
   self.chi_cut = chi
   self.phi_cut = phi
   self.psi_cut = psi
   self.setCutsRanges(self.tth_cut,self.th_cut,self.chi_cut,self.phi_cut,self.psi_cut)
   return

def getCuts(self):
   print  "The current cuts are:\n tth=%s, th=%s, chi = %s, phi= %s" % (self.tth_cut,self.th_cut,self.chi_cut,self.phi_cut)
   return

def setCutsRanges(self,tth,th,chi,phi,psi):
   self.tth_min = tth
   self.tth_Max = tth+360.0
   self.th_min = th
   self.th_Max = th+360.0
   self.chi_min = chi
   self.chi_Max = chi+360.0
   self.phi_min = phi
   self.phi_Max = phi+360.0
   if psi >=0:
      self.psi_min = 0.0
      self.psi_Max = 180.0
   else:
      self.psi_min = -180.0
      self.psi_Max =  0.0
   return

def getCutsRanges(self):
   print "The ranges of the motors are:\n tth=(%s,%s) ,th=(%s,%s), chi=(%s,%s), phi=(%s,%s), psi=(%s,%s)" % (self.tth_min,self.tth_Max,self.th_min,self.th_Max,self.chi_min,self.chi_Max,self.phi_min,self.phi_Max,self.psi_min,self.psi_Max)
   return


def setTheta(theta):
   "@sig public void setTheta( double theta)"
   theta=setRange(theta,getThetaCut())
   DifInfo.ChangeValue('theta',theta)
   return

def getTheta():
   return  DifInfo.getValue('theta')

def setThetaCut(cut):
   "@sig public void setThetaCut( double cut)"
   DifInfo.ChangeValue('thetacut',cut)
   return

def getThetaCut():
   "@sig public double getThetaCut( )"
   return  DifInfo.getValue('thetacut')


def setChi(chi):
   "@sig public void setChi( double Chi)"
   chi=setRange(chi,getChiCut())
   DifInfo.ChangeValue('Chi',chi)
   return

def getChi():
   return  DifInfo.getValue('Chi')


def setChiCut(cut):
   "@sig public void setThetaCut( double cut)"
   DifInfo.ChangeValue('Chicut',cut)
   return

def getChiCut():
   "@sig public double getThetaCut( )"
   return  DifInfo.getValue('Chicut')


def setPhi(phi):
   "@sig public void setPhi( double 'Phi')"
   phi=setRange(phi,getPhiCut())
   DifInfo.ChangeValue('Phi',phi)
   return

def getPhi():
   return  DifInfo.getValue('Phi')

def setPhiCut(cut):
   "@sig public void setPhiCut( double cut)"
   DifInfo.ChangeValue('Phicut',cut)
   return

def getPhiCut():
   "@sig public double getPhiCut( )"
   return  DifInfo.getValue('Phicut')



def getAngles():
   "@sig public [double] getAngles()"
   return [getTwoTheta(),getTheta(),getChi(),getPhi()]


def SectorConversion4C(ttheta_g,omega_g,chi_g,phi_g,sector=None):
   if sector == None:
      sector=getSector()
   if sector == 0:
      ttheta_g = ttheta_g
      omega_g =omega_g
      chi_g = chi_g
      phi_g = phi_g
   elif sector == 1:
      ttheta_g = ttheta_g
      omega_g =omega_g-pi
      chi_g = -chi_g
      phi_g = phi_g-pi
   elif sector == 2:
      ttheta_g = -ttheta_g
      omega_g =-omega_g
      chi_g = chi_g-pi
      phi_g = phi_g
   elif sector == 3:
      ttheta_g = -ttheta_g
      omega_g =pi-omega_g
      chi_g = pi-chi_g
      phi_g = phi_g-pi
   elif sector == 4:
      ttheta_g = ttheta_g
      omega_g =-omega_g
      chi_g = pi-chi_g
      phi_g = phi_g-pi
   elif sector == 5:
      ttheta_g = ttheta_g
      omega_g =pi-omega_g
      chi_g = chi_g-pi
      phi_g = phi_g
   elif sector == 6:
      ttheta_g = -ttheta_g
      omega_g =omega_g
      chi_g = -chi_g
      phi_g = phi_g-pi
   elif sector == 7:
      ttheta_g = -ttheta_g
      omega_g =omega_g-pi
      chi_g = chi_g
      phi_g = phi_g
   return [ttheta_g,omega_g,chi_g,phi_g]

def setRange(x,cut):
   if x < cut:
      x=x+360.
   elif x > cut+360.:
      x=x-360.
   return x


