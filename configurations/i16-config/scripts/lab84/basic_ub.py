# If lastub fails, this script will set up a new 'test' ub matrix

try:
	rmub 'test'
	prompt = "Replaced existing 'test' ub matrix"
except:
	prompt = "Created new 'test' ub matrix" 

newub 'test'
setlat 'testsample' 3.8 3.8 7.9 90 90 90
pos idgap 7
pos euler [0, 90, 12.5345, 0, 100, 0]
pos chi 0
addref [1 0 0]
pos chi 90
addref [0 0 1]
con delta 0
con eta 0
con psi 0

print "%s %s %s" % ("*"*30, prompt, "*"*30) 
listub