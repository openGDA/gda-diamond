'''
Created on Mar 6, 2023

@author: fy65
'''
from org.apache.commons.lang3.builder import EqualsBuilder, HashCodeBuilder
from gda.observable import Observer

class GeneralObserver(Observer):
    ''' a generic gda.observable.Observer which can be added to any gda.observable.Observable 
    on update it calls the given update function
    '''
    def __init__(self, name, update_function):
        self.name =name
        self.updateFunction = update_function # a function point
        
    def update(self, source, change):
        self.updateFunction(source, change)
    
    #both equals and hashCode method required by addIObserver and deleteIOberser in Java observers set.        
    def equals(self, other):
        return EqualsBuilder.reflectionEquals(self, other, True)
      
    def hashCode(self):
        return HashCodeBuilder.reflectionHashCode(self, True)