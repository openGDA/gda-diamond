# i10 beamline profile
#KrisB 17/09/14 - Commenting out $BEAMLINE as always set on beamline workstations via /etc/profile.d/beamline.sh


if [ ! -n "$BEAMLINE" ]; then
  echo "ERROR: BEAMLINE not set" 1>&2
  exit 1
fi

module load gda_launcher

export PATH=/dls_sw/$BEAMLINE/software/gda/config/bin:${PATH}
export LD_LIBRARY_PATH=/dls_sw/i21/software/anaconda2/plugins/platforms:${LD_LIBRARY_PATH}
export GDA_MODE=live

# Set up command completion for the gda command
source /dls_sw/$BEAMLINE/software/gda/workspace_git/gda-core.git/core-config/bin/gda_core_completion
