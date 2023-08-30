'''
implement group that provide on and off control of member's channel for iSeg device

Created on 25 Aug 2023

@author: fy65
'''

class ISegGroup(object):
    '''
    classdocs
    '''


    def __init__(self, name, group):
        '''
        Constructor
        '''
        self.name = name
        self.group = group
    
    def on(self):
        if not isinstance(self.group, list):
            raise ValueError("%s's group %s is not a list" % (self.name,self.group))
        [each.on() for each in self.group]
        
    def off(self):
        if not isinstance(self.group, list):
            raise ValueError("%s's group %s is not a list" % (self.name,self.group))
        [each.off() for each in self.group]
        
        
        