# p45 beamline profile

# This file is sourced by /etc/profile.d/gda_environment.sh on beamline workstations, via a symlink in /dls_sw/p45/etc

if [ ! -n "$BEAMLINE" ]; then
  echo "ERROR: BEAMLINE not set" 1>&2
  exit 1
fi

# Set up path and mode
# Prepend legacy config/bin
export PATH=/dls_sw/$BEAMLINE/software/gda/workspace_git/gda-diamond.git/configurations/p45-config/bin:${PATH}

# Postpend new gda_launcher
export PATH=${PATH}:/dls_sw/apps/gda_launcher/nightly

export GDA_MODE=live

# Set up command completion for the gda command
source /dls_sw/$BEAMLINE/software/gda/workspace_git/gda-core.git/core-config/bin/gda_core_completion

