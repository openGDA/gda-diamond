'''
Created on 31 May 2019

@author: fy65
'''
import socket
import sys

HOST = 'ws128.diamond.ac.uk'  
PORT = 7000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('# Socket created')

# Create socket on port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print('# Bind failed. '), msg
    sys.exit()

print('# Socket bind complete')

# Start listening on socket
s.listen(10)
print('# Socket now listening')

# Wait for client
while True:
    conn, addr = s.accept()
    print('# Connected to ' + addr[0] + ':' + str(addr[1]))

# Receive data from client
while True:     
    data = conn.recv(1024)
    line = data.decode('UTF-8')    # convert to string (Python 3 only)
    line = line.replace("\n","")   # remove newline character
    print( line )

s.close()