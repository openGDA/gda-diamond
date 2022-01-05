# -*- coding: utf8 -*-

from time import sleep;
import socket;

#For TCP client sockets
#from socket import SO_KEEPALIVE, SO_LINGER, SO_OOBINLINE, SO_RCVBUF, SO_REUSEADDR, SO_SNDBUF, SO_TIMEOUT, TCP_NODELAY

# For TCP server sockets
#from socket import SO_RCVBUF ,SO_REUSEADDR, SO_TIMEOUT;

#For UDP sockets
#from socket import SO_BROADCAST ,SO_RCVBUF ,SO_REUSEADDR ,SO_SNDBUF, SO_TIMEOUT;


class SocketError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class SocketDeviceClass(object):
	def __init__(self, hostName, hostPort):
		self.serverHost = hostName;
		self.serverPort = hostPort;

		self.timeOut = 30;
		self.setTimeout(self.timeOut);
		self.socket=None; # socket.socket(socket.AF_INET, socket.SOCK_STREAM);

#		print "Default Socket Timeout: " + str(socket.getdefaulttimeout());
		
	def setTimeout(self, newTimeout):
		self.timeOut = newTimeout;
		print "Default Socket Timeout: " + str(socket.getdefaulttimeout());
		socket.setdefaulttimeout(self.timeOut);
		
	#Socket connection implementation		
	def setupServer(self, hostName, hostPort):
		self.serverHost = hostName;
		self.serverPort = hostPort;

	def sendAndReply(self, strSend):
		self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM);
#		print "Individual socke timeout: " + str( self.socket.gettimeout() );
#		self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1);
#		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
#		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_TIMEOUT, 3);
		
		try:
			self.socket.connect((self.serverHost,self.serverPort));
			self.socket.settimeout(self.timeOut);
#			print 'Send out ->' + strSend;
			self.socket.send(strSend);
			data = self.socket.recv(1024);
			self.socket.close();
#			print 'Received ->' + data; print;
			return data;
		except socket.timeout:
			raise SocketError("Time Out");
			self.socket.close();
			print 'Connection Error, timeout.';
		except socket.error, msg:
			raise SocketError( str(msg) );
			print 'Connection Error, other exceptions.';

	def send(self, strSend):
		try:
			self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM);
			self.socket.connect((self.serverHost,self.serverPort));
#			print 'Send out ->' + strSend;
			self.socket.send(strSend);
			self.socket.close();
		except socket.timeout:
			print "Time Out";
			raise SocketError("Time Out");
		except socket.error, msg:
			print "Socket Error: " + str(msg) ;
			raise SocketError( str(msg) );


	def resilientSendAndReply(self, strSend, retry=5):
		data = None;
		if retry < 0:
			retry = 1;
			
		for i in range(retry+1):
			try:
				data = self.sendAndReply(strSend);
				return data;
			except SocketError, msg:
				print "Communication Error with Server: " + str(msg); 
				print "Retry... " + str(i);

		raise SocketError("Retry Efforts Failed");

#The Class for creating a socket-based Device
class SingleSessionSocketDeviceClass(SocketDeviceClass):
	def __init__(self, hostName, hostPort):
		SocketDeviceClass.__init__(self, hostName, hostPort);
		self.connectionStatus = False;

	def connect(self):
		self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM);
		self.socket.settimeout(self.timeOut);
		try:
			self.socket.connect((self.serverHost,self.serverPort));
		except socket.timeout:
			raise SocketError("Time Out");
			data = 'Connection Error, timeout.';
		except socket.error, msg:
			raise SocketError( str(msg) );
			data = 'Connection Error, other exceptions.';

	def disconnect(self):
		self.socket.close();

	def sendAndReply(self, strSend):
		try:
			print 'Send out ->' + strSend;
			self.socket.settimeout(self.timeOut);
			self.socket.send(strSend);

			data = self.socket.recv(1024);
		except socket.timeout:
			raise SocketError("Time Out");
			data = 'Connection Error, timeout.';
		except socket.error, msg:
			raise SocketError( str(msg) );
			data = 'Connection Error, other exceptions.';
		
		print 'Received ->' + data; print;
		return data;

	def send(self, strSend):
		try:
			print 'Send out ->' + strSend;
			self.socket.send(strSend);
		except socket.timeout:
			raise SocketError("Time Out");
		except socket.error, msg:
			raise SocketError( str(msg) );

		
	def receive(self):
		try:
			data = self.socket.recv(1024);
		except socket.timeout:
			raise SocketError("Time Out");
			data = 'Connection Error, timeout.';
		except socket.error, msg:
			raise SocketError( str(msg) );
			data = 'Connection Error, other exceptions.';

		print 'Received ->' + data; print;
		return data;


#print "Note: Use object name 'sd' for socket communication";
#sd = SocketDeviceClass('diamrl5068.diamond.ac.uk', 2729 );
