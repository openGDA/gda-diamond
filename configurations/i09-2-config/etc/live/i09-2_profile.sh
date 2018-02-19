# i09-2 beamline profile
#This script is sourced from /dls_sw/i09-2/etc/i09-2_profile.sh

if [ ! -n "$BEAMLINE" ]; then
  echo "ERROR: BEAMLINE not set" 1>&2
  exit 1
fi

export GDA_INSTANCE_NAME=${BEAMLINE}

export GDA_WORKSPACE_PARENT=/dls_sw/$BEAMLINE/software/gda
export GDA_INSTANCE_CONFIG=$GDA_WORKSPACE_PARENT/workspace_git/gda-dls-beamlines-i09.git/i09-2-config

export PATH=${GDA_INSTANCE_CONFIG}/bin:${GDA_WORKSPACE_PARENT}/pythonscript:${PATH}
export GDA_MODE=live
