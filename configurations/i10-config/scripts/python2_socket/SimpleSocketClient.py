'''
Created on 31 May 2019

@author: fy65
'''
# Socket client example in python

import socket
import sys  

host = '172.23.240.161'
port = 80  # web

# create socket
print('# Creating socket')
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print('Failed to create socket')
    sys.exit()

print('# Getting remote IP address') 
try:
    remote_ip = socket.gethostbyname( host )
except socket.gaierror:
    print('Hostname could not be resolved. Exiting')
    sys.exit()

# Connect to remote server
print('# Connecting to server, ' + host + ' (' + remote_ip + ')')
s.connect((remote_ip , port))

# Send data to remote server
print('# Sending data to server')
request = "GET / HTTP/1.0\r\n\r\n"

try:
    s.sendall(request)
except socket.error:
    print 'Send failed'
    sys.exit()

# Receive data
print('# Receive data from server')
reply = s.recv(4096)

print reply 