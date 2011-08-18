# EXAFS scan with sample movement corrections


myscan=I18ExafsScanClass()
myscan.setWindows('/dls_sw/i18/software/gda/i18-config/var/windows/Cu_Ka.cnf','Cu_Ka')
myscan.setSampleMovementLookupTable('/dls/i18/tmp/lookuptables/Cu_EXAFS_SESO_Movement1.dat')
myscan.setHeaderInfo('','','','')
myscan.setNoOfRepeats(1)
myscan.addAngleScan(12941.5,12748.1,-8.299999999999985,1000.0)
myscan.addAngleScan(12748.1,12672.5,-1.4000000000000068,1000.0)
myscan.addKScan(3.0,12.0,0.04,1000.0,1000.0,3,8.98019655625695,6.2695)
myscan.startScan()
