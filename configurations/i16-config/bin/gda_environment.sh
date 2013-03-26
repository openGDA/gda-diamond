#!/bin/sh

if [ ! -n "$BEAMLINE" ]; 
then
  echo "Please set BEAMLINE environment variable."
  exit 1
fi

export PATH=/dls_sw/$BEAMLINE/software/gda/config/bin:/dls_sw/$BEAMLINE/bin:${PATH}


case $DISPLAY in 
	:0.0|${BEAMLINE}*:0)
		( cd $HOME/Desktop && test -e "${BEAMLINE}_Launchers" || ln -s /usr/local/etc/"${BEAMLINE}_Launchers" . ) > /dev/null 2>&1
		( cd $HOME/Desktop && test -e "DLS_Launchers" || ln -s /usr/local/etc/"DLS_Launchers" . ) > /dev/null 2>&1
		;;
	*)
		:
		;;
esac
