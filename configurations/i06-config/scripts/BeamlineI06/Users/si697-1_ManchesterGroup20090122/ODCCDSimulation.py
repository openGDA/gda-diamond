#!/bin/env python2.4
#
# require a fixed version of serial_sim to be imported
from pkg_resources import require
require("dls.serial_sim==0.0")
from dls.serial_sim import serial_device
# create a class that represents the device
# This device has 3 integer values, a, b, and c
# They can be set by sending "a=100"
# They can be read by sending "a"
# Unrecognised commands reply "ERROR"
from src import serial_device
import struct
class my_device(serial_device):
    # set the terminator to control when a string is passed to reply
    InTerminator = "\r\n"
    OutTerminator="\n\r"
    Terminator="\n\r"
    debug = True
    # create an internal dict of values
    vals = { "a":5, "b":6, "c":7 }
    loginName="gda"
    binary = False
    connected = False
    # implement a reply function            
    def reply(self, command):
        print "recv: -" + command + "-"
        if "=" in command:
            # set a value in the internal dictionary
            split = command.split("=")
            # if val isn't in the dict, return error
            if not self.vals.has_key(split[0]):
                return "ERROR"
            try:
                # set the dictionary to the right value
                self.vals[split[0]] = int(split[1])
                # returning None means nothing will be sent back
                return None
            except:
                # if there was an error (like a non integer value)
                return "ERROR"
        else:
            try:
                # report the value as a string
                if command == "binary":
                    self.binary=True
                elif command == "disconnect":
                    self.connected = False
                elif command == "temp":
                    d = struct.pack("ccccccciiiiiiiiiiii","(","D","A","T","A",")",":",0,0,0,4,1,2,3,4,0,0,0,0)
                    return d
            except:
                # if it wasn't in the internal dictionary
                return "ERROR"

    def onHandlerSetup(self, handler):
        "Overwrite to do something when a connection is made. e.g. write a WELCOME banner "
        handler.request.send("Welcome client "+ self.loginName +self.Terminator)
        handler.request.send("Connection restored." +self.Terminator)
        self.connected = True


if __name__ == "__main__":
    # little test function that runs only when you run this file
    dev = my_device()
    dev.start_ip(9120)
#    dev.start_debug(9006)
    # do a raw_input() to stop the program exiting immediately
    raw_input()
