
from time import sleep;
#import socket;
from java.io import BufferedReader, InputStreamReader;
from java.io import BufferedWriter, OutputStreamWriter, PrintWriter;
from java.io import IOException;

from java.net import Socket;
from java.net import ConnectException, SocketTimeoutException, SocketException;

from Diamond.Comm.SocketDevice import SocketError;

class JavaSocketDeviceClass(object):
	def __init__(self, hostName, hostPort):
		self.serverHost = hostName;
		self.serverPort = hostPort;

		self.timeOut = 30;
		self.setTimeout(self.timeOut);
		self.socket=None; # socket.socket(socket.AF_INET, socket.SOCK_STREAM);

#		print "Default Socket Timeout: " + str(socket.getdefaulttimeout());
		
	def setTimeout(self, newTimeout):
		self.timeOut = newTimeout;
		
	#Socket connection implementation		
	def setupServer(self, hostName, hostPort):
		self.serverHost = hostName;
		self.serverPort = hostPort;

	def sendAndReply(self, strSend):
		try:
			self.socket = Socket(self.serverHost, self.serverPort);
			self.socket.setSoTimeout(self.timeOut * 1000);
			
			outWriter = BufferedWriter( OutputStreamWriter(self.socket.getOutputStream()) );
			outWriter.write(strSend);
			outWriter.flush();
			inReader = BufferedReader( InputStreamReader(self.socket.getInputStream()) );
			
#			while not inReader.ready():
#				sleep(0.1);
#			data = inReader.readLine();
#
			while True:
				data=inReader.readLine();
				if data is not None:
					break;
			
			outWriter.close();
			inReader.close();
			self.socket.close()	

		except ConnectException, msg:
			print "Connection Exception: " + msg;
			return;
		except SocketTimeoutException:
			raise SocketError("Time Out");
			print "Connection Error, timeout.";
			return;
		except SocketException, msg:
			raise SocketError( str(msg) );
			print "Connection Error, other socket exceptions.";
			return;
		except IOException, msg:
			print "IOException.";
			return;
		
		if type(data).__name__ == 'unicode':
			return data.encode('utf-8');
		elif type(data).__name__ == 'str':
			return data;
		else:
			print "Unknow type of Socket input" + repr(type(data));
			raise SocketError("Unknown type of socket input");
			

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

	def send(self, strSend):
		try:
			self.socket = Socket(self.serverHost, self.serverPort);
			self.socket.setSoTimeout(self.timeOut * 1000);
			
			outWriter = PrintWriter( self.socket.getOutputStream() );
			outWriter.print(strSend);
			outWriter.flush();

			outWriter.close();
			self.socket.close()	
			
		except ConnectException, msg:
			print "Connection Exception: " + msg;
		except SocketTimeoutException:
			raise SocketError("Time Out");
			print "Connection Error, timeout.";
		except SocketException, msg:
			raise SocketError( str(msg) );
			print "Connection Error, other socket exceptions.";
		except IOException, msg:
			print "IOException.";
		
		return;


#print "Note: Use object name 'sd' for socket communication";
#sd = SocketDeviceClass('diamrl5068.diamond.ac.uk', 2729 );
