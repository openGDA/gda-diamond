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

if redana == "analysis":
	client.service.setDataAnalysisStatus(collid, state, messagefilename)
else:
	client.service.setDataReductionStatus(collid, state, messagefilename)

#client.service.setDataAnalysisStatus("1985", "COMPLETE", "filename")
#client.service.setDataAnalysisStatus(collid, state, messagefilename)
#client.service.setDataReductionStatus(dataCollectionId = "2033", status = "FAILED", filenameOrMessage = "failed message")
#client.service.setDataReductionStatus(2033, "COMPLETE", "/dls/b21/data/2013/sm999-9/b21-14.nxs")

addr = (controlserver,udpport)
UDPSock = socket(AF_INET,SOCK_DGRAM)
UDPSock.sendto(prefix+":"+collid,addr)
UDPSock.close()
