#! /usr/bin/env python

import sys
from suds.client import Client
from suds.transport.http import HttpAuthenticated
from socket import *

host = "cs04r-sc-vserv-49"
# this needs to be set to the machine running GDA server
# since it is evaluated on the cluster, "localhost" WILL NOT WORK
controlserver = "b21-control.diamond.ac.uk"

udpport=9877
prefix="biosaxs"

URL="http://"+host+":8080/ispyb-ejb3/ispybWS/ToolsForBiosaxsWebService?wsdl"
sys.path.append("/dls_sw/dasc/important")
from ispybbUserInfo import ispybbUser, ispybbPassword
username = ispybbUser()
userPassword = ispybbPassword()
httpAuthenticatedWebService = HttpAuthenticated(username=username, password=userPassword)
client = Client(URL, transport=httpAuthenticatedWebService)

redana=sys.argv[1]
collid=sys.argv[2]
state=sys.argv[3]
messagefilename=sys.argv[4]

if redana == "reduction":
	client.service.setDataReductionStatus(collid, state, messagefilename)
else:
	print "unexpected status to update. analysis is no longer supported"
	sys.exit(1)

addr = (controlserver,udpport)
UDPSock = socket(AF_INET,SOCK_DGRAM)
UDPSock.sendto(prefix+":"+collid,addr)
UDPSock.close()
