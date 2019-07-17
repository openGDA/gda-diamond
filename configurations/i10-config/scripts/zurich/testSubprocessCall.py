print "start of script"

import subprocess



proc = subprocess.Popen('python /dls_sw/i10/scripts/David/zurich/zurichSubprocess.py', 
			shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, )
proc.wait()
print "proc ended"
print proc.stdout
for line in proc.stdout:
	print line,
print "end of output"
for line in proc.stderr:
	print line,
print "end of errors"





print "end of script"
