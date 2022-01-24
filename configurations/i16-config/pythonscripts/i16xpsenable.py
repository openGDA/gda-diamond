#Matthew Pearson, Script to enable all XPS axes on I16

import sys
import time
import socket

from XPS_C8_drivers import XPS

def main():

   hostname = "172.23.116.165"
   hostname2 = "172.23.116.166"
   port = 5001
   socket = None
   socket_timeout = 5.0

   names = ('GROUP1','GROUP2','GROUP3','GROUP4','GROUP5','GROUP6')
   names2 = ('GROUP1','GROUP2')
   
   xps = XPS()
   
   socket = xps.TCP_ConnectToServer(hostname, port, socket_timeout)
   for name in names:
      time.sleep(0.1)
      xps.GroupMotionEnable(socket, name)
   xps.TCP_CloseSocket(socket)

   socket = xps.TCP_ConnectToServer(hostname2, port, socket_timeout)
   for name in names2:
      time.sleep(0.1)
      xps.GroupMotionEnable(socket, name)
   xps.TCP_CloseSocket(socket)

   print "XPS enabled"
   




   
  
   
   

if __name__ == "__main__":
   main()
