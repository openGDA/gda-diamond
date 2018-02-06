'''
This module provides a convenient method to run all of diagnostics objects in the system by

    >>> rundiagnose()
    
It also provide a base class for diagnosing the health of an object. 
Subclass must specify the object to be diagnosed and providing a "diagnose" method
to each of the object to be diagnosed which implements its diagnosetic rules.

Created on 6 Nov 2009

@author: fy65
'''
listOfDiagnoseticsObjects=[]

class Diagnostics(object):
    '''
    Base class for creating diagnostics objects. Subclass constructor should always call this class's 
    constructor in order to add the objects it will diagnose to the list of objects to be diagnosed
    so that the diagnose processing can be run by
     
        <diagnosetics_object>.run()
        
    '''

    def __init__(self, name, objectToDiagnose=[]):
        '''
        Constructor which adds a diagnose object and its rule to the dictionary
        '''
        if name is None:
            self.setName("diagnostics")
        else:
            self.setName(name)
        self.objectToDiagnose=objectToDiagnose
    
    def setName(self, name):
        self.name = name
        
    def getName(self):
        return self.name
    
    def run(self, result=[]):
        '''run the diagnose-object and report failed objects only'''
        if self.objectToDiagnose is None: 
            return "No object to be diagnosed in the list."
        for each in self.objectToDiagnose:
            if not each.diagnose():
                result.append(each.getName() + ": Failed.")
        if result is None:
            result.append("ALL PASSED.")
        return result
            
def rundiagnose(result={}):
    ''' run system diagnose, return diagnose results in a dictionary if any.'''
    if listOfDiagnoseticsObjects is None:
        return "No diagnosetics object is available to run. listOfDiagnoseticsObjects is empty."
    for each in listOfDiagnoseticsObjects:
        result[each]=each.run()
    return result
       
