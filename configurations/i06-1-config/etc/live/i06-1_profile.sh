# i06 beamline profile

# Set up path and mode
export PATH=/dls_sw/prod/etc/Launcher:/dls_sw/$BEAMLINE/software/gda/config/bin:${PATH}
export GDA_MODE=live

# Set up command completion for the gda command
source /dls_sw/$BEAMLINE/software/gda/workspace_git/gda-core.git/core-config/bin/gda_core_completion
