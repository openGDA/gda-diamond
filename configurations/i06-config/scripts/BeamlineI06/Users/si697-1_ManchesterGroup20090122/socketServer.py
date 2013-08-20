#!/usr/bin/python
#
# 
import socket

def printAscii(string):
	for x in string:
		print ord(x),
	print;

myHost = socket.gethostname();
myPort = 2729;
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM); # create a TCP socket
mySocket.bind((myHost, myPort));         # bind it to the server port
mySocket.listen(5);                      # allow 5 simultaneous

# socket.setdefaulttimeout(5)

while True:
	# wait for next client to connect
	connection, address = mySocket.accept() # connection is a new socket
	print 'We have opened a connection with', address;
	while True:
		data = connection.recv(1024) # receive up to 1K bytes
		if not data:# return zero byte means connection closed by client
			break;

		printAscii(data);

		#td=data.translate(None, ' \n\r');
		td=data.strip(' \n\r');
		printAscii(td);

		if td != "qq": #client send quit
			connection.send('Echo --> ' + data)
		else:
			break;

	print "Close current connection with ", address;
	connection.close();


# http://docs.python.org/library/socket.html
# http://www.amk.ca/python/howto/sockets/
# http://www.devshed.com/c/a/Python/Sockets-in-Python/1/
# http://floppsie.comp.glam.ac.uk/Glamorgan/gaius/wireless/5.html
# http://trac.diamond.ac.uk/gda/wiki/SocketPseudoDevice


