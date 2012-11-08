#!/bin/sh
# This script assumes that $BEAMLINE is set (e.g. i02, i18, b16) if not exit...

# **** DO NOT EDIT THIS SCRIPT AS IT MAY BE AUTOMATICALLY OVERWRITTEN *****

if [ ! -n "$BEAMLINE" ]; 
then
  echo "Please set BEAMLINE environment variable."
  exit 1
fi

export GDA_ROOT=/dls_sw/$BEAMLINE/software/gda

export PATH=$GDA_ROOT/bin:/dls_sw/$BEAMLINE/bin:${PATH}


case $DISPLAY in 
	:0.0|${BEAMLINE}*:0)
		( cd $HOME/Desktop && test -e "${BEAMLINE}_Launchers" || ln -s /usr/local/etc/"${BEAMLINE}_Launchers" . ) > /dev/null 2>&1
		( cd $HOME/Desktop && test -e "DLS_Launchers" || ln -s /usr/local/etc/"DLS_Launchers" . ) > /dev/null 2>&1
		;;
	*)
		:
		;;
esac
