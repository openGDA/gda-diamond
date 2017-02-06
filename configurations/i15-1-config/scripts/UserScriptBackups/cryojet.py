from time import sleep

# some cryojet commands
def setCryoTemp(temp=300,setFlow=True):
    """ sets the cryojet temperature and the appropriate flows."""
    if temp < 81:
        temp = 81.
    elif temp > 520:
        temp = 520.
    
    # find the flows
    if temp < 94.9:
        samFlow = 16.
        shiFlow = 3.9
    elif temp < 99.9:
        samFlow = 15.
        shiFlow = 3.9
    elif temp < 199.9:
        samFlow = 10.
        shiFlow = 3.9
    elif temp < 269.9:
        samFlow = 7.5
        shiFlow = 3.9
    elif temp < 299.9:
        samFlow = 6.5
        shiFlow = 3.9
    else:
        samFlow = 5.5
        shiFlow = 0.0
    
    # set the flows
    if setFlow:
        caput("BL15I-CG-CJET-01:SAMPLEFLW:SET",samFlow)
        caput("BL15I-CG-CJET-01:SHIELDFLW:SET",shiFlow)
    
    # set the temperature
    caput("BL15I-CG-CJET-01:TTEMP:SET",temp)
    
    sleep(0.5)
    #print 'The CryoJet settings are now:'
    #print 'Set point: %3.2f (K) Sample Flow: %2.1f ls-1 Shield Flow: %2.1f' % (caget('BL15I-CG-CJET-01:TTEMP'),\
    #                                                                           caget('BL15I-CG-CJET-01:SAMPLEFLW:SET'),\
    #                                                                           caget('BL15I-CG-CJET-01:SHIELDFLW:SET'))
print(r't = caget("BL15I-CG-CJET-01:STEMP") # returns the current temperature)')


