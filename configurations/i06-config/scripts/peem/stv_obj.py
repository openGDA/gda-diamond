#from java import lang
from java.lang import System
from time import sleep
import math
from gda.device.scannable import PseudoDevice

class Stv_Obj(PseudoDevice):
    def __init__(self, name, leem_stv, leem_obj, a=-38.7462,b = -12.82824,c = 20.92462):
        self.name = name
        self.setOutputFormat(['%4.1f'])
        self.currentPosition = leem_stv.getPosition()
        self.setInputNames([name]);
        self.leem_stv=leem_stv
        self.leem_obj=leem_obj
        self.a = a
        self.b = b
        self.c = c

    def getPosition(self):
        return self.leem_stv.getPosition()

    def asynchronousMoveTo(self,new_position):
        objStart = self.leem_obj.getPosition()-self.obj_delta(self.leem_stv.getPosition())
        self.leem_stv.asynchronousMoveTo(new_position)
        self.currentPosition=new_position
        #move the obj accordingly
        finalObj = objStart + self.obj_delta(new_position)
        self.leem_obj.asynchronousMoveTo(finalObj)
        return

    def isBusy(self):
        return self.leem_obj.isBusy() or self.leem_stv.isBusy()

    def obj_delta(self, new_position):
        return self.a - self.b * math.log(new_position + self.c)
 

