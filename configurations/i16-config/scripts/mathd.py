from math import *

def sind(x):
	return sin(x*pi/180.)

def cosd(x):
	return cos(x*pi/180.)

def tand(x):
	return tan(x*pi/180.)

def interplin(xTable,yTable,x):
	if len(xTable)!=len(yTable):
		return 'Wrong table input: x and y have different sizes'
#		raise Exception('Wrong table input: x and y have different sizes')
	if x<min(xTable) or x>max(xTable):
		print 'x out of range: x: %f, min(xTable): %f, max(xTable): %f' % (x, min(xTable), max(xTable))
		return None
#		raise Exception('x out of range: x: %f, min(xTable): %f, max(xTable): %f' % (x, min(xTable), max(xTable)))  #  Too risky without thorough testing --- RobW
	for i in range(len(xTable)):
		if x==xTable[i]:
			yy = yTable[i]
			return yy
		elif xTable[i]==min(xTable):
			i1 = i
		elif xTable[i]==max(xTable):
			i2 = i
	for i in range(len(xTable)):
		if xTable[i]>xTable[i1] and xTable[i]<x:
			i1 = i
		if xTable[i]<xTable[i2] and xTable[i]>x:
			i2 = i
	aa1 = (x-xTable[i1])/(xTable[i2]-xTable[i1])
	aa2 = (xTable[i2]-x)/(xTable[i2]-xTable[i1])
	yy = aa2*yTable[i1]+aa1*yTable[i2]
	return yy

def ascii2matrix(filename):
	f=open(filename)
	AA = f.read()
	f.close()
	count = 1
#	while count > 0:
	AA = AA.replace('\t\t','\t',count)
#	print "count=", count
	AA = AA.replace('\t\n','\n')
	AA = AA.split('\n')
	A=[]
	for i in range(len(AA)):
		aa = AA[i].split('\t')
#		print aa
		try:
			for j in range(len(aa)):
				aa[j] = float(aa[j])
			A.append(aa)
		except:
			pass
	exec('A= [[r[col] for r in A] for col in range(len(A[0]))]')
	return A

