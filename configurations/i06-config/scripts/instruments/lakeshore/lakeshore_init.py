#Lakeshore 331S initialization script
from instruments.lakeshore.lakeshore_class import Lakeshore331_class, LakeshoreHeaterOut_class, LakeshoreSetPoint_class, LakeshoreTemperature_class
from RS232.RS232_class import rs232

exec('[lakeshore, temp, heater, setTemp]=[None, None, None, None]')
#set com port 1 on patch panel U1 (beamline)
com1 = rs232(1,'U1')
#Baud = 9600, bit = 7, bitstop = 1, parity = Odd, Flow Control = None
#\r\n OutTerminator, \r\n InTerminator
#com1.setParameters(9600,7, 1, "Odd", "None", "\r\n","\r\n")
lakeshore=Lakeshore331_class('lakeshore', com1) 
temp = LakeshoreTemperature_class('temp',lakeshore)
heater = LakeshoreHeaterOut_class('heater',lakeshore)
setTemp = LakeshoreSetPoint_class('setTemp',lakeshore)
 
