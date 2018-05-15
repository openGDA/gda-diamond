# i12 beamline profile

# $BEAMLINE is always set on beamline workstations via /etc/profile.d/beamline.sh

if [ ! -n "$BEAMLINE" ]; then
  echo "ERROR: BEAMLINE not set" 1>&2
  exit 1
fi

export GDA_INSTANCE_NAME=${BEAMLINE}

export GDA_WORKSPACE_PARENT=/dls_sw/$BEAMLINE/software/gda
export GDA_INSTANCE_CONFIG=${GDA_WORKSPACE_PARENT}/workspace_git/gda-diamond.git/configurations/i12-config

export PATH=$GDA_INSTANCE_CONFIG/bin:${PATH}
export GDA_MODE=live

export MATLABPATH=/dls_sw/$BEAMLINE/software/tomoTilt/code/release
export PATH=${MATLABPATH}:/dls_sw/dasc/bin/iKittenScripts:${PATH}

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
