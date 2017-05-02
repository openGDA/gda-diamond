#!/usr/bin/env /dls_sw/i21/software/miniconda2/envs/gdaenv/bin/python 
'''

Created on 26 Aug 2016

@author: fy65
'''
import argparse
from lookupTable.Lookup2Dto2D import forwardLookup, reverseLookup

parser = argparse.ArgumentParser(description="Process ID lookupTable for (gap, phase) <==> (polarisation, energy) in linear angular mode")
parser.add_argument('--version', action='version', version='1.0.0')
parser.add_argument('-f', action='store', dest='filename', default='./lookupTable/LinearAngle.csv',help='the filename of the lookupTable table')
subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands', dest='subparser_name', help='specify what parameters are required as inputs')

polarisationenergy_parser = subparsers.add_parser('polarisationenergy', help='lookupTable (polarisation, energy) pair')
polarisationenergy_parser.add_argument('polarisation', metavar='polarisation', type=float, help='beam polarisation in degree between 0 and -90')
polarisationenergy_parser.add_argument('energy', metavar='energy', type=float, help='beam energy in eV, upper limit=1535eV, lower limit varies from 200eV to 450eV depending on polarisationMode')
polarisationenergy_parser.set_defaults(func=reverseLookup)

gaprowphase_parser = subparsers.add_parser('gapphase', help='lookupTable (gap, phase) pair')
gaprowphase_parser.add_argument('gap', help='ID gap in mm between 20 and 70')
gaprowphase_parser.add_argument('phase', help='ID row phase position in mm between 0 and 28')
gaprowphase_parser.set_defaults(func=forwardLookup)

if __name__ == '__main__':
    args = parser.parse_args()
    if args.subparser_name == 'polarisationenergy':
        if args.filename=='' or args.filename==None:
            print args.func(args.polarisation, args.energy) # use default lookupTable table file inside the project's lookupTable package
        else:
            print args.func(args.polarisation, args.energy, filename=args.filename)  
    if args.subparser_name == 'gapphase':
        if args.filename=='' or args.filename==None:
            print args.func(args.gap, args.phase) # use default lookupTable table file inside the project's lookupTable package
        else:
            print args.func(args.gap, args.phase, filename=args.filename)
    