'''
Gate valve checking scannable which pause scan by blocking getPosition() call while the valve is closed, and resume scan when valve opens.
It has built-in checking for vacuum pressure, if pressure falls below specified maximum threshold, it opens the valve, so scan will continue.

created on 28 May 2024

@author: fy65
'''
###############################################################################
###                           Wait for beam device                          ###
###############################################################################
from utils.ExceptionLogs import localStation_exception
import sys
from gdaserver import gv12, gauge16  # @UnresolvedImport
from gdascripts.scannable.beamokay import WaitForScannableState
from time import sleep

class WaitWhenGateValueClosedWhileCheckGaugePressureForOpenAction(WaitForScannableState):

	def __init__(self, name, scannable_to_check, max_threshold, scannable_to_monitor, seconds_between_checks = 1, seconds_to_wait_after_beam_back_up = None, ready_states = ['Open'], fault_states = ['Fault']):
		WaitForScannableState.__init__( self, name, scannable_to_monitor, seconds_between_checks, seconds_to_wait_after_beam_back_up, ready_states, fault_states)
		self.scannable_to_check = scannable_to_check
		self.max_threshold = max_threshold
		self.setExtraNames([])
		self.setOutputFormat([])

	def atScanStart(self):
		ready_states_string = self.readyStates[0] if len(self.readyStates)==1 else str(self.readyStates)
		print('=== Valve checking enabled: '+self.scannableToMonitor.getName()+' must be in state: ' + ready_states_string+', currently '+str(self._getStatus()))
		self.statusRemainedGoodSinceLastGetPosition = True

	def _collectNewMonitorValue(self):
		WaitForScannableState._collectNewMonitorValue(self)
		if not self._getStatus() and float(self.scannable_to_check.getPosition()) < self.max_threshold:
			#valve not in open state but vacuum pressure is good now
			self.scannableToMonitor.moveTo("Reset")
			sleep(0.5)
			self.scannableToMonitor.moveTo("Open")
			sleep(1.0)

try:
	print("-"*100)
	print("Creating checkgv12 device:")
	print(" 'checkgv12' - check Gate Valve 12, pause scan when this valve is closed, and monitor then try to re-open the gate valve.")

	checkgv12 = WaitWhenGateValueClosedWhileCheckGaugePressureForOpenAction('checkgv12', gauge16, 1.0e-6, gv12, seconds_between_checks = 1, seconds_to_wait_after_beam_back_up = 2, ready_states = ['Open'], fault_states = ['Fault'])
	checkgv12.configure()
except:
	localStation_exception(sys.exc_info(), "creating checkgv12 objects")

