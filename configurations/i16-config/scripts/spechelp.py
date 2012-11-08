from gda.jython.commands.GeneralCommands import alias

class MessageClass:
	'Creates object that exist only to return string messages'
	def __init__(self,message_string):
		self.message_string=message_string
	def __call__(self, *p1):
		return self.message_string
	def __repr__(self):
		return self.__call__(0)

ct=MessageClass(" ==="+ " This is not SPEC! Try 'pos t 1'"); alias('ct')
umv=MessageClass(" ==="+ " This is not SPEC! Try 'pos device position'"); alias('umv')
mv=MessageClass(" ==="+ " This is not SPEC! Try 'pos device position'"); alias('mv')
umvr=MessageClass(" ==="+ " This is not SPEC! Try 'inc device position'"); alias('umvr')
#dscan=lup=MessageClass(" ==="+ " This is not SPEC! Use scancn (type help scancn)"); alias('lup'); alias('dscan')
#ascan=MessageClass(" ==="+ " This is not SPEC! Use scan"); alias('ascan')
ubr=MessageClass(" ==="+ " This is not SPEC! Use pos hkl hklvalue, e.g. pos hkl [1 1 0]"); alias('ubr')
or0=or1=MessageClass(" ==="+ " This is not SPEC! Use ubm('parimaryname','secondaryname') where the names refer to reflections in the reflection list"); alias('or0'); alias('or1'); 
moveE=MessageClass(" ==="+ " This is not SPEC! Try 'pos energy value'"); alias('moveE')
getE=MessageClass(" ==="+ " This is not SPEC! Type 'energy'"); alias('getE')
Escan=MessageClass(" ==="+ " This is not SPEC! Try 'scan energy ...'"); alias('Escan')
wm=MessageClass(" ==="+ " This is not SPEC! Just type a motor name to get its position, or  'pos device'"); alias('wm')
shopen=MessageClass(" ==="+ " This is not SPEC! Try 'pos shutter 1'"); alias('shopen')
shclose=MessageClass(" ==="+ " This is not SPEC! Try 'pos shutter 0'"); alias('shclose')
#lim=MessageClass("Commands for GDA PD limits\n
	#showlm\tshows all limits and shows if they are not defaults (defaults set in ConfigureLimits.py)
	#setlm\sets lower and upper limit of device
	#setllm\sets lower limit of device to value (if specified) or current position
	#setulm\sets upper limit of device to value (if specified) or current position
	#device/pos device\tShow current position and limits
#	"); alias('lim')
