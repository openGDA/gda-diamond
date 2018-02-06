#!/bin/env /dls/i11/software/python/bin/python

import pidly
from optparse import OptionParser
import sys, os
# import array stuff
from numpy import *


if __name__=="__main__":
    # first we parse the options and get argument list
    #use action store_true in all cases to keep argument array constant size
    parser = OptionParser("%prog filename step [rebin_string]")
    parser.add_option("-d", "--detector", action="store_true", dest="detector", help="output separate files (x45) for each detector")
    parser.add_option("-m", "--macarms", action="store_true", dest="macarms", help="output separate rebinned files (x5) for each mac arm 1..5")
    parser.add_option("-o", "--offsets", action="store_true", dest="offsets", help="output separate rebinned files (x5) for each mac arms 1..5 using nominal offsets")
    parser.add_option("-a", "--additional", action="store_true", dest="additional", help="output a single rebin/summed file for all files in file list")
    parser.add_option("-A", "--Tadditional", action="store_true", dest="Tadditional", help="same as -a but without header lines and with xye extension")
    parser.add_option("-b", "--batch", action="store_true", dest="batch", help="output separate rebin files for each file in file list (batch rebin)")  
    parser.add_option("-B", "--Tbatch", action="store_true", dest="Tbatch", help="same as -b but without header line and with xye extension") 
    parser.add_option("-T", "--Tsingle", action="store_true", dest="Tsingle", help="rebins a single file in headlerless *.xye format")
    (options,args) = parser.parse_args()
    #
    idl_args=["","","","",""]  # <option>,<filename(s) list>,<path>,<step size>,<user string>
    option_found=0
    try:
        if options.detector:
            #only one argument expected
            idl_args[0]="-d"
            idl_args[2] = os.path.dirname(args[0])+"/" #path
            run_num=args[0].split(idl_args[2])
            run_num=run_num[1].split(".dat")
            run_num=run_num[0].replace("/"," ")
            idl_args[1]=" "+run_num
            option_found=1
        if options.macarms or options.offsets:
            #two or three arguments expected
            print "macarms or offsets"
            idl_args[2] = os.path.dirname(args[0])+"/" #path
            run_num=args[0].split(idl_args[2])
            run_num=run_num[1].split(".dat")
            run_num=run_num[0].replace("/"," ")
            idl_args[1]=" "+run_num
            #
            idl_args[3]=" "+args[1]
            if len(args)==3:
               idl_args[4]=" "+args[2]
            if options.macarms:
               idl_args[0]="-m"
            if options.offsets:
               idl_args[0]="-o"
            option_found=1
        if options.additional or options.batch or options.Tadditional or options.Tbatch:
            #three or four arguments expected
            print "additional or batch"
            idl_args[2] = os.path.dirname(args[1])+"/" #path
            run_num=args[1].split(idl_args[2])
            run_num=run_num[1].split(".dat")
            run_num=run_num[0].replace("/"," ")
            idl_args[1]=" "+run_num
            #
            run_num=args[0].replace(","," ")
            idl_args[1]=idl_args[1]+" "+run_num
            #
            idl_args[3]=" "+args[2]
            if len(args)==4:
               idl_args[4]=" "+args[3]
            if options.additional:
               idl_args[0]="-a"
            if options.Tadditional:
               idl_args[0]="-A"
            if options.batch:
               idl_args[0]="-b"
            if options.Tbatch:
               idl_args[0]="-B"
            option_found=1
        if option_found==0 or options.Tsingle:
             #default single file rebin
             #expect two or three arguments
             print "default"
             idl_args[2] = os.path.dirname(args[0])+"/" #path
             run_num=args[0].split(idl_args[2])
             run_num=run_num[1].split(".dat")
             run_num=run_num[0].replace("/"," ")
             idl_args[1]=" "+run_num
             #
             idl_args[3]=" "+args[1]
             if len(args)==3:
                idl_args[4]=" "+args[2]
             idl_args[0]="-b"
             if options.Tsingle:
                idl_args[0]="-B"
    except IndexError:
        parser.error("Incorrect number of arguments")
    print "idl arguments"
    print idl_args
    #
    ret=""
    idl = pidly.IDL()
    idl.pro('.compile /dls/i11/software/gda/config/idlobjects/rebin_idl.pro')
    idl.pro('rebin_idl',idl_args[0],idl_args[1],idl_args[2],idl_args[3],idl_args[4],ret)
    idl.close()
    print ret


