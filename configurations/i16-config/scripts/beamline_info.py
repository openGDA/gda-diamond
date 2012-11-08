## @file BLinfo.py This file contains a module
#  dealing with the beamline settings (Energy, wavelength,...)
#
#  @author Alessandro Bombardi
#  @version 1.0 (alpha release)
#  Please report bugs to Alessandro.Bombardi@diamond.ac.uk
#  Diamond Light Source Ltd.

import ShelveIO
import beamline_objects as BLobjects
import AllBeamlineObjects

# Global Variables of the Module; Please do not change
BLI=ShelveIO.ShelveIO()
BLI.path=ShelveIO.ShelvePath+'BLinfo'
BLI.setSettingsFileName('BLinfo')


energy=None
wavelength=None

## This function allows to set the energy in keV and will change
#  consequently the wavelength.
def setEnergy(E):
  # "@sig pub lic void setEnergy(double E)"
   global energy
   global wavelength
   energy = E
   wavelength = 12.39842/E
   if (AllBeamlineObjects.isDummySimulation() or BLobjects.isSimulation() ):
      BLI.ChangeValue('Energy',energy)
      BLI.ChangeValue('Wavelength',wavelength)
#   else:
#      BLobjects.getWavelength().moveTo(wavelength)
   return

## This function allows to set the wavelength in Angstrom and will
#  change consequently the wavelength.
def setWavelength(W):
   "@sig public void setWavelength(double W)"
   global energy
   global wavelength
   energy = 12.39842/W
   wavelength = W
   if (AllBeamlineObjects.isDummySimulation() or BLobjects.isSimulation() ):
      BLI.ChangeValue('Energy',energy)
      BLI.ChangeValue('Wavelength',wavelength)
#   else:
#      BLobjects.getWavelength().moveTo(wavelength)
   return

## This function allows to get the energy from a locally stored
#  variable or from a file if the local variable has no value assigned
def getEnergy():
   "@sig public double getEnergy()"
   global energy
   global wavelength
   if (AllBeamlineObjects.isDummySimulation() or BLobjects.isSimulation() ):
      energy = BLI.getValue('Energy')
#   else:
#      wavelength = BLobjects.getWavelength().getPosition()
#      energy = 12.39842/wavelength   
   return energy
#   return 8.078

## This function allows to get the wavelength from a locally stored
#  variable or from a file if the local variable has no value assigned
def getWavelength():
   "@sig public double getWavelength()"
   global wavelength
   if (AllBeamlineObjects.isDummySimulation() or BLobjects.isSimulation() ):
      wavelength = BLI.getValue('Wavelength')
#   else:
#      wavelength = BLobjects.getWavelength().getPosition()
#   return 12.39842/8.078
   return wavelength 
  
