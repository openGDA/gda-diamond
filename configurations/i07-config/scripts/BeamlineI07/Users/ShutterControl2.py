def shclose():
	shstatus = eh1shutterstatus.getPosition()
	if shstatus==1:
		print "Shutter was open"
	elif shstatus==3:
		print "Shutter was closed"
	else :
		print "Shutter was in undefined state"

	if shstatus != 3:
		print "Closing shutter..."
		shutter1.moveTo("Close")

		shstatus = eh1shutterstatus.getPosition()
		if shstatus==1:
			print "Shutter is open"
		elif shstatus==3:
			print "Shutter is closed"
		else :
			print "Shutter is in undefined state"

	print "\n*** Check for green lights before opening hutch! ***"

def shopen():
	shstatus = eh1shutterstatus.getPosition()
	ilstatus = eh1interlockstatus.getPosition()
	if shstatus==1:
		print "Shutter was open"
	elif shstatus==3:
		print "Shutter was closed"
	else :
		print "Shutter was in undefined state"
			
	if shstatus != 1:
		if (ilstatus==1) or (ilstatus==2):
			print "Interlocks are OK"
		else :
			if ilstatus==0:
				print "Interlocks failed"
			else :
				print "Interlocks in undefined state"
			print "Resetting interlocks..."
			shutter1.moveTo("Reset")
			ilstatus = eh1interlockstatus.getPosition()
			if ilstatus==0:
				print "Interlocks failed"
			elif (ilstatus==1) or (ilstatus==2):
				print "Interlocks are OK"
			else :
				print "Interlocks in undefined state"
		print "Opening shutter..."
		shutter1.moveTo("Open")
		shstatus = eh1shutterstatus.getPosition()	
		if shstatus==1:
			print "Shutter is open"
		elif shstatus==3:
			print "Shutter is closed"
		else :
				print "Shutter is in undefined state"

def shcl():
	shclose()

def shop():
	shopen()

alias("shclose")
alias("shopen")
alias("shcl")
alias("shop")
