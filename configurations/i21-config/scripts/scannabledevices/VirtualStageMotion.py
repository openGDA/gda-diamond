'''
Created on 21 Mar 2018

@author: fy65
'''
from gda.device.scannable import  ScannableMotionBase
from diffcalc.ub.ub import ubcalc 
from gdaserver import sax, say, saz

class VirtualStageMotion(ScannableMotionBase):
        '''Device to move sample stage perpendicular or parallel to the beam when phi and th are not zero'''
        def __init__(self,name,x,y,z,help=None):
            self.setName(name)             
            if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
            self.setInputNames([name])
            self.setOutputFormat(['%4.4f'])
            self.Units=['mm']
            self.setLevel(5)
            self.x=x
            self.y=y
            self.z=z

        def asynchronousMoveTo(self,value):
            if (self.getName()=="vz"):
                vx_value=vx.getPosition()
                vy_value=vy.getPosition()
                vz_value=value
            elif (self.getName()=="vy"):
                vx_value=vx.getPosition()
                vy_value=value
                vz_value=vz.getPosition()
                
            elif (self.getName()=="vx"):
                vx_value=value
                vy_value=vy.getPosition()
                vz_value=vz.getPosition()
            else:
                raise RuntimeError('Blah!')
            self.z.asynchronousMoveTo(ubcalc.U[0,0]*float(vz_value) - ubcalc.U[0,1]*float(vy_value) - ubcalc.U[0,2]*float(vx_value))
            self.y.asynchronousMoveTo(-ubcalc.U[1,0]*float(vz_value) + ubcalc.U[1,1]*float(vy_value) + ubcalc.U[1,2]*float(vx_value))
            self.x.asynchronousMoveTo(-ubcalc.U[2,0]*float(vz_value) + ubcalc.U[2,1]*float(vy_value) + ubcalc.U[2,2]*float(vx_value))
               
        def getPosition(self):
            if (self.getName()=="vz"):
                index=0
            elif (self.getName()=="vy"):
                index=1
            elif (self.getName()=="vx"):
                index=2
            else:
                raise RuntimeError('Blah!')
            tmp_pos = (-ubcalc.U.I[index,0]*float(self.z.getPosition()))+(ubcalc.U.I[index,1]*float(self.y.getPosition()))+(ubcalc.U.I[index,2]*float(self.x.getPosition()))
            if (self.getName()=="vz"):
                tmp_pos *= -1
            return tmp_pos

           
        def isBusy(self):
            return self.x.isBusy() or self.y.isBusy() or self.z.isBusy()

vx=VirtualStageMotion("vx",sax,say,saz)
vy=VirtualStageMotion("vy",sax,say,saz)
vz=VirtualStageMotion("vz",sax,say,saz)

