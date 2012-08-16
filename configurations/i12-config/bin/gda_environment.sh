#!/bin/sh
# This script assumes that $BEAMLINE is set (e.g. i02, i18, b16) if not exit...

if [ ! -n "$BEAMLINE" ]; 
then
  echo "Please set BEAMLINE environment variable."
  exit 1
fi

export SOFTWAREFOLDER=dls_sw
export GDA_ROOT=/$SOFTWAREFOLDER/$BEAMLINE/software/gda/plugins
export GDA_CONFIG=${GDA_ROOT}/../i12-config
export GDA_DATADIR=/dls/$BEAMLINE/data

LIBRARY_SUBDIR=linux-`uname -i`
LD_LIBRARY_PATH=${GDA_ROOT}/uk.ac.gda.core/lib/${LIBRARY_SUBDIR}:$LD_LIBRARY_PATH; export LD_LIBRARY_PATH

unset ANT_HOME
unset JAVA_HOME
unset SVN_HOME

export CLASSPATH=/$SOFTWAREFOLDER/$BEAMLINE/software/gda/thirdparty/eclipse/plugins/*:$CLASSPATH
export MATLABPATH=/$SOFTWAREFOLDER/$BEAMLINE/software/tomoTilt/code/release

export PATH=/$SOFTWAREFOLDER/$BEAMLINE/software/gda/i12-config/bin:/$SOFTWAREFOLDER/$BEAMLINE/software/tomoTilt/code/release:/dls_sw/dasc/bin/iKittenScripts:/$SOFTWAREFOLDER/$BEAMLINE/bin:$PATH

module load java/gda826

# If for whatever reason GDA_Launchers failed to be created on user login, this will create it when user open a terminal.
case $DISPLAY in 
	:0.0|${BEAMLINE}*:0)
		( cd $HOME/Desktop && test -e "GDA_Launchers" || ln -s /usr/local/etc/"GDA_Launchers" . ) > /dev/null 2>&1
		( cd $HOME/Desktop && test -e "${BEAMLINE}_Launchers" || ln -s /usr/local/etc/"${BEAMLINE}_Launchers" . ) > /dev/null 2>&1
		;;
	*)
		:
		;;
esac
