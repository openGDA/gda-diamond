

pointArray = [ [1.0,   2.0,   3.0,   4.0,   5.0,   6.0],
			 [10.0,  20.0,  30.0,  40.0,  50.0,  60.0],
			 [100.0, 200.0, 300.0, 400.0, 500.0, 600.0]	];
			 

srsHeader=[" &SRS\n", " SRSRUN=null,SRSDAT=null,SRSTIM=null,\n", " SRSSTN='null',SRSPRJ='null    ',SRSEXP='null    ',\n", " SRSTLE='                                                            ',\n", " SRSCN1='        ',SRSCN2='        ',SRSCN3='        ',\n", " &END\n"];
try:
	fileName = "/dls_sw/i06/logs/try.dat"
	print fileName
	fh=open(fileName, 'w');

	#SRS Header
	for i in range(len(srsHeader)):
		fh.write(srsHeader[i]);

	titleLine='%(v1)s \t %(v2)s \t %(v3)s \t %(v4)s \t %(v5)s \t %(v6)s \n' %{'v1': 'Value 1', 'v2': 'Value 2', 'v3': 'Value 3', 'v4': 'Value 4','v5': 'Value 5','v6': 'Value 6'};
	fh.write(titleLine);
		
	for i in range(len(pointArray)): #0 1 2
		newLine='%(v1).8f \t %(v2).8f \t %(v3).8f \t %(v4).8f \t %(v5).8f \t %(v6).8f \n' %{'v1': pointArray[i][0], 'v2': pointArray[i][1], 'v3': pointArray[i][2], 'v4': pointArray[i][3],'v5': pointArray[i][4],'v6': pointArray[i][5]};
		fh.write(newLine);

	fh.close();
except IOError:
	print "File IOError.";
except:
	print "Aa, something wrong.";

