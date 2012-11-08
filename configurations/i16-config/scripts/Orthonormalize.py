import java
from math import *
from Jama import Matrix
from MatrixAlgebra import CROSS

def orthonormalize(x,y=None):
   if y == None:
      try:
         print "Matrix calculated without using the reference vector"
         y=[sqrt(x[1]**2+x[2]**2), -(x[0]*x[1])/sqrt(x[1]**2+x[2]**2),-(x[0]*x[2])/sqrt(x[1]**2+x[2]**2)]
      except:
         print "THIS IS Y", y
         print "Not possible to build an orthogonal matrix from the given vector"
   x=Matrix(x,3)
   y=Matrix(y,3)
   x=x.times(1./x.normF())
   y=y.times(1./y.normF())
   X=[x.get(0,0),x.get(1,0),x.get(2,0)]
   Y=[y.get(0,0),y.get(1,0),y.get(2,0)]
   Z=CROSS(X,Y)
   z=Matrix(Z,3)
   z=z.times(1./z.normF())
   Z=[z.get(0,0),z.get(1,0),z.get(2,0)]
   Y= CROSS(Z,X)
   y=Matrix(Y,3)
   y=y.times(1./y.normF())
   ortho=Matrix(3,3)
   ortho.setMatrix(0,2,0,0,x)
   ortho.setMatrix(0,2,1,1,y)
   ortho.setMatrix(0,2,2,2,z)
   return ortho
