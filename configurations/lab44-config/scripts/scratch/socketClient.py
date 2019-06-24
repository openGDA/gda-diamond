#!/usr/bin/python
# Echo client program
#
# 
import socket

def printAscii(string):
	for x in string:
		print ord(x),
	print;

serverHost = 'localhost';
serverPort = 2729;
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM); # create a TCP socket
mySocket.connect((serverHost, serverPort));         # connect to the server socket

while True:
	s = raw_input('Input -> ');
	mySocket.send(s);
	data = mySocket.recv(1024);
	if not data:
		break;
	print 'Received -> ' + data; print;
print "Client closed."
mySocket.close();



