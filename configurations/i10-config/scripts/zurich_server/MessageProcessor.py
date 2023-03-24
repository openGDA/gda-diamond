'''
An interface for handling messages from a socket client to a connected socket server.

Created on 4 Jun 2019

@author: fy65
'''

class Processor(object):
    '''
    parent class for implementing socket communication protocols on the server side.
    '''


    def __init__(self, name):
        '''
        Constructor
        '''
        self.name=name
     
    def process(self, message):
        '''method to be override by sub-class which provides actual message processing from a socket connection.
        '''
        pass 