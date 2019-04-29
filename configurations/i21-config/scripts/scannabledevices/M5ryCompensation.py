'''
Created on 11 Jan 2019

@author: fy65
'''

from gda.device.scannable import ScannableMotionBase
from collections import OrderedDict
from scisoftpy.jython.jymaths import interp
from lookup.cvs2dictionary import loadCVSTable

lookup_file='/dls_sw/i21/software/gda/config/lookupTables/M5ryCompensation.txt'

class M5ryCompensation(ScannableMotionBase):
    '''
    classdocs
    '''
    class ValueLookup():
        def __init__(self, value_from_index, unit):
            self.value_from_index = value_from_index
            self.unit = unit
            
            if type(self.value_from_index) == type({}):
                # Do some minimal sanity checking on the lookups. 
                value_from_index_sorted = OrderedDict(sorted(value_from_index.items()))
                self.value_lookup_x = value_from_index_sorted.keys()
                self.value_lookup_y = value_from_index_sorted.values()

        def __call__(self, index):
            if self.value_from_index == None:
                return None
    
            if type(self.value_from_index) == type({}):
                sorted_keys = sorted(self.value_from_index.iterkeys())
                if index < sorted_keys[0]:
                    raise ValueError("%s %r below minimum of %r" % (self.unit, index, sorted_keys[0]))
                if index > sorted_keys[-1]:
                    raise ValueError("%s %r above maximum of %r" % (self.unit, index, sorted_keys[-1]))
                interp_value= interp(index, self.value_lookup_x, self.value_lookup_y)
                # print "### value returned from jymath.interp: %f" % (interp_value)
                return interp_value
            return self.value_from_index

        def __repr__(self):
            return self.value_from_index.__repr__()

        def index(self, value):
            if type(self.value_from_index) != type({}):
                return None
            # Only lookup tables provide back reliable reverse transforms
            if value < self.value_lookup_y[0]:
                raise ValueError("motor position %r below minimum of %r" % (value, self.value_lookup_y[0]))
            if value > self.value_lookup_y[-1]:
                raise ValueError("motor position %r above maximum of %r" % (value, self.jawphase_lookup_y[-1]))
            interp_value= interp(value, self.value_lookup_y, self.value_lookup_x)
#             print "### value returned from jymath.interp: %f" % (interp_value)
            return interp_value

    def __init__(self, name, theta, m5hqry, m5lqry, lut=lookup_file):
        '''
        Constructor
        '''
        self.setName(name)
        self.theta=theta
        self.m5hqry=m5hqry
        self.m5lqry=m5lqry
        self.setInputNames([theta.getName()])
        self.setExtraNames([m5hqry.getName(),m5lqry.getName()])
        self.setOutputFormat([theta.getOutputFormat()[0],m5hqry.getOutputFormat()[0],m5lqry.getOutputFormat()[0]])
        table=loadCVSTable(lut)
        self.m5hqry_from_theta=M5ryCompensation.ValueLookup(dict(zip(table['theta'], table['m5hqry'])),'theta_deg')
        self.m5lqry_from_theta=M5ryCompensation.ValueLookup(dict(zip(table['theta'], table['m5lqry'])), 'theta_deg')
        
    def rawGetPosition(self):
        return [self.theta.getPosition(), self.m5hqry.getPosition(), self.m5lqry.getPosition()]
    
    def rawAsynchronousMoveTo(self, new_pos):
        theta_newpos=float(new_pos)
        m5hqry_newpos=self.m5hqry_from_theta(theta_newpos)
        #m5lqry_newpos=self.m5lqry_from_theta(theta_newpos)
        self.theta.asynchronousMoveTo(theta_newpos)
        self.m5hqry.asynchronousMoveTo(m5hqry_newpos)
        #self.m5hqry.asynchronousMoveTo(m5lqry_newpos)
    
    def isBusy(self):
        return self.theta.isBusy() or self.m5hqry.isBusy() or self.m5lqry.isBusy()
    
theta = M5ryCompensation('theta', th, m5hqry, m5lqry, lut=lookup_file)  # @UndefinedVariable
