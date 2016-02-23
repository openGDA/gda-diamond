# Class to control the DCM Energy Mode Control
#
# At the EPICS level, the control has buttons to move to Pink & Mono beam
# and a button to stop the movement. It also has a read-back field to show the current
# state (Pink, Mono, Busy, Error). TODO: verify the possible states
#
# The control is a virtual motor which moves 4-5 real motors (to be confirmed).

from time import sleep
from epics_scripts.pv_scannable_utils import caput, caget

class DcmEnergyMode:
    
    class ModeControl:
        def __init__(self, basePv):
            self.goto_pink = basePv + ':GOTOPINK'
            self.goto_mono = basePv + ':GOTOMONO'
            self.rbv = basePv + ':RBV'
            self.stop = basePv + ':STOP.PROC'


    def __init__(self):
        self.modecontrol = self.ModeControl('BL13I-OP-DCM-01:MODE')

        # The real motors that move when mode is changed
        self.motors = ['BL13I-OP-DCM-01:Y', 'BL13I-OP-DCM-01:Z',
                       'BL13I-OP-DCM-01:BRAGG', 'BL13I-OP-DCM-01:PERPOFFSET']


    def get_mode(self):
        return caget(self.modecontrol.rbv)


    def set_mode(self, mode, wait_sec=3., nattempts=32):
        mode = mode.strip()
        current_mode = self.get_mode().strip()

        # early out if already in the requested mode
        if (mode.lower() == current_mode.lower()):
            print 'DCM energy mode is already', mode
            return
        
        if (mode.lower() == 'pink'):
            move_pv = self.modecontrol.goto_pink
        elif (mode.lower() == 'mono'):
            move_pv = self.modecontrol.goto_mono
        else:
            print 'Invalid input value for DCM mode: %s!' %(mode)
            print 'Valid modes are "pink" and "mono"'
            return

        try:
            caput(move_pv, 1)
            sleep(wait_sec) # give Epics time to start up
            result = self.waitForCompletion('setting energy mode', wait_sec, nattempts)
            if (result == 'Success'):
                print 'energy mode control moved OLD: %s NEW: %s' %(current_mode) %(mode)

        except Exception, ex:
            print 'Error in DcmEnergyMode.set_mode: %s!' %(str(ex))


    def stop(self):
        caput(self.modecontrol.stop, 1)

        result = self.waitForCompletion('stopping mode control', 2, 5)
        if (result == 'Success'):
            print 'mode control stopped'
            

    def waitForCompletion(self, action, wait_sec, nattempts):
        attempt = 0

        while (attempt < nattempts):
            if (self.get_mode() == 'Invalid'):
                print 'Invalid state in', action
                self.report()
                return 'Invalid'
            
            for motor in self.motors:
                if (self.get_motor_severity(motor) != 'NO_ALARM'):
                    print 'motor %s is in error state' %(motor)
                    return 'Invalid'
            
            if (self.isBusy()):
                sleep(wait_sec)
                attempt += 1
            else:
                break

        if attempt == nattempts:
            print 'timed out on attempt %i (with wait interval of %.2f seconds)' %(attempt, wait_sec) 
            return 'Timeout'
        
        return 'Success' 
        

    def isBusy(self):
        # Check the mode control first
        if (self.get_mode().startswith('Moving')):
            return True
        
        # To be safe, check that the motors have stopped moving
        for motor in self.motors:
            if (self.get_motor_state(motor) == '0'):
                return True
             
        return False

    def get_motor_state(self, motor):
        # DMOV returns 0 if motor is moving, 1 if not
        return caget(motor + '.DMOV')

    def get_motor_severity(self, motor):
        return caget(motor + '.SEVR')

    
    def report(self):
        print '==================================================================================='
        print 'Mode control:', self.get_mode()
        print 'Busy:', self.isBusy()
        for motor in self.motors:
            print motor,': RBV:', caget(motor + ".RBV"), ', DMOV:', self.get_motor_state(motor), ', SEVR:', self.get_motor_severity(motor)
        print '==================================================================================='
