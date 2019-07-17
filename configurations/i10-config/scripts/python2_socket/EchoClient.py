#!/usr/bin/env python
'''
Created on 3 Jun 2019

@author: fy65
'''
import socket
from python2_socket.ContextManagerWrapper4Python2 import socketcontext

HOST = 'ws128.diamond.ac.uk'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

with socketcontext(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Hello, world')
    data = s.recv(1024)

print('Received', repr(data))