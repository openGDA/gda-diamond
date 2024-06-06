# i10-1 beamline profile

export PATH=/dls_sw/i10-1/software/gda/config/bin:/dls_sw/apps/gda_launcher/stable:${PATH}
export LD_LIBRARY_PATH=/dls_sw/i21/software/anaconda2/plugins/platforms:${LD_LIBRARY_PATH}
export GDA_MODE=live

# Set up command completion for the gda command
source  <(gda completions bash)