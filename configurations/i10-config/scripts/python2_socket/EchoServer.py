'''
Created on 31 May 2019

@author: fy65
'''
import socket
from python2_socket.ContextManagerWrapper4Python2 import socketcontext,\
    connectioncontext

HOST = 'ws128.diamond.ac.uk'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)


with socketcontext(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(10)
    with connectioncontext(s) as conn:
        print('Connected by', conn[1])
        while True:
            data = conn[0].recv(1024)
            if not data:
                break
            conn[0].sendall(data)

