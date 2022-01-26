
from time import sleep;
import socket;

#The Class for creating a socket-based Device
class SingleSessionSockteDeviceClass(object):
	def __init__(self, hostName, hostPort):
		self.serverHost = hostName;
		self.serverPort = hostPort;

		self.socket=None; # socket.socket(socket.AF_INET, socket.SOCK_STREAM);
		self.connectionStatus = False;
		

	#Socket connection implementation		
	def setupServer(self, hostName, hostPort):
		self.serverHost = hostName;
		self.serverPort = hostPort;

	def connect(self):
		self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM);
		#socket.setdefaulttimeout(10);
		self.socket.settimeout(5);
		try:
			self.socket.connect((self.serverHost,self.serverPort));
		except socket.timeout:
			data = 'Connection Error, timeout.';
		except socket.error, msg:
			print 'something wrong: ' + str(msg);
			data = 'Connection Error, other exceptions.';

	def disconnect(self):
		self.socket.close();

	def sendAndReply(self, strSend):
		try:
			print 'Send out ->' + strSend;
			self.socket.send(strSend);

			data = self.socket.recv(1024);
		except socket.timeout:
			data = 'Connection Error, timeout.';
		except socket.error, msg:
			print 'something wrong: ' + str(msg);
			data = 'Connection Error, other exceptions.';
		
		print 'Received ->' + data; print;
		return data;

	def send(self, strSend):
		print 'Send out ->' + strSend;
		self.socket.send(strSend);


class SockteDeviceClass(object):
	def __init__(self, hostName, hostPort):
		self.serverHost = hostName;
		self.serverPort = hostPort;

		self.socket=None; # socket.socket(socket.AF_INET, socket.SOCK_STREAM);
		#socket.setdefaulttimeout(10);
		#self.socket.settimeout(10);

	#Socket connection implementation		
	def setupServer(self, hostName, hostPort):
		self.serverHost = hostName;
		self.serverPort = hostPort;

	def sendAndReply(self, strSend):
		self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM);
		self.socket.settimeout(5);
		try:
			self.socket.connect((self.serverHost,self.serverPort));
			print 'Send out ->' + strSend;
			self.socket.send(strSend);

			data = self.socket.recv(1024);
		except socket.timeout:
			data = 'Connection Error, timeout.';
		except socket.error, msg:
			print 'something wrong: ' + str(msg);
			data = 'Connection Error, other exceptions.';
		
		print 'Received ->' + data; print;
		self.socket.close();
		return data;

	def send(self, strSend):
		self.socket.connect((self.serverHost,self.serverPort));
		print 'Send out ->' + strSend;
		self.socket.send(strSend);
		self.socket.close();

#print "Note: Use object name 'sd' for socket communication";
#sd = SockteDeviceClass('diamrl5068.diamond.ac.uk', 2729 );
