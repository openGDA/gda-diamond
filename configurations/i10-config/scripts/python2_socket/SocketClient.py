'''
Created on 4 Jun 2019

@author: fy65
'''
from python2_socket.SocketMessageHandlerFunctions import socketcontext,\
    send_size, send_end, recv_size, recv_end, recv_timeout, recv_basic
import socket
import weakref

class SocketClient(object):
    '''
    classdocs
    '''


    def __init__(self, host, port, terminator='\n', parent=None):
        '''
        Constructor
        '''
        self.host=host
        self.port=port
        self.terminator=terminator
        if parent:
            #needed to ensure reset_namespace close the connection if connected
            self.parent=weakref.ref(parent)
        else:
            self.parent=parent
        self.socket=None
        
    def connect(self, host, port):
        if self.socket is None:
            with socketcontext(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
                self.socket.connect((self.host, self.port))
                self.socket.settimeout(5.0)
        
    def close(self):
        if self.socket:
            self.socket.close()
            self.socket=None
        
    def send(self,msg, msg_type='end'):
        self.connectIfRequired()
        if msg_type=='size': send_size(self.socket, msg)
        elif msg_type=='end': send_end(self.socket, msg, End=self.terminator)
        else: self.socket.sendall(msg)
        
    def receive(self, msg_type='end'):
        if msg_type=='size': result=recv_size(self.socket)
        elif msg_type=='end': result=recv_end(self.socket, End=self.terminator)
        elif msg_type=='timeout': result=recv_timeout(self.socket, timeout=2)
        else: result=recv_basic(self.socket)
        print("got result %s", result)
        return result
    
    def sendWithReply(self, msg, msg_type='end'):
        self.send(msg, msg_type)
        return self.receive(msg_type)
    
    def connectIfRequired(self):
        self.connect(self.host, self.port)
        
    def __del__(self):
        '''required to ensure socket connection is closed when reset_namespace
        '''
        print ("close socket connection on delete this object.")
        self.close()           