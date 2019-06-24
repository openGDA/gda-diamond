#delta Elektronika ES300 initialization script
from instruments.DeltaElektronika.delta_ES300_CLASS import Delta
from RS232.RS232_class import rs232

exec('[delta1,delta2]=[None,None]')
#set com port 1 on patch panel U1 (beamline)
com1 = rs232(1,'U1')
#Baud = 9600, bit = 8, bitstop = 1, parity = None, Flow Control = None
#\r OutTerminator, \n\r InTerminator
com1.setParameters(9600,8, 1, "None", "None", "\r","\n\r")
delta1=Delta('delta1', 1, 0.01, com1) 
delta2=Delta('delta2', 2, 0.01, com1)

def TurnOff():
    delta1.turnOff()
    delta2.turnOff()
