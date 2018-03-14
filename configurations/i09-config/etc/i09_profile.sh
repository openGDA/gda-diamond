# i09 beamline profile

if [ ! -n "$BEAMLINE" ]; then
  echo "ERROR: BEAMLINE not set" 1>&2
  exit 1
fi

export GDA_INSTANCE_NAME=${BEAMLINE}

export GDA_WORKSPACE_PARENT=/dls_sw/$BEAMLINE/software/gda
export GDA_INSTANCE_CONFIG=$GDA_WORKSPACE_PARENT/workspace_git/gda-diamond.git/configurations/i09-config

export PATH=${GDA_INSTANCE_CONFIG}/bin:${PATH}
export GDA_MODE=live
