#! /usr/bin/env jython

import sys;
import socket;
import threading;
from time import sleep;

sys.path.append("/home/xr56/Dev/gdaDev/gda-config-local/localBase/scripts");
#sys.path.append("/home/xr56/Dev/gdaDev/gda-config/i07/scripts");
#sys.path.append("/dls/i07/software/gda_versions/gdaDev/dev_gdaConfig/i07/scripts");
#sys.path.append("/home/cop98/Dev/gdaDev/gda-config-local/localBase/scripts");

from Diamond.Comm.SocketDevice import SocketDeviceClass, SingleSessionSocketDeviceClass ;
from Diamond.Comm.SocketDevice import SocketError;

#Method one: using the Python Threading package
class ServingPythonThread(threading.Thread):
	parseLock=threading.Lock();
	id=0;
	
	def __init__(self, newSocket):
		threading.Thread.__init__(self);
		self.myid=ServingPythonThread.id;
		ServingPythonThread.id += 1;

		self.hostSocket = newSocket;

		(self.connection, address) = self.hostSocket.accept() # connection is a new socket
		print 'New Python thread to deal with socket client from ', address;
	
		
	def run(self):
		while True:
			data = self.connection.recv(1024) # receive up to 1K bytes
			if not data:# return zero byte means connection closed by client
				print "Client closed";
				break;
			print 'Received -> ' + data;
			print "ASCII Code: "
			self.printAscii(data);
	
			td=data.strip(EchoSocketServerClass.TERMINATERS);
			
			if td != "quit": #client send quit
				ServingPythonThread.parseLock.acquire();
				reply = self.parse(td);
				ServingPythonThread.parseLock.release();
				if reply != "quiet":
					self.connection.send(reply + EchoSocketServerClass.TERMINATERS);
				else:
					reply=raw_input("Please type a reply to the client: ");
					self.connection.send(reply + EchoSocketServerClass.TERMINATERS);
			else:
				print "Client quitting";
				sleep(1);
				break;
		
		self.connection.close();
		
	def parse(self, inStr):
		reply = None;
		
		rlist = inStr.split(' ',1);
		
		if rlist[0] == 'echo':
			reply = rlist[1];
			
		elif rlist[0] == 'quiet':
			reply = 'quiet';

		else:
			reply = 'Unknown Command: ' + inStr;

		return reply;

	def printAscii(self, inString):
		for x in inString:
			print ord(x),
		print;


class EchoSocketServerClass(object):
	TERMINATERS = '\n\r';

	def __init__(self, hostName, port):
		
		self.hostName=hostName;
		self.port=port;

		self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM); # create a TCP socket
		self.mySocket.bind((self.hostName, self.port));         # bind it to the server port
		self.mySocket.listen(5);                      # allow 5 simultaneous

		self.threadList = [];

	def start(self):
		for i in range(5):#Up to two clients can connect to this server
			# wait for next client to connect
			spt=ServingPythonThread(self.mySocket);
			self.threadList.append(spt);
			spt.start();

	def join(self):
		#wait until all serving thread done
		for st in self.threadList:
			st.join();#join the thread with the main thread so that the main thread can finish only when all jointed threads terminated. 

	def shutdown(self):
		self.mySocket.close();
		print "Bye Bye";

	def setout(self):
		self.start();
		self.join();
		self.shutdown();


#hostName = socket.gethostname();
#portNumber = 2741;
#camserver=CamServerSimClass(hostName, portNumber, PilatusInfo.PILATUS_MODEL_100K);
#camserver.setout();


serverHost = socket.gethostname();
#hostName = '172.23.243.157'
serverPort = 41234;


echoserver=EchoSocketServerClass(serverHost, serverPort);

echoserver.setout();

