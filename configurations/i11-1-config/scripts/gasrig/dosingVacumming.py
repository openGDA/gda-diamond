'''
Created on 23 May 2014

@author: fy65
'''

#setSystemPressure(self, sysP,target,flow)
dose.setSystemPressure(0,1.3,0.1)
sleep(1)
#setSamplePressure(self,SampleP, target, increment)
dose.setSamplePressure(0, 0.05, 0.001)

#scan 
cvscan(1800)  # @UndefinedVariable

#setSamplePressure(self, SampleP, target, decrement)
vac.setSamplePressure(0.0, 0, 0.01)
sleep(15)
#setSystemPressure(self, sysP, target, decrement):
vac.setSystemPressure(0.7, 0, 0.01)