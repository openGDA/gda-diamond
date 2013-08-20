# i06-1 beamline profile

#To pick up the beamline name XXX based on login host name XXX-ws00?.diamond.ac.uk:
# Strip out shortest match between '-' and 'k', at end of string
hn=$HOSTNAME
BEAMLINE=${hn%-ws*uk}      # XXX

export BEAMLINE

if [ -f "/etc/profile.d/modules.sh" ]; then
    . /etc/profile.d/modules.sh
fi

if [ -r "/dls_sw/$BEAMLINE/etc/gda_environment.sh" ]; then
        . "/dls_sw/$BEAMLINE/etc/gda_environment.sh"
fi

