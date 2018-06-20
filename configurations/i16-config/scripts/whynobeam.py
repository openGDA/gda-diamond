################################################################################
#Check beamline status and possible problems suggesting solutions to the users #
################################################################################
#CV 2010
################################################################################
#Program calls: whynobeam()
################################################################################
class whynobeam:
    '''        Check I16 Status
    type: whynobeam(table_number) 
    table_number: None=All tables; 0=default; 1=table1.dat'''
    def __init__(self,*tabnum):
        self=self.i16status(tabnum)
    def __call__(self):
        return self
    def __repr__(self):
        return ' '

################################################################################
#Read device from table and create device objects
################################################################################

    def readdevices(self,devicename,devicecode,devicebest,devicetype):
        '''Read device list from a file and create device obj'''
        self.devicename=devicename
        self.devicecode=devicecode
        self.devicebest=devicebest
        self.devicetype=devicetype
        if float(self.devicetype)>0:
            devicecode=str(devicecode) + '()'
        elif float(self.devicetype)<0:
            devicecode="caget('" + str(devicecode)+"')"
        return devicename,devicecode,devicebest,devicetype
    
################################################################################
#Write device to table.dat
################################################################################
    
    def writedev(self,devicename,devicecode,devicebest,devicetype):
        '''Adds a new device to the table: 'device' code best type(1 for val=0,1; 2 val>best; 3 for val<best; 4 val=x, <0 for epix code)'''
        try:
            file = open('table1.dat', 'r').readlines()
            nd=[]
            nd=[devicename,devicecode,devicebest,devicetype]
            for line in file:
                if line[-1] == "\n":
                    nd=str(devicename) + ' ' + str(devicecode) + ' ' +str(devicebest) + ' ' + str(devicetype) 
                else:
                    nd='\n' + str(devicename) + ' ' + str(devicecode) + ' ' +str(devicebest) + ' ' + str(devicetype) 
            file = open('table1.dat','a')
            file.write(nd)
            print str(nd) + " <-- new device added\n"
            return 
        except:
            print 'Error writing table file!'
            file.close()
            file.close()  
    
################################################################################
#Read file table.dat
################################################################################
    
    def opendevtable(self,filename):
        '''Read file table.dat with the list of devices'''
        try:
            file = open(filename, "r").readlines()
            KEYWORDS = ['#']
            table=[]; countskip=0;
            for line in file:
                words_list = line.split()
                for x in range(0, len(KEYWORDS)):
                    if str(words_list[0][0])==KEYWORDS[x]:
                        countskip=1
                for x in range(0, len(KEYWORDS)):
                    if str(words_list[0][0])!=KEYWORDS[x]:
                        countskip=0
                if countskip!=1:
                    table.append(words_list)
            return table
        except:
            print 'Error opening table file!'
        file.close()
    
################################################################################
#Create dictionaries of devices and values
################################################################################
    
    def readdev(self,table):
        '''Create dictionaries of devices and values'''
        out=(); new=[]; dev={}; best={}; type_d={};  type_1={}; type_2={}; type_3={}; type_4={}; dev1={}; dev2={}; dev3={}; dev4={}; best1={}; best2={}; best3={}; best4={}; type_5={}; dev5={}; best5={}; type_6={}; dev6={}; best6={}; type_7={}; dev7={}; best7={}; type_8={}; dev8={}; best8={}; type_9={}; dev9={}; best9={}
        code={}; code1={}; code2={}; code3={}; code4={}; code5={}; code6={}; code7={}; code8={}; code9={};
        for i in range(0, len(table)):
            if table[i]==None:
                pass
            else:
                new=self.readdevices(table[i][0],table[i][1],str(table[i][2]),str(table[i][3]))
                dev[new[0]]=eval(new[1])
                code[new[0]]=str(new[1])
                best[new[0]]=float(new[2])
                type_d[new[0]]=float(new[3])
            dev1=dev.copy(); dev2=dev.copy(); dev3=dev.copy(); dev4=dev.copy(); best1=best.copy(); best2=best.copy(); best3=best.copy(); best4=best.copy();
            item1='' ; item2='' ; item3=''; item4=''; dev5=dev.copy(); best5=best.copy(); item5=''; dev6=dev.copy(); best6=best.copy(); item6=''; dev7=dev.copy(); best7=best.copy(); item7=''; dev8=dev.copy(); best8=best.copy(); item8='';dev9=dev.copy(); best9=best.copy(); item9=''
            code1=code.copy(); code2=code.copy(); code3=code.copy(); code4=code.copy(); code5=code.copy(); code6=code.copy();code7=code.copy();code8=code.copy();code9=code.copy();    
        for x in range(0, len(dev1)):
            if type_d.values()[x] != 1:
                item1=type_d.keys()[x]
                del dev1[item1]
                del best1[item1]
                del code1[item1]
        for x in range(0, len(dev2)):
            if type_d.values()[x] != 2:
                item2=type_d.keys()[x]
                del dev2[item2]
                del best2[item2]
                del code2[item2]
        for x in range(0, len(dev3)):
            if type_d.values()[x] != 3:
                item3=type_d.keys()[x]
                del dev3[item3]
                del best3[item3]
                del code3[item3]
        for x in range(0, len(dev4)):
            if type_d.values()[x] != 4:
                item4=type_d.keys()[x]
                del dev4[item4]
                del best4[item4]
                del code4[item4]
        for x in range(0, len(dev5)):
            if type_d.values()[x] != -1:
                item5=type_d.keys()[x]
                del dev5[item5]
                del best5[item5]
                del code5[item5]
        for x in range(0, len(dev6)):
            if type_d.values()[x] != -2:
                item6=type_d.keys()[x]
                del dev6[item6]
                del best6[item6]
                del code6[item6]
        for x in range(0, len(dev7)):
            if type_d.values()[x] != -3:
                item7=type_d.keys()[x]
                del dev7[item7]
                del best7[item7]
                del code7[item7]
        for x in range(0, len(dev8)):
            if type_d.values()[x] != -4:
                item8=type_d.keys()[x]
                del dev8[item8]
                del best8[item8]
                del code8[item8]
        for x in range(0, len(dev9)):
            if type_d.values()[x] != 6:
                item9=type_d.keys()[x]
                del dev9[item9]
                del best9[item9]
                del code9[item9]
        out=(dev1,dev2,dev3,best1,best2,best3,dev4,best4,dev5,best5,dev6,best6,dev7,best7,dev8,best8,dev9,best9,code1,code2,code3,code4,code5,code6,code7,code8,code9)
#        print out # prints the dictionary of devices and values
        return out 
    
################################################################################
#Check for potential problems and give suggestions
#type= 1 for val=0,1; 2 for val>best; 3 for val<best; 4 for val=x; <0 for epix code
#for epix code: type= -1 for val=0,1; -2 for val>best; -3 for val<best; -4 for val=x; <0 
#type=6 dev()=[val1,val2] , example: attenuation, it takes only the 1st value
################################################################################
   
    def checktype(self,outdev):
        '''Check for potential problems and give suggestions'''
        errors=0
#        type 1
        print "\nList of possible actions to be taken:\n" + "--------------------------------------------------\n"
        for x in range(0, len(outdev[0])):
            if outdev[0].items()[x]!=outdev[3].items()[x]:
                errors += 1
#                print "- " + str(outdev[0].keys()[x])+ " is " + str(round(outdev[0].values()[x],4)) + ", Open it to start the measurements, type: pos " + str(outdev[0].keys()[x]) + " 1"
                print "-> " + str(outdev[0].keys()[x])+ " is " + str(round(outdev[0].values()[x],4)) + ", Open it to start the measurements, type: pos " + str(outdev[18].values()[x]).strip('()') + ' ' + str(outdev[3].values()[x]).strip('.0')
#        type 2
        for x in range(0, len(outdev[1])):
            if outdev[1].items()[x]<outdev[4].items()[x]:
                print "-> " + str(outdev[1].keys()[x])+ " is " + str(round(outdev[1].values()[x],4)) + ", "+str(outdev[1].keys()[x]) +" may be too small \nOpen it to start the measurements, type: pos " + str(outdev[19].values()[x]).strip('()') + " " + str(outdev[4].values()[x])
                errors += 1
#        type 3
        for x in range(0, (len(outdev[2]))):
            if outdev[2].items()[x]>outdev[5].items()[x]:
                print "-> " + str(outdev[2].keys()[x])+ " is " + str(round(outdev[2].values()[x],4)) + ", "+str(outdev[2].keys()[x]) +" may be too large\nDecrease it to start the measurements, type: pos " + str(outdev[20].values()[x]).strip('()') + " " + str(outdev[5].values()[x])
                errors += 1
#        type 4
        for x in range(0, (len(outdev[6]))):
            if round(outdev[6].values()[x],4)==outdev[7].values()[x]:
                print "-> " + str(outdev[6].keys()[x]) + " is " + str(round(outdev[6].values()[x],4)) 
#                errors += 1
            else:
                print "-> " + str(outdev[6].keys()[x]) + " is " + str(round(outdev[6].values()[x],4)) + ", Check it to start the measurements"
#        type 6
        for x in range(0, (len(outdev[16]))):
#            print outdev[16].values()[x][0] #print check for atten=[atten, transm]
            if round(outdev[16].values()[x][0],4)==outdev[17].values()[x]:
                print "-> " + str(outdev[16].keys()[x]) + " is " + str(round(outdev[16].values()[x][0],4))
#                errors += 1
            else:
                print "-> " + str(outdev[16].keys()[x]) + " is " + str(round(outdev[16].values()[x][0],4)) + ", Check it to start the measurements"
#        type -1
        for x in range(0, (len(outdev[8]))):
            if outdev[8].items()[x][0]!=outdev[9].items()[x][0] or str(outdev[8].items()[x][1])!=str(round(outdev[9].items()[x][1],1)):
                print str(outdev[8].items()[x][1]),str(outdev[9].items()[x])
#                print "- " + str(outdev[8].keys()[x])+ " is " + str(round(outdev[8].values()[x],4)) + ", Open it to start the measurements, type: pos " + str(outdev[8].keys()[x]) + " 1"
                print "-> " + str(outdev[8].keys()[x])+ " is " + str(round(outdev[8].values()[x],4)) + ", Open it to start the measurements, type: caput(" + str(outdev[22].values()[x]).strip('caget(').strip(')') + ',' + str(outdev[9].values()[x]).strip('.0') + ')'
                errors += 1
            else:
                print "-> " + str(outdev[8].keys()[x]) + " is open."
#        type -2
        for x in range(0, len(outdev[10])):
            if outdev[10].items()[x]<=outdev[11].items()[x]:
#                print "- " + str(outdev[10].keys()[x])+ " is " + str(round(outdev[10].values()[x],4)) + ", "+str(outdev[10].keys()[x]) +" may be too small \nOpen it to start the measurements, type: pos " + str(outdev[10].keys()[x]) + " " + str(outdev[11].values()[x])
                print "-> " + str(outdev[10].keys()[x])+ " is " + str(round(outdev[10].values()[x],2)) + ", "+str(outdev[10].keys()[x]) +" may be too small \nOpen it to start the measurements, type: caput(" + str(outdev[23].values()[x]).strip('caget(').strip(')') + "," + str(outdev[11].values()[x]) + ")"
                errors += 1
#        type -3
        for x in range(0, (len(outdev[12]))):
            if outdev[12].items()[x]>outdev[13].items()[x]:
#                print "- " + str(outdev[12].keys()[x])+ " is " + str(round(outdev[12].values()[x],4)) + ", "+str(outdev[12].keys()[x]) +" may be too large\nDecrease it to start the measurements, type: pos " + str(outdev[12].keys()[x]) + " " + str(outdev[13].values()[x])
                print "-> " + str(outdev[12].keys()[x])+ " is " + str(round(outdev[12].values()[x],2)) + ", "+str(outdev[12].keys()[x]) +" may be too large\nDecrease it to start the measurements, type: caput(" + str(outdev[24].values()[x]).strip('caget(').strip(')') + "," + str(outdev[13].values()[x]) + ")"
                errors += 1
#        type -4
        for x in range(0, (len(outdev[14]))):
            if round(outdev[14].values()[x],4)==outdev[15].values()[x]:
                print "-> " + str(outdev[14].keys()[x])+ " is " + str(round(outdev[14].values()[x],4)) 
#                errors += 1
            else:
                print "-> " + str(outdev[14].keys()[x]) + " is " + str(round(outdev[14].values()[x],4)) + ", Check it to start the measurements"
        return errors
    
################################################################################
#Summary table of checked devices and best values
#Devicename            ---->            DeviceValue          ( DeviceBestValue )
################################################################################
    
    def summary(self,outdev,errors):
        '''Summary table of checked devices and best values'''
        if errors==0:
            goodness="\n--------------------------------------------------" + "\nEverything is OK, please check beam current in the ring if no beam is available.\nIf the problem still persists, \nCall your local contact, the numbers are on the whiteboard.\n--------------------------------------------------"      
        else:
            goodness="\n--------------------------------------------------" + "\nPossible errors: " + str(errors) +"\n--------------------------------------------------"
        print goodness
        print '\nDevice Name'.ljust(20) + " ---->  " + "Value".ljust(10) + " ( " + "Best Value".ljust(7) + " )\n"
        for x in range(0, len(outdev[0])):
            print str(outdev[0].keys()[x]).ljust(20) + " ---->  " + str(round(outdev[0].values()[x],3)).ljust(10) + " ( " + '= ' + str(outdev[3].values()[x]).strip('.0').ljust(7) + " )"
        for x in range(0, len(outdev[1])):
            print str(outdev[1].keys()[x]).ljust(20) + " ---->  " + str(round(outdev[1].values()[x],3)).ljust(10) + " ( " + '> ' + str(outdev[4].values()[x]).ljust(7) + " )"
        for x in range(0, len(outdev[2])):
            print str(outdev[2].keys()[x]).ljust(20) + " ---->  " + str(round(outdev[2].values()[x],3)).ljust(10) + " ( " + '< ' + str(outdev[5].values()[x]).ljust(7) + " )"
        for x in range(0, len(outdev[6])):
            print str(outdev[6].keys()[x]).ljust(20) + " ---->  " + str(round(outdev[6].values()[x],3)).ljust(10) + " ( " + '  ' + str(outdev[7].values()[x]).ljust(7) + " )"
        for x in range(0, len(outdev[8])):
            print str(outdev[8].keys()[x]).ljust(20) + " ---->  " + str(round(outdev[8].values()[x],3)).ljust(10) + " ( " + '= ' + str(outdev[9].values()[x]).strip('.0').ljust(7) + " )"
        for x in range(0, len(outdev[10])):
            print str(outdev[10].keys()[x]).ljust(20) + " ---->  " + str(round(outdev[10].values()[x],3)).ljust(10) + " ( " + '> ' + str(outdev[11].values()[x]).ljust(7) + " )"
        for x in range(0, len(outdev[12])):
            print str(outdev[12].keys()[x]).ljust(20) + " ---->  " + str(round(outdev[12].values()[x],3)).ljust(10) + " ( " + '< ' + str(outdev[13].values()[x]).ljust(7) + " )"
        for x in range(0, len(outdev[14])):
            print str(outdev[14].keys()[x]).ljust(20) + " ---->  " + str(round(outdev[14].values()[x],3)).ljust(10) + " ( " + '  ' + str(outdev[15].values()[x]).ljust(7) + " )"
        for x in range(0, len(outdev[16])):
            print str(outdev[16].keys()[x]).ljust(20) + " ---->  " + str(round(outdev[16].values()[x][0],3)).ljust(10) + " ( " + '  ' + str(outdev[17].values()[x]).ljust(7) + " )"
        return 
    
################################################################################
#Tells which detector is in use
################################################################################

    def detectorpos(self,offset):
        '''Tells which detector is in use'''
        self.offset=offset
#        detector_reference={'pilatus':9.5,'diode':54.4,'APD':2.6,'vortex':-14.8,'camera':34.2,'ccd':70}
        detector_reference={'pilatus':do.pil,'diode':tthp.diode,'APD':tthp.apd,'vortex':tthp.vortex,'camera':tthp.camera,'ccd':tthp.ccd}
        detector_angle=tthp()-offset
        deltaaxisoffset=delta_axis_offset()-offset
        tolerance=3
        if offset == 0:
            if deltaaxisoffset == detector_reference['pilatus']:
                print 'Pilatus100k is in use'
            else:
                if round(detector_reference['diode'],1) == round(detector_angle,1):
                    print 'Diode is in use'
                elif round(detector_reference['APD'],1) == round(detector_angle,1):
                    print 'APD is in use'
                elif round(detector_reference['camera'],1) == round(detector_angle,1):
                    print 'Camera is in use'
                elif round(detector_reference['vortex'],1) == round(detector_angle,1):
                    print 'Vortex is in use'
                elif round(detector_reference['ccd'],1) == round(detector_angle,1):
                    print 'ccd is in use'
                else:
                    print 'No detector position can be recognised, please check detector offsets'
        elif offset != 0:
            newdetector_angle=offset
            newdetector_angle1=newdetector_angle+tolerance
            newdetector_angle2=newdetector_angle-tolerance
            if detector_reference['pilatus']-tolerance <= (deltaaxisoffset+offset) <= detector_reference['pilatus']+tolerance:
                print 'Pilatus detector is in use'
            else:
                if round(newdetector_angle2,1) <= round(detector_reference['diode'],1) <= round(newdetector_angle1,1):
                    print 'Diode is in use'
                elif round(newdetector_angle2,1) <= round(detector_reference['APD'],1) <= round(newdetector_angle1,1):
                    print 'APD is in use'
                elif round(newdetector_angle2,1) <= round(detector_reference['camera'],1) <= round(newdetector_angle1,1):
                    print 'Camera is in use'
                elif round(newdetector_angle2,1) <= round(detector_reference['vortex'],1) <= round(newdetector_angle1,1):
                    print 'Vortex is in use'
                elif round(newdetector_angle2,1) <= round(detector_reference['ccd'],1) <= round(newdetector_angle1,1):
                    print 'ccd is in use'
                else:
                    print 'No detector position can be recognised, please check detector offsets'
            
################################################################################
#Tells if analyzer is in
################################################################################
    
    def analyzerpos(self):
        offset=0
        '''Tells if analyzer is in'''
        zetapi=zp(); tihpi=thp()
        if abs(zetapi)> -8. and (-0.1<=tihpi<=0.1 or 179.5<=tihpi<=180.5):
            print "\nAnalyzer is out"
            offset=0
            detector=self.detectorpos(offset)
        else:
            print "\nAnalyzer ("+ pol.crystal + ") is in: zp= " + str(zetapi) + " and thp= " + str(round(tihpi,3))
            print 'stokes= ' + str(stokes()) + ', psic= ' + str(psic()) + ', azimuthal reference= ' + '[' + str(azir()[0]) + ',' + str(azir()[1]) + ',' + str(azir()[2]) + ']'
            offset=tthp_detoffset()
            detector=self.detectorpos(offset)
        return offset
    
################################################################################
#Tells if phase plate is in
################################################################################
    
    def phaseplate(self):
        '''Tells if phase plates are in'''
        if round(ppx(),1)==22 and round(ppy(),1)==8:
            print "Phase plates are out"
        else:
            print "Phase plates are in"

################################################################################
#Tells if minimirrors are in
################################################################################
    
    def minimir(self):
        '''Tells if minimirrors are in'''
        if round(m3x(),1)==-4 and round(m4x(),1)==4 and round(m3pitch(),1)==0 and round(m3pitch(),1)==0:
            print "minimirros are out"
        else:
            print "minimirrors are in"
 
################################################################################
#Tells what is the current energy and relative information
################################################################################
    
#    def energyinfo(self):
#        '''Tells what is the current energy'''
#	mirrorcoating=en.coating()
#	print "\nCurrent Energy: " + str(round(en(),5)) 
#	print "With mirror coating: " + str(mirrorcoating) + " Selectect harmonic: " + str(uharmonic()) + " with idgap: " + str(idgap())
    
   
################################################################################
#Default device list
################################################################################
#device code bestvalue type(1 for val=0,1, 2 val>best, 3 for val<best, 4 val=x, <0 for epix code, val=6 dev()=[val1,val2]) 
#Examples
#shutter2 shutter 1 1 
#SampleSlits_hgap2 s5hgap 0.001 2
#IonChamber2 ic1 800 4
#attenuation2 atten 0 6
#New devices added from this line
    
    def devlist(self):
        '''Default device list''' 
        table=[]
#        table=[['shutter', 'shutter', 1, 1],['fastshutter', 'x1', 1, 1],['IonChamber', 'ic1', 400, 4],['attenuation', 'atten', 0.0, 6],['SampleSlits_htrans', 's5htrans', 0.0, 4],['SampleSlits_vtrans', 's5vtrans', 0.0, 4],['DetectorSlits_htrans', 's5htrans', 0.0, 4],['DetectorSlits_vtrans', 's5vtrans', 0.0, 4],['SampleSlits_hgap', 's5hgap', 0.001, 2],['SampleSlits_vgap', 's5vgap', 0.001, 2],['DetectorSlits_hgap', 's5hgap', 0.001, 2],['DetectorSlits_vgap', 's5vgap', 0.001, 2],['d2', 'd2', 1, 1],['FronEndAbsorber1', 'absorber1', 1, 1],['FrontEndAbsorber2', 'absorber2', 1, 1],['mu','mu',0,4]]
        table=[['shutter', 'shutter', 1, 1],['RingCurrent', 'rc', 300, 4],['fastshutter_x1', 'x1', 1, 1],['fastshutter_x2', 'x2', 0, 4],['IonChamber', 'ic1', 400, 4],['attenuation', 'atten', 0.0, 6],['SampleSlits_hgap', 's5xgap', 0.001, 2],['SampleSlits_vgap', 's5ygap', 0.001, 2],['DetectorSlits_hgap', 's6xgap', 0.01, 2],['DetectorSlits_vgap', 's6ygap', 0.005, 2],['d2', 'd2', 1, 1],['FrontEndAbsorber1', 'absorber1', 1, 1],['FrontEndAbsorber2', 'absorber2', 1, 1],['mu','mu',0,4],['monitor','BL16I-DI-BPM-01:DIAG.VAL',-2.0,-1]]
        return table

################################################################################
#Program add_table to add new table of devices
################################################################################
    
    def addtable(self, tablenum):
        '''add tables'''
        if tablenum !=():
            tablenum=tablenum[0]
        table=[]; table0=[]; table1=[]; table2=[]; table3=[]; table4=[]; table5=[]; table6=[]; 
        table0=self.devlist()
        table1=self.opendevtable('/dls_sw/i16/software/gda/config/scripts/table1.dat')
#        add new tables here:
#        table2=self.opendevtable('/dls_sw/i16/software/gda/config/scripts/table2.dat')
#        table3=self.opendevtable('/dls_sw/i16/software/gda/config/scripts/table3.dat')
        if tablenum==0:
            table=table0
        elif tablenum==1:
            table=table1
        elif tablenum==2:
            table=table2
        elif tablenum==3:
            table=table3
        elif tablenum==4:
            table=table4
        elif tablenum==5:
            table=table5
        elif tablenum==6:
            table=table6
        else:
            table=table0+table1+table2+table3+table4+table5+table6
        return table

################################################################################
#Program i16status: whynobeam main function
################################################################################
    
    def i16status(self,tabnum):
        try:
            table=self.addtable(tabnum)
            outdev=self.readdev(table)
            errors=self.checktype(outdev)
            summ=self.summary(outdev,errors)
            an=self.analyzerpos()
            phaseplatepos=self.phaseplate()
            minimir=self.minimir()
        except Exception, reason:
            print 'Exception block!'
            print reason
        return 
       
#whynobeam() 
################################################################################
#End program
################################################################################
