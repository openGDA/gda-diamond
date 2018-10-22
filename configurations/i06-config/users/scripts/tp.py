
class SinglePrint(object):
	msg = None;
	
	@classmethod
	def SinglePrint(cls, msg):
		if msg != SinglePrint.msg:
			SinglePrint.msg = msg;
			print msg;
		return;

			