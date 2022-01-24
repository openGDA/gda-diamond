def Denary2Binary(n):
	'''convert denary integer n to binary string bStr'''
	bStr = ''
	if n < 0:  raise ValueError, "must be a positive integer"
	if n == 0: return '0'
	while n > 0:	
		bStr = str(n % 2) + bStr
		n = n >> 1
	return bStr
 
def int2bin(n, count=8):
	"""returns the binary of integer n, using count number of digits"""
	return "".join([str((n >> y) & 1) for y in range(count-1, -1, -1)])

 