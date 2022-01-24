import java
import math
from math import *

def CROSS(X,Y):
   "@sig public double[] CROSS(double[] X,double[] Y)"
   z0=X[1]*Y[2]-X[2]*Y[1]
   z1=X[2]*Y[0]-X[0]*Y[2]
   z2=X[0]*Y[1]-X[1]*Y[0]
   Z=[z0,z1,z2]
   return Z

def __repr__(self):
   return '<MatrixAlgebra error>'


