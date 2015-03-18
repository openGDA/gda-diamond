# i05 beamline profile
#This script is sourced from /dls_sw/i05/etc/i05_profile.sh

if [ ! -n "$BEAMLINE" ]; then
  echo "ERROR: BEAMLINE not set" 1>&2
  exit 1
fi

export GDA_INSTANCE_NAME=${BEAMLINE}

export GDA_WORKSPACE_PARENT=/dls_sw/$BEAMLINE/software/gda
export GDA_INSTANCE_CONFIG_rel=${GDA_WORKSPACE_GIT_NAME}/gda-pes.git/i05-config

export PATH=$GDA_INSTANCE_CONFIG/bin:${PATH}
export GDA_MODE=live

