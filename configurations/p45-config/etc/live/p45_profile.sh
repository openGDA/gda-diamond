# p45 beamline profile

# This file is sourced by /etc/profile.d/gda_environment.sh on beamline workstations, via a symlink in /dls_sw/p45/etc

if [ ! -n "$BEAMLINE" ]; then
  echo "ERROR: BEAMLINE not set" 1>&2
  exit 1
fi

# Set up path and mode
export PATH=/dls_sw/$BEAMLINE/software/gda/workspace_git/gda-diamond.git/configurations/p45-config/bin:${PATH}
export GDA_MODE=live

# Set up command completion for the gda command
if [[ $(command -v gda >/dev/null) ]]; then
    source <(gda completions bash)
fi
