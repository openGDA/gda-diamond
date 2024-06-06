# i06-2 beamline profile

# Set up path and mode
export PATH=/dls_sw/prod/etc/Launcher:/dls_sw/$BEAMLINE/software/gda/config/bin:/dls_sw/apps/gda_launcher/stable:${PATH}
export GDA_MODE=live

# Set up command completion for the gda command
source  <(gda completions bash)