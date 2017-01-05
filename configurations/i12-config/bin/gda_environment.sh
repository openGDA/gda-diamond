#!/bin/sh
export BEAMLINE=i12

export SOFTWARE_FOLDER=dls_sw
export GDA_ROOT=/$SOFTWARE_FOLDER/$BEAMLINE/software/gda/plugins
export GDA_CONFIG=${GDA_ROOT}/../i12-config
export GDA_DATADIR=/dls/$BEAMLINE/data
export GDA_LOGS=/dls_sw/i12/software/logs
export GDA_FOLDER=/dls_sw/$BEAMLINE/software/gda

export CLASSPATH=/$SOFTWARE_FOLDER/$BEAMLINE/software/gda/thirdparty/eclipse/plugins/*:$CLASSPATH
export MATLABPATH=/$SOFTWARE_FOLDER/$BEAMLINE/software/tomoTilt/code/release

export PATH=/$SOFTWARE_FOLDER/$BEAMLINE/software/gda/i12-config/bin:/$SOFTWARE_FOLDER/$BEAMLINE/software/tomoTilt/code/release:/dls_sw/dasc/bin/iKittenScripts:/$SOFTWARE_FOLDER/$BEAMLINE/bin:$PATH:/$SOFTWARE_FOLDER/$BEAMLINE/software/gda/workspace_git/gda-diamond.git/dls-config/bin

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
