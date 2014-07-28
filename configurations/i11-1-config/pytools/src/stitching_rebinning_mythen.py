'''
Created on 17 Mar 2014

@author: Tom Arnold
'''
#script for rebinning a series of mythen scans at 2 different angles.

#this has 4 loops for 4 different temperature regimes, and names the binned data accordingly so that they can subsequently be summed more easily

 

from os import system

#the first scan number in the range is given here, subsequent runs alternate between two angles.

start1 = 278178

angle1 = ""

angle2 = ""

#50 loops indicates 100 scans.

for n in range (0,50):

                angle1 = str(start1+(2*n)) + "-mythen_1_reprocessed.dat "  #this needs to be the string at the end of your .dat files

                angle2 = str(1+start1+(2*n)) + "-mythen_1_reprocessed.dat "

                print "sample" +angle1

                # A String is added to the output file name, here i've used Hi_ to indicat high temperatures

                # the output is in the same directory as the data files, so if your data files are not in the processing directory you'll need to modify the filestructure of the output

                system ("mythenbin.py -f mean -b 0.03 " +angle1 + angle2 + "> Hi_"+str(start1+(2*n)) +"_binned.dat")

                # -f mean = averaging the bins

                # -b 0.03 = rebinning into bins of 0.03 degrees

 

#Now repeat for the next set of scans...

start2 = 278278

angle3 = ""

angle4 = ""

for n in range (0,65):

                angle3 = str(start2+(2*n)) + "-mythen_1_reprocessed.dat "

                angle4 = str(1+start2+(2*n)) + "-mythen_1_reprocessed.dat "

                print "sample" +angle3

                system ("mythenbin.py -f mean -b 0.03 " +angle3 + angle4 + "> Cool_"+str(start2+(2*n)) +"_binned.dat")

 

start3 = 278408

angle5 = ""

angle6 = ""

for n in range (0,120):

                angle5 = str(start3+(2*n)) + "-mythen_1_reprocessed.dat "

                angle6 = str(1+start3+(2*n)) + "-mythen_1_reprocessed.dat "

                print "sample" +angle5

                system ("mythenbin.py -f mean -b 0.03 " +angle5 + angle6 + "> Lo_"+str(start3+(2*n)) +"_binned.dat")

 

start4 = 278648

angle7 = ""

angle8 = ""

for n in range (0,110):

                angle7 = str(start4+(2*n)) + "-mythen_1_reprocessed.dat "

                angle8 = str(1+start4+(2*n)) + "-mythen_1_reprocessed.dat "

                print "sample" +angle7

                system ("mythenbin.py -f mean -b 0.03 " +angle7 + angle8 + "> Heat_"+str(start4+(2*n)) +"_binned.dat")