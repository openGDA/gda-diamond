'''
A NXDetector class allows setting of X-ray beam size, sample size, and sample centre, exposure time limit at each sample position,
determining which axis is continuous or step motion, and step size.

Created on Feb 6, 2023

@author: fy65
'''


from gda.device.detector import NXDetector

class ExposureLimitedDetector(NXDetector):
    '''
    a detector that ensures exposure time at every position of the sample is limited to avoid X-ray damage of the sample. 
    '''


    def __init__(self, name, collection_strategy, additional_plugin_list=[]):
        '''
        Constructor
        '''
        super(NXDetector, self).__init__(name, collection_strategy, additional_plugin_list)

    def setBeamSize(self, beam_size):
        self.collectionStrategy.setBeamSize(beam_size)
        
    def setSampleSize(self, sample_size):
        self.collectionStrategy.setSampleSize(sample_size)
        
    def setSampleCentre(self, sample_centre):
        self.collectionStrategy.setSampleCentre(sample_centre)
        
    def setYStep(self, step):
        self.collectionStrategy.setYStep(step)
    
    def setZStep(self, step):
        self.collectionStrategy.setZStep(step)
        
    def setExposureTimeLimit(self, limit):
        self.collectionStrategy.setExposureTimeLimit(limit)
        
    def setYContinuous(self, b):
        self.collectionStrategy.setYContinuous(b)
        
    def setZContinuous(self, b):
        self.collectionStrategy.setZContinuous(b) 
         
        


             
    
         
        
