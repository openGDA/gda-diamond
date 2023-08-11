'''
class defines a compound scannable which moves multiple scannables given simultaneously.
It requires a function to provide conversion from input data to demanded target for each scannable.
 
Created on 14 Jul 2023

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase

class CompoundScannable(ScannableMotionBase):
    '''
    a scannable that consists of multiple scannables which move in a coordinated fashion defined in a given function or algorithm
    '''


    def __init__(self, name, function, *scannables):
        '''
        Constructor - merge input names, extra names, and output formats of all scannables
        '''
        self.setName(name)
        self.setInputNames([str(inputname) for s in scannables for inputname in s.getInputNames()])
        self.setExtraNames([str(extraname) for s in scannables for extraname in s.getExtraNames()])
        self.setOutputFormat([str(outputformat) for s in scannables for outputformat in s.getOutputFormat()])
        self.func = function
        self.scannables =  scannables
        
    def getPosition(self):
        input_results = []
        extra_results = [] 
        for s in self.scannables:
            values = s.getPosition()
            if isinstance(values, (list, tuple)):
                input_length = len(s.getInputNames())
                input_results += values[:input_length]
                extra_results += values[input_length:]
            else:
                if len(s.getInputNames()) == 1:
                    input_results.append(values)
                else:
                    extra_results.append(values)
        return input_results + extra_results
    
    def asynchronousMoveTo(self, newpos):
        if not isinstance(newpos, (list, tuple)):
            raise ValueError("input to scannable %s must be a list or tuple" % (self.getName()))
        if len(self.getInputNames()) !=  len(newpos):
            raise ValueError("%d number of input required, but only %d is given" % (len(self.getInputNames()), len(newpos)))
        input_targets = []
        input_start_index = 0
        for s in self.scannables:
            input_length = len(s.getInputNames())
            input_targets.append(newpos[input_start_index:(input_length + input_start_index)])
            input_start_index += input_length
        
        #calculate new positions for each scannable from the input targets 
        # please note the data in input_targets is list of lists - 1st list is for 1st scannable, etc...   
        positions_4_scannables = self.func(input_targets)
        
        for s, p in zip(self.scannables, positions_4_scannables):
            s.asynchronousMoveTo(p)
            
    def isBusy(self):
        my_busy = False
        for s in self.scannables:
            my_busy = my_busy or s.isBusy()
        return my_busy
    

