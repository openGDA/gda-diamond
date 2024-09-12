# p99 beamline profile

# This file is sourced by /etc/profile.d/gda_environment.sh on beamline workstations, via a symlink in /dls_sw/p99/etc

if [ ! -n "$BEAMLINE" ]; then
  echo "ERROR: BEAMLINE not set" 1>&2
  exit 1
fi

export GDA_INSTANCE_NAME=${BEAMLINE}

export GDA_WORKSPACE_PARENT=/dls_sw/$BEAMLINE/software/gda
export GDA_INSTANCE_CONFIG=${GDA_WORKSPACE_PARENT}/workspace_git/gda-diamond.git/configurations/k11-config

export PATH=$PATH:/dls_sw/apps/gda_launcher/nightly
export GDA_MODE=live