#!/bin/bash

export PATH=$PATH:/dls_sw/epics/R3.14.11/base/bin/linux-x86/

#
# RJW: this is copied from a script used on B18.
# Values have been altered in this script to match what is used in I20 Vortex
#
    ###########################################
    #
    #ACQUISITION CONFIGURATION
    #
    ###########################################
    #No of bins
    caput BL20I-EA-DET-01:MCA1.NUSE 2048

    sleep 1

    #Toggle mode so MCA spectra is selected...
    caput BL20I-EA-DET-01:CollectMode 3
    caput BL20I-EA-DET-01:CollectMode 0
    sleep 1

    #Toggle preset mode to Real Time is selected
    caput BL20I-EA-DET-01:PresetMode 0
    sleep 1
    caput BL20I-EA-DET-01:PresetMode 1
    sleep 1
    caput BL20I-EA-DET-01:PresetMode 0
    sleep 1
    ########################################
    #
    #PREAMP PARAMETERS
    #
    ########################################
    #20 kev 10ev bin
    #bin energy range, resolution, dynamic range etc.

    #max energy
    caput BL20I-EA-DET-01:DXP1:MaxEnergy 20.48
    caput BL20I-EA-DET-01:CopyMaxEnergy 1
    sleep 1
    #Adc percent rule
    caput BL20I-EA-DET-01:DXP1:ADCPercentRule 5.0
    caput BL20I-EA-DET-01:CopyADCPercentRule 1
    sleep 1
    #reset delay  RJW: this differs from B18 version
    caput BL20I-EA-DET-01:DXP1:ResetDelay 2
    caput BL20I-EA-DET-01:CopyResetDelay 1
    sleep 1
    #pre-amp gain  RJW: changed from B18 as this is detector specific
    caput BL20I-EA-DET-01:DXP1:PreampGain 1.61
    caput BL20I-EA-DET-01:DXP2:PreampGain 1.6
    caput BL20I-EA-DET-01:DXP3:PreampGain 1.6
    caput BL20I-EA-DET-01:DXP4:PreampGain 1.645

    #pre-amp polarity
    #system operation settings
    # RJW: these differ from B18
    caput BL20I-EA-DET-01:StatusAll.SCAN 7
    caput BL20I-EA-DET-01:ReadAll.SCAN 6
    caput BL20I-EA-DET-01:ReadLLParams.SCAN 0
    ############################################
    #
    #Filter parameters
    #
    ###########################################
    #Set trigger peaking time
    caput BL20I-EA-DET-01:DXP1:TriggerPeakingTime 0.1
    caput BL20I-EA-DET-01:CopyTriggerPeakingTime 1
    sleep 1
    #Set trigger gap
    caput BL20I-EA-DET-01:DXP1:TriggerGapTime 0.0
    caput BL20I-EA-DET-01:CopyTriggerGapTime 1
    sleep 1
    set trigger threshold level
    caput BL20I-EA-DET-01:DXP1:TriggerThreshold 0.995
    caput BL20I-EA-DET-01:CopyTriggerThreshold 1
    sleep 1
    #Set energy peaking time
    caput BL20I-EA-DET-01:DXP1:PeakingTime 0.26
    caput BL20I-EA-DET-01:CopyPeakingTime 1
    sleep 1
    #Set energy gap time
    caput BL20I-EA-DET-01:DXP1:GapTime 0.2
    caput BL20I-EA-DET-01:CopyGapTime 1
    sleep 1
    #Energy threshold level
    caput BL20I-EA-DET-01:DXP1:EnergyThreshold 0.0
    caput BL20I-EA-DET-01:CopyEnergyThreshold 1
    sleep 1
    #Maximum width
    caput BL20I-EA-DET-01:DXP1:MaxWidth 1
    caput BL20I-EA-DET-01:CopyMaxWidth 1
    sleep 1
    #Baseline cut
    caput BL20I-EA-DET-01:DXP1:BaselineCutPercent 0.0
    caput BL20I-EA-DET-01:CopyBaselineCutPercent 1
    caput BL20I-EA-DET-01:DXP1:BaselineCutEnable 0
    caput BL20I-EA-DET-01:CopyBaselineCutEnable 1
    sleep 1
    #baseline threshold
    caput BL20I-EA-DET-01:DXP1:BaselineThreshold 1.5
    caput BL20I-EA-DET-01:CopyBaselineThreshold 1
    sleep 1
    #filter length
    # RJW: these differ from B18
    caput BL20I-EA-DET-01:DXP1:BaselineFilterLength 256
    caput BL20I-EA-DET-01:CopyBaselineFilterLength 1
    sleep 1

    #########################################
    #
    ##specific mapping settings
    #
    #########################################
    #gate mode
    caput BL20I-EA-DET-01:PixelAdvanceMode 1
    sleep 1
    caput BL20I-EA-DET-01:PixelAdvanceMode 0

    caput BL20I-EA-DET-01:AutoPixelsPerBuffer 0
    sleep 1
    caput BL20I-EA-DET-01:AutoPixelsPerBuffer 1

    #set ignore gate to No
    caput BL20I-EA-DET-01:IgnoreGate 1
    sleep 1
    caput BL20I-EA-DET-01:IgnoreGate 0

    #output file setup
    # RJW: these differ from B18 was 2, I20: 0
    caput BL20I-EA-DET-01:HDF:FileWriteMode 0
    # RJW: these differ from B18 was 1, I20: 0
    caput BL20I-EA-DET-01:HDF:EnableCallbacks 0
    caput BL20I-EA-DET-01:HDF:AutoSave 0
    caput BL20I-EA-DET-01:HDF:AutoIncrement 0

	# for I20, ensure that the bin width is always 0.01 kev
	caput BL20I-EA-DET-01:DXP1:MaxEnergy 20.480
	caput BL20I-EA-DET-01:DXP2:MaxEnergy 20.480
	caput BL20I-EA-DET-01:DXP3:MaxEnergy 20.480
	caput BL20I-EA-DET-01:DXP4:MaxEnergy 20.480

    #take some data to fill the ndarray
    caput BL20I-EA-DET-01:CollectMode 1
    caput -c BL20I-EA-DET-01:EraseStart 1
    sleep 1
    caput -c BL20I-EA-DET-01:StopAll 1
    caput BL20I-EA-DET-01:CollectMode 0
    echo 'Configuration of Vortex complete.'

