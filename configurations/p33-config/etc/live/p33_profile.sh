# p33 beamline profile

# This file is sourced by /etc/profile.d/gda_environment.sh on beamline workstations, via a symlink in /dls_sw/p33/etc

if [ ! -n "$BEAMLINE" ]; then
  echo "ERROR: BEAMLINE not set" 1>&2
  exit 1
fi

# Set up path and mode
export GDA_MODE=live

export PATH=$PATH:/dls_sw/apps/gda_launcher/nightly

# Set up command completion for the gda command
if [[ $(command -v gda >/dev/null) ]]; then
    source <(gda completions bash)
fi
