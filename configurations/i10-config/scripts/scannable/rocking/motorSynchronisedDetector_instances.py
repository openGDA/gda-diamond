'''
Created on 2 Aug 2019

@author: fy65
'''
from scannable.rocking.detectorWithRockingMotion import NXDetectorWithRockingMotion
from gdaserver import pimte, th, pixis

thpimte=NXDetectorWithRockingMotion("thpimte", th, pimte)
thpixis=NXDetectorWithRockingMotion("thpixis", th, pixis)
