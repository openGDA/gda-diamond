'''
implement commands listed in attached file http://jira.diamond.ac.uk/secure/attachment/26005/Keysight-Command-ListFinal.pdf
Created on 10 Nov 2017

@author: fy65
'''
from userDevices.ASCIIComunicator import ASCIIComunicator
from gda.jython.commands.GeneralCommands import alias


keysight=ASCIIComunicator("keysight", "172.23.106.128", 1025, '\n')
keysight.configure()

def ksstatus():
    return keysight.send("*IDN?")
alias("ksstatus")

def ksbeepoff():
    keysight.send(":SYST:BEEP:STAT OFF")
alias("ksbeepoff")

def ksvcomp(v):
    keysight.send(":SENS:VOLT:PROT "+ str(v))
alias("ksvcomp")

def kssource(amp):
    keysight.send(":SOUR:CURR:RANG:AUTO ON")
    keysight.send(":SOUR:CURR " + str(amp)+"e-3")
    keysight.send(":OUTP ON")
alias("kssource")
    
def kssourceoff():
    keysight.send(":OUTP OFF")
alias("kssourceoff")

def ks2p():
    keysight.send(':SENS:FUNC "VOLT”')
    keysight.send(":SENS:VOLT:RANG:AUTO ON")
    keysight.send(":SENS:REM OFF")
    keysight.send(':SENS:FUNC "VOLT”') 
    return keysight.send(":MEAS:VOLT?") 
alias("ks2p")

def ks4p(v):
    keysight.send(':SENS:FUNC "VOLT”')
    keysight.send(":SENS:VOLT:RANG:AUTO OFF")
    keysight.send(":SENS:VOLT:RANG " + str(v)+"e-3")
    keysight.send(":SENS:REM ON")
    return keysight.send(":MEAS:VOLT?") 
alias("ks4p")

def kspulse(amplitude, width, numpulses, interval, compvol):
    keysight.send(":*RST")
    keysight.send(":SENS:VOLT:PROT "+str(compvol))
    keysight.send(":SOUR:FUNC:MODE CURR")
    keysight.send(":SOUR:CURR:RANG:AUTO ON")
    keysight.send(":SOUR:FUNC:SHAP PULS")
    keysight.send(":SOUR:PULS:DEL 0")
    keysight.send(":SOUR:PULS:WIDT "+str(width)+"e-3")
    keysight.send(":SOUR:CURR 0")
    keysight.send("SOUR:CURR:TRIG "+str(amplitude/1000.0))
    keysight.send(':SENS:FUNC "VOLT"') 
    keysight.send(":SENS:VOLT:RANG:AUTO ON")
    keysight.send(":SENS:REM OFF")
    keysight.send(":SENS:CURR:APER ("+str(width)+"e-3)/2")
    keysight.send(":TRIG:TRAN:DEL 1e-4")
    keysight.send(":TRIG:ACQ:DEL ("+str(width)+"e-3)/4")
    keysight.send(":TRIG:SOUR TIM")
    keysight.send(":TRIG:TIME "+str(interval))
    keysight.send(":TRIG:COUN "+str(numpulses))
    keysight.send(":OUTP On")
    keysight.send(":INIT")
    datastring=keysight.send(":FETC:ARR:VOLT?")
    keysight.send("*RST")
    return datastring
alias("kspulse")


