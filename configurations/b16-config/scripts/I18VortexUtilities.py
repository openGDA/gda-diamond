def writeVortexData(absFilename):
    ##spectrum file
    ##get dat from the vortex detecttor
    vortexSpectrum = xmapMca.getData()
    print str(len(vortexSpectrum))
    for data in vortexSpectrum:
        datacounter = 0
        datalen = len(data)
        line = ''
        sfid = open(absFilename, 'a')
        for j in data:
            datacounter = datacounter + 1
            if(datacounter == datalen):
                #print 'writing new line', str(datacounter)
                line = line + str(j) 
            else:
                line = line + str(j) + ' '
            #print line
        print >> sfid, line
        sfid.close()