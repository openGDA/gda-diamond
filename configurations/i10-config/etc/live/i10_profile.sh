# i10 beamline profile
#This script is sourced from /dls_sw/b24/etc/i14_profile.sh
#KrisB 17/09/14 - Commenting out $BEAMLINE as always set on beamline workstations via /etc/profile.d/beamline.sh


if [ ! -n "$BEAMLINE" ]; then
  echo "ERROR: BEAMLINE not set" 1>&2
  exit 1
fi

#export GDA_INSTANCE_NAME=${BEAMLINE}

#export GDA_WORKSPACE_PARENT=/dls_sw/$BEAMLINE/software/gda
#export GDA_INSTANCE_CONFIG=${GDA_WORKSPACE_PARENT}/config

export PATH=/dls_sw/$BEAMLINE/software/gda/config/bin:${PATH}
export LD_LIBRARY_PATH=/dls_sw/i21/software/anaconda2/plugins/platforms:${LD_LIBRARY_PATH}
export GDA_MODE=live

# Set up command completion for the gda command
source /dls_sw/$BEAMLINE/software/gda/workspace_git/gda-core.git/core-config/bin/gda_core_completion
