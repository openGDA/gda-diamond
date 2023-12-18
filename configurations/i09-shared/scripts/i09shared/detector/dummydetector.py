'''
Created on 16 Oct 2013

@author: fy65
'''
from i09shared.detector.dummy_detector import DummyDetector
try:
    if dummydetector == None: #@UndefinedVariable
        dummydetector=DummyDetector("dummydetector")
except:
    dummydetector=DummyDetector("dummydetector")