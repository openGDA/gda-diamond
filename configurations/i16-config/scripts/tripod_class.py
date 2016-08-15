# Copyright 2015 Diamond Light Source Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

try:
    print "=== Trying Python imports..."
    import numpy as np
    from numpy.linalg.linalg import norm
    from numpy.linalg.linalg import inv
    from numpy.linalg.linalg import dot
    print "=== OK"
except:
    print "=== ... No joy ... trying Jython imports"
    import scisoftpy as np
    from scisoftpy.linalg import norm   
    from scisoftpy.linalg import inv
    from scisoftpy import dot
    print "=== OK"


class tripod_class():
    '''
    Python class to carry out calculations for tripod with six base translations
    See tripod_calculations.pdf for desciption.
    Needs basic array methods from numpy (python) or Diamond scisoftpy (jython) for iterative solver
    Initialization arguments:
    l, t, psi:      Lists of l, t, psi values for each leg
    c:              x,y,z coordinates of tooling point relative to the top
    theta:          Approximate theta values (used for signs and numerical solver)
    BX, BY:         Lists is X and Y coordinates for base positions when translations are zero
    tol:            Minimum meaningful angular step (rad) (keyword arg: default=1e-7) 
    Main user (public) methods:
    Typing object name (string representation) gives a summary of parameters and
        calculation of tooling point parameters from base vectors and back
    self.ctool((X1, X2, X3), (Y1, Y2, Y3) calculates tool parameters from X list (X values for each leg)
        and Y list; outputs coordinates of tooling point and tilt angles (degrees)
    self.cbase((CX, CY, CZ),(alpha1,alpha2, alpha3)) calculates base vectors
        for tooling point coordinates and angles (degrees)
    SP Collins & RC Harwin
    '''

    def __init__(self, l, t, psi, c, theta, BX, BY, tol=1e-7):
        self.l, self.t, self.psi, self.c, self.theta, self.BX, self.BY = l, t, psi, c, theta, BX, BY
        self.X, self.Y = 0, 0    # initial values of slides
        self.tol = tol           # smallest meaningful angle step

    def __repr__(self):
        rad_to_deg = 180.0/np.pi
        C, (alpha1, alpha2, alpha3) = self.ctool(self.X, self.Y)    # calculate top position and angles from base translations
        X, Y = self._calcBXY(C, np.array([alpha1, alpha2, alpha3])*np.pi/180)               # reverse calculation (as a check)

        return '\nTripod parameters:\n\n' \
            + 'Leg lenghts(l):\t\t %.3f, %.3f, %.3f\n' % tuple(self.l) \
            + 'Edge lenghts(s):\t\t %.3f, %.3f, %.3f\n' % tuple(self.t) \
            + 'Hinge rotations (psi deg):\t %.3f, %.3f, %.3f\n' % tuple(np.array(self.psi) * rad_to_deg) \
            + 'Tool point xyz:\t\t %.3f, %.3f, %.3f\n' % tuple(self.c) \
            + 'Base X centres:\t\t %.3f, %.3f, %.3f\n' % tuple(self.BX) \
            + 'Base Y centres:\t\t %.3f, %.3f, %.3f\n' % tuple(self.BY) \
            + 'Approx. tilts (theta deg ):\t %.3f, %.3f, %.3f\n\n' % tuple(np.array(self.theta) * rad_to_deg) \
            + 'Slide X:\t\t\t %.3f, %.3f, %.3f\n' % tuple(self.X) \
            + 'Slide Y:\t\t\t %.3f, %.3f, %.3f\n' % tuple(self.Y) \
            + 'Tool point (C):\t\t %.3f, %.3f, %.3f\n' % tuple(C) \
            + 'Tool angles (alpha deg):\t %.3f, %.3f, %.3f\n' % (alpha1, alpha2, alpha3) \
            + 'Reverse calc Slide X:\t\t %.3f, %.3f, %.3f\n' % tuple(X) \
            + 'Reverse calc Slide Y:\t\t %.3f, %.3f, %.3f\n' % tuple(Y) \

    def ctool(self, X, Y):
        '''
        self.ctool((X1, X2, X3), (Y1, Y2, Y3) calculates tool parameters from X list (X values for each leg) 
            and Y list; outputs coordinates of tooling point and tilt angles (degrees)
        '''
        self.X, self.Y = X, Y
        # main calculation of C and alpha tilts from base positions
        # Base vectors from given translations (X,Y)and fixed centres (BX, BY)
        B1 = np.array((X[0] + self.BX[0], Y[0] + self.BY[0], 0))
        B2 = np.array((X[1] + self.BX[1], Y[1] + self.BY[1], 0))
        B3 = np.array((X[2] + self.BX[2], Y[2] + self.BY[2], 0))
        # Top (T) vectors from bottom (B) vectors and leg vectors (v)
        (theta1, theta2, theta3) = self._calcThetafromB([B1, B2, B3])
        v1 = np.array([np.cos(self.psi[0]) * np.sin(theta1), np.sin(self.psi[0]) * np.sin(theta1), np.cos(theta1)])
        v2 = np.array([np.cos(self.psi[1]) * np.sin(theta2), np.sin(self.psi[1]) * np.sin(theta2), np.cos(theta2)])
        v3 = np.array([np.cos(self.psi[2]) * np.sin(theta3), np.sin(self.psi[2]) * np.sin(theta3), np.cos(theta3)])
        T1, T2, T3 = B1 + self.l[0] * v1, B2 + self.l[1] * v2, B3 + self.l[2] * v3
        self.T1, self.T2, self.T3 = T1, T2, T3    # for diagnostics only - can remove
        # calculate tooling point coords and angles
        yvec = (T1 - T2)/norm(T1 - T2)
        zvec = np.cross((T3 - T1),yvec)/norm(np.cross((T3 - T1),yvec))
        xvec = np.cross(yvec, zvec)
        C = T2 + self.c[0] * xvec+self.c[1] * yvec+self.c[2] * zvec
        self.alpha1 = np.arctan(yvec[2]/zvec[2])
        self.alpha2 = np.arcsin(-xvec[2])
        self.alpha3 = np.arctan(xvec[1]/xvec[0])
        return (C, np.array([self.alpha1*180/np.pi, self.alpha2*180/np.pi, self.alpha3*180/np.pi]))

    def _tripod_calc_theta123_func(self, p, B1X, B1Y, B2X, B2Y, B3X, B3Y, psi1, psi2, psi3, l1, l2, l3, t1, t2, t3):
        # function to minimize
        theta1, theta2, theta3 = p
        # all params: theta1, theta2, theta3, B1X, B1Y, B2X, B2Y, B3X, B3Y, psi1, psi2, psi3, l1, l2, 3, t1, t2, t3 
        B1 = np.array([B1X, B1Y, 0])
        B2 = np.array([B2X, B2Y, 0])
        B3 = np.array([B3X, B3Y, 0])
        v1 = np.array([np.cos(psi1) * np.sin(theta1), np.sin(psi1) * np.sin(theta1), np.cos(theta1)])
        v2 = np.array([np.cos(psi2) * np.sin(theta2), np.sin(psi2) * np.sin(theta2), np.cos(theta2)])
        v3 = np.array([np.cos(psi3) * np.sin(theta3), np.sin(psi3) * np.sin(theta3), np.cos(theta3)])
        eq1 = norm(B2 + l2 * v2 - B3 - l3 * v3) - t1
        eq2 = norm(B3 + l3 * v3 - B1 - l1 * v1) - t2
        eq3 = norm(B1 + l1 * v1 - B2 - l2 * v2) - t3
        return (eq1, eq2, eq3)

    def _calcThetafromB(self, B):
        # calculates leg tilt angles (see documentation)
        # iteration stops when angle error < self.tol/10
        args = (B[0][0], B[0][1], B[1][0], B[1][1], B[2][0], B[2][1], self.psi[0], self.psi[1], self.psi[2], self.l[0], self.l[1], self.l[2], self.t[0], self.t[1], self.t[2])
        Y = self._tripod_calc_theta123_func   # use abbreviated function name
        X = (self.theta[0], self.theta[1], self.theta[2])  # start values
        dX = np.array(3 * [self.tol])
        dY_dX = [None, None, None]
        _maxiter = 99
        for i in range(_maxiter):
            Y_X =Y(X ,*args)
            dY_dX[0] = (np.array(Y((X[0] + dX[0], X[1], X[2]), *args)) - np.array(Y_X)) / dX[0]
            dY_dX[1] = (np.array(Y((X[0], X[1] + dX[1], X[2]), *args)) - np.array(Y_X)) / dX[1]
            dY_dX[2] = (np.array(Y((X[0], X[1], X[2] + dX[2]), *args)) - np.array(Y_X)) / dX[2]
            M = np.array(dY_dX)
            Minv = inv(M)
            Xnew = np.array(X) - dot(np.array(Y_X), Minv)
            ang_change = norm(Xnew - np.array(X))
            X = Xnew
            if ang_change < self.tol / 10:
                break
        assert ang_change < self.tol / 10, '=== No convergence:\n=== DO NOT MOVE TO THIS POSITION ==='
        return X

    def _calcBXY(self, C, (alpha1, alpha2, alpha3)):
        # calculate base translations (see documentation)
        (xvec, yvec, zvec) = self._calc_xyzvec(alpha1, alpha2, alpha3)
        # calculate T1,2,3 from xvec, yvec, zvec
        T2 = C - (self.c[0]*xvec+self.c[1]*yvec+self.c[2]*zvec)
        T1 = T2+self.t[2]*yvec
        cos_t2 = (self.t[0]**2+self.t[2]**2 - self.t[1]**2)/(2*self.t[0]*self.t[2])  # cosine rule
        sin_t2 = np.sqrt(1 - cos_t2**2)
        T3 = T2 + xvec*self.t[0]*sin_t2 + yvec*self.t[0]*cos_t2
        # calc B from T
        cos_theta1 = T1[2]/self.l[0]    # T1[2] =  = T1.z etc
        cos_theta2 = T2[2]/self.l[1]
        cos_theta3 = T3[2]/self.l[2]
        sin_theta1 = np.sqrt(1 - cos_theta1**2)*np.sign(self.theta[0])
        sin_theta2 = np.sqrt(1 - cos_theta2**2)*np.sign(self.theta[1])
        sin_theta3 = np.sqrt(1 - cos_theta3**2)*np.sign(self.theta[2])
        v1 = np.array([np.cos(self.psi[0])*sin_theta1, np.sin(self.psi[0])*sin_theta1, cos_theta1])
        v2 = np.array([np.cos(self.psi[1])*sin_theta2, np.sin(self.psi[1])*sin_theta2, cos_theta2])
        v3 = np.array([np.cos(self.psi[2])*sin_theta3, np.sin(self.psi[2])*sin_theta3, cos_theta3])
        B1, B2, B3 = T1 - v1*self.l[0], T2 - v2*self.l[1], T3 - v3*self.l[2]
        X = [B1[0] - self.BX[0], B2[0] - self.BX[1], B3[0] - self.BX[2]]   # X[leg1,2,3], B1,2,3[X,Y,Z], BX[leg1,2,3]
        Y = [B1[1] - self.BY[0], B2[1] - self.BY[1], B3[1] - self.BY[2]]
        return X, Y

    def _calc_xyzvec(self, alpha1, alpha2, alpha3):
        # calculate top plate coordinate vectors (see documentation)
        Rx_alpha1 = np.array([[1, 0, 0], [0, np.cos(alpha1), -np.sin(alpha1)], [0, np.sin(alpha1), np.cos(alpha1)]])
        Ry_alpha2 = np.array([[np.cos(alpha2), 0, np.sin(alpha2)], [0, 1, 0], [-np.sin(alpha2), 0, np.cos(alpha2)]])
        Rz_alpha3 = np.array([[np.cos(alpha3), -np.sin(alpha3), 0], [np.sin(alpha3), np.cos(alpha3), 0], [0, 0, 1]])
        R = np.dot(Rz_alpha3, np.dot(Ry_alpha2, Rx_alpha1))
        xvec, yvec, zvec = R[:,0], R[:,1], R[:,2]
        return (xvec, yvec, zvec)

    def cbase(self, C, (alpha1, alpha2, alpha3)):
        'self.cbase((CX, CY, CZ),(alpha1,alpha2, alpha3)) calculates base vectors for tooling point coordinates and angles (degrees)'
        X, Y = self._calcBXY(C, (alpha1 * np.pi / 180, alpha2 * np.pi / 180, alpha3 * np.pi / 180))
        self.X, self.Y = X, Y
        return np.array(X), np.array(Y)

if __name__ == '__main__':
    print '=== Performing transformations in both directions for consistency, using random numbers'
    tp = tripod_class([134.2, 134.2, 134.2], [194.1, 194.1, 59.9], [-np.pi/3, np.pi/3, 0], [98.0, 29.95, 60.0], [np.pi/4, np.pi/4, -np.pi/4], [0.0, 0.0, 357], [254.0, 0.0, 127.0])  # mainly from drawings except base centres
    X, Y = np.random.rand(3) * 5, np.random.rand(3) * 5
    print 'X coords of base translations applied: %.3f %.3f %.3f' % tuple(X), '\nY coords of base translations applied: %.3f %.3f %.3f' % tuple(Y)
    c, alpha = tp.ctool(X, Y)  # calculate tool-pint coordinates c and tiltangles alpha for given X Y base translations
    print 'Tool point coords (c):  %.3f %.3f %.3f' % tuple(c), '\nTilt angles (alpha, deg) :%.3f %.3f %.3f' % tuple(alpha)
    print 'Reverse calculation to check that X and Y are reproduced'
    Xnew, Ynew = tp.cbase(c, np.array(alpha))
    print 'X coords of base translations applied: %.3f %.3f %.3f' % tuple(Xnew),'\nY coords of base translations applied: %.3f %.3f %.3f' % tuple(Ynew)
    if np.allclose([X, Y], [Xnew, Ynew]):
        print '=== Test passed!'
    else:
        print '=== Test failed!'
