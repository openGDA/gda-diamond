# b16 beamline profile

if [ ! -n "$BEAMLINE" ]; then
  echo "ERROR: BEAMLINE not set" 1>&2
  exit 1
fi

# Set up path and mode
export PATH=/dls_sw/$BEAMLINE/software/gda/config/bin:${PATH}
export GDA_MODE=live

# Set up command completion for the gda command
source /dls_sw/$BEAMLINE/software/gda/workspace_git/gda-core.git/core-config/bin/gda_core_completion
