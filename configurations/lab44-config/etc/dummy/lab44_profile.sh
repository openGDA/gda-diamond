# lab44 beamline profile

#define BEAMLINE env variable as this not set in /etc/profile.d/
export BEAMLINE=lab44

# Set up path and mode
export PATH=/dls_sw/prod/etc/Launcher:/dls_sw/$BEAMLINE/software/gda/config/bin:${PATH}
export GDA_MODE=dummy

# Set up command completion for the gda command
if [[ $(command -v gda >/dev/null) ]]; then
    source <(gda completions bash)
fi
