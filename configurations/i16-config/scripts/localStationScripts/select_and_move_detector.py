class change_setup():
	'''
	Make a change to experimental set-up
	See help for go_pil, go_pa, go_apd, go_camera, go_diode 
	'''
	def __init__(self,command_list,help=None):
		self.command_list=command_list
		self.help=help
		self.__doc__+='\n'+self.help

	def __call__(self):
		print self.help
		print 'Changing set-up please wait...'
		self.dostuff()

	def __repr__(self):
		self.__call__()
		return '...Done!'

	def dostuff(self):
		for command in self.command_list:
			exec(command)
			

go_pil=change_setup(['dd=delta()','do(do.pil)','delta(dd)'],help='Change to Pilatus 100K')
go_pa=change_setup(['dd=delta()','do(0)','delta(dd)'],help='Change to PA without changing PA settings')
go_apd=change_setup(['dd=delta()','do(0)','delta(dd)','tthp(tthp.apd)'],help='Change to APD (PA out)')
go_camera=change_setup(['dd=delta()','do(0)','delta(dd)','tthp(tthp.camera)'],help='Change to camera (PA out)')
go_diode=change_setup(['dd=delta()','do(0)','delta(dd)','tthp(tthp.diode)'],help='Change to diode (PA out)')
