print("\nRunning 'ionchamber_autofill.py")

ionchamber2fill="I0"
targetPressureAr=35 #mbar
targetPressureHe=1800 #mbar

ionchamber_purge_time=20.00 #30
ionchamber_leak_wait_time=10.0 #10
injection_equilibration_wait_time=20
helium_equilibration_wait_time=10.0

PRESSURE_CONTROL="Control"
PRESSURE_HOLD="Hold"
VALVE_OPEN = "Open"
VALVE_CLOSE = "Close"
VALVE_RESET = "Reset"

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
    gir_vacuum_pump.moveTo(VALVE_RESET)
    gir_vacuum_pump.moveTo(VALVE_OPEN)  # pump on
    time.sleep(1)

def pump_off():
    print("Switching vacuum pump off")
    gir_vacuum_pump.moveTo(VALVE_CLOSE) # pump off
    time.sleep(1)

def open_valve(valve) :
    print("Opening valve : {}".format(valve.getName()))
    pv_name = valve.getPvName()
    CAClient.put(pv_name, VALVE_RESET)
    #valve.moveTo(2) # reset valve
    time.sleep(1)
    CAClient.put(pv_name, VALVE_OPEN)
    #valve.moveTo(0) # open valve
    time.sleep(1)

def close_valve(valve) :
    print("Closing valve : {}".format(valve.getName()))
    pv_name = valve.getPvName()
    # valve.moveTo(1) # close valve
    CAClient.put(pv_name, VALVE_CLOSE)
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
    device_name = extract_device_name(ionchamber_valve)
    print_header("Purging ionchamber {}".format(device_name))
    pump_on()
    open_valve(gir_line_valve)
    open_valve(ionchamber_valve)
    long_sleep(ionchamber_purge_time, "to purge lines")
    # logic check for leaks in the ionchamber
    base_pressure=float(ionchamber_pressure.getPosition()) # record base pressure
    close_valve(ionchamber_valve)
    print("Checking the ionchamber {} for leaks".format(ionchamber_pressure.getName()))
    long_sleep(ionchamber_leak_wait_time)
    
    check_pressure=float(ionchamber_pressure.getPosition()) # pressure after dwell
    if math.fabs(check_pressure-base_pressure) > 3 :
        print("----- WARNING, suspected leak in "+device_name+" !!! -----")

    close_valve(ionchamber_valve)
    close_valve(gir_line_valve)
    pump_off()

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

# Dictionaries to return valve and pressure readout scannables for i0, it, iref, i1 ionchambers
valves_dict = {"i0":gir_i0_valve, "it":gir_it_valve, "iref":gir_iref_valve, "i1":gir_i1_valve, "argon":gir_argon_valve}
pressures_dict = {"i0":gir_i0_pressure, "it":gir_it_pressure, "iref":gir_iref_pressure, "i1":gir_i1_pressure}

# Return valve scannable for i0, it, iref or i1 ionchamber
def get_valve(chamber_name) :
    if chamber_name.lower() not in valves_dict :
        raise Exception("Could not get valve scannable for "+chamber_name)
    return valves_dict[chamber_name.lower()]

# Return pressure readout scannable for i0, it, iref or i1 ionchamber
def get_pressure_readout(chamber_name) :
    if chamber_name.lower() not in pressures_dict :
        raise Exception("Could not get pressure readout scannable for "+chamber_name)
    return pressures_dict[chamber_name.lower()]

# Purge i0, it, iref, i1
def purge(chamber_name) :
    purge_ionchamber(get_valve(chamber_name), get_pressure_readout(chamber_name))

# inject Argon into i0, it, iref, or i1
def inject_argon(chamber_name, target_pressure_Ar):
    inject_gas_into_ionchamber(target_pressure_Ar, gir_argon_valve, get_valve(chamber_name))

# inject He into i0, it, iref or i1
def inject_helium(chamber_name, target_pressure_He):
    inject_helium_into_ionchamber(target_pressure_He, get_valve(chamber_name))


print("""Adding ionchamber gas fill and purge commands. Example command usage : 
  purge_line()  - purge the gas supply line
  purge('i0')   - purge I0 ionchamber
  inject_argon('it', 80)    - fill It ionchamber with 80mbar of Argon
  inject_helium('it', 1800) - fill It ionchamber with 1800mb of Helium""")

