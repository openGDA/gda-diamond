# Functions to control the sample stage
from gda.epics import CAClient
from gdaserver import SampleX, SampleX_coarse, SampleX_fine, SampleY, SampleY_coarse, SampleY_fine
from i08_shared_utilities import is_live


def sample_stage_home():
    if is_live():
        print('Homing sample stage')
        caClient = CAClient()
        try:
            caClient.configure()
            caClient.caput('BL08I-EA-TABLE-01:HM:HMGRP', 'All', 1)
            caClient.caput('BL08I-EA-TABLE-01:HM:HOME', 1, 30)
        finally:
            caClient.clearup()
    else:
        print('Homing sample stage (dummy)')
        SampleX.getMotor().home()
        SampleY.getMotor().home()
        SampleX_coarse.getMotor().home()
        SampleY_coarse.getMotor().home()
        SampleX_fine.getMotor().home()
        SampleY_fine.getMotor().home()

        SampleX.waitWhileBusy()
        SampleY.waitWhileBusy()
        SampleX_coarse.waitWhileBusy()
        SampleY_coarse.waitWhileBusy()
        SampleX_fine.waitWhileBusy()
        SampleY_fine.waitWhileBusy()

    print('Finished homing sample stage')
