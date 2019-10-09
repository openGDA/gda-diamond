import java
import math
from math import *


#class Rotations(java.lang.Object):
#   def __init__(self):
#      self.rrrr=0.0

def R_x_l(alpha):
   "@sig public double R_x_l(double alpha)"
#      phi=phi*pi/180.0
   ALPHA=[[1.0, 0.0, 0.0],[0.0, cos(alpha), sin(alpha)], [0.0, -sin(alpha), cos(alpha)]]
   return ALPHA

def R_x_r(alpha):
   "@sig public double R_x_r(double alpha)"
#      phi=phi*pi/180.0
   ALPHA=[[1.0, 0.0, 0.0],[0.0, cos(alpha),-sin(alpha)], [0.0, sin(alpha), cos(alpha)]]
   return ALPHA


def R_y_r(alpha):
   "@sig public double R_y_r(double alpha)"
   ALPHA=[[cos(alpha),0.0, sin(alpha)],[0.0, 1.0, 0.0], [-sin(alpha), 0.0, cos(alpha)]]
   return ALPHA

def R_y_l(alpha):
   "@sig public double R_z_l(double alpha)"
   ALPHA=[[cos(alpha),0.0, -sin(alpha)],[0.0, 1.0, 0.0], [sin(alpha), 0.0, cos(alpha)]]
   return ALPHA


def R_z_l(alpha):
   "@sig public double R_z_l(double alpha)"
   ALPHA=[[cos(alpha),sin(alpha), 0.0],[-sin(alpha), cos(alpha), 0.0], [0.0, 0.0, 1.0]]
   return ALPHA

def R_z_r(alpha):
   "@sig public double R_z_r(double alpha)"
   ALPHA=[[cos(alpha),-sin(alpha), 0.0],[sin(alpha), cos(alpha), 0.0], [0.0, 0.0, 1.0]]
   return ALPHA


