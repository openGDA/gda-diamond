-------------------
Epics gda-interface
-------------------

    When updating the gda-interfaces:
    
    1) Find the latest gda-interface files for BL06I.
    2) Update files if newer than current. To preserve time stamps use:
    	$ cp --preserve=timestamps <src>.xml <dest>.xml
    3) Update this document with new history.
    3) Update this document with new locations.

-----------------------------
Epics gda-interface locations
-----------------------------

	Ideally, we should be able to find the location of the currently in use
Epics gui by using configure-ioc:

$ configure-ioc show BL06I-gui
BL06I-gui /dls_sw/prod/R3.14.12.3/ioc/BL06I/BL/2-82/bin/linux-x86/stBL06I-gui2

	Sometimes though, these do not match up, so it is worth checking in the
data directories too: 

$ ll -t --time-style=long-iso /dls_sw/prod/*/ioc/BL06*/BL/*/data/BL*-gda-interface.xml /dls_sw/work/*/ioc/BL06*/BL/data/BL06*-gda-interface.xml /dls_sw/i06*/software/gda/workspace_git/gda-mt.git/configurations/*/xml/epics/BL06*-gda-interface.xml /dls_sw/i06*/software/gda_versions/*/workspace_git/gda-mt.git/configurations/*/xml/epics/BL06*-gda-interface.xml
-r-xr-xr-x. 1 pjl45    dcs      2552828 2015-06-23 12:23 /dls_sw/work/R3.14.12.3/ioc/BL06I/BL/data/BL06I-gda-interface.xml
-rwxrwxr-x. 1 voo82358 dls_dasc 1474816 2015-06-18 11:56 /dls_sw/i06/software/gda_versions/gda_8.38c/workspace_git/gda-mt.git/configurations/i06-config/xml/epics/BL06I-gda-interface.xml
-rwxrwxr-x. 1 voo82358 dls_dasc 1474816 2015-06-18 11:56 /dls_sw/i06/software/gda/workspace_git/gda-mt.git/configurations/i06-config/xml/epics/BL06I-gda-interface.xml
-rwxrwxr-x. 1 uri03204 dls_dasc 1474816 2015-06-17 17:44 /dls_sw/i06-1/software/gda_versions/gda_8.38c/workspace_git/gda-mt.git/configurations/i06-config/xml/epics/BL06I-gda-interface.xml
-rwxrwxr-x. 1 uri03204 dls_dasc 1474816 2015-06-17 17:44 /dls_sw/i06-1/software/gda/workspace_git/gda-mt.git/configurations/i06-config/xml/epics/BL06I-gda-interface.xml
-r-xr-xr-x. 1    37523    37523 2552828 2015-05-08 15:56 /dls_sw/prod/R3.14.12.3/ioc/BL06I/BL/2-82/data/BL06I-gda-interface.xml
-r-xr-xr-x. 1    37523    37523 2552828 2015-04-09 11:31 /dls_sw/prod/R3.14.12.3/ioc/BL06I/BL/2-81/data/BL06I-gda-interface.xml
-r-xr-xr-x. 1    37523    37523 2552828 2015-03-26 13:57 /dls_sw/prod/R3.14.12.3/ioc/BL06I/BL/2-80/data/BL06I-gda-interface.xml
-r-xr-xr-x. 1    37523    37523 2552828 2015-03-16 15:16 /dls_sw/prod/R3.14.12.3/ioc/BL06I/BL/2-79/data/BL06I-gda-interface.xml
-r-xr-xr-x. 1    37523    37523 2552828 2015-03-13 11:21 /dls_sw/prod/R3.14.12.3/ioc/BL06I/BL/2-78/data/BL06I-gda-interface.xml
-r-xr-xr-x. 1    37523    37523 2552498 2015-02-10 16:25 /dls_sw/prod/R3.14.12.3/ioc/BL06I/BL/2-77/data/BL06I-gda-interface.xml
-r-xr-xr-x. 1    37523    37523 2552498 2015-02-06 15:53 /dls_sw/prod/R3.14.12.3/ioc/BL06I/BL/2-76/data/BL06I-gda-interface.xml
-r-xr-xr-x. 1    37523    37523 2552498 2015-01-27 12:01 /dls_sw/prod/R3.14.12.3/ioc/BL06I/BL/2-75/data/BL06I-gda-interface.xml
-rwxrwxr-x. 1 voo82358 dls_dasc 1474816 2014-11-06 11:38 /dls_sw/i06-1/software/gda_versions/gda_8.38b/workspace_git/gda-mt.git/configurations/i06-config/xml/epics/BL06I-gda-interface.xml
-rwxrwxr-x. 1 voo82358 dls_dasc 1474816 2014-10-16 16:36 /dls_sw/i06/software/gda_versions/gda_8.40a/workspace_git/gda-mt.git/configurations/i06-config/xml/epics/BL06I-gda-interface.xml
-rwxrwxr-x. 1 voo82358 dls_dasc 1474816 2014-10-15 12:23 /dls_sw/i06/software/gda_versions/gda_8.38b/workspace_git/gda-mt.git/configurations/i06-config/xml/epics/BL06I-gda-interface.xml
-rwxrwxr-x. 1 zrb13439 dls_dasc 1474816 2014-06-25 17:01 /dls_sw/i06-1/software/gda_versions/gda_8.38a/workspace_git/gda-mt.git/configurations/i06-config/xml/epics/BL06I-gda-interface.xml
-r-xr-xr-x. 1 qvr31998 dcs      1716855 2014-04-01 16:43 /dls_sw/work/R3.14.11/ioc/BL06I/BL/data/BL06I-gda-interface.xml
-rwxrwxr-x+ 1 voo82358 dls_dasc 1474176 2014-03-21 11:56 /dls_sw/i06/software/gda_versions/gda_8.38a/workspace_git/gda-mt.git/configurations/i06-config/xml/epics/BL06I-gda-interface.xml
-rwxrwxr-x+ 1 voo82358 dls_dasc 1474176 2013-10-08 13:29 /dls_sw/i06/software/gda_versions/gda_8.34b/workspace_git/gda-mt.git/configurations/i06-config/xml/epics/BL06I-gda-interface.xml
-r-xr-xr-x. 1 els59    dcs        98685 2011-01-24 11:51 /dls_sw/work/R3.14.8.2/ioc/BL06I/BL/data/BL06I-gda-interface.xml
