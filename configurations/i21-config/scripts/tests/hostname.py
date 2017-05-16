'''
Created on 10 May 2017

@author: fy65
'''
from java.net import InetAddress

##print InetAddress.getHostName()
print InetAddress.getLocalHost().getHostName().split('.')[0]
