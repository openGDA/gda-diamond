from gda.device.enumpositioner.ValvePosition import *

ionchamber2fill="I0"
targetPressureAr=35 #mbar
targetPressureHe=1800 #mbar

ionchamber_purge_time=10.00 #30
ionchamber_leak_wait_time=10.0 #10
helium_equilibration_wait_time=5.0

PRESSURE_CONTROL="Control"
PRESSURE_HOLD="Hold"

def extract_device_name(scannable) :
    name=scannable.getName()
    vals=["gir", "pressure", "valve", "_"]
    for val in vals : 
        name = name.replace(val, "")
    return name

def long_sleep(sleep_time, reason="") :
    print("Waiting for {} seconds {}".format(sleep_time,reason))
    while sleep_time > 0 :
        print".",
        time.sleep(1)
        sleep_time -= 1
    print ""
    
def set_target_pressure(pressure_setpoint, target_pressure) :
    print("Setting setpoint pressure on {} to {}".format(pressure_setpoint.getName(), target_pressure))
    pressure_setpoint.moveTo(target_pressure) # apply the target pressure setpoint
    time.sleep(1)
    
def pressure_mode_hold(pressure_controller):
    print("Setting pressure control mode to "+PRESSURE_HOLD)
    pressure_controller.moveTo(PRESSURE_HOLD)
    time.sleep(1)

def pressure_mode_control(pressure_controller):
    print("Setting pressure control mode to "+PRESSURE_CONTROL)
    pressure_controller.moveTo(PRESSURE_CONTROL)
    time.sleep(1)
    
def pump_on():
    print("Switching vacuum pump on")
    gir_vacuum_pump.moveTo(RESET)
    gir_vacuum_pump.moveTo(OPEN)  # pump on
    time.sleep(1)

def pump_off():
    print("Switching vacuum pump off")
    gir_vacuum_pump.moveTo(CLOSE) # pump off
    time.sleep(1)

def open_valve(valve) :
    print("Opening valve : {}".format(valve.getName()))
    pv_name = valve.getPvName()
    CAClient.put(pv_name, "Reset")
    #valve.moveTo(2) # reset valve
    time.sleep(1)
    CAClient.put(pv_name, "Open")
    #valve.moveTo(0) # open valve
    time.sleep(1)

def close_valve(valve) :
    print("Closing valve : {}".format(valve.getName()))
    pv_name = valve.getPvName()
    # valve.moveTo(1) # close valve
    CAClient.put(pv_name, "Close")
    time.sleep(1)

def print_header(str) :
    print("\n--- {} ---".format(str))
    
def purge_line():
    print_header("Purging the gas-supply line")
    pump_on()
    open_valve(gir_line_valve)
    #loop to wait for pressure in the lines to get to base vacuum
    line_pressure=10
    print("Waiting for pressure to reduce...")
    while line_pressure>8.5: #mbar
        print".",
        time.sleep(1)
        line_pressure=float(gir_line_pressure.getPosition())
        print ""+str(line_pressure)
    close_valve(gir_line_valve)
    pump_off()

def purge_ionchamber(ionchamber_valve, ionchamber_pressure):
    print_header("Purging ionchamber {}".format(extract_device_name(ionchamber_valve)))
    pump_on()
    open_valve(gir_line_valve)
    open_valve(ionchamber_valve)
    long_sleep(ionchamber_purge_time, "to purge lines")
    # logic check for leaks in the ionchamber
    base_pressure=float(ionchamber_pressure.getPosition()) # record base pressure
    close_valve(ionchamber_valve)
    print("Checking the ionchamber {} for leaks".format(ionchamber_pressure.getName()))
    long_sleep(ionchamber_leak_wait_time)
    check_pressure=float(ionchamber_pressure.getPosition()) # record pressure after dwell
    if check_pressure-base_pressure > 3:  # use math.abs here, or is sign important
        print "WARNING, suspected leak in", ionchamber2fill, "Stopping here!!!"
        # 'exit' early logic goes here ?
    close_valve(ionchamber_valve)
    close_valve(gir_line_valve)
    pump_off()

injection_equilibration_wait_time=10
def inject_gas_into_ionchamber(target_pressure, gas_valve, ionchamber_valve):
    print_header("Injecting {} into ionchamber {}".format(extract_device_name(gas_valve), 
                                                   extract_device_name(ionchamber_valve)))
    
    set_target_pressure(gir_pressure1_setpoint, target_pressure) # apply the target pressure setpoint
    open_valve(gas_valve)
    pressure_mode_control(gir_pressure1_mode) #set MFC to control mode
    open_valve(ionchamber_valve)
    long_sleep(injection_equilibration_wait_time, "for pressure to equilibrate") # dwell time for pressure to equilibrate
    # close all valves
    close_valve(ionchamber_valve)
    pressure_mode_hold(gir_pressure1_mode) # put MFC1 on hold
    close_valve(gas_valve)

def inject_helium_into_ionchamber(target_pressure_He, ionchamber_valve):
    print_header("Injecting Helium into ionchamber {}".format(extract_device_name(ionchamber_valve)))
    set_target_pressure(gir_pressure2_setpoint, target_pressure_He)
    pressure_mode_control(gir_pressure2_mode) # set MFC2 to control
    open_valve(ionchamber_valve)
    long_sleep(helium_equilibration_wait_time, "for pressure to equilibrate") # do not modify this timing
    close_valve(ionchamber_valve)
    pressure_mode_hold(gir_pressure2_mode) # set MFC2 to hold


def purge_Iref():
    purge_ionchamber(gir_iref_valve, gir_iref_pressure)

def inject_argonIntoIref(targetPressureAr):
    inject_gas_into_ionchamber(targetPressureAr, gir_argon_valve, gir_iref_valve)

def inject_heliumIntoIref(targetPressureHe):
    inject_helium_into_ionchamber(targetPressureHe, gir_iref_valve)
    

def purge_I0():
    purge_ionchamber(gir_i0_valve, gir_i0_pressure)

def inject_argonIntoI0(targetPressureAr):
    inject_gas_into_ionchamber(targetPressureAr, gir_argon_valve, gir_i0_valve)

def inject_heliumIntoI0(targetPressureHe):
    inject_helium_into_ionchamber(targetPressureHe, gir_i0_valve)

def test():
    # repeat sometimes purge and He injection 2 or 3 times to clean out the lines
    purge_line()
    purge_I0()
    inject_heliumIntoI0(targetPressureHe)
    
    # Fill with  argon
    purge_I0()
    inject_argonIntoI0(targetPressureAr)
    
    # then fill with Helium
    inject_heliumIntoI0(targetPressureHe)
    
    print 'Script finished,',ionchamber2fill,'filled successfully!'
    print 'Live long and prosper!'
