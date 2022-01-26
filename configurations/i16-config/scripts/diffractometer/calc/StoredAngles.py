import java
import ShelveIO
import Angles
import EulerianKconversionModes

################################################
# to merge with GDA systems
import beamline_objects as BLobjects
################################################

class  StoredAngles(java.lang.Object):

   def __init__(self,x='SA'):
      self.x = x
      self.SA=ShelveIO.ShelveIO()
      self.SA.path=ShelveIO.ShelvePath+x
      self.SA.setSettingsFileName(x)
      self.ang=Angles.Angles()
      self.ekcm = EulerianKconversionModes.EulerianKconversionModes()


   def ChangeAngle(self,key,angle):
      if BLobjects.isSimulation():
         try:
            d=self.SA.getValue('Angles')
         except:
            d=self.ang
         exec('d'+'.'+ key +'='+'angle')
         self.SA.ChangeValue('Angles',d)
      else:
         #(rdw) changed  August 15th so limit exceptions could be caught and used to trigger a stop all
         #print "moving ",key
         #command_string = 'BLobjects.get'+key+'().asynchronousMoveTo('+`angle`+')'
         #print command_string
         #exec(command_string)
         if key=='Kphi':
            BLobjects.getKphi().asynchronousMoveTo(angle)
         elif key=='Kap':
            BLobjects.getKap().asynchronousMoveTo(angle)
         elif key=='Kth':
            BLobjects.getKth().asynchronousMoveTo(angle)
         elif key=='Kmu':
            BLobjects.getKmu().asynchronousMoveTo(angle)
         if self.x == 'smargon':
            if key=='phi':
               BLobjects.getsgphi().asynchronousMoveTo(angle)
            if key=='chi':
               BLobjects.getsgchi().asynchronousMoveTo(angle)
            if key=='eta':
               BLobjects.getsgomega().asynchronousMoveTo(angle)
         
   def getAngles(self):
      if BLobjects.isSimulation():
         d=self.SA.getValue('Angles')
         return d
      elif self.x == "K": 
         print "sono qui"
         d = Angles.Angles()
         d.Kmu = BLobjects.getKmu().getPosition()
         d.Kphi = BLobjects.getKphi().getPosition()
         d.Kap = BLobjects.getKap().getPosition()
         d.Kth = BLobjects.getKth().getPosition()
         d.Delta = BLobjects.getDelta().getPosition()
         d.Gam = BLobjects.getGam().getPosition()
         return d
      elif self.x == 'SA':
         euAngles = self.ekcm.getEulerianAngles([BLobjects.getKth().getPosition(),BLobjects.getKap().getPosition(),BLobjects.getKphi().getPosition()])
         d = Angles.Angles()
         d.Theta = euAngles.Theta
         d.Phi = euAngles.Phi
         d.Chi = euAngles.Chi
         d.Mu = BLobjects.getKmu().getPosition()
         d.Eta = euAngles.Theta
         d.Kmu = BLobjects.getKmu().getPosition()
         d.Kphi = BLobjects.getKphi().getPosition()
         d.Kap = BLobjects.getKap().getPosition()
         d.Kth = BLobjects.getKth().getPosition()
         d.Delta = BLobjects.getDelta().getPosition()
         d.Gam = BLobjects.getGam().getPosition()
         d.Gamma = BLobjects.getGam().getPosition()
         return d
      elif self.x == 'smargon':
         d = Angles.Angles()
         d.Theta = BLobjects.getsgomega().getPosition() #warning in sixc can be mu or eta
         d.Phi = BLobjects.getsgphi().getPosition()
         d.Chi = BLobjects.getsgchi().getPosition()
         d.Mu = BLobjects.getKmu().getPosition()
         d.Eta = BLobjects.getsgomega().getPosition()
         d.Kmu = BLobjects.getKmu().getPosition()
         d.Kphi = BLobjects.getKphi().getPosition()
         d.Kap = BLobjects.getKap().getPosition()
         d.Kth = BLobjects.getKth().getPosition()
         d.Delta = BLobjects.getDelta().getPosition()
         d.Gam = BLobjects.getGam().getPosition()
         d.Gamma = BLobjects.getGam().getPosition()
         return d
         
         
         #get the current motor value
