import os
import string

def createFilefromRawData(filePath, headerLines=7, columnsToInclude=6):
    dirName = os.path.dirname(filePath)
    print dirName
    fileName = os.path.basename(filePath)
    print fileName
    rawFileDir = string.split(fileName, ".")[0]
    print rawFileDir
    rawFilePath = os.path.join(dirName, "mca", rawFileDir)
    print rawFilePath
    header,data = readFile(filePath, headerLines)
    dataNo = len(data)
    newDataFile = os.path.join(dirName, rawFileDir+"_corr.dat")
    newFile = open(newDataFile, "w")
    scanNo =1
    i = 0
    offset =0
    for f in range(0,len(header)):
        newFile.write(header[f])
    while(i< dataNo):
        values = string.split (data[i + offset]," ")
        scalarFile = str(rawFileDir) +"_scan_"+str(scanNo)+ "_index_"+ str(i)+"_scalar.dat"
        scalarPath = os.path.join(rawFilePath,scalarFile)
        fileLine =""
        for j in range(0,columnsToInclude):
            fileLine = fileLine + values[j] + " "
        windowValues=""
        windowTot =0
        try:
            windowValues = Xspress2Utilities.interpretScalerFile(scalarPath,0)[2]
        except:
            print "exception"
            dataNo=dataNo - i
            scanNo = scanNo + 1
            offset = offset + i
            i = 0
            continue
        #print windowValues
        for k in range(0,len(windowValues)):
            windowTot = windowTot + windowValues[k]
            fileLine = fileLine + str(windowValues[k]) + " "
        fileLine = fileLine + str(windowTot)
        print fileLine
        print >>newFile, fileLine
        i = i+ 1
    newFile.close()
        
        
    
def readFile(filePath, headerLineNumber):
    file = open(filePath)
    lines = file.readlines()
    file.close()
    dataLinesNumber = len(lines) - headerLineNumber
    headerLines = lines[:headerLineNumber]
    dataLines = lines[headerLineNumber:]
    print headerLines
    print "Finish of HEader"
    #print dataLines
    return headerLines, dataLines

createFilefromRawData('/dls/i18/data/2009/nt1237-1/39030.dat')
createFilefromRawData('/dls/i18/data/2009/nt1237-1/39031.dat')
createFilefromRawData('/dls/i18/data/2009/nt1237-1/39032.dat')
createFilefromRawData('/dls/i18/data/2009/nt1237-1/39033.dat')
createFilefromRawData('/dls/i18/data/2009/nt1237-1/39034.dat')
createFilefromRawData('/dls/i18/data/2009/nt1237-1/39035.dat')
createFilefromRawData('/dls/i18/data/2009/nt1237-1/39036.dat')
createFilefromRawData('/dls/i18/data/2009/nt1237-1/39037.dat')
createFilefromRawData('/dls/i18/data/2009/nt1237-1/39038.dat')
createFilefromRawData('/dls/i18/data/2009/nt1237-1/39039.dat')
