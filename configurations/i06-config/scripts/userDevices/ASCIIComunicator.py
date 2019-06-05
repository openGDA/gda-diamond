'''
Created on 9 Nov 2017

@author: fy65
'''
from gda.device import DeviceBase
from gda.io.socket import SocketBidiAsciiCommunicator
import weakref

class ASCIIComunicator(DeviceBase):
    '''
    handle ASCII communicator with the specified device (ipaddress:port)
    after create the device object, you need to call .configure() to initialise the connection,
    when finished you need to call .close() to close the connection.
    
    Command is sent to device using .send(cmd) method which return any reply which must be handled by user
    Command is sent to device using .sendCmdNoReply(cmd) method does not return any reply.
    '''


    def __init__(self, name, ipaddress, port, terminator, parent=None):
        '''
        Constructor
        @param name: the name of this object.
        @param ipaddress: the IP Address to talk to.
        @param port: the port number over which communicate with device is done.
        @param terminator: the command and reply terminator used by this device.
        @param parent: the caller of this object - used to ensure socket is closed when this object is deleted.
        '''
        self.setName(name)
        self.ipaddress=ipaddress
        self.port=port
        self.terminator=terminator
        if parent is None:
            self.parent=parent
        else:
            self.parent=weakref.ref(parent)
        self.communicator=SocketBidiAsciiCommunicator()
        self.terminatorRequired=True
        
    def setAddress(self, address):
        self.ipaddress=address
        
    def getAddress(self):
        return self.ipaddress
    
    def setPort(self, portnumber):
        self.port=portnumber
        
    def getPort(self):
        return self.port
    
    def setTerminator(self, term):
        self.terminator=term
        
    def getTerminator(self):
        return self.terminator
    
    def setTerminatorRequired(self, b):
        self.terminatorRequired=b
        
    def isTerminatorRequired(self):
        return self.terminatorRequired
        
    def configure(self):
        ''' configure and initialise the connection
        '''
        if not self.configured:
            if self.ipaddress is not None:
                self.communicator.setAddress(self.ipaddress)
            else:
                raise Exception("IP address is required!")
            if self.port is not None and type(self.port) is int:
                self.communicator.setPort(self.port)
            else:
                raise Exception("Port number is required and it is must an Integer Number!")
            if self.terminator is not None:
                self.communicator.setCmdTerm(self.terminator)
                self.communicator.setReplyTerm(self.terminator)
            else:
                if self.terminatorRequired:
                    raise Exception("Terminator is required!")
                else:
                    print "Terminator is not set, maybe not required by the device commands and replies."
#             try:
#                 self.communicator.connectIfRequired()
#             except DeviceException, err:
#                 print err
#             else:
#                 print "Device %s is connected in port %d." % (self.ipaddress, self.port)
            
            self.configured=True
        else:
            print "Device % is already configured at port %d !" % (self.ipaddress, self.port) 
    
    def send(self, cmd):
        '''send command to device and get reply from this command'''
        return self.communicator.send(cmd)
        
    def sendCmdNoReply(self, cmd):
        '''send command to device, and does not get reply'''
        self.communicator.sendCmdNoReply(cmd)
        
    def close(self):
        '''close connection'''
        self.communicator.closeConnection()
        
    def isClosed(self):
        self.communicator.isClosed()
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print "close socket connection on exit with-statement"
        self.close()
        
    def __del__(self):
        print "close socket connection on delete this object."
        self.close()