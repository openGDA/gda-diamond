from gda.jython.commands import Input
import pd_epicsdevice

def setGain(diode):
    """
    e.g. setGain(d3)

    """
    from gdascripts.parameters import beamline_parameters
    jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
    beamline = jythonNameMap.beamline
    
    
    if diode.name=="ionc1":
        PV = "-DI-FEMTO-05:GAIN"
    else:
        PV = "-DI-FEMTO-0"+diode.name[1]+":GAIN"
        
        
    current_gain = pd_epicsdevice.Simple_PD_EpicsDevice("current_gain", beamline, PV)
    
    print str(current_gain)
    
    print "Diode ", str(diode),", gains available: 3 low, 4 low, 5 low, 6 low, 7 low, 8 low, 9 low, 5 high, 6 high, 7 high, 8 high, 9 high, 10 high, 11 high"
    gain = Input.requestInput("Please enter the gain: ")
    
    if gain=="3 low":
        tag = "10^3 low noise"
    
    elif gain=="4 low":
        tag = "10^4 low noise"
    
    elif gain=="5 low":
        tag = "10^5 low noise"
    
    elif gain=="6 low":
        tag = "10^6 low noise"
    
    elif gain=="7 low":
        tag = "10^7 low noise"
    
    elif gain=="8 low":
        tag = "10^8 low noise"
    
    elif gain=="9 low":
        tag = "10^9 low noise"
        
    elif gain=="5 high":
        tag = "10^5 high speed"

    elif gain=="6 high":
        tag = "10^6 high speed" 

    elif gain=="7 high":
        tag = "10^7 high speed" 

    elif gain=="8 high":
        tag = "10^8 high speed"
        
    elif gain=="9 high":
        tag = "10^9 high speed"  
        
    elif gain=="10 high":
        tag = "10^10 high speed" 
        
    elif gain=="11 high":
        tag = "10^11 high speed" 

    
    
    
    beamline.setValue("Top",PV,tag)
