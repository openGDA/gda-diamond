#! /usr/bin/python

'''
Created on 31 May 2019

@author: fy65
'''
import socket
from python2_socket.SocketMessageHandlerFunctions import socketcontext,\
    connectioncontext, recv_size, recv_end, recv_timeout, recv_basic, send_size,\
    send_end
from python2_socket.MessageProcessor import Processor

HOST = 'ws128.diamond.ac.uk'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

class SocketServer():
    def __init__(self, host, port, maxConn=10, terminator='\n', processor=None):
        self.host=host
        self.port=port
        self.maxConnections=maxConn
        self.terminator=terminator
        self.processor=processor
        
    def start(self, msg_type='end'):
        with socketcontext(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(self.maxConnections)
            try:
                while True:
                    with connectioncontext(s) as conn:
                        print('Connected from', conn[1])
                        connection=conn[0]
                        if msg_type=='size': result=recv_size(connection)
                        elif msg_type=='end': result=recv_end(connection, End=self.terminator)
                        elif msg_type=='timeout': result=recv_timeout(connection, timeout=2)
                        else: result=recv_basic(connection) 
                        
                        if result:
                            print ('got %s' % (result))
                            #process data
                            if self.processor:
                                response=self.processor.process(result)
                                if response:
                                    if msg_type=='size': send_size(connection, result)
                                    elif msg_type=='end': send_end(connection, result, End=self.terminator)
                                    else: self.connection.sendall(result)
                                else:
                                    print ("No response returned from processor")
                        else:
                            # no more data - quit the loop
                            print ("no more data")
            except KeyboardInterrupt:
                import os
                os._exit(0)


import argparse

parser=argparse.ArgumentParser(description='Start a socket server')
parser.add_argument('host', metavar='IP', help='server host IP address')
parser.add_argument('port', metavar='N', type=int, default=65432, help='the server listening port')
parser.add_argument('maxConn', metavar='M', type=int, default=10, help='the maximum number of connections')
parser.add_argument('terminator', metavar='T', default='\n', help='the end mark of message, i.e. terminator')
parser.add_argument('processor', metavar='P', type=Processor, default=argparse.SUPPRESS, help='the end mark of message, i.e. terminator')
args=parser.parse_args()

if __name__=='__main__':
    socket_server = SocketServer(args.host, args.port, maxConn=args.maxConn, terminator=args.terminator, processor=args.processor)
    socket_server.start(msg_type='end')
    