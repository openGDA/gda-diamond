"""
Continuous Thp Scannable and Controller for using Constant Velocity on I10
for use with GDA at Diamond Light Source
"""

from datetime import datetime, timedelta
from gda.device import DeviceBase
from gda.device.continuouscontroller import ConstantVelocityMoveController
from java.util.concurrent import Callable
from org.slf4j import LoggerFactory
import threading, time

from scannable.continuous.deprecated import ContinuousPgmEnergyMoveController

class ContinuousThpMoveController(ContinuousPgmEnergyMoveController):
    def __init__(self, name, thp): # motors, maybe also detector to set the delay time
        ContinuousPgmEnergyMoveController.__init__(self, name, thp)
        self.logger = LoggerFactory.getLogger("ContinuousThpMoveController:%s" % name)

# TODO: Ideally, these should both be renammed ContinuousScannableMoveController,
#       since it appears that neither have any non generic requirements.