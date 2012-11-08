from gda.device.scannable import ScannableBase
from math import sqrt
class Sampler(ScannableBase):
    
    def __init__(self, scannable_to_sample, processors, readout_samples=True):
        self.name = scannable_to_sample.name + '_sampler'
        self.scannable = scannable_to_sample
        self.processors = list(processors)
        self.readout_samples = readout_samples
        
        self.n_samples = 1
        self.t_sample = 1
        self.samples = [999]
    
    def getInputNames(self):
        return self.scannable.name + '_tsamp', self.scannable.name + '_nsamp'
    
    def getExtraNames(self):
        names = []
        if self.readout_samples:
            for i in range(self.n_samples):
                names.append('%s_%i' % (self.scannable.name, i))
        for processor in self.processors:
            names.append('%s_%s' % (self.scannable.name, processor.name))
        return names

    def getOutputFormat(self):
        sample_fmt = list(self.scannable.getOutputFormat())[0]
        return ['%.3f', '%i'] + [sample_fmt] * len(self.getExtraNames())
    
    def rawAsynchronousMoveTo(self, pos):
        self.t_sample, self.n_samples,  = list(pos)
        self.samples = []
        for _ in range(self.n_samples):
            self.scannable.asynchronousMoveTo(self.t_sample)
            self.scannable.waitWhileBusy()
            self.samples.append(self.scannable.getPosition())
    
    def isBusy(self):
        return False
    
    def rawGetPosition(self):
        position = [self.t_sample, self.n_samples]
        if self.readout_samples:
            position += self.samples
        for processor in self.processors:
            position.append(processor.process(self.samples))
        return position
        


    #===========================================================================
    # 
    # SampleProcessors
    # 
    #===========================================================================

class SampleProcessor(object):
    
    def __init__(self, name):
        self.name = name
    
    def process(self, sample_list):
        """Return a single number
        """
        raise NotImplementedError()


class SumProcessor(SampleProcessor):
    
    def __init__(self):
        SampleProcessor.__init__(self, 'sum')
        
    def process(self, sample_list):
        return sum(sample_list)


class RmsProcessor(SampleProcessor):
    
    def __init__(self):
        SampleProcessor.__init__(self, 'RMS')
        
    def process(self, samples):
        return sqrt(float(sum([s*s for s in samples]))/len(samples))


