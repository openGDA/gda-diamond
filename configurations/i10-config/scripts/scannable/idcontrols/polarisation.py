'''
A single polarisation scannable that sets the polarisation of the X-ray beam in GDA.
It defines X-ray polaristion modes to be one of ['pc','nc', 'lh', 'lv', 'la'] in GDA only.
It also set 'energy' object to correct energy scannable for the specific source and polarisation.  

Created on 9 May 2018

@author: fy65
'''
from gda.device.scannable import ScannableBase
from scannable.idcontrols.sourceModes import SourceMode
from scannable.continuous.continuous_energy_scannables import egy_g_idd_circ_pos_energy,\
    egy_g_idd_circ_neg_energy, egy_g_idd_lin_hor_energy,\
    egy_g_idd_lin_ver_energy, egy_g_idd_lin_arbitrary_energy,\
    egy_g_idu_circ_pos_energy, egy_g_idu_circ_neg_energy,\
    egy_g_idu_lin_hor_energy, egy_g_idu_lin_ver_energy,\
    egy_g_idu_lin_hor3_energy, cemc_g_idu_circ_pos_energy,\
    cemc_g_idu_circ_neg_energy, cemc_g_idu_lin_hor_energy,\
    cemc_g_idu_lin_ver_energy, cemc_g_idu_lin_hor3_energy,\
    cemc_g_idd_circ_neg_energy, cemc_g_idd_circ_pos_energy,\
    cemc_g_idd_lin_hor_energy, cemc_g_idd_lin_ver_energy,\
    cemc_g_idd_lin_arbitrary_energy
from scannable.id_energys.idd_lin_energy import idd_lin_arbitrary_angle
import __main__  # @UnresolvedImport
from org.slf4j import LoggerFactory

class Polarisation(ScannableBase):
    '''
    Scannable to set the polarisation of the X-ray beam in GDA ONLY. 
    It switches 'energy' scannable reference based on current source mode and polarisation set here.
    '''
    POLARISATIONS=['pc','nc', 'lh', 'lv', 'la', 'lh3']
    
    def __init__(self, name, smode, defaultPolarisation=None):
        '''
        Constructor - default polarisation mode is None
        '''
        self.logger = LoggerFactory.getLogger("Polarisation:%s" % name)
        self.setName(name)
        self.mode=smode
        self.polarisation=defaultPolarisation
        self.amIBusy=False
        self.verbose=False
        
    def getPosition(self):
        ''' get current polarisation that has been set last time 
        '''
        return self.polarisation
    
    def asynchronousMoveTo(self, newpos):
        '''set polarisation of ID according to source mode.
        '''
        if newpos not in Polarisation.POLARISATIONS:
            message="polarisation string is wrong: legal values are %s" % (Polarisation.POLARISATIONS)
            raise Exception(message)
        mode=self.mode.getPosition()
        if mode == None:
            message="X-ray source mode is not set"
            raise Exception(message)
        self.amIBusy=True # need to block to ensure any script run complete before any other actions
        #need to delete __main__.energy and __main__.laa before set it to another scannable due to 'Cannot overwrite scannable
        try:
            exec('__maim__.energy=None;__main__.laa=None')
        except:
            pass
        if mode == SourceMode.SOURCE_MODES[0]:
            if newpos == Polarisation.POLARISATIONS[0]:
                __main__.energy = egy_g_idd_circ_pos_energy
                __main__.mcsr16_g.setHardwareTriggerProvider(cemc_g_idd_circ_pos_energy)
                __main__.mcsr17_g.setHardwareTriggerProvider(cemc_g_idd_circ_pos_energy)
                __main__.mcsr18_g.setHardwareTriggerProvider(cemc_g_idd_circ_pos_energy)
                __main__.mcsr19_g.setHardwareTriggerProvider(cemc_g_idd_circ_pos_energy)
                __main__.binpointGrtPitch_g.setHardwareTriggerProvider(cemc_g_idd_circ_pos_energy)
                __main__.binpointMirPitch_g.setHardwareTriggerProvider(cemc_g_idd_circ_pos_energy)
                __main__.binpointPgmEnergy_g.setHardwareTriggerProvider(cemc_g_idd_circ_pos_energy)
                __main__.binpointId1JawPhase_g.setHardwareTriggerProvider(cemc_g_idd_circ_pos_energy)
                __main__.binpointId2JawPhase_g.setHardwareTriggerProvider(cemc_g_idd_circ_pos_energy)
                __main__.binpointMcaTime_g.setHardwareTriggerProvider(cemc_g_idd_circ_pos_energy)
                __main__.binpointCustom1_g.setHardwareTriggerProvider(cemc_g_idd_circ_pos_energy)
                if self.verbose: 
                    message = "'energy' is switched to %s " % (egy_g_idd_circ_pos_energy.getName())
                    print message
                    self.logger.info(message)
                
            elif newpos == Polarisation.POLARISATIONS[1]:
                __main__.energy = egy_g_idd_circ_neg_energy
                __main__.mcsr16_g.setHardwareTriggerProvider(cemc_g_idd_circ_neg_energy)
                __main__.mcsr17_g.setHardwareTriggerProvider(cemc_g_idd_circ_neg_energy)
                __main__.mcsr18_g.setHardwareTriggerProvider(cemc_g_idd_circ_neg_energy)
                __main__.mcsr19_g.setHardwareTriggerProvider(cemc_g_idd_circ_neg_energy)
                __main__.binpointGrtPitch_g.setHardwareTriggerProvider(cemc_g_idd_circ_neg_energy)
                __main__.binpointMirPitch_g.setHardwareTriggerProvider(cemc_g_idd_circ_neg_energy)
                __main__.binpointPgmEnergy_g.setHardwareTriggerProvider(cemc_g_idd_circ_neg_energy)
                __main__.binpointId1JawPhase_g.setHardwareTriggerProvider(cemc_g_idd_circ_neg_energy)
                __main__.binpointId2JawPhase_g.setHardwareTriggerProvider(cemc_g_idd_circ_neg_energy)
                __main__.binpointMcaTime_g.setHardwareTriggerProvider(cemc_g_idd_circ_neg_energy)
                __main__.binpointCustom1_g.setHardwareTriggerProvider(cemc_g_idd_circ_neg_energy)
                if self.verbose: 
                    message = "'energy' is switched to %s " % (egy_g_idd_circ_neg_energy.getName())
                    print message
                    self.logger.info(message)
            elif newpos == Polarisation.POLARISATIONS[2]:
                __main__.energy = egy_g_idd_lin_hor_energy
                __main__.mcsr16_g.setHardwareTriggerProvider(cemc_g_idd_lin_hor_energy)
                __main__.mcsr17_g.setHardwareTriggerProvider(cemc_g_idd_lin_hor_energy)
                __main__.mcsr18_g.setHardwareTriggerProvider(cemc_g_idd_lin_hor_energy)
                __main__.mcsr19_g.setHardwareTriggerProvider(cemc_g_idd_lin_hor_energy)
                __main__.binpointGrtPitch_g.setHardwareTriggerProvider(cemc_g_idd_lin_hor_energy)
                __main__.binpointMirPitch_g.setHardwareTriggerProvider(cemc_g_idd_lin_hor_energy)
                __main__.binpointPgmEnergy_g.setHardwareTriggerProvider(cemc_g_idd_lin_hor_energy)
                __main__.binpointId1JawPhase_g.setHardwareTriggerProvider(cemc_g_idd_lin_hor_energy)
                __main__.binpointId2JawPhase_g.setHardwareTriggerProvider(cemc_g_idd_lin_hor_energy)
                __main__.binpointMcaTime_g.setHardwareTriggerProvider(cemc_g_idd_lin_hor_energy)
                __main__.binpointCustom1_g.setHardwareTriggerProvider(cemc_g_idd_lin_hor_energy)
                if self.verbose: 
                    message = "'energy' is switched to %s " % (egy_g_idd_lin_hor_energy.getName())
                    print message
                    self.logger.info(message)
            elif newpos == Polarisation.POLARISATIONS[3]:
                __main__.energy = egy_g_idd_lin_ver_energy
                __main__.mcsr16_g.setHardwareTriggerProvider(cemc_g_idd_lin_ver_energy)
                __main__.mcsr17_g.setHardwareTriggerProvider(cemc_g_idd_lin_ver_energy)
                __main__.mcsr18_g.setHardwareTriggerProvider(cemc_g_idd_lin_ver_energy)
                __main__.mcsr19_g.setHardwareTriggerProvider(cemc_g_idd_lin_ver_energy)
                __main__.binpointGrtPitch_g.setHardwareTriggerProvider(cemc_g_idd_lin_ver_energy)
                __main__.binpointMirPitch_g.setHardwareTriggerProvider(cemc_g_idd_lin_ver_energy)
                __main__.binpointPgmEnergy_g.setHardwareTriggerProvider(cemc_g_idd_lin_ver_energy)
                __main__.binpointId1JawPhase_g.setHardwareTriggerProvider(cemc_g_idd_lin_ver_energy)
                __main__.binpointId2JawPhase_g.setHardwareTriggerProvider(cemc_g_idd_lin_ver_energy)
                __main__.binpointMcaTime_g.setHardwareTriggerProvider(cemc_g_idd_lin_ver_energy)
                __main__.binpointCustom1_g.setHardwareTriggerProvider(cemc_g_idd_lin_ver_energy)
                if self.verbose: 
                    message = "'energy' is switched to %s " % (egy_g_idd_lin_ver_energy.getName())
                    print message
                    self.logger.info(message)
            elif newpos == Polarisation.POLARISATIONS[4]:
                __main__.energy = egy_g_idd_lin_arbitrary_energy
                __main__.mcsr16_g.setHardwareTriggerProvider(cemc_g_idd_lin_arbitrary_energy)
                __main__.mcsr17_g.setHardwareTriggerProvider(cemc_g_idd_lin_arbitrary_energy)
                __main__.mcsr18_g.setHardwareTriggerProvider(cemc_g_idd_lin_arbitrary_energy)
                __main__.mcsr19_g.setHardwareTriggerProvider(cemc_g_idd_lin_arbitrary_energy)
                __main__.binpointGrtPitch_g.setHardwareTriggerProvider(cemc_g_idd_lin_arbitrary_energy)
                __main__.binpointMirPitch_g.setHardwareTriggerProvider(cemc_g_idd_lin_arbitrary_energy)
                __main__.binpointPgmEnergy_g.setHardwareTriggerProvider(cemc_g_idd_lin_arbitrary_energy)
                __main__.binpointId1JawPhase_g.setHardwareTriggerProvider(cemc_g_idd_lin_arbitrary_energy)
                __main__.binpointId2JawPhase_g.setHardwareTriggerProvider(cemc_g_idd_lin_arbitrary_energy)
                __main__.binpointMcaTime_g.setHardwareTriggerProvider(cemc_g_idd_lin_arbitrary_energy)
                __main__.binpointCustom1_g.setHardwareTriggerProvider(cemc_g_idd_lin_arbitrary_energy)
                __main__.laa = idd_lin_arbitrary_angle
                if self.verbose: 
                    message = "'energy' is switched to %s " % (egy_g_idd_lin_arbitrary_energy.getName())
                    print message
                    self.logger.info(message)
            elif newpos == Polarisation.POLARISATIONS[5]:
                __main__.energy = None
                raise Exception('Polarisation %s for source mode % is not supported: Energy Calibration is not available!' % (newpos, mode))
        elif mode == SourceMode.SOURCE_MODES[1]:
            if newpos == Polarisation.POLARISATIONS[0]:
                __main__.energy = egy_g_idu_circ_pos_energy
                __main__.mcsr16_g.setHardwareTriggerProvider(cemc_g_idu_circ_pos_energy)
                __main__.mcsr17_g.setHardwareTriggerProvider(cemc_g_idu_circ_pos_energy)
                __main__.mcsr18_g.setHardwareTriggerProvider(cemc_g_idu_circ_pos_energy)
                __main__.mcsr19_g.setHardwareTriggerProvider(cemc_g_idu_circ_pos_energy)
                __main__.binpointGrtPitch_g.setHardwareTriggerProvider(cemc_g_idu_circ_pos_energy)
                __main__.binpointMirPitch_g.setHardwareTriggerProvider(cemc_g_idu_circ_pos_energy)
                __main__.binpointPgmEnergy_g.setHardwareTriggerProvider(cemc_g_idu_circ_pos_energy)
                __main__.binpointId1JawPhase_g.setHardwareTriggerProvider(cemc_g_idu_circ_pos_energy)
                __main__.binpointId2JawPhase_g.setHardwareTriggerProvider(cemc_g_idu_circ_pos_energy)
                __main__.binpointMcaTime_g.setHardwareTriggerProvider(cemc_g_idu_circ_pos_energy)
                __main__.binpointCustom1_g.setHardwareTriggerProvider(cemc_g_idu_circ_pos_energy)
                if self.verbose: 
                    message = "'energy' is switched to %s " % (egy_g_idu_circ_pos_energy.getName())
                    print message
                    self.logger.info(message)            
            elif newpos == Polarisation.POLARISATIONS[1]:
                __main__.energy = egy_g_idu_circ_neg_energy
                __main__.mcsr16_g.setHardwareTriggerProvider(cemc_g_idu_circ_neg_energy)
                __main__.mcsr17_g.setHardwareTriggerProvider(cemc_g_idu_circ_neg_energy)
                __main__.mcsr18_g.setHardwareTriggerProvider(cemc_g_idu_circ_neg_energy)
                __main__.mcsr19_g.setHardwareTriggerProvider(cemc_g_idu_circ_neg_energy)
                __main__.binpointGrtPitch_g.setHardwareTriggerProvider(cemc_g_idu_circ_neg_energy)
                __main__.binpointMirPitch_g.setHardwareTriggerProvider(cemc_g_idu_circ_neg_energy)
                __main__.binpointPgmEnergy_g.setHardwareTriggerProvider(cemc_g_idu_circ_neg_energy)
                __main__.binpointId1JawPhase_g.setHardwareTriggerProvider(cemc_g_idu_circ_neg_energy)
                __main__.binpointId2JawPhase_g.setHardwareTriggerProvider(cemc_g_idu_circ_neg_energy)
                __main__.binpointMcaTime_g.setHardwareTriggerProvider(cemc_g_idu_circ_neg_energy)
                __main__.binpointCustom1_g.setHardwareTriggerProvider(cemc_g_idu_circ_neg_energy)
                if self.verbose: 
                    message = "'energy' is switched to %s " % (egy_g_idu_circ_neg_energy.getName())
                    print message
                    self.logger.info(message)            
            elif newpos == Polarisation.POLARISATIONS[2]:
                __main__.energy = egy_g_idu_lin_hor_energy
                __main__.mcsr16_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor_energy)
                __main__.mcsr17_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor_energy)
                __main__.mcsr18_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor_energy)
                __main__.mcsr19_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor_energy)
                __main__.binpointGrtPitch_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor_energy)
                __main__.binpointMirPitch_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor_energy)
                __main__.binpointPgmEnergy_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor_energy)
                __main__.binpointId1JawPhase_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor_energy)
                __main__.binpointId2JawPhase_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor_energy)
                __main__.binpointMcaTime_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor_energy)
                __main__.binpointCustom1_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor_energy)
                if self.verbose: 
                    message = "'energy' is switched to %s " % (egy_g_idu_lin_hor_energy.getName())
                    print message
                    self.logger.info(message)            
            elif newpos == Polarisation.POLARISATIONS[3]:
                __main__.energy = egy_g_idu_lin_ver_energy
                __main__.mcsr16_g.setHardwareTriggerProvider(cemc_g_idu_lin_ver_energy)
                __main__.mcsr17_g.setHardwareTriggerProvider(cemc_g_idu_lin_ver_energy)
                __main__.mcsr18_g.setHardwareTriggerProvider(cemc_g_idu_lin_ver_energy)
                __main__.mcsr19_g.setHardwareTriggerProvider(cemc_g_idu_lin_ver_energy)
                __main__.binpointGrtPitch_g.setHardwareTriggerProvider(cemc_g_idu_lin_ver_energy)
                __main__.binpointMirPitch_g.setHardwareTriggerProvider(cemc_g_idu_lin_ver_energy)
                __main__.binpointPgmEnergy_g.setHardwareTriggerProvider(cemc_g_idu_lin_ver_energy)
                __main__.binpointId1JawPhase_g.setHardwareTriggerProvider(cemc_g_idu_lin_ver_energy)
                __main__.binpointId2JawPhase_g.setHardwareTriggerProvider(cemc_g_idu_lin_ver_energy)
                __main__.binpointMcaTime_g.setHardwareTriggerProvider(cemc_g_idu_lin_ver_energy)
                __main__.binpointCustom1_g.setHardwareTriggerProvider(cemc_g_idu_lin_ver_energy)
                if self.verbose: 
                    message = "'energy' is switched to %s " % (egy_g_idu_lin_ver_energy.getName())
                    print message
                    self.logger.info(message)            
            elif newpos == Polarisation.POLARISATIONS[4]:
                __main__.energy = None
                __main__.laa = None
                raise Exception('Polarisation %s for source mode % is not supported: Energy Calibration is not available!' % (newpos, mode))
            elif newpos == Polarisation.POLARISATIONS[5]:
                __main__.energy = egy_g_idu_lin_hor3_energy
                __main__.mcsr16_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor3_energy)
                __main__.mcsr17_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor3_energy)
                __main__.mcsr18_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor3_energy)
                __main__.mcsr19_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor3_energy)
                __main__.binpointGrtPitch_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor3_energy)
                __main__.binpointMirPitch_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor3_energy)
                __main__.binpointPgmEnergy_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor3_energy)
                __main__.binpointId1JawPhase_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor3_energy)
                __main__.binpointId2JawPhase_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor3_energy)
                __main__.binpointMcaTime_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor3_energy)
                __main__.binpointCustom1_g.setHardwareTriggerProvider(cemc_g_idu_lin_hor3_energy)
                if self.verbose: 
                    message = "'energy' is switched to %s " % (egy_g_idu_lin_hor3_energy.getName())
                    print message
                    self.logger.info(message)            
            
        self.polarisation=newpos
        self.amIBusy=False
    
    def isBusy(self):
        return self.amIBusy

