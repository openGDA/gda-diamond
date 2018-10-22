'''
Created on 5 Apr 2018

@author: fy65
'''

from scannable.detectors.fastDicroismZebraDetector import FastDichroismZebraDetector

print "-"*100
print "Create Fast Dichroism detector 'fastDichroism' using Zebra"

global zebraContinuousMoveController #NOTE I10 does not have this bean
#fastDichroism=FastDichroismZebraDetector('fastDichroism', 'BL10I-EA-ZEBRA-01:', zebraContinuousMoveController)
fastDichroism=FastDichroismZebraDetector('fastDichroism', 'BL10I-EA-ZEBRA-01:', None)