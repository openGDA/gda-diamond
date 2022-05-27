# Dr Gareth Nisbet, Diamond Light Source LTD, March 2022 

import scisoftpy as np

class kinematics(object):
    '''
    Calculates forward and inverse kinematics for robot arm.\n
    Instantiate with:\n
    kin = kinematics(axis_vects,L_vects,motor_limits,motor_offsets,tool_offset)
    '''
    def __init__(self,*args):
        self.axis_vects=args[0]
        self.L_vects=args[1]
        self.motor_limits = args[2]
        self.motor_offsets = np.array(args[3])
        self.tool_offset = args[4]
        self.centre_offset = args[5]
        self.strategy = args[6]
        self.weighting = args[7]
        self.constraint = args[8]
        self.solutions = np.array([0,0,0,0,0,0])

    def setStrategy(self,strategy):
        ''' minimum_movement, minimum_movement_weighted, comfortable_limits '''
        self.strategy = strategy
        
    def setConstraint(self,constraint):
        self.constraint = constraint
        
    def setWeighting(self,weighting):
        self.weighting = weighting
         
    def setLimits(self,motor_limits):
        self.motor_limits = motor_limits
        
    def setToolOffset(self, tool_offset):
        self.tool_offset = tool_offset
        
    def setMotorOffset(self, motor_offsets):
        self.motor_offsets = motor_offsets
    
    def setCentreOffset(self, centre_offset):
        self.centre_offset = centre_offset

    def vanglev(self,v1,v2):
        angle = np.arccos(np.dot(v1,v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)))
        return angle

    def vp_angle(self,v1,v2,v3):
        plane_normal = np.cross(v2,v3)
        return np.arccos(np.dot(v1,plane_normal)/(np.linalg.norm(v1)*np.linalg.norm(plane_normal)))

    def rotxyz(self, v, u, angle):
        u = np.array(u)
        if len(u.shape) < 2:
            u = np.array([u])
        u=u/np.linalg.norm(u)
        e11=u[0,0]**2+(1-u[0,0]**2)*np.cos(angle*np.pi/180.0)
        e12=u[0,0]*u[0,1]*(1-np.cos(angle*np.pi/180.0))-u[0,2]*np.sin(angle*np.pi/180.0)
        e13=u[0,0]*u[0,2]*(1-np.cos(angle*np.pi/180.0))+u[0,1]*np.sin(angle*np.pi/180.0)
        e21=u[0,0]*u[0,1]*(1-np.cos(angle*np.pi/180.0))+u[0,2]*np.sin(angle*np.pi/180.0)
        e22=u[0,1]**2+(1-u[0,1]**2)*np.cos(angle*np.pi/180.0)
        e23=u[0,1]*u[0,2]*(1-np.cos(angle*np.pi/180.0))-u[0,0]*np.sin(angle*np.pi/180.0)
        e31=u[0,0]*u[0,2]*(1-np.cos(angle*np.pi/180.0))-u[0,1]*np.sin(angle*np.pi/180.0)
        e32=u[0,1]*u[0,2]*(1-np.cos(angle*np.pi/180.0))+u[0,0]*np.sin(angle*np.pi/180.0)
        e33=u[0,2]**2+(1-u[0,2]**2)*np.cos(angle*np.pi/180.0)
        self.rotmatx = np.array([[e11,e12,e13],[e21,e22,e23],[e31,e32,e33]])
        return np.dot(self.rotmatx,v.T).T

    def eulerMatrix(self,alpha,beta,gamma):
        M_alpha = np.array([[np.cos(alpha*np.pi/180), np.sin(alpha*np.pi/180), 0],
                             [-np.sin(alpha*np.pi/180), np.cos(alpha*np.pi/180), 0],
                             [0, 0, 1]
                             ])
        M_beta = np.array([[np.cos(beta*np.pi/180), 0, -np.sin(beta*np.pi/180)],
                            [0, 1, 0],
                            [np.sin(beta*np.pi/180), 0, np.cos(beta*np.pi/180)],

                             ])
        M_gamma = np.array([[np.cos(gamma*np.pi/180), np.sin(gamma*np.pi/180), 0],
                             [-np.sin(gamma*np.pi/180), np.cos(gamma*np.pi/180), 0],
                             [0, 0, 1]
                             ])
        return np.dot(M_alpha,M_beta,M_gamma)

    def rotationMatrixToEulerXYX(self,rmatrix):
        alpha = np.arctan2(rmatrix[1,0],-rmatrix[2,0]) #  z-y-x rotation matrix is constructed from vectors
        beta = -np.arctan2(np.sqrt(1-rmatrix[0,0]**2),rmatrix[0,0]) #  z-y-x 
        gamma = -np.arctan2(rmatrix[0,1],rmatrix[0,2])  #  in rows not columns  
        return alpha*180/np.pi, beta*180/np.pi, gamma*180/np.pi
        
    def rotationMatrixToEulerZYX(self,rmatrix):
        sy = np.sqrt(rmatrix[2,1]**2 +  rmatrix[2,2]**2)
        singular = sy < 1e-6
        if  not singular :
            alpha = -np.arctan2(rmatrix[2,1],rmatrix[2,2]) #  z-y-x rotation matrix is constructed from vectors
            beta = -np.arctan2(-rmatrix[2,0],np.sqrt(rmatrix[2,1]**2+rmatrix[2,2]**2)) #  z-y-x 
            gamma = -np.arctan2(rmatrix[1,0],rmatrix[0,0])  #  in rows not columns 
        else:
            alpha = np.pi-np.arctan2(rmatrix[0,1],rmatrix[0,2]) #  z-y-x rotation matrix is constructed from vectors
            beta = -np.arctan2(-rmatrix[2,0],np.sqrt(rmatrix[2,1]**2+rmatrix[2,2]**2)) #  z-y-x 
            gamma = -np.arctan2(rmatrix[1,0],rmatrix[0,0])  #  in rows not columns
        return alpha*180/np.pi, beta*180/np.pi, gamma*180/np.pi

    def rotmat(self,u, angle):
        #clockwise rotation
        u=np.array([u])
        u=u/np.linalg.norm(u)
        e11=u[0,0]**2+(1-u[0,0]**2)*np.cos(angle*np.pi/180.0)
        e12=u[0,0]*u[0,1]*(1-np.cos(angle*np.pi/180.0))-u[0,2]*np.sin(angle*np.pi/180.0)
        e13=u[0,0]*u[0,2]*(1-np.cos(angle*np.pi/180.0))+u[0,1]*np.sin(angle*np.pi/180.0)
        e21=u[0,0]*u[0,1]*(1-np.cos(angle*np.pi/180.0))+u[0,2]*np.sin(angle*np.pi/180.0)
        e22=u[0,1]**2+(1-u[0,1]**2)*np.cos(angle*np.pi/180.0)
        e23=u[0,1]*u[0,2]*(1-np.cos(angle*np.pi/180.0))-u[0,0]*np.sin(angle*np.pi/180.0)
        e31=u[0,0]*u[0,2]*(1-np.cos(angle*np.pi/180.0))-u[0,1]*np.sin(angle*np.pi/180.0)
        e32=u[0,1]*u[0,2]*(1-np.cos(angle*np.pi/180.0))+u[0,0]*np.sin(angle*np.pi/180.0)
        e33=u[0,2]**2+(1-u[0,2]**2)*np.cos(angle*np.pi/180.0)
        rotmatx = np.array([[e11,e12,e13],[e21,e22,e23],[e31,e32,e33]])
        return rotmatx

    def rotationMatrixToEulerZYZ_extrinsic(self,rmatrix):
        alpha = np.pi/2-np.arctan2(rmatrix[2,0],rmatrix[2,1]) #  z-y-x rotation matrix is constructed from vectors
        beta = np.pi/2-np.arccos(rmatrix[2,2]) 
        gamma = -(np.arctan2(rmatrix[0,2],rmatrix[1,2])+np.pi/2) #  in rows not columns
        return alpha*180/np.pi, beta*180/np.pi, gamma*180/np.pi

    def setEulerTarget(self,_x,_y,_z,r_alpha,r_beta,r_gamma):
        xyz = np.array([_x,_y,_z])

        vx = np.array([1,0,0])
        vy = np.array([0,1,0])
        vz = np.array([0,0,1])
        #em = self.rotmat(vz, r_gamma)*self.rotmat(vy, r_beta)*self.rotmat(vx, r_alpha)
        em = np.dot(np.dot(self.rotmat(vx, r_alpha),self.rotmat(vy, r_beta)),self.rotmat(vz, r_gamma)) # ZYX convention
        targetmatrix = np.array([ 
                        np.dot(em,np.array([vx]).T).T[0], 
                        np.dot(em,np.array([vy]).T).T[0],
                        np.dot(em,np.array([vz]).T).T[0]  ]) 
        tool = np.dot(np.array([self.tool_offset]),targetmatrix)[0]
        xyzt = np.array(xyz+tool)
        tv1 =  list(np.dot(np.array([vx]),targetmatrix)[0])
        tv2 =  list(np.dot(np.array([vy]),targetmatrix)[0])
        tv3 =  list(np.dot(np.array([vz]),targetmatrix)[0])
        raw_motor_values = self.i_kinematics(np.array([xyzt, tv1, tv2, tv3]))
        return raw_motor_values

    def get_mu_eta_chi_phi(self,alpha,beta,gamma):
        
        v=np.identity(3)
        em = np.dot(np.dot(self.rotmat(v[:,0], alpha),self.rotmat(v[:,1], beta)),self.rotmat(v[:,2], gamma)) # ZYX convention
        R = np.array([np.dot(em,np.array(v[:,0]).T).T, 
                      np.dot(em,np.array(v[:,1]).T).T,
                      np.dot(em,np.array(v[:,2]).T).T])
        
        if self.constraint == 'mu':    
            phi = -gamma
            chi = 90-beta
            eta = -alpha
            mu = 0        
        elif self.constraint == 'eta':
            eta = 0
            alpha2, beta2, gamma2 = self.rotationMatrixToEulerZYZ_extrinsic(R)
            phi = gamma2
            chi = beta2
            mu = alpha2
            if alpha <= -179.9999 and alpha >= -180.0001 and gamma <= -179.9999 and gamma >= -180.0001:
                phi = -gamma
                chi = 90-beta
                eta = -alpha
                mu = 0        
        else:
            print('#------------------------------------------#')
            print('Set eta or mu Constraint')
            print('#------------------------------------------#')
        return mu, eta, chi, phi

    def set_mu_eta_chi_phi(self,mu, eta, chi, phi):
        v =  np.identity(3)
#         rmatrix = np.dot(self.rotmat(v[2,:], -mu), self.rotmat(v[0,:], eta), self.rotmat(v[1,:], -(90-chi)), self.rotmat(v[2,:], phi))
        m1 = np.dot(self.rotmat(v[2,:], phi),self.rotmat(v[1,:], -(90-chi)))
        m2 = np.dot(m1,self.rotmat(v[0,:], eta))
        rmatrix = np.dot(m2,self.rotmat(v[2,:], -mu))
        #rmatrix = np.dot(self.rotmat(v[2,:], phi),self.rotmat(v[1,:], -(90-chi))),self.rotmat(v[0,:], eta),self.rotmat(v[2,:], mu))
        rmatrix[np.where(np.abs(rmatrix)<0.00001)] = 0
        alpha,beta,gamma = self.rotationMatrixToEulerZYX(rmatrix)
        return alpha, beta, gamma # fix this 

    def f_kinematics(self,*inputs):
        inputs=inputs[0]
        
        angles = inputs + self.motor_offsets

        #L 0
        _v0 = np.array([self.axis_vects[0,:]])
        self.v0 = self.rotxyz(np.array([self.L_vects[0,:]]), _v0 ,angles[0])
        
        # L 1
        _v1 = self.rotxyz(np.array([self.L_vects[1,:]]), self.axis_vects[1,:], angles[1])
        self.v1 = self.v0 + self.rotxyz(_v1, self.axis_vects[0,:], angles[0])
       
        #L2
        _v2 = self.rotxyz(np.array([self.L_vects[2,:]]), self.axis_vects[2,:], angles[2])
        _v2 = self.rotxyz(_v2, self.axis_vects[1,:], angles[1])    
        self.v2 = self.v1 + self.rotxyz(_v2, self.axis_vects[0,:], angles[0])  
            
        #L3
        _v3 = self.rotxyz(np.array([self.L_vects[3,:]]), self.axis_vects[3,:], angles[3])
        _v3 = self.rotxyz(_v3, self.axis_vects[2,:], angles[2])
        _v3 = self.rotxyz(_v3, self.axis_vects[1,:], angles[1])
        self.v3 = self.v2 + self.rotxyz(_v3, self.axis_vects[0,:], angles[0])

        #L4
        _v4 = self.rotxyz(np.array([self.L_vects[4,:]]), self.axis_vects[4,:], angles[4])
        _v4 = self.rotxyz(_v4, self.axis_vects[3,:], angles[3])
        _v4 = self.rotxyz(_v4, self.axis_vects[2,:], angles[2])  
        _v4 = self.rotxyz(_v4, self.axis_vects[1,:], angles[1])          
        self.v4 = self.v3 + self.rotxyz(_v4, self.axis_vects[0,:], angles[0]) 
    
        #L5
        _v5 = self.rotxyz(np.array([self.L_vects[5,:]]), self.axis_vects[5,:], angles[5])
        _v5 = self.rotxyz(_v5, self.axis_vects[4,:], angles[4])
        _v5 = self.rotxyz(_v5, self.axis_vects[3,:], angles[3])  
        _v5 = self.rotxyz(_v5, self.axis_vects[2,:], angles[2])
        _v5 = self.rotxyz(_v5, self.axis_vects[1,:], angles[1])                  
        self.v5 = self.rotxyz(_v5, self.axis_vects[0,:], angles[0])


        new_centre = self.rotxyz(np.array([self.centre_offset]), self.axis_vects[5,:] ,angles[5])        
        new_centre = self.rotxyz(new_centre, self.axis_vects[4,:] ,angles[4]) 
        new_centre = self.rotxyz(new_centre, self.axis_vects[3,:] ,angles[3]) 
        new_centre = self.rotxyz(new_centre, self.axis_vects[2,:] ,angles[2]) 
        new_centre = self.rotxyz(new_centre, self.axis_vects[1,:] ,angles[1])        
        new_centre = self.rotxyz(new_centre, self.axis_vects[0,:] ,angles[0])



                #L5
        _t_off = self.rotxyz(np.array([self.tool_offset]), self.axis_vects[5,:], angles[5])
        _t_off = self.rotxyz(_t_off, self.axis_vects[4,:], angles[4])
        _t_off = self.rotxyz(_t_off, self.axis_vects[3,:], angles[3])  
        _t_off = self.rotxyz(_t_off, self.axis_vects[2,:], angles[2])
        _t_off = self.rotxyz(_t_off, self.axis_vects[1,:], angles[1])                  
        self._t_off = self.rotxyz(_t_off, self.axis_vects[0,:], angles[0])
        
        
        
        _v6 = self.rotxyz(np.array([self.L_vects[6,:]]), self.axis_vects[5,:], angles[5])
        _v6 = self.rotxyz(_v6, self.axis_vects[4,:], angles[4])
        _v6 = self.rotxyz(_v6, self.axis_vects[3,:], angles[3])  
        _v6 = self.rotxyz(_v6, self.axis_vects[2,:], angles[2])
        _v6 = self.rotxyz(_v6, self.axis_vects[1,:], angles[1])        
        self.v6 = self.rotxyz(_v6, self.axis_vects[0,:], angles[0])
        
        _v7 = self.rotxyz(np.array([self.L_vects[7,:]]), self.axis_vects[5,:], angles[5])
        _v7 = self.rotxyz(_v7, self.axis_vects[4,:], angles[4])
        _v7 = self.rotxyz(_v7, self.axis_vects[3,:], angles[3])  
        _v7 = self.rotxyz(_v7, self.axis_vects[2,:], angles[2])
        _v7 = self.rotxyz(_v7, self.axis_vects[1,:], angles[1])        
        self.v7 = self.rotxyz(_v7, self.axis_vects[0,:], angles[0])
        
        #----------------  Conversion back to Euler angles  -------------------#
        rmatrix = np.concatenate((self.v5,self.v6,self.v7),0)
        rmatrix[np.where(np.abs(rmatrix)<0.0000001)] = 0
        alpha, beta, gamma = self.rotationMatrixToEulerZYX(rmatrix)
        self.al_be_gam = np.array([[alpha,beta,gamma]])
        self.position = self.v4-self._t_off+new_centre
                #----------------------------------------------------------------------# 
        #return np.concatenate((self.v0, self.v1,self.v2,self.v3,self.v4,self.v5,self.v6,self.v7,self.position,self.al_be_gam),0)
        return np.concatenate((self.position,self.al_be_gam),0)
           
    def i_kinematics(self,target):
        #solutions=np.array([[]]*6).T
        solutions=np.zeros((6))
        #valid_solutions = np.array([[]]*6).T
        valid_solutions = np.zeros((6))
        self.target = target
        flip = 0
        L1 = np.linalg.norm(self.L_vects[1,:])
        L2 = np.linalg.norm(self.L_vects[2,:]+self.L_vects[3,:])
        v0 = self.target[0,:]
        v1 = self.target[1,:]
        v2 = self.target[2,:]
        v3 = self.target[3,:]
        new_offset = np.dot(np.array([self.centre_offset]),self.target[1:,:])[0]
        v0 = v0 - new_offset
        
        vlength = (np.linalg.norm(self.L_vects[4,:]))
        vc1 = (v0-(v3/np.linalg.norm(v3)*vlength))-self.L_vects[0,:] # Calculate the origin of L4
        vc1n = np.linalg.norm(vc1)
        theta0check = np.arctan2(vc1[1],vc1[0])
#        t_v3_check = np.arctan2(target[3,1],target[3,0])
        #-------------------  To prevent the arm bending backwards ------------#
#        if (theta0check-t_v3_check)-np.pi < (theta0check-(t_v3_check+np.pi))-(2*np.pi):
        
        num_checks = 8
        keep_index = np.zeros((8,2))
        for ii in list(range(num_checks)):
            if ii == 0 or ii == 4:
                theta0 = theta0check
                theta1 = np.arccos((L1**2+vc1n**2-L2**2)/(2*L1*vc1n)) # law of cosines
                theta2 = np.pi-np.arccos((L1**2+L2**2-vc1n**2)/(2*L1*L2)) # law of cosines
                theta2 = theta2-(self.vp_angle((self.L_vects[3,:]+self.L_vects[2,:]),[1,0,0],[0,1,0]))
                theta1 = -theta1+self.vp_angle(vc1,[1,0,0],[0,1,0])
            elif ii ==1 or ii == 5:
                theta0 = theta0check + np.pi
                theta1 = np.arccos((L1**2+vc1n**2-L2**2)/(2*L1*vc1n)) # law of cosines
                theta2 = np.pi-np.arccos((L1**2+L2**2-vc1n**2)/(2*L1*L2)) # law of cosines
                theta2 = theta2-(self.vp_angle((self.L_vects[3,:]+self.L_vects[2,:]),[1,0,0],[0,1,0]))
                theta1 = -theta1-self.vp_angle(vc1,[1,0,0],[0,1,0])
            elif ii == 2 or ii == 6:
                theta0 = theta0check
                theta1 = -np.arccos((L1**2+vc1n**2-L2**2)/(2*L1*vc1n)) # law of cosines
                theta2 = -(np.pi-np.arccos((L1**2+L2**2-vc1n**2)/(2*L1*L2))) # law of cosines
                theta2 = theta2-(self.vp_angle((self.L_vects[3,:]+self.L_vects[2,:]),[1,0,0],[0,1,0]))
                theta1 = -theta1+self.vp_angle(vc1,[1,0,0],[0,1,0])

            elif ii == 3 or ii == 7:
                theta0 = theta0check + np.pi
                theta1 = -np.arccos((L1**2+vc1n**2-L2**2)/(2*L1*vc1n)) # law of cosines
                theta2 = -(np.pi-np.arccos((L1**2+L2**2-vc1n**2)/(2*L1*L2))) # law of cosines
                theta2 = theta2-(self.vp_angle((self.L_vects[3,:]+self.L_vects[2,:]),[1,0,0],[0,1,0]))
                theta1 = -theta1-self.vp_angle(vc1,[1,0,0],[0,1,0])
                
            # theta1 theta2 and theta3 determine position of Lvect origin
            vec3 = self.rotxyz(np.array([self.L_vects[3,:]]), np.array([self.axis_vects[2,:]]), theta2*180/np.pi)
            vec3 = self.rotxyz(vec3, self.axis_vects[1,:], theta1*180/np.pi)
            vec3 = self.rotxyz(vec3, self.axis_vects[0,:], theta0*180/np.pi)
            av3 = self.rotxyz(np.array([self.axis_vects[4,:]]), np.array([self.axis_vects[2,:]]), theta2*180/np.pi)
            av3 = self.rotxyz(av3, self.axis_vects[1,:], theta1*180/np.pi)
            av3 = self.rotxyz(av3, self.axis_vects[0,:], theta0*180/np.pi)
        
            if np.abs(np.dot(np.array(av3)[0],v3))>0.001: # To check that av3 is not already orthoganol to v3
                theta3i = self.vp_angle(np.array(av3)[0],np.array(v3),np.array(vec3)[0])
                if ii < 4:
#                if theta3i < np.pi/2: 
                    theta3 = ((self.vp_angle(np.array(av3)[0],np.array(v3),np.array(vec3)[0])))
                elif theta3i > np.pi/2:
                    theta3 = -((self.vp_angle(np.array(av3)[0],np.array(vec3)[0],np.array(v3))))     
            else:
                theta3 = 0
           
            theta3 =-np.sign(np.dot(np.array(av3)[0],np.array(v3)))*theta3
            vec4 = self.rotxyz(np.array([self.L_vects[4,:]]), np.array([self.axis_vects[3,:]]), theta3*180/np.pi)
            vec4 = self.rotxyz(vec4, self.axis_vects[2,:], theta2*180/np.pi)
            vec4 = self.rotxyz(vec4, self.axis_vects[1,:], theta1*180/np.pi)
            vec4 = self.rotxyz(vec4, self.axis_vects[0,:], theta0*180/np.pi)
            theta4 = self.vanglev(v3,np.array(vec4)[0])

            vec5 = self.rotxyz(np.array([self.L_vects[5,:]]), np.array([self.axis_vects[4,:]]), theta4*180/np.pi)
            vec5 = self.rotxyz(vec5, self.axis_vects[3,:], theta3*180/np.pi)
            vec5 = self.rotxyz(vec5, self.axis_vects[2,:], theta2*180/np.pi)
            vec5 = self.rotxyz(vec5, self.axis_vects[1,:], theta1*180/np.pi)
            vec5 = self.rotxyz(vec5, self.axis_vects[0,:], theta0*180/np.pi)
            theta4_check = np.abs(self.vanglev(v3,np.array(vec5)[0])-np.pi/2)
            if theta4_check > 0.000001:
                theta4 = -self.vanglev(v3,np.array(vec4)[0])
                
            vec5 = self.rotxyz(np.array([self.L_vects[5,:]]), np.array([self.axis_vects[4,:]]), theta4*180/np.pi)
            vec5 = self.rotxyz(vec5, self.axis_vects[3,:], theta3*180/np.pi)
            vec5 = self.rotxyz(vec5, self.axis_vects[2,:], theta2*180/np.pi)
            vec5 = self.rotxyz(vec5, self.axis_vects[1,:], theta1*180/np.pi)
            vec5 = self.rotxyz(vec5, self.axis_vects[0,:], theta0*180/np.pi)
            theta5 = -self.vanglev(v1,np.array(vec5)[0])
            vec5 = self.rotxyz(np.array([self.L_vects[5,:]]), np.array([self.axis_vects[5,:]]), theta5*180/np.pi)
            vec5 = self.rotxyz(vec5, self.axis_vects[4,:], theta4*180/np.pi)    
            vec5 = self.rotxyz(vec5, self.axis_vects[3,:], theta3*180/np.pi)
            vec5 = self.rotxyz(vec5, self.axis_vects[2,:], theta2*180/np.pi)
            vec5 = self.rotxyz(vec5, self.axis_vects[1,:], theta1*180/np.pi)
            vec5 = self.rotxyz(vec5, self.axis_vects[0,:], theta0*180/np.pi)
            if np.abs(self.vanglev(v1,np.array(vec5)[0]))>0.01:
                theta5 = -theta5

            vec5 = self.rotxyz(np.array([self.L_vects[5,:]]), np.array([self.axis_vects[5,:]]), theta5*180/np.pi)
            vec5 = self.rotxyz(vec5, self.axis_vects[4,:], theta4*180/np.pi)    
            vec5 = self.rotxyz(vec5, self.axis_vects[3,:], theta3*180/np.pi)
            vec5 = self.rotxyz(vec5, self.axis_vects[2,:], theta2*180/np.pi)
            vec5 = self.rotxyz(vec5, self.axis_vects[1,:], theta1*180/np.pi)
            vec5 = self.rotxyz(vec5, self.axis_vects[0,:], theta0*180/np.pi)
            if np.abs(self.vanglev(v1,np.array(vec5)[0]))>0.01:
                theta5 = self.vanglev(v1,np.array(vec5)[0])+np.pi

            if np.isnan(theta5):
                theta5 = 0
            #set angular range between -180 and 180
            theta0 = (np.mod(theta0+np.pi,2*np.pi)-np.pi)
            theta1 = (np.mod(theta1+np.pi,2*np.pi)-np.pi)
            theta2 = (np.mod(theta2+np.pi,2*np.pi)-np.pi)
            theta3 = (np.mod(theta3+np.pi,2*np.pi)-np.pi)
            theta4 = (np.mod(theta4+np.pi,2*np.pi)-np.pi)
            theta5 = (np.mod(theta5+np.pi,2*np.pi)-np.pi)
            output = np.array([theta0*180/np.pi, theta1*180/np.pi, theta2*180/np.pi,theta3*180/np.pi,theta4*180/np.pi,theta5*180/np.pi])
            solutions = np.vstack([solutions,output])


        solutions = solutions - self.motor_offsets
        self.solutions = solutions[1:,:]
        solutions = solutions[1:,:]
        #----------------------------------------------------------------------#
        #      Check all motors are within their respective limits
        #----------------------------------------------------------------------#
        
        for iii in list(range(int(num_checks))):
            if np.where(self.motor_limits.T[0,:]<=solutions[iii,:])[0].shape[0] == 6:
                keep_index[iii,0] = 1
            if np.where(self.motor_limits.T[1,:]>=solutions[iii,:])[0].shape[0] == 6:
                keep_index[iii,1] = 1       

        for iii in list(range(num_checks)):
            if keep_index[iii,0]*keep_index[iii,1] == 1:
                valid_solutions = np.vstack([valid_solutions,solutions[iii,:]])
        valid_solutions = valid_solutions[1:,:]
        current_position = np.array([0,0,0,0,0,0])
        
        if valid_solutions.shape[0] < 1:
            best_solution = current_position
            print('No solution within limits')
        else:
            #------------------------------------------------------------------#
            #                      Solution strategy
            #-------------------------------------------------------------------
            if self.strategy == 'minimum_movement':
                comparator = np.sum(valid_solutions-current_position,1)
                best_solution = valid_solutions[np.argmin(comparator)]
                
            if self.strategy == 'minimum_movement_weighted':
                comparator = np.sum((valid_solutions-current_position)*self.weighting,1)
                best_solution = valid_solutions[np.argmin(comparator)]

            elif self.strategy == 'comfortable_limits':
                limit_centres = np.mean(self.motor_limits,1)
                comparator = np.sum(np.abs(limit_centres-valid_solutions),1)
                best_solution = valid_solutions[np.argmin(comparator)] 

        return best_solution

#----------------------------------------------------------------------#
#                       Define Robot Geometry
#----------------------------------------------------------------------#

v0 = np.array([0,0,135.0])
v1 = np.array([0,0,270.0])
v2 = np.array([0.0,0,341.5])
v3 = np.array([31.26,0,391.5])
v4 = np.array([31.26,0,460.22])
v5 = np.array([1,0,0])
v6 = np.array([0,1,0])
v7 = np.array([0,0,1])
L_vects = np.array([v0, (v1-v0), (v2-v1), (v3-v2), (v4-v3), v5, v6, v7])
L_vects[1,:] =  L_vects[1,:]*(1+-0.0099)
L_vects[2,:] =  L_vects[2,:]*(1+0.0019)
L_vects[3,:] =  L_vects[3,:]*(1+0.0078)
L_vects[4,:] =  L_vects[4,:]*(1+0.0094)
ax3=v3-v2
axis_vects = np.array([[0,0,1],[0,1,0],[0,1,0],ax3,[0,1,0],[0,0,1]]) # make sure v4 is consistent with ax4 rotation offset
motor_offsets = (0,0,58,0,32,0)

# motor_limits = np.array([[-175, 175],[-70, 90],[-135, 70],[-170, 170],[-115, 115],[-3600, 3600]])
motor_limits = np.array([[-175, 175],[-70, 90],[-90, 70],[-170, 170],[-90, 115],[-3600, 3600]])

tool_offset = [0,0,-15.28000]
L3_angle_offset = 32
strategy = 'minimum_movement_weighted'
weighting = [6,5,4,3,2,1]
centre_offset = [0, 0.8, 0]
initial_rotations = np.array([[0,0,0],
                                [0,0,0],
                                [0,0,0],
                                [0,32*np.pi/180,0],
                                [0,0,0],
                                [0,0,0]])
constraint = 'eta'
kin = kinematics(axis_vects,L_vects,motor_limits,motor_offsets,tool_offset,centre_offset,strategy,weighting,constraint)
#----------------------------------------------------------------------#
# 
class robotArmClass(ScannableMotionBase):
    '''Device to control the Meca 500 robot arm.'''
    def __init__(self,name,arm,help=None):
            self.setName(name)
            if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
            # self.setInputNames([name])
            self.setInputNames(['rx','ry', 'rz','ralpha','rbeta','rgamma'])
            self.setOutputFormat(['%4.5f', '%4.5f','%4.5f','%4.5f','%4.5f','%4.5f'])
            self.Units=['mixed']
            self.setLevel(5)
            self.arm=arm
            self.channel = 'BL16I-MO-ROBOT-01:'
    def setSpeed(self,speed):
        '''Speed is set as a percentage. 10 is a good value'''
        CAClient.put(self.channel+'JOINTVEL:SET',speed)
        
    def getPositionRaw(self):
        arm = [CAClient.get(self.channel+'JOINTS:THETA1:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA2:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA3:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA4:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA5:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA6:RBV')]
        return arm
    
    def pos_raw_motors(self,values):
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',1)
        sleep(0.1)
        CAClient.put(self.channel+'JOINTS:THETA1:SP',values[0])
        CAClient.put(self.channel+'JOINTS:THETA2:SP',values[1])
        CAClient.put(self.channel+'JOINTS:THETA3:SP',values[2])
        CAClient.put(self.channel+'JOINTS:THETA4:SP',values[3])
        CAClient.put(self.channel+'JOINTS:THETA5:SP',values[4])
        CAClient.put(self.channel+'JOINTS:THETA6:SP',values[5])
        CAClient.put(self.channel+'PREPARE_MOVE_JOINTS_ARRAY.PROC',1)

    def pos_xyz_and_euler(self,values):
        _x = values[0]
        _y = values[1]
        _z = values[2]
        r_alpha = values[3]
        r_beta = values[4]
        r_gamma = values[5]
        motor_values = kin.setEulerTarget(_x,_y,_z,r_alpha,r_beta,r_gamma)
        self.pos_raw_motors(motor_values)

    def pos_mu_eta_chi_phi(self,values):
        mu=values[0]
        eta=values[1]
        chi=values[2]
        phi=values[3]
        current_VM_values = self.getPosition()
        r_alpha, r_beta, r_gamma = kin.set_mu_eta_chi_phi(mu, eta, chi, phi)
        motor_values = kin.setEulerTarget(current_VM_values[0],current_VM_values[1],current_VM_values[2],r_alpha,r_beta,r_gamma)
        self.pos_raw_motors(motor_values)
    
    def get_mu_eta_chi_phi(self):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        values = kin.get_mu_eta_chi_phi(v_motors[3],v_motors[4],v_motors[5])
        return values
    
    def pos_txyz(self,offsets):
        current_position = self.getPosition()
        kin.setToolOffset(offsets)
        motor_values = kin.setEulerTarget(current_position[0],current_position[1],current_position[2],current_position[3],current_position[4],current_position[5])
        self.pos_raw_motors(motor_values)
        
        
    def asynchronousMoveTo(self,values):

        values = np.asarray(values)
        
        _x = values[0]
        _y = values[1]
        _z = values[2]
        r_alpha = values[3]
        r_beta = values[4]
        r_gamma = values[5]
        motor_values = kin.setEulerTarget(_x,_y,_z,r_alpha,r_beta,r_gamma)
        self.pos_raw_motors(motor_values)
    
    def getPosition(self):
        raw_motors = self.getPositionRaw() 
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        return v_motors.tolist()
    
    def isBusy(self):
        sleep(0.2)
        loopcheck = 0
        while CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0' and CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY' and loopcheck < 10:
            loopcheck+=1
            sleep(0.1)
        if CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0':
            CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        return CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY'

    def stop(self):
        CAClient.put(self.channel+'MOTION:ABORT',1)
        CAClient.put(self.channel+'MOTION:RESUME',1)
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)

class robotArmClassRaw(ScannableMotionBase):
    '''Device to control the Meca 500 robot arm.'''
    def __init__(self,name,arm,help=None):
            self.setName(name)
            if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
            self.setInputNames([name])
            self.setOutputFormat(['%4.5f', '%4.5f','%4.5f','%4.5f','%4.5f','%4.5f'])
            self.Units=['deg']
            self.setLevel(5)
            self.arm=kin.solutions[0]
            self.channel = 'BL16I-MO-ROBOT-01:'
    def setSpeed(self,speed):
        '''Speed is set as a percentage. 10 is a good value'''
        CAClient.put(self.channel+'JOINTVEL:SET',speed)
    
    def asynchronousMoveTo(self,values):
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',1)
        sleep(0.1)
        CAClient.put(self.channel+'JOINTS:THETA1:SP',values[0])
        CAClient.put(self.channel+'JOINTS:THETA2:SP',values[1])
        CAClient.put(self.channel+'JOINTS:THETA3:SP',values[2])
        CAClient.put(self.channel+'JOINTS:THETA4:SP',values[3])
        CAClient.put(self.channel+'JOINTS:THETA5:SP',values[4])
        CAClient.put(self.channel+'JOINTS:THETA6:SP',values[5])
        CAClient.put(self.channel+'PREPARE_MOVE_JOINTS_ARRAY.PROC',1)
    
    def getPosition(self):
        arm = [CAClient.get(self.channel+'JOINTS:THETA1:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA2:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA3:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA4:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA5:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA6:RBV')]

        return np.array(arm)
    
    def isBusy(self):
        sleep(0.2)
        loopcheck = 0
        while CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0' and CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY' and loopcheck < 10:
            loopcheck+=1
            sleep(0.1)
        if CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0':
            CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        return CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY'

    def stop(self):
        CAClient.put(self.channel+'MOTION:ABORT',1)
        CAClient.put(self.channel+'MOTION:RESUME',1)
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)



class rMuEtaChiPhiClass(robotArmClass):
    '''Device to control the Meca 500 robot arm.'''
    def __init__(self,name, help=None):
            self.setName(name)
            if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
            self.setInputNames(['rmu','reta','rchi','rphi'])
            self.setExtraNames(['rm1','rm2','rm3','rm4','rm5','rm6'])
            self.setOutputFormat(['%4.5f','%4.5f','%4.5f','%4.5f','%4.5f','%4.5f','%4.5f','%4.5f','%4.5f','%4.5f'])
            self.setLevel(5)
            self.channel = 'BL16I-MO-ROBOT-01:'

    def asynchronousMoveTo(self,values):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        current_mu_eta_chi_phi = kin.get_mu_eta_chi_phi(v_motors[3],v_motors[4],v_motors[5])
        r_alpha, r_beta, r_gamma = kin.set_mu_eta_chi_phi(values[0], values[1],values[2], values[3])
        motor_values = kin.setEulerTarget(v_motors[0],v_motors[1],v_motors[2],r_alpha,r_beta,r_gamma)
        self.pos_raw_motors(motor_values)

    def getPosition(self):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        diff_motors = kin.get_mu_eta_chi_phi(v_motors[3],v_motors[4],v_motors[5])
        return list(diff_motors)+raw_motors



class rMuClass(ScannableMotionBase):
    '''Device to control the Meca 500 robot arm.'''
    def __init__(self,name,help=None):
            self.setName(name)
            if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
            self.setInputNames([name])
            self.setOutputFormat(['%4.5f'])
            self.Units=['deg']
            self.setLevel(5)
            self.channel = 'BL16I-MO-ROBOT-01:'

    def getPositionRaw(self):
        arm = [CAClient.get(self.channel+'JOINTS:THETA1:SP'),
               CAClient.get(self.channel+'JOINTS:THETA2:SP'),
               CAClient.get(self.channel+'JOINTS:THETA3:SP'),
               CAClient.get(self.channel+'JOINTS:THETA4:SP'),
               CAClient.get(self.channel+'JOINTS:THETA5:SP'),
               CAClient.get(self.channel+'JOINTS:THETA6:SP')]
        return arm
    def pos_raw_motors(self,values):
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',1)
        sleep(0.1)
        CAClient.put(self.channel+'JOINTS:THETA1:SP',values[0])
        CAClient.put(self.channel+'JOINTS:THETA2:SP',values[1])
        CAClient.put(self.channel+'JOINTS:THETA3:SP',values[2])
        CAClient.put(self.channel+'JOINTS:THETA4:SP',values[3])
        CAClient.put(self.channel+'JOINTS:THETA5:SP',values[4])
        CAClient.put(self.channel+'JOINTS:THETA6:SP',values[5])
        CAClient.put(self.channel+'PREPARE_MOVE_JOINTS_ARRAY.PROC',1)

    def asynchronousMoveTo(self,muval):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        current_mu_eta_chi_phi = kin.get_mu_eta_chi_phi(v_motors[3],v_motors[4],v_motors[5])
        r_alpha, r_beta, r_gamma = kin.set_mu_eta_chi_phi(muval, current_mu_eta_chi_phi[1],current_mu_eta_chi_phi[2], current_mu_eta_chi_phi[3])
        motor_values = kin.setEulerTarget(v_motors[0],v_motors[1],v_motors[2],r_alpha,r_beta,r_gamma)
        self.pos_raw_motors(motor_values)

    def getPosition(self):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        values = kin.get_mu_eta_chi_phi(v_motors[3],v_motors[4],v_motors[5])
        return float(values[0])
    
    def isBusy(self):
        sleep(0.2)
        loopcheck = 0
        while CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0' and CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY' and loopcheck < 10:
            loopcheck+=1
            sleep(0.1)
        if CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0':
            CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        return CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY'

    def stop(self):
        CAClient.put(self.channel+'MOTION:ABORT',1)
        CAClient.put(self.channel+'MOTION:RESUME',1)
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)

class rEtaClass(ScannableMotionBase):
    '''Device to control the Meca 500 robot arm.'''
    def __init__(self,name,help=None):
            self.setName(name)
            if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
            self.setInputNames([name])
            self.setOutputFormat(['%4.5f'])
            self.Units=['deg']
            self.setLevel(5)
            self.channel = 'BL16I-MO-ROBOT-01:'
            self.scanningState = False
    def getPositionRaw(self):
        arm = [CAClient.get(self.channel+'JOINTS:THETA1:SP'),
               CAClient.get(self.channel+'JOINTS:THETA2:SP'),
               CAClient.get(self.channel+'JOINTS:THETA3:SP'),
               CAClient.get(self.channel+'JOINTS:THETA4:SP'),
               CAClient.get(self.channel+'JOINTS:THETA5:SP'),
               CAClient.get(self.channel+'JOINTS:THETA6:SP')]
        return arm
    def pos_raw_motors(self,values):
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',1)
        sleep(0.1)
        CAClient.put(self.channel+'JOINTS:THETA1:SP',values[0])
        CAClient.put(self.channel+'JOINTS:THETA2:SP',values[1])
        CAClient.put(self.channel+'JOINTS:THETA3:SP',values[2])
        CAClient.put(self.channel+'JOINTS:THETA4:SP',values[3])
        CAClient.put(self.channel+'JOINTS:THETA5:SP',values[4])
        CAClient.put(self.channel+'JOINTS:THETA6:SP',values[5])
        CAClient.put(self.channel+'PREPARE_MOVE_JOINTS_ARRAY.PROC',1)

    def asynchronousMoveTo(self,etaval):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        current_mu_eta_chi_phi = kin.get_mu_eta_chi_phi(v_motors[3],v_motors[4],v_motors[5])
        r_alpha, r_beta, r_gamma = kin.set_mu_eta_chi_phi(current_mu_eta_chi_phi[0], etaval, current_mu_eta_chi_phi[2], current_mu_eta_chi_phi[3])
        motor_values = kin.setEulerTarget(v_motors[0],v_motors[1],v_motors[2],r_alpha,r_beta,r_gamma)
        self.pos_raw_motors(motor_values)

    def getPosition(self):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        values = kin.get_mu_eta_chi_phi(v_motors[3],v_motors[4],v_motors[5])
        return float(values[1])

    def isBusy(self):
        sleep(0.2)
        loopcheck = 0
        while CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0' and CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY' and loopcheck < 10:
            loopcheck+=1
            sleep(0.1)
        if CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0':
            CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        return CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY'

    def atScanStart(self):
        self.scanningState = True
        self.kick()
        
    def kick(self):
        print('kick turned off')
        # raw_motors = self.getPositionRaw()
        # raw_motors[0] = float(raw_motors[0])-0.2
        # raw_motors[1] = float(raw_motors[1])-0.2
        # raw_motors[2] = float(raw_motors[2])-0.2
        # raw_motors[3] = float(raw_motors[3])-0.2
        # raw_motors[4] = float(raw_motors[4])-0.2
        # raw_motors[5] = float(raw_motors[5])-0.2
        # self.pos_raw_motors(raw_motors)
        # sleep(0.2)
        # raw_motors = self.getPositionRaw()
        # raw_motors[0] = float(raw_motors[0])+0.2
        # raw_motors[1] = float(raw_motors[1])+0.2
        # raw_motors[2] = float(raw_motors[2])+0.2
        # raw_motors[3] = float(raw_motors[3])+0.2
        # raw_motors[4] = float(raw_motors[4])+0.2
        # raw_motors[5] = float(raw_motors[5])+0.2
        # self.pos_raw_motors(raw_motors)
        
    def atLevelStart(self):
        if not self.scanningState:
            self.kick()
            
    def atScanEnd(self):
        self.scanningState = False
    
    def atCommandFailure(self):
        self.scanningState = False
    
    def stop(self):
        CAClient.put(self.channel+'MOTION:ABORT',1)
        CAClient.put(self.channel+'MOTION:RESUME',1)
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)

class rChiClass(ScannableMotionBase):
    '''Device to control the Meca 500 robot arm.'''
    def __init__(self,name,help=None):
            self.setName(name)
            if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
            self.setInputNames([name])
            self.setOutputFormat(['%4.5f'])
            self.Units=['deg']
            self.setLevel(5)
            self.channel = 'BL16I-MO-ROBOT-01:'

    def getPositionRaw(self):
        arm = [CAClient.get(self.channel+'JOINTS:THETA1:SP'),
               CAClient.get(self.channel+'JOINTS:THETA2:SP'),
               CAClient.get(self.channel+'JOINTS:THETA3:SP'),
               CAClient.get(self.channel+'JOINTS:THETA4:SP'),
               CAClient.get(self.channel+'JOINTS:THETA5:SP'),
               CAClient.get(self.channel+'JOINTS:THETA6:SP')]
        return arm
    def pos_raw_motors(self,values):
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',1)
        sleep(0.1)
        CAClient.put(self.channel+'JOINTS:THETA1:SP',values[0])
        CAClient.put(self.channel+'JOINTS:THETA2:SP',values[1])
        CAClient.put(self.channel+'JOINTS:THETA3:SP',values[2])
        CAClient.put(self.channel+'JOINTS:THETA4:SP',values[3])
        CAClient.put(self.channel+'JOINTS:THETA5:SP',values[4])
        CAClient.put(self.channel+'JOINTS:THETA6:SP',values[5])
        CAClient.put(self.channel+'PREPARE_MOVE_JOINTS_ARRAY.PROC',1)

    def asynchronousMoveTo(self,chival):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        current_mu_eta_chi_phi = kin.get_mu_eta_chi_phi(v_motors[3],v_motors[4],v_motors[5])
        r_alpha, r_beta, r_gamma = kin.set_mu_eta_chi_phi(current_mu_eta_chi_phi[0], current_mu_eta_chi_phi[1], chival, current_mu_eta_chi_phi[3])
        motor_values = kin.setEulerTarget(v_motors[0],v_motors[1],v_motors[2],r_alpha,r_beta,r_gamma)
        self.pos_raw_motors(motor_values)
        # while CAClient.get(self.channel+'ROBOT:STATUS:EOM')!='1.0' and busycheck < 20:
        #     sleep(0.1)
        #     busycheck += 1
        

    def getPosition(self):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        values = kin.get_mu_eta_chi_phi(v_motors[3],v_motors[4],v_motors[5])
        return float(values[2])

    def isBusy(self):
        sleep(0.2)
        loopcheck = 0
        while CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0' and CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY' and loopcheck < 10:
            loopcheck+=1
            sleep(0.1)
        if CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0':
            CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        return CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY'

    def stop(self):
        CAClient.put(self.channel+'MOTION:ABORT',1)
        CAClient.put(self.channel+'MOTION:RESUME',1)
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        
class rPhiClass(ScannableMotionBase):
    '''Device to control the Meca 500 robot arm.'''
    def __init__(self,name,help=None):
            self.setName(name)
            if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
            self.setInputNames([name])
            self.setOutputFormat(['%4.5f'])
            self.Units=['deg']
            self.setLevel(5)
            self.channel = 'BL16I-MO-ROBOT-01:'

    def getPositionRaw(self):
        arm = [CAClient.get(self.channel+'JOINTS:THETA1:SP'),
               CAClient.get(self.channel+'JOINTS:THETA2:SP'),
               CAClient.get(self.channel+'JOINTS:THETA3:SP'),
               CAClient.get(self.channel+'JOINTS:THETA4:SP'),
               CAClient.get(self.channel+'JOINTS:THETA5:SP'),
               CAClient.get(self.channel+'JOINTS:THETA6:SP')]
        return arm
    def pos_raw_motors(self,values):
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',1)
        sleep(0.1)
        CAClient.put(self.channel+'JOINTS:THETA1:SP',values[0])
        CAClient.put(self.channel+'JOINTS:THETA2:SP',values[1])
        CAClient.put(self.channel+'JOINTS:THETA3:SP',values[2])
        CAClient.put(self.channel+'JOINTS:THETA4:SP',values[3])
        CAClient.put(self.channel+'JOINTS:THETA5:SP',values[4])
        CAClient.put(self.channel+'JOINTS:THETA6:SP',values[5])
        CAClient.put(self.channel+'PREPARE_MOVE_JOINTS_ARRAY.PROC',1)

    def asynchronousMoveTo(self,phival):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        current_mu_eta_chi_phi = kin.get_mu_eta_chi_phi(v_motors[3],v_motors[4],v_motors[5])
        r_alpha, r_beta, r_gamma = kin.set_mu_eta_chi_phi(current_mu_eta_chi_phi[0], current_mu_eta_chi_phi[1], current_mu_eta_chi_phi[2], phival)
        motor_values = kin.setEulerTarget(v_motors[0],v_motors[1],v_motors[2],r_alpha,r_beta,r_gamma)
        self.pos_raw_motors(motor_values)

    def getPosition(self):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        values = kin.get_mu_eta_chi_phi(v_motors[3],v_motors[4],v_motors[5])
        return float(values[3])

    def isBusy(self):
        sleep(0.2)
        loopcheck = 0
        while CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0' and CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY' and loopcheck < 10:
            loopcheck+=1
            sleep(0.1)
        if CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0':
            CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        return CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY'

    def stop(self):
        CAClient.put(self.channel+'MOTION:ABORT',1)
        CAClient.put(self.channel+'MOTION:RESUME',1)
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)

class ralphaClass(ScannableMotionBase):
    '''Device to control the Meca 500 robot arm.'''
    def __init__(self,name,help=None):
            self.setName(name)
            if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
            self.setInputNames([name])
            self.setOutputFormat(['%4.5f'])
            self.Units=['deg']
            self.setLevel(5)
            self.channel = 'BL16I-MO-ROBOT-01:'

    def getPositionRaw(self):
        arm = [CAClient.get(self.channel+'JOINTS:THETA1:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA2:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA3:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA4:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA5:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA6:RBV')]
        return arm
    
    def pos_raw_motors(self,values):
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',1)
        sleep(0.1)
        CAClient.put(self.channel+'JOINTS:THETA1:SP',values[0])
        CAClient.put(self.channel+'JOINTS:THETA2:SP',values[1])
        CAClient.put(self.channel+'JOINTS:THETA3:SP',values[2])
        CAClient.put(self.channel+'JOINTS:THETA4:SP',values[3])
        CAClient.put(self.channel+'JOINTS:THETA5:SP',values[4])
        CAClient.put(self.channel+'JOINTS:THETA6:SP',values[5])
        CAClient.put(self.channel+'PREPARE_MOVE_JOINTS_ARRAY.PROC',1)

    def asynchronousMoveTo(self,alpha):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        motor_values = kin.setEulerTarget(v_motors[0],v_motors[1],v_motors[2],alpha,v_motors[4],v_motors[5])
        self.pos_raw_motors(motor_values)


    def getPosition(self):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        return v_motors[3]

    def isBusy(self):
        sleep(0.2)
        loopcheck = 0
        while CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0' and CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY' and loopcheck < 10:
            loopcheck+=1
            sleep(0.1)
        if CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0':
            CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        return CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY'

    def stop(self):
        CAClient.put(self.channel+'MOTION:ABORT',1)
        CAClient.put(self.channel+'MOTION:RESUME',1)
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
    
class rbetaClass(ScannableMotionBase):
    '''Device to control the Meca 500 robot arm.'''
    def __init__(self,name,help=None):
            self.setName(name)
            if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
            self.setInputNames([name])
            self.setOutputFormat(['%4.5f'])
            self.Units=['deg']
            self.setLevel(5)
            self.channel = 'BL16I-MO-ROBOT-01:'

    def getPositionRaw(self):
        arm = [CAClient.get(self.channel+'JOINTS:THETA1:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA2:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA3:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA4:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA5:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA6:RBV')]
        return arm
    
    def pos_raw_motors(self,values):
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',1)
        sleep(0.1)
        CAClient.put(self.channel+'JOINTS:THETA1:SP',values[0])
        CAClient.put(self.channel+'JOINTS:THETA2:SP',values[1])
        CAClient.put(self.channel+'JOINTS:THETA3:SP',values[2])
        CAClient.put(self.channel+'JOINTS:THETA4:SP',values[3])
        CAClient.put(self.channel+'JOINTS:THETA5:SP',values[4])
        CAClient.put(self.channel+'JOINTS:THETA6:SP',values[5])
        CAClient.put(self.channel+'PREPARE_MOVE_JOINTS_ARRAY.PROC',1)

    def asynchronousMoveTo(self,beta):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        motor_values = kin.setEulerTarget(v_motors[0],v_motors[1],v_motors[2], v_motors[3], beta ,v_motors[5])
        self.pos_raw_motors(motor_values)

    def getPosition(self):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        return v_motors[4]

    def isBusy(self):
        sleep(0.2)
        loopcheck = 0
        while CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0' and CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY' and loopcheck < 10:
            loopcheck+=1
            sleep(0.1)
        if CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0':
            CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        return CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY'

    def stop(self):
        CAClient.put(self.channel+'MOTION:ABORT',1)
        CAClient.put(self.channel+'MOTION:RESUME',1)
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)

class rgammaClass(ScannableMotionBase):
    '''Device to control the Meca 500 robot arm.'''
    def __init__(self,name,help=None):
            self.setName(name)
            if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
            self.setInputNames([name])
            self.setOutputFormat(['%4.5f'])
            self.Units=['deg']
            self.setLevel(5)
            self.channel = 'BL16I-MO-ROBOT-01:'

    def getPositionRaw(self):
        arm = [CAClient.get(self.channel+'JOINTS:THETA1:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA2:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA3:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA4:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA5:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA6:RBV')]
        return arm
    
    def pos_raw_motors(self,values):
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',1)
        sleep(0.1)
        CAClient.put(self.channel+'JOINTS:THETA1:SP',values[0])
        CAClient.put(self.channel+'JOINTS:THETA2:SP',values[1])
        CAClient.put(self.channel+'JOINTS:THETA3:SP',values[2])
        CAClient.put(self.channel+'JOINTS:THETA4:SP',values[3])
        CAClient.put(self.channel+'JOINTS:THETA5:SP',values[4])
        CAClient.put(self.channel+'JOINTS:THETA6:SP',values[5])
        CAClient.put(self.channel+'PREPARE_MOVE_JOINTS_ARRAY.PROC',1)

    def asynchronousMoveTo(self,gamma):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        motor_values = kin.setEulerTarget(v_motors[0],v_motors[1],v_motors[2],v_motors[3],v_motors[4],gamma)
        self.pos_raw_motors(motor_values)

    def getPosition(self):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        return v_motors[5]

    def isBusy(self):
        sleep(0.2)
        loopcheck = 0
        while CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0' and CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY' and loopcheck < 10:
            loopcheck+=1
            sleep(0.1)
        if CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0':
            CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        return CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY'

    def stop(self):
        CAClient.put(self.channel+'MOTION:ABORT',1)
        CAClient.put(self.channel+'MOTION:RESUME',1)
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)




class rXClass(ScannableMotionBase):
    '''Device to control the Meca 500 robot arm.'''
    def __init__(self,name,help=None):
            self.setName(name)
            if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
            self.setInputNames([name])
            self.setOutputFormat(['%4.5f'])
            self.Units=['mm']
            self.setLevel(5)
            self.channel = 'BL16I-MO-ROBOT-01:'

    def getPositionRaw(self):
        arm = [CAClient.get(self.channel+'JOINTS:THETA1:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA2:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA3:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA4:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA5:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA6:RBV')]
        return arm
    
    def pos_raw_motors(self,values):
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',1)
        sleep(0.1)
        CAClient.put(self.channel+'JOINTS:THETA1:SP',values[0])
        CAClient.put(self.channel+'JOINTS:THETA2:SP',values[1])
        CAClient.put(self.channel+'JOINTS:THETA3:SP',values[2])
        CAClient.put(self.channel+'JOINTS:THETA4:SP',values[3])
        CAClient.put(self.channel+'JOINTS:THETA5:SP',values[4])
        CAClient.put(self.channel+'JOINTS:THETA6:SP',values[5])
        CAClient.put(self.channel+'PREPARE_MOVE_JOINTS_ARRAY.PROC',1)

    def asynchronousMoveTo(self,x):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        motor_values = kin.setEulerTarget(x,v_motors[1],v_motors[2],v_motors[3],v_motors[4],v_motors[5])
        self.pos_raw_motors(motor_values)
        busycheck = 0

    def getPosition(self):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        return v_motors[0]

    def isBusy(self):
        sleep(0.2)
        loopcheck = 0
        while CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0' and CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY' and loopcheck < 10:
            loopcheck+=1
            sleep(0.1)
        if CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0':
            CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        return CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY'

    def stop(self):
        CAClient.put(self.channel+'MOTION:ABORT',1)
        CAClient.put(self.channel+'MOTION:RESUME',1)
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)

class rYClass(ScannableMotionBase):
    '''Device to control the Meca 500 robot arm.'''
    def __init__(self,name,help=None):
            self.setName(name)
            if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
            self.setInputNames([name])
            self.setOutputFormat(['%4.5f'])
            self.Units=['mm']
            self.setLevel(5)
            self.channel = 'BL16I-MO-ROBOT-01:'

    def getPositionRaw(self):
        arm = [CAClient.get(self.channel+'JOINTS:THETA1:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA2:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA3:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA4:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA5:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA6:RBV')]
        return arm
    def pos_raw_motors(self,values):
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',1)
        sleep(0.1)
        CAClient.put(self.channel+'JOINTS:THETA1:SP',values[0])
        CAClient.put(self.channel+'JOINTS:THETA2:SP',values[1])
        CAClient.put(self.channel+'JOINTS:THETA3:SP',values[2])
        CAClient.put(self.channel+'JOINTS:THETA4:SP',values[3])
        CAClient.put(self.channel+'JOINTS:THETA5:SP',values[4])
        CAClient.put(self.channel+'JOINTS:THETA6:SP',values[5])
        CAClient.put(self.channel+'PREPARE_MOVE_JOINTS_ARRAY.PROC',1)

    def asynchronousMoveTo(self,y):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        motor_values = kin.setEulerTarget(v_motors[0],y,v_motors[2],v_motors[3],v_motors[4],v_motors[5])
        self.pos_raw_motors(motor_values)

    def getPosition(self):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        return v_motors[1]

    def isBusy(self):
        sleep(0.2)
        loopcheck = 0
        while CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0' and CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY' and loopcheck < 10:
            loopcheck+=1
            sleep(0.1)
        if CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0':
            CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        return CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY'

    def stop(self):
        CAClient.put(self.channel+'MOTION:ABORT',1)
        CAClient.put(self.channel+'MOTION:RESUME',1)
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        
class rZClass(ScannableMotionBase):
    '''Device to control the Meca 500 robot arm.'''
    def __init__(self,name,help=None):
            self.setName(name)
            if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
            self.setInputNames([name])
            self.setOutputFormat(['%4.5f'])
            self.Units=['mm']
            self.setLevel(5)
            self.channel = 'BL16I-MO-ROBOT-01:'

    def getPositionRaw(self):
        arm = [CAClient.get(self.channel+'JOINTS:THETA1:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA2:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA3:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA4:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA5:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA6:RBV')]
        return arm
    def pos_raw_motors(self,values):
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',1)
        sleep(0.1)
        CAClient.put(self.channel+'JOINTS:THETA1:SP',values[0])
        CAClient.put(self.channel+'JOINTS:THETA2:SP',values[1])
        CAClient.put(self.channel+'JOINTS:THETA3:SP',values[2])
        CAClient.put(self.channel+'JOINTS:THETA4:SP',values[3])
        CAClient.put(self.channel+'JOINTS:THETA5:SP',values[4])
        CAClient.put(self.channel+'JOINTS:THETA6:SP',values[5])
        CAClient.put(self.channel+'PREPARE_MOVE_JOINTS_ARRAY.PROC',1)

    def asynchronousMoveTo(self,z):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        motor_values = kin.setEulerTarget(v_motors[0],v_motors[1],z,v_motors[3],v_motors[4],v_motors[5])
        self.pos_raw_motors(motor_values)
        busycheck = 0

    def getPosition(self):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        return v_motors[2]

    def isBusy(self):
        sleep(0.2)
        loopcheck = 0
        while CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0' and CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY' and loopcheck < 10:
            loopcheck+=1
            sleep(0.1)
        if CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0':
            CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        return CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY'

    def stop(self):
        CAClient.put(self.channel+'MOTION:ABORT',1)
        CAClient.put(self.channel+'MOTION:RESUME',1)
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)


class rTXClass(ScannableMotionBase):
    '''Device to control the Meca 500 robot arm.'''
    def __init__(self,name,help=None):
            self.setName(name)
            if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
            self.setInputNames([name])
            self.setOutputFormat(['%4.5f'])
            self.Units=['mm']
            self.setLevel(5)
            self.channel = 'BL16I-MO-ROBOT-01:'

    def getPositionRaw(self):
        arm = [CAClient.get(self.channel+'JOINTS:THETA1:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA2:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA3:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA4:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA5:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA6:RBV')]
        return arm
    def pos_raw_motors(self,values):
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',1)
        sleep(0.1)
        CAClient.put(self.channel+'JOINTS:THETA1:SP',values[0])
        CAClient.put(self.channel+'JOINTS:THETA2:SP',values[1])
        CAClient.put(self.channel+'JOINTS:THETA3:SP',values[2])
        CAClient.put(self.channel+'JOINTS:THETA4:SP',values[3])
        CAClient.put(self.channel+'JOINTS:THETA5:SP',values[4])
        CAClient.put(self.channel+'JOINTS:THETA6:SP',values[5])
        CAClient.put(self.channel+'PREPARE_MOVE_JOINTS_ARRAY.PROC',1)

    def asynchronousMoveTo(self,tx):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        offsets = kin.tool_offset
        offsets[0] = tx
        kin.setToolOffset(offsets)
        motor_values = kin.setEulerTarget(v_motors[0],v_motors[1],v_motors[2],v_motors[3],v_motors[4],v_motors[5])
        self.pos_raw_motors(motor_values)
        busycheck = 0

    def getPosition(self):
        offsets = kin.tool_offset
        return offsets[0]

    def isBusy(self):
        sleep(0.2)
        loopcheck = 0
        while CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0' and CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY' and loopcheck < 10:
            loopcheck+=1
            sleep(0.1)
        if CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0':
            CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        return CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY'

    def stop(self):
        CAClient.put(self.channel+'MOTION:ABORT',1)
        CAClient.put(self.channel+'MOTION:RESUME',1)
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        
class rTYClass(ScannableMotionBase):
    '''Device to control the Meca 500 robot arm.'''
    def __init__(self,name,help=None):
            self.setName(name)
            if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
            self.setInputNames([name])
            self.setOutputFormat(['%4.5f'])
            self.Units=['mm']
            self.setLevel(5)
            self.channel = 'BL16I-MO-ROBOT-01:'

    def getPositionRaw(self):
        arm = [CAClient.get(self.channel+'JOINTS:THETA1:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA2:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA3:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA4:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA5:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA6:RBV')]
        return arm
    def pos_raw_motors(self,values):
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',1)
        sleep(0.1)
        CAClient.put(self.channel+'JOINTS:THETA1:SP',values[0])
        CAClient.put(self.channel+'JOINTS:THETA2:SP',values[1])
        CAClient.put(self.channel+'JOINTS:THETA3:SP',values[2])
        CAClient.put(self.channel+'JOINTS:THETA4:SP',values[3])
        CAClient.put(self.channel+'JOINTS:THETA5:SP',values[4])
        CAClient.put(self.channel+'JOINTS:THETA6:SP',values[5])
        CAClient.put(self.channel+'PREPARE_MOVE_JOINTS_ARRAY.PROC',1)

    def asynchronousMoveTo(self,ty):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        offsets = kin.tool_offset
        offsets[1] = ty
        kin.setToolOffset(offsets)
        motor_values = kin.setEulerTarget(v_motors[0],v_motors[1],v_motors[2],v_motors[3],v_motors[4],v_motors[5])
        self.pos_raw_motors(motor_values)
        busycheck = 0

    def getPosition(self):
        offsets = kin.tool_offset
        return offsets[1]

    def isBusy(self):
        sleep(0.2)
        loopcheck = 0
        while CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0' and CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY' and loopcheck < 10:
            loopcheck+=1
            sleep(0.1)
        if CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0':
            CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        return CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY'

    def stop(self):
        CAClient.put(self.channel+'MOTION:ABORT',1)
        CAClient.put(self.channel+'MOTION:RESUME',1)
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        
class rTZClass(ScannableMotionBase):
    '''Device to control the Meca 500 robot arm.'''
    def __init__(self,name,help=None):
            self.setName(name)
            if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
            self.setInputNames([name])
            self.setOutputFormat(['%4.5f'])
            self.Units=['mm']
            self.setLevel(5)
            self.channel = 'BL16I-MO-ROBOT-01:'

    def getPositionRaw(self):
        arm = [CAClient.get(self.channel+'JOINTS:THETA1:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA2:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA3:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA4:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA5:RBV'),
               CAClient.get(self.channel+'JOINTS:THETA6:RBV')]
        return arm
    def pos_raw_motors(self,values):
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',1)
        sleep(0.1)
        CAClient.put(self.channel+'JOINTS:THETA1:SP',values[0])
        CAClient.put(self.channel+'JOINTS:THETA2:SP',values[1])
        CAClient.put(self.channel+'JOINTS:THETA3:SP',values[2])
        CAClient.put(self.channel+'JOINTS:THETA4:SP',values[3])
        CAClient.put(self.channel+'JOINTS:THETA5:SP',values[4])
        CAClient.put(self.channel+'JOINTS:THETA6:SP',values[5])
        CAClient.put(self.channel+'PREPARE_MOVE_JOINTS_ARRAY.PROC',1)

    def asynchronousMoveTo(self,tz):
        raw_motors = self.getPositionRaw()
        virtual_motors = kin.f_kinematics([float(raw_motors[0]),float(raw_motors[1]),float(raw_motors[2]),float(raw_motors[3]),float(raw_motors[4]),float(raw_motors[5])])
        v_motors = np.concatenate((virtual_motors[0,:],virtual_motors[1,:]),0)
        offsets = kin.tool_offset
        offsets[2] = tz
        kin.setToolOffset(offsets)
        motor_values = kin.setEulerTarget(v_motors[0],v_motors[1],v_motors[2],v_motors[3],v_motors[4],v_motors[5])
        self.pos_raw_motors(motor_values)

    def getPosition(self):
        offsets = kin.tool_offset
        return offsets[2]

    def isBusy(self):
        sleep(0.2)
        loopcheck = 0
        while CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0' and CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY' and loopcheck < 10:
            loopcheck+=1
            sleep(0.1)
        if CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0':
            CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        return CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY'

    def stop(self):
        CAClient.put(self.channel+'MOTION:ABORT',1)
        CAClient.put(self.channel+'MOTION:RESUME',1)
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        
        
class rMClass(ScannableMotionBase):
    '''Device to control the Meca 500 robot arm.'''
    def __init__(self,name,axis,help=None):
            self.setName(name)
            if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
            self.setInputNames([name])
            self.setOutputFormat(['%4.5f'])
            self.Units=['deg']
            self.setLevel(5)
            self.channel = 'BL16I-MO-ROBOT-01:'
            self.axis = axis

    def asynchronousMoveTo(self,m1):
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',1)
        sleep(0.1)
        CAClient.put(self.channel+'JOINTS:THETA%s:SP'%self.axis,m1)
        CAClient.put(self.channel+'PREPARE_MOVE_JOINTS_ARRAY.PROC',1)

    def getPosition(self):
        return float(CAClient.get(self.channel+'JOINTS:THETA%s:RBV'%self.axis))

    def isBusy(self):
        sleep(0.2)
        loopcheck = 0
        while CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0' and CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY' and loopcheck < 10:
            loopcheck+=1
            sleep(0.1)
        if CAClient.get(self.channel+'ROBOT:STATUS:EOM')=='0.0':
            CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
        return CAClient.get(self.channel+'ROBOT:STATUS:BUSY')=='BUSY'

    def stop(self):
        CAClient.put(self.channel+'MOTION:ABORT',1)
        CAClient.put(self.channel+'MOTION:RESUME',1)
        CAClient.put(self.channel+'ROBOT:STATUS:BUSY',0)
    def atCommandFailure(self):
        self.stop()

# xyz = np.array([0,0,0.32])
# vx = np.array([1,0,0])
# vy = np.array([0,1,0])
# vz = np.array([0,0,1])
# #r_alpha,r_beta,r_gamma = 0,0,0
# kin.setStrategy('comfortable_limits')
# r_alpha,r_beta,r_gamma = kin.set_mu_eta_chi_phi(0,0,90,0)
# print(kin.setEulerTarget(xyz,r_alpha,r_beta,r_gamma))
#  
#  
# print('should be:\n [  0.        , -62.40567661,  62.46713701,   0.        ,  -90.0614604 ,   0.        ]')
#----------------------------------------------------#
#               Raw Motors
#----------------------------------------------------#
rm1 = rMClass('rm1',axis=1,help='robot Arm m1')
rm2 = rMClass('rm2',axis=2,help='robot Arm m2')
rm3 = rMClass('rm3',axis=3,help='robot Arm m3')
rm4 = rMClass('rm4',axis=4,help='robot Arm m4')
rm5 = rMClass('rm5',axis=5,help='robot Arm m5')
rm6 = rMClass('rm6',axis=6,help='robot Arm m6')
rbraw = robotArmClassRaw('rbraw','_arm',help='Robot Arm Control')

#----------------------------------------------------#
#               Raw Motors
#----------------------------------------------------#
rb=robotArmClass('rb','_arm',help='Robot Arm Control')
rmu_eta_chi_phi = rMuEtaChiPhiClass('rmu_eta_chi_phi',help='Grouped mu eta chi phi device')
#rmu_eta_chi_phi2 = rMuEtaChiPhiClass2('rmu_eta_chi_phi',help='Grouped mu eta chi phi device')

rmu = rMuClass('rmu',help='robot Arm Mu')
ralpha = ralphaClass('ralpha',help='robot Arm alpha')
rbeta = rbetaClass('rbeta',help='robot Arm beta')
rgamma = rgammaClass('rgamma',help='robot Arm gamma')
reta = rEtaClass('reta',help='robot Arm eta')
rchi = rChiClass('rchi',help='robot Arm chi')
rphi = rPhiClass('rphi',help='robot Arm phi')
rx = rXClass('rx',help='robot Arm x')
ry = rYClass('ry',help='robot Arm y')
rz = rZClass('rz',help='robot Arm z')
rtx = rTXClass('rtx',help='robot Arm tx')
rty = rTYClass('rty',help='robot Arm ty')
rtz = rTZClass('rtz',help='robot Arm tz')

kin.setConstraint('mu')
def rbbusy(val):
    CAClient.put('BL16I-MO-ROBOT-01:ROBOT:STATUS:BUSY',val)
