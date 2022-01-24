if [ ! -n "$BEAMLINE" ]; then
  echo "ERROR: BEAMLINE not set" 1>&2
  exit 1
fi

export GDA_INSTANCE_NAME=${BEAMLINE}

export GDA_WORKSPACE_PARENT=/dls_sw/$BEAMLINE/software/gda
export GDA_INSTANCE_CONFIG=$GDA_WORKSPACE_PARENT/workspace_git/gda-diamond.git/configurations/i07-config

export PATH=$GDA_INSTANCE_CONFIG/bin:${PATH}
export GDA_MODE=live

if [ -r "/dls_sw/$BEAMLINE/bin/i07_setup.sh" ]; then
   . "/dls_sw/$BEAMLINE/bin/i07_setup.sh" >& /dev/null
fi

# Set up command completion for the gda command
source /dls_sw/$BEAMLINE/software/gda/workspace_git/gda-core.git/core-config/bin/gda_core_completion
