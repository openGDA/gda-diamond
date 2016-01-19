# This file is sourced from /dls_sw/$BEAMLINE/etc/$BEAMLINE_profile.sh
# which is sourced from /etc/profile.d/gda_environment.sh

if [ ! -n "$BEAMLINE" ]; then
  echo "ERROR: BEAMLINE not set" 1>&2
  exit 1
fi

if [ -f "/etc/profile.d/modules.sh" ]; then
    . /etc/profile.d/modules.sh
fi

# Correct the beamline name based on login host name BL-ws00?.diamond.ac.uk:
# Strip out shortest match between '-' and 'k', at end of string

#To deal with non-standard beamline machines:
case $HOSTNAME in
    bl06i-mo-serv-01.diamond.ac.uk) NEW_BEAMLINE=i06 ;;
    bl06i-mo-serv-02.diamond.ac.uk) NEW_BEAMLINE=i06-1 ;;
    i06-ws010.diamond.ac.uk)        NEW_BEAMLINE=i06
                                    export GDA_MODE=mobilerack ;;
    *)                              NEW_BEAMLINE=${HOSTNAME%-ws*uk} ;;
esac

if [ -z $GDA_MODE ] ; then
	export GDA_MODE=$NEW_BEAMLINE
fi

if [ ! $BEAMLINE == $NEW_BEAMLINE ]; then
    echo $0: BEAMLINE was $BEAMLINE , it is now $NEW_BEAMLINE
    export BEAMLINE=$NEW_BEAMLINE
fi

GDA_ROOT=/dls_sw/$BEAMLINE/software/gda
GDA_CONFIG=$GDA_ROOT/workspace_git/gda-mt.git/configurations/i06-config
MT_CONFIG=$GDA_ROOT/workspace_git/gda-mt.git/configurations/mt-config

export PATH=$GDA_CONFIG/bin:/dls_sw/$BEAMLINE/bin:${PATH}
