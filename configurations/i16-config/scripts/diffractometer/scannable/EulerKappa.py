import EulerianKconversionModes

from gda.device.scannable.scannablegroup import ScannableMotionWithScannableFieldsBase

def n(n):
	return None if n is None else n[0]

class EulerKappa(ScannableMotionWithScannableFieldsBase):

	def __init__(self, name, coordinatatedMotionKappaScannable, is_fly=False):
		"""coordinatatedMotionKappaScannable must have input fields:
		      	<ref bean="muC" />
				<ref bean="deltaC" />
				<ref bean="gamC" />
				<ref bean="kthC" />
				<ref bean="kapC" />
				<ref bean="kphiC" />
		"""
		self.name = name
		self.kappa = coordinatatedMotionKappaScannable

		if not is_fly:
			self.setInputNames(('phi','chi','eta', 'mu', 'delta', 'gam'))
		else :
			self.setInputNames(('phi_fly','chi_fly','eta_fly', 'mu_fly', 'delta_fly', 'gam_fly'))
		self.setOutputFormat(['% 5.5f']*6)

		self.ekcm = EulerianKconversionModes.EulerianKconversionModes()

		# Note mu, delta and gam limits must be stored in the kappa device
		self.mu_tolerance = .001
		self.last_move_involved_chi = False

	def isBusy(self):
		return self.kappa.isBusy()

	def waitWhileBusy(self):
		return self.kappa.waitWhileBusy()

	def rawGetPosition(self):
		kphi, kap, kth, kmu, kdelta, kgam = self.kappa.getPosition()
		eulerobj = self.ekcm.getEulerianAngles( (kth,kap,kphi))
		eta = eulerobj.Theta
		phi = eulerobj.Phi
		chi = eulerobj.Chi
		return phi, chi, eta, kmu, kdelta, kgam

	def getFieldPosition(self, index):
		if index in (3,4,5): #kmu, kdelta, kgam
			return self.kappa.getPosition()[index]
		else:
			return self.getPosition()[index]

	def eulerToKappa(self, eta, chi, phi):
		ang = self.ekcm.getKPossibleAngles( (eta, chi, phi) ) #-> ang.Vector, ang.KTheta, ang.K, ang.KPhi 
		kth = ang.KTheta
		kappa = ang.K
		kphi = ang.KPhi
		return (kth, kappa, kphi)

	def setMode(self,mode):
		self.ekcm.setEuleriantoKmode(mode)

	def getMode(self):
		return self.ekcm.getEuleriantoKmode()

#	def simulateMoveTo(self, eulerPos):
#		(kphi, kappa, kth, kmu, kdelta, kgam)=self.eulerToKappa(eulerPos)
#		(oldkphi, oldkappa, oldkth, oldkmu, oldkdelta, oldkgam) = self.kappa.getPosition()
#		result = "Kappa would move from/to\n"
#		result += "   kmu   : % 5.5f --> % 5.5f\n" % (oldkmu,kmu)
#		result += "   kdelta: % 5.5f --> % 5.5f\n" % (oldkdelta,kdelta)
#		result += "   kgam  : % 5.5f --> % 5.5f\n" % (oldkgam,kgam)
#		result += "   kth   : % 5.5f --> % 5.5f\n" % (oldkth,kth)
#		result += "   kappa : % 5.5f --> % 5.5f\n" % (oldkappa,kappa)
#		result += "   kphi  : % 5.5f --> % 5.5f\n" % (oldkphi,kphi)
#		return result

	def rawAsynchronousMoveTo(self, eulerPos):

		#euler:: 0:mu, 1:delta, 2:gamma, 3:eta, 4:chi, 5:phi
		#kappa:: 0:mu, 1:delta, 2:gamma, 3:kth, 4:kap, 5:kphi'

		# Check the euler (self) limits

		# mu, delta and gamma can be move independently of the others, although
		# moving mu may invalidate the others.
		phi, chi, eta, mu, delta, gam = tuple(eulerPos)

		if chi is not None:
			self.last_move_involved_chi = True
		else:
			self.last_move_involved_chi = False

		if phi==chi==eta==None:
			self.kappa.asynchronousMoveTo((None, None,None, mu,delta,gam) )
		else:
			phi_orig, chi_orig, eta_orig = phi, chi, eta
			if None in (phi, chi, eta):
				position_at_scan_start = self.getPositionAtScanStart()
				base_position = position_at_scan_start if position_at_scan_start is not None else self.rawGetPosition()

				phi_c, chi_c, eta_c, _, _, _ = base_position
				if phi is None: phi = phi_c
				if chi is None: chi = chi_c
				if eta is None: eta = eta_c

				# update position_at_scan_start
				if position_at_scan_start is not None:
					position_at_scan_start = list(position_at_scan_start)
					if phi_orig is not None:
						position_at_scan_start[0] = phi_orig
					if chi_orig is not None:
						position_at_scan_start[1] = chi_orig
					if eta_orig is not None:
						position_at_scan_start[2] = eta_orig
					self.setPositionAtScanStart(position_at_scan_start)
			kth, kappa, kphi = self.eulerToKappa(eta, chi, phi)
			self.kappa.asynchronousMoveTo( (kphi, kappa, kth, mu, delta, gam) )

	def checkMuIsCorrectForMode_UNUSED(self, mu_resulting):
		mode = self.ekcm.getEuleriantoKmode()
		mu_required = [None, 0., 0., 180., 180.][mode]
		if abs(mu_resulting-mu_required) > self.mu_tolerance:
			raise Exception, "Mu will be %f, but must be close to %f, in kappa mode %i" % (mu_resulting, mu_required, mode)

	def atCommandFailure(self):
		ScannableMotionWithScannableFieldsBase.atCommandFailure(self)
		if self.last_move_involved_chi:
			fmt = "         ETA, CHI, PHI = %s, %s, %s" % tuple(self.outputFormat[3:])
			print "-"*80 + "\nWARNING: chi movement was incomplete, eta and phi may have changed:\n" + fmt % tuple(self.getPosition()[3:]) + '\n'+ "-"*68 + '\n'

	def stop(self):
		self.kappa.stop()
		ScannableMotionWithScannableFieldsBase.stop(self)

	def checkPositionValid(self, eulerPos):
		result = ScannableMotionWithScannableFieldsBase.checkPositionValid(self, eulerPos)
		if result:
			return result
		phi, chi, eta, mu, delta, gam = tuple(eulerPos)
		if None in (phi, chi, eta):
			base_position = self.rawGetPosition()
			phi_c, chi_c, eta_c, _, _, _ = base_position
			if phi is None: phi = phi_c
			if chi is None: chi = chi_c
			if eta is None: eta = eta_c
		kth, kappa, kphi = self.eulerToKappa(eta, chi, phi)
		result = self.kappa.checkPositionValid( (kphi, kappa, kth, mu, delta, gam) )
		return result

	def getLowerGdaLimits(self):
		super_euler_limits = ScannableMotionWithScannableFieldsBase.getLowerGdaLimits(self)
		phi, chi, eta = (None, None, None) if super_euler_limits==None else super_euler_limits[0:3]
		mu = n(self.kappa.getGroupMembersAsArray()[3].getLowerGdaLimits())
		delta = n(self.kappa.getGroupMembersAsArray()[4].getLowerGdaLimits())
		gam = n(self.kappa.getGroupMembersAsArray()[5].getLowerGdaLimits())
		if phi==chi==eta==mu==delta==gam==None:
			return None
		return phi, chi, eta, mu, delta, gam

	def getUpperGdaLimits(self):
		super_euler_limits = ScannableMotionWithScannableFieldsBase.getUpperGdaLimits(self)
		phi, chi, eta = (None, None, None) if super_euler_limits==None else super_euler_limits[0:3]
		mu = n(self.kappa.getGroupMembersAsArray()[3].getUpperGdaLimits())
		delta = n(self.kappa.getGroupMembersAsArray()[4].getUpperGdaLimits())
		gam = n(self.kappa.getGroupMembersAsArray()[5].getUpperGdaLimits())
		if phi==chi==eta==mu==delta==gam==None:
			return None
		return phi, chi, eta, mu, delta, gam

	def setUpperGdaLimits(self,value):
		if value==None:
			phi=chi=eta=mu=delta=gam=None
		else:
			phi, chi, eta, mu, delta, gam = tuple(value)

		# phi, chi, eta
		super_euler_limits = None if phi==chi==eta==None else (phi, chi, eta, None, None, None)
		ScannableMotionWithScannableFieldsBase.setUpperGdaLimits(self, super_euler_limits)
		# mu, delta, gam
		self.kappa.getGroupMembersAsArray()[3].setUpperGdaLimits(mu)
		self.kappa.getGroupMembersAsArray()[4].setUpperGdaLimits(delta)
		self.kappa.getGroupMembersAsArray()[5].setUpperGdaLimits(gam)

	def setLowerGdaLimits(self,value):
		if value==None:
			phi=chi=eta=mu=delta=gam=None
		else:
			phi, chi, eta, mu, delta, gam = tuple(value)

		# phi, chi, eta
		super_euler_limits = None if phi==chi==eta==None else (phi, chi, eta, None, None, None)
		ScannableMotionWithScannableFieldsBase.setLowerGdaLimits(self, super_euler_limits)
		# mu, delta, gam
		self.kappa.getGroupMembersAsArray()[3].setLowerGdaLimits(mu)
		self.kappa.getGroupMembersAsArray()[4].setLowerGdaLimits(delta)
		self.kappa.getGroupMembersAsArray()[5].setLowerGdaLimits(gam)

	def setOperatingContinuously(self, b):
		if callable(getattr(self.kappa, "isOperatingContinously", None)) :
			self.kappa.setOperatingContinuously(b);

	def isOperatingContinously(self):
		if callable(getattr(self.kappa, "isOperatingContinously", None)) :
			return self.kappa.isOperatingContinously()
		return False

	def getContinuousMoveController(self):
		#raise Exception("Eulerian axes cannot be traj scanned. Use the axes on the group 'kappa' (e.g. kth) instead. (Due to a multi-axes traj scans not triggering reliably from Epics)")
		return self.kappa.getContinuousMoveController()

	def setContinuousMoveController(self, controller):
		self.kappa.setContinuousMoveController(controller)